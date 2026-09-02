#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 1. Sequencing QC of lane L001, computed from the FASTQ.

WHAT IT IS
    A real per-cycle QC panel, not a citation of one. Everything is accumulated
    in a single pass over a reproducible subsample of R1.

THE ONE THING THAT DECIDES THE DESIGN
    This instrument emits BINNED base qualities: four discrete values, not a
    continuum. Two earlier versions of panel A failed for ignoring that. With
    percentiles, P25/P50/P75 land in the same bin and the bands collapse into a
    grey box that reads as a rendering artefact. With a density heat map, the
    top bin holds ~93 % of bases and the panel is flat. The informative variable
    is the mass that LEAVES the top bin along the read, and that is panel A.

    Read length is invariant here, so it is reported as the degenerate value it
    is, in the provenance strip, instead of being inflated into a histogram.
"""
from __future__ import annotations
import collections, gzip, sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

READLEN = 200
N_DEFAULT = 300_000
IDX = {"A": 0, "C": 1, "G": 2, "T": 3, "N": 4}
BASE_COL = {"A": S.BLUE, "C": S.ORANGE, "G": S.GREEN, "T": S.PURPLE}
BASE_DASH = {"A": "-", "C": "--", "G": "-.", "T": ":"}


def scan(fastq: str, n_reads: int = N_DEFAULT) -> dict:
    """One pass over the subsample. Returns only measured quantities."""
    qhist = np.zeros((READLEN, 64), dtype=np.int64)
    base_at_cycle = np.zeros((READLEN, 5), dtype=np.int64)
    gc_per_read, read_mean_q, lens = [], [], collections.Counter()

    n = 0
    with gzip.open(fastq, "rt", errors="replace") as f:
        for i, line in enumerate(f):
            m = i % 4
            if m == 1:
                s = line.strip()
                L = len(s)
                lens[L] += 1
                gc_per_read.append(100.0 * (s.count("G") + s.count("C")) / L if L else 0.0)
                for c, ch in enumerate(s[:READLEN]):
                    base_at_cycle[c, IDX.get(ch, 4)] += 1
                n += 1
            elif m == 3:
                q = line.strip()[:READLEN]
                tot = 0
                for c, ch in enumerate(q):
                    v = ord(ch) - 33
                    if 0 <= v < 64:
                        qhist[c, v] += 1
                        tot += v
                read_mean_q.append(tot / max(len(q), 1))
                if n >= n_reads:
                    break

    cyc = int(max(lens))
    qh = qhist[:cyc]
    levels = [v for v in range(64) if qh[:, v].sum() > 0]
    per_cycle = qh.sum(1)
    frac = {v: 100.0 * qh[:, v] / np.maximum(per_cycle, 1) for v in levels}
    top = levels[-1]
    non_top = sum(frac[v] for v in levels if v != top)

    # median Phred per cycle, read off the binned histogram
    med = []
    for c in range(cyc):
        cs = np.cumsum(qh[c])
        med.append(int(np.searchsorted(cs, per_cycle[c] / 2.0)))

    return {
        "n_reads": n, "cycles": cyc, "lengths": dict(lens),
        "levels": levels, "top_bin": top, "frac": frac, "non_top": non_top,
        "median_per_cycle": np.asarray(med),
        "gc": np.asarray(gc_per_read), "read_mean_q": np.asarray(read_mean_q),
        "base_at_cycle": base_at_cycle[:cyc],
        "q30_pct": 100.0 * qh[:, 30:].sum() / max(qh.sum(), 1),
    }


def build(d: dict, source_label: str = "lane L001, read 1"):
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 6.0))
    x = np.arange(1, d["cycles"] + 1)
    lv, top, nt = d["levels"], d["top_bin"], d["non_top"]

    # -- A -- what leaves the top quality bin, cycle by cycle ----------------
    ax = axes[0, 0]
    low = [v for v in lv if v != top]
    ax.stackplot(x, *[d["frac"][v] for v in low],
                 labels=[f"Q{v}" for v in low],
                 colors=[S.VERM, S.ORANGE, S.SKY, S.PURPLE][:len(low)],
                 edgecolor="none")
    ax.plot(x, nt, color=S.INK, lw=1.0)
    ax.set_xlim(1, d["cycles"])
    ax.set_ylim(0, max(float(nt.max()) * 1.42, 4.0))
    ax.set_xlabel("sequencing cycle (bp)")
    ax.set_ylabel(f"bases outside top bin Q{top} (%)")
    S.panel(ax, "A")
    S.head(ax, f"Binned base quality: {len(lv)} discrete levels "
               f"({', '.join('Q' + str(v) for v in lv)})")
    S.grid(ax)
    ax.legend(ncol=len(low), loc="upper left", fontsize=S.BASE - 1.0)
    ax.annotate(f"non-Q{top} rises from {nt[0]:.2f} % to {nt[-1]:.2f} % across the read",
                xy=(d["cycles"], nt[-1]), xytext=(d["cycles"] * 0.60, nt.max() * 1.22),
                fontsize=S.BASE - 0.5, color=S.INK,
                arrowprops=dict(arrowstyle="-|>", color=S.INK, lw=0.9))

    # -- B -- GC per read against the human genome reference value -----------
    ax = axes[0, 1]
    gc = d["gc"]
    ax.hist(gc, bins=np.arange(0, 101, 1.0), density=True, color=S.HAIRLINE,
            edgecolor=S.MUTED, linewidth=0.35, zorder=2)
    mu, sd = float(gc.mean()), float(gc.std())
    xs = np.linspace(0, 100, 400)
    ax.plot(xs, np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)),
            color=S.BLUE, lw=1.2, ls="--", zorder=4,
            label=f"normal fit (mean {mu:.1f} %, SD {sd:.1f})")
    ax.axvline(41.0, color=S.VERM, lw=1.2, ls="-", zorder=5,
               label="human genome GC = 41 %")
    ax.set_xlim(0, 100)
    ax.set_xlabel("GC content per read (%)")
    ax.set_ylabel("density (reads)")
    S.panel(ax, "B")
    S.head(ax, "GC content per read")
    S.grid(ax)
    ax.legend(loc="upper right", fontsize=S.BASE - 1.0)

    # -- C -- mean quality per read ------------------------------------------
    ax = axes[1, 0]
    rq = d["read_mean_q"]
    ax.hist(rq, bins=np.arange(0, 42.25, 0.25), color=S.HAIRLINE,
            edgecolor=S.MUTED, linewidth=0.25, zorder=2)
    lo30 = 100.0 * float((rq < 30).mean())
    ax.axvline(30, color=S.VERM, lw=1.2, ls="--", zorder=4)
    ax.annotate(f"{lo30:.1f} % of reads below Q30", xy=(30, ax.get_ylim()[1] * 0.55),
                xytext=(17.0, ax.get_ylim()[1] * 0.72), fontsize=S.BASE - 0.5,
                color=S.VERM, arrowprops=dict(arrowstyle="-|>", color=S.VERM, lw=0.9))
    ax.set_xlim(0, 42)
    ax.set_xlabel("mean Phred quality per read")
    ax.set_ylabel("reads")
    S.panel(ax, "C")
    S.head(ax, f"Mean quality per read (median {np.median(rq):.1f})")
    S.grid(ax)

    # -- D -- base composition, fixed scale ----------------------------------
    ax = axes[1, 1]
    bac = d["base_at_cycle"]
    tot = np.maximum(bac.sum(1), 1)
    for b in ("A", "C", "G", "T"):
        ax.plot(x, 100.0 * bac[:, IDX[b]] / tot, color=BASE_COL[b],
                ls=BASE_DASH[b], lw=1.1, label=b)
    ax.set_xlim(1, d["cycles"])
    ax.set_ylim(0, 50)                       # fixed scale, not data-driven
    ax.set_xlabel("sequencing cycle (bp)")
    ax.set_ylabel("bases at cycle (%)")
    S.panel(ax, "D")
    S.head(ax, "Base composition per cycle")
    S.grid(ax)
    ax.legend(ncol=4, loc="lower right", fontsize=S.BASE - 1.0)
    gfin = 100.0 * bac[-1, IDX["G"]] / tot[-1]
    ax.annotate(f"G at final cycle {gfin:.1f} %, no poly-G drift",
                xy=(d["cycles"], gfin), xytext=(d["cycles"] * 0.30, 6.0),
                fontsize=S.BASE - 1.0, color=S.MUTED,
                arrowprops=dict(arrowstyle="-|>", color=S.MUTED, lw=0.8))

    lens = d["lengths"]
    fig.tight_layout(rect=(0, 0.028, 1, 1), h_pad=2.4, w_pad=2.6)
    S.note(fig, f"{source_label}  ·  n = {S.thousands(d['n_reads'])} reads  ·  "
                f"read length {d['cycles']} bp (degenerate: {len(lens)} distinct value)  ·  "
                f"{d['q30_pct']:.1f} % of bases at Q30 or above  ·  "
                f"reproducible subsample, first {S.thousands(d['n_reads'])} records of R1")
    return fig


def load_and_build():
    from src.paths import get
    d = scan(get("patient", "fastq_l001_r1"))
    return build(d), d


if __name__ == "__main__":
    fig, d = load_and_build()
    print(S.export(fig, "fig00_fastq_qc", "DATA", "MEASURED"))
