#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QC sobre una muestra de la cabecera del FASTQ. No alinea, no escribe secuencias
del paciente: solo agregados y patrones tecnicos conocidos (adaptador, polyG).

Los duplicados se clasifican pero NUNCA se imprime la secuencia si es genomica
(Regla Dura 1). Los identificadores de muestra e indice se muestran en consola
para el operador, pero no deben copiarse a ningun fichero versionado.

Lee de stdin. Uso:
  zcat X_R1.fastq.gz | head -n 8000000 | python src/qc_fastq_sample.py R1

Para el conteo EXACTO sobre el fichero completo (no muestra), la pasada es:
  zcat X_R1.fastq.gz | awk 'NR%4==2{n++;b+=length($0);L[length($0)]++}
    END{print "READS",n; print "BASES",b; for(k in L) print "LEN",k,L[k]}'

Resultados de la ejecucion sobre L001: docs/QC_L001.md
"""
import sys, collections
import numpy as np

tag = sys.argv[1] if len(sys.argv) > 1 else "?"
N_QUAL = 1_000_000      # reads para calidad por posicion
N_DUP  = 1_000_000      # reads para proxy de duplicacion

ADAPTERS = {
    "TruSeq/universal": b"AGATCGGAAGAGC",
    "Nextera":          b"CTGTCTCTTATACACATCT",
    "polyG(2-color)":   b"GGGGGGGGGGGGGGGGGGGG",
}

reads = 0
bases = 0
n_count = 0
gc_count = 0
lens = collections.Counter()
qual_min, qual_max = 255, 0
adapter_hits = collections.Counter()
dup_keys = collections.Counter()
qual_rows = []
first_header = None
tiles = set()
inst = run = fc = lane = index_seq = None

inp = sys.stdin.buffer
while True:
    h = inp.readline()
    if not h:
        break
    s = inp.readline().rstrip(b"\n\r")
    inp.readline()
    q = inp.readline().rstrip(b"\n\r")
    if not q:
        break

    reads += 1
    L = len(s)
    bases += L
    lens[L] += 1
    n_count += s.count(b"N")
    gc_count += s.count(b"G") + s.count(b"C") + s.count(b"g") + s.count(b"c")

    if first_header is None:
        first_header = h.decode("ascii", "replace").strip()
        parts = first_header.lstrip("@").split(":")
        if len(parts) >= 7:
            inst, run, fc, lane = parts[0], parts[1], parts[2], parts[3]
        if " " in first_header:
            f2 = first_header.split(" ", 1)[1].split(":")
            if len(f2) >= 4:
                index_seq = f2[3]

    # tile: campo 5 del header
    try:
        tiles.add(h.split(b":")[4])
    except Exception:
        pass

    for name, seq in ADAPTERS.items():
        if seq in s:
            adapter_hits[name] += 1

    if reads <= N_DUP:
        dup_keys[s[:50]] += 1

    if reads <= N_QUAL:
        qb = np.frombuffer(q, dtype=np.uint8)
        if qb.size:
            lo, hi = int(qb.min()), int(qb.max())
            qual_min = min(qual_min, lo)
            qual_max = max(qual_max, hi)
        qual_rows.append(q)

# --- calidad por posicion ---
modal_len = lens.most_common(1)[0][0] if lens else 0
sel = [r for r in qual_rows if len(r) == modal_len]
per_pos = None
mean_q = None
if sel:
    arr = np.frombuffer(b"".join(sel), dtype=np.uint8).reshape(len(sel), modal_len).astype(np.int16) - 33
    per_pos = arr.mean(axis=0)
    mean_q = float(arr.mean())
    # fraccion de bases >= Q30 (sobre la muestra)
    q30 = float((arr >= 30).mean()) * 100
    q20 = float((arr >= 20).mean()) * 100
else:
    q30 = q20 = float("nan")

dup_total = sum(dup_keys.values())
dup_unique = len(dup_keys)
dup_rate = 100.0 * (1 - dup_unique / dup_total) if dup_total else 0.0

def clasifica(seq_bytes):
    """Solo etiquetamos patrones tecnicos. Nunca imprimimos secuencia genomica."""
    t = seq_bytes.decode("ascii", "replace")
    if t.count("G") >= len(t) * 0.9:
        return "polyG (artefacto 2-color)"
    if t.count("N") >= len(t) * 0.5:
        return "polyN"
    for name, ad in ADAPTERS.items():
        if ad.decode() in t:
            return "adaptador " + name
    return "secuencia genomica (no se imprime)"

print("=" * 62)
print(f"MUESTRA {tag}  —  {reads:,} reads leidos de la cabecera del fichero")
print("=" * 62)
print(f"  longitudes            : {dict(lens.most_common(6))}")
print(f"  longitud modal        : {modal_len} bp")
print(f"  bases (muestra)       : {bases:,}")
print(f"  GC                    : {100*gc_count/bases:.2f} %")
print(f"  N                     : {100*n_count/bases:.5f} %")
print(f"  Phred rango observado : {qual_min}..{qual_max}  -> "
      f"{'Phred+33 (Illumina 1.8+)' if qual_min >= 33 and qual_max <= 75 else 'REVISAR codificacion'}")
if mean_q is not None:
    print(f"  calidad media         : Q{mean_q:.2f}")
    print(f"  bases >= Q30          : {q30:.2f} %")
    print(f"  bases >= Q20          : {q20:.2f} %")
print(f"  duplicacion aprox     : {dup_rate:.2f} %  (primeros 50 bp, {dup_total:,} reads)")
print(f"  tiles distintos       : {len(tiles)}")
print(f"  instrumento/run       : {inst} / run {run} / flowcell {fc} / lane {lane}")
print(f"  indice                : {index_seq}")
print(f"  adaptadores (conteo sobre {reads:,} reads):")
for name in ADAPTERS:
    c = adapter_hits.get(name, 0)
    print(f"      {name:<20} {c:>10,}  ({100*c/reads:.4f} %)")
print("  top duplicados (clasificados, sin imprimir secuencia genomica):")
for seq, c in dup_keys.most_common(3):
    print(f"      {c:>9,} x  {clasifica(seq)}")

if per_pos is not None:
    print("  calidad media por ciclo (agrupada de 10 en 10):")
    line = []
    for i in range(0, modal_len, 10):
        line.append(f"{i+1:>3}-{min(i+10,modal_len):<3}:Q{per_pos[i:i+10].mean():.1f}")
    for i in range(0, len(line), 5):
        print("      " + "  ".join(line[i:i+5]))
    worst = int(np.argmin(per_pos))
    print(f"  peor ciclo            : {worst+1} (Q{per_pos[worst]:.1f})")
    print(f"  ultimo ciclo          : Q{per_pos[-1]:.1f}")
print()
