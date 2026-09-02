#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelo de transcrito y dominios proteicos de BUB1B desde Ensembl REST.

POR QUE
    La figura de curacion dibujaba exones en un SVG hecho a mano. Un revisor no
    puede comprobar de donde salen. Aqui la estructura viene de Ensembl, se
    cachea con su version de release, y la figura se construye sobre ella con
    `dna_features_viewer`, que es la libreria que se usa para esto.

QUE SALE DE AQUI — y que NO
    Sale la anatomia PUBLICA del gen: exones del transcrito MANE Select y
    dominios de InterPro/Pfam sobre la traduccion.
    NO sale ninguna coordenada del paciente. Las posiciones del caso entran en
    la figura como offsets en CDS, calculados aparte y nunca escritos aqui.

REPRODUCIBILIDAD
    Cache en work/struct/transcript.json con la release de Ensembl. Borrarlo
    fuerza la descarga. Sin datos del paciente en la peticion: solo 'BUB1B'.
"""
from __future__ import annotations
import io, json, os, time, urllib.request

GENE = "BUB1B"
SPECIES = "homo_sapiens"
REST = "https://rest.ensembl.org"
CACHE = "work/struct/transcript.json"


def _get(path: str, tries: int = 3):
    url = REST + path
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Content-Type": "application/json",
                                                       "User-Agent": "mosaic-rescue/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


def fetch(force: bool = False) -> dict:
    if not force and os.path.exists(CACHE):
        return json.load(io.open(CACHE, encoding="utf-8"))

    release = _get("/info/data?")["releases"][0]
    # expand=1 trae transcritos y exones en una sola peticion
    g = _get(f"/lookup/symbol/{SPECIES}/{GENE}?expand=1")

    # MANE Select: el transcrito canonico que usan ClinVar y VEP. Si el endpoint
    # no lo marca, se cae al canonico de Ensembl y se DECLARA cual se uso.
    mane = None
    for t in g["Transcript"]:
        if t.get("is_canonical") == 1:
            mane = t
    picked = "canonical"
    for t in g["Transcript"]:
        if str(t.get("id", "")).startswith("ENST") and t.get("MANE"):
            mane, picked = t, "MANE Select"
    assert mane is not None, "sin transcrito canonico"

    tr = _get(f"/lookup/id/{mane['id']}?expand=1&utr=1")
    exons = [{"id": e["id"], "start": e["start"], "end": e["end"]} for e in tr["Exon"]]
    exons.sort(key=lambda e: e["start"], reverse=(tr["strand"] < 0))

    tsl = tr.get("Translation") or {}

    # Mapa exon -> rango de CDS y de aminoacidos. Necesario para que el modelo
    # de transcrito y la pista de dominios compartan eje en la figura.
    cds0, cds1 = tsl.get("start"), tsl.get("end")
    if cds0:
        acc = 0
        for e in exons:
            a0, a1 = max(e["start"], cds0), min(e["end"], cds1)
            if a1 < a0:
                e["cds"] = None
                continue
            n = a1 - a0 + 1
            e["cds"] = [acc + 1, acc + n]
            e["aa"] = [acc // 3 + 1, (acc + n - 1) // 3 + 1]
            acc += n
        cds_len = acc
    domains = []
    if tsl.get("id"):
        for f in _get(f"/overlap/translation/{tsl['id']}?content-type=application/json"):
            if f.get("type") in ("Pfam", "Superfamily", "Gene3D", "PANTHER", "SMART"):
                domains.append({"type": f["type"], "id": f.get("id"),
                                "desc": f.get("description") or f.get("interpro_description") or "",
                                "start": f["start"], "end": f["end"],
                                "interpro": f.get("interpro")})

    out = {"release": release, "gene": GENE, "gene_id": g["id"],
           "chrom": g["seq_region_name"], "strand": tr["strand"],
           "transcript": mane["id"], "transcript_pick": picked,
           "biotype": tr.get("biotype"), "n_exons": len(exons), "exons": exons,
           "translation": {"id": tsl.get("id"), "length": tsl.get("length"),
                           "cds_len": cds_len if cds0 else None},
           "domains": sorted(domains, key=lambda d: (d["start"], d["end"]))}
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    tmp = CACHE + ".tmp"
    json.dump(out, io.open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, CACHE)
    return out


if __name__ == "__main__":
    d = fetch()
    print(f"  Ensembl release {d['release']} · {d['gene']} ({d['gene_id']}) "
          f"chr{d['chrom']} hebra {d['strand']:+d}")
    print(f"  transcrito {d['transcript']} [{d['transcript_pick']}] · {d['biotype']} · "
          f"{d['n_exons']} exones · proteina {d['translation']['length']} aa")
    cod = [e for e in d["exons"] if e.get("cds")]
    print(f"  exones codificantes: {len(cod)} · CDS {d['translation']['cds_len']:,} nt "
          f"= {d['translation']['length']} aa + stop")
    print(f"  dominios anotados: {len(d['domains'])}")
    seen = set()
    for x in d["domains"]:
        k = (x["desc"] or x["id"])
        if k in seen:
            continue
        seen.add(k)
        print(f"    {x['type']:<12}{x['start']:>5}-{x['end']:<5} {k[:56]}")
