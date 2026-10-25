#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 6 of the final set (slug fig10_bub1b_readlevel_assay).
BUB1B read-level breakpoint metrics, body versus equal-length flanks, descriptive only.

What it draws and what it does not
    Every point is one 1 kb bin from work/callers/final/ae3_bub1b_readlevel.json, written by
    go2b_stop_tools/ae3_bub1b_readlevel.py (pysam 0.23.0 inside the pinned CNVpytor image, BAM
    sha256 6388cd66…) under the assay preregistered in AE_PREREG_LOOKUPS.md § AE3: single 1 kb
    grid 15:40101001-40282000, bins assigned to upstream / body / downstream by midpoint inside
    exact 60 055 bp intervals (60 / 60 / 60), one CONTEXT_ONLY bin excluded from every summary.
    The six metrics and their denominators are exactly the preregistered ones; the renderer
    sorts and plots, it computes nothing new. Region medians drawn are the ones in the JSON.

    Introns 2 and 8 are subsets of the body bins shown separately ONLY because the literature
    highlighted them (Kawakami 2024, PMID 38102195; Kato 2017, PMID 28611924); they were not
    selected after seeing the BAM.

Claim ceiling (the only approved sentence)
    "The preregistered short-read breakpoint metrics for the BUB1B body and equal-length
    flanks are reported side by side; no inferential excess/no-excess threshold was defined,
    and complex insertion is not excluded." Forbidden: "excess", "no excess", "complex
    insertion excluded".
