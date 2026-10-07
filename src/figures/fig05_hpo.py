#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 6. Seven traits, two checks: only nephrocalcinosis fails both.

A · matriz término HPO × modelo, en bits (dato medido). B · registro alineado fila a fila: comprobación 1
(anotado en el modelo MVA1, medido), comprobación 2 (compilación publicada de 31 casos, del audit) y el veredicto que
DERIVA de ambas. Sustituye a las barras de BMA, que ahora van en la etiqueta de cada columna.

What the cells hold
    Resnik: the information content, in bits, of the most informative common
    ancestor between the proband term and the best-matching term of the model.
    That is the quantity the ranking engine itself consumes; nothing here is a
    category we invented.

Why not a simple annotated / not annotated flag
    Binary is the wrong answer to a graded question, and an "ancestor covers it"
    rule is worse: the corpus stores terms PROPAGATED to the root, so every model
    trivially annotates an ancestor of everything. That version was built, came
    out uniform, and was discarded.

Two kinds of support, kept separate
    Colour = HPO database support, in bits.
    Ring   = literature support for MVA1 specifically, from the 31-case literature compilation.
    Literature is never converted into a Resnik score. Mixing the two is exactly
    how a phenotype gap gets talked away.

Column labels
    Disease name and gene on top, identifier small underneath. A reader should
    not have to memorise OMIM codes to see the pattern.
