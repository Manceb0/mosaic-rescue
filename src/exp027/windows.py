"""Ventanas de EXP-027 (Amendment 3 regla 9; Amendment 4 regla 5; Amendment 8).

Convención: todas las coordenadas en base 1 e inclusivas. Los BED (base 0, semiabiertos) se
convierten al leerlos. Solape = al menos 1 pb en común.
"""
from __future__ import annotations

from bisect import bisect_right

from .serialize import tile_order_key, window_id

TILE_BP = 2_000_000
N_EVALUATION_LATTICE = 49
N_CALIBRATION = 20
BUB1B_WINDOW = ("chr15", 39_191_079, 41_191_078)     # GENCODE v33, punto medio ± 1 Mb
AUTOSOMES = tuple(f"chr{i}" for i in range(1, 23))


def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    """Solape de al menos 1 pb entre intervalos cerrados [start, end]."""
    return a_start <= b_end and b_start <= a_end


class Intervals:
    """Intervalos por cromosoma, base 1 inclusivos, con consulta de solape por bisección."""

    def __init__(self, items=()):
        self._by_chrom: dict[str, list[tuple[int, int]]] = {}
        for chrom, start, end in items:
            self._by_chrom.setdefault(chrom, []).append((int(start), int(end)))
        self._starts = {}
        self._max_end = {}
        for chrom, iv in self._by_chrom.items():
            iv.sort()
            self._starts[chrom] = [s for s, _ in iv]
            running, me = 0, []
            for _, e in iv:
                running = max(running, e)
                me.append(running)
            self._max_end[chrom] = me

    @classmethod
    def from_bed_lines(cls, lines):
        """BED (base 0, semiabierto) -> base 1 inclusivo: [s+1, e]."""
        items = []
        for line in lines:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            f = line.split("\t")
            items.append((f[0], int(f[1]) + 1, int(f[2])))
        return cls(items)

    def hits(self, chrom: str, start: int, end: int) -> bool:
        starts = self._starts.get(chrom)
        if not starts:
            return False
        i = bisect_right(starts, end) - 1        # último intervalo que empieza <= end
        return i >= 0 and self._max_end[chrom][i] >= start


def lattice_tiles(chrom_lengths: dict[str, int], size: int = TILE_BP):
    """Tiles [k·size+1, (k+1)·size] enteras dentro de cada autosoma (k = 0, 1, …)."""
    tiles = []
    for chrom in AUTOSOMES:
        length = chrom_lengths.get(chrom)
        if length is None:
            continue
        k = 0
        while (k + 1) * size <= length:
            tiles.append((chrom, k * size + 1, (k + 1) * size))
            k += 1
    return tiles


def global_order(tiles, tile_exclusions: Intervals, bub1b=BUB1B_WINDOW):
    """Tiles elegibles en orden hash (Amendment 8 r1).

    Solo gaps/centrómeros (tile_exclusions) eliminan una tile, por solape ≥ 1 pb con su núcleo de
    2 Mb; las tiles que solapan la ventana BUB1B quedan fuera para no duplicar la ventana primaria.
    Duplicaciones segmentarias, blacklist y SV ya no entran aquí: son máscaras de sitio (masks.py).
    """
    bchr, bs, be = bub1b
    keep = [t for t in tiles
            if not tile_exclusions.hits(*t)
            and not (t[0] == bchr and overlaps(t[1], t[2], bs, be))]
    return sorted(keep, key=lambda t: tile_order_key(t[0], t[1]))


def evaluation_lattice(order, n: int = N_EVALUATION_LATTICE):
    """Lista global: las 49 primeras del orden hash (las mismas para los 20 hijos)."""
    if len(order) < n:
        raise ValueError(f"solo hay {len(order)} tiles elegibles; hacen falta {n}")
    return list(order[:n])


def evaluation_windows(lattice49, tile_exclusions: Intervals, bub1b=BUB1B_WINDOW):
    """BUB1B (si no solapa gaps/centrómeros) + las 49: las mismas para los 20 hijos (Amendment 8).

    Ninguna máscara de sitio quita ventanas ni las sustituye: la evaluabilidad de cada hijo ×
    ventana la decide Hmin = 50 después de las máscaras.
    """
    out = [] if tile_exclusions.hits(*bub1b) else [bub1b]
    return out + list(lattice49)


def calibration_tiles(order, n_eval: int = N_EVALUATION_LATTICE, n: int = N_CALIBRATION):
    """Las 20 tiles siguientes del orden global tras las 49 de evaluación, comunes a los 20 hijos
    (Amendment 8 r7). Cada hijo aplica dentro sus máscaras de sitio."""
    if len(order) < n_eval + n:
        raise ValueError(f"solo hay {len(order)} tiles elegibles; hacen falta {n_eval + n}")
    return list(order[n_eval:n_eval + n])


def phasing_region(window, buffer_bp: int, chrom_lengths: dict[str, int]):
    """Región de fase de una ventana: ventana ± buffer (250 kb por lado), recortada al cromosoma."""
    chrom, start, end = window
    return chrom, max(1, start - buffer_bp), min(chrom_lengths[chrom], end + buffer_bp)


def wid(window) -> str:
    return window_id(*window)
