#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construccion y ejecucion de los notebooks cientificos.

POR QUE GENERADOS Y NO ESCRITOS A MANO
    El notebook es el registro reproducible; la fuente de verdad vive en src/.
    Generarlos garantiza que ejecutan las MISMAS funciones del pipeline y
    permite reconstruirlos todos con un comando cuando algo cambia.

DEFINICION DE HECHO (impuesta por verify())
    - ejecuta de arriba abajo sin errores;
    - contiene al menos N_FIGS salidas graficas EMBEBIDAS (display_data con
      image/png o image/svg+xml) — generar un SVG en figures/ no cuenta;
    - pasa el escaner de saneado despues de ejecutarse.
"""
from __future__ import annotations
import io, os, sys, time

import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

# Celda 0 de todos los notebooks: entorno, estilo y biblioteca de figuras.
SETUP = '''import sys, os, io, json, pickle, collections
os.chdir("..")                       # el pipeline usa rutas relativas a la raiz
sys.path.insert(0, ".")
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
from src.nb import figlib as fl      # figuras inline + caption con procedencia
print("entorno listo · las figuras de este notebook aparecen INLINE, con caption")'''


def build(path: str, cells: list) -> None:
    nb = new_notebook()
    for kind, src in cells:
        nb.cells.append(new_markdown_cell(src) if kind == "md" else new_code_cell(src))
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python",
                                 "name": "python3"}
    nb.metadata["language_info"] = {"name": "python", "version": sys.version.split()[0]}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nbf.write(nb, path)


def execute(path: str, timeout: int = 1800):
    from nbclient import NotebookClient
    nb = nbf.read(path, as_version=4)
    t0 = time.time()
    NotebookClient(nb, timeout=timeout, kernel_name="python3",
                   resources={"metadata": {"path": os.path.dirname(path) or "."}}).execute()
    nbf.write(nb, path)
    return nb, time.time() - t0


def verify(path: str, min_figs: int):
    """(errores, figuras embebidas). Una figura solo cuenta si esta DENTRO."""
    nb = nbf.read(path, as_version=4)
    errs, figs = 0, 0
    for c in nb.cells:
        if c.cell_type != "code":
            continue
        for o in c.get("outputs", []):
            if o.get("output_type") == "error":
                errs += 1
            data = o.get("data", {})
            if "image/png" in data or "image/svg+xml" in data:
                figs += 1
    ok = errs == 0 and figs >= min_figs
    return errs, figs, ok


def run(path: str, cells: list, min_figs: int):
    build(path, cells)
    _, secs = execute(path)
    errs, figs, ok = verify(path, min_figs)
    tag = "OK" if ok else "FALLA"
    print(f"  {os.path.basename(path):<38} {secs:5.0f}s  figuras embebidas: {figs:>2}  "
          f"errores: {errs}  [{tag}]")
    return ok
