"""Verdad mendeliana por het del hijo (Amendment 3 regla 2; Amendment 5 regla 2).

Un het del hijo tiene orientación paterna resoluble solo si el trio es mendelianamente consistente
y al menos un progenitor es homocigoto. Los hets con ambos progenitores heterocigotos, con
inconsistencia mendeliana o con de novo putativo devuelven None y no entran en la verdad.
Genotipos como tuplas no faseadas de alelos 0/1, p. ej. (0, 1).
"""
from __future__ import annotations


def _alleles(gt):
    if gt is None or len(gt) != 2 or any(a not in (0, 1) for a in gt):
        return None
    return tuple(sorted(gt))


def paternal_allele(child_gt, father_gt, mother_gt):
    """Alelo (0 o 1) heredado del padre en un het del hijo, o None si no es resoluble."""
    c, f, m = _alleles(child_gt), _alleles(father_gt), _alleles(mother_gt)
    if None in (c, f, m) or c != (0, 1):
        return None
    candidates = set()
    for pa in set(f):
        ma = 1 - pa                                  # el hijo es 0/1: el materno es el otro
        if ma in m:
            candidates.add(pa)
    return candidates.pop() if len(candidates) == 1 else None
