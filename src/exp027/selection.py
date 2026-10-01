"""Selección determinista de los 20 hijos del benchmark (Amendment 3, regla 14)."""
from __future__ import annotations

from .serialize import child_order_key

SUPERPOPULATIONS = ("AFR", "AMR", "EAS", "EUR", "SAS")
PER_SUPERPOPULATION = 4


def select_offspring(trios, per_superpop: int = PER_SUPERPOPULATION):
    """Elige hijos de trios completos, 4 por superpoblación, por SHA256("42:"+sample_id) ascendente.

    trios: iterable de dicts con claves child, father, mother, superpop, complete,
    parents_sequenced. Devuelve (seleccion_por_estrato, estratos_cortos). Si un estrato tiene menos
    de 4 elegibles se toman todos y se reporta.
    """
    eligible = [t for t in trios if t["complete"] and t["parents_sequenced"]]
    chosen, short = {}, []
    for sp in SUPERPOPULATIONS:
        pool = sorted((t for t in eligible if t["superpop"] == sp),
                      key=lambda t: child_order_key(t["child"]))
        chosen[sp] = pool[:per_superpop]
        if len(chosen[sp]) < per_superpop:
            short.append(sp)
    return chosen, short


def first_degree_relatives(target: str, pedigree) -> set[str]:
    """Padres e hijos de target según el pedigrí (lista de (hijo, padre, madre)), y hermanos."""
    rel = set()
    parents = {}
    for kid, fa, mo in pedigree:
        parents[kid] = {p for p in (fa, mo) if p and p != "NA"}
    rel |= parents.get(target, set())
    rel |= {kid for kid, ps in parents.items() if target in ps}
    rel |= {kid for kid, ps in parents.items() if kid != target and ps and ps == parents.get(target)}
    return rel


def conditioning_cohort(phase3_unrelated, target: str | None, pedigree) -> list[str]:
    """C_target = Phase3_2504 \\ ({target} ∪ familiares de primer grado) (Amendment 5, regla 1).

    Para el paciente (target=None) se devuelve la cohorte completa.
    """
    if target is None:
        return list(phase3_unrelated)
    drop = {target} | first_degree_relatives(target, pedigree)
    return [s for s in phase3_unrelated if s not in drop]
