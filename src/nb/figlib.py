#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Biblioteca de figuras para los notebooks cientificos.

LA REGLA QUE ESTA BIBLIOTECA HACE CUMPLIR
    Generar una figura y escribirla en figures/ NO basta. La figura aparece
    INLINE en el notebook, en la misma celda o la siguiente, con un caption que
    declara: experimento, clase de evidencia, interpretacion y QUE NO DEMUESTRA.
    Un notebook debe poder leerse de arriba abajo sin salir de el.

CLASES DE EVIDENCIA (brief §15 + contrato visual)
    MEASURED  - observacion directa sobre los datos del caso
    DERIVED   - calculado por nosotros a partir de lo anterior
    EXTERNAL  - base de datos, literatura o modelo de terceros
    PREDICTED - salida de un modelo, no una medicion
    SIMULATED - modelo sin datos del paciente
"""
from __future__ import annotations
import io, os, hashlib

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, SVG

# Paleta de la casa: la misma de las figuras SVG del proyecto.
INK, SOFT, RULE = "#14191E", "#5A646D", "#DCE0E3"
ALIVE, DEAD, OPEN, FLOW, VOID = "#2E7D6B", "#B4453A", "#C07A2E", "#8C99A4", "#6B5F87"
GROUND = "#FAFAF8"

matplotlib.rcParams.update({
    "figure.dpi": 110, "figure.facecolor": GROUND, "axes.facecolor": GROUND,
    "savefig.facecolor": GROUND, "axes.edgecolor": RULE, "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": SOFT, "ytick.color": SOFT,
    "axes.grid": True, "grid.color": RULE, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
})

_VALID = {"MEASURED", "DERIVED", "EXTERNAL", "PREDICTED", "SIMULATED"}


def _hash(path: str) -> str:
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        h.update(f.read(1 << 22))
    return h.hexdigest()[:12]


def cap(title: str, exp: str, ev: str, reads: str, not_proves: str,
        prov: str | None = None) -> None:
    """Caption estandar bajo cada figura. Obligatorio, no decorativo.

    ev acepta combinaciones: "EXTERNAL+DERIVED".
    """
    for e in ev.replace(" ", "").split("+"):
        assert e in _VALID, f"clase de evidencia desconocida: {e}"
    prov_line = f"  \n> procedencia: `{prov}`" if prov else ""
    display(Markdown(
        f"> **{title}**  \n"
        f"> `{exp}` · **{ev}**  \n"
        f"> *Qué enseña:* {reads}  \n"
        f"> **Qué NO demuestra:** {not_proves}{prov_line}"))


def svg(path: str, title: str, exp: str, ev: str, reads: str,
        not_proves: str, generator: str | None = None) -> None:
    """Embebe un SVG existente de figures/ con su caption. La procedencia es el
    generador + hash del fichero, para que 'la figura cambio' sea detectable."""
    assert os.path.exists(path), f"no existe {path}"
    display(SVG(filename=path))
    prov = f"{generator or 'ver src/'} → {os.path.basename(path)} · sha256[:12]={_hash(path)}"
    cap(title, exp, ev, reads, not_proves, prov)


def done(fig, title: str, exp: str, ev: str, reads: str, not_proves: str,
         prov: str | None = None) -> None:
    """Cierra una figura matplotlib: la muestra y le pone el caption."""
    fig.tight_layout()
    plt.show()
    cap(title, exp, ev, reads, not_proves, prov)
