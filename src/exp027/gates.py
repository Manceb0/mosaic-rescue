"""Puertas de Phase 1 y aplicabilidad de A1 (Amendment 3 regla 10; Amendment 5 regla 3; Amendment 6).

Ponderación (Amendment 6): sensibilidad y retención por hijo (media de sus ventanas; cada ventana =
fracción detectada entre sus réplicas) y después media con peso igual entre hijos. SER: media con
peso igual de los SER por hijo (marcadores analíticos MAF ≥ 1 %; el SER del scaffold es solo
descriptivo). APR (Amendment 7): K positivos con datos intactos sobre N pares hijo × ventana
evaluables; FAIL solo si el test binomial exacto unilateral contra 0.05 da p < 0.05. Es un centinela
operativo de calibración, no un FPR biológico: el binomial presupone independencia aproximada.
"""
from __future__ import annotations

from math import comb

from .selection import SUPERPOPULATIONS

APR_P0 = 0.05
APR_ALPHA = 0.05
SENS_MIN = 0.80
RETENTION_MIN = 0.90
SER_MAX = 0.02
STRATUM_SER_MAX = 0.04
LOCUS_CHILDREN_MIN = 15
LOCUS_STRATA_MIN = 4
SENTINEL_P0 = 0.05
SENTINEL_ALPHA = 0.05
DELTA_GATE = "0.10"


def binomial_upper_tail(k: int, n: int, p: float = SENTINEL_P0) -> float:
    """P(X ≥ k) para X ~ Binomial(n, p)."""
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(max(k, 0), n + 1))


def sentinel_veto(positives: int, n_eligible: int) -> bool:
    """Centinela técnico de BUB1B: exceso significativo de positivos con datos intactos."""
    return binomial_upper_tail(positives, n_eligible) < SENTINEL_ALPHA


def sentinel_critical_count(n_eligible: int) -> int:
    return next(k for k in range(n_eligible + 2) if binomial_upper_tail(k, n_eligible) < SENTINEL_ALPHA)


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def _child_sensitivity(windows: dict, key: str, only_bub1b: bool = False):
    """Media, sobre las ventanas evaluables del hijo, de la fracción detectada a δ = 0.10.

    Global: todas sus ventanas (BUB1B pesa como una más). Locus: solo la ventana BUB1B.
    """
    vals = [_mean(w[key][DELTA_GATE]) for w in windows.values()
            if w["power_evaluable"] and (w["is_bub1b"] if only_bub1b else True)]
    return _mean(vals)


def phase1_report(results: dict) -> dict:
    """Informe PASS/FAIL de Phase 1 y aplicabilidad de A1 a partir de los resultados por hijo.

    results = {"children": {hijo: {"superpop", "ser", "windows": {window_id: {
        "is_bub1b", "apr_evaluable", "apr_positive", "power_evaluable",
        "detect_inferred": {δ: [bool]}, "detect_mendel": {δ: [bool]}}}}}}
    """
    kids = results["children"]
    reasons = []

    apr_pairs = [w["apr_positive"] for k in kids.values() for w in k["windows"].values()
                 if w["apr_evaluable"]]
    apr_k, apr_n = sum(apr_pairs), len(apr_pairs)
    apr = apr_k / apr_n if apr_n else None
    apr_p = binomial_upper_tail(apr_k, apr_n, APR_P0) if apr_n else None

    sens_i = {c: _child_sensitivity(k["windows"], "detect_inferred") for c, k in kids.items()}
    sens_m = {c: _child_sensitivity(k["windows"], "detect_mendel") for c, k in kids.items()}
    sens_inferred = _mean(v for v in sens_i.values() if v is not None)
    sens_mendel = _mean(v for v in sens_m.values() if v is not None)
    retention = (sens_inferred / sens_mendel) if sens_mendel else None
    ser = _mean(k["ser"] for k in kids.values() if k.get("ser") is not None)

    strata = {}
    for sp in SUPERPOPULATIONS:
        members = [c for c, k in kids.items() if k["superpop"] == sp]
        s_ser = _mean(kids[c]["ser"] for c in members if kids[c].get("ser") is not None)
        s_sens = _mean(sens_i[c] for c in members if sens_i[c] is not None)
        veto = (s_ser is not None and s_ser > STRATUM_SER_MAX) or (s_sens is not None and s_sens < SENS_MIN)
        strata[sp] = {"ser": s_ser, "sensitivity": s_sens, "veto": veto}

    checks = {
        "apr_calibration": apr_p is not None and apr_p >= APR_ALPHA,
        "sensitivity": sens_inferred is not None and sens_inferred >= SENS_MIN,
        "retention": retention is not None and retention >= RETENTION_MIN,
        "ser": ser is not None and ser <= SER_MAX,
        "no_stratum_veto": not any(s["veto"] for s in strata.values()),
    }
    reasons += [f"global:{k}" for k, ok in checks.items() if not ok]
    global_pass = all(checks.values())

    # Locus BUB1B
    locus_kids = [c for c, k in kids.items()
                  if any(w["is_bub1b"] and w["power_evaluable"] for w in k["windows"].values())]
    n_e = len(locus_kids)
    strata_e = len({kids[c]["superpop"] for c in locus_kids})
    per_superpop = {sp: sum(1 for c in locus_kids if kids[c]["superpop"] == sp) for sp in SUPERPOPULATIONS}
    li = {c: _child_sensitivity(kids[c]["windows"], "detect_inferred", only_bub1b=True) for c in locus_kids}
    lm = {c: _child_sensitivity(kids[c]["windows"], "detect_mendel", only_bub1b=True) for c in locus_kids}
    locus_sens = _mean(li.values())
    locus_sens_m = _mean(lm.values())
    locus_retention = (locus_sens / locus_sens_m) if locus_sens_m else None
    positives = sum(1 for c in locus_kids for w in kids[c]["windows"].values()
                    if w["is_bub1b"] and w["apr_evaluable"] and w["apr_positive"])
    locus = {
        "evaluable_children": n_e,
        "evaluable_strata": strata_e,
        "evaluable_by_superpop": per_superpop,
        "sensitivity": locus_sens,
        "retention": locus_retention,
        "sentinel_positives": positives,
        "sentinel_critical": sentinel_critical_count(n_e) if n_e else None,
        "sentinel_veto": sentinel_veto(positives, n_e) if n_e else False,
    }
    locus_checks = {
        "evaluable": n_e >= LOCUS_CHILDREN_MIN and strata_e >= LOCUS_STRATA_MIN,
        "sensitivity": locus_sens is not None and locus_sens >= SENS_MIN,
        "retention": locus_retention is not None and locus_retention >= RETENTION_MIN,
        "no_sentinel_veto": not locus["sentinel_veto"],
    }
    reasons += [f"bub1b:{k}" for k, ok in locus_checks.items() if not ok]

    return {
        "phase1_global": "PASS" if global_pass else "FAIL",
        "a1_applicable": global_pass and all(locus_checks.values()),
        "apr": apr, "apr_k": apr_k, "apr_n": apr_n, "apr_p_binom_one_sided": apr_p,
        "apr_pairs": apr_n,
        "ser_scaffold_descriptive": _mean(k["ser_scaffold"] for k in kids.values()
                                          if k.get("ser_scaffold") is not None),
        "sensitivity_inferred": sens_inferred, "sensitivity_mendelian": sens_mendel,
        "retention": retention, "ser": ser, "strata": strata,
        "locus_bub1b": locus, "fail_reasons": reasons,
    }
