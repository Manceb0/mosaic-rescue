"""Track 1 · la idea central: sin panel de genes, el genoma converge en BUB1B.

Tres piezas, cada una con un trabajo:
  A · embudo: del genoma entero (13 191 posiciones HIGH/MODERATE en 6 321 genes) a los 151 genes con un
      modelo de herencia, y a un solo gen que encabeza 14 de 15 rankings.
  B · tablero de rankings: BUB1B y sus rivales en los 15 análisis congelados, en A0-FREQFIX y en Exomiser
      (método externo sobre el MISMO VCF: no es evidencia biológica independiente). Enseña el #4 del A0 congelado y por qué, sin esconderlo: regla
      del proyecto, los dos números van siempre juntos.
  C · tablero de eliminación: cada competidor con el falsificador más barato que lo descartó (frecuencia →
      cigosidad → mecanismo); HLA-DRB1 queda señalado como hipótesis de auditoría, no eliminado.
Techo: candidato bialélico fuerte, NO diagnóstico (fase sin resolver).

Fuentes, comprobadas por SHA256 antes de dibujar: work/gw/mode_b_results_v4.pkl (15 rankings congelados),
work/gw/highmod_ann.tsv (anotación de la que salen el universo y A0-FREQFIX) y el genes.tsv del baseline
de Exomiser. Los textos del panel C citan docs/: TRACK1_REPORT §5, COMPETITOR_AUDIT_LZTR1_IGBP1,
EXTERNAL_BASELINE. Sin coordenadas: solo genes y posiciones de ranking.
"""
import csv
import hashlib
import io
import pickle
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon

sys.path.insert(0, ".")
from src.figures import style as S

PKL = (Path("work/gw/mode_b_results_v4.pkl"), "3ec4862274fa0f5168d32be8f69d1adacb631936e57aed678cf83a0cd79a8b3d")
ANN = (Path("work/gw/highmod_ann.tsv"), "6bb5d13907efa9d576115e5877603321c49eb523cff7c7d7dfbfd3bdba6f5ce2")
EXO = (Path("work/exomiser/runs/BASELINE-PRIMARY/BASELINE-PRIMARY.genes.tsv"),
       "00b8ef31c993095b4b7987d3f17c864feffad1a31dfa5cb66565081ed4c332e7")
FOCUS = "BUB1B"
RIVALS = ["CTU2", "PEX5", "SLC22A1"]
DEPTH = 8                       # posiciones dibujadas; por debajo se agrupan en «below #8»
ORDER = ["A0_GENETICS", "A1_GENETICS_CLINVAR", "B0_FULL_PROBAND", "B1_MINUS_RHABDOMYOSARCOMA",
         "B2_MINUS_RENAL", "B3_MINUS_GROWTH_PERINATAL", "B4_GENETICS_ONLY_CONTROL", "FH_ON",
         "LOO_HP_0002859", "LOO_HP_0000121", "LOO_HP_0004322", "LOO_HP_0001508", "LOO_HP_0003202",
         "LOO_HP_0001622", "LOO_HP_0001518"]
LABEL = {"A0_GENETICS": "A0\nfrozen", "A1_GENETICS_CLINVAR": "+ClinVar", "B0_FULL_PROBAND": "+HPO",
         "B1_MINUS_RHABDOMYOSARCOMA": "−rhabdo", "B2_MINUS_RENAL": "−renal", "B3_MINUS_GROWTH_PERINATAL": "−growth",
         "B4_GENETICS_ONLY_CONTROL": "genetics\ncontrol", "FH_ON": "+family\nhistory"}


def _check(path_sha) -> bytes:
    path, sha = path_sha
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError(f"{path} cambió respecto a la fuente congelada; revisar antes de dibujar")
    return raw


