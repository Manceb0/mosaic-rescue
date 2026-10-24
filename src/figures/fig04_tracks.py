#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figures 5 and 5S. AlphaGenome REF, ALT and Δ browser around the candidate.

Why two figures and not one
    Nine tracks squeezed into one slide-shaped panel read as noise. Legibility
    wins over count, so the tracks are split by modality, a split fixed by what
    the modality is, never by which tracks look better:
        main         RNA expression + splicing   (the modalities that decide the
                                                  regulatory hypothesis)
        supplement   chromatin accessibility + TF binding
    Both figures use the same layout, the same relative x axis and the same
    drawing rules, so they can be read side by side.

Two drawing rules, fixed before looking at the data
    1. REF and ALT share the exact same y scale inside a track. Without this,
       any difference can be manufactured by rescaling.
    2. Δ = ALT − REF sits in its own lane with zero visible and a symmetric
       scale. It is never overlaid on the REF/ALT lane.

What these tracks are
    Model PREDICTIONS. They are not measurements, not from patient tissue, and
    not from any tissue. The word PREDICTED is in the figure, not only in the
    caption.

Sanitisation
    The x axis is offset from the variant. No absolute coordinate is drawn.
"""
from __future__ import annotations
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

GROUPS = {
    "main": {
        "title": "RNA expression and splicing",
        "mods": ["rna_seq", "splice_sites", "splice_site_usage", "splice_junctions"],
    },
    "supp": {
        "title": "Chromatin accessibility and transcription-factor binding",
        "mods": ["atac", "dnase", "chip_tf"],
    },
}
MOD_LABEL = {
    "rna_seq": "RNA-seq", "splice_sites": "splice sites",
    "splice_site_usage": "splice site usage", "splice_junctions": "splice junctions",
    "atac": "ATAC", "dnase": "DNase", "chip_tf": "TF ChIP",
}
MOD_COL = {
    "rna_seq": S.GREEN, "splice_sites": S.VERM, "splice_site_usage": S.VERM,
    "splice_junctions": S.VERM, "atac": S.BLUE, "dnase": S.BLUE, "chip_tf": S.PURPLE,
}


def select(tracks, which: str):
    mods = GROUPS[which]["mods"]
    return [t for m in mods for t in tracks if t["mod"] == m]


NL2 = chr(10)


def build(tracks, exons_rel, flank, transcript, release, which: str, fig_tag: str):
    sel = select(tracks, which)
    n = len(sel)
    fig = plt.figure(figsize=(10.4, 1.35 + 1.62 * n))
    gs = fig.add_gridspec(1 + 2 * n, 1,
                          height_ratios=[0.90] + [2.05, 0.95] * n, hspace=0.0)
    axG = fig.add_subplot(gs[0])
    XL = (-flank, flank)

    # ---- gene model + candidate marker -------------------------------------
    axG.set_xlim(*XL); axG.set_ylim(0, 1); axG.set_yticks([])
    for sp in ("left", "right", "top", "bottom"):
        axG.spines[sp].set_visible(False)
    # set_xticks([]) en este eje borraba los ticks de los nueve paneles, porque
    # comparten eje x. Se ocultan solo las etiquetas de este.
    axG.tick_params(axis="x", length=0, labelbottom=False)
    axG.hlines(0.32, XL[0], XL[1], color=S.HAIRLINE, lw=1.4)
    for a, b in exons_rel:
        axG.add_patch(plt.Rectangle((a, 0.14), max(b - a, flank * 0.0016), 0.36,
                                    color="#5B6670", lw=0))
    axG.axvline(0, color=S.VERM, lw=1.3, zorder=5)
    axG.text(0, 0.54, "candidate variant", ha="center", va="bottom",
             fontsize=S.BASE - 0.5, color=S.VERM, fontweight="bold")
    S.panel(axG, "A", dx=-0.085, dy=0.24)
    axG.text(XL[0], 0.88, f"{transcript} · Ensembl release {release} · "
             f"{len(exons_rel)} exons in window", fontsize=S.BASE - 1.4,
             color=S.MUTED, va="top")

    letters = "BCDEFGHIJK"
    for i, t in enumerate(sel):
        axT = fig.add_subplot(gs[1 + 2 * i], sharex=axG)
        axD = fig.add_subplot(gs[2 + 2 * i], sharex=axG)
        ref = np.asarray(t["ref"], dtype=float)
        alt = np.asarray(t["alt"], dtype=float)
        bp = float(t["bp_per_bin"])
        x = (np.arange(len(ref)) - len(ref) / 2.0) * bp + bp / 2.0
        col = MOD_COL.get(t["mod"], S.MUTED)

        # rasterized=True SOLO en los trazos densos: a 1 pb/bin son 10 000 puntos
        # por pista y el SVG se iba a 8 MB, ilegible para cualquier editor
        # vectorial. Ejes, ticks y texto siguen siendo vector, que es lo que
        # importa para una figura de publicacion.
        axT.fill_between(x, 0, ref, step="mid", color=col, alpha=0.26, lw=0,
                         rasterized=True)
        axT.step(x, ref, where="mid", color=col, lw=1.0, label="REF",
                 rasterized=True)
        axT.step(x, alt, where="mid", color=S.INK, lw=0.9, ls=(0, (2.6, 1.6)),
                 label="ALT", rasterized=True)
        hi = max(float(ref.max()), float(alt.max()), 1e-12)
        axT.set_ylim(0, hi * 1.30)                      # identical for REF and ALT
        axT.axvline(0, color=S.VERM, lw=0.8, alpha=0.8)
        axT.set_ylabel(MOD_LABEL.get(t["mod"], t["mod"]), fontsize=S.BASE - 0.5,
                       rotation=0, ha="right", va="center", labelpad=8)
        axT.tick_params(labelsize=S.BASE - 1.4)
        # Los ticks extremos de una pista chocaban con los de la lane de delta
        # de abajo. Se podan los extremos y se limita el numero.
        from matplotlib.ticker import MaxNLocator
        axT.yaxis.set_major_locator(MaxNLocator(nbins=4, prune="lower"))
        plt.setp(axT.get_xticklabels(), visible=False)
        S.panel(axT, letters[i], dx=-0.085, dy=0.66)
        axT.text(XL[0] * 0.985, hi * 1.13, str(t["meta"])[:72],
                 fontsize=S.BASE - 1.6, color=S.MUTED)
        axT.text(XL[1] * 0.985, hi * 1.13,
                 f"{bp:.0f} bp/bin · REF max {ref.max():.4g}", ha="right",
                 fontsize=S.BASE - 1.6, color=S.MUTED)
        if i == 0:
            axT.legend(ncol=2, loc="lower right", fontsize=S.BASE - 1.2,
                       bbox_to_anchor=(1.0, 1.10))

        d = alt - ref
        m = float(np.abs(d).max())
        lim = m * 1.45 if m > 0 else 1.0
        axD.fill_between(x, 0, d, step="mid", color=S.VERM, alpha=0.85, lw=0,
                         rasterized=True)
        axD.axhline(0, color=S.INK, lw=0.7)             # zero always visible
        axD.set_ylim(-lim, lim)
        axD.set_ylabel("Δ", fontsize=S.BASE - 0.5, rotation=0, ha="right",
                       va="center", labelpad=8)
        axD.tick_params(labelsize=S.BASE - 1.8)
        axD.yaxis.set_major_locator(MaxNLocator(nbins=3, prune="upper"))
        axD.text(XL[1] * 0.985, lim * 0.52, f"max |Δ| = {m:.4g}", ha="right",
                 fontsize=S.BASE - 1.6, color=S.VERM)
        if i < n - 1:
            plt.setp(axD.get_xticklabels(), visible=False)
        else:
            axD.set_xlabel("offset from candidate variant (bp)")

    axG.set_xlim(*XL)
    mx = max(float(np.abs(np.asarray(t["alt"], dtype=float)
                          - np.asarray(t["ref"], dtype=float)).max()) for t in sel)
    fig.suptitle(f"AlphaGenome predicted tracks: {GROUPS[which]['title']}",
                 x=0.006, y=0.998, ha="left", fontsize=S.BASE + 2.0,
                 fontweight="bold", color=S.INK)
    fig.tight_layout(rect=(0.02, 0.056, 1, 0.972))
    S.note(fig, "PREDICTED, not measured. No patient tissue, and no tissue of any kind, is behind these tracks." + NL2 +
           "REF and ALT share the exact y scale within each track; Δ = ALT − REF has its own symmetric lane with zero visible." + NL2 +
           "Tracks were frozen before the call was repeated; the split from the supplement is by modality, not appearance.  ·  "
           f"largest |Δ| in any bin shown here: {mx:.4g}", y=0.004)

    return fig, {"n_tracks": n, "max_abs_delta": mx}


def load_and_build():
    import glob, io, json
    from src.structure.transcript_model import fetch
    ar = json.load(io.open(glob.glob("work/alphagenome/arrays_*.json")[0], encoding="utf-8"))
    tx = fetch()
    vpos, flank = ar["pos"], ar["flank_bp"]
    exons_rel = [(e["start"] - vpos, e["end"] - vpos) for e in tx["exons"]
                 if e["end"] > vpos - flank and e["start"] < vpos + flank]
    out = {}
    for which, tag in (("main", "Figure 5"), ("supp", "Figure 5S")):
        out[which] = build(ar["tracks"], exons_rel, flank, tx["transcript"],
                           tx["release"], which, tag)
    return out, ar


if __name__ == "__main__":
    out, ar = load_and_build()
    print(S.export(out["main"][0], "fig04_alphagenome_rna_splicing",
                   "MODEL_OUTPUT", "PREDICTED"))
    print(S.export(out["supp"][0], "fig04S_alphagenome_accessibility_tf",
                   "MODEL_OUTPUT", "PREDICTED"))
