#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Biblioteca de figuras para los notebooks cientificos.

La prueba que decide si una figura es cientifica: quitandole el titulo, el
    pie y la conclusion, .un experto reconoce que objeto cientifico esta viendo?

    Si ve un transcrito, tracks, una distribucion, una estructura, un
    alineamiento, BAF, un heatmap, un ranking o cobertura -> SI.
    Si ve "SURVIVES", "BLOCKED", cajas verdes y flechas -> NO: es narrativa.

    `ax.axis("off")` + Rectangle + texto es una diapositiva hecha con
    Matplotlib. Puede ser util, pero NUNCA es la figura cientifica principal.

CLASES DE FIGURA
    DATA          objeto o distribucion calculada desde datos del caso
    MODEL_OUTPUT  salida de un modelo externo (AlphaGenome, AlphaFold)
    SIMULATION    distribucion generada por simulacion, sin datos del paciente
    SYNTHESIS     integra resultados ya obtenidos; no expone el dato crudo
    NARRATIVE     explica una conclusion; no contiene dato

    Solo DATA / MODEL_OUTPUT / SIMULATION cuentan como figura cientifica.
    Las otras dos se etiquetan como tales EN LA PROPIA FIGURA.

ORIGEN DE LA EVIDENCIA (brief §15). Es un eje distinto de la clase.
    MEASURED · DERIVED · EXTERNAL · PREDICTED · SIMULATED

    Son dos preguntas separadas y hay que responder las dos:
      FIGURE CLASS     que TIPO DE OBJETO es la figura
      EVIDENCE ORIGIN  de DONDE viene lo que hay dentro
    La matriz HPO es DATA y a la vez MEASURED+EXTERNAL+DERIVED. Colapsar los dos
    ejes la hacia parecer "datos del paciente", que no lo es.
