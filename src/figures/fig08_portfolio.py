#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 9. Track 2 experimental portfolio: three interventions, three controls.

WHAT THIS FIGURE IS
    A CURATED EVIDENCE figure built from research/track2_candidates.tsv. Every
    cell is a versioned row with its own identifier, checked by src/verify.py.

WHAT IT IS NOT, AND THIS MATTERS
    It is NOT a ranking, NOT a score and NOT a therapeutic recommendation. The
    three interventions do not compete for a first place; they occupy three
    DIFFERENT roles, and each one teaches something different by failing:

        azithromycin  ALLELE       the only arm aimed at this patient's own
                                   truncating allele
        arimoclomol   SENTINEL     its FAILURE is the informative outcome: it
                                   closes the pharmacological translation of
                                   bridge 7
        sirolimus     ADVERSARIAL  exists to probe the safety boundary, not to
                                   win

    Drawing them as a leaderboard would destroy the entire point, so there is
    no ordering by merit anywhere in this figure.

WHY THE EVIDENCE PANEL LOOKS EMPTY IN PLACES
    Because it is. Panel A colours each claim by WHERE IT COMES FROM, using the
    same vocabulary src/verify.py enforces. An empty-looking row is a real gap,
    not a rendering artefact, and it is the most useful thing on the page.
