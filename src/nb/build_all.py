#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstruye y ejecuta LOS OCHO notebooks, y emite la matriz de verificacion.

DEFINICION DE HECHO, cambiada en la pasada visual. El motivo:
  El criterio anterior era «al menos N figuras embebidas». Ese requisito produjo
  relleno: cajas, flechas y estados dibujados con Matplotlib para llegar al
  numero. El criterio ahora es cualitativo y mas duro:

  - ejecuta de arriba abajo sin errores;
  - contiene al menos una figura cientifica embebida, entendiendo por cientifica
    la que su propio caption declara DATA, MODEL_OUTPUT, SIMULATION o
    CURATED_EVIDENCE;
  - pasa el escaner de saneado sobre lo versionado.

  Una figura SYNTHESIS o NARRATIVE sigue siendo legitima y util. Lo que ya no
  puede es contar para el minimo.

Uso:  python src/nb/build_all.py
"""
from __future__ import annotations
import sys, subprocess, importlib

sys.path.insert(0, ".")

# (modulo, notebook, objeto cientifico principal, pregunta)
NOTEBOOKS = [
    ("nb00_data_reality",  "00_DATA_REALITY",
     "QC de FASTQ por ciclo, calculado sobre L001",
     "Que se puede y que no responder con los datos que hay"),
    ("nb01_track1",        "01_TRACK1_GENOME_WIDE",
     "Manhattan de priorizacion genome-wide sobre A0 congelado",
     "Que gen explica el caso cuando compite todo el genoma codificante"),
    ("nb02_alleles",       "02_BUB1B_ALLELE_CURATION",
     "Navegador del gen: exones, dominios y 1 497 missense de ClinVar",
     "Que sostiene cada alelo, y que haria falta para que el par sea causal"),
    ("nb03_mechanism",     "03_BUBR1_MECHANISM",
     "Bolsillo de AlphaFold con distancias reales + logo de conservacion",
     "El missense no se mueve por clasificacion: se mueve por mecanismo"),
    ("nb04_hidden_allele", "04_HIDDEN_SECOND_ALLELE",
     "Navegador REF/ALT/delta de las nueve pistas congeladas",
     "Existe un segundo alelo que el pipeline codificante no ve"),
    ("nb05_residual",      "05_RESIDUAL_PHENOTYPE",
     "Matriz termino HPO x modelo de enfermedad, en bits de Resnik",
     "Que rasgos no explica MVA, y alguno exige un segundo diagnostico"),
    ("nb06_mosaic_mito",   "06_MOSAIC_AND_MITOREAD",
     "Distribuciones de BAF simuladas + curva de potencia",
     "Que le pasa a la senal de mosaicismo cuando se rompe la clonalidad"),
    ("nb07_track2",        "07_TRACK2_SAFE_RESCUE",
     "Matriz 8 puentes x 10 dimensiones de evidencia",
     "Hay un mecanismo terapeutico plausible, falsable y seguro"),
]


def main():
    print("=== PASADA VISUAL-CIENTIFICA · reconstruccion completa ===\n")
    results = []
    for mod, name, hero, question in NOTEBOOKS:
        m = importlib.import_module(f"src.nb.{mod}")
        ok = m.run(m.OUT, m.CELLS, min_sci=1)
        results.append((name, ok, hero, question))

    from src.nb.nbutil import verify
    print("\n=== MATRIZ DE VERIFICACION ===\n")
    print(f"  {'notebook':<28}{'figuras':>9}{'cientif.':>10}{'errores':>9}  estado")
    print("  " + "-" * 70)
    allok = True
    for name, ok, hero, _ in results:
        e, f, sci, good = verify(f"notebooks/{name}.ipynb", 1)
        allok &= good
        print(f"  {name:<28}{f:>9}{sci:>10}{e:>9}  {'OK' if good else 'FALLA'}")

    print(f"\n=== OBJETO CIENTIFICO PRINCIPAL DE CADA NOTEBOOK ===\n")
    for name, _ok, hero, _q in results:
        print(f"  {name:<28}{hero}")

    r = subprocess.run([sys.executable, "src/sanitize_scan.py"],
                       capture_output=True, text=True)
    clean = "LIMPIO" in r.stdout
    print(f"\n  saneado sobre lo versionado: {'LIMPIO' if clean else 'CON HALLAZGOS'}")
    print(f"  pasada: {'COMPLETA' if allok and clean else 'INCOMPLETA'}")
    return 0 if (allok and clean) else 1


if __name__ == "__main__":
    sys.exit(main())
