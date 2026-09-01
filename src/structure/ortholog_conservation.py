#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-011 · conservacion ortologa del residuo candidato de BUB1B.

QUE PREGUNTA RESPONDE
    .Esta la posicion candidata bajo restriccion evolutiva, y de que TIPO?
    No responde "es patogenica": la conservacion pertenece a la historia
    mecanistica, no a la clasificacion ACMG (docs/STRUCTURAL_MISSENSE.md).

DECISIONES DE METODO, congeladas antes de mirar el resultado
    1. SOLO ortologos 1:1. Los paralogos BUB1/BUB1B comparten el dominio
       pseudoquinasa; mezclarlos mide conservacion de familia, no de ortologo.
    2. Las columnas del alineamiento se recalculan PARA CADA homologia. Ensembl
       devuelve alineamientos por pares, cada uno con su propio patron de huecos
       en la secuencia fuente; reutilizar las columnas de una homologia en otra
       produce numeros sin sentido (fallo detectado y corregido en EXP-011).
    3. Los huecos se EXCLUYEN del denominador en vez de contarse como
       discrepancia. Un hueco es "no alineable aqui", no "residuo distinto".
    4. LINEA BASE INTERNA obligatoria: la identidad de una posicion suelta es
       ininterpretable. Se calcula la identidad de las 1050 posiciones y se
       situa la candidata en el percentil de esa distribucion.
    5. Se declara el sesgo de caida del alineamiento: si los huecos se
       concentran en los ortologos lejanos, el denominador NO es una muestra
       aleatoria de vertebrados.

PROCEDENCIA
    EXTERNAL  - las secuencias y los alineamientos vienen de Ensembl Compara.
    DERIVED   - identidad, percentil y clase quimica se calculan aqui.
    PREDICTED - nada. Este modulo no predice; mide sobre datos externos.
