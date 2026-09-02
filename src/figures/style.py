#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publication-grade figure standard for the whole project.

Why this module exists
    The figures were being tuned to look good inside a contact sheet. That is
    backwards: the contact sheet is an index, the full-size figure is the
    deliverable. Every hero figure is now built here at FULL size and only
    then downsampled for the index.

Why the figure text is in English
    Notebooks explain in Spanish, figures speak English. Mixing both inside one
    figure is the fastest way to look unserious. Decision recorded here so it
    does not drift.

Rules enforced here rather than written down elsewhere
    - one type scale, one family, minimum legible size;
    - panel letters A/B/C/D top-left, outside the data area;
    - axis labels carry units; no giant titles inside the axes;
    - the caption lives in the notebook, never on top of the data;
    - grids are hairlines or absent;
    - colour is never the only encoder: categories also differ by marker or
      dash pattern, and the palette is colour-blind safe (Okabe-Ito);
    - export vector (SVG) + raster at 300 dpi; the thumbnail is a separate,
      smaller render, never a brutal resize of the full one.

What this module does not do
    It does not decide what a figure shows. Nothing here fabricates, smooths,
    interpolates or infers a value.
"""
from __future__ import annotations
import os

import matplotlib
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- palette ---
# Okabe-Ito: the standard colour-blind-safe qualitative set. Named by role so a
# figure never says "the green one" as its only way of identifying a series.
INK      = "#1A1A1A"
MUTED    = "#5B6670"
HAIRLINE = "#D6DADD"
PAPER    = "#FFFFFF"

ORANGE   = "#E69F00"
SKY      = "#56B4E9"
GREEN    = "#009E73"
YELLOW   = "#F0E442"
BLUE     = "#0072B2"
VERM     = "#D55E00"
PURPLE   = "#CC79A7"
BLACK    = "#000000"

CYCLE = [BLUE, VERM, GREEN, ORANGE, PURPLE, SKY, YELLOW, BLACK]

# Marker and dash vocabularies, so a category is identifiable in grayscale.
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
DASHES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 2))]

# --------------------------------------------------------------- type ------
BASE = 8.0
RC = {
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": BASE,
    "axes.titlesize": BASE + 0.5, "axes.titleweight": "regular", "axes.titlepad": 4.0,
    "axes.labelsize": BASE + 0.5, "axes.labelcolor": INK, "axes.labelpad": 2.5,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False,
    "grid.color": HAIRLINE, "grid.linewidth": 0.45, "grid.alpha": 1.0,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelsize": BASE - 0.5, "ytick.labelsize": BASE - 0.5,
    "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "xtick.major.size": 2.6, "ytick.major.size": 2.6,
    "text.color": INK,
    "legend.fontsize": BASE - 0.5, "legend.frameon": False,
    "legend.handlelength": 1.6, "legend.handletextpad": 0.6,
    "legend.columnspacing": 1.2, "legend.borderaxespad": 0.2,
    "lines.linewidth": 1.1, "lines.markersize": 3.4,
    "figure.dpi": 110, "savefig.dpi": 300, "savefig.bbox": "standard",
    "svg.fonttype": "none",          # text stays text in the SVG, never outlines
    "pdf.fonttype": 42,
    # Los trazos densos se marcan rasterized=True en su figura; esto solo evita
    # emitir puntos que caen en el mismo pixel.
    "path.simplify": True, "path.simplify_threshold": 1.0,
}


def use():
    matplotlib.rcParams.update(RC)


use()


# --------------------------------------------------------------- helpers ---
def panel(ax, letter: str, dx: float = -0.062, dy: float = 1.045, size: float = 10.5):
    """Panel letter, outside the data area, top-left. Always the same place."""
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=size,
            fontweight="bold", color=INK, ha="left", va="bottom")


def head(ax, text: str, size: float = BASE + 0.5):
    """Short panel heading, left-aligned above the axes. Not a title banner."""
    ax.set_title(text, loc="left", fontsize=size, color=INK, pad=4.0)


def note(fig, text: str, y: float = 0.004, size: float = BASE - 1.3):
    """Provenance strip along the bottom of the figure, outside every axes."""
    fig.text(0.006, y, text, fontsize=size, color=MUTED, ha="left", va="bottom")


def grid(ax, axis: str = "y"):
    ax.grid(True, axis=axis, color=HAIRLINE, lw=0.45, zorder=0)
    ax.set_axisbelow(True)


def thousands(n) -> str:
    return f"{n:,}".replace(",", " ")


# ------------------------------------------------------- the two axes ------
# Dos ejes distintos. Confundirlos es como una figura acaba diciendo algo
#
#   figure class    que tipo de objeto es la figura
#   evidence origin de donde viene lo que hay dentro
#
# La matriz HPO es FIGURE CLASS = DATA, pero su EVIDENCE ORIGIN es
# MEASURED (terminos del probando) + EXTERNAL (modelos de enfermedad) +
# DERIVED (Resnik). Colapsar los dos ejes en una sola etiqueta la hacia parecer
# "datos del paciente", que no es. Track 2 tenia el problema simetrico.
FIGURE_CLASS = ("DATA", "MODEL_OUTPUT", "SIMULATION", "CURATED_EVIDENCE",
                "SYNTHESIS", "NARRATIVE")
SCIENTIFIC_CLASS = ("DATA", "MODEL_OUTPUT", "SIMULATION", "CURATED_EVIDENCE")
EVIDENCE_ORIGIN = ("MEASURED", "DERIVED", "EXTERNAL", "PREDICTED", "SIMULATED")

CLASS_COL = {"DATA": GREEN, "MODEL_OUTPUT": BLUE, "SIMULATION": PURPLE,
             "CURATED_EVIDENCE": ORANGE, "SYNTHESIS": ORANGE, "NARRATIVE": MUTED}


def check(fig_class: str, origin: str):
    assert fig_class in FIGURE_CLASS, f"unknown figure class: {fig_class}"
    for o in origin.replace(" ", "").split("+"):
        assert o in EVIDENCE_ORIGIN, f"unknown evidence origin: {o}"
    return fig_class, origin


def stamp(fig, fig_class: str, origin: str):
    """Both axes, on the figure itself, top right.

    Set in one discreet grey line rather than two bold badges: the badges made
    the figures look like a dashboard, and the data should dominate.
    """
    check(fig_class, origin)
    fig.text(0.998, 0.9975,
             "Figure class: " + fig_class.replace("_", " ").lower()
             + "    Evidence origin: " + origin.lower().replace("+", ", "),
             ha="right", va="top", fontsize=BASE - 1.8, color=MUTED)


# ---------------------------------------------------------------- export ---
FULL_DIR = "figures/pub"
THUMB_DIR = "figures/pub/thumb"


def export(fig, slug: str, fig_class: str, origin: str, thumb_width: float = 5.4):
    """Write FULL (SVG + PNG 300 dpi) and a SEPARATE thumbnail render.

    The thumbnail is produced by re-rendering the same figure at a lower dpi,
    not by resampling the 300-dpi raster: a brutal downscale is what made the
    dense panels unreadable in the index.
    """
    # Los dos ejes se DECLARAN aqui o no hay exportacion: es la unica forma de
    # que no se olvide uno al anadir una figura nueva.
    stamp(fig, fig_class, origin)
    os.makedirs(FULL_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)
    svg = os.path.join(FULL_DIR, slug + ".svg")
    png = os.path.join(FULL_DIR, slug + ".png")
    thumb = os.path.join(THUMB_DIR, slug + ".png")
    fig.savefig(svg, format="svg", dpi=300)   # dpi manda sobre lo rasterizado
    fig.savefig(png, dpi=300)
    w = fig.get_size_inches()[0]
    fig.savefig(thumb, dpi=max(40.0, 96.0 * thumb_width / max(w, 0.1)))
    return {"svg": svg, "png": png, "thumb": thumb,
            "figure_class": fig_class, "evidence_origin": origin,
            "size_in": tuple(round(float(v), 2) for v in fig.get_size_inches())}
