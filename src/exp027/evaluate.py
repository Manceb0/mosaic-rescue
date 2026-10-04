"""Evaluación por hijo y ventana, y ensamblado del informe de Phase 1 (EXP-027).

Entrada por ventana (WindowSites): conteos del extractor (n_ref, n_alt), el alelo que la fase
inferida pone en H1, el alelo paterno verdadero (−1 si no es mendelianamente resoluble) y la máscara
de hets analíticos (MAF ≥ 1 %, PASS, GQ ≥ 30, het en el hijo, n ≥ 20). Python puro: no llama a
herramientas externas. Amendment 8: los sitios enmascarados ya no llegan aquí (globales y
copy-changing del hijo) o llegan con paternal = −1 (copy-changing parental); Hmin se aplica después.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import gates, rho as rho_mod, stats
from .serialize import DELTA_GRID, delta_fmt, perm_seed_obs, perm_seed_spike
from .spikein import oriented_h1_counts, paternal_counts, replicates_for

DEPTH_MIN = 20


@dataclass
class WindowSites:
    n_ref: np.ndarray
    n_alt: np.ndarray
    h1_allele: np.ndarray          # 0/1: alelo en H1 según la fase inferida
    paternal: np.ndarray           # 0/1, o −1 si no es resoluble o lo enmascara un SV parental
    analytic: np.ndarray           # bool
    audit: dict | None = None      # recuentos de máscaras de Amendment 8 (masks.window_audit)

    def depth(self) -> np.ndarray:
        return np.asarray(self.n_ref) + np.asarray(self.n_alt)

    def mask(self) -> np.ndarray:
        return np.asarray(self.analytic, bool) & (self.depth() >= DEPTH_MIN)

    def full_audit(self) -> dict:
        """Auditoría de Amendment 8 r10 con los conjuntos finales (tras profundidad): n_after_intact
        es lo que ven APR y A1; n_after_truth, lo que ven potencia y retención. Hmin = 50 se aplica
        sobre estos recuentos; las fracciones son solo descriptivas."""
        m = self.mask()
        out = dict(self.audit or {})
        out["n_after_intact"] = int(m.sum())
        out["n_after_truth"] = int((m & (np.asarray(self.paternal) >= 0)).sum())
        return out


def _h1_counts(n_ref, n_alt, h1_allele):
    return np.where(np.asarray(h1_allele) == 1, n_alt, n_ref)


def intact_eval(s: WindowSites, child: str, wid: str, b: int = stats.B_PERMUTATIONS) -> dict:
    """Datos reales intactos (δ = 0): APR y A1 usan el conjunto analítico completo."""
    m = s.mask()
    n = s.depth()[m]
    if n.size < stats.H_MIN:
        return {"evaluable": False, "n_hets": int(n.size)}
    h1 = _h1_counts(s.n_ref[m], s.n_alt[m], s.h1_allele[m])
    d = stats.deltas(h1, n - h1)
    p = stats.phase_randomized_p(d, perm_seed_obs(child, wid), b)
    return {"evaluable": True, "n_hets": int(n.size), "p": p, "T": stats.t_statistic(d, n),
            "effect": stats.a1_effect(d), "positive": p < stats.ALPHA}


def power_eval(s: WindowSites, child: str, wid: str, is_bub1b: bool, rho_by_depth,
               deltas_grid=DELTA_GRID, b: int = stats.B_PERMUTATIONS) -> dict:
    """Spike-in sobre hets mendelianamente resolubles; mismo conjunto para fase inferida y mendeliana.

    rho_by_depth: función n -> ρ (ρ del bin de profundidad del hijo, ya resuelto con su jerarquía).
    """
    m = s.mask() & (np.asarray(s.paternal) >= 0)
    n = s.depth()[m]
    if n.size < stats.H_MIN:
        return {"evaluable": False, "n_hets": int(n.size)}
    pat, h1 = np.asarray(s.paternal)[m], np.asarray(s.h1_allele)[m]
    rho_i = np.array([rho_by_depth(int(x)) for x in n])
    out_i, out_m = {}, {}
    for delta in deltas_grid:
        key = delta_fmt(delta)
        out_i[key], out_m[key] = [], []
        for rep in range(replicates_for(is_bub1b)):
            k = paternal_counts(n, delta, rep, rho_i, child, wid)
            seed = perm_seed_spike(child, wid, delta, rep)
            n_h1 = oriented_h1_counts(n, k, pat, h1)
            out_i[key].append(stats.phase_randomized_p(stats.deltas(n_h1, n - n_h1), seed, b) < stats.ALPHA)
            out_m[key].append(stats.phase_randomized_p(stats.deltas(k, n - k), seed, b) < stats.ALPHA)
    return {"evaluable": True, "n_hets": int(n.size), "detect_inferred": out_i, "detect_mendel": out_m}


def rho_lookup(table: dict, child: str):
    """Convierte la tabla de rho.rho_table en una función n -> ρ para un hijo."""
    def f(n: int) -> float:
        key = rho_mod.depth_bin(n)
        return table.get((child, key), 0.0)
    return f


def run_benchmark(children: dict, b: int = stats.B_PERMUTATIONS, deltas_grid=DELTA_GRID) -> dict:
    """children = {hijo: {"superpop", "ser", "calibration": (b, n),
                          "windows": {window_id: (WindowSites, is_bub1b)}}}

    Devuelve el informe de gates.phase1_report más los resultados por hijo.
    """
    table, source = rho_mod.rho_table({c: k["calibration"] for c, k in children.items()})
    results = {"children": {}}
    for child, k in children.items():
        f = rho_lookup(table, child)
        wins = {}
        for wid, (sites, is_bub1b) in k["windows"].items():
            ie = intact_eval(sites, child, wid, b)
            pe = power_eval(sites, child, wid, is_bub1b, f, deltas_grid, b)
            wins[wid] = {
                "is_bub1b": is_bub1b,
                "apr_evaluable": ie["evaluable"], "apr_positive": bool(ie.get("positive", False)),
                "power_evaluable": pe["evaluable"],
                "detect_inferred": pe.get("detect_inferred", {}),
                "detect_mendel": pe.get("detect_mendel", {}),
                "audit": sites.full_audit(),
            }
        results["children"][child] = {"superpop": k["superpop"], "ser": k.get("ser"),
                                       "ser_scaffold": k.get("ser_scaffold"), "windows": wins}
    report = gates.phase1_report(results)
    report["rho_source"] = {f"{c}|{b_[0]}-{b_[1]}": s for (c, b_), s in source.items()}
    return {"report": report, "results": results}
