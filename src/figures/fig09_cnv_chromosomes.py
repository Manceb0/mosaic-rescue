#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 5 of the final set (slug fig09_cnvpytor_chromosome_rd_baf).
CNVpytor chromosome-level RD and BAF summary of the patient's blood WGS, descriptive only.

What it draws and what it does not
    Every number comes from work/callers/final/go2b_cnv_hdf5_metrics.json, written by
    go2b_stop_tools/cnv_hdf5_metrics.py inside the pinned CNVpytor 1.3.2 image under the
    metrics preregistered in CNV_METRICS_PREREG.md BEFORE any value was inspected. The
    renderer sorts, scales and labels; it adds no metric, no threshold and no selection.
    Normalisation to the autosomal median (RD_ref) is the single DERIVED step and it was
    preregistered.

    Autosomes and X/Y share one axis and one normalisation but are visually separated:
    X and Y are reported with the autosomal reference, without adjustment and without
    interpretation. No copy-number guide lines at 0.5 or 1.5 are drawn on purpose.

Claim ceiling
    "Chromosome-level RD/BAF showed [the pattern drawn]." Forbidden: "aneuploidy
    detected / excluded", "mosaic fraction = X %", "chromosome N is trisomic/monosomic".
    CNVpytor's own segmentation is described for high cell fractions (PMID 34817058);
    this figure estimates no cell fraction.

Provenance
    Reads only the gitignored final artifact; the figure, the code and the QA card are
    the versioned objects. The source sha256 is printed in the provenance strip.
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
SRC = "go2b_cnv_hdf5_metrics.json"
SRC_CALLS = "go2b_cnv_read.json"
AUTO = [str(i) for i in range(1, 23)]
SEX = ["X", "Y"]
ORDER = AUTO + SEX


