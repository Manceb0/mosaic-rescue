#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AlphaGenome sobre UN candidato no codificante de la shortlist.

AVISO DE GOBERNANZA. A diferencia del resto del pipeline, esta llamada NO es
offline: envia la coordenada y los alelos de la variante a la API de Google
DeepMind. Es el unico paso del proyecto que transmite dato del paciente fuera
de la maquina, y esta previsto en docs/03_ALPHAGENOME_ASSESSMENT.md §7:
solo la shortlist priorizada, nunca el VCF.

Salida: REF, ALT y DELTA por modalidad. TODO se etiqueta PREDICTED.
No mide expresion: la infiere.

Uso (con el venv aislado):
  work/venv-ag/Scripts/python.exe src/run_alphagenome.py CHR POS REF ALT
"""
import io, os, sys, json
import numpy as np
from alphagenome.models import dna_client
from alphagenome.data import genome

CHR, POS, REF, ALT = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]

# clave desde .env, nunca en codigo ni en logs
key = None
for line in io.open(".env", encoding="utf-8"):
    if line.startswith("ALPHAGENOME_API_KEY="):
        key = line.split("=", 1)[1].strip()
if not key:
    sys.exit("falta ALPHAGENOME_API_KEY en .env")

WIN = dna_client.SEQUENCE_LENGTH_1MB
half = WIN // 2
interval = genome.Interval(chromosome=CHR, start=POS - half, end=POS - half + WIN)
variant = genome.Variant(chromosome=CHR, position=POS,
                         reference_bases=REF, alternate_bases=ALT)

OUTS = [dna_client.OutputType.RNA_SEQ,
        dna_client.OutputType.SPLICE_SITES,
        dna_client.OutputType.SPLICE_SITE_USAGE,
        dna_client.OutputType.SPLICE_JUNCTIONS,
        dna_client.OutputType.ATAC,
        dna_client.OutputType.DNASE,
        dna_client.OutputType.CHIP_TF,
        dna_client.OutputType.CHIP_HISTONE]

print(f"  ventana   {interval.chromosome}:{interval.start:,}-{interval.end:,}  ({WIN//1024} kb)")
print(f"  variante  {CHR}:{POS} {REF}>{ALT}")
print("  -> llamando a la API de AlphaGenome (dato del paciente sale de la maquina)")

model = dna_client.create(key)
out = model.predict_variant(interval=interval, variant=variant,
                            requested_outputs=OUTS, ontology_terms=None)

def summarize(name, ref_td, alt_td):
    """Delta por modalidad. Resumimos con estadisticos, no con un solo numero."""
    if ref_td is None or alt_td is None:
        return None
    r = np.asarray(ref_td.values, dtype=np.float32)
    a = np.asarray(alt_td.values, dtype=np.float32)
    if r.shape != a.shape or r.size == 0:
        return None
    d = a - r
    absd = np.abs(d)
    # ventana local: +-2 kb alrededor de la variante, en bins
    n = r.shape[0]
    center = n // 2
    w = max(1, int(2000 / (WIN / n)))
    loc = absd[max(0, center - w):center + w]
    return dict(
        modalidad=name,
        pistas=int(r.shape[1]) if r.ndim > 1 else 1,
        ref_media=float(np.nanmean(r)),
        alt_media=float(np.nanmean(a)),
        delta_max_abs=float(np.nanmax(absd)),
        delta_medio_abs=float(np.nanmean(absd)),
        delta_local_max=float(np.nanmax(loc)) if loc.size else 0.0,
        delta_rel=float(np.nanmax(absd) / (np.nanmax(np.abs(r)) + 1e-9)),
    )

res = []
for name in ("rna_seq", "splice_sites", "splice_site_usage", "splice_junctions",
             "atac", "dnase", "chip_tf", "chip_histone"):
    s = summarize(name, getattr(out.reference, name, None), getattr(out.alternate, name, None))
    if s: res.append(s)

print(f"\n{'='*78}")
print("ALPHAGENOME — PREDICTED. No es medicion: no hay RNA-seq de este paciente.")
print("="*78)
print(f"  {'modalidad':<20}{'pistas':>7}{'|d| max':>12}{'|d| medio':>12}{'|d| local':>12}{'d rel':>9}")
for s in res:
    print(f"  {s['modalidad']:<20}{s['pistas']:>7}{s['delta_max_abs']:>12.4f}"
          f"{s['delta_medio_abs']:>12.6f}{s['delta_local_max']:>12.4f}{s['delta_rel']:>9.4f}")

os.makedirs("work/alphagenome", exist_ok=True)
io.open(f"work/alphagenome/{CHR}_{POS}_{REF}_{ALT}.json", "w", encoding="utf-8").write(
    json.dumps({"variant": f"{CHR}:{POS}{REF}>{ALT}", "window_bp": WIN,
                "status": "PREDICTED", "modalities": res}, indent=2, ensure_ascii=False))
print(f"\n  -> work/alphagenome/{CHR}_{POS}_{REF}_{ALT}.json")
