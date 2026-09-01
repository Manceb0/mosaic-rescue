#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstruye y ejecuta LOS OCHO notebooks, y emite la matriz de verificacion.

DEFINICION DE HECHO, comprobada aqui y no declarada:
  - ejecuta de arriba abajo sin errores;
  - contiene al menos el minimo de figuras EMBEBIDAS (display_data con imagen);
    generar un SVG en figures/ NO cuenta;
  - pasa el escaner de saneado sobre lo versionado.

Uso:  python src/nb/build_all.py
"""
from __future__ import annotations
import sys, subprocess, importlib

sys.path.insert(0, ".")

# (modulo, notebook, minimo de figuras, pregunta cientifica)
NOTEBOOKS = [
    ("nb00_data_reality",  "00_DATA_REALITY",           3,
     "Que se puede y que no responder con los datos que hay"),
    ("nb01_track1",        "01_TRACK1_GENOME_WIDE",     6,
     "Que gen explica el caso cuando compite todo el genoma codificante"),
    ("nb02_alleles",       "02_BUB1B_ALLELE_CURATION",  4,
     "Que sostiene cada alelo, y que haria falta para que el par sea causal"),
    ("nb03_mechanism",     "03_BUBR1_MECHANISM",        4,
     "El missense no se mueve por clasificacion: se mueve por mecanismo"),
    ("nb04_hidden_allele", "04_HIDDEN_SECOND_ALLELE",   3,
     "Existe un segundo alelo que el pipeline codificante no ve"),
    ("nb05_residual",      "05_RESIDUAL_PHENOTYPE",     3,
     "Que rasgos no explica MVA, y alguno exige un segundo diagnostico"),
    ("nb06_mosaic_mito",   "06_MOSAIC_AND_MITOREAD",    3,
     "Que le pasa a la senal de mosaicismo cuando se rompe la clonalidad"),
    ("nb07_track2",        "07_TRACK2_SAFE_RESCUE",     3,
     "Hay un mecanismo terapeutico plausible, falsable y seguro"),
]


def main():
    print("=== NOTEBOOK RECOVERY SPRINT · reconstruccion completa ===\n")
    results = []
    for mod, name, minf, question in NOTEBOOKS:
        m = importlib.import_module(f"src.nb.{mod}")
        ok = m.run(m.OUT, m.CELLS, min_figs=minf)
        results.append((name, ok, minf, question))

    from src.nb.nbutil import verify
    print("\n=== MATRIZ DE VERIFICACION ===\n")
    print(f"  {'notebook':<28}{'ejec':>6}{'figuras':>9}{'minimo':>8}{'errores':>9}  estado")
    print("  " + "-" * 76)
    allok = True
    for name, ok, minf, _ in results:
        e, f, good = verify(f"notebooks/{name}.ipynb", minf)
        allok &= good
        print(f"  {name:<28}{'si':>6}{f:>9}{minf:>8}{e:>9}  {'OK' if good else 'FALLA'}")

    r = subprocess.run([sys.executable, "src/sanitize_scan.py"],
                       capture_output=True, text=True)
    clean = "LIMPIO" in r.stdout
    print(f"\n  saneado sobre lo versionado: {'LIMPIO' if clean else 'CON HALLAZGOS'}")
    print(f"  sprint: {'COMPLETO' if allok and clean else 'INCOMPLETO'}")
    return 0 if (allok and clean) else 1


if __name__ == "__main__":
    sys.exit(main())
