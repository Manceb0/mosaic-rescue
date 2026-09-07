#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 5C. AlphaGenome-predicted chromatin contact maps: REF, ALT and ALT − REF.

What this is
    A MODEL OUTPUT. The three maps are predictions from sequence for one
    pre-declared biosample; they are not Hi-C, not measured, and not from
    the patient or any tissue. The word PREDICTED is on the figure.

Drawing rules, fixed in the run manifest before the prediction was made
    1. REF and ALT share one colour scale. Without this any difference can be
       manufactured by rescaling. The scale is log10(1 + signal), the usual
       way to look at a contact map whose strong pairs are three orders of
       magnitude above its diagonal; nothing is clipped, and the transform is
       identical for both maps and stated on the figure.
    2. ALT − REF is drawn in LINEAR units on its own diverging scale, symmetric
       around a visible zero, never transformed and never clipped.
    3. The candidate-containing bin is marked on all three maps, on both axes.
    4. The 28-track robustness strip is shown so the reader can see where the
       pre-declared biosample falls; it was never used to choose the biosample.

Sanitisation
    Axes are offsets from the candidate in kb. No absolute coordinate is drawn.
    The figure reads only work/alphagenome/contacts/, which is gitignored.
"""
from __future__ import annotations
import io, json, os, sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

DIR = "work/alphagenome/contacts"
NL2 = chr(10)


def load():
    meta = json.load(io.open(os.path.join(DIR, "metadata.json"), encoding="utf-8"))
    z = np.load(os.path.join(DIR, "matrices.npz"))
    rob = json.load(io.open(os.path.join(DIR, "robustness_scores.json"), encoding="utf-8"))
    return meta, z["ref"], z["alt"], z["delta"], rob


def build(meta, ref, alt, delta, rob, fig_tag: str = "Figure 5C"):
    n = ref.shape[0]
    res_kb = meta["output_resolution_bp"] / 1000.0
    cb_idx = meta["candidate_bin"]
    lo, hi = -(cb_idx + 0.5) * res_kb, (n - cb_idx - 0.5) * res_kb   # kb from candidate
    extent = (lo, hi, hi, lo)
    L_ref, L_alt = np.log10(1.0 + np.clip(ref, 0, None)), np.log10(1.0 + np.clip(alt, 0, None))
    vmax = float(max(L_ref.max(), L_alt.max(), 1e-12))
    dmax = float(max(np.abs(delta).max(), 1e-12))

    fig = plt.figure(figsize=(12.8, 5.5))
    # a spacer column keeps panel D's labels clear of panel C's colour bar
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 0.22, 0.62], wspace=0.26,
                          left=0.05, right=0.985, top=0.86, bottom=0.23)
    axes = [fig.add_subplot(gs[i]) for i in range(3)]
    axR = fig.add_subplot(gs[4])

    for ax, M, title, letter in ((axes[0], L_ref, "REF, predicted", "A"),
                                 (axes[1], L_alt, "ALT, predicted", "B")):
        im = ax.imshow(M, cmap="YlOrRd", vmin=0, vmax=vmax, extent=extent,
                       interpolation="nearest", rasterized=True)
        S.head(ax, title)
        S.panel(ax, letter, dx=-0.16, dy=1.02)
    imD = axes[2].imshow(delta, cmap="RdBu_r",
                         norm=TwoSlopeNorm(vmin=-dmax, vcenter=0, vmax=dmax),
                         extent=extent, interpolation="nearest", rasterized=True)
    S.head(axes[2], "ALT − REF, linear, zero-centred")
    S.panel(axes[2], "C", dx=-0.16, dy=1.02)
    for i, ax in enumerate(axes):
        ax.axvline(0, color=S.INK, lw=0.5, alpha=0.7)
        ax.axhline(0, color=S.INK, lw=0.5, alpha=0.7)
        ax.set_xlabel("offset from candidate (kb)")
        ax.set_xticks([-400, -200, 0, 200, 400]); ax.set_yticks([-400, -200, 0, 200, 400])
        ax.tick_params(labelsize=S.BASE - 1.2)
        if i == 0:
            ax.set_ylabel("offset from candidate (kb)")
        else:
            plt.setp(ax.get_yticklabels(), visible=False)   # same axis as A
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(True)
    # colour bars outside the axes, so the three maps keep the same size
    cax1 = axes[1].inset_axes([1.04, 0.0, 0.045, 1.0])
    cb1 = fig.colorbar(im, cax=cax1)
    cb1.set_label("log10(1 + predicted contact signal), REF and ALT", fontsize=S.BASE - 1.4)
    cb1.ax.tick_params(labelsize=S.BASE - 1.8)
    cax2 = axes[2].inset_axes([1.04, 0.0, 0.045, 1.0])
    cb2 = fig.colorbar(imD, cax=cax2)
    cb2.set_label("ALT − REF (model units, linear)", fontsize=S.BASE - 1.4)
    cb2.ax.tick_params(labelsize=S.BASE - 1.8)

    # ---- D: robustness strip, all contact tracks, chosen one highlighted ----
    rows = sorted(rob["rows"], key=lambda r: r["score"])
    sc = np.array([r["score"] for r in rows]) * 1e3
    chosen = [i for i, r in enumerate(rows) if r["ontology_curie"] == rob["chosen_ontology"]]
    y = np.arange(len(rows))
    axR.scatter(sc, y, s=13, color=S.MUTED, marker="o", zorder=3)
    for i in chosen:
        axR.scatter(sc[i], y[i], s=36, color=S.VERM, marker="D", zorder=4)
        axR.text(sc[i], y[i] + 1.1, rows[i]["biosample_name"], fontsize=S.BASE - 1.4,
                 color=S.VERM, ha="center", va="bottom", fontweight="bold")
    axR.axvline(float(np.median(sc)), color=S.HAIRLINE, lw=0.9, ls="--")
    axR.set_yticks([]); axR.set_ylabel(f"{len(rows)} contact tracks, ranked")
    axR.set_xlabel("ContactMapScorer, local" + chr(10) + "disruption (×10⁻³, model units)")
    axR.tick_params(labelsize=S.BASE - 1.4)
    axR.set_ylim(-1, len(rows) + 1.5)
    S.head(axR, "Robustness across biosamples")
    S.panel(axR, "D", dx=-0.12, dy=1.02)
    S.grid(axR, "x")

    ratio = meta["interpretation"]["ratio"]
    fig.suptitle(f"{fig_tag}. AlphaGenome predicted chromatin contacts around the frozen "
                 f"candidate: {meta['biosample_name']}", x=0.006, y=0.985, ha="left",
                 fontsize=S.BASE + 2.0, fontweight="bold", color=S.INK)
    S.note(fig, "PREDICTED, not measured. Not Hi-C, not patient chromatin, not any tissue: a sequence model's output for one biosample chosen before the prediction." + NL2 +
           f"1 Mb window, {n}×{n} bins of {meta['output_resolution_bp']} bp. REF and ALT share one log10(1 + signal) scale, unclipped; ALT − REF is linear, zero-centred, symmetric, unclipped." + NL2 +
           f"max |ALT − REF| = {meta['interpretation']['max_abs_delta']:.3g} against max REF = "
           f"{meta['interpretation']['max_abs_ref']:.3g} ({100 * ratio:.2f} %; pre-declared threshold 5 %).  "
           f"The {len(rows)}-track strip is context, not a selection.",
           y=0.004)
    return fig, {"n_bins": n, "ratio": ratio, "visible": meta["interpretation"]["visible"],
                 "chosen_rank": rob["chosen_rank_of_n"], "n_tracks": len(rows),
                 "scale": "log10(1+x) shared by REF and ALT; delta linear"}


def load_and_build():
    meta, ref, alt, delta, rob = load()
    return build(meta, ref, alt, delta, rob)


if __name__ == "__main__":
    fig, st = load_and_build()
    print(S.export(fig, "fig04C_alphagenome_contact_maps", "MODEL_OUTPUT", "PREDICTED"))
    print(st)