"""
from __future__ import annotations
import io, json, os, sys

import numpy as np
import matplotlib.pyplot as plt

REPO = os.environ.get("MOSAIC_REPO", ".")
sys.path.insert(0, REPO)
from src.figures import style as S                                     # noqa: E402

from src.figures.frozen import load_frozen                             # noqa: E402

FINAL = os.path.join(REPO, "work/callers/final")
SRC = "ae3_bub1b_readlevel.json"
GROUPS = [("upstream", "up-\nstream", S.MUTED), ("body", "BUB1B\nbody", S.GREEN),
          ("downstream", "down-\nstream", S.MUTED), ("intron_2", "intron\n2 *", S.SKY),
          ("intron_8", "intron\n8 *", S.SKY)]
METRICS = [("f_softclip", "f_softclip · soft clip ≥ 20 bp", "fraction of bin reads"),
           ("f_split", "f_split · SA tag present", "fraction of bin reads"),
           ("f_discordant", "f_discordant · preregistered definition", "fraction of bin reads"),
           ("f_mapq0", "f_mapq0 · MAPQ = 0", "fraction of bin reads"),
           ("n_clip_clusters", "n_clip_clusters · ≥ 3 reads, same clip coordinate + side", "clusters per bin"),
           ("n_reads", "n_reads · reads starting in the bin (denominator)", "reads per bin")]


def bins_of(per_bin, key):
    if key in ("upstream", "body", "downstream"):
        return [b for b in per_bin if b["region"] == key]
    return [b for b in per_bin if key in b["literature"]]


def build(d: dict, src_hash: str):
    per_bin = d["per_bin"]; summ = d["summary"]
    rng = np.random.default_rng(7)                       # jitter only; fixed seed for byte-identical SVG
    fig = plt.figure(figsize=(11.6, 7.6))
    gs = fig.add_gridspec(2, 3, hspace=0.62, wspace=0.30)
    for k, (metric, title, ylab) in enumerate(METRICS):
        ax = fig.add_subplot(gs[k // 3, k % 3])
        for gi, (key, label, col) in enumerate(GROUPS):
            vals = np.array([b[metric] for b in bins_of(per_bin, key) if b[metric] is not None], dtype=float)
            xj = gi + rng.uniform(-0.18, 0.18, size=len(vals))
            ax.scatter(xj, vals, s=11, color=col, alpha=0.75, linewidth=0, zorder=3)
            if metric in summ[key]:
                med = summ[key][metric]["median"] if isinstance(summ[key][metric], dict) else None
            else:
                med = None
            if metric == "n_clip_clusters":
                med = None
            if med is not None:
                ax.hlines(med, gi - 0.30, gi + 0.30, color=S.INK, lw=1.4, zorder=4)
        if metric == "n_clip_clusters":
            for gi, (key, label, col) in enumerate(GROUPS):
                ax.text(gi, ax.get_ylim()[1] * 0.0 + max(b["n_clip_clusters"] for b in per_bin) * 1.08,
                        f"Σ {summ[key]['sum_n_clip_clusters']}", ha="center", fontsize=S.BASE - 1.4, color=S.INK)
            ax.set_ylim(-0.3, max(b["n_clip_clusters"] for b in per_bin) * 1.25)
        if metric == "n_reads":
            for gi, (key, label, col) in enumerate(GROUPS):
                ax.text(gi, max(b["n_reads"] for b in per_bin) * 1.08, f"{summ[key]['n_bins_contributing']} bins",
                        ha="center", fontsize=S.BASE - 1.4, color=S.INK)
            ax.set_ylim(0, max(b["n_reads"] for b in per_bin) * 1.25)
        ax.set_xticks(range(len(GROUPS))); ax.set_xticklabels([g[1] for g in GROUPS], fontsize=S.BASE - 1.8)
        ax.set_ylabel(ylab)
        S.panel(ax, "ABCDEF"[k]); S.head(ax, title, size=S.BASE - 0.3)
        S.grid(ax)
        ax.axvline(2.5, color=S.HAIRLINE, lw=1.0, ls=(0, (3, 2)), zorder=1)
    fig.subplots_adjust(bottom=0.155, top=0.885)
    fig.text(0.5, 0.955, "Each point is one 1 kb bin; black bar = region median from the frozen summary. Upstream, body and downstream are exact "
             "60 055 bp intervals.\n* Intron 2 and intron 8 are subsets of the body, shown separately only because the literature highlighted them; "
             "they were not chosen after seeing the BAM.",
             ha="center", va="center", fontsize=S.BASE - 0.9, color=S.MUTED)
    S.note(fig,
           f"Patient blood WGS BAM (sha256 6388cd66…), pysam 0.23.0 inside the pinned CNVpytor image. Source work/callers/final/ae3_bub1b_readlevel.json "
           f"(sha256 {src_hash[:10]}…) · run 1b315b3.\n"
           f"Assay preregistered in AE_PREREG_LOOKUPS.md § AE3: grid 15:40101001-40282000 in 1 kb bins; bin midpoint inside exact 60 055 bp intervals → "
           f"{d['assignment']['upstream']} / {d['assignment']['body']} / {d['assignment']['downstream']} bins; {d['assignment']['CONTEXT_ONLY']} CONTEXT_ONLY bin excluded.\n"
           f"Reads: primary, not secondary, not supplementary, not duplicate, not QC-fail; n_reads = reads whose alignment starts in the bin; "
           f"discordant = unpaired, mate unmapped, other contig, |TLEN| > 1 000 bp or not a proper pair.\n"
           f"DESCRIPTIVE ONLY. The preregistered short-read breakpoint metrics for the BUB1B body and equal-length flanks are reported side by side;\n"
           f"no inferential excess/no-excess threshold was defined, and complex insertion is not excluded (Kawakami 2024, PMID 38102195).",
           y=0.004)
    return fig


def load_and_build():
    d, h = load_frozen(SRC, FINAL)                   # FAIL CLOSED: hash verificado antes de dibujar
    return build(d, h), {"source_sha256": h}


if __name__ == "__main__":
    S.use()
    fig, meta = load_and_build()
    print(S.export(fig, "fig10_bub1b_readlevel_assay", "DATA", "MEASURED+DERIVED"))
    print(meta)
