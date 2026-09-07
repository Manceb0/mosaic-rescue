#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-024 · Calibracion del score de AlphaGenome del candidato congelado frente a
un null emparejado y a controles positivos, con el plan estadistico sellado
ANTES de puntuar nada.

LO QUE RESPONDE
    EXP-023 respondio "¿el candidato cae donde el modelo es localmente
    sensible?" (no). Esto responde otra cosa: "¿cuan inusual es el score del
    candidato frente a SNV COMPARABLES puntuados con el mismo sistema?". Es
    calibracion del modelo, no calibracion clinica: un percentil no es una
    probabilidad de patogenicidad.

DOS CONJUNTOS, CONGELADOS CON SHA256 ANTES DE LA PRIMERA LLAMADA
    NULL-A   SNV sinteticas en los intrones PROFUNDOS del mismo transcrito
             (>= 1 000 pb de cualquier borde de exon), fuera de la ventana ISM
             del candidato, de la misma clase mutacional (transicion) y con la
             base REF leida del FASTA GRCh38 local. Mismo gen, misma hebra,
             mismo contexto genico: el emparejamiento mas estrecho que no
             requiere elegir otros genes a mano.
    CTRL-POS las cuatro posiciones canonicas de splicing de cada intron
             (donante +1/+2, aceptor -2/-1), mutadas a su transicion. Son el
             control de POTENCIA de la lectura de splicing: si ni siquiera
             estas salen extremas, un negativo del candidato no informa.

    El candidato no puede estar en ninguno de los dos (se comprueba).
    El muestreo del null es el UNICO paso aleatorio: semilla 42, registrada.

LO QUE SE PUNTUA (identico para candidato, null y controles)
    16 kb   los dos scorers de la ISM de EXP-023 (splice sites primario, DNase
            secundario), para que el escalar del candidato sea EL MISMO objeto
            que en EXP-023.
    1 Mb    ContactMapScorer oficial (28 pistas; la predeclarada CL:0002620) y
            los scorers recomendados del panel tejido x modalidad de EXP-024b
            (ver alphagenome_tissue_matrix.py).