"""
from __future__ import annotations
import io, json, collections
from dataclasses import dataclass, asdict

# Cadenas laterales capaces de ACEPTAR un puente de hidrogeno. Es la propiedad
# que el analisis estructural senalo como rotamero-independiente: el silvestre
# ACEPTA un puente del esqueleto y el residuo entrante solo puede donar.
ACCEPTOR = set("NQDESTYHW")
DONOR_ONLY = set("KR")
HYDROPHOBIC = set("AVLIMFWCPGY")

# Clases quimicas mutuamente excluyentes. "Conservacion de clase" = fraccion de
# ortologos cuyo residuo cae en la MISMA clase que el humano. Es la medida que
# hace comparables posiciones de naturaleza distinta: en un residuo hidrofobico
# pregunta si sigue siendo hidrofobico; en uno acido, si sigue siendo acido.
CLASSES = {
    "aromatico":   set("FWY"),
    "alifatico":   set("AVLIMC"),
    "polar":       set("STNQ"),
    "acido":       set("DE"),
    "basico":      set("KRH"),
    "especial":    set("GP"),
}


def chemical_class(aa: str) -> str:
    for name, members in CLASSES.items():
        if aa in members:
            return name
    return "otro"


def class_conservation(observed: dict, human_aa: str) -> float:
    """% de ortologos en la misma clase quimica que el residuo humano."""
    tot = sum(observed.values()) or 1
    cls = chemical_class(human_aa)
    return round(100 * sum(k for a, k in observed.items() if chemical_class(a) == cls) / tot, 1)

MIN_ALIGNED = 60          # posiciones con menos ortologos alineados no entran en la linea base


ENSEMBL = ("https://rest.ensembl.org/homology/id/human/{gene}"
           "?type=orthologues;sequence=protein;content-type=application/json")


def fetch(gene_id: str, dest: str) -> str:
    """Descarga las homologias de Ensembl Compara. Idempotente: si el fichero ya
    existe no vuelve a pedirlo, para que reejecutar el analisis no dependa de la
    disponibilidad del servicio ni cambie los datos bajo los pies."""
    import os, urllib.request
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(ENSEMBL.format(gene=gene_id),
                                 headers={"User-Agent": "mosaic-rescue/EXP-011"})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
    io.open(dest, "wb").write(body)
    return dest


def _one2one(path: str):
    d = json.load(io.open(path, encoding="utf-8"))
    return [h for h in d["data"][0]["homologies"] if h["type"] == "ortholog_one2one"]


@dataclass
class PositionStats:
    resnum: int
    human_aa: str
    n_aligned: int
    identity_pct: float
    percentile: float
    observed: dict            # aa -> n
    acceptor_pct: float
    hydrophobic_pct: float
    class_pct: float
    human_class: str


def per_position(homologies):
    """Identidad por posicion sobre TODA la proteina, en una sola pasada.

    Devuelve (human_seq_by_pos, n_aligned, n_identical, observed_by_pos).
    """
    ident = collections.Counter()
    aligned = collections.Counter()
    observed = collections.defaultdict(collections.Counter)
    human = {}
    for h in homologies:
        src, tgt = h["source"]["align_seq"], h["target"]["align_seq"]
        n = 0
        for col, ch in enumerate(src):
            if ch == "-":
                continue
            n += 1
            if col >= len(tgt):
                break
            human[n] = ch
            aa = tgt[col]
            if aa == "-":
                continue
            aligned[n] += 1
            observed[n][aa] += 1
            if aa == ch:
                ident[n] += 1
    return human, aligned, ident, observed


def by_clade(homologies, target: int, lineages: dict):
    """Reparte lo observado en la posicion candidata por clado de vertebrados.

    Los ortologos NO son observaciones independientes: Ensembl muestrea mucho mas
    densamente mamiferos. Un agregado alto puede estar sostenido por un solo
    linaje sobremuestreado, asi que se desglosa antes de interpretarlo.
    """
    from src.structure.clades import clade_of, ORDER
    out = {c: {"observed": collections.Counter(), "gapped": 0, "n_species": 0} for c in ORDER}
    for h in homologies:
        src, tgt = h["source"]["align_seq"], h["target"]["align_seq"]
        n, col = 0, None
        for i, ch in enumerate(src):
            if ch != "-":
                n += 1
                if n == target:
                    col = i
                    break
        aa = tgt[col] if (col is not None and col < len(tgt)) else "-"
        c = clade_of(lineages.get(str(h["target"]["taxon_id"])))
        out[c]["n_species"] += 1
        if aa == "-":
            out[c]["gapped"] += 1
        else:
            out[c]["observed"][aa] += 1
    res = []
    for c in ORDER:
        d = out[c]
        n = sum(d["observed"].values())
        if not d["n_species"]:
            continue
        res.append({
            "clade": c,
            "n_species": d["n_species"],
            "n_aligned": n,
            "gapped": d["gapped"],
            "observed": dict(d["observed"].most_common()),
            "acceptor_pct": round(100 * sum(k for a, k in d["observed"].items()
                                            if a in ACCEPTOR) / n, 1) if n else None,
            "donor_only_n": sum(k for a, k in d["observed"].items() if a in DONOR_ONLY),
        })
    return res


def analyse(orthologs_json: str, target: int, pocket=(), lineages=None):
    homs = _one2one(orthologs_json)
    human, aligned, ident, observed = per_position(homs)

    pct = {n: 100 * ident[n] / aligned[n] for n in aligned if aligned[n] >= MIN_ALIGNED}
    ordered = sorted(pct.values())

    def percentile_of(x):
        return 100 * sum(1 for v in ordered if v < x) / len(ordered)

    # --- percentil con COBERTURA COMPARABLE ---------------------------------
    # Comparar la candidata contra posiciones sostenidas por denominadores mucho
    # menores infla su percentil: una posicion alineada en 65 especies y otra en
    # 120 no son la misma medida. Se restringe a una banda de cobertura.
    COVERAGE_BAND = 10
    tgt_cov = aligned[target]
    comparable = sorted(v for n, v in pct.items()
                        if abs(aligned[n] - tgt_cov) <= COVERAGE_BAND)

    def percentile_comparable(x):
        return 100 * sum(1 for v in comparable if v < x) / len(comparable)

    def stats(n) -> PositionStats:
        obs = observed[n]
        tot = sum(obs.values()) or 1
        return PositionStats(
            resnum=n, human_aa=human[n], n_aligned=aligned[n],
            identity_pct=round(pct[n], 2), percentile=round(percentile_of(pct[n]), 1),
            observed=dict(obs.most_common()),
            acceptor_pct=round(100 * sum(k for a, k in obs.items() if a in ACCEPTOR) / tot, 1),
            hydrophobic_pct=round(100 * sum(k for a, k in obs.items() if a in HYDROPHOBIC) / tot, 1),
            class_pct=class_conservation(obs, human[n]),
            human_class=chemical_class(human[n]),
        )

    # sesgo de caida: .quienes NO alinean en la posicion candidata?
    dropout = {"aligned": [], "gapped": []}
    for h in homs:
        src, tgt = h["source"]["align_seq"], h["target"]["align_seq"]
        n, col = 0, None
        for i, ch in enumerate(src):
            if ch != "-":
                n += 1
                if n == target:
                    col = i
                    break
        aa = tgt[col] if (col is not None and col < len(tgt)) else "-"
        rec = {"species": h["target"]["species"], "global_pct_id": h["target"].get("perc_id"), "aa": aa}
        dropout["aligned" if aa != "-" else "gapped"].append(rec)

    return {
        "n_orthologs_one2one": len(homs),
        "n_positions_scored": len(pct),
        "protein_length": max(human),
        "baseline": {
            "median_identity_pct": round(ordered[len(ordered) // 2], 2),
            "p10": round(ordered[int(0.10 * (len(ordered) - 1))], 2),
            "p25": round(ordered[int(0.25 * (len(ordered) - 1))], 2),
            "p75": round(ordered[int(0.75 * (len(ordered) - 1))], 2),
            "p90": round(ordered[int(0.90 * (len(ordered) - 1))], 2),
            "all_positions": [round(v, 2) for v in ordered],
        },
        "coverage_comparable": {
            "band": COVERAGE_BAND,
            "candidate_coverage": tgt_cov,
            "n_positions": len(comparable),
            "candidate_percentile": round(percentile_comparable(pct[target]), 1),
            "median_identity_pct": round(comparable[len(comparable) // 2], 2),
            "all_positions": [round(v, 2) for v in comparable],
        },
        "candidate": asdict(stats(target)),
        "by_clade": by_clade(homs, target, lineages) if lineages else None,
        "pocket": [asdict(stats(p)) for p in pocket if p in pct],
        "dropout": dropout,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.paths import get
    # La posicion NO se escribe aqui: un fichero versionado no puede llevarla.
    TARGET = get("candidate", "residue")
    POCKET = get("candidate", "pocket")
    from src.structure.clades import fetch_lineages
    src = fetch("ENSG00000156970", "work/conservation/orthologs.json")   # BUB1B
    tids = sorted({h["target"]["taxon_id"] for h in _one2one(src)})
    lin = fetch_lineages(tids, "work/conservation/taxonomy.json")
    out = analyse(src, TARGET, POCKET, lineages=lin)
    json.dump(out, io.open("work/conservation/conservation_full.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    c = out["candidate"]
    print(f"  ortologos 1:1 {out['n_orthologs_one2one']} · linea base mediana "
          f"{out['baseline']['median_identity_pct']} %")
    print(f"  candidato: identidad {c['identity_pct']} % · percentil {c['percentile']}")
    print(f"  aceptor de puente de H conservado: {c['acceptor_pct']} %")
    print(f"  -> work/conservation/conservation_full.json")
