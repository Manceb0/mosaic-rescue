"""EXP-027 Phase 1 · resultado sellado, contado como idea: el método ve la señal inyectada, pero se enciende sin señal inyectada.

Cuatro piezas, cada una con un trabajo:
  A · matriz de los 1 000 pares reales (20 hijos × 50 ventanas): cada casilla es un par con datos intactos;
      las que el test llama positivas se encienden. Un test calibrado encendería ~5 %.
  B · QQ-plot de los 995 p-valores intactos frente a la diagonal uniforme (envolvente iid Uniform, 95 %,
      DESCRIPTIVA, semilla fija; los pares no son independientes): null mal calibrado en el benchmark.
  C · potencia: detección frente al δ inyectado con fase inferida y mendeliana; el hueco es lo que cuesta
      la fase inferida.
  D · tablero de puertas preregistradas que desemboca en la compuerta del paciente: cerrada.

Fuentes congeladas, comprobadas por SHA256 antes de dibujar: phase1_report.json (informe adjudicado),
phase1_posthoc.json (reproducción idéntica; curvas por δ), apr_map.csv (llamadas por par reconstruidas con
las mismas semillas; dan las mismas 249/995 que el informe) y plan_windows.json (orden de ventanas, BUB1B #1).
No se escriben coordenadas: las columnas son el orden de evaluación.
"""
import csv
import hashlib
import io
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.insert(0, ".")
from src.figures import style as S

ROOT = Path("work/exp027")
SOURCES = {
    "report": (ROOT / "phase1_r2/phase1_report.json",
               "37e676ad5137dc4ceee283de7251b403323c3d9dda589907e8eff43a441e1e3e"),
    "posthoc": (ROOT / "posthoc/phase1_posthoc.json",
                "923cfb32854c76867bc7fd06a28bef83c624f0e49bb17d6a987d3de4146ae136"),
    "map": (ROOT / "posthoc/apr_map.csv",
            "316f0cf7be522f0ca62e1b4e55bcb1c01f1efe65e3591b27babdc23c7897da3d"),
    "plan": (ROOT / "plan_execution/plan_windows.json",
             "e3731d525b1980026a5700f2fe8772a02eee6d363fa69e376cdd4b8bfa7c1c80"),
}
OFF = "#EEF0F2"           # par intacto no positivo
SEED = 42


def _raw(key: str) -> bytes:
    path, sha = SOURCES[key]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError(f"{path} cambió respecto al artefacto sellado; revisar antes de dibujar")
    return raw


def _load():
    rep = json.loads(_raw("report"))
    ph = json.loads(_raw("posthoc"))
    plan = json.loads(_raw("plan"))
    text = _raw("map").decode("utf-8")
    rows = list(csv.DictReader(l for l in io.StringIO(text) if not l.startswith("#")))
    if not ph["reproduction"]["identical_to_sealed_report"]:
        raise ValueError("la reproducción no coincide con el informe sellado")
    pos = sum(r["positive"] == "True" for r in rows if r["evaluable"] == "True")
    if (pos, sum(r["evaluable"] == "True" for r in rows)) != (rep["apr_k"], rep["apr_n"]):
        raise ValueError("el mapa por par no reproduce el APR del informe")
    return rep, ph, plan, rows


