#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mide el alcance real de la fase fisica (PGT/PID) en un VCF.

Salida EXCLUSIVAMENTE agregada: numero de bloques, variantes por bloque y
distribucion de la envergadura en pb. No imprime coordenadas, genotipos ni
secuencia (Regla Dura 1).

La pregunta que responde: PGT/PID solo enlaza variantes que el caller pudo
colocar sobre el mismo haplotipo ensamblado. Saber hasta que distancia llega
determina si la fase sirve para heterocigosis compuesta en un gen real.

Uso:  python src/phasing_span_stats.py RUTA.vcf.gz
"""
import gzip, sys, collections

path = sys.argv[1]

fmt_cache = {}
blocks = {}            # (chrom, PID) -> [min_pos, max_pos, n]
n_var = n_phased = 0

with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) < 10:
            continue
        n_var += 1
        fmt, smp = p[8], p[9]
        idx = fmt_cache.get(fmt)
        if idx is None:
            keys = fmt.split(":")
            idx = keys.index("PID") if "PID" in keys else -1
            fmt_cache[fmt] = idx
        if idx < 0:
            continue
        vals = smp.split(":")
        if idx >= len(vals):
            continue
        pid = vals[idx]
        if pid in (".", ""):
            continue
        n_phased += 1
        pos = int(p[1])
        key = (p[0], pid)
        b = blocks.get(key)
        if b is None:
            blocks[key] = [pos, pos, 1]
        else:
            if pos < b[0]: b[0] = pos
            if pos > b[1]: b[1] = pos
            b[2] += 1

spans  = sorted(b[1] - b[0] for b in blocks.values())
counts = sorted(b[2] for b in blocks.values())

def pct(sorted_list, q):
    if not sorted_list:
        return 0
    return sorted_list[min(len(sorted_list) - 1, int(q * len(sorted_list)))]

print("=" * 66)
print("ALCANCE REAL DE LA FASE FISICA (PGT/PID)  —  solo agregados")
print("=" * 66)
print(f"  variantes totales        : {n_var:,}")
print(f"  variantes con PID        : {n_phased:,}  ({100*n_phased/max(n_var,1):.2f} %)")
print(f"  bloques de fase          : {len(blocks):,}")
if blocks:
    print(f"\n  variantes por bloque")
    print(f"    mediana                : {pct(counts,.5)}")
    print(f"    p90 / p99              : {pct(counts,.9)} / {pct(counts,.99)}")
    print(f"    maximo                 : {counts[-1]}")
    print(f"\n  envergadura del bloque (pb)")
    for q, et in ((.5, "mediana"), (.75, "p75"), (.9, "p90"), (.99, "p99")):
        print(f"    {et:<22} : {pct(spans,q):,}")
    print(f"    maximo                 : {spans[-1]:,}")
    for umbral in (150, 300, 1000, 5000, 20000):
        n = sum(1 for s in spans if s >= umbral)
        print(f"    bloques >= {umbral:>6,} pb   : {n:,}  ({100*n/len(spans):.2f} %)")
print()
