#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tercera pasada de AlphaGenome sobre la MISMA variante ya transmitida.
Guarda los ARRAYS de las pistas preseleccionadas para poder dibujar REF/ALT/Delta
de verdad, en vez de una tabla de porcentajes.

La seleccion esta CONGELADA en docs/DECISIONS.md antes de esta ejecucion.

Uso: work/venv-ag/Scripts/python.exe src/alphagenome_arrays.py CHR POS REF ALT
"""
import io, sys, json, os
import numpy as np
from alphagenome.models import dna_client
from alphagenome.data import genome

CHR, POS, REF, ALT = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
key = next(l.split("=", 1)[1].strip() for l in io.open(".env", encoding="utf-8")
           if l.startswith("ALPHAGENOME_API_KEY="))

WIN = dna_client.SEQUENCE_LENGTH_1MB
half = WIN // 2
interval = genome.Interval(chromosome=CHR, start=POS - half, end=POS - half + WIN)
variant = genome.Variant(chromosome=CHR, position=POS, reference_bases=REF, alternate_bases=ALT)
OUTS = [dna_client.OutputType.RNA_SEQ, dna_client.OutputType.SPLICE_SITES,
        dna_client.OutputType.SPLICE_SITE_USAGE, dna_client.OutputType.SPLICE_JUNCTIONS,
        dna_client.OutputType.ATAC, dna_client.OutputType.DNASE,
        dna_client.OutputType.CHIP_TF]

print(f"  ventana {interval.chromosome}:{interval.start:,}-{interval.end:,}")
model = dna_client.create(key)
out = model.predict_variant(interval=interval, variant=variant,
                            requested_outputs=OUTS, ontology_terms=None)

BASE_MIN = 0.01          # umbral de linea base, preregistrado
FLANK = 5000             # +-5 kb dibujados

def meta_of(td, i):
    try:
        row = td.metadata.iloc[i]
        for k in ("name", "biosample_name", "ontology_curie"):
            if k in row and str(row[k]) not in ("nan", ""):
                bits = [str(row.get(x, "")) for x in ("name", "biosample_name") if x in row]
                return " · ".join(b for b in bits if b and b != "nan")[:60]
    except Exception:
        pass
    return f"pista {i}"

def window(td):
    a = np.asarray(td.values, dtype=np.float32)
    n = a.shape[0]
    bp_per_bin = WIN / n
    w = max(4, int(FLANK / bp_per_bin))
    c = n // 2
    return a[max(0, c - w): c + w], bp_per_bin, w

selected = []

def add(mod, idx, why):
    r_td = getattr(out.reference, mod); a_td = getattr(out.alternate, mod)
    R, bpb, w = window(r_td); A, _, _ = window(a_td)
    if R.ndim < 2:
        return
    ref = R[:, idx]; alt = A[:, idx]
    selected.append(dict(mod=mod, idx=int(idx), why=why, meta=meta_of(r_td, idx),
                         bp_per_bin=float(bpb), flank_bins=int(w),
                         ref=[round(float(x), 6) for x in ref],
                         alt=[round(float(x), 6) for x in alt]))

# --- splicing: las tres, obligatorias. Se toma la pista de mayor |d| local ---
for mod in ("splice_sites", "splice_site_usage", "splice_junctions"):
    td = getattr(out.reference, mod, None)
    if td is None:
        continue
    R, _, _ = window(td); A, _, _ = window(getattr(out.alternate, mod))
    if R.ndim < 2:
        continue
    d = np.abs(A - R).max(axis=0)
    add(mod, int(np.argmax(d)), "obligatoria")

# --- CTCF y RAD21: mayores cambios absolutos en la pasada anterior ---
td = getattr(out.reference, "chip_tf", None)
if td is not None:
    R, _, _ = window(td); A, _, _ = window(out.alternate.chip_tf)
    d = np.abs(A - R).max(axis=0)
    for tf in ("CTCF", "RAD21"):
        cand = [i for i in range(R.shape[1]) if tf.lower() in meta_of(td, i).lower()]
        if cand:
            add("chip_tf", max(cand, key=lambda i: d[i]), f"mayor |d| absoluto · {tf}")

# --- RNA: las 2 mayores CON linea base suficiente ---
td = out.reference.rna_seq
R, _, _ = window(td); A, _, _ = window(out.alternate.rna_seq)
d = np.abs(A - R).max(axis=0); base = np.abs(R).max(axis=0)
ok = [i for i in range(R.shape[1]) if base[i] >= BASE_MIN]
print(f"  pistas RNA con linea base >= {BASE_MIN}: {len(ok)} de {R.shape[1]}")
for i in sorted(ok, key=lambda i: -d[i])[:2]:
    add("rna_seq", i, f"mayor |d| con base >= {BASE_MIN}")

# --- ATAC y DNase representativas, mismo minimo ---
for mod in ("atac", "dnase"):
    td = getattr(out.reference, mod, None)
    if td is None:
        continue
    R, _, _ = window(td); A, _, _ = window(getattr(out.alternate, mod))
    d = np.abs(A - R).max(axis=0); base = np.abs(R).max(axis=0)
    ok = [i for i in range(R.shape[1]) if base[i] >= BASE_MIN]
    if ok:
        add(mod, max(ok, key=lambda i: d[i]), f"representativa · base >= {BASE_MIN}")

print(f"\n  pistas guardadas: {len(selected)}")
for s in selected:
    r = np.array(s["ref"]); a = np.array(s["alt"])
    print(f"    {s['mod']:<18} max|d|={np.abs(a-r).max():.4f}  base={np.abs(r).max():.4f}  {s['meta'][:44]}")

os.makedirs("work/alphagenome", exist_ok=True)
json.dump(dict(variant=f"{CHR}:{POS}{REF}>{ALT}", pos=POS, chrom=CHR, flank_bp=FLANK,
               status="PREDICTED", base_min=BASE_MIN, tracks=selected),
          io.open(f"work/alphagenome/arrays_{POS}.json", "w", encoding="utf-8"))
print(f"\n  -> work/alphagenome/arrays_{POS}.json")
