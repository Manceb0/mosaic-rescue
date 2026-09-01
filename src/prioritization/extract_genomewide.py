#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-006 · paso 1: extraer TODAS las variantes HIGH+MODERATE del genoma,
sin filtro de panel.

No se menciona ningun gen. Esa es la garantia de imparcialidad.

CORRECCION v2. La v1 cruzaba VEP con el VCF por (chrom, pos) EXACTO y perdia
466 posiciones, 228 de ellas de alto impacto incluidos 157 frameshifts: VEP
normaliza los indels a la izquierda y desplaza la coordenada respecto al POS del
VCF. Se acepta ahora una tolerancia de +-1 y se VERIFICA la recuperacion.
"""
import io, gzip, collections

VEP = "work/pass1/pass1_20260830T043708Z.tsv"
from src.paths import patient_vcf          # Regla Dura 2: la ruta NO vive en el codigo
VCF = patient_vcf()
OUT = "work/gw/highmod.vcf"

want = collections.defaultdict(set)      # chrom -> {pos}
cons = {}
with io.open(VEP, encoding="utf-8", errors="replace") as f:
    ix = None
    for line in f:
        if line.startswith("##"):
            continue
        if line.startswith("#"):
            h = line[1:].rstrip("\n").split("\t"); ix = {k: i for i, k in enumerate(h)}; continue
        p = line.rstrip("\n").split("\t")
        try:
            if p[ix["IMPACT"]] not in ("HIGH", "MODERATE"):
                continue
            c, r = p[ix["Location"]].split(":")
            pos = int(r.split("-")[0])
            want[c].add(pos)
            cons[(c, pos)] = p[ix["Consequence"]]
        except (IndexError, KeyError, ValueError):
            pass
n_want = sum(len(v) for v in want.values())
print(f"  posiciones HIGH/MODERATE segun VEP : {n_want:,}")

out = io.open(OUT, "w", encoding="utf-8", newline="\n")
n = 0
hit = set()
with gzip.open(VCF, "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        if line.startswith("#"):
            out.write(line); continue
        p = line.split("\t", 3)
        c, pos = p[0], int(p[1])
        s = want.get(c)
        if not s:
            continue
        # tolerancia +-1: VEP desplaza la coordenada de los indels
        for d in (0, 1, -1):
            if pos + d in s:
                out.write(line); n += 1
                hit.add((c, pos + d))
                break
out.close()

lost = n_want - len(hit)
print(f"  variantes extraidas                : {n:,}")
print(f"  posiciones de VEP recuperadas      : {len(hit):,}")
print(f"  todavia sin casar                  : {lost:,}")
if lost:
    c2 = collections.Counter()
    for k, v in cons.items():
        if k not in hit:
            c2[v.split(",")[0]] += 1
    for k, v in c2.most_common(6):
        print(f"      {k:<38} {v}")