def build(m: dict, calls: dict, src_hash: str, calls_hash: str):
    T = m["table"]
    x = np.arange(len(ORDER))
    col = [S.GREEN if c in AUTO else S.MUTED for c in ORDER]
    fig = plt.figure(figsize=(11.6, 7.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], hspace=0.50, wspace=0.22)

    # ---------------- A · normalised read depth ------------------------------
    axA = fig.add_subplot(gs[0, 0])
    rd = np.array([T[c]["rd_median_norm"] for c in ORDER], dtype=float)
    mad = np.array([T[c]["rd_mad_norm"] for c in ORDER], dtype=float)
    axA.errorbar(x, rd, yerr=mad, fmt="none", ecolor=S.INK, elinewidth=0.8, capsize=2.2, zorder=3)
    axA.scatter(x, rd, s=28, c=col, edgecolor=S.INK, linewidth=0.5, zorder=4)
    axA.axhline(1.0, color=S.HAIRLINE, lw=1.0, zorder=1)
    axA.axvline(len(AUTO) - 0.5, color=S.HAIRLINE, lw=1.0, ls=(0, (3, 2)), zorder=1)
    axA.text(len(AUTO) + 0.5, 0.72, "X · Y: same autosomal\nreference, no adjustment,\nno interpretation",
             fontsize=S.BASE - 1.5, color=S.MUTED, ha="center", va="center")
    axA.set_xticks(x); axA.set_xticklabels(ORDER, fontsize=S.BASE - 1.0)
    axA.set_ylim(0.35, 1.15)
    axA.set_ylabel("median RD / autosomal median (100 kb bins)")
    axA.set_xlabel("chromosome")
    S.panel(axA, "A"); S.head(axA, "Normalised read depth per chromosome, median ± MAD over 100 kb bins")
    S.grid(axA)

    # ---------------- B · minor-allele fraction ------------------------------
    axB = fig.add_subplot(gs[0, 1])
    maf = np.array([T[c]["maf_median"] for c in ORDER], dtype=float)
    mmad = np.array([T[c]["maf_mad"] for c in ORDER], dtype=float)
    axB.errorbar(x, maf, yerr=mmad, fmt="none", ecolor=S.INK, elinewidth=0.8, capsize=2.2, zorder=3)
    axB.scatter(x, maf, s=28, c=col, edgecolor=S.INK, linewidth=0.5, zorder=4)
    axB.axvline(len(AUTO) - 0.5, color=S.HAIRLINE, lw=1.0, ls=(0, (3, 2)), zorder=1)
    axB.set_xticks(x); axB.set_xticklabels(ORDER, fontsize=S.BASE - 1.0)
    axB.set_ylim(0.10, 0.52)
    axB.set_ylabel("median per-bin minor-allele fraction (het SNPs)")
    axB.set_xlabel("chromosome")
    S.panel(axB, "B"); S.head(axB, "BAF summary: minor-allele fraction, median ± MAD over bins with heterozygous SNPs")
    S.grid(axB)
    ny = T["Y"]["n_het_snps"]; nby = T["Y"]["n_bins_with_het"]
    axB.annotate(f"Y: {ny} het SNPs in {nby} bins", xy=(x[-1], maf[-1]), xytext=(x[-1] - 6.0, 0.24),
                 fontsize=S.BASE - 1.3, color=S.MUTED, arrowprops=dict(arrowstyle="-|>", color=S.MUTED, lw=0.7))

    # ---------------- C · likelihood-based BAF statistics ---------------------
    axC = fig.add_subplot(gs[1, 0])
    i1 = np.array([T[c]["i1_median"] for c in ORDER], dtype=float)
    i2 = np.array([T[c]["i2_median"] for c in ORDER], dtype=float)
    axC.plot(x, i1, marker="o", ms=4.2, lw=1.0, color=S.VERM, label="i1 median: BAF deviation from 0.5 at the folded-likelihood maximum (0 = balanced)")
    axC.plot(x, i2, marker="s", ms=4.0, lw=1.0, color=S.BLUE, label="i2 median: likelihood at 0.5 / maximum likelihood (1 = compatible with 0.5)")
    axC.axvline(len(AUTO) - 0.5, color=S.HAIRLINE, lw=1.0, ls=(0, (3, 2)), zorder=1)
    axC.set_xticks(x); axC.set_xticklabels(ORDER, fontsize=S.BASE - 1.0)
    axC.set_ylim(-0.05, 1.08)
    axC.set_xlabel("chromosome"); axC.set_ylabel("statistic value, median over bins with het SNPs")
    S.panel(axC, "C"); S.head(axC, "CNVpytor per-bin BAF likelihood statistics, as emitted")
    S.grid(axC)
    axC.legend(loc="center left", bbox_to_anchor=(0.01, 0.5), fontsize=S.BASE - 1.6)

    # ---------------- D · what fed the summaries -----------------------------
    axD = fig.add_subplot(gs[1, 1])
    nhet = np.array([T[c]["n_het_snps"] for c in ORDER], dtype=float)
    nb = np.array([T[c]["n_bins_used"] for c in ORDER], dtype=float)
    ntot = np.array([T[c]["n_bins_total"] for c in ORDER], dtype=float)
    axD.bar(x - 0.2, nhet / 1000.0, width=0.4, color=S.SKY, edgecolor=S.INK, linewidth=0.4, label="heterozygous SNPs used (thousands)")
    axD2 = axD.twinx()
    axD2.bar(x + 0.2, nb / ntot, width=0.4, color=S.HAIRLINE, edgecolor=S.INK, linewidth=0.4, label="fraction of 100 kb bins with RD > 0")
    axD2.set_ylim(0, 1.05); axD2.set_ylabel("fraction of bins used")
    axD.set_xticks(x); axD.set_xticklabels(ORDER, fontsize=S.BASE - 1.0)
    axD.set_xlabel("chromosome"); axD.set_ylabel("heterozygous SNPs (thousands)")
    S.panel(axD, "D"); S.head(axD, "Denominators behind each summary")
    h1, l1 = axD.get_legend_handles_labels(); h2, l2 = axD2.get_legend_handles_labels()
    axD.legend(h1 + h2, l1 + l2, loc="lower right", bbox_to_anchor=(1.0, 1.01), ncol=1, fontsize=S.BASE - 1.8,
               handlelength=1.2, borderpad=0.2, labelspacing=0.25)

    # RD calls per chromosome are NOT plotted: the 49 RD+BAF records are raw caller inventory (AE4).
    rd_calls = calls["1_accounting"]["RD"]["total"]; cb_calls = calls["1_accounting"]["RD_BAF"]["total"]
    S.note(fig,
           f"Patient blood WGS, aggregated. Source work/callers/final/go2b_cnv_hdf5_metrics.json (sha256 {src_hash[:10]}…) · CNVpytor 1.3.2 by digest · "
           f"bin {m['bin_size']:,} bp · run 1b315b3.\n"
           f"RD_ref = {m['RD_ref_autosomal_median_bins_gt0']:,.1f} reads per bin (autosomal median of bins > 0). Metrics fixed in CNV_METRICS_PREREG.md "
           f"before any value was inspected; MAD without scale factor.\n"
           f"The caller's {rd_calls} RD and {cb_calls} RD+BAF records (go2b_cnv_read.json, sha256 {calls_hash[:10]}…) are raw inventory, "
           f"not adjudicated CNVs, and are not drawn.\n"
           f"DESCRIPTIVE ONLY. No mosaic cell fraction is estimated; cytogenetic aneuploidy is neither asserted nor excluded "
           f"(CNVpytor segmentation: high cell fractions, PMID 34817058).",
           y=0.004)
    return fig


def load_and_build():
    m, h_m = load_frozen(SRC, FINAL)                 # FAIL CLOSED: hash verificado antes de dibujar
    calls, h_c = load_frozen(SRC_CALLS, FINAL)
    return build(m, calls, h_m, h_c), {"source_sha256": h_m, "calls_sha256": h_c}


if __name__ == "__main__":
    S.use()
    fig, d = load_and_build()
    print(S.export(fig, "fig09_cnvpytor_chromosome_rd_baf", "DATA", "MEASURED+DERIVED"))
    print(d)
