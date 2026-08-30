#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye el funnel genomico a partir de la salida de VEP pasada 1 y cruza
los tres carriles: MVA, renal y escape genome-wide.

Cuenta a nivel de VARIANTE, no de fila. `--pick_allele_gene` emite una fila por
alelo y gen, asi que una variante entre dos genes produce dos filas: contar filas
inflaria el funnel.

Salida agregada, mas un detalle acotado de los candidatos de los paneles con
FILTER/GT/DP/AD tomados del VCF. Ese detalle SI incluye genotipo y por eso se
escribe a work/ (ignorado por Git), nunca a docs/.

Uso:  python src/build_funnel.py VEP.tsv VCF.gz
"""
import sys, gzip, collections, io, os

vep_tsv, vcf = sys.argv[1], sys.argv[2]

def load_panel(p):
    genes = set()
    for line in io.open(p, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if line:
            genes.add(line.upper())
    return genes

MVA   = load_panel("config/panels/mva.txt")
RENAL = load_panel("config/panels/nephrocalcinosis.txt")

RANK = {"HIGH": 3, "MODERATE": 2, "LOW": 1, "MODIFIER": 0}

var_impact = {}                       # variante -> mejor IMPACT (rango)
cons_count = collections.Counter()    # a nivel de fila
impact_rows = collections.Counter()
panel_hits = collections.defaultdict(list)   # (carril, gen) -> [filas]
highs = collections.Counter()         # gen -> nº de variantes HIGH (genome-wide)
high_vars = collections.defaultdict(set)
n_rows = 0

with io.open(vep_tsv, encoding="utf-8", errors="replace") as f:
    hdr = None
    for line in f:
        if line.startswith("##"):
            continue
        if line.startswith("#"):
            hdr = line[1:].rstrip("\n").split("\t")
            ix = {k: i for i, k in enumerate(hdr)}
            continue
        n_rows += 1
        p = line.rstrip("\n").split("\t")
        try:
            var = p[ix["Uploaded_variation"]]
            sym = p[ix["SYMBOL"]].upper()
            con = p[ix["Consequence"]]
            imp = p[ix["IMPACT"]]
        except (IndexError, KeyError):
            continue

        cons_count[con] += 1
        impact_rows[imp] += 1
        r = RANK.get(imp, 0)
        if var_impact.get(var, -1) < r:
            var_impact[var] = r

        if imp == "HIGH":
            highs[sym] += 1
            high_vars[sym].add(var)

        if sym in MVA:
            panel_hits[("MVA", sym)].append((var, con, imp, p))
        if sym in RENAL:
            panel_hits[("RENAL", sym)].append((var, con, imp, p))

n_vars = len(var_impact)
by_impact = collections.Counter()
for v, r in var_impact.items():
    by_impact[{3: "HIGH", 2: "MODERATE", 1: "LOW", 0: "MODIFIER"}[r]] += 1

print("=" * 70)
print("THE GENOMIC FUNNEL — pasada 1 de VEP, sin filtro de frecuencia")
print("=" * 70)
print(f"  variantes en el VCF        : 5,012,204")
print(f"  variantes anotadas         : {n_vars:,}")
print(f"  filas de anotacion         : {n_rows:,}   (>1 por variante: alelo x gen)")

print("\n[IMPACT — por VARIANTE, tomando el maximo]")
tot = sum(by_impact.values())
for k in ("HIGH", "MODERATE", "LOW", "MODIFIER"):
    c = by_impact.get(k, 0)
    print(f"    {k:<10} {c:>10,}  ({100*c/tot:.3f} %)")

print("\n[CONSECUENCIAS mas frecuentes — por fila]")
for k, c in cons_count.most_common(14):
    print(f"    {k:<44} {c:>10,}")

# --- carriles de panel ---
def lane(name, panel):
    print(f"\n{'='*70}\nCARRIL · {name}   ({len(panel)} genes en el panel)\n{'='*70}")
    genes = sorted({g for (l, g) in panel_hits if l == name})
    if not genes:
        print("    sin variantes anotadas en genes del panel")
        return {}
    resumen = {}
    for g in genes:
        rows = panel_hits[(name, g)]
        vs = {r[0] for r in rows}
        imps = collections.Counter(r[2] for r in rows)
        hi = {r[0] for r in rows if r[2] == "HIGH"}
        mo = {r[0] for r in rows if r[2] == "MODERATE"}
        resumen[g] = (len(vs), len(hi), len(mo))
    print(f"  {'GEN':<12} {'variantes':>10} {'HIGH':>6} {'MODERATE':>9}")
    for g in sorted(resumen, key=lambda x: (-resumen[x][1], -resumen[x][2], x)):
        v, h, m = resumen[g]
        marca = "  <<<" if h else ""
        print(f"  {g:<12} {v:>10,} {h:>6} {m:>9}{marca}")
    th = sum(r[1] for r in resumen.values())
    tm = sum(r[2] for r in resumen.values())
    print(f"\n  >>> TOTAL {name}:  HIGH={th}   MODERATE={tm}")
    return resumen

res_mva   = lane("MVA", MVA)
res_renal = lane("RENAL", RENAL)

# --- carril genome-wide ---
print(f"\n{'='*70}\nCARRIL · ESCAPE GENOME-WIDE (sin panel, sin filtro de frecuencia)\n{'='*70}")
tot_high = by_impact.get("HIGH", 0)
print(f"  variantes de alto impacto en todo el genoma : {tot_high:,}")
print(f"  genes distintos con >=1 HIGH                : {len(highs):,}")
g2 = {g: len(v) for g, v in high_vars.items() if len(v) >= 2}
print(f"  genes con >=2 variantes HIGH                : {len(g2):,}")
print("\n  Sin filtro de frecuencia poblacional esto es RUIDO, no señal:")
print("  la mayoria seran variantes comunes y errores de anotacion en")
print("  pseudogenes y transcritos mal soportados. gnomAD es pasada 2.")

# --- detalle de candidatos de panel, con FILTER/GT del VCF ---
want = set()
for (l, g), rows in panel_hits.items():
    for r in rows:
        if r[2] in ("HIGH", "MODERATE"):
            want.add(r[0])

if want:
    print(f"\n{'='*70}\nDETALLE — {len(want)} variantes HIGH/MODERATE de panel, cruzadas con el VCF")
    print("=" * 70)
    key2vcf = {}
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line[0] == "#":
                continue
            p = line.rstrip("\n").split("\t")
            for a in p[4].split(","):
                k = f"{p[0]}_{p[1]}_{p[3]}/{a}"
                if k in want:
                    key2vcf[k] = p
    os.makedirs("work/lanes", exist_ok=True)
    out = io.open("work/lanes/panel_candidates.tsv", "w", encoding="utf-8", newline="\n")
    out.write("carril\tgen\tvariante\tconsecuencia\timpacto\tFILTER\tGT\tDP\tAD\tHGVSc\tHGVSp\n")
    shown = 0
    for (l, g), rows in sorted(panel_hits.items()):
        for var, con, imp, p in rows:
            if imp not in ("HIGH", "MODERATE"):
                continue
            v = key2vcf.get(var)
            if v:
                fmt = v[8].split(":"); sm = v[9].split(":")
                d = dict(zip(fmt, sm))
                filt, gt, dp, ad = v[6], d.get("GT", "?"), d.get("DP", "?"), d.get("AD", "?")
            else:
                filt = gt = dp = ad = "?"
            hgvsc = p[ix["HGVSc"]] if "HGVSc" in ix and ix["HGVSc"] < len(p) else "-"
            hgvsp = p[ix["HGVSp"]] if "HGVSp" in ix and ix["HGVSp"] < len(p) else "-"
            out.write(f"{l}\t{g}\t{var}\t{con}\t{imp}\t{filt}\t{gt}\t{dp}\t{ad}\t{hgvsc}\t{hgvsp}\n")
            shown += 1
    out.close()
    print(f"  escrito: work/lanes/panel_candidates.tsv  ({shown} filas)")
    print("  (contiene genotipos: NO se versiona, work/ esta en .gitignore)")

    # resumen agregado, seguro para consola
    print("\n  Recuento por gen y FILTER:")
    agg = collections.Counter()
    for (l, g), rows in panel_hits.items():
        for var, con, imp, p in rows:
            if imp in ("HIGH", "MODERATE"):
                v = key2vcf.get(var)
                agg[(l, g, imp, v[6] if v else "?")] += 1
    for k in sorted(agg):
        l, g, imp, filt = k
        print(f"    {l:<6} {g:<12} {imp:<9} {filt:<16} {agg[k]}")
print()