"""
from __future__ import annotations
import io, sys

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

TSV = "research/track2_candidates.tsv"
NL, TAB = chr(10), chr(9)

# Las cinco columnas que AFIRMAN algo sobre el mundo. Son exactamente las que
# verify.py obliga a que lleven identificador.
CLAIMS = ["evidencia directa", "evidencia indirecta", "evidencia contraria",
          "exposicion", "seguridad"]
CLAIM_LABEL = {
    "evidencia directa":   "direct" + NL + "evidence",
    "evidencia indirecta": "indirect" + NL + "evidence",
    "evidencia contraria": "counter-" + NL + "evidence",
    "exposicion":          "human" + NL + "exposure",
    "seguridad":           "safety" + NL + "profile",
}

ROLE_LABEL = {"ALLELE": "allele-directed", "SENTINEL": "falsification sentinel",
              "ADVERSARIAL": "adversarial comparator", "CONTROL": "control"}

# Procedencia de cada celda. El orden importa: se evalua de arriba abajo.
CITED, INTERNAL, UNVERIFIED, DECLARED, NA = (
    "CITED", "INTERNAL", "UNVERIFIED", "DECLARED_ABSENT", "NA")
COL = {CITED: S.GREEN, INTERNAL: S.BLUE, UNVERIFIED: S.ORANGE,
       DECLARED: S.VERM, NA: "#F0F2F3"}
TXT = {CITED: "cited", INTERNAL: "internal", UNVERIFIED: "unverified",
       DECLARED: "none", NA: ""}
LEGEND = {CITED: "published identifier (DOI / PMID / label)",
          INTERNAL: "project artefact",
          UNVERIFIED: "gap declared, not verified in session",
          DECLARED: "evidence declared absent",
          NA: "not applicable to this arm"}


def classify(v: str) -> str:
    """De donde viene lo que dice esta celda.

    Regla explicita y en un solo sitio, para que la figura no pueda contar una
    historia distinta de la que valida verify.py.
    """
    t = v.strip()
    low = t.lower()
    if low in ("n/a", "no aplica", ""):
        return NA
    if low.startswith(("ninguna", "ninguno")):
        return DECLARED
    if "no verificado" in low:
        return UNVERIFIED
    if any(k in t for k in ("DOI ", "PMID ", "PMC", "etiqueta MIPLYFFA")):
        return CITED
    if "notebooks/" in t or "track2_evidence.tsv" in t:
        return INTERNAL
    return UNVERIFIED


def read(path: str = TSV):
    rows = [ln.rstrip(NL).split(TAB) for ln in io.open(path, encoding="utf-8")
            if not ln.startswith("#") and ln.strip()]
    hdr = rows[0]
    return [dict(zip(hdr, r + [""] * (len(hdr) - len(r)))) for r in rows[1:]]


def _wrap(t: str, width: int) -> str:
    out, line = [], ""
    for w in t.split():
        if len(line) + len(w) + 1 > width:
            out.append(line); line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    return NL.join(out)


def build(rows):
    inter = [r for r in rows if r["rol"] != "CONTROL"]
    ctrl = [r for r in rows if r["rol"] == "CONTROL"]
    order = inter + ctrl

    fig = plt.figure(figsize=(13.2, 7.4))
    gsp = fig.add_gridspec(1, 2, width_ratios=[1.06, 1.0])
    fig.subplots_adjust(left=0.163, right=0.988, top=0.800, bottom=0.158, wspace=0.030)

    # ------------------------------------------------- A · procedencia -----
    axA = fig.add_subplot(gsp[0, 0])
    for i, r in enumerate(order):
        for j, c in enumerate(CLAIMS):
            k = classify(r[c])
            axA.add_patch(plt.Rectangle((j - 0.46, i - 0.46), 0.92, 0.92, zorder=2,
                                        facecolor=COL[k], edgecolor="white", linewidth=0.8))
            if TXT[k]:
                axA.text(j, i, TXT[k], ha="center", va="center", zorder=3,
                         fontsize=S.BASE - 2.0, color="white", fontweight="bold")
    axA.set_xlim(-0.5, len(CLAIMS) - 0.5)
    axA.set_ylim(len(order) - 0.5, -0.5)
    axA.set_xticks(range(len(CLAIMS)))
    axA.set_xticklabels([CLAIM_LABEL[c] for c in CLAIMS], fontsize=S.BASE - 1.4,
                        linespacing=1.30)
    axA.xaxis.set_ticks_position("top")
    axA.tick_params(axis="x", length=0, pad=4)
    axA.set_yticks(range(len(order)))
    # El rol va en la propia etiqueta. Antes iba a la derecha de la matriz, donde
    # se solapaba con el panel B: dos textos distintos en el mismo pixel.
    axA.set_yticklabels([r["candidato"] + NL + ROLE_LABEL[r["rol"]] for r in order],
                        fontsize=S.BASE + 0.3, linespacing=1.45)
    axA.tick_params(axis="y", length=0)
    for sp in axA.spines.values():
        sp.set_visible(False)
    axA.grid(False)

    # la linea que separa brazos activos de controles
    axA.axhline(len(inter) - 0.5, color=S.MUTED, lw=0.9, ls=(0, (4, 2)), zorder=5)

    S.panel(axA, "A", dx=-0.300, dy=1.130)
    axA.text(-0.300, 1.088, "Where each claim comes from", transform=axA.transAxes,
             ha="left", va="bottom", fontsize=S.BASE + 0.5, color=S.INK)
    # AQUI HABIA una linea "colour encodes provenance...". Se retiro: caia sobre
    # las cabeceras de columna del propio panel, y una aclaracion que tapa el
    # dato empeora la figura mas de lo que la aclara. La advertencia completa
    # vive en la tira de procedencia del pie, que es texto corrido y no compite
    # con nada.
    axA.legend(handles=[Patch(facecolor=COL[k], edgecolor="white", label=LEGEND[k])
                        for k in (CITED, INTERNAL, UNVERIFIED, DECLARED, NA)],
               loc="upper left", bbox_to_anchor=(-0.300, -0.045), ncol=2,
               fontsize=S.BASE - 1.0)

    # ------------------------------------------- B · que mata cada fallo ----
    axB = fig.add_subplot(gsp[0, 1])
    axB.set_xlim(0, 1); axB.set_ylim(0, 1)
    axB.axis("off")
    S.panel(axB, "B", dx=-0.020, dy=1.130)
    axB.text(-0.020, 1.088, "What a negative result would falsify",
             transform=axB.transAxes, ha="left", va="bottom",
             fontsize=S.BASE + 0.5, color=S.INK)

    ROLE_COL = {"ALLELE": S.BLUE, "SENTINEL": S.ORANGE, "ADVERSARIAL": S.VERM}
    y = 0.975
    for r in inter:
        col = ROLE_COL[r["rol"]]
        axB.add_patch(plt.Rectangle((0.0, y - 0.300), 0.016, 0.290,
                                    facecolor=col, edgecolor="none",
                                    transform=axB.transAxes, clip_on=False))
        axB.text(0.042, y, r["candidato"], fontsize=S.BASE + 1.2, fontweight="bold",
                 color=S.INK, va="top", ha="left")
        axB.text(0.042, y - 0.048, ROLE_LABEL[r["rol"]].upper(), fontsize=S.BASE - 1.4,
                 color=col, va="top", ha="left", fontweight="bold")
        axB.text(0.042, y - 0.098, _wrap(r["regla de descarte (EN)"], 60),
                 fontsize=S.BASE - 0.8, color=S.INK, va="top", ha="left",
                 linespacing=1.42)
        y -= 0.335

    fig.suptitle("Figure 9. Track 2 experimental portfolio: three roles, not a ranking",
                 x=0.006, y=0.988, ha="left", fontsize=S.BASE + 1.6,
                 fontweight="bold", color=S.INK)
    fig.text(0.006, 0.930,
             "No overall score, no winner. Each intervention is informative by failing, "
             "and a different hypothesis dies in each case.",
             ha="left", va="top", fontsize=S.BASE, color=S.MUTED)

    n_cited = sum(1 for r in rows for c in CLAIMS if classify(r[c]) == CITED)
    S.note(fig,
           f"Built from {TSV}: {len(inter)} interventions, {len(ctrl)} controls, "
           f"{len(rows) * len(CLAIMS)} claim cells, {n_cited} carrying a published identifier."
           + NL +
           "Colour encodes PROVENANCE, not efficacy or support: a green cell means the claim carries a published identifier, not that it favours the arm."
           + NL +
           "Vehicle is the only true negative control; sirolimus is an adversarial comparator, "
           "not a negative control.  ·  NONE of these is proposed for administration.")
    return fig, {"interventions": len(inter), "controls": len(ctrl), "cited": n_cited}


def load_and_build():
    return build(read())


if __name__ == "__main__":
    f, m = load_and_build()
    print(S.export(f, "fig08_track2_portfolio", "CURATED_EVIDENCE", "EXTERNAL+DERIVED"), m)
