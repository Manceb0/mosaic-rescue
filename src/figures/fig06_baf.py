#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 7. BAF cancellation in variegated aneuploidy, and what it costs.

Why the distributions and not the summary
    A mean cannot show a cancellation. The summary statistic of a variegated
    genome looks like that of a euploid one, and that resemblance IS the failure
    mode. So panels A–C plot the site-level BAF distribution, on one shared and
    identical scale, at the SAME cell fraction.

The baseline is named for what it is
    Panel D compares the coverage-dispersion index against a SITE-WISE UNPHASED
    BAF statistic. That is not MoChA. MoChA draws its power from long-range
    phased BAF, which this comparator does not reproduce, so no superiority over
    the standard method is claimed here, and the comparator is named inside
    the panel so they survive a crop.

No patient data
    Nothing in this figure comes from the case. It is a simulation with a fixed,
    preregistered seed.
"""
from __future__ import annotations
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

SCEN = [("Euploid", "null", S.MUTED),
        ("Clonal (same homolog in every cell)", "clonal", S.BLUE),
        ("Variegated (random homolog per lineage)", "variegated", S.PURPLE)]
BINS = np.linspace(0.15, 0.85, 71)


def build(sim: dict, bafs: dict, fraction: float, n_chrom_affected: int = 3):
    fig = plt.figure(figsize=(11.6, 7.3))
    # bottom leaves room for the five-line provenance strip; it used to overflow the canvas.
    gs = fig.add_gridspec(2, 3, height_ratios=[1.20, 1.0], hspace=0.46, wspace=0.16,
                          bottom=0.17)

    dens = {k: np.histogram(bafs[k], bins=BINS, density=True)[0] for k, _m, _c in SCEN}
    hi = max(d.max() for d in dens.values())

    for j, (label, mode, col) in enumerate(SCEN):
        ax = fig.add_subplot(gs[0, j])
        v = np.asarray(bafs[label])
        ax.hist(v, bins=BINS, density=True, color=col, alpha=0.80, lw=0, zorder=3)
        ax.axvline(0.5, color=S.INK, lw=1.1, ls=(0, (3, 2)), zorder=5)
        ax.set_xlim(0.15, 0.85)
        ax.set_ylim(0, hi * 1.30)                    # identical across the three
        ax.set_xlabel("BAF (B-allele fraction)")
        if j == 0:
            ax.set_ylabel("density of heterozygous sites")
        else:
            ax.set_yticklabels([])
        S.panel(ax, "ABC"[j])
        S.head(ax, label, size=S.BASE)
        S.grid(ax)
        md = float(np.abs(v - 0.5).mean())
        ax.text(0.5, hi * 1.20, f"mean |BAF − 0.5| = {md:.4f}", ha="center",
                fontsize=S.BASE - 0.5, color=S.INK, fontweight="bold")
        if mode == "clonal":
            p = (1 + fraction) / (2 + fraction)
            for xx in (p, 1 - p):
                ax.axvline(xx, color=S.VERM, lw=1.0, ls=(0, (1.4, 1.4)), zorder=6)
            ax.annotate("expected clonal shift\nat this cell fraction",
                        xy=(p, hi * 0.55), xytext=(0.70, hi * 0.92), ha="center",
                        fontsize=S.BASE - 1.2, color=S.VERM,
                        arrowprops=dict(arrowstyle="-|>", color=S.VERM, lw=0.9))
        if mode == "variegated":
            ax.annotate("re-centres on 0.5 with the same\naneuploidy present",
                        xy=(0.5, hi * 0.72), xytext=(0.5, hi * 0.98), ha="center",
                        fontsize=S.BASE - 1.0, color=S.VERM, fontweight="bold",
                        arrowprops=dict(arrowstyle="-|>", color=S.VERM, lw=1.0))
        if mode == "null":
            ax.annotate("BAF = 0.5", xy=(0.5, hi * 0.35), xytext=(0.255, hi * 0.62),
                        fontsize=S.BASE - 1.2, color=S.INK,
                        arrowprops=dict(arrowstyle="-|>", color=S.INK, lw=0.8))

    # ---------------- D · power ---------------------------------------------
    axD = fig.add_subplot(gs[1, :])
    style = {"clonal": ("-", "o"), "variegated": ("--", "s")}
    for mode in ("clonal", "variegated"):
        rs = [r for r in sim["results"] if r["mode"] == mode]
        xs = [r["fraction"] * 100 for r in rs]
        ls, mk = style[mode]
        axD.plot(xs, [r["power_baf"] for r in rs], ls=ls, marker=mk, ms=4.6,
                 color=S.VERM, lw=1.3,
                 label=f"site-wise unphased BAF statistic · {mode}")
        axD.plot(xs, [r["power_dispersion"] for r in rs], ls=ls, marker=mk, ms=4.6,
                 color=S.GREEN, lw=1.3,
                 label=f"coverage-dispersion index · {mode}")
    axD.axvline(fraction * 100, color=S.INK, lw=0.9, ls=":", zorder=2)
    axD.annotate("cell fraction of panels A–C", xy=(fraction * 100, 0.50),
                 xytext=(fraction * 100 - 2.2, 0.50), ha="right", va="center",
                 fontsize=S.BASE - 1.2, color=S.MUTED,
                 arrowprops=dict(arrowstyle="-|>", color=S.MUTED, lw=0.8))
    axD.set_xlabel("cell fraction carrying the event (%)")
    axD.set_ylabel(f"power at fixed FPR = {sim['alpha']}")
    axD.set_ylim(-0.05, 1.08)
    S.panel(axD, "D")
    S.head(axD, "Detection power against cell fraction, at a fixed false-positive rate",
           size=S.BASE + 0.5)
    S.grid(axD)
    # La leyenda va ENCIMA del titulo del panel, no sobre el. Antes se anclaba a
    # 1.02, que es justo donde S.head escribe el encabezado, y los dos textos se
    # pisaban.
    axD.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.115),
               fontsize=S.BASE - 1.0, columnspacing=2.4)
    axD.text(0.015, 0.93, "Baseline is a site-wise unphased BAF statistic,\nnot MoChA: no long-range phasing",
             transform=axD.transAxes, ha="left", va="top",
             fontsize=S.BASE - 0.5, color=S.VERM, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.32", fc="white", ec=S.VERM, lw=0.9))

    pv = [r["power_baf"] for r in sim["results"] if r["mode"] == "variegated"]
    n_sites = len(bafs[SCEN[0][0]])
    # NOTA: aqui habia un fig.tight_layout(rect=...) que no hacia nada. El
    # gridspec lleva hspace/wspace explicitos, lo que lo marca como
    # 'localmente modificado'; tight_layout entonces descarta esos ejes,
    # avisa de que 'el resultado puede ser incorrecto' y sale sin tocar ni
    # las posiciones ni el rect. Comprobado midiendo gridspec y
    # get_position() antes y despues: identicos. El hueco inferior para la
    # tira de procedencia lo da el bottom por defecto, no el rect.
    S.note(fig,
           f"Simulation, no patient data. Seed {sim['seed']} (preregistered)  ·  "
           f"{sim['n_rep']} replicates per cell  ·  depth {sim['depth']}×  ·  "
           f"{sim['n_sites']} heterozygous sites per chromosome  ·  "
           f"{n_chrom_affected} affected chromosomes  ·  panels A–C at "
           f"{fraction * 100:.0f} % cell fraction, {S.thousands(n_sites)} sites each.\n"
           f"Variegated power of this site-wise ABSOLUTE statistic falls from {pv[0]:.3f} to "
           f"{pv[-1]:.3f}. The project first attributed that to lineage cancellation and its own "
           "audit falsified it: an absolute statistic is blind to sign.\n"
           "The 2x2 ablation (EXP-015c, POST-HOC, designed after the audit and not "
           "preregistered) shows the fall is driven by copy-number-dependent depth. What "
           "cancellation does move is the SIGNED statistic, 0.980 to 0.050.\n"
           "No superiority over the standard method is claimed: the comparator is unphased and "
           "MoChA is not reproduced here.\n"
           "Simulated power is optimistic: no GC bias, no mappability, no reference-allele "
           "bias, which at this depth are the real limiting factors.", y=0.005)
    return fig


def load_and_build():
    import io, json
    from src.mosaic.simulate_dispersion import site_bafs, SEED
    sim = json.load(io.open("work/mosaic/dispersion_simulation.json", encoding="utf-8"))
    F = 0.20
    bafs = {label: site_bafs(SEED + i, 0.0 if mode == "null" else F, mode)
            for i, (label, mode, _c) in enumerate(SCEN)}
    return build(sim, bafs, F), {"sim": sim, "bafs": bafs, "fraction": F}


if __name__ == "__main__":
    fig, d = load_and_build()
    print(S.export(fig, "fig06_baf_cancellation", "SIMULATION", "SIMULATED"))
