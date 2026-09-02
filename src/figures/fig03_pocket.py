#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 4. Local geometry and evolutionary constraint at the candidate residue.

WHAT THE READER SHOULD GET IN ONE LOOK
    local geometry (A, B)  +  model confidence (C)  +  evolutionary constraint (D)
    and the uncertainty attached to each of them.

Five things that must stay distinguishable, and do
    candidate side chain · neighbours within 5 A · heavy-atom minimum distance ·
    CANDIDATE H-bond geometry · AlphaFold pLDDT.

    A candidate H-bond is not a demonstrated interaction. The model carries no
    hydrogens, so the donor-H-acceptor angle cannot be checked: what is drawn is
    a donor/acceptor pair within 3.5 A. The word CANDIDATE is in the panel, the
    legend and the provenance strip, not only in the caption.

COORDINATES
    Everything is relative to the candidate residue. Absolute residue numbers
    appear nowhere in the figure or in its SVG text.
"""
from __future__ import annotations
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402
from src.structure import pocket_geometry as pg                        # noqa: E402

WIN_PLDDT = 45
WIN_LOGO = 12
CAND_COL = S.VERM
SEQ_COL = S.BLUE          # neighbour contiguous in sequence
TERT_COL = S.PURPLE       # tertiary contact
CONTEXT = "#DCE0E3"


def _rel(n, tgt):
    d = n - tgt
    return f"{d:+d}" if d else "0"


def build(geom: dict, logo: dict):
    tgt = geom["target"]
    res, NB, HB = geom["res"], geom["neighbours"], geom["hbonds"]
    sc_hb = [h for h in HB if h["from"] not in pg.BACKBONE]

    fig = plt.figure(figsize=(13.4, 8.0))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.52, 1.0], height_ratios=[1.20, 1.0],
                          wspace=0.24, hspace=0.46)
    ax3 = fig.add_subplot(gs[0, 0], projection="3d")
    axB = fig.add_subplot(gs[0, 1])
    axD = fig.add_subplot(gs[1, 0])   # logo, panel C in reading order
    axC = fig.add_subplot(gs[1, 1])   # pLDDT, panel D in reading order

    # ---------------- A · pocket geometry from the model coordinates --------
    show = [tgt] + [n["resnum"] for n in NB]
    cen = np.mean([res[r]["atoms"]["CA"] for r in show], axis=0)
    lo, hi = min(show), max(show)
    trace = [res[n]["atoms"]["CA"] for n in range(lo - 6, hi + 7)
             if n in res and "CA" in res[n]["atoms"]]
    ax3.plot(*zip(*trace), color=CONTEXT, lw=3.0, solid_capstyle="round", zorder=1)

    def covalent(atoms):
        ks = list(atoms)
        return [(atoms[a], atoms[b]) for i, a in enumerate(ks) for b in ks[i + 1:]
                if pg._d(atoms[a], atoms[b]) < 1.8]

    for r in show:
        is_t = r == tgt
        col = CAND_COL if is_t else (SEQ_COL if abs(r - tgt) <= 4 else TERT_COL)
        at = res[r]["atoms"]
        side = {k: v for k, v in at.items() if k not in pg.BACKBONE} or at
        for a, b in covalent(at):
            ax3.plot(*zip(a, b), color=col, lw=4.6 if is_t else 2.4,
                     alpha=1.0 if is_t else 0.85, solid_capstyle="round",
                     zorder=6 if is_t else 4)
        pts = np.asarray(list(side.values()))
        ax3.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=64 if is_t else 26, color=col,
                    depthshade=False, edgecolors="white", linewidths=0.6,
                    zorder=7 if is_t else 5)
        c = pts.mean(0)
        v = c - cen
        q = c + v / (np.linalg.norm(v) or 1.0) * 4.6
        if is_t:
            q = c + np.array([0.0, 0.0, 4.6])
            ax3.plot(*zip(c, q), color=col, lw=0.9, ls=":", zorder=6)
        ax3.text(q[0], q[1], q[2], f"{res[r]['aa']} (candidate)" if is_t
                 else f"{res[r]['aa']}{_rel(r, tgt)}",
                 fontsize=S.BASE + 1.4 if is_t else S.BASE - 0.2,
                 fontweight="bold" if is_t else "normal", color=col,
                 ha="center", va="center", zorder=9)

    # Las tres distancias caian en el mismo punto de la proyeccion y se
    # solapaban. Se escalonan en Z por indice.
    for k, h in enumerate(sc_hb):
        a = res[tgt]["atoms"][h["from"]]
        b = res[h["to_res"]]["atoms"][h["to_atom"]]
        ax3.plot(*zip(a, b), color=S.INK, lw=1.5, ls=(0, (2.2, 1.8)), zorder=8)
        m = [(a[i] + b[i]) / 2 for i in range(3)]
        off = np.array([2.2 * (k - 1), -0.6 * k, -1.4 - 1.5 * k])
        ax3.plot(*zip(m, np.asarray(m) + off), color=S.INK, lw=0.6, ls=":", zorder=8)
        q = np.asarray(m) + off
        ax3.text(q[0], q[1], q[2], f"{h['dist']:.2f} Å", fontsize=S.BASE - 1.0,
                 color=S.INK, ha="center", fontweight="bold", zorder=9)

    ax3.set_axis_off()
    ax3.view_init(elev=16, azim=-58)
    # Un Axes3D reserva margenes muy generosos y la molecula quedaba pequena
    # dentro de su celda. Se recoloca a mano sobre la celda del gridspec.
    _b = ax3.get_position()
    ax3.set_position([_b.x0 - _b.width * 0.10, _b.y0 - _b.height * 0.06,
                      _b.width * 1.20, _b.height * 1.16])
    for setter, i in ((ax3.set_xlim, 0), (ax3.set_ylim, 1), (ax3.set_zlim, 2)):
        setter(cen[i] - 7.6, cen[i] + 7.6)
    ax3.text2D(-0.02, 1.045, "A", transform=ax3.transAxes, fontsize=10.5,
               fontweight="bold", color=S.INK)
    ax3.text2D(0.045, 1.045, "Pocket geometry in AlphaFold model AF-O60566-F1",
               transform=ax3.transAxes, fontsize=S.BASE + 0.5, color=S.INK)
    ax3.legend(handles=[
        Line2D([], [], color=CAND_COL, lw=3.4, label="candidate side chain"),
        Line2D([], [], color=SEQ_COL, lw=2.2, label="neighbour ≤5 A, sequence-local (|Δ| ≤ 4)"),
        Line2D([], [], color=TERT_COL, lw=2.2, label="neighbour ≤5 A, tertiary contact"),
        Line2D([], [], color=S.INK, lw=1.5, ls=(0, (2.2, 1.8)),
               label="candidate H-bond (distance only, no angle)"),
        Line2D([], [], color=CONTEXT, lw=3.0, label="backbone trace"),
    ], loc="upper center", bbox_to_anchor=(0.5, 0.03), fontsize=S.BASE - 1.0, ncol=2)

    # ---------------- B · the measured distances ----------------------------
    order = sorted(NB, key=lambda n: n["dmin"], reverse=True)
    ypos = np.arange(len(order))
    axB.barh(ypos, [n["dmin"] for n in order], height=0.62, zorder=3,
             color=[SEQ_COL if n["contiguo"] else TERT_COL for n in order],
             edgecolor="white", linewidth=0.5)
    axB.set_yticks(ypos)
    axB.set_yticklabels([f"{n['aa']}{_rel(n['resnum'], tgt)}" for n in order],
                        fontsize=S.BASE - 0.5)
    axB.axvline(pg.HB_MAX, color=S.INK, lw=1.0, ls=(0, (2.2, 1.8)), zorder=5)
    axB.text(pg.HB_MAX - 0.10, len(order) - 0.35, f"{pg.HB_MAX} Å H-bond cut-off",
             fontsize=S.BASE - 1.2, color=S.INK, ha="right", va="top")
    for i, n in enumerate(order):
        axB.text(n["dmin"] + 0.07, i, f"{n['dmin']:.2f}", va="center",
                 fontsize=S.BASE - 1.0, color=S.MUTED)
    axB.set_xlim(0, pg.CONTACT + 1.1)
    axB.set_xlabel("minimum heavy-atom distance to candidate side chain (Å)")
    S.panel(axB, "B")
    S.head(axB, f"{len(NB)} residues within {pg.CONTACT:.0f} Å")
    S.grid(axB, axis="x")
    axB.legend(handles=[Patch(color=SEQ_COL, label="sequence-local"),
                        Patch(color=TERT_COL, label="tertiary contact")],
               loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
               fontsize=S.BASE - 1.0)

    # ---------------- C · model confidence ----------------------------------
    xs, ys = pg.plddt_track(res, tgt - WIN_PLDDT, tgt + WIN_PLDDT)
    xr = [x - tgt for x in xs]
    axC.axhspan(90, 100, color="#EAF3EF", lw=0, zorder=0)
    axC.axhspan(70, 90, color="#F6F1E7", lw=0, zorder=0)
    axC.axhspan(0, 70, color="#F8ECE9", lw=0, zorder=0)
    axC.plot(xr, ys, color=S.INK, lw=1.2, zorder=4)
    axC.scatter([n["resnum"] - tgt for n in NB], [n["plddt"] for n in NB],
                s=20, marker="o", facecolors="none", edgecolors=TERT_COL,
                linewidths=0.9, zorder=5, label="pocket neighbours")
    axC.scatter([0], [geom["plddt"]], s=70, marker="D", color=CAND_COL,
                edgecolors="white", linewidths=0.8, zorder=6,
                label=f"candidate, pLDDT {geom['plddt']:.1f}")
    axC.set_xlim(-WIN_PLDDT, WIN_PLDDT); axC.set_ylim(40, 100)
    axC.set_xlabel("position relative to candidate residue (aa)")
    axC.set_ylabel("AlphaFold pLDDT")
    S.panel(axC, "D")
    S.head(axC, "Model confidence where the argument is made")
    axC.text(-WIN_PLDDT + 1.5, 92.6, "very high (>90)", fontsize=S.BASE - 1.4, color=S.MUTED)
    axC.text(-WIN_PLDDT + 1.5, 72.0, "confident (70–90)", fontsize=S.BASE - 1.4, color=S.MUTED)
    axC.legend(loc="lower left", fontsize=S.BASE - 1.0)

    # ---------------- D · sequence logo + alignment coverage ----------------
    import logomaker
    import pandas as pd
    df = pd.DataFrame(logo["info_matrix"], index=logo["offsets"], columns=logo["aas"])
    box = axD.get_position()
    axD.set_position([box.x0, box.y0 + box.height * 0.30, box.width, box.height * 0.70])
    axCov = fig.add_axes([box.x0, box.y0, box.width, box.height * 0.24])

    logomaker.Logo(df, ax=axD, color_scheme="chemistry", vpad=0.02, width=0.92,
                   font_name="DejaVu Sans")
    axD.axvspan(-0.5, 0.5, color=CAND_COL, alpha=0.12, lw=0, zorder=0)
    axD.set_ylabel("information (bits)")
    axD.set_xlim(min(logo["offsets"]) - 0.6, max(logo["offsets"]) + 0.6)
    axD.set_xticks([])
    axD.grid(False)
    S.panel(axD, "C")
    S.head(axD, f"Sequence logo over {logo['n_orthologs']} one-to-one orthologs "
                f"(Ensembl); height is information, not frequency")
    axD.text(0, logo["hmax"] * 0.055, "candidate", ha="center", va="bottom",
             fontsize=S.BASE - 1.0, color=CAND_COL, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    cov = np.asarray(logo["aligned"], dtype=float)
    axCov.bar(logo["offsets"], cov, width=0.82, zorder=3,
              color=[CAND_COL if o == 0 else "#8E979E" for o in logo["offsets"]],
              edgecolor="white", linewidth=0.4)
    axCov.axhline(logo["n_orthologs"], color=S.MUTED, lw=0.8, ls="--", zorder=4)
    axCov.text(max(logo["offsets"]), logo["n_orthologs"] * 0.62,
               f"{logo['n_orthologs']} in set", ha="right", va="center",
               fontsize=S.BASE - 1.4, color=S.MUTED)
    axCov.set_xlim(min(logo["offsets"]) - 0.6, max(logo["offsets"]) + 0.6)
    axCov.set_ylim(0, logo["n_orthologs"] * 1.42)
    axCov.set_xticks(logo["offsets"][::2])
    axCov.set_xlabel("position relative to candidate residue (aa)")
    axCov.set_ylabel("n aligned", fontsize=S.BASE - 0.5)
    axCov.tick_params(labelsize=S.BASE - 1.4)
    S.grid(axCov)
    axCov.text(min(logo["offsets"]), logo["n_orthologs"] * 1.04,
               f"coverage is NOT constant: {int(cov.min())}–{int(cov.max())} aligned "
               f"across the window; the deepest clades drop out first",
               fontsize=S.BASE - 1.4, color=S.MUTED, va="bottom")

    S.note(fig, "Predicted structure, not an experimental one. Distances are measured on the "
                "model's coordinates; H-bonds are CANDIDATES from a donor/acceptor distance "
                "criterion only. The model carries no hydrogens, so no angle was checked.\n"
                f"Orthologs share ancestry: {logo['n_orthologs']} sequences are not "
                f"{logo['n_orthologs']} independent observations, and the clade breakdown puts "
                "the effective count near 5–6.")
    return fig


def prepare_logo(target: int, window: int = WIN_LOGO):
    from src.structure.ortholog_conservation import _one2one, per_position
    hom = _one2one("work/conservation/orthologs.json")
    human, aligned, ident, observed = per_position(hom)
    offs = [p - target for p in range(target - window, target + window + 1) if p in observed]
    cols = [target + o for o in offs]
    aas = sorted({a for p in cols for a in observed[p] if a.isalpha()})
    M = np.zeros((len(cols), len(aas)))
    for i, p in enumerate(cols):
        n = sum(v for k, v in observed[p].items() if k.isalpha())
        for j, a in enumerate(aas):
            M[i, j] = observed[p].get(a, 0) / n if n else 0.0
    hmax = float(np.log2(20))
    info = np.array([hmax + sum(q * np.log2(q) for q in row if q > 0) for row in M])
    return {"offsets": offs, "aas": aas, "info_matrix": M * info[:, None],
            "aligned": [aligned[p] for p in cols],
            "ident": [ident[p] for p in cols],
            "n_orthologs": len(hom), "hmax": hmax,
            "info_at_candidate": float(info[offs.index(0)]),
            "aligned_at_candidate": int(aligned[target]),
            "ident_at_candidate": int(ident[target])}


def load_and_build():
    from src.paths import get
    tgt = int(get("candidate", "residue"))
    geom = pg.summary(tgt)
    logo = prepare_logo(tgt)
    return build(geom, logo), {"geom": geom, "logo": logo}


if __name__ == "__main__":
    fig, d = load_and_build()
    print(S.export(fig, "fig03_pocket_and_conservation", "MODEL_OUTPUT", "PREDICTED+EXTERNAL"))
