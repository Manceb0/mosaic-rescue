"""Sobredispersión ρ del spike-in (Amendment 4 regla 4; Amendment 5 regla 5).

ρ̂ = max(0, (mean((b_i − 0.5)²·n_i/0.25) − 1) / (mean(n_i) − 1)), por bin de profundidad, con datos
reales intactos de las tiles de calibración. Jerarquía: ρ(hijo, bin) si el bin tiene ≥ 200 hets;
si no, ρ_global(bin) de los 20 hijos; si no, ρ_global(todos). Nunca ventanas de evaluación.
"""
from __future__ import annotations

import numpy as np

DEPTH_BINS = ((20, 30), (30, 40), (40, 60), (60, None))
MIN_HETS = 200


def depth_bin(n: int):
    for lo, hi in DEPTH_BINS:
        if n >= lo and (hi is None or n < hi):
            return (lo, hi)
    return None


def rho_hat(b, n) -> float:
    b, n = np.asarray(b, float), np.asarray(n, float)
    if b.size == 0 or n.mean() <= 1:
        return 0.0
    return float(max(0.0, (np.mean((b - 0.5) ** 2 * n / 0.25) - 1.0) / (n.mean() - 1.0)))


def _by_bin(b, n):
    out = {}
    for bi, ni in zip(b, n):
        key = depth_bin(int(ni))
        if key is not None:
            out.setdefault(key, ([], []))
            out[key][0].append(bi)
            out[key][1].append(ni)
    return out


def rho_table(calibration_by_child: dict[str, tuple]):
    """calibration_by_child: {hijo: (b, n)} con hets analíticos intactos de calibración.

    Devuelve ({(hijo, bin): ρ}, {(hijo, bin): origen}) con origen en
    {"child_bin", "global_bin", "global_all"}.
    """
    per_child = {c: _by_bin(*bn) for c, bn in calibration_by_child.items()}
    pooled_bin = {}
    all_b, all_n = [], []
    for bins in per_child.values():
        for key, (bb, nn) in bins.items():
            pooled_bin.setdefault(key, ([], []))
            pooled_bin[key][0].extend(bb)
            pooled_bin[key][1].extend(nn)
            all_b.extend(bb)
            all_n.extend(nn)
    rho_all = rho_hat(all_b, all_n)
    table, source = {}, {}
    for c, bins in per_child.items():
        for key in DEPTH_BINS:
            bb, nn = bins.get(key, ([], []))
            if len(bb) >= MIN_HETS:
                table[(c, key)], source[(c, key)] = rho_hat(bb, nn), "child_bin"
            elif len(pooled_bin.get(key, ([], []))[0]) >= MIN_HETS:
                table[(c, key)], source[(c, key)] = rho_hat(*pooled_bin[key]), "global_bin"
            else:
                table[(c, key)], source[(c, key)] = rho_all, "global_all"
    return table, source
