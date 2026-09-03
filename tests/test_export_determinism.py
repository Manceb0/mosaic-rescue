#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La exportacion de figuras es determinista y declara sus dos ejes.

Ningun dato del paciente: las figuras de prueba se construyen con numeros
inventados aqui mismo.

POR QUE EXISTE ESTA SUITE
    Regenerar las figuras sin cambiar una linea de codigo producia nueve SVG
    distintos. Matplotlib deriva los `id=` de clipPaths y glifos de un salt
    ALEATORIO por proceso, y ademas escribe la fecha de creacion dentro del
    fichero. El PNG no sufre ninguna de las dos cosas, asi que el problema
    pasaba desapercibido hasta que alguien miraba `git diff` y veia nueve
    ficheros cambiados sin motivo.

    Un diff que cambia sin que cambie nada destruye la unica senal util que da
    el control de versiones sobre una figura.
"""
import io, pathlib, re, sys, hashlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.figures import style as S                                      # noqa: E402


def _figura_de_prueba():
    """Una figura pequena, con datos inventados, que ejercita el mismo export."""
    fig, ax = plt.subplots(figsize=(3.2, 2.2))
    ax.plot([0, 1, 2, 3], [0.0, 0.4, 0.1, 0.9], marker="o", color=S.BLUE)
    ax.set_xlabel("x (unidades arbitrarias)")
    ax.set_ylabel("y (unidades arbitrarias)")
    S.panel(ax, "A")
    return fig


def _exportar(tmp_path, slug):
    """Exporta a un directorio temporal, sin tocar figures/pub."""
    full, thumb = S.FULL_DIR, S.THUMB_DIR
    S.FULL_DIR = str(tmp_path / "pub")
    S.THUMB_DIR = str(tmp_path / "pub" / "thumb")
    try:
        out = S.export(_figura_de_prueba(), slug, "SIMULATION", "SIMULATED")
        svg = io.open(out["svg"], encoding="utf-8").read()
        png = io.open(out["png"], "rb").read()
        return out, svg, png
    finally:
        S.FULL_DIR, S.THUMB_DIR = full, thumb
        plt.close("all")


# ─────────── 1-3 · determinismo ───────────

def test_01_dos_exportaciones_dan_el_mismo_svg_byte_a_byte(tmp_path):
    _o1, svg1, _p1 = _exportar(tmp_path / "a", "det")
    _o2, svg2, _p2 = _exportar(tmp_path / "b", "det")
    assert hashlib.sha256(svg1.encode()).hexdigest() == \
           hashlib.sha256(svg2.encode()).hexdigest(), (
        "dos renderizados identicos han producido SVG distintos: "
        "revisa svg.hashsalt y metadata Date")


def test_02_el_svg_no_lleva_fecha_embebida(tmp_path):
    _o, svg, _p = _exportar(tmp_path, "sinfecha")
    assert "<dc:date>" not in svg, (
        "el SVG lleva la fecha de creacion: cada render produciria un fichero distinto")


def test_03_el_svg_no_tiene_espacios_al_final_de_linea(tmp_path):
    """`git diff --check` los marca y un fichero generado no deberia provocarlos."""
    _o, svg, _p = _exportar(tmp_path, "sinespacios")
    malas = [n for n, l in enumerate(svg.split(chr(10)), 1) if l != l.rstrip()]
    assert not malas, f"lineas con espacio final en el SVG: {malas[:10]}"


# ─────────── 4-5 · el salt esta fijado, y el PNG tambien es estable ───────────

def test_04_el_hashsalt_esta_fijado():
    assert matplotlib.rcParams.get("svg.hashsalt"), (
        "svg.hashsalt sin fijar: los id= del SVG serian aleatorios por proceso")


def test_05_dos_exportaciones_dan_el_mismo_png(tmp_path):
    _o1, _s1, png1 = _exportar(tmp_path / "a", "detpng")
    _o2, _s2, png2 = _exportar(tmp_path / "b", "detpng")
    assert png1 == png2, "el PNG no es reproducible entre ejecuciones"


# ─────────── 6-9 · los dos ejes de metadatos ───────────

def test_06_no_se_puede_exportar_sin_declarar_los_dos_ejes(tmp_path):
    with pytest.raises(TypeError):
        S.export(_figura_de_prueba(), "sinejes")           # faltan class y origin
    plt.close("all")


def test_07_una_clase_inventada_es_rechazada():
    with pytest.raises(AssertionError):
        S.check("DASHBOARD", "MEASURED")


def test_08_un_origen_inventado_es_rechazado():
    with pytest.raises(AssertionError):
        S.check("DATA", "VIBES")


def test_09_los_dos_ejes_aparecen_en_el_svg(tmp_path):
    _o, svg, _p = _exportar(tmp_path, "ejes")
    assert "Figure class" in svg and "Evidence origin" in svg, (
        "la figura exportada no lleva estampados sus dos ejes de metadatos")


# ─────────── 10 · la clase cientifica es un subconjunto declarado ───────────

def test_10_las_clases_cientificas_son_subconjunto_de_todas():
    assert set(S.SCIENTIFIC_CLASS) < set(S.FIGURE_CLASS)
    assert "SYNTHESIS" not in S.SCIENTIFIC_CLASS
    assert "NARRATIVE" not in S.SCIENTIFIC_CLASS