def _matrix(ax, rep, plan, rows):
    kids = [s["child"] for s in plan["selection"]]
    sp = {s["child"]: s["superpop"] for s in plan["selection"]}
    col = {w: i for i, w in enumerate(plan["evaluation"])}
    cell = {(r["child"], r["window"]): r for r in rows}
    for y, kid in enumerate(kids):
        for w, x in col.items():
            r = cell[(kid, w)]
            yy = len(kids) - 1 - y
            if r["evaluable"] != "True":
                ax.add_patch(Rectangle((x + .08, yy + .08), .84, .84, facecolor="white", edgecolor=S.HAIRLINE, lw=.6))
                ax.plot([x + .25, x + .75], [yy + .25, yy + .75], color=S.MUTED, lw=.6)
            else:
                on = r["positive"] == "True"
                ax.add_patch(Rectangle((x + .08, yy + .08), .84, .84, facecolor=S.VERM if on else OFF, lw=0))
    ax.add_patch(Rectangle((-.02, -.12), 1.04, len(kids) + .24, fill=False, edgecolor=S.INK, lw=1.2))
    ax.text(.5, len(kids) + .35, "BUB1B", ha="center", va="bottom", fontsize=8, color=S.INK)
    for y, kid in enumerate(kids):
        ax.text(-.4, len(kids) - 1 - y + .5, f"{sp[kid]}", ha="right", va="center", fontsize=6.5,
                color=S.MUTED if y % 4 else S.INK)
    ax.set_xlim(-2.2, 50.2)
    ax.set_ylim(-2.9, len(kids) + 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    k, n = rep["apr_k"], rep["apr_n"]
    items = [(S.VERM, None, f"lit: called positive on intact data ({k}/{n} = {100 * k / n:.0f} %)"),
             (OFF, None, "unlit"),
             ("white", S.HAIRLINE, "not evaluable (< 50 markers, 5 pairs)")]
    for x, (fc, ec, label) in zip((0.0, 23.5, 28.5), items):       # posiciones fijas: sin solapes
        ax.add_patch(Rectangle((x, -1.55), .84, .84, facecolor=fc, edgecolor=ec or fc, lw=.6))
        ax.text(x + 1.25, -1.13, label, fontsize=7.5, color=S.MUTED, va="center")
    ax.text(0, -2.45, "columns: the 50 evaluation windows (BUB1B first) · rows: the 20 children, grouped by "
            "superpopulation", fontsize=7.5, color=S.MUTED, va="center")


def _qq(ax, rows):
    p = np.array(sorted(float(r["p"]) for r in rows if r["evaluable"] == "True"))
    n = p.size
    exp = -np.log10((np.arange(1, n + 1) - .5) / n)
    obs = -np.log10(p)
    rng = np.random.default_rng(SEED)
    sims = -np.log10(np.sort(rng.uniform(size=(2000, n)), axis=1))
    lo, hi = np.quantile(sims, [.025, .975], axis=0)
    ax.fill_between(exp, lo, hi, color=S.HAIRLINE, lw=0, label="iid Uniform reference envelope (95 %, descriptive)")
    lim = math.ceil(max(exp.max(), obs.max()) * 10) / 10 + .15
    ax.plot([0, lim], [0, lim], color=S.MUTED, lw=1, ls="--", label="calibrated: observed = expected")
    ax.plot(exp, obs, "o", ms=2.6, color=S.VERM, mec="none", label="995 intact benchmark pairs")
    floor = -math.log10(1 / 10001)
    ax.axhline(floor, color=S.HAIRLINE, lw=.8)
    ax.text(.05, floor + .06, "permutation floor 1/(B+1)", fontsize=7, color=S.MUTED)
    z2 = [NormalDist().inv_cdf(1 - x / 2) ** 2 for x in p]
    lam = float(np.median(z2)) / 0.4549364
    ax.axhline(-math.log10(.05), color=S.INK, lw=.6, ls=":")
    ax.text(lim - .05, -math.log10(.05) - .2, "p = 0.05", ha="right", fontsize=7, color=S.INK)
    ax.text(.15, lim - .35, f"inflation λ ≈ {lam:.1f}\n(calibrated: 1.0)", fontsize=9, color=S.VERM, va="top")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("expected −log10 p (iid Uniform)")
    ax.set_ylabel("observed −log10 p")
    ax.legend(loc="lower right", frameon=False, fontsize=7.5)
    S.grid(ax, "both")
    return lam


def _power(ax, rep, ph):
    c = ph["sensitivity_by_delta"]
    ds = sorted(c["inferred"], key=float)
    x = np.array([float(d) for d in ds])
    yi = np.array([c["inferred"][d] for d in ds])
    ym = np.array([c["mendelian"][d] for d in ds])
    ax.fill_between(x, yi, ym, color=S.SKY, alpha=.25, lw=0)
    ax.plot(x, ym, color=S.MUTED, lw=2, marker="s", ms=5, mfc="white", label="true (Mendelian) phase")
    ax.plot(x, yi, color=S.BLUE, lw=2, marker="o", ms=5, label="inferred phase (SHAPEIT5)")
    ax.axhline(.80, color=S.INK, lw=.6, ls=":")
    ax.text(.198, .815, "gate 0.80", ha="right", fontsize=7, color=S.INK)
    ax.axvline(.10, color=S.HAIRLINE, lw=1)
    ax.annotate(f"δ* = 0.10\nsensitivity {rep['sensitivity_inferred']:.3f}\nretention {rep['retention']:.3f}",
                (.10, rep["sensitivity_inferred"]), xytext=(.118, .42), fontsize=8, color=S.BLUE,
                arrowprops={"arrowstyle": "-", "color": S.BLUE, "lw": .8})
    ax.text(.03, .86, "cost of\ninferred phase", fontsize=7, color=S.MUTED)
    ax.set_xlim(-.005, .205)
    ax.set_ylim(-.02, 1.04)
    ax.set_xlabel("spiked-in haplotype imbalance δ")
    ax.set_ylabel("windows detected (child-weighted)")
    ax.legend(loc="lower right", frameon=False, fontsize=7.5)
    S.grid(ax)


def _gates(ax, rep):
    loc = rep["locus_bub1b"]
    k, n = rep["apr_k"], rep["apr_n"]
    gates = [
        (True, "Sensitivity at δ = 0.10", f"{rep['sensitivity_inferred']:.3f} ≥ 0.80"),
        (True, "Power retention", f"{rep['retention']:.3f} ≥ 0.90"),
        (True, "Switch error (common)", f"{100 * rep['ser']:.2f} % ≤ 2 %"),
        (True, "No superpopulation veto", "5 / 5 strata"),
        (False, "Calibration sentinel (APR)", f"{k}/{n} = {100 * k / n:.0f} % vs 5 %"),
        (True, "BUB1B: evaluable children", f"{loc['evaluable_children']} / 20 ≥ 15"),
        (True, "BUB1B: sensitivity", f"{loc['sensitivity']:.3f} ≥ 0.80"),
        (False, "BUB1B: retention", f"{loc['retention']:.3f} < 0.90"),
        (True, "BUB1B: technical sentinel", f"{loc['sentinel_positives']} < {loc['sentinel_critical']}"),
    ]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    top, step = 9.55, 1.02
    for i, (ok, name, val) in enumerate(gates):
        y = top - i * step
        col = S.GREEN if ok else S.VERM
        ax.add_patch(FancyBboxPatch((.1, y - .38), 5.6, .76, boxstyle="round,pad=0.02,rounding_size=.18",
                                    facecolor="white", edgecolor=col, lw=1.6 if not ok else 1.0))
        ax.text(.4, y, "✓" if ok else "✗", fontsize=11, color=col, va="center", ha="center", fontweight="bold")
        ax.text(.8, y + .12, name, fontsize=7.6, color=S.INK, va="center")
        ax.text(.8, y - .2, val, fontsize=7, color=S.MUTED, va="center")
        ax.add_patch(FancyArrowPatch((5.75, y), (6.85, 5.0), arrowstyle="-", color=col,
                                     lw=1.4 if not ok else .5, alpha=1 if not ok else .45,
                                     connectionstyle="arc3,rad=0"))
    ax.add_patch(FancyBboxPatch((6.9, 3.55), 3.0, 2.9, boxstyle="round,pad=0.02,rounding_size=.3",
                                facecolor=S.INK, edgecolor=S.INK))
    ax.text(8.4, 5.75, "ALL gates must pass", ha="center", fontsize=7, color="white")
    ax.text(8.4, 5.05, "PATIENT A1", ha="center", fontsize=10.5, color="white", fontweight="bold")
    ax.text(8.4, 4.45, "NOT RUN", ha="center", fontsize=12, color=S.VERM, fontweight="bold")
    ax.text(8.4, 3.85, "gate closed by 2 failures", ha="center", fontsize=7, color="white")


def load_and_build():
    rep, ph, plan, rows = _load()
    fig = plt.figure(figsize=(16, 9.2))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.55, .95, 1.1], height_ratios=[1.12, 1],
                          left=.045, right=.985, top=.82, bottom=.10, wspace=.26, hspace=.36)
    fig.suptitle("High sensitivity, failed calibration → patient test not performed",
                 x=.045, y=.965, ha="left", fontsize=19, fontweight="bold", color=S.INK)
    fig.text(.045, .93, "The method detects a haplotype imbalance when we inject one, but on intact, unspiked benchmark "
             "data it lights up one window in four.\nA detector that fires without injected signal cannot be trusted on a "
             "child, so Mosaic Rescue closed the gate.", fontsize=11, color=S.MUTED, va="top")
    fig.text(.045, .852, "EXP-027 Phase 1 · METHOD VALIDATION FAIL · public 1000 Genomes high-coverage trios, "
             "no patient data · tag exp027-phase1-execution-freeze-r2", fontsize=9, color=S.MUTED)

    axA = fig.add_subplot(gs[0, 0:2])
    _matrix(axA, rep, plan, rows)
    S.panel(axA, "A", dx=-.01)
    S.head(axA, "Intact, unspiked benchmark data, 1 000 pairs: what lit up")
    axB = fig.add_subplot(gs[0, 2])
    lam = _qq(axB, rows)
    S.panel(axB, "B")
    S.head(axB, "The null is miscalibrated on the benchmark")
    axC = fig.add_subplot(gs[1, 0])
    _power(axC, rep, ph)
    S.panel(axC, "C")
    S.head(axC, "…while the signal is seen")
    axD = fig.add_subplot(gs[1, 1:3])
    _gates(axD, rep)
    S.panel(axD, "D", dx=-.01)
    S.head(axD, "Preregistered gates → patient")
    S.note(fig, "Sources SHA256-checked: phase1_report.json 37e676ad… · post-hoc reproduction 923cfb32… "
           "(identical to the sealed report) · per-pair calls apr_map.csv 316f0cf7… (same seeds; 249/995) · "
           "plan_windows.json e3731d52….\nQQ envelope: 2 000 iid Uniform draws, seed 42, descriptive only (the 995 pairs share children, windows and pipeline, so they are not iid). APR is an operational "
           "calibration sentinel on LCL-derived benchmark DNA, not a biological false-positive rate. "
           "The patient was never tested.")
    return fig, {"apr": rep["apr_k"] / rep["apr_n"], "lambda": lam, "bub1b_retention": rep["locus_bub1b"]["retention"]}


if __name__ == "__main__":
    fig, info = load_and_build()
    print(S.export(fig, "fig13_exp027_phase1_result", "DATA", "EXTERNAL+DERIVED"), info)
