#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 6. Proband HPO terms against every disease model evaluated.

What the cells hold
    Resnik: the information content, in bits, of the most informative common
    ancestor between the proband term and the best-matching term of the model.
    That is the quantity the ranking engine itself consumes; nothing here is a
    category we invented.

Why not a simple annotated / not annotated flag
    Binary is the wrong answer to a graded question, and an "ancestor covers it"
    rule is worse: the corpus stores terms PROPAGATED to the root, so every model
    trivially annotates an ancestor of everything. That version was built, came
    out uniform, and was discarded.

Two kinds of support, kept separate
    Colour = HPO database support, in bits.
    Ring   = literature support for MVA1 specifically, from the published series.
    Literature is never converted into a Resnik score. Mixing the two is exactly
    how a phenotype gap gets talked away.

Column labels
    Disease name and gene on top, identifier small underneath. A reader should
    not have to memorise OMIM codes to see the pattern.
"""
from __future__ import annotations
import io, sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

NL2 = chr(10)
MVA_IDS = ["OMIM:257300", "OMIM:614114", "OMIM:617598"]
SHORT = {"OMIM:257300": "MVA 1", "OMIM:614114": "MVA 2", "OMIM:617598": "MVA 3"}
HPOA = "work/hpo/phenotype.hpoa"


def disease_names(path: str = HPOA) -> dict:
    """database_id -> disease_name, straight from the HPO annotation file."""
    out, hdr = {}, None
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if line.startswith("#"):
            continue
        parts = line.rstrip("\n").split("\t")
        if hdr is None:
            hdr = parts
            continue
        r = dict(zip(hdr, parts))
        did = r.get("database_id")
        if did and did not in out and r.get("disease_name"):
            out[did] = r["disease_name"]
    return out


def wrap(text: str, width: int = 22, max_lines: int = 3) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:width - 1] + "…"
    return "\n".join(lines)


def build(m: dict):
    """m: the prepared matrix, see prepare()."""
    PT, COLS = m["terms"], m["cols"]
    BM, COV, LIT = m["bestmatch"], m["covered"], m["literature"]
    names, ic_t = m["names"], m["ic_terms"]

    fig, (ax, axs) = plt.subplots(
        2, 1, figsize=(13.0, 7.6), sharex=True,
        gridspec_kw={"height_ratios": [3.6, 1.0], "hspace": 0.09})
    # Margenes explicitos: tight_layout no puede con etiquetas de fila largas
    # ni con nombres de enfermedad de tres lineas, y recortaba las dos cosas.
    fig.subplots_adjust(left=0.185, right=0.905, top=0.885, bottom=0.245)

    vmax = float(max(BM.max(), max(ic_t.values())))
    im = ax.imshow(BM, cmap="YlGnBu", vmin=0, vmax=vmax, aspect="auto")
    for i in range(len(PT)):
        for j in range(len(COLS)):
            v = BM[i, j]
            dark = v > vmax * 0.55
            ax.text(j, i - 0.10, f"{v:.1f}", ha="center", va="center",
                    fontsize=S.BASE - 0.5, color="white" if dark else S.INK,
                    fontweight="bold" if COV[i, j] else "normal")
            if COV[i, j]:
                ax.text(j, i + 0.26, "covered", ha="center", va="center",
                        fontsize=S.BASE - 2.4, color="white" if dark else S.MUTED)
            if LIT[i, j]:
                ax.add_patch(plt.Rectangle((j - 0.46, i - 0.46), 0.92, 0.92, fill=False,
                                           edgecolor=S.VERM, lw=1.6, zorder=5,
                                           linestyle=(0, (2.4, 1.4))))
    ax.set_yticks(range(len(PT)))
    ax.set_yticklabels([f"{m['term_labels'][t]}   (own IC {ic_t[t]:.1f})" for t in PT],
                       fontsize=S.BASE + 0.2)
    ax.set_xticks(range(len(COLS)))
    ax.grid(False)
    for j, c in enumerate(COLS):
        if c["id"] in MVA_IDS:
            ax.add_patch(plt.Rectangle((j - 0.5, -0.5), 1.0, len(PT), fill=False,
                                       edgecolor=S.INK, lw=1.8, zorder=6))
    S.panel(ax, "A")
    S.head(ax, "Semantic match of each proband term to each evaluated disease model "
               "(Resnik, in bits)")
    cax = fig.add_axes([0.918, 0.42, 0.011, 0.44])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("Resnik: IC of the most informative" + NL2 + "common ancestor (bits)",
                 fontsize=S.BASE - 0.8)
    cb.ax.tick_params(labelsize=S.BASE - 1.2)
    ax.legend(handles=[
        Line2D([], [], color="none", marker="s", markerfacecolor="#2B7BBA",
               markeredgecolor="none", ms=8, label="colour: HPO database support (bits)"),
        Line2D([], [], color=S.VERM, lw=1.6, ls=(0, (2.4, 1.4)),
               label="dashed ring: literature support for MVA1 (not a Resnik score)"),
        Line2D([], [], color=S.INK, lw=1.8, label="boxed columns: the three MVA models"),
    ], loc="lower left", bbox_to_anchor=(0.0, 1.045), ncol=3, fontsize=S.BASE - 1.0)

    axs.bar(range(len(COLS)), [c["bma"] for c in COLS], width=0.66, zorder=3,
            color=[S.INK if c["id"] in MVA_IDS else "#9AA4AC" for c in COLS],
            edgecolor="white", linewidth=0.5)
    axs.set_ylabel("profile BMA\n(bits)", fontsize=S.BASE - 0.5)
    axs.set_xticks(range(len(COLS)))
    axs.set_xticklabels([wrap(names.get(c["id"], c["gene"]), width=17, max_lines=2)
                         + NL2 + c["gene"] + NL2 + c["id"]
                         for c in COLS], fontsize=S.BASE - 2.2, linespacing=1.30)
    axs.tick_params(axis="x", pad=2)
    S.panel(axs, "B")
    S.grid(axs)

    i_nef = m["nephro_index"]
    mv = [j for j, c in enumerate(COLS) if c["id"] in MVA_IDS]
    ot = [j for j in range(len(COLS)) if j not in mv]
    cov_mva1 = [m["term_labels"][PT[i]] for i in range(len(PT)) if COV[i, mv[0]]]
    unc_mva1 = [m["term_labels"][PT[i]] for i in range(len(PT)) if not COV[i, mv[0]]]
    nef_other = sum(1 for j in ot if COV[i_nef, j])
    full = int(sum(1 for j in range(len(COLS)) if COV[:, j].all()))

    S.note(fig,
           f"MVA1 covers {len(cov_mva1)} of {len(PT)} proband terms by HPO annotation "
           f"({', '.join(cov_mva1).lower()}) and leaves {len(unc_mva1)} uncovered "
           f"({', '.join(unc_mva1).lower()}); {full} of {len(COLS)} models cover all "
           f"{len(PT)}.\n"
           f"Nephrocalcinosis is uncovered by all three MVA models. Its best match "
           f"{BM[i_nef, mv[0]]:.1f} bits against its own IC of "
           f"{ic_t[PT[i_nef]]:.1f}, while {nef_other} of the {len(ot)} neighbour models "
           f"do cover it, and it is the only term with neither annotation nor literature "
           f"support.\n"
           "Annotation bias is not corrected here: a poorly annotated disease scores low "
           "even where the trait occurs. Columns are the nearest models to the FULL "
           "profile, not a search for renal models.",
           y=0.006)
    return fig


def prepare(target_terms, term_labels, literature_mva1, n_cols: int = 12):
    """Everything measured; nothing here is a hand-placed category."""
    import pickle
    from src.phenotype.semantic import ancestors, resnik_bma

    prep = pickle.load(io.open("work/hpo/prepared.pkl", "rb"))
    PAR, IC, MODELS = prep["parents"], prep["ic"], prep["models"]
    cache = {}
    PT = list(target_terms)

    def bestmatch(t, model):
        at = ancestors(t, PAR, cache)
        best = 0.0
        for mt in model.terms:
            sh = at & ancestors(mt, PAR, cache)
            if sh:
                v = max(IC.get(a, 0.0) for a in sh)
                best = max(best, v)
        return best

    byid = {}
    for mo in MODELS:
        byid.setdefault(mo.disease_id, mo)
    scored = sorted(((resnik_bma(PT, mo.terms, IC, PAR, cache), mo)
                     for mo in byid.values()), key=lambda x: -x[0])
    chosen, seen = [], set()
    for did in MVA_IDS:
        if did in byid:
            chosen.append(byid[did]); seen.add(did)
    for sc, mo in scored:
        if len(chosen) >= n_cols:
            break
        if mo.disease_id not in seen:
            chosen.append(mo); seen.add(mo.disease_id)

    cols = [{"id": mo.disease_id, "gene": mo.gene,
             "bma": resnik_bma(PT, mo.terms, IC, PAR, cache)} for mo in chosen]
    BM = np.array([[bestmatch(t, mo) for mo in chosen] for t in PT])
    COV = np.array([[t in mo.terms for mo in chosen] for t in PT])
    LIT = np.zeros_like(COV)
    for i, t in enumerate(PT):
        if literature_mva1.get(t):
            for j, mo in enumerate(chosen):
                if mo.disease_id == MVA_IDS[0]:
                    LIT[i, j] = True

    names = disease_names()
    for did, short in SHORT.items():
        if did in names:
            names[did] = short + ": " + names[did].split(",")[0]
    return {"terms": PT, "cols": cols, "bestmatch": BM, "covered": COV,
            "literature": LIT, "names": names,
            "ic_terms": {t: IC.get(t, 0.0) for t in PT},
            "term_labels": term_labels, "n_models": len(byid),
            "nephro_index": PT.index("HP:0000121")}


PROBAND = [
    ("HP:0002859", "Rhabdomyosarcoma"),
    ("HP:0004322", "Short stature"),
    ("HP:0001518", "Small for gestational age"),
    ("HP:0001508", "Failure to thrive"),
    ("HP:0001622", "Premature birth"),
    ("HP:0003202", "Skeletal muscle atrophy"),
    ("HP:0000121", "Nephrocalcinosis"),
]
# Literature support in the published MVA1 series, as already recorded in the
# project. Kept as a BOOLEAN: it is never turned into bits.
LIT_MVA1 = {"HP:0002859": True, "HP:0004322": True, "HP:0001518": True,
            "HP:0001508": True, "HP:0001622": False, "HP:0003202": False,
            "HP:0000121": False}


def load_and_build():
    m = prepare([t for t, _ in PROBAND], dict(PROBAND), LIT_MVA1)
    return build(m), m


if __name__ == "__main__":
    fig, m = load_and_build()
    print(S.export(fig, "fig05_hpo_disease_matrix", "DATA", "MEASURED+EXTERNAL+DERIVED"))
