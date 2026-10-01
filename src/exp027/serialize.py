"""Serialización congelada de EXP-027 (config/exp027_benchmark.yaml, implementation_decisions).

Toda cadena que entra en un hash se construye aquí y solo aquí, para que el orden de los hijos, el
orden de las tiles, las semillas de sorteo y el signo del spike-in sean reproducibles bit a bit.
"""
from __future__ import annotations

import hashlib

SEED = 42
DELTA_GRID = (0.00, 0.02, 0.05, 0.10, 0.15, 0.20)


def sha256_hex(text: str) -> str:
    """SHA-256 hexadecimal de una cadena ASCII, sin espacios ni relleno."""
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def child_order_key(sample_id: str) -> str:
    """Orden de selección de hijos: SHA256("42:" + sample_id), hex ascendente."""
    return sha256_hex(f"{SEED}:{sample_id}")


def tile_order_key(chrom: str, start: int) -> str:
    """Orden de tiles: SHA256("42:" + chr + ":" + start), con chr = "chrN" y start en base 1."""
    if not chrom.startswith("chr"):
        raise ValueError(f"chrom debe tener la forma chrN, no {chrom!r}")
    return sha256_hex(f"{SEED}:{chrom}:{int(start)}")


def window_id(chrom: str, start: int, end: int) -> str:
    """Identificador de ventana: "chrN:start-end", GRCh38, base 1, inclusiva."""
    if not chrom.startswith("chr"):
        raise ValueError(f"chrom debe tener la forma chrN, no {chrom!r}")
    return f"{chrom}:{int(start)}-{int(end)}"


def delta_fmt(delta: float) -> str:
    """δ siempre con dos decimales ("0.10"); solo valores de la rejilla congelada."""
    s = f"{delta:.2f}"
    if s not in {f"{d:.2f}" for d in DELTA_GRID}:
        raise ValueError(f"δ fuera de la rejilla congelada: {delta}")
    return s


def draw_seed(child: str, wid: str, delta: float, rep: int) -> int:
    """Semilla del sorteo de una réplica: int(SHA256("42:draw:"+child+":"+window_id+":"+δ+":"+rep)[:16], 16)."""
    if rep < 0:
        raise ValueError("rep es 0-based y no negativo")
    return int(sha256_hex(f"{SEED}:draw:{child}:{wid}:{delta_fmt(delta)}:{int(rep)}")[:16], 16)


def perm_seed_obs(child: str, wid: str) -> int:
    """Semilla del null de fase aleatorizada con datos intactos: SHA256("42:perm:OBS:"+child+":"+window_id).

    Separada de las de spike-in para no confundir datos intactos con δ = 0.00 (Amendment 7). La
    semilla inicializa el RNG y de él salen las B permutaciones; no se hashea cada permutación.
    """
    return int(sha256_hex(f"{SEED}:perm:OBS:{child}:{wid}")[:16], 16)


def perm_seed_spike(child: str, wid: str, delta: float, rep: int) -> int:
    """Semilla del null con spike-in: SHA256("42:perm:SPIKE:"+child+":"+window_id+":"+δ+":"+rep)."""
    if rep < 0:
        raise ValueError("rep es 0-based y no negativo")
    return int(sha256_hex(f"{SEED}:perm:SPIKE:{child}:{wid}:{delta_fmt(delta)}:{int(rep)}")[:16], 16)


def rep_sign(rep: int) -> int:
    """Signo del spike-in solo por paridad de rep: par = +δ, impar = −δ (Amendment 6, regla 1)."""
    return 1 if int(rep) % 2 == 0 else -1