"""
from __future__ import annotations
import io, sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

NL2 = chr(10)
MVA_IDS = ["OMIM:257300", "OMIM:614114", "OMIM:617598"]
SHORT = {"OMIM:257300": "MVA 1", "OMIM:614114": "MVA 2", "OMIM:617598": "MVA 3"}
HPOA = "work/hpo/phenotype.hpoa"


def disease_names(path: str = HPOA) -> dict:
    """database_id -> disease_name, straight from the HPO annotation file."""
    out, hdr = {}, None
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if line.startswith("#"):
            continue
        parts = line.rstrip("\n").split("\t")
        if hdr is None:
            hdr = parts
            continue
        r = dict(zip(hdr, parts))
        did = r.get("database_id")
        if did and did not in out and r.get("disease_name"):
            out[did] = r["disease_name"]
    return out


def wrap(text: str, width: int = 22, max_lines: int = 3) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:width - 1] + "…"
    return "\n".join(lines)


def verdicts(m: dict) -> list:
    """Veredicto por rasgo, DERIVADO de las dos comprobaciones; nada colocado a mano.

    Comprobación 1 (medida): ¿el término está anotado en el modelo MVA1 del corpus HPO?
    Comprobación 2 (literatura): ¿la compilación publicada de 31 casos MVA1 lo respalda? (LIT_MVA1_DETAIL,
    tal como está en docs/PHENOTYPE_RESIDUAL_AUDIT.md). Las categorías son las del audit.
    """
    PT, COV = m["terms"], m["covered"]
    j1 = [j for j, c in enumerate(m["cols"]) if c["id"] == MVA_IDS[0]][0]
    out = []
    for i, t in enumerate(PT):
        lit, _txt = LIT_MVA1_DETAIL[t]
        if COV[i, j1]:
            v = "EXPLAINED"
        elif lit == "yes":
            v = "ANNOTATION GAP"
        elif lit == "nq":
            v = "CANNOT JUDGE"
        else:
            v = "RESIDUAL"
        out.append(v)
    return out


VSTYLE = {  # relleno, borde, tinta, trama; la identidad va además escrita en la píldora
    "EXPLAINED":      ("#E3EEF6", "#2B7BBA", "#1F5F8F", None),
    "ANNOTATION GAP": ("#FFFFFF", "#2B7BBA", "#1F5F8F", None),
    "CANNOT JUDGE":   ("#F2F3F4", "#9AA4AC", "#5B6670", None),
    "RESIDUAL":       ("#D55E00", "#D55E00", "#FFFFFF", None),
}
VNOTE = {
    "EXPLAINED": "annotated in the MVA1 model",
    "ANNOTATION GAP": "corpus gap; broader support only",
    "CANNOT JUDGE": "PARKED: no number in the compilation",
    "RESIDUAL": "fails both checks",
}


def build(m: dict):
    """m: the prepared matrix, see prepare()."""
    from matplotlib.patches import FancyBboxPatch, Rectangle

    PT, COLS = m["terms"], m["cols"]
    BM, COV, LIT = m["bestmatch"], m["covered"], m["literature"]
    names, ic_t = m["names"], m["ic_terms"]
    V = verdicts(m)
    i_nef = m["nephro_index"]
    # Guardia: la tesis del título tiene que salir de los datos, o no se dibuja.
    if [i for i, v in enumerate(V) if v == "RESIDUAL"] != [i_nef]:
        raise SystemExit(f"fig05: el residual no es solo nefrocalcinosis: {V}")

    n = len(PT)
    fig = plt.figure(figsize=(16.0, 9.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[12, 6.4], left=.13, right=.985,
                          top=.745, bottom=.215, wspace=.025)
    ax = fig.add_subplot(gs[0, 0])
    al = fig.add_subplot(gs[0, 1], sharey=ax)

    vmax = float(max(BM.max(), max(ic_t.values())))
    im = ax.imshow(BM, cmap="YlGnBu", vmin=0, vmax=vmax, aspect="auto")
    for i in range(n):
        for j in range(len(COLS)):
            v = BM[i, j]
            dark = v > vmax * 0.55
            ax.text(j, i - 0.10, f"{v:.1f}", ha="center", va="center",
                    fontsize=S.BASE - 0.6, color="white" if dark else S.INK,
                    fontweight="bold" if COV[i, j] else "normal")
            if COV[i, j]:
                ax.text(j, i + 0.27, "covered", ha="center", va="center",
                        fontsize=S.BASE - 2.6, color="white" if dark else S.MUTED)
            if LIT[i, j]:
                ax.add_patch(Rectangle((j - 0.45, i - 0.45), 0.9, 0.9, fill=False,
                                       edgecolor=S.VERM, lw=1.5, zorder=5,
                                       linestyle=(0, (2.4, 1.4))))
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{m['term_labels'][t]}\nown IC {ic_t[t]:.1f} bits" for t in PT],
                       fontsize=S.BASE + 0.1, linespacing=1.25)
    ax.set_xticks(range(len(COLS)))
    ax.set_xticklabels([wrap(names.get(c["id"], c["gene"]), width=16, max_lines=3)
                        + NL2 + c["gene"] + NL2 + f"profile {c['bma']:.2f} bits"
                        for c in COLS], fontsize=S.BASE - 2.4, linespacing=1.25)
    ax.tick_params(axis="x", pad=3, length=0)
    ax.grid(False)
    for j, c in enumerate(COLS):
        if c["id"] in MVA_IDS:
            ax.add_patch(Rectangle((j - 0.5, -0.5), 1.0, n, fill=False,
                                   edgecolor=S.INK, lw=1.8, zorder=6))
    # La fila residual se recorta en los dos paneles, para que el ojo la siga de lado a lado.
    for a, x0, w in ((ax, -0.5, len(COLS)), (al, 0.0, 10.0)):
        a.add_patch(Rectangle((x0, i_nef - 0.5), w, 1.0, fill=False, edgecolor=S.VERM,
                              lw=2.4, zorder=7, clip_on=False))
    S.panel(ax, "A", dx=-0.03, dy=1.135)
    ax.text(0, 1.135, "Where each trait fits: semantic match to every model evaluated "
            "(Resnik, bits)", transform=ax.transAxes, fontsize=S.BASE + 0.5, color=S.INK)
    ax.text(0, 1.03, "colour and number = HPO database support  ·  dashed ring = MVA1 literature "
            "support (never a score)  ·  boxed = the three MVA models",
            transform=ax.transAxes, fontsize=S.BASE - 1.2, color=S.MUTED, va="bottom")
    cax = fig.add_axes([.13, .095, .16, .011])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("Resnik: IC of the most informative common ancestor (bits)",
                 fontsize=S.BASE - 1.4, color=S.MUTED)
    cb.ax.xaxis.set_label_position("top")
    cb.ax.tick_params(labelsize=S.BASE - 1.6)

    # ---- B · registro de veredictos, fila a fila --------------------------------
    al.set_xlim(0, 10)
    al.axis("off")
    X1, X2, XV = .9, 3.05, 7.3
    al.text(X1, -0.78, "1 · annotated\nin MVA1 model?", ha="center", va="bottom",
            fontsize=S.BASE - 1.1, color=S.INK, fontweight="bold", linespacing=1.15)
    al.text(X2 - .55, -0.78, "2 · supported by the 31-case\nMVA1 literature compilation?",
            ha="left", va="bottom", fontsize=S.BASE - 1.1, color=S.INK, fontweight="bold",
            linespacing=1.15)
    al.text(XV, -0.78, "verdict", ha="center", va="bottom", fontsize=S.BASE - 1.1,
            color=S.INK, fontweight="bold")
    S.panel(al, "B", dx=0.0, dy=1.135)
    al.text(.045, 1.135, "Two checks per trait", transform=al.transAxes,
            fontsize=S.BASE + 0.5, color=S.INK)
    j1 = [j for j, c in enumerate(COLS) if c["id"] == MVA_IDS[0]][0]
    for i, t in enumerate(PT):
        if i:
            al.plot([0.1, 9.9], [i - 0.5, i - 0.5], color=S.HAIRLINE, lw=.6)
        ok1 = bool(COV[i, j1])
        al.text(X1, i, "✓" if ok1 else "✗", ha="center", va="center", fontsize=S.BASE + 5,
                color="#1F5F8F" if ok1 else S.MUTED, fontweight="bold")
        lit, txt = LIT_MVA1_DETAIL[t]
        mark = {"yes": "✓", "nq": "?", "no": "✗"}[lit]
        col2 = {"yes": "#1F5F8F", "nq": S.MUTED, "no": S.VERM}[lit]
        al.text(X2 - .55, i, mark, ha="center", va="center", fontsize=S.BASE + 5, color=col2,
                fontweight="bold")
        al.text(X2 - .1, i, txt, ha="left", va="center", fontsize=S.BASE - 1.6,
                color=S.INK, linespacing=1.15)
        fill, edge, ink, hatch = VSTYLE[V[i]]
        al.add_patch(FancyBboxPatch((XV - 1.25, i - .30), 2.5, .40,
                                    boxstyle="round,pad=0,rounding_size=.12", fc=fill,
                                    ec=edge, lw=1.3, hatch=hatch, zorder=3,
                                    ls="--" if V[i] == "CANNOT JUDGE" else "-"))
        al.text(XV, i - .10, V[i], ha="center", va="center", fontsize=S.BASE - 1.3,
                color=ink, fontweight="bold", zorder=4)
        al.text(XV, i + .27, VNOTE[V[i]], ha="center", va="center", fontsize=S.BASE - 2.3,
                color=S.VERM if V[i] == "RESIDUAL" else S.MUTED, zorder=4)
    al.set_ylim(n - 0.5, -0.5)

    mv = [j for j, c in enumerate(COLS) if c["id"] in MVA_IDS]
    ot = [j for j in range(len(COLS)) if j not in mv]
    nef_other = [j for j in ot if COV[i_nef, j]]
    n_bartter = sum(1 for j in nef_other if "bartter" in names.get(COLS[j]["id"], "").lower())
    cnt = {v: V.count(v) for v in VSTYLE}
    unc_mva = all(not COV[i_nef, j] for j in mv)
    if not unc_mva:
        raise SystemExit("fig05: algún modelo MVA cubre la nefrocalcinosis; revisar el texto")

    fig.text(.03, .955, "Among seven recorded traits, nephrocalcinosis is the only one unsupported by both checks",
             fontsize=21, fontweight="bold", color=S.INK)
    fig.text(.03, .845,
             f"{cnt['EXPLAINED']} traits are annotated in the MVA1 model; {cnt['ANNOTATION GAP']} more is supported by the 31-case compilation only "
             f"through a broader growth phenotype; {cnt['CANNOT JUDGE']} cannot be judged (PARKED, not negative)." + NL2 +
             f"Nephrocalcinosis is annotated in none of the three MVA models (best match "
             f"{BM[i_nef, mv[0]]:.1f} of {ic_t[PT[i_nef]]:.1f} bits) and not reported in the compilation, while "
             f"{len(nef_other)} of {len(ot)} neighbour models cover it ({n_bartter} Bartter)." + NL2 +
             "A residual trait raises, but does not establish, a second diagnosis.",
             fontsize=11.5, color=S.MUTED, linespacing=1.4)
    S.note(fig,
           "Sources: work/hpo/prepared.pkl (9 155 disease models) + work/hpo/phenotype.hpoa (names); "
           "check 2 and its percentages from Pavone et al. 2022 (PMID 35804254), a 31-case literature compilation, via docs/PHENOTYPE_RESIDUAL_AUDIT.md (EXP-018/019).\n"
           "Annotation bias is not corrected: a poorly annotated disease scores low even where the "
           "trait occurs. Columns are the nearest models to the FULL profile, not a search for renal "
           "models. Level L2.",
           y=0.004)
    return fig


def prepare(target_terms, term_labels, literature_mva1, n_cols: int = 12):
    """Everything measured; nothing here is a hand-placed category."""
    import pickle
    from src.phenotype.semantic import ancestors, resnik_bma

    prep = pickle.load(io.open("work/hpo/prepared.pkl", "rb"))
    PAR, IC, MODELS = prep["parents"], prep["ic"], prep["models"]
    cache = {}
    PT = list(target_terms)

    def bestmatch(t, model):
        at = ancestors(t, PAR, cache)
        best = 0.0
        for mt in model.terms:
            sh = at & ancestors(mt, PAR, cache)
            if sh:
                v = max(IC.get(a, 0.0) for a in sh)
                best = max(best, v)
        return best

    byid = {}
    for mo in MODELS:
        byid.setdefault(mo.disease_id, mo)
    scored = sorted(((resnik_bma(PT, mo.terms, IC, PAR, cache), mo)
                     for mo in byid.values()), key=lambda x: -x[0])
    chosen, seen = [], set()
    for did in MVA_IDS:
        if did in byid:
            chosen.append(byid[did]); seen.add(did)
    for sc, mo in scored:
        if len(chosen) >= n_cols:
            break
        if mo.disease_id not in seen:
            chosen.append(mo); seen.add(mo.disease_id)

    cols = [{"id": mo.disease_id, "gene": mo.gene,
             "bma": resnik_bma(PT, mo.terms, IC, PAR, cache)} for mo in chosen]
    BM = np.array([[bestmatch(t, mo) for mo in chosen] for t in PT])
    COV = np.array([[t in mo.terms for mo in chosen] for t in PT])
    LIT = np.zeros_like(COV)
    for i, t in enumerate(PT):
        if literature_mva1.get(t):
            for j, mo in enumerate(chosen):
                if mo.disease_id == MVA_IDS[0]:
                    LIT[i, j] = True

    names = disease_names()
    for did, short in SHORT.items():
        if did in names:
            names[did] = short + ": " + names[did].split(",")[0]
    return {"terms": PT, "cols": cols, "bestmatch": BM, "covered": COV,
            "literature": LIT, "names": names,
            "ic_terms": {t: IC.get(t, 0.0) for t in PT},
            "term_labels": term_labels, "n_models": len(byid),
            "nephro_index": PT.index("HP:0000121")}


PROBAND = [
    ("HP:0002859", "Rhabdomyosarcoma"),
    ("HP:0004322", "Short stature"),
    ("HP:0001518", "Small for gestational age"),
    ("HP:0001508", "Failure to thrive"),
    ("HP:0001622", "Premature birth"),
    ("HP:0003202", "Skeletal muscle atrophy"),
    ("HP:0000121", "Nephrocalcinosis"),
]
# Literature support in the 31-case MVA1 literature compilation, as already recorded in the
# project. Kept as a BOOLEAN: it is never turned into bits.
LIT_MVA1 = {"HP:0002859": True, "HP:0004322": True, "HP:0001518": True,
            "HP:0001508": True, "HP:0001622": False, "HP:0003202": False,
            "HP:0000121": False}
# Comprobación 2 con su categoría y su cifra, copiadas de docs/PHENOTYPE_RESIDUAL_AUDIT.md
# (compilación publicada de 31 casos etiquetados como MVA1, Pavone et al. 2022). "nq" = no cuantificado: PARKED, no NEGATIVE.
LIT_MVA1_DETAIL = {
    "HP:0002859": ("yes", "direct: RMS among reported" + NL2 + "malignancies (all, 38.7 %)"),
    "HP:0004322": ("yes", "broader: pre/postnatal" + NL2 + "growth retardation 93.5 %"),
    "HP:0001518": ("yes", "broader: pre/postnatal" + NL2 + "growth retardation 93.5 %"),
    "HP:0001508": ("yes", "broader: pre/postnatal" + NL2 + "growth phenotype 93.5 %"),
    "HP:0001622": ("nq", "plausible (perinatal)," + NL2 + "not quantified"),
    "HP:0003202": ("nq", "not quantified"),
    "HP:0000121": ("no", "not reported; generic renal" + NL2 + "dysfunction 12.9 %"),
}


def load_and_build():
    m = prepare([t for t, _ in PROBAND], dict(PROBAND), LIT_MVA1)
    return build(m), m


if __name__ == "__main__":
    fig, m = load_and_build()
    print(S.export(fig, "fig05_hpo_disease_matrix", "DATA", "MEASURED+EXTERNAL+DERIVED"))