ESTADISTICA, FIJADA AQUI
    percentil  = 100 * #{|S_null| <  |S_cand|} / N
    p_emp      = (1 + #{|S_null| >= |S_cand|}) / (N + 1)
    z robusto  = (S_cand - mediana) / (1.4826 * MAD)
    familia    = {splice, dnase, contact}: tres p_emp -> q de Benjamini-Hochberg
    potencia   = fraccion de CTRL-POS con p_emp < 0,05 en la lectura de splicing

REGLAS DE LECTURA, FIJADAS AQUI
    q >= 0,05       "unremarkable relative to the matched computational null"
    q <  0,05       "extreme relative to the matched computational null":
                    se registra como CONTRADICCION CONCRETA para que el
                    mantenedor la adjudique; NO cambia por si sola ninguna
                    clasificacion, ranking ni rama
    potencia < 0,5  "readout insufficiently sensitive in this gene: the
                    candidate's negative is uninformative" (se declara)

Uso:
    python src/model_outputs/alphagenome_calibration.py freeze   # sin modelo
    work/venv-ag/Scripts/python.exe src/model_outputs/alphagenome_calibration.py run
"""
from __future__ import annotations
import io, json, os, random, sys, time

import numpy as np

sys.path.insert(0, ".")
from src.model_outputs import alphagenome_common as C                  # noqa: E402

DIR = os.path.join(C.WORK, "calibration")
NULL_MANIFEST = os.path.join(DIR, "null_manifest.json")

N_NULL = 300
MIN_EXON_DIST = 1000          # pb a cualquier borde de exon
SEED = 42                     # el unico paso aleatorio del experimento
TRANSITION = {"A": "G", "G": "A", "C": "T", "T": "C"}
FAMILY = ("splice", "dnase", "contact")


# ------------------------------------------------------- conjuntos ---------
def _exons():
    from src.structure.transcript_model import fetch
    tx = fetch()
    ex = sorted((int(e["start"]), int(e["end"])) for e in tx["exons"])
    return tx, ex


def eligible_positions(ex, cand_pos: int, ism_half: int):
    """Posiciones intronicas profundas del transcrito, fuera de la ventana ISM."""
    out = []
    for (a1, b1), (a2, b2) in zip(ex[:-1], ex[1:]):
        lo, hi = b1 + 1 + MIN_EXON_DIST, a2 - 1 - MIN_EXON_DIST
        for p in range(lo, hi + 1):
            if abs(p - cand_pos) > ism_half:
                out.append(p)
    return out


def canonical_sites(ex, strand: int):
    """Las 4 posiciones canonicas de cada intron: +1,+2 tras el exon y -2,-1
    antes del siguiente, en coordenadas genomicas (la hebra solo cambia que
    dinucleotido se espera, no que posiciones)."""
    out = []
    for (a1, b1), (a2, b2) in zip(ex[:-1], ex[1:]):
        out += [(b1 + 1, "donor+1" if strand > 0 else "acceptor-1"),
                (b1 + 2, "donor+2" if strand > 0 else "acceptor-2"),
                (a2 - 2, "acceptor-2" if strand > 0 else "donor+2"),
                (a2 - 1, "acceptor-1" if strand > 0 else "donor+1")]
    return out


def freeze() -> dict:
    if os.path.exists(NULL_MANIFEST):
        raise SystemExit(f"{NULL_MANIFEST} ya existe: un conjunto congelado no se reescribe")
    man = C.load_manifest()                       # el de EXP-023, intacto
    cand = man["candidate"]
    plain = cand["chromosome"].replace("chr", "")
    tx, ex = _exons()
    strand = int(tx.get("strand", 1))
    ism_half = man["ism"]["ism_window_bp"] // 2

    pool = eligible_positions(ex, cand["position_1based"], ism_half)
    rng = random.Random(SEED)
    picked = sorted(rng.sample(pool, N_NULL))
    null = []
    for p in picked:
        ref = C.fasta_fetch(C.FASTA, plain, p, p)
        if ref not in TRANSITION:
            raise SystemExit(f"base ambigua en el FASTA en el offset {p - cand['position_1based']:+d}")
        null.append({"chromosome": cand["chromosome"], "position_1based": p,
                     "ref": ref, "alt": TRANSITION[ref], "offset_bp": p - cand["position_1based"]})
    ctrl = []
    for p, role in canonical_sites(ex, strand):
        ref = C.fasta_fetch(C.FASTA, plain, p, p)
        ctrl.append({"chromosome": cand["chromosome"], "position_1based": p,
                     "ref": ref, "alt": TRANSITION[ref], "role": role,
                     "offset_bp": p - cand["position_1based"]})
    for s in (null, ctrl):
        if any(v["position_1based"] == cand["position_1based"] for v in s):
            raise SystemExit("el candidato aparece en un conjunto: fuga")
    if len({v["position_1based"] for v in null}) != N_NULL:
        raise SystemExit("posiciones repetidas en el null")

    out = {
        "experiment": "EXP-024 calibration", "frozen_at_utc": C.now_utc(),
        "git_commit": C.git_commit(), "exp023_manifest_sha256":
            io.open(C.MANIFEST + ".sha256").read().strip(),
        "candidate": {"id": cand["candidate_id"], "class": f"{cand['ref']}>{cand['alt']} transition",
                      "in_null": False, "in_controls": False},
        "transcript": {"id": tx["transcript"], "release": tx["release"], "strand": strand,
                       "n_exons": len(ex), "n_introns": len(ex) - 1},
        "null_A": {"definition": "deep-intronic synthetic transitions of the same transcript, "
                                 f">= {MIN_EXON_DIST} bp from any exon boundary, outside the "
                                 "candidate's ISM window, REF read from local GRCh38",
                   "n": N_NULL, "eligible_positions": len(pool), "seed": SEED,
                   "sampling": "random.Random(seed).sample(pool, n), without replacement",
                   "variants": null},
        "control_positive": {"definition": "the four canonical splice-site positions of every "
                                           "intron (donor +1/+2, acceptor -2/-1), transition",
                             "n": len(ctrl), "variants": ctrl},
        "scoring": {
            "16kb": {"context_bp": man["ism"]["sequence_context_bp"], "scorers": man["ism"]["scorers"],
                     "note": "identical to EXP-023 ISM: the candidate scalar is the same object"},
            "1Mb": {"context_bp": man["contacts"]["sequence_context_bp"],
                    "contact": {"scorer": "ContactMapScorer", "tracks": "all 28",
                                "predeclared_track": man["contacts"]["ontology_curie"]},
                    "panel": "src/model_outputs/alphagenome_tissue_matrix.py (frozen panel manifest)"},
        },
        "statistics": {
            "percentile": "100 * #{|S_null| < |S_cand|} / N",
            "p_emp": "(1 + #{|S_null| >= |S_cand|}) / (N + 1)",
            "robust_z": "(S_cand - median) / (1.4826 * MAD)",
            "family": list(FAMILY), "multiplicity": "Benjamini-Hochberg over the family only",
            "power_check": "fraction of CTRL-POS with p_emp < 0.05 under the splice readout",
        },
        "reading_rules": {
            "unremarkable": "q >= 0.05",
            "extreme": "q < 0.05: logged as a concrete contradiction for the maintainer to "
                       "adjudicate; changes no classification, ranking or branch by itself",
            "uninformative": "power_check < 0.5: the readout is insufficiently sensitive in this "
                             "gene and the candidate's negative is declared uninformative",
            "not_pathogenicity": "percentile, p_emp and z are model-score calibration, never "
                                 "probability of pathogenicity or ACMG evidence",
        },
        "random_seed": SEED,
    }
    sha = C.write_json(NULL_MANIFEST, out)
    io.open(NULL_MANIFEST + ".sha256", "w").write(sha + "\n")
    return out, sha


def load_null_manifest() -> dict:
    want = io.open(NULL_MANIFEST + ".sha256").read().strip()
    if C.sha256_file(NULL_MANIFEST) != want:
        raise SystemExit("el manifest del null cambio despues de congelarse")
    return C.read_json(NULL_MANIFEST)


# ------------------------------------------------------------ estadistica ---
def calibrate(s_cand: float, s_null: np.ndarray) -> dict:
    a, c = np.abs(np.asarray(s_null, dtype=float)), abs(float(s_cand))
    n = len(a)
    med = float(np.median(s_null)); mad = float(np.median(np.abs(s_null - med)))
    return {"n": int(n), "percentile": float(100.0 * (a < c).sum() / n),
            "p_emp": float((1 + (a >= c).sum()) / (n + 1)),
            "robust_z": float((s_cand - med) / (1.4826 * mad)) if mad > 0 else None,
            "null_median": med, "null_mad": mad}


def bh(pvals: list) -> list:
    p = np.asarray(pvals, dtype=float); m = len(p)
    order = np.argsort(p); ranked = p[order] * m / (np.arange(m) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m); out[order] = np.minimum(q, 1.0)
    return out.tolist()


# --------------------------------------------------------------- the run ---
def _scalar(adata, spec) -> float:
    from src.model_outputs.alphagenome_ism import scalar_from
    return scalar_from(adata, spec)[0]


def run() -> int:
    from alphagenome.data import genome
    from alphagenome.models import dna_client, variant_scorers
    from src.model_outputs.alphagenome_ism import make_scorers
    from src.model_outputs import alphagenome_tissue_matrix as TM

    man = C.load_manifest(); nm = load_null_manifest(); panel = TM.load_panel()
    cand = man["candidate"]
    sets = ([("candidate", cand["chromosome"], cand["position_1based"], cand["ref"], cand["alt"], "candidate")]
            + [("null", v["chromosome"], v["position_1based"], v["ref"], v["alt"], "null")
               for v in nm["null_A"]["variants"]]
            + [("control", v["chromosome"], v["position_1based"], v["ref"], v["alt"], v["role"])
               for v in nm["control_positive"]["variants"]])
    model = dna_client.create(C.api_key(), model_version=man["model"]["model_version_requested"])
    ism_scorers = make_scorers(man["ism"]["scorers"])
    contact = variant_scorers.ContactMapScorer()
    panel_scorers = TM.make_scorers(panel)
    print(f"  -> {len(sets)} variantes (1 candidato, {nm['null_A']['n']} null, "
          f"{nm['control_positive']['n']} controles): solo el locus del candidato es dato del paciente")
    os.makedirs(DIR, exist_ok=True)
    rows, t0 = [], time.time()
    for i, (kind, chrom, pos, ref, alt, role) in enumerate(sets):
        v = genome.Variant(chromosome=chrom, position=pos, reference_bases=ref, alternate_bases=alt)
        r16 = model.score_variant(interval=v.reference_interval.resize(man["ism"]["sequence_context_bp"]),
                                  variant=v, variant_scorers=ism_scorers)
        r1m = model.score_variant(interval=v.reference_interval.resize(man["contacts"]["sequence_context_bp"]),
                                  variant=v, variant_scorers=[contact] + panel_scorers)
        row = {"kind": kind, "role": role, "offset_bp": pos - cand["position_1based"], "ref": ref, "alt": alt,
               "splice": _scalar(r16[0], man["ism"]["scorers"][0]),
               "dnase": _scalar(r16[1], man["ism"]["scorers"][1])}
        X = np.asarray(r1m[0].X, dtype=float).ravel()
        cur = r1m[0].var["ontology_curie"].astype(str).to_numpy()
        row["contact"] = float(X[np.flatnonzero(cur == man["contacts"]["ontology_curie"])[0]])
        row["contact_all"] = dict(zip(cur.tolist(), X.tolist()))
        row["panel"] = TM.extract(r1m[1:], panel)
        rows.append(row)
        if (i + 1) % 25 == 0:
            print(f"    {i + 1}/{len(sets)}  {time.time() - t0:.0f} s", flush=True)
    raw_path = os.path.join(DIR, "raw_scores.json.gz")
    sha_raw = C.write_json(raw_path, {"rows": rows}, gz=True)
    io.open(os.path.join(DIR, "raw_scores.tsv"), "w", encoding="utf-8", newline="\n").write(
        "kind\trole\toffset_bp\tref\talt\tsplice\tdnase\tcontact\n" + "".join(
            f"{r['kind']}\t{r['role']}\t{r['offset_bp']}\t{r['ref']}\t{r['alt']}\t{r['splice']!r}\t"
            f"{r['dnase']!r}\t{r['contact']!r}\n" for r in rows))

    c = rows[0]; nul = [r for r in rows if r["kind"] == "null"]; ctl = [r for r in rows if r["kind"] == "control"]
    stats = {k: calibrate(c[k], np.array([r[k] for r in nul])) for k in FAMILY}
    q = bh([stats[k]["p_emp"] for k in FAMILY])
    for k, qq in zip(FAMILY, q):
        stats[k]["q_bh"] = qq
    power = {k: float(np.mean([calibrate(r[k], np.array([x[k] for x in nul]))["p_emp"] < 0.05 for r in ctl]))
             for k in FAMILY}
    ctl_pct = {k: float(np.median([calibrate(r[k], np.array([x[k] for x in nul]))["percentile"] for r in ctl]))
               for k in FAMILY}
    reading = {}
    for k in FAMILY:
        reading[k] = ("extreme relative to the matched computational null (logged as a concrete "
                      "contradiction for adjudication)" if stats[k]["q_bh"] < 0.05
                      else "unremarkable relative to the matched computational null")
    if power["splice"] < 0.5:
        reading["splice"] += "; POWER CHECK FAILED: readout insufficiently sensitive in this gene, " \
                             "the candidate's negative is uninformative"
    meta = {"run": "calibration", "figure_class": "MODEL_OUTPUT", "evidence_origin": "PREDICTED+DERIVED",
            "source_type": "predicted_not_patient_measurement", "started_utc": C.now_utc(),
            "environment": C.environment(), "manifest_sha256": io.open(C.MANIFEST + ".sha256").read().strip(),
            "null_manifest_sha256": io.open(NULL_MANIFEST + ".sha256").read().strip(),
            "panel_manifest_sha256": TM.panel_sha(), "n_scored": len(rows),
            "files": {"raw_scores": "raw_scores.json.gz", "raw_scores_sha256": sha_raw},
            "candidate_scores": {k: c[k] for k in FAMILY}, "calibration": stats,
            "power_check": power, "control_median_percentile": ctl_pct, "reading": reading,
            "random_seed": nm["random_seed"]}
    C.write_json(os.path.join(DIR, "metadata.json"), meta)
    for k in FAMILY:
        s = stats[k]
        print(f"  {k:<8} percentil {s['percentile']:5.1f}  p_emp {s['p_emp']:.4f}  q {s['q_bh']:.4f}  "
              f"potencia(controles) {power[k]:.2f}  -> {reading[k][:60]}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "freeze"
    if cmd == "freeze":
        out, sha = freeze()
        print(f"  null congelado : {NULL_MANIFEST}  sha256 {sha[:16]}...")
        print(f"  NULL-A         : {out['null_A']['n']} de {out['null_A']['eligible_positions']:,} "
              f"posiciones elegibles, semilla {out['random_seed']}")
        print(f"  CTRL-POS       : {out['control_positive']['n']} posiciones canonicas de splicing "
              f"({out['transcript']['n_introns']} intrones)")
    elif cmd == "run":
        sys.exit(run())
    else:
        raise SystemExit("uso: freeze | run")
