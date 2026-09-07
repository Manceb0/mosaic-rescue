#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 5I. AlphaGenome in silico mutagenesis (ISM) around the frozen candidate.

What this is
    A MODEL OUTPUT: 768 synthetic single-nucleotide substitutions (256 positions
    × 3 alternatives) scored under two pre-declared readouts. It shows where the
    model's output responds to sequence changes in the local window; it does
    not measure anything and does not classify anything.

Why two readouts, and why these
    They mirror the frozen split of the AlphaGenome block by modality:
        PRIMARY     splice sites, the modality that decided the hypothesis
        SECONDARY   DNase accessibility, on the very track already frozen for
                    the supplementary figure
    Both were fixed in the run manifest before the first prediction.

Drawing rules, fixed before looking
    1. The heatmap shows all four bases per position, mean-centred exactly as
       the official ism_matrix does; the reference base of each position is
       marked, so a reader can tell reference from alternative.
    2. The bar panel shows only the reference base's centred contribution, the
       official "sequence logo" reading of the same matrix, as bar heights: a
       letter logo at 256 positions is illegible at publication size and a bar
       carries exactly the same number.
    3. Each readout has its own symmetric colour scale; the candidate column is
       outlined; the x axis is offset from the candidate, never a coordinate.
       Colour bars live OUTSIDE the axes so heatmap columns and bars stay
       aligned to the same offsets.
    4. If the candidate is not where the window is most sensitive, nothing is
       done to make it look otherwise.

Sanitisation
    Only offsets are drawn. The figure reads work/alphagenome/ism/, gitignored.
