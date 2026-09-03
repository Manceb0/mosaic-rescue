#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 3. BUB1B gene browser: transcript, domains and ClinVar landscape.

READING ORDER, TOP TO BOTTOM
    transcript model -> annotated protein domains -> ClinVar variation.
    Each track is drawn on the same protein-coordinate axis so a reader can move
    a finger down the figure and stay at the same residue.

PROVENANCE
    Exon structure and InterPro/Pfam domains come from Ensembl REST; the request
    carries only the gene symbol. The variation track is every missense record
    ClinVar holds for this gene, one per record, not a summary.

SANITISATION
    The two case alleles appear as unlabelled markers on the axis. Their residue
    numbers are never written, in this figure or in its SVG text.
"""
from __future__ import annotations
import collections, sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

CLASS_COL = {"P/LP": S.VERM, "B/LB": S.BLUE, "VUS": "#B9C0C6"}
CLASS_MARK = {"P/LP": "D", "B/LB": "s", "VUS": "o"}
BIN_AA = 25


def build(tx: dict, clinvar: dict, marks: dict):
    """tx: transcript_model.fetch(); clinvar: landscape_missense.json;
    marks: {'ptc_aa': int, 'mis_aa': int}, used only to place markers."""
    L = tx["translation"]["length"]
    exons = [e for e in tx["exons"] if e.get("aa")]
    domains = [d for d in tx["domains"] if d["type"] in ("Pfam", "Gene3D")]

    per = collections.defaultdict(collections.Counter)
    for v in clinvar["variants"]:
        per[v["pos"]][v["cls"]] += 1
    totals = clinvar["totals"]
    n_rec = len(clinvar["variants"])

    fig, (axT, axD, axC, axH) = plt.subplots(
        4, 1, figsize=(11.0, 6.4), sharex=True,
        gridspec_kw={"height_ratios": [0.75, 0.55, 2.5, 0.95], "hspace": 0.16})

    # -- A -- transcript model ------------------------------------------------
    axT.set_ylim(0, 1); axT.set_yticks([])
    for sp in ("left", "bottom"):
        axT.spines[sp].set_visible(False)
    axT.hlines(0.5, 0, L, color=S.MUTED, lw=0.8, zorder=1)
    for i, e in enumerate(exons):
        a, b = e["aa"]
        axT.add_patch(plt.Rectangle((a, 0.24), max(b - a, 1.2), 0.52, zorder=3,
                                    facecolor=("#5B6670" if i % 2 == 0 else "#AEB6BC"),
                                    edgecolor="white", linewidth=0.6))
        if i % 4 == 0 or i == len(exons) - 1:
            axT.text((a + b) / 2, 0.86, str(i + 1), ha="center", va="bottom",
                     fontsize=S.BASE - 1.6, color=S.MUTED)
    S.panel(axT, "A")
    S.head(axT, f"{tx['transcript']} ({tx['transcript_pick']}), {tx['n_exons']} exons "
                f"projected onto the {L} aa protein · Ensembl release {tx['release']}")

    # -- B -- protein domains -------------------------------------------------
    axD.set_ylim(0, 1); axD.set_yticks([])
    for sp in ("left", "bottom"):
        axD.spines[sp].set_visible(False)
    dcol = [S.GREEN, S.PURPLE, S.SKY, S.ORANGE]
    # Domains overlap along the sequence, so their labels are staggered in Y.
    # Two of them nest (Gene3D 46-203 contains Pfam 57-179) and their captions
    # collided when written at the same height.
    for k, dm in enumerate(domains):
        w = dm["end"] - dm["start"]
        y0 = 0.34 - 0.09 * (k % 2)
        axD.add_patch(plt.Rectangle((dm["start"], y0), w, 0.30, zorder=3 + k,
                                    facecolor=dcol[k % len(dcol)], alpha=0.85,
                                    edgecolor="white", linewidth=0.5))
        lab_y = 1.55 - 0.42 * (k % 2)
        ha = "left" if dm["start"] < L * 0.5 else "right"
        lx = dm["start"] if ha == "left" else dm["end"]
        axD.annotate(f"{dm['desc']}  ({dm['type']} {dm['start']}–{dm['end']})",
                     xy=((dm["start"] + dm["end"]) / 2, y0 + 0.30),
                     xytext=(lx, lab_y), ha=ha, va="bottom",
                     fontsize=S.BASE - 1.4, color=S.INK,
                     arrowprops=dict(arrowstyle="-", color=S.HAIRLINE, lw=0.7))
    axD.set_ylim(0, 2.15)
    S.panel(axD, "B")
    S.head(axD, "InterPro / Pfam domains on the translation", size=S.BASE - 0.5)

    # -- C -- ClinVar records, one per record ---------------------------------
    for k, dm in enumerate(domains):                 # domains carried down
        axC.axvspan(dm["start"], dm["end"], color=dcol[k % len(dcol)], alpha=0.06,
                    lw=0, zorder=0)
    zo = {"VUS": 2, "B/LB": 4, "P/LP": 6}
    for pos in sorted(per):
        base = 0
        for cls in ("VUS", "B/LB", "P/LP"):
            n = per[pos][cls]
            if not n:
                continue
            axC.vlines(pos, base, base + n, color=CLASS_COL[cls],
                       lw=0.8 if cls == "VUS" else 1.2, zorder=zo[cls])
            axC.plot([pos], [base + n], marker=CLASS_MARK[cls],
                     ms=2.0 if cls == "VUS" else 4.2, color=CLASS_COL[cls],
                     markeredgecolor="white" if cls != "VUS" else "none",
                     markeredgewidth=0.4, zorder=zo[cls] + 1)
            base += n
    hi = max(sum(c.values()) for c in per.values())
    axC.set_ylim(0, hi + 3.0)
    axC.set_ylabel("ClinVar records at residue")
    S.panel(axC, "C")
    S.head(axC, f"ClinVar missense records: all {S.thousands(n_rec)}, "
                f"one mark per record, at {S.thousands(len(per))} distinct residues")
    S.grid(axC)
    axC.legend(handles=[Line2D([], [], color=CLASS_COL[k], marker=CLASS_MARK[k],
                               lw=1.4, ms=4.2,
                               label=f"{k}  n = {S.thousands(totals.get(k, 0))}")
                        for k in ("P/LP", "B/LB", "VUS")],
               loc="upper left", ncol=3, fontsize=S.BASE - 1.0,
               bbox_to_anchor=(0.0, 1.0))

    # Case alleles: a full-height guide through the variation tracks, labelled
    # by ROLE only. The residue number is never written. Drawn as a line rather
    # than a below-axis arrow because the arrow spilled into the next panel.
    for aa, lab, dash in ((marks["ptc_aa"], "truncating allele (PTC)", (0, (4, 2))),
                          (marks["mis_aa"], "missense allele (candidate)", (0, (1, 1.6)))):
        for a in (axC, axH):
            a.axvline(aa, color=S.INK, lw=1.0, ls=dash, zorder=9)
        axC.text(aa, hi + 1.45, lab, ha="center", va="top", rotation=0,
                 fontsize=S.BASE - 1.0, color=S.INK,
                 bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.9))

    # -- D -- density, so 1 497 records read as a distribution ----------------
    edges = np.arange(0, L + BIN_AA, BIN_AA)
    counts = np.zeros(len(edges) - 1)
    for pos, c in per.items():
        j = min(int(pos // BIN_AA), len(counts) - 1)
        counts[j] += sum(c.values())
    axH.bar(edges[:-1], counts, width=BIN_AA, align="edge", color="#7C868E",
            edgecolor="white", linewidth=0.3, zorder=3)
    axH.set_xlim(0, L)
    axH.set_ylabel(f"records per {BIN_AA} aa")
    axH.set_xlabel("position in protein (aa)")
    S.panel(axH, "D")
    S.grid(axH)

    # NOTA: aqui habia un fig.tight_layout(rect=...) que no hacia nada. El
    # gridspec lleva hspace/wspace explicitos, lo que lo marca como
    # 'localmente modificado'; tight_layout entonces descarta esos ejes,
    # avisa de que 'el resultado puede ser incorrecto' y sale sin tocar ni
    # las posiciones ni el rect. Comprobado midiendo gridspec y
    # get_position() antes y despues: identicos. El hueco inferior para la
    # tira de procedencia lo da el bottom por defecto, no el rect.
    S.note(fig, f"Exons and domains: Ensembl REST release {tx['release']}, request carries the "
                f"gene symbol only.  ·  Variation: ClinVar, {S.thousands(n_rec)} missense "
                f"records ({100 * totals['VUS'] / sum(totals.values()):.0f} % VUS, "
                f"{totals.get('P/LP', 0)} P/LP in the whole gene).\n"
                "Case alleles are marked by position and are deliberately unlabelled; their "
                "residue numbers appear nowhere in this figure or its SVG text.")
    return fig


def load_and_build():
    import io, json
    from src.structure.transcript_model import fetch
    tx = fetch()
    cv = json.load(io.open("work/clinvar/landscape_missense.json", encoding="utf-8"))
    g = json.load(io.open("work/struct/fig3_exons.json", encoding="utf-8"))
    marks = {"ptc_aa": g["ptc_cds"] // 3 + 1, "mis_aa": g["mis_cds"] // 3 + 1}
    return build(tx, cv, marks), {"tx": tx, "cv": cv}


if __name__ == "__main__":
    fig, d = load_and_build()
    print(S.export(fig, "fig02_gene_browser", "DATA", "EXTERNAL+MEASURED"))
