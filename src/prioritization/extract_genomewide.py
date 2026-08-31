#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-006 · paso 1: extraer TODAS las variantes HIGH+MODERATE del genoma,
sin filtro de panel, para que los genes compitan sin que les digamos el ganador.

No se menciona ningun gen en este script. Esa es la garantia.
"""
import io, gzip, sys, collections

VEP = "work/pass1/pass1_20260830T043708Z.tsv"
VCF = "C:/Users/USUARIO/Downloads/[REDACTED]_[REDACTED].vcf.gz"
OUT = "work/gw/highmod.vcf"

want = set()
genes = collections.Counter()
with io.open(VEP, encoding="utf-8", errors="replace") as f:
    ix = None
    for line in f:
        if line.startswith("##"):
            continue
        if line.startswith("#"):
            h = line[1:].rstrip("\n").split("\t"); ix = {k: i for i, k in enumerate(h)}; continue
        p = line.rstrip("\n").split("\t")
        try:
            if p[ix["IMPACT"]] in ("HIGH", "MODERATE"):
                loc = p[ix["Location"]]
                want.add((loc.split(":")[0], loc.split(":")[1].split("-")[0]))
                genes[p[ix["SYMBOL"]]] += 1
        except (IndexError, KeyError):
            pass
print(f"  posiciones HIGH/MODERATE : {len(want):,}")
print(f"  genes implicados         : {len(genes):,}")

out = io.open(OUT, "w", encoding="utf-8", newline="\n"); n = 0
with gzip.open(VCF, "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        if line.startswith("#"):
            out.write(line); continue
        p = line.split("\t", 3)
        if (p[0], p[1]) in want:
            out.write(line); n += 1
out.close()
print(f"  extraidas a {OUT}: {n:,} variantes")