def _freqfix_ranks() -> dict:
    """A0-FREQFIX exactamente como en el notebook 01 (misma fórmula; frecuencias reparadas)."""
    from src.paths import patient_vcf
    from src.prioritization.freqfix_sensitivity import recovered_frequencies
    from src.prioritization.genome_wide import load, rank
    rows = load(str(ANN[0]), patient_vcf())
    freq = recovered_frequencies()
    for v in rows:
        if v.max_af is not None:
            continue
        base = int(v.loc.split(":")[1].split("-")[0])
        for d in (0, -1, -2):
            if (v.chrom, base + d) in freq:
                v.max_af = freq[(v.chrom, base + d)]
                break
    out = []
    for c in rank(rows, male=True):
        s = c.score
        if any("pathogenic" in (x.clinsig or "").lower() and "conflicting" not in (x.clinsig or "").lower()
               for x in c.variants):
            s -= 5.0
        out.append((s, c.gene))
    genes = [g for _, g in sorted(out, key=lambda t: (-t[0], t[1]))]
    return {g: i for i, g in enumerate(genes, 1)}


def _universe() -> tuple[int, int]:
    from src.paths import patient_vcf
    from src.prioritization.genome_wide import load
    rows = [r for r in load(str(ANN[0]), patient_vcf()) if r.impact in ("HIGH", "MODERATE")]
    return len({r.loc for r in rows}), len({r.gene for r in rows})


def _exomiser():
    rows = list(csv.reader(io.StringIO(_check(EXO).decode("utf-8")), delimiter="\t"))[1:]
    first = {}
    for r in rows:
        first.setdefault(r[2], int(r[0]))
    return first, len(first)


def _funnel(ax, n_pos, n_genes, n_scored):
    levels = [(f"{n_pos:,}".replace(",", " "), "HIGH/MODERATE positions,\nwhole genome, no panel"),
              (f"{n_genes:,}".replace(",", " "), "genes carrying them:\nevery one competed"),
              (str(n_scored), "genes whose genotype fits\nan inheritance model"),
              ("1", "BUB1B: #1 in 14 of\n15 rankings")]
    widths = [np.log10(max(int(t[0].replace(" ", "")), 1)) + 1 for t in levels]
    top = 9.4
    for i, ((num, txt), w) in enumerate(zip(levels, widths)):
        y0, y1 = top - i * 2.3, top - i * 2.3 - 1.7
        wn = widths[i + 1] if i + 1 < len(widths) else w * .55
        col = S.VERM if i == len(levels) - 1 else [S.HAIRLINE, "#C9CED3", "#AAB2BA"][i]
        ax.add_patch(Polygon([(-w, y0), (w, y0), (wn, y1), (-wn, y1)], closed=True, facecolor=col, lw=0))
        ax.text(0, (y0 + y1) / 2 + .15, num, ha="center", va="center", fontsize=15 if i < 3 else 13,
                fontweight="bold", color="white" if i == len(levels) - 1 else S.INK)
        ax.text(5.2, (y0 + y1) / 2, txt, va="center", fontsize=8.6, color=S.MUTED)
    ax.set_xlim(-5.2, 13)
    ax.set_ylim(.2, 9.8)
    ax.axis("off")


