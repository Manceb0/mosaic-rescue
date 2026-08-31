#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Segunda pasada de AlphaGenome sobre la MISMA variante ya transmitida:
en vez de agregar, saca las pistas individuales mas alteradas con su contexto.

Un efecto fuerte en un solo tejido puede diluirse en la media de 1 617 pistas.
Esto comprueba si existe.

Uso: work/venv-ag/Scripts/python.exe src/alphagenome_tracks.py CHR POS REF ALT
"""
import io, sys, json, os
import numpy as np
from alphagenome.models import dna_client
from alphagenome.data import genome

CHR, POS, REF, ALT = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
key = next(l.split("=",1)[1].strip() for l in io.open(".env",encoding="utf-8")
           if l.startswith("ALPHAGENOME_API_KEY="))
WIN = dna_client.SEQUENCE_LENGTH_1MB
half = WIN // 2
interval = genome.Interval(chromosome=CHR, start=POS-half, end=POS-half+WIN)
variant  = genome.Variant(chromosome=CHR, position=POS, reference_bases=REF, alternate_bases=ALT)
OUTS = [dna_client.OutputType.RNA_SEQ, dna_client.OutputType.SPLICE_SITES,
        dna_client.OutputType.SPLICE_SITE_USAGE, dna_client.OutputType.SPLICE_JUNCTIONS,
        dna_client.OutputType.ATAC, dna_client.OutputType.DNASE,
        dna_client.OutputType.CHIP_TF, dna_client.OutputType.CHIP_HISTONE]
model = dna_client.create(key)
out = model.predict_variant(interval=interval, variant=variant,
                            requested_outputs=OUTS, ontology_terms=None)

allrows=[]
for name in ("rna_seq","splice_sites","splice_site_usage","splice_junctions",
             "atac","dnase","chip_tf","chip_histone"):
    r_td=getattr(out.reference,name,None); a_td=getattr(out.alternate,name,None)
    if r_td is None or a_td is None: continue
    r=np.asarray(r_td.values,dtype=np.float32); a=np.asarray(a_td.values,dtype=np.float32)
    if r.shape!=a.shape or r.ndim<2: continue
    n=r.shape[0]; c=n//2; w=max(1,int(2000/(WIN/n)))
    lo,hi=max(0,c-w),min(n,c+w)
    # por pista: maximo |delta| LOCAL y su valor de referencia local
    dloc=np.abs(a[lo:hi]-r[lo:hi]).max(axis=0)
    rloc=np.abs(r[lo:hi]).max(axis=0)
    rel=dloc/(rloc+1e-9)
    md=getattr(r_td,"metadata",None)
    def meta(i):
        try:
            row=md.iloc[i]
            bits=[str(row.get(k,"")) for k in ("name","biosample_name","ontology_curie","strand") if k in row]
            return " | ".join([b for b in bits if b and b!="nan"])[:76]
        except Exception:
            return f"pista {i}"
    for i in range(r.shape[1]):
        allrows.append(dict(mod=name, idx=i, dloc=float(dloc[i]),
                            rloc=float(rloc[i]), rel=float(rel[i]), meta=meta(i)))

allrows.sort(key=lambda x:-x["rel"])
print("="*94)
print("ALPHAGENOME — PISTAS INDIVIDUALES, ventana local +-2 kb.  PREDICTED.")
print("="*94)
print(f"  pistas evaluadas: {len(allrows):,}")
print(f"\n  TOP 20 por cambio RELATIVO local\n")
print(f"  {'modalidad':<18}{'|d| local':>11}{'ref local':>11}{'rel':>9}   contexto")
for r in allrows[:20]:
    print(f"  {r['mod']:<18}{r['dloc']:>11.4f}{r['rloc']:>11.4f}{r['rel']:>9.4f}   {r['meta']}")
print(f"\n  TOP 10 por cambio ABSOLUTO local\n")
for r in sorted(allrows,key=lambda x:-x["dloc"])[:10]:
    print(f"  {r['mod']:<18}{r['dloc']:>11.4f}{r['rloc']:>11.4f}{r['rel']:>9.4f}   {r['meta']}")
os.makedirs("work/alphagenome",exist_ok=True)
json.dump({"variant":f"{CHR}:{POS}{REF}>{ALT}","status":"PREDICTED",
           "top_rel":allrows[:60]},
          io.open(f"work/alphagenome/{CHR}_{POS}_tracks.json","w",encoding="utf-8"),indent=2)
print(f"\n  -> work/alphagenome/{CHR}_{POS}_tracks.json")
