#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contact sheet: an index of the eight publication figures.

Que cambio, y por que importa
    The first version squeezed each hero into a gallery tile, and the figures
    started being designed to survive that squeeze. That is backwards. The full
    figure is the deliverable; this sheet is only a way to find it.

    One row per notebook, with the thumbnail render, which is a separate and smaller
    render produced by src/figures/style.export(), never a brutal downscale of
    the 300-dpi raster, plus the title, the figure class and a single-line
    takeaway. No captions. Nothing else.

Salida
    work/nbrender/CONTACT_SHEET.png. work/ is gitignored, so the sheet is reviewed
    before anything is versioned.
"""
from __future__ import annotations
import os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402
from src.figures.render_all import FIGURES                             # noqa: E402

OUT = "work/nbrender/CONTACT_SHEET.png"
BADGE = {"DATA": S.GREEN, "MODEL_OUTPUT": S.BLUE, "SIMULATION": S.PURPLE,
         "CURATED_EVIDENCE": S.ORANGE, "SYNTHESIS": S.ORANGE, "NARRATIVE": S.MUTED}


def wrap(text: str, width: int = 96) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return "\n".join(lines)


def main():
    rows = []
    for _mod, slug, nb, cls, origin, takeaway in FIGURES:
        p = os.path.join(S.THUMB_DIR, slug + ".png")
        if not os.path.exists(p):
            print(f"  falta {p}, ejecuta src/figures/render_all.py primero")
            continue
        rows.append((nb, slug, cls, origin, takeaway, mpimg.imread(p)))

    n = len(rows)
    # Rejilla explicita de dos columnas. La version anterior recolocaba los ejes
    # a mano y luego pedia bbox_inches="tight": las dos cosas se peleaban y
    # dejaban un hueco enorme arriba con los textos montados unos sobre otros.
    fig = plt.figure(figsize=(12.0, 1.34 + 2.10 * n), facecolor=S.PAPER)
    gs = fig.add_gridspec(n, 2, width_ratios=[1.0, 2.35],
                          left=0.018, right=0.986, top=1 - 1.10 / (1.34 + 2.10 * n),
                          bottom=0.012, hspace=0.30, wspace=0.02)

    for i, (nb, slug, cls, origin, takeaway, img) in enumerate(rows):
        axt = fig.add_subplot(gs[i, 0])
        axt.axis("off")
        axt.text(0, 1.00, nb.replace("_", " "), fontsize=S.BASE + 2.4,
                 fontweight="bold", color=S.INK, va="top", transform=axt.transAxes)
        axt.text(0, 0.855, cls.replace("_", " "), fontsize=S.BASE - 0.5,
                 fontweight="bold", color=BADGE.get(cls, S.MUTED), va="top",
                 transform=axt.transAxes)
        # el segundo eje va aparte, nunca pegado al primero
        axt.text(0, 0.775, origin, fontsize=S.BASE - 1.2, fontweight="bold",
                 color=S.MUTED, va="top", transform=axt.transAxes)
        axt.text(0, 0.680, wrap(takeaway, 40), fontsize=S.BASE - 0.8, color=S.MUTED,
                 va="top", linespacing=1.55, transform=axt.transAxes)
        axt.text(0, 0.015, f"figures/pub/{slug}.svg", fontsize=S.BASE - 2.0,
                 color="#B7BDC2", va="bottom", transform=axt.transAxes)

        axi = fig.add_subplot(gs[i, 1])
        axi.imshow(img)
        axi.set_xticks([]); axi.set_yticks([])
        for sp in axi.spines.values():
            sp.set_color(S.HAIRLINE)

    fig.suptitle("MOSAIC RESCUE, publication figures: index",
                 x=0.018, y=0.996, ha="left", fontsize=S.BASE + 6.0,
                 fontweight="bold", color=S.INK)
    fig.text(0.018, 0.996 - 0.40 / (1.34 + 2.10 * n),
             "thumbnails are separate small renders, not downscaled 300-dpi rasters; "
             "the full-size figure is the deliverable",
             fontsize=S.BASE - 0.5, color=S.MUTED, ha="left", va="top")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=118, facecolor=S.PAPER)
    print(f"  {OUT}  ({os.path.getsize(OUT) / 1024:.0f} kB · {n} rows)")
    print()
    print(f"  {'notebook':<26}{'FIGURE CLASS':<18}{'EVIDENCE ORIGIN':<28}figure")
    print("  " + "-" * 104)
    for nb, slug, cls, origin, _t, _i in rows:
        print(f"  {nb:<26}{cls:<18}{origin:<28}figures/pub/{slug}.svg")


if __name__ == "__main__":
    main()