"""
from __future__ import annotations
import gzip, io, json, os, sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Rectangle

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

DIR = "work/alphagenome/ism"
VOCAB = "ACGT"
NL2 = chr(10)


def _read(path):
    with gzip.open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def load():
    meta = json.load(io.open(os.path.join(DIR, "metadata.json"), encoding="utf-8"))
    mats = {}
    for role in ("PRIMARY", "SECONDARY"):
        f = meta["primary"]["roles"][role]["files"]["matrix"]
        mats[role] = _read(os.path.join(DIR, f))
    return meta, mats


def _exons_rel(cand_pos: int):
    """Exons of the frozen transcript as offsets from the candidate."""
    from src.structure.transcript_model import fetch
    tx = fetch()
    return [(e["start"] - cand_pos, e["end"] - cand_pos) for e in tx["exons"]], tx


def _bars(ax, logo: np.ndarray, offsets: np.ndarray, col: str):
    v = logo.sum(axis=1)               # one non-zero cell per row
    ax.bar(offsets, v, width=1.0, color=col, lw=0, rasterized=True)
    ax.axhline(0, color=S.INK, lw=0.6)
    m = float(np.abs(v).max()) if np.abs(v).max() > 0 else 1.0
    ax.set_ylim(-m * 1.25, m * 1.25)


def build(meta, mats, fig_tag: str = "Figure 5I"):
    run = meta["primary"]
    L = run["ism_window_bp"]
    cand_idx = run["candidate_index_in_window"]
    ctx_kb = run["sequence_context_bp"] / 1000.0
    P = mats["PRIMARY"]; Q = mats["SECONDARY"]
    offsets = np.asarray(P["offsets"], dtype=float)
    refseq = P["reference_window"]

    fig = plt.figure(figsize=(10.4, 9.0))
    # rows: A gene context · spacer · B heat · C bars · spacer · D heat · E bars
    gs = fig.add_gridspec(7, 1, height_ratios=[0.58, 0.16, 1.5, 0.85, 0.22, 1.5, 0.85],
                          hspace=0.42, left=0.105, right=0.905, top=0.94, bottom=0.115)
    axG = fig.add_subplot(gs[0])
    axH1 = fig.add_subplot(gs[2]); axL1 = fig.add_subplot(gs[3], sharex=axH1)
    axH2 = fig.add_subplot(gs[5], sharex=axH1); axL2 = fig.add_subplot(gs[6], sharex=axH1)

    # ---- A: gene context over the whole sequence context --------------------
    from src.model_outputs.alphagenome_common import resolve_candidate
    cand = resolve_candidate()
    exons, tx = _exons_rel(cand["position_1based"])
    half = run["sequence_context_bp"] / 2.0
    axG.set_xlim(-half, half); axG.set_ylim(0, 1); axG.set_yticks([])
    for sp in ("left", "right", "top"):
        axG.spines[sp].set_visible(False)
    axG.hlines(0.42, -half, half, color=S.HAIRLINE, lw=1.4)
    n_ex = 0
    for a, b in exons:
        if b > -half and a < half:
            axG.add_patch(Rectangle((a, 0.24), max(b - a, half * 0.003), 0.36,
                                    color="#5B6670", lw=0))
            n_ex += 1
    w0, w1 = offsets[0] - 0.5, offsets[-1] + 0.5
    axG.add_patch(Rectangle((w0, 0.06), w1 - w0, 0.80, facecolor=S.ORANGE, alpha=0.4, lw=0))
    axG.axvline(0, color=S.VERM, lw=1.2, zorder=5)
    axG.text(-half * 0.02, 0.92, "candidate", ha="right", va="top", fontsize=S.BASE - 0.8,
             color=S.VERM, fontweight="bold")
    axG.text(half * 0.02, 0.92, f"ISM window, {L} bp", ha="left", va="top",
             fontsize=S.BASE - 0.8, color=S.ORANGE, fontweight="bold")
    axG.set_xlabel(f"offset from candidate (bp), {ctx_kb:.0f} kb sequence context")
    axG.tick_params(labelsize=S.BASE - 1.2)
    axG.text(-half, 1.06, f"{tx['transcript']} · Ensembl release {tx['release']} · "
             f"{n_ex} exon(s) in context", fontsize=S.BASE - 1.4, color=S.MUTED, va="bottom")
    S.panel(axG, "A", dx=-0.075, dy=0.98)

    # ---- heatmap + bars per readout --------------------------------------
    letters = iter("BCDE")
    stats = {}
    for role, M, axH, axL, col in (("PRIMARY", P, axH1, axL1, S.VERM),
                                   ("SECONDARY", Q, axH2, axL2, S.BLUE)):
        C = np.asarray(M["centered"], dtype=float)          # L x 4
        logo = np.asarray(M["logo_ref_only"], dtype=float)
        m = float(np.abs(C).max()) if np.abs(C).max() > 0 else 1.0
        spec = run["roles"][role]["scorer"]
        rk = run["roles"][role]["ranks"]
        extent = (offsets[0] - 0.5, offsets[-1] + 0.5, 3.5, -0.5)
        im = axH.imshow(C.T, aspect="auto", cmap="RdBu_r",
                        norm=TwoSlopeNorm(vmin=-m, vcenter=0, vmax=m), extent=extent,
                        interpolation="nearest", rasterized=True)
        ref_rows = np.array([VOCAB.index(b) for b in refseq])
        axH.scatter(offsets, ref_rows, s=2.2, color=S.INK, marker="s", lw=0, zorder=4,
                    rasterized=True)
        axH.add_patch(Rectangle((-0.5, -0.5), 1.0, 4.0, fill=False, lw=1.1,
                                edgecolor=S.INK, zorder=5))
        axH.set_yticks(range(4)); axH.set_yticklabels(list(VOCAB))
        axH.tick_params(labelsize=S.BASE - 1.2)
        plt.setp(axH.get_xticklabels(), visible=False)
        label = (f"{role.lower()} readout: {spec['output'].replace('_', ' ').lower()} · "
                 f"{spec['scorer']} {spec['width']} bp · {spec['aggregation'].lower()} · "
                 + (spec["ontology_curie"] if spec["ontology_curie"] else "4 tracks"))
        S.head(axH, label)
        S.panel(axH, next(letters), dx=-0.075, dy=1.03)
        # colour bar OUTSIDE the axes: the heatmap keeps the full width and its
        # columns stay aligned with the bars of the panel below
        cax = axH.inset_axes([1.012, 0.0, 0.013, 1.0])
        cb = fig.colorbar(im, cax=cax)
        cb.set_label("centred score", fontsize=S.BASE - 1.4)
        cb.ax.tick_params(labelsize=S.BASE - 1.9)
        cb.ax.yaxis.get_offset_text().set_fontsize(S.BASE - 2.0)
        axH.text(1.0, -0.05,
                 f"candidate: position rank {rk['candidate_position_rank_of_L']} of {L} · "
                 f"substitution rank {rk['candidate_substitution_rank_of_all']} of {3 * L} · "
                 f"window max |score| at offset {rk['window_argmax_offset']:+d} bp",
                 transform=axH.transAxes, ha="right", va="top", fontsize=S.BASE - 1.6,
                 color=S.MUTED)

        _bars(axL, logo, offsets, col)
        axL.axvline(0, color=S.INK, lw=0.7, alpha=0.8)
        axL.set_ylabel("reference-base" + chr(10) + "contribution", fontsize=S.BASE - 0.8)
        axL.tick_params(labelsize=S.BASE - 1.4)
        axL.yaxis.get_offset_text().set_fontsize(S.BASE - 2.0)
        S.panel(axL, next(letters), dx=-0.075, dy=1.03)
        if axL is axL2:
            axL.set_xlabel("offset from candidate (bp)")
        else:
            plt.setp(axL.get_xticklabels(), visible=False)
        stats[role] = {"max_abs": m, "rank_pos": rk["candidate_position_rank_of_L"],
                       "rank_sub": rk["candidate_substitution_rank_of_all"],
                       "argmax_offset": rk["window_argmax_offset"]}

    ip = meta["interpretation"]
    r = ip.get("context_pearson_r", {})
    fig.suptitle(f"{fig_tag}. AlphaGenome in silico mutagenesis: local sequence sensitivity "
                 "around the frozen candidate", x=0.006, y=0.993, ha="left",
                 fontsize=S.BASE + 2.0, fontweight="bold", color=S.INK)
    S.note(fig, "PREDICTED, not measured. Model attribution only: 768 synthetic substitutions scored by a sequence model; no patient tissue, no assay." + NL2 +
           "Heatmaps: all four bases per position, centred per position exactly as the official ism_matrix; black marks = reference base; outlined column = candidate." + NL2 +
           "Bars: the reference base's centred contribution. Readouts, window and reading rule were fixed in the run manifest before the first prediction." + NL2 +
           f"Pre-declared reading: {ip['reading']}.  Context check, Pearson r between 16 kb and 100 kb: "
           f"primary {r.get('PRIMARY', float('nan')):.2f}, secondary {r.get('SECONDARY', float('nan')):.2f}.",
           y=0.004)
    return fig, {"L": L, "candidate_index": cand_idx, "readouts": stats,
                 "reading": ip["reading"], "context_r": r}


def load_and_build():
    meta, mats = load()
    return build(meta, mats)


if __name__ == "__main__":
    fig, st = load_and_build()
    print(S.export(fig, "fig04I_alphagenome_ism", "MODEL_OUTPUT", "PREDICTED"))
    print(st)