def _board(ax, res, fx, exo_rank, n_exo):
    cols = ORDER[:1] + ["FREQFIX"] + ORDER[1:]
    xs = {c: i for i, c in enumerate(cols)}
    x_exo = len(cols) + .9
    clip = lambda r: r if r <= DEPTH else DEPTH + 1
    ranks = {}
    for c in cols:
        if c == "FREQFIX":
            ranks[c] = {g: fx.get(g, 999) for g in [FOCUS] + RIVALS}
        else:
            genes = [x[0] for x in res[c]]
            ranks[c] = {g: (genes.index(g) + 1 if g in genes else 999) for g in [FOCUS] + RIVALS}
    for g in RIVALS:
        ys = [clip(ranks[c][g]) for c in cols]
        ax.plot([xs[c] for c in cols], ys, color="#B8BFC6", lw=1.3, marker="o", ms=4, zorder=2)
        ax.text(-.35, clip(ranks["A0_GENETICS"][g]), g, ha="right", va="center", fontsize=8, color=S.MUTED)
    ys = [clip(ranks[c][FOCUS]) for c in cols]
    ax.plot([xs[c] for c in cols], ys, color=S.VERM, lw=3, marker="o", ms=7, mec="white", mew=1.2, zorder=4)
    ax.text(-.35, ys[0], FOCUS, ha="right", va="center", fontsize=9.5, color=S.VERM, fontweight="bold")
    # Exomiser: otro universo, otra escala; se dibuja aparte y se nombra el #1
    ax.axvline(len(cols) + .3, color=S.HAIRLINE, lw=1)
    ax.plot([x_exo], [exo_rank["BUB1B"]], "o", ms=9, color=S.VERM, mec="white", mew=1.2, zorder=4)
    ax.plot([x_exo], [exo_rank["HLA-DRB1"]], "o", ms=6, color="#B8BFC6", zorder=3)
    ax.text(x_exo + .3, exo_rank["HLA-DRB1"], "HLA-DRB1", va="center", fontsize=7.5, color=S.MUTED)
    ax.text(x_exo + .3, exo_rank["BUB1B"], f"BUB1B #{exo_rank['BUB1B']} of {n_exo}", va="center", fontsize=8,
            color=S.VERM, fontweight="bold")
    ax.annotate("#4 in the frozen A0: the three genes\nahead are common polymorphisms",
                (0, ys[0]), xytext=(2.3, 7.7), fontsize=8, color=S.INK,
                arrowprops={"arrowstyle": "-", "color": S.INK, "lw": .7})
    ax.annotate("#1 once the 33 missing\npopulation frequencies are repaired", (1, ys[1]), xytext=(5.6, 6.35),
                fontsize=8, color=S.INK, arrowprops={"arrowstyle": "-", "color": S.INK, "lw": .7})
    labels = [LABEL.get(c, "A0-FREQFIX" if c == "FREQFIX" else "LOO " + c.split("_")[-1][-4:]).replace("\n", " ")
              for c in cols]
    ax.set_xticks(list(range(len(cols))) + [x_exo], labels + ["Exomiser (external)"], fontsize=7, rotation=90)
    ax.set_yticks(list(range(1, DEPTH + 1)) + [DEPTH + 1], [f"#{i}" for i in range(1, DEPTH + 1)] + [f"below\n#{DEPTH}"])
    ax.set_ylim(DEPTH + 1.6, .4)
    ax.set_xlim(-2.4, x_exo + 3.6)
    ax.set_ylabel("rank (1 = top candidate)")
    S.grid(ax)


def _elimination(ax):
    cards = [
        ("CTU2 · PEX5 · SLC22A1", "A0 #1–#3", "FREQUENCY", "common polymorphisms with rsIDs;\nup to 313 150 homozygotes in gnomAD", "out"),
        ("FANCD2", "Exomiser", "FREQUENCY + ZYGOSITY", "3 alleles at ~47 %, all heterozygous:\nno recessive configuration", "out"),
        ("LZTR1", "B0 #4", "ZYGOSITY + MECHANISM", "one allele, recessive syndromic form;\nno role in chromosome segregation", "out"),
        ("IGBP1", "B0 #6", "MECHANISM + FREQUENCY", "reported mechanism is 5'UTR, one family;\nMAX_AF 1e-4", "out"),
        ("HLA-DRB1", "Exomiser #1", "FLAGGED, NOT PROVEN", "35 variants, 28 without population\nfrequency, 0 ClinVar P/LP (audit hypothesis)", "flag"),
        ("BUB1B", "survives", "CANDIDATE, NOT DIAGNOSIS", "truncating Likely Pathogenic (9 points)\n+ rare missense VUS; phase unresolved", "keep"),
    ]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(cards) * 1.55 + .3)
    ax.axis("off")
    for i, (gene, where, verdict, why, kind) in enumerate(cards):
        y = (len(cards) - 1 - i) * 1.55 + .35
        edge = {"out": S.HAIRLINE, "flag": S.ORANGE, "keep": S.VERM}[kind]
        ax.add_patch(FancyBboxPatch((.05, y), 9.85, 1.25, boxstyle="round,pad=0.02,rounding_size=.15",
                                    facecolor="white" if kind != "keep" else "#FBEFE6", edgecolor=edge,
                                    lw=1.0 if kind == "out" else 1.8))
        gcol = S.MUTED if kind == "out" else (S.ORANGE if kind == "flag" else S.VERM)
        ax.text(.3, y + .85, gene, fontsize=9.5, fontweight="bold", color=gcol, va="center")
        ax.text(.3, y + .38, where, fontsize=7.5, color=S.MUTED, va="center")
        if kind == "out":
            ax.plot([.25, min(.35 + .155 * len(gene), 2.6)], [y + .85, y + .85], color=S.MUTED, lw=1.2)
        ax.text(3.55, y + .9, verdict, fontsize=7.6, fontweight="bold", color=gcol, va="center")
        ax.text(3.55, y + .4, why, fontsize=7.1, color=S.INK, va="center", linespacing=1.15)
    ax.text(.05, len(cards) * 1.55 + .2, "cheapest falsifier first: frequency → zygosity → mechanism → replication",
            fontsize=7.5, color=S.MUTED)


