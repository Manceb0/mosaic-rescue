#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Censo del VCF sin anotacion. Produce los niveles superiores del funnel con
numeros reales: filtros, clase de variante, genotipos, balance alelico y
distribucion por contig.

Salida EXCLUSIVAMENTE agregada. No imprime coordenadas, genotipos individuales
ni secuencia (Regla Dura 1).

Uso:  python src/vcf_variant_census.py RUTA.vcf.gz
"""
import gzip, sys, collections

path = sys.argv[1]

PRIMARY = {str(i) for i in range(1, 23)} | {"X", "Y", "MT", "M", "chrM"}

filters   = collections.Counter()
klass     = collections.Counter()
gts       = collections.Counter()
contigcls = collections.Counter()
ab_hist   = collections.Counter()     # balance alelico de heterocigotas, en pasos de 0.05
dp_hist   = collections.Counter()     # profundidad, agrupada
n = 0
n_multi = 0
ab_n = 0
fmt_cache = {}

with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        if line[0] == "#":
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) < 10:
            continue
        n += 1
        chrom, ref, alt, filt, fmt, smp = p[0], p[3], p[4], p[6], p[8], p[9]

        # --- filtros ---
        for tok in filt.split(";"):
            filters[tok] += 1

        # --- contig ---
        contigcls["primario" if chrom in PRIMARY else "no colocado / decoy"] += 1

        # --- clase de variante ---
        alts = alt.split(",")
        if len(alts) > 1:
            n_multi += 1
            klass["multialelica"] += 1
        else:
            a = alts[0]
            if len(ref) == 1 and len(a) == 1:
                klass["SNV"] += 1
            elif len(ref) == len(a):
                klass["MNV"] += 1
            elif len(ref) < len(a):
                klass["insercion"] += 1
            else:
                klass["delecion"] += 1

        # --- genotipo, AD, DP ---
        idx = fmt_cache.get(fmt)
        if idx is None:
            k = fmt.split(":")
            idx = (k.index("GT") if "GT" in k else -1,
                   k.index("AD") if "AD" in k else -1,
                   k.index("DP") if "DP" in k else -1)
            fmt_cache[fmt] = idx
        gi, ai, di = idx
        v = smp.split(":")

        gt = v[gi] if 0 <= gi < len(v) else "./."
        gtn = gt.replace("|", "/")
        gts[gtn if gtn in ("0/1", "1/1", "0/0", "./.", "1/2") else "otro"] += 1

        if 0 <= di < len(v) and v[di].isdigit():
            d = int(v[di])
            b = 0 if d == 0 else min(200, (d // 10) * 10)
            dp_hist[b] += 1

        # balance alelico solo en heterocigotas bialelicas con AD utilizable
        if gtn == "0/1" and 0 <= ai < len(v) and len(alts) == 1:
            try:
                r, a_ = v[ai].split(",")[:2]
                r, a_ = int(r), int(a_)
                if r + a_ >= 10:
                    ab = a_ / (r + a_)
                    ab_hist[round(ab * 20) / 20] += 1
                    ab_n += 1
            except (ValueError, ZeroDivisionError):
                pass

print("=" * 68)
print("CENSO DEL VCF (sin anotacion)  —  solo agregados")
print("=" * 68)
print(f"  variantes totales : {n:,}")

print("\n[1] FILTROS")
for k_, c in filters.most_common():
    print(f"    {k_:<20} {c:>10,}  ({100*c/n:.2f} %)")
npass = filters.get("PASS", 0)
print(f"\n    >>> nivel primario (PASS)   : {npass:,}")
print(f"    >>> nivel de rescate        : {n-npass:,}")

print("\n[2] CLASE DE VARIANTE")
for k_, c in klass.most_common():
    print(f"    {k_:<20} {c:>10,}  ({100*c/n:.2f} %)")

print("\n[3] CONTIG")
for k_, c in contigcls.most_common():
    print(f"    {k_:<20} {c:>10,}  ({100*c/n:.2f} %)")

print("\n[4] GENOTIPO")
for k_, c in gts.most_common():
    print(f"    {k_:<20} {c:>10,}  ({100*c/n:.2f} %)")
het, hom = gts.get("0/1", 0), gts.get("1/1", 0)
if hom:
    print(f"\n    ratio het/hom : {het/hom:.2f}   (esperado ~1,5-2,0 en WGS humano)")

print(f"\n[5] BALANCE ALELICO — heterocigotas bialelicas, DP>=10  (n={ab_n:,})")
if ab_hist:
    tot = sum(ab_hist.values())
    for b in sorted(ab_hist):
        c = ab_hist[b]
        if c / tot >= 0.004:
            bar = "#" * int(60 * c / max(ab_hist.values()))
            print(f"    {b:.2f}  {c:>9,}  {bar}")
    centro = sum(c for b, c in ab_hist.items() if 0.40 <= b <= 0.60)
    bajo   = sum(c for b, c in ab_hist.items() if b < 0.30)
    print(f"\n    en 0,40-0,60 : {100*centro/tot:.2f} %   (heterocigosis germinal limpia)")
    print(f"    por debajo de 0,30 : {100*bajo/tot:.2f} %   (mosaicismo o artefacto: NO distinguible aqui)")

print("\n[6] PROFUNDIDAD")
if dp_hist:
    tot = sum(dp_hist.values())
    acc = 0
    med = None
    for b in sorted(dp_hist):
        acc += dp_hist[b]
        if med is None and acc >= tot / 2:
            med = b
    print(f"    mediana (agrupada de 10 en 10) : ~{med}x")
    baja = sum(c for b, c in dp_hist.items() if b < 10)
    print(f"    variantes con DP < 10          : {baja:,}  ({100*baja/tot:.2f} %)")
print()
