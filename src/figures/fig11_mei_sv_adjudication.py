#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 7 of the final set (slug fig11_mei_sv_adjudication_map).
The alternative structural signals near BUB1B, where they map, what each caller emitted, and the
gene context of every breakpoint, with the adjudicated ceiling for each.

Sources, all frozen
    work/callers/final/tier1_sv_manta_delly.json   Manta and DELLY records in the Tier 1 window (STOP of
                                                    2026-09-09, stages 2/3 under 47d24da), gene body, alleles
    work/callers/final/go2b_mei_read.json          xTea / SCRAMble records in the same window (ffb3c09)
    work/callers/final/ae1_gene_context.json       AE1 gene context from the frozen GENCODE v33 (5b66f58)
    The renderer places records at their emitted coordinates and prints the AE1 annotations verbatim.
    The only derived numbers are distances between frozen coordinates, used for labels.

Claim ceiling
    None of these loci overlaps the BUB1B gene body or the two prioritised positions. Every locus keeps
    the ceiling adjudicated in the science reports: "geometry consistent with ..." for BND clusters,
    "xTea annotates ... consistent with an L1-mediated transduction hypothesis" for 39.70 Mb, and for
    40.56 Mb "gene-associated breakpoint context but not a retrocopy or processed-pseudogene insertion
    architecture". Genotypes are caller-GT only. Nothing here is a diagnosis or an exclusion.
