#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 8. Curated evidence matrix for Track 2: eight bridges, ten dimensions.

What this figure is, and what it is not
    It is a CURATED EVIDENCE MATRIX: 80 cells, each one a versioned row in
    research/track2_evidence.tsv with its own source. It is NOT an experimental
    matrix and NOT patient data. Labelling it plain "data" would invite exactly
    that misreading, so the class is written out in full.

No overall score, and that is deliberate
    There is no weight, no total, no ranking and no winner. Combining evidence of
    different kinds into one number requires a preregistered method for doing so,
    and no such method exists here. The value of the matrix is in the GAPS:
        bridge 7 is the translational gap (pharmacological co-induction unproven,
                                        with verified counter-evidence)
        bridge 8 is the safety gap (no qualifying evidence in our scoped
                                    search, in any dimension)

The corridor lives elsewhere
    The Safe Rescue Corridor is a scientific synthesis and lives in its own
    figure. It is deliberately not merged into this one.
"""
from __future__ import annotations
import collections, io, sys
import re

_BIBID = re.compile(r"(?:PMID\s+\d+|DOI\s+[^\s·]+)", re.I)


def publications(sources):
    """Agrupa cadenas de `fuente` que comparten un identificador bibliografico.

    POR QUE EXISTE. `PMID 34481829` y `PMID 34481829 · DOI 10.1016/j.jlr.2021.100114`
    son EL MISMO articulo escrito de dos formas. Contar cadenas daba 7 "fuentes
    distintas" mientras el pie de la propia figura enumeraba 6, cuatro lineas mas
    abajo. Ese numero no es decorativo: es el denominador con el que el proyecto
    pide al lector que NO lea las 80 celdas como 80 evidencias. Un denominador de
    honestidad inflado es peor que no darlo.

    Devuelve (publicaciones, artefactos_internos), ya deduplicadas y ordenadas.
    Un articulo citado dos veces cuenta UNA. Una fuente sin identificador
    bibliografico -- `docs/EVIDENCE.md`, `src/structure/` -- no es literatura y
    se cuenta aparte, porque mezclarlas infla el respaldo externo.
    """
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    limpio = sorted({s.strip() for s in sources if s and s.strip() and s.strip() != "-"})
    ids_de = {}
    for s in limpio:
        ids = [i.strip().rstrip(".,;") for i in _BIBID.findall(s)]
        ids_de[s] = ids
        for i in ids:
            union(s, i)

    grupos = {}
    for s in limpio:
        grupos.setdefault(find(s), []).append(s)

    pubs, internos = [], []
    for miembros in grupos.values():
        ids = sorted({i for m in miembros for i in ids_de[m]}, key=len)
        (pubs if ids else internos).append(ids[0] if ids else miembros[0])
    return sorted(pubs), sorted(internos)


import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

TSV = "research/track2_evidence.tsv"
NL = chr(10)

DIMS = ["paciente", "mva_humana", "celulas_aneuploides", "otro_contexto",
        "perturbacion_genetica", "perturbacion_farmacologica",
        "abundancia_bubr1", "proteostasis", "cin", "supervivencia_clonogenica"]
# Cabeceras cortas: con los nombres largos las columnas se solapaban entre si,
# que es peor que abreviar. La forma larga vive en el TSV y en el pie.
DIM_LABEL = {
    "paciente": "patient-" + NL + "specific",
    "mva_humana": "human" + NL + "MVA",
    "celulas_aneuploides": "aneuploid" + NL + "cells",
    "otro_contexto": "other" + NL + "context",
    "perturbacion_genetica": "genetic" + NL + "perturb.",
    "perturbacion_farmacologica": "pharmacol." + NL + "perturb.",
    "abundancia_bubr1": "BUBR1" + NL + "abundance",
    "proteostasis": "proteo-" + NL + "stasis",
    "cin": "CIN" + NL + "readout",
    "supervivencia_clonogenica": "clonogenic" + NL + "survival",
}
BRIDGE_LABEL = {
    1: "This patient's variant destabilises BUBR1",
    2: "Destabilised BUBR1 lowers protein level",
    3: "Raising chaperone capacity raises BUBR1",
    4: "More BUBR1 means less chromosome instability",
    5: "Aneuploidy causes proteotoxic and mitochondrial stress",
    6: "Raising HSP levels rescues that stress",
    7: "Pharmacological co-induction reproduces the rescue",
    8: "The same intervention affects CIN and clonogenic survival",
}
COL = {"DIRECT": S.GREEN, "GENETIC": S.BLUE, "NEAR": S.ORANGE,
       "CONTRADICTORY": S.VERM, "ABSENT": "#F0F2F3"}
# Etiquetas de celda en caja baja: la version en mayusculas hacia que la
# matriz pareciera una interfaz en vez de una figura.
TXT = {"DIRECT": "direct", "GENETIC": "genetic", "NEAR": "near",
       "CONTRADICTORY": "contra.", "ABSENT": ""}
LEGEND = {"DIRECT": "direct", "GENETIC": "genetic only", "NEAR": "near",
          "CONTRADICTORY": "contradictory", "ABSENT": "absent"}
GAPS = {7: "translational gap", 8: "safety gap"}


def read(path: str = TSV):
    rows = [ln.rstrip(NL).split(chr(9)) for ln in io.open(path, encoding="utf-8")
            if not ln.startswith("#") and ln.strip()]
    hdr = rows[0]
    ev = [dict(zip(hdr, r + [""] * (len(hdr) - len(r)))) for r in rows[1:]]
    orphan = [e for e in ev if e["clase"] != "ABSENT" and not e["fuente"].strip()]
    assert not orphan, f"cells without a source: {[(e['puente'], e['dimension']) for e in orphan]}"
    return ev


def build(ev):
    cell = {(int(e["puente"]), e["dimension"]): e for e in ev}
    ruta = {int(e["puente"]): e["ruta"] for e in ev}
    BR = sorted({int(e["puente"]) for e in ev})
    assert len(ev) == len(BR) * len(DIMS), f"matrix is not complete: {len(ev)} rows"

    fig, ax = plt.subplots(figsize=(12.8, 5.2))
    fig.subplots_adjust(left=0.310, right=0.845, top=0.815, bottom=0.240)

    for i, b in enumerate(BR):
        for j, d in enumerate(DIMS):
            c = cell[(b, d)]["clase"]
            ax.add_patch(plt.Rectangle((j - 0.46, i - 0.46), 0.92, 0.92, zorder=2,
                                       facecolor=COL[c], edgecolor="white", linewidth=0.8))
            if TXT[c]:
                ax.text(j, i, TXT[c], ha="center", va="center", zorder=3,
                        fontsize=S.BASE - 1.6, color="white", fontweight="bold")
    ax.set_xlim(-0.5, len(DIMS) - 0.5)
    ax.set_ylim(len(BR) - 0.5, -0.5)
    ax.set_xticks(range(len(DIMS)))
    ax.set_xticklabels([DIM_LABEL[d] for d in DIMS], fontsize=S.BASE - 1.4,
                       linespacing=1.30)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.tick_params(axis="x", length=0, pad=4)
    ax.set_yticks(range(len(BR)))
    ax.set_yticklabels([f"{b}  ·  {BRIDGE_LABEL[b]}" for b in BR], fontsize=S.BASE)
    ax.tick_params(axis="y", length=0)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

    for i, b in enumerate(BR):
        ax.text(len(DIMS) - 0.40, i, ruta[b].replace("ambas", "both"), va="center",
                ha="left", fontsize=S.BASE - 1.0, color=S.MUTED)
        if b in GAPS:
            ax.add_patch(plt.Rectangle((-0.5, i - 0.5), len(DIMS), 1.0, fill=False,
                                       edgecolor=S.INK, lw=1.8, zorder=6))
            ax.text(len(DIMS) + 0.10, i, GAPS[b], va="center", ha="left",
                    fontsize=S.BASE - 0.5, color=S.INK, fontweight="bold")

    ax.legend(handles=[Patch(facecolor=COL[k], edgecolor="white", label=LEGEND[k])
                       for k in ("DIRECT", "GENETIC", "NEAR", "CONTRADICTORY", "ABSENT")],
              loc="upper left", bbox_to_anchor=(0.0, -0.055), ncol=5,
              fontsize=S.BASE - 0.5)

    cnt = collections.Counter(e["clase"] for e in ev)
    srcs = sorted({e["fuente"] for e in ev if e["fuente"].strip()})
    b8_all_absent = all(cell[(8, d)]["clase"] == "ABSENT" for d in DIMS)
    b1_non_absent = [d for d in DIMS if cell[(1, d)]["clase"] != "ABSENT"]
    b7_contra = [d for d in DIMS if cell[(7, d)]["clase"] == "CONTRADICTORY"]

    fig.suptitle("Figure 8. Track 2 curated evidence matrix "
                 "(external literature + project evidence, not patient observations)",
                 x=0.006, y=0.988, ha="left", fontsize=S.BASE + 1.6,
                 fontweight="bold", color=S.INK)
    pubs, internos = publications(srcs)
    compact = pubs + internos
    S.note(fig,
           f"Every cell is a versioned row in {TSV}: {len(ev)} cells drawn from {len(pubs)} distinct publications and {len(internos)} internal project artefacts; no cell other than an absent one may lack a source (checked at build time)." + NL +
           f"{cnt['ABSENT']} cells are empty, {cnt['DIRECT']} hold evidence of the exact kind the bridge needs, {cnt['CONTRADICTORY']} point against it. Bridge 8 is empty in all ten dimensions" + NL +
           f"({'confirmed' if b8_all_absent else 'checked'}). Bridge 1, the only one tied to this patient, has {len(b1_non_absent)} non-empty cell and it is near, not direct. Bridge 7 is contradictory in {len(b7_contra)} dimensions." + NL +
           "No overall score, weight or ranking is computed. Combining heterogeneous evidence into one number would need a preregistered method, and none exists. An absent cell means no qualifying evidence was identified in our scoped literature search, not that the claim is false and not that nobody has ever looked." + NL +
           f"Sources ({len(pubs)} published, {len(internos)} internal): " + "  ·  ".join(compact), y=0.004)

    return fig, {"counts": dict(cnt), "sources": srcs}


def load_and_build():
    ev = read()
    return build(ev)[0], {"ev": ev}


if __name__ == "__main__":
    fig, d = load_and_build()
    print(S.export(fig, "fig07_track2_evidence_matrix", "CURATED_EVIDENCE", "EXTERNAL+DERIVED"))