def load_and_build():
    res = pickle.loads(_check(PKL))
    _check(ANN)
    fx = _freqfix_ranks()
    exo_rank, n_exo = _exomiser()
    n_pos, n_genes = _universe()
    n_scored = len(res["A0_GENETICS"])
    top = sum(1 for k in ORDER if res[k][0][0] == FOCUS)
    if (top, len(ORDER), fx[FOCUS], exo_rank[FOCUS]) != (14, 15, 1, 2):
        raise ValueError("los rankings no coinciden con los números publicados (14/15, FREQFIX #1, Exomiser #2)")
    fig = plt.figure(figsize=(16, 9.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.25], height_ratios=[.82, 1.18],
                          left=.05, right=.985, top=.83, bottom=.135, wspace=.16, hspace=.30)
    fig.suptitle("Without a gene panel, the genome converges on BUB1B", x=.05, y=.965, ha="left",
                 fontsize=19, fontweight="bold", color=S.INK)
    ng = f"{n_genes:,}".replace(",", " ")
    fig.text(.05, .93, f"Every gene with a high- or moderate-impact allele competed ({ng} genes). BUB1B leads "
             f"{top} of {len(ORDER)} rankings and an external tool on the same VCF places it #{exo_rank[FOCUS]} of {n_exo}.\n"
             "It is #4 in the frozen A0 and #1 after repairing missing frequencies: both numbers are always "
             "reported. Phase is unresolved, so this is a strong candidate, not a diagnosis.",
             fontsize=10.5, color=S.MUTED, va="top")
    axA = fig.add_subplot(gs[0, 0])
    _funnel(axA, n_pos, n_genes, n_scored)
    S.panel(axA, "A", dx=-.01)
    S.head(axA, "From the whole genome to one gene")
    axC = fig.add_subplot(gs[:, 1])
    _elimination(axC)
    S.panel(axC, "C", dx=-.01)
    S.head(axC, "Every rival, and what removed it")
    axB = fig.add_subplot(gs[1, 0])
    _board(axB, res, fx, exo_rank, n_exo)
    S.panel(axB, "B")
    S.head(axB, "Rank of BUB1B and its rivals: 15 frozen rankings + A0-FREQFIX + Exomiser")
    S.note(fig, "Sources SHA256-checked: mode_b_results_v4.pkl 3ec48622… (15 frozen rankings) · highmod_ann.tsv "
           "6bb5d139… (universe; A0-FREQFIX recomputed with the notebook-01 formula) · Exomiser BASELINE-PRIMARY "
           "genes.tsv 00b8ef31….\nPanel C texts: reports/TRACK1_REPORT.md §5, docs/COMPETITOR_AUDIT_LZTR1_IGBP1.md, "
           "docs/EXTERNAL_BASELINE.md. Prioritization scores are not test statistics. No coordinates shown.")
    return fig, {"top": top, "freqfix": fx[FOCUS], "exomiser": exo_rank[FOCUS], "n_genes": n_genes}


if __name__ == "__main__":
    fig, info = load_and_build()
    print(S.export(fig, "fig14_track1_convergence", "DATA", "MEASURED+EXTERNAL+DERIVED"), info)
