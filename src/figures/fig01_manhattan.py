#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 2. Genome-wide gene prioritization with no panel applied.

THIS IS NOT A MANHATTAN PLOT OF ASSOCIATION
    The y axis is a prioritization SCORE: a weighted sum of terms we chose. It
    is not a test statistic, there is no null distribution behind it and there
    is no p-value. So this figure deliberately refuses the visual grammar of
    GWAS: no -log10(p) axis, no genome-wide significance line, no "hits above
    the threshold". Borrowing that grammar would import a statistical claim we
    have not earned.

THE MISREADING THIS FIGURE IS BUILT TO PREVENT
    That only 151 genes competed. They did not. 6,321 genes carry a HIGH or
    MODERATE consequence allele; 151 of them additionally satisfy an inheritance
    model and therefore receive a score. Both universes are drawn: the scored
    subset as points, the full universe as a rug on the baseline and as a
    density track below.

FROZEN NUMBERS
    The score plotted is A0 as preregistered and FROZEN. In that version BUB1B
    ranks #4. The later A0-FREQFIX sensitivity puts it #1. Project rule: the two
    numbers are always reported together, and this figure shows the frozen one.
"""
from __future__ import annotations
import collections, gzip, sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

BIN = 1_000_000          # 1 Mb: the axis resolution, and the sanitisation floor
HIGHLIGHT = "BUB1B"


def contig_lengths(vcf: str) -> dict:
    out = {}
    with gzip.open(vcf, "rt", errors="replace") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line.startswith("##contig="):
                d = dict(kv.split("=", 1) for kv in line.strip()[10:-1].split(",")
                         if "=" in kv)
                if "ID" in d and "length" in d:
                    out[d["ID"]] = int(d["length"])
    return out


def genome_axis(contigs: dict):
    plain = [str(i) for i in range(1, 23)] + ["X", "Y"]
    ch = [c for c in plain if c in contigs] or \
         [c for c in ("chr" + c for c in plain) if c in contigs]
    off, acc = {}, 0
    for c in ch:
        off[c] = acc
        acc += contigs[c] // BIN + 1
    return ch, off, acc


def prepare(by_gene: dict, a0: list, contigs: dict) -> dict:
    """by_gene: gene -> [Variant]; a0: frozen A0 ranking [(gene, score, ...)]."""
    ch, off, total = genome_axis(contigs)

    def gbin(g):
        vs = by_gene.get(g, [])
        if not vs:
            return None
        c = vs[0].loc.split(":")[0]
        if c not in off:
            return None
        p = min(int(v.loc.split(":")[1].split("-")[0]) for v in vs)
        return c, off[c] + p // BIN      # rounded to 1 Mb before it leaves here

    scored = []
    for rank, row in enumerate(a0, start=1):
        g, sc = row[0], row[1]
        b = gbin(g)
        if b:
            scored.append({"gene": g, "chrom": b[0], "x": b[1], "score": float(sc),
                           "rank": rank})
    scored_names = {s["gene"] for s in scored}

    universe_x, load = [], collections.Counter()
    for g in by_gene:
        b = gbin(g)
        if b:
            universe_x.append(b[1])
            load[b[1]] += 1

    return {"ch": ch, "off": off, "total": total, "contigs": contigs,
            "scored": scored, "universe_x": np.asarray(universe_x), "load": load,
            "n_universe": len(by_gene), "n_scored": len(scored),
            "n_unscored": len(by_gene) - len(scored_names & set(by_gene))}


def build(d: dict, n_labels: int = 4):
    fig, (ax, axl) = plt.subplots(
        2, 1, figsize=(11.4, 5.4), sharex=True,
        gridspec_kw={"height_ratios": [3.1, 1.0], "hspace": 0.10})

    ch, off, total, contigs = d["ch"], d["off"], d["total"], d["contigs"]
    scored = d["scored"]
    ymax = max(s["score"] for s in scored)

    # alternating neutral chromosome bands, in both panels
    for i, c in enumerate(ch):
        if i % 2 == 0:
            a, b = off[c], off[c] + contigs[c] // BIN
            ax.axvspan(a, b, color="#F2F4F5", lw=0, zorder=0)
            axl.axvspan(a, b, color="#F2F4F5", lw=0, zorder=0)

    # -- baseline rug: the FULL universe these 151 were drawn from ------------
    rug_y = -ymax * 0.085
    ax.scatter(d["universe_x"], np.full(len(d["universe_x"]), rug_y), marker="|",
               s=26, linewidths=0.35, color="#9AA4AC", zorder=2)
    ax.axhline(0, color=S.HAIRLINE, lw=0.7, zorder=1)
    ax.text(total * 0.012, rug_y + ymax * 0.028,
            f"rug: all {S.thousands(d['n_universe'])} genes carrying a HIGH or MODERATE "
            f"consequence allele, the universe the scored subset was drawn from",
            fontsize=S.BASE - 1.2, color=S.MUTED, va="bottom")

    # -- scored genes ---------------------------------------------------------
    xs = [s["x"] for s in scored]
    ys = [s["score"] for s in scored]
    ax.scatter(xs, ys, s=22, marker="o", facecolors="none",
               edgecolors=[S.MUTED if ch.index(s["chrom"]) % 2 else S.BLUE for s in scored],
               linewidths=0.9, zorder=4,
               label=f"{d['n_scored']} genes scored under an inheritance model")

    top = sorted(scored, key=lambda s: s["rank"])[:n_labels]
    hi = next((s for s in scored if s["gene"] == HIGHLIGHT), None)
    for s in top:
        if hi and s["gene"] == HIGHLIGHT:
            continue
        ax.annotate(s["gene"], (s["x"], s["score"]), xytext=(0, 7),
                    textcoords="offset points", ha="center",
                    fontsize=S.BASE - 1.0, color=S.MUTED)
    if hi:
        ax.scatter([hi["x"]], [hi["score"]], s=64, marker="D", color=S.VERM,
                   edgecolors="white", linewidths=0.8, zorder=6,
                   label=f"{HIGHLIGHT}, rank #{hi['rank']} in frozen A0")
        ax.axhline(hi["score"], color=S.VERM, lw=0.8, ls=":", zorder=3)
        n_at_or_above = sum(1 for s in scored if s["score"] >= hi["score"])
        ax.annotate(f"{HIGHLIGHT} · chr{hi['chrom']} · rank #{hi['rank']} of {d['n_scored']}"
                    f"\n{n_at_or_above} scored genes at or above this score",
                    xy=(hi["x"], hi["score"]), xycoords="data",
                    xytext=(0.28, 0.78), textcoords="axes fraction",
                    ha="left", va="center", fontsize=S.BASE - 0.5, color=S.VERM,
                    arrowprops=dict(arrowstyle="-|>", color=S.VERM, lw=1.0,
                                    shrinkA=2, shrinkB=4))

    ax.set_ylim(rug_y - ymax * 0.20, ymax * 1.18)
    ax.set_ylabel("A0 genetics-only prioritization score")
    S.panel(ax, "A")
    S.head(ax, "Gene prioritization score across the genome, no panel applied")
    ax.grid(True, axis="y", color=S.HAIRLINE, lw=0.45, zorder=1)
    ax.set_axisbelow(False)
    ax.legend(loc="upper left", ncol=2, fontsize=S.BASE - 1.0,
              bbox_to_anchor=(0.0, 1.005))

    # -- B -- density of the universe along the genome ------------------------
    ks = sorted(d["load"])
    axl.bar(ks, [d["load"][k] for k in ks], width=1.0, color="#6E7A83", lw=0, zorder=3)
    axl.set_xlim(0, total)
    axl.set_ylabel("genes per Mb")
    axl.set_xlabel("chromosome  (position binned to 1 Mb; no patient variant coordinate is used)")
    axl.set_xticks([off[c] + contigs[c] // BIN // 2 for c in ch])
    axl.set_xticklabels([c.replace("chr", "") for c in ch], fontsize=S.BASE - 1.2)
    axl.grid(True, axis="y", color=S.HAIRLINE, lw=0.45, zorder=1)
    axl.set_axisbelow(True)
    S.panel(axl, "B")
    S.head(axl, f"Density of the {S.thousands(d['n_universe'])}-gene HIGH/MODERATE universe",
           size=S.BASE)

    fig.tight_layout(rect=(0, 0.058, 1, 1))
    S.note(fig, "Score axis is a weighted sum of preregistered terms: NOT a p-value, no null "
                "distribution, and no significance threshold is drawn.\n"
                "A0 shown FROZEN as preregistered; the later A0-FREQFIX sensitivity ranks "
                f"{HIGHLIGHT} #1. Both numbers are always reported together.", y=0.008)
    return fig


def load_and_build():
    import collections as _c, io, pickle
    from src.paths import patient_vcf
    from src.prioritization.genome_wide import load
    rows = load("work/gw/highmod_ann.tsv", patient_vcf())
    by_gene = _c.defaultdict(list)
    for v in rows:
        if v.impact in ("HIGH", "MODERATE"):
            by_gene[v.gene].append(v)
    res = pickle.load(io.open("work/gw/mode_b_results_v4.pkl", "rb"))
    d = prepare(by_gene, res["A0_GENETICS"], contig_lengths(patient_vcf()))
    return build(d), d


if __name__ == "__main__":
    fig, d = load_and_build()
    print(S.export(fig, "fig01_prioritization_genomewide", "DATA", "MEASURED+DERIVED"))