"""
from __future__ import annotations
import io, json, os, sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch

REPO = os.environ.get("MOSAIC_REPO", ".")
sys.path.insert(0, REPO)
from src.figures import style as S                                     # noqa: E402

from src.figures.frozen import load_frozen                             # noqa: E402

FINAL = os.path.join(REPO, "work/callers/final")
SRC_T1 = "tier1_sv_manta_delly.json"
SRC_MEI = "go2b_mei_read.json"
SRC_AE1 = "ae1_gene_context.json"


def box(ax, x, y, w, h, text, fc="white", ec=S.INK, lw=0.8, fs=None, weight="normal", color=None, width=46):
    import textwrap
    wrapped = "\n".join(textwrap.fill(par, width=width) for par in text.split("\n"))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012", fc=fc, ec=ec, lw=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, wrapped, ha="center", va="center", fontsize=fs or S.BASE - 1.2, color=color or S.INK,
            fontweight=weight, zorder=4, linespacing=1.2)


def arrow(ax, x0, y0, x1, y1, color=S.MUTED):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, color=color, lw=0.9, zorder=2,
                                 connectionstyle="arc3,rad=0.0"))


def ae1_rel(ae1, key):
    r = ae1["loci"][key]
    if r["overlapping_genes"]:
        parts = []
        for g in r["overlapping_genes"]:
            rels = sorted({t["relationship"] for t in g["transcripts"] if t["basic"]}) or sorted({t["relationship"] for t in g["transcripts"]})
            parts.append(f"{g['gene']} ({g['gene_type'].replace('_', ' ')}): " + "; ".join(rels))
        return "\n".join(parts)
    ig = r["intergenic"]
    return (f"intergenic · {ig['upstream_gene']['gene']} at {ig['upstream_gene']['distance_bp']:,} bp · "
            f"{ig['downstream_gene']['gene']} at {ig['downstream_gene']['distance_bp']:,} bp")


def build(t1: dict, mei: dict, ae1: dict, hashes: dict):
    def region(s):                      # "15:a-b" as frozen in the Tier 1 JSON
        a, b = s.split(":")[1].split("-"); return int(a), int(b)
    gb_lo, gb_hi = region(t1["gene_body"])
    alleles = [int(a["pos"]) if isinstance(a, dict) else int(a) for a in t1["alleles"]]
    win_lo, win_hi = region(t1["tier1"])
    manta = [r for r in t1["manta"]]
    delly_only_ins = [r for r in t1["delly"] if r.get("svtype") == "INS" and r.get("filter") == "PASS" and r.get("gt") not in (None, "0/0")]
    win = mei["5_targeted"]["tier1_window_pm1Mb"]
    xtea_l1 = win["xtea"]["L1"]; xtea_alu = win["xtea"]["Alu"]; scr = win["scramble"]

    fig = plt.figure(figsize=(11.6, 8.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.55], hspace=0.30)

    # ---------------- A · the window ----------------------------------------
    axA = fig.add_subplot(gs[0])
    Mb = 1e6
    axA.set_xlim(win_lo / Mb, win_hi / Mb); axA.set_ylim(-2.9, 6)
    axA.set_yticks([]); axA.set_xlabel("chr15 position (Mb, GRCh38, Tier 1 window ± 1 Mb around BUB1B)")
    for s in ("left", "right", "top"):
        axA.spines[s].set_visible(False)
    # gene body and alleles
    axA.add_patch(Rectangle((gb_lo / Mb, 4.55), (gb_hi - gb_lo) / Mb, 0.55, fc=S.GREEN, ec=S.INK, lw=0.6, zorder=3))
    axA.text((gb_lo + gb_hi) / 2 / Mb, 5.35, "BUB1B gene body (+)", ha="center", fontsize=S.BASE - 0.6, color=S.INK, fontweight="bold")
    for a in alleles:
        axA.plot([a / Mb, a / Mb], [4.45, 5.20], color=S.VERM, lw=1.2, zorder=5)
    axA.text(alleles[0] / Mb - 0.02, 4.20, "two prioritised alleles (caller-GT 0/1 each)", ha="right", va="center", fontsize=S.BASE - 1.4, color=S.VERM)
    axA.axhline(4.82, color=S.HAIRLINE, lw=0.8, zorder=1)
    # SV rows
    rows = {"Manta": 3.35, "DELLY": 2.55, "xTea": 1.75, "SCRAMble": 0.95}
    for name, y in rows.items():
        axA.text(win_lo / Mb - 0.01, y, name, ha="right", va="center", fontsize=S.BASE - 0.8, color=S.INK)
        axA.axhline(y, color=S.HAIRLINE, lw=0.6, zorder=1)
    mk = {"DEL": ("s", S.MUTED), "BND": ("^", S.PURPLE), "INS": ("D", S.ORANGE)}
    for r in manta:
        m, c = mk.get(r["svtype"], ("o", S.MUTED))
        x = (r["pos"] + (r["end"] or r["pos"])) / 2 / Mb
        axA.scatter([x], [rows["Manta"]], marker=m, s=34, color=c, edgecolor=S.INK, linewidth=0.5, zorder=4,
                    alpha=1.0 if r["filter"] == "PASS" else 0.45)
    for r in delly_only_ins:
        axA.scatter([r["pos"] / Mb], [rows["DELLY"]], marker="D", s=34, color=S.ORANGE, edgecolor=S.INK, linewidth=0.5, zorder=4)
    for r in t1["delly"]:
        if r.get("filter") == "PASS" and r.get("gt") not in (None, "0/0") and r.get("svtype") != "INS":
            m, c = mk.get(r["svtype"], ("o", S.MUTED))
            axA.scatter([r["pos"] / Mb], [rows["DELLY"]], marker=m, s=26, color=c, edgecolor=S.INK, linewidth=0.4, zorder=4, alpha=0.9)
    for r in xtea_l1:
        axA.scatter([r["pos"] / Mb], [rows["xTea"]], marker="o", s=40, color=S.BLUE, edgecolor=S.INK, linewidth=0.5, zorder=4)
    for r in xtea_alu:
        axA.scatter([r["pos"] / Mb], [rows["xTea"]], marker="o", s=40, color=S.SKY, edgecolor=S.INK, linewidth=0.5, zorder=4)
    for r in scr:
        axA.scatter([r["pos"] / Mb], [rows["SCRAMble"]], marker="o", s=40, color=S.SKY, edgecolor=S.INK, linewidth=0.5, zorder=4)
    # locus labels with AE1 context
    loci = [("MEI concordant ALU", [REDACTED], "Alu · xTea caller-GT 0/1 + SCRAMble\nAC109630.1 lncRNA intron"),
            ("BND group 39.70 Mb site (Tier 1 SV) / xTea L1 record", 39702428, "BND ×2 Manta+DELLY · xTea L1 caller-GT 0/1\nFSIP1 intron 10"),
            ("DELLY INS 40.11 Mb", [REDACTED], "INS DELLY-only caller-GT 1/1\nintergenic, BMF at 4.2 kb"),
            ("BND+INS group 40.56 Mb site (Tier 1 SV)", 40561984, "BND ×3 + INS Manta, BND DELLY\nCCDC32 intron 2")]
    for i, (key, pos, label) in enumerate(loci):
        d = (gb_lo - pos) if pos < gb_lo else (pos - gb_hi)
        side = "upstream" if pos < gb_lo else "downstream"
        ytop = -0.35 if i % 2 == 0 else -1.75           # two staggered label levels below the caller rows
        axA.plot([pos / Mb, pos / Mb], [ytop, 3.75], color=S.HAIRLINE, lw=0.8, ls=(0, (2, 2)), zorder=1)
        axA.text(pos / Mb, ytop, f"{label}\n{d / 1000:.0f} kb {side}", ha="center", va="top",
                 fontsize=S.BASE - 1.9, color=S.INK, zorder=6,
                 bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=S.HAIRLINE, lw=0.6))
    S.panel(axA, "A"); S.head(axA, "Alternative structural signals in the Tier 1 window: none overlaps the BUB1B gene body or the two alleles")
    legend_items = [plt.Line2D([], [], marker="s", ls="", color=S.MUTED, mec=S.INK, label="DEL"),
                    plt.Line2D([], [], marker="^", ls="", color=S.PURPLE, mec=S.INK, label="BND"),
                    plt.Line2D([], [], marker="D", ls="", color=S.ORANGE, mec=S.INK, label="INS (SV caller)"),
                    plt.Line2D([], [], marker="o", ls="", color=S.BLUE, mec=S.INK, label="MEI L1 (xTea)"),
                    plt.Line2D([], [], marker="o", ls="", color=S.SKY, mec=S.INK, label="MEI Alu (xTea / SCRAMble)")]
    axA.legend(handles=legend_items, loc="upper right", ncol=5, fontsize=S.BASE - 1.8, bbox_to_anchor=(1.0, 1.02), handletextpad=0.3, columnspacing=1.0)

    # ---------------- B · partner context of the two BND groups ---------------
    axB = fig.add_subplot(gs[1]); axB.set_xlim(0, 1); axB.set_ylim(0, 1); axB.axis("off")
    S.panel(axB, "B", dx=-0.02, dy=1.0); S.head(axB, "Where the breakpoint partners map (AE1, frozen GENCODE v33), and the adjudicated ceiling of each group")
    F = S.BASE - 2.0
    # left group: 39.70 Mb ------------------------------------------------------
    box(axB, 0.005, 0.55, 0.225, 0.41,
        "chr15 39.70 Mb\nBND ×2 (Manta + DELLY), caller-GT 0/1\nxTea L1 record at [REDACTED], caller-GT 0/1, subtype orphan_or_sibling_transduction\n"
        + ae1_rel(ae1, "BND group 39.70 Mb site (Tier 1 SV) / xTea L1 record"), fc="#EEF6F1", fs=F, width=40)
    box(axB, 0.265, 0.77, 0.225, 0.19, "chr12 56.596 Mb · xTea TD_SRC\n" + ae1_rel(ae1, "xTea TD_SRC (transduction source)"), fs=F, width=46)
    box(axB, 0.265, 0.55, 0.225, 0.19, "chr12 BND partners [REDACTED] and [REDACTED]\n"
        + ae1_rel(ae1, "BND partner chr12 #1").split("\n")[0] + "\n" + ae1_rel(ae1, "BND partner chr12 #2"), fs=F, width=46)
    arrow(axB, 0.23, 0.86, 0.265, 0.865); arrow(axB, 0.23, 0.66, 0.265, 0.645)
    box(axB, 0.005, 0.305, 0.485, 0.22,
        "Ceiling (frozen). Geometry consistent with insertion of non-local chr12-derived sequence with a poly-T tract; xTea annotates the locus "
        "as an L1-family orphan/sibling transduction, consistent with an L1-mediated transduction hypothesis. SCRAMble emitted no call here: its "
        "method needs clipped reads aligning to an element consensus. Mechanism NOT established. 459 kb upstream of BUB1B.",
        fc="#FFF7EE", ec=S.ORANGE, fs=F, width=100)
    # right group: 40.56 Mb -----------------------------------------------------
    box(axB, 0.515, 0.55, 0.215, 0.41,
        "chr15 40.56 Mb\nBND ×3 + INS (Manta), BND (DELLY)\ncaller-GT 0/1 (BND), 1/1 (INS)\nno xTea or SCRAMble call\n"
        + ae1_rel(ae1, "BND+INS group 40.56 Mb site (Tier 1 SV)"), fc="#EEF6F1", fs=F, width=38)
    p7 = "\n".join(f"{k}: {ae1_rel(ae1, key).split(': ', 1)[1]}" for k, key in (("26201745", "partner chr7 #1"), ("26206367", "partner chr7 #2"), ("26213351", "partner chr7 #3")))
    box(axB, 0.765, 0.775, 0.23, 0.185, "chr7 26.20 Mb · CBX3 (protein coding)\n" + p7, fs=F, width=56)
    box(axB, 0.765, 0.645, 0.23, 0.115, "chr6 116.45 Mb\n" + ae1_rel(ae1, "partner chr6"), fs=F, width=56)
    box(axB, 0.765, 0.545, 0.23, 0.09, "chr12 95.29 Mb\n" + ae1_rel(ae1, "partner chr12 (40.56 group)"), fs=F, width=48)
    arrow(axB, 0.73, 0.87, 0.765, 0.87); arrow(axB, 0.73, 0.72, 0.765, 0.70); arrow(axB, 0.73, 0.60, 0.765, 0.59)
    box(axB, 0.515, 0.305, 0.48, 0.22,
        "Ceiling (frozen). Breakpoints overlap exonic and intronic regions of CBX3; another partner overlaps an exon of CBX3P9, which GENCODE "
        "annotates as a processed pseudogene. This establishes gene-associated breakpoint context but does not establish a retrocopy or "
        "processed-pseudogene insertion architecture. 341 kb downstream of BUB1B.",
        fc="#FFF7EE", ec=S.ORANGE, fs=F, width=100)
    # bottom strip: the two remaining loci ------------------------------------
    box(axB, 0.005, 0.04, 0.485, 0.24,
        "DELLY INS 15:[REDACTED] (caller-GT 1/1, DELLY only). " + ae1_rel(ae1, "DELLY INS 40.11 Mb") + ". No xTea, SCRAMble or CNVpytor record "
        "overlaps it. 48 kb upstream of BUB1B, outside the gene body; regulatory relevance not adjudicated.", fs=F, width=100)
    box(axB, 0.515, 0.04, 0.48, 0.24,
        "Alu 15:[REDACTED], concordant between xTea (caller-GT 0/1) and SCRAMble under the post-STOP ±50 bp rule. " + ae1_rel(ae1, "MEI concordant ALU")
        + ". 677 kb upstream of BUB1B. Population status: AE2 NOT EXECUTED (data policy); absence in gnomAD would not have meant rarity.", fs=F, width=100)

    S.note(fig,
           f"Sources under work/callers/final/: tier1_sv_manta_delly.json (sha256 {hashes['t1'][:10]}…, Manta and DELLY, 47d24da) · "
           f"go2b_mei_read.json (sha256 {hashes['mei'][:10]}…, xTea and SCRAMble, ffb3c09)\n"
           f"· ae1_gene_context.json (sha256 {hashes['ae1'][:10]}…, GENCODE v33 frozen, 5b66f58). Records drawn at their emitted coordinates; "
           f"gene context printed verbatim from AE1;\n"
           f"distances are differences of frozen coordinates; genotypes are caller-GT, never biological zygosity.\n"
           f"CLAIM CEILING. None of these loci overlaps the BUB1B gene body (15:{gb_lo}-{gb_hi}) or the two prioritised positions. "
           f"No retrocopy or processed-pseudogene insertion is established;\nno locus is a diagnosis and none is excluded (GO 2B SCIENCE FINAL).",
           y=0.004)
    return fig


def load_and_build():
    t1, h1 = load_frozen(SRC_T1, FINAL)              # FAIL CLOSED: hash verificado antes de dibujar
    mei, h2 = load_frozen(SRC_MEI, FINAL)
    ae1, h3 = load_frozen(SRC_AE1, FINAL)
    hashes = {"t1": h1, "mei": h2, "ae1": h3}
    return build(t1, mei, ae1, hashes), hashes


if __name__ == "__main__":
    S.use()
    fig, h = load_and_build()
    print(S.export(fig, "fig11_mei_sv_adjudication_map", "DATA", "MEASURED+EXTERNAL+DERIVED"))
    print(h)
