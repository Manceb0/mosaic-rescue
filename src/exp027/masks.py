"""Máscaras de sitio de EXP-027 (Amendment 8).

Las duplicaciones segmentarias, la ENCODE blacklist v2, los gaps/centrómeros y los SV copy-changing
ya no eliminan ventanas: retiran marcadores. Un marcador se enmascara si su span VCF
[POS, POS + len(REF) − 1] interseca la pista (≥ 1 pb). Ninguna fracción enmascarada es una puerta;
la evaluabilidad la decide Hmin = 50 después de las máscaras.

Dónde actúa cada máscara (Amendment 8 r3-r5):
  global (gaps/centrómeros, segdups, blacklist) -> input de fase y todos los conjuntos;
  copy-changing del hijo -> input de fase, APR, A1-benchmark, potencia, calibración (ρ) y SER;
  copy-changing de padre/madre -> solo verdad mendeliana, potencia y SER (no APR ni ρ).
El paciente no usa máscaras de CNV: un CNV copy-changing que solape su ventana de A1 la deja
NOT_EVALUABLE (Amendment 8 r9, sin cambios respecto al contrato).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .windows import Intervals, overlaps

COPY_CHANGING_TYPES = frozenset({"DEL", "DUP", "CNV"})
COPY_NEUTRAL_TYPES = frozenset({"INS", "INV", "BND", "CTX"})
DIPLOID = 2


def marker_span(pos: int, ref: str) -> tuple[int, int]:
    """Span VCF de un marcador: [POS, POS + len(REF) − 1] (base 1, inclusivo)."""
    return int(pos), int(pos) + max(len(ref), 1) - 1


def _carries(gt: str) -> bool:
    return any(a not in ("0", ".", "") for a in gt.replace("|", "/").split("/"))


def explicit_copy_number(values: dict) -> int | None:
    """Copy number explícito del callset: FORMAT/CN si existe y es numérico; si no, FORMAT/RD_CN.

    Los valores no enteros (estimaciones de profundidad) se redondean al entero más próximo; "." o
    ausente -> None.
    """
    for key in ("CN", "RD_CN"):
        raw = values.get(key)
        if raw in (None, "", "."):
            continue
        try:
            return int(round(float(raw.split(",")[0])))
        except ValueError:
            continue
    return None


def sample_copy_changing(svtype: str, fmt_keys: list[str], sample_field: str) -> bool:
    """¿Este registro SV es copy-changing en esta muestra? (Amendment 8 r4).

    DEL/DUP/CNV (con subtipos, p. ej. DEL:ME, DUP:TANDEM): portador por GT no referencia, o copy
    number explícito distinto de 2. INS/INV/BND/CTX: copy-neutral, nunca. Otros tipos (CPX): solo si la
    muestra es portadora y el callset da un copy number explícito distinto de 2.
    """
    base = svtype.split(":")[0]
    values = dict(zip(fmt_keys, sample_field.split(":")))
    carrier = _carries(values.get("GT", "."))
    cn = explicit_copy_number(values)
    if base in COPY_NEUTRAL_TYPES:
        return False
    if base in COPY_CHANGING_TYPES:
        return carrier or (cn is not None and cn != DIPLOID)
    return carrier and cn is not None and cn != DIPLOID


def merged(items) -> dict[str, list[tuple[int, int]]]:
    by: dict[str, list[list[int]]] = {}
    for chrom, s, e in items:
        by.setdefault(chrom, []).append([int(s), int(e)])
    out = {}
    for chrom, iv in by.items():
        iv.sort()
        m: list[list[int]] = []
        for s, e in iv:
            if m and s <= m[-1][1] + 1:
                m[-1][1] = max(m[-1][1], e)
            else:
                m.append([s, e])
        out[chrom] = [(s, e) for s, e in m]
    return out


def covered_fraction(items, window) -> float:
    """Fracción de bases de la ventana cubierta por la unión de intervalos (solo descriptiva)."""
    chrom, ws, we = window
    bp = sum(max(0, min(e, we) - max(s, ws) + 1) for s, e in merged(items).get(chrom, []))
    return bp / (we - ws + 1)


@dataclass
class SiteMasks:
    """Máscaras de un hijo: pistas globales + sus SV copy-changing + los de sus padres."""
    gaps: list = field(default_factory=list)
    segdup: list = field(default_factory=list)
    blacklist: list = field(default_factory=list)
    child_cc: list = field(default_factory=list)
    parent_cc: list = field(default_factory=list)

    def __post_init__(self):
        self._iv = {k: Intervals(getattr(self, k)) for k in
                    ("gaps", "segdup", "blacklist", "child_cc", "parent_cc")}

    def flags(self, chrom: str, pos: int, ref: str) -> dict[str, bool]:
        s, e = marker_span(pos, ref)
        return {k: iv.hits(chrom, s, e) for k, iv in self._iv.items()}

    def phasing_intervals(self) -> list:
        """Lo que se retira del input de fase del objetivo: global + copy-changing del hijo."""
        return self.gaps + self.segdup + self.blacklist + self.child_cc

    def truth_intervals(self) -> list:
        """Lo que se retira del conjunto de verdad (verdad mendeliana, potencia, SER)."""
        return self.phasing_intervals() + self.parent_cc


def intact_excluded(f: dict[str, bool]) -> bool:
    """Fuera de APR, A1-benchmark, potencia y calibración: global o copy-changing del hijo."""
    return f["gaps"] or f["segdup"] or f["blacklist"] or f["child_cc"]


def truth_excluded(f: dict[str, bool]) -> bool:
    return intact_excluded(f) or f["parent_cc"]


def window_audit(chrom: str, candidates, masks: SiteMasks, window) -> tuple[set, set, dict]:
    """Clasifica los hets analíticos candidatos de una ventana (antes de AD y de la profundidad).

    candidates: iterable de (pos, ref). Devuelve (posiciones que entran en el conjunto intacto,
    posiciones del conjunto intacto que salen de la verdad mendeliana, auditoría parcial). Los
    recuentos por pista no son excluyentes: un sitio puede caer en varias.
    """
    keep, no_truth = set(), set()
    audit = {"n_before": 0, "n_mask_gaps": 0, "n_mask_segdup": 0, "n_mask_blacklist": 0,
             "n_mask_child_copychange": 0, "n_mask_parent_copychange_truth": 0}
    for pos, ref in candidates:
        f = masks.flags(chrom, pos, ref)
        audit["n_before"] += 1
        audit["n_mask_gaps"] += f["gaps"]
        audit["n_mask_segdup"] += f["segdup"]
        audit["n_mask_blacklist"] += f["blacklist"]
        audit["n_mask_child_copychange"] += f["child_cc"]
        if intact_excluded(f):
            continue
        keep.add(pos)
        if f["parent_cc"]:
            audit["n_mask_parent_copychange_truth"] += 1
            no_truth.add(pos)
    audit["masked_bp_fraction_intact"] = covered_fraction(masks.phasing_intervals(), window)
    audit["masked_bp_fraction_truth"] = covered_fraction(masks.truth_intervals(), window)
    return keep, no_truth, audit


def patient_window_blocked(patient_cnv, window) -> bool:
    """Salvaguarda de A1 (sin cambios): un CNV copy-changing del paciente que solape la ventana con
    ≥ 1 pb la deja NOT_EVALUABLE. No es una máscara: no se retiran sitios para salvar la ventana."""
    chrom, ws, we = window
    return any(c == chrom and overlaps(s, e, ws, we) for c, s, e in patient_cnv)


def bed_lines(items, chrom: str | None = None) -> list[str]:
    """Intervalos base 1 inclusivos -> BED (base 0, semiabierto), fusionados y ordenados."""
    out = []
    for c, iv in sorted(merged(items).items()):
        if chrom is not None and c != chrom:
            continue
        out += [f"{c}\t{s - 1}\t{e}" for s, e in iv]
    return out