"""
from __future__ import annotations
import io, os, hashlib

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, SVG

INK, SOFT, RULE = "#14191E", "#5A646D", "#DCE0E3"
ALIVE, DEAD, OPEN, FLOW, VOID = "#2E7D6B", "#B4453A", "#C07A2E", "#8C99A4", "#6B5F87"
GROUND = "#FAFAF8"

matplotlib.rcParams.update({
    "figure.dpi": 118, "figure.facecolor": GROUND, "axes.facecolor": GROUND,
    "savefig.facecolor": GROUND, "axes.edgecolor": RULE, "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": SOFT, "ytick.color": SOFT,
    "axes.grid": True, "grid.color": RULE, "grid.linewidth": 0.55,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 9.5, "axes.titlesize": 11.5, "axes.titleweight": "bold",
})

_EVID = {"MEASURED", "DERIVED", "EXTERNAL", "PREDICTED", "SIMULATED"}
# CURATED_EVIDENCE: tabla de evidencia versionada, con fuente por celda. Es un
# objeto de datos y no narrativa, pero NO son observaciones del paciente, y
# por eso no se etiqueta simplemente DATA.
SCIENTIFIC = {"DATA", "MODEL_OUTPUT", "SIMULATION", "CURATED_EVIDENCE"}
_CLASSES = SCIENTIFIC | {"SYNTHESIS", "NARRATIVE"}

_BADGE = {"DATA": ALIVE, "MODEL_OUTPUT": FLOW, "SIMULATION": VOID,
          "CURATED_EVIDENCE": OPEN, "SYNTHESIS": OPEN, "NARRATIVE": SOFT}

REGISTRY = []          # se vuelca al final del notebook para la tabla de HECHO

# Cada notebook fija su propio par de etiquetas para el pie. Con un unico par
# fijo los ocho salian calcados, como si vinieran de la misma plantilla, y la
# disciplina de declarar el limite de la evidencia acababa leyendose como un
# formulario. El contenido es el mismo; el encabezado cambia.
LABELS = ["Lectura", "Limite de la evidencia"]


def labels(reads: str, limits: str):
    LABELS[0], LABELS[1] = reads, limits


def _hash(path: str) -> str:
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        h.update(f.read(1 << 22))
    return h.hexdigest()[:12]


def cap(title, exp, ev, cls, reads, not_proves, prov=None, source=None, lib=None):
    for e in ev.replace(" ", "").split("+"):
        assert e in _EVID, f"clase de evidencia desconocida: {e}"
    assert cls in _CLASSES, f"clase de figura desconocida: {cls}"
    REGISTRY.append({"title": title, "exp": exp, "cls": cls, "ev": ev,
                     "source": source or prov or "", "lib": lib or "matplotlib"})
    tag = ("figura cientifica" if cls in SCIENTIFIC
           else "no es un dato: " + cls.lower().replace("_", " "))
    extra = []
    if source:
        extra.append(f"datos: `{source}`")
    if lib:
        extra.append(f"libreria: `{lib}`")
    if prov:
        extra.append(f"procedencia: `{prov}`")
    tail = ("  \n> " + " · ".join(extra)) if extra else ""
    display(Markdown(
        f"> **{title}**  \n"
        f"> `{exp}` · figure class `{cls}`, {tag} · evidence origin `{ev}`  \n"
        f"> *{LABELS[0]}.* {reads}  \n"
        f"> **{LABELS[1]}.** {not_proves}{tail}"))


def _stamp(fig, cls):
    """Sella la clase EN la figura: si alguien recorta la imagen y la pega en
    una diapositiva, la etiqueta viaja con ella."""
    fig.text(0.995, 0.004, cls.replace("_", " "), ha="right", va="bottom",
             fontsize=6.6, color=_BADGE[cls], alpha=0.95, fontweight="bold")


def done(fig, title, exp, ev, cls, reads, not_proves, prov=None, source=None, lib=None):
    _stamp(fig, cls)
    fig.tight_layout(rect=(0, 0.012, 1, 1))
    plt.show()
    cap(title, exp, ev, cls, reads, not_proves, prov, source, lib)


def pub(fig, title, exp, ev, cls, reads, not_proves, source=None, lib=None,
        slug=None):
    """Muestra una figura YA construida a tamano de publicacion.

    POR QUE NO SE REUTILIZA done()
        done() aplica tight_layout y estampa la clase abajo a la derecha. Las
        figuras de src/figures/ vienen con su propia composicion, sus margenes
        calculados y su franja de procedencia; volver a tocarlas las rompe.
        Aqui solo se estampa la clase arriba a la derecha, fuera de los ejes, y
        se registra en la tabla de HECHO.
    """
    assert cls in _CLASSES, f"clase de figura desconocida: {cls}"
    fig.text(0.998, 0.999, cls.replace("_", " "), ha="right", va="top",
             fontsize=6.8, color=_BADGE[cls], alpha=0.95, fontweight="bold")
    display(fig)
    plt.close(fig)
    cap(title, exp, ev, cls, reads, not_proves,
        prov=(f"figures/pub/{slug}.svg + .png 300 dpi" if slug else None),
        source=source, lib=lib)


def svg(path, title, exp, ev, cls, reads, not_proves, generator=None, source=None):
    assert os.path.exists(path), f"no existe {path}"
    display(SVG(filename=path))
    prov = (f"{generator or 'ver src/'} genera {os.path.basename(path)}, sha256[:12]={_hash(path)}")
    cap(title, exp, ev, cls, reads, not_proves, prov, source, lib="SVG")


def summary():
    """Tabla de figuras del notebook, para la definicion de HECHO."""
    sci = sum(1 for r in REGISTRY if r["cls"] in SCIENTIFIC)
    print(f"  figuras: {len(REGISTRY)}  ·  cientificas: {sci}  ·  "
          f"narrativa/sintesis: {len(REGISTRY) - sci}")
    print()
    print(f"  {'clase':<14}{'evidencia':<22}{'libreria':<20}titulo")
    print("  " + "-" * 96)
    for r in REGISTRY:
        print(f"  {r['cls']:<14}{r['ev']:<22}{r['lib']:<20}{r['title'][:44]}")
    assert sci >= 1, "un notebook mayor necesita AL MENOS UNA figura cientifica"
