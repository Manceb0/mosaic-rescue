"""Estadístico de ventana, null de fase aleatorizada, efecto y clases de A1 (contrato; Amendments 3-6).

delta_i = b_i - 0.5, con b_i = n del alelo en H1 / (n_H1 + n_H2), H1 según la fase usada.
T = sum(delta_i) / sqrt(sum(0.25 / n_i)).
p = (1 + #{|T_perm| >= |T_obs|}) / (B + 1), con B permutaciones que invierten el signo de cada
delta_i con probabilidad 0.5 (el denominador de T no cambia con los signos).
"""
from __future__ import annotations

import numpy as np

B_PERMUTATIONS = 10_000
ALPHA = 0.05
DELTA_STAR = 0.10
H_MIN = 50
_PERM_CHUNK = 1_000


def deltas(n_h1, n_h2) -> np.ndarray:
    n_h1 = np.asarray(n_h1, float)
    n = n_h1 + np.asarray(n_h2, float)
    return n_h1 / n - 0.5


def t_statistic(delta, n) -> float:
    delta, n = np.asarray(delta, float), np.asarray(n, float)
    return float(delta.sum() / np.sqrt((0.25 / n).sum()))


def phase_randomized_p(delta, seed: int, b: int = B_PERMUTATIONS) -> float:
    """p empírica bilateral de T bajo aleatorización de fase (signos ±1 independientes)."""
    delta = np.asarray(delta, float)
    obs = abs(delta.sum())
    rng = np.random.default_rng(seed)
    exceed, done = 0, 0
    tol = 1e-12 * max(1.0, obs)
    while done < b:
        m = min(_PERM_CHUNK, b - done)
        signs = rng.integers(0, 2, size=(m, delta.size), dtype=np.int8) * 2 - 1
        exceed += int((np.abs(signs @ delta) >= obs - tol).sum())
        done += m
    return (1 + exceed) / (b + 1)


def a1_effect(delta) -> float:
    """|delta_hat| = abs(mean(delta_i)) con delta_i orientado por la fase inferida.

    No es mean(abs(delta_i)), que mediría dispersión y no desequilibrio coherente.
    """
    return float(abs(np.mean(np.asarray(delta, float))))


NO_EVIDENCE = "NO_EVIDENCE"
SUGGESTIVE = "SUGGESTIVE"
CONSISTENT = "CONSISTENT_WITH_HAPLOTYPE_SPECIFIC_ALLELIC_IMBALANCE"
NOT_EVALUABLE = "NOT_EVALUABLE"


def a1_class(p: float, effect: float, n_hets: int, cnv_overlap: bool,
             alpha: float = ALPHA, delta_star: float = DELTA_STAR, h_min: int = H_MIN) -> str:
    """Clase de A1 para la ventana primaria (m = 1, p empírica sin BH).

    Precedencia por especificidad (pendiente de confirmación del líder): el texto del contrato
    solapa NO_EVIDENCE («p ≥ 0.05 o |efecto| < δ*») con SUGGESTIVE («p < 0.05 pero |efecto| < δ*»).
    Se aplica la lectura en la que todas las cláusulas tienen contenido:
    p ≥ α -> NO_EVIDENCE; p < α y efecto < δ* -> SUGGESTIVE; p < α y efecto ≥ δ* -> CONSISTENT.
    """
    if cnv_overlap or n_hets < h_min:
        return NOT_EVALUABLE
    if p >= alpha:
        return NO_EVIDENCE
    return CONSISTENT if effect >= delta_star else SUGGESTIVE
