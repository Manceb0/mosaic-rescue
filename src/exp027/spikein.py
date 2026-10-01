"""Spike-in beta-binomial a nivel de conteos (Amendment 3 regla 7; Amendments 5-6).

Solo sobre hets mendelianamente resolubles. El n_i observado se mantiene fijo; únicamente cambia la
probabilidad del alelo paterno verdadero: p = 0.5 + signo·δ, con signo por paridad de rep. Las
lecturas del BAM no se tocan.
"""
from __future__ import annotations

import numpy as np

from .serialize import draw_seed, rep_sign

REPLICATES_BUB1B = 100
REPLICATES_OTHER = 2


def replicates_for(is_bub1b: bool) -> int:
    return REPLICATES_BUB1B if is_bub1b else REPLICATES_OTHER


def paternal_counts(n, delta: float, rep: int, rho, child: str, wid: str) -> np.ndarray:
    """Lecturas del alelo paterno verdadero en cada het, para una réplica.

    Beta-binomial con media p y sobredispersión rho por sitio (Var = n·p(1−p)·(1+(n−1)·rho));
    rho = 0 es el binomial. rho puede ser escalar o un valor por het (su bin de profundidad).
    Sorteo en orden genómico con semilla draw_seed(child, window_id, δ, rep).
    """
    n = np.asarray(n, dtype=np.int64)
    rho = np.broadcast_to(np.asarray(rho, float), n.shape)
    p = 0.5 + rep_sign(rep) * delta
    rng = np.random.default_rng(draw_seed(child, wid, delta, rep))
    pi = np.full(n.shape, p)
    mask = rho > 0
    if mask.any():
        r = rho[mask]
        pi[mask] = rng.beta(p * (1 - r) / r, (1 - p) * (1 - r) / r)
    return rng.binomial(n, pi)


def oriented_h1_counts(n, k_paternal, paternal_allele, h1_allele) -> np.ndarray:
    """Lecturas del alelo que la fase usada coloca en H1.

    Si la fase pone en H1 el alelo paterno, n_H1 = k; si pone el materno, n_H1 = n − k.
    """
    n, k = np.asarray(n), np.asarray(k_paternal)
    same = np.asarray(paternal_allele) == np.asarray(h1_allele)
    return np.where(same, k, n - k)
