#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Invariantes de la puntuacion genome-wide.

TODOS LOS DATOS SON SINTETICOS. Ninguna prueba toca el genoma del paciente, de
modo que esta suite corre al clonar el repositorio y en el CI.

Lo que se fija aqui no es el RESULTADO del ranking, es su COMPORTAMIENTO. Un
resultado se puede reproducir mirando el pickle; un comportamiento hay que
protegerlo, porque es lo que se rompe al tocar los pesos.

Invariantes:
  1-3   el ranking no conoce ningun gen: es simetrico ante el nombre
  4-6   un modelo de herencia COMPLETO puntua por encima de uno incompleto
  7-8   los filtros de rareza y calidad excluyen, no reordenan
  9-10  hemicigosis en varon es modelo completo, no media evidencia
  11    determinismo: mismas entradas, mismo orden
"""
import pathlib, sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.prioritization.genome_wide import Variant, rank, is_hemizygous  # noqa: E402


def V(gene, loc="1:1000-1000", gt="0/1", impact="HIGH",
      consequence="stop_gained", max_af=None, dp=40, gq=99, ad="20,20",
      filt="PASS", allele="T", canonical=True, mane="NM_000001.1"):
    """Variante sintetica con valores por defecto que pasan calidad."""
    return Variant(loc=loc, gene=gene, consequence=consequence, impact=impact,
                   max_af=max_af, sift="", polyphen="", clinsig="", hgvsp="",
                   canonical=canonical, mane=mane, allele=allele, gt=gt,
                   dp=dp, gq=gq, ad=ad, filt=filt)


def _score(calls, gene):
    """rank() devuelve GeneCall (dataclass), no tuplas."""
    for c in calls:
        if c.gene == gene:
            return c.score
    return None


# ─────────── 1-3 · el ranking no conoce ningun gen ───────────

def test_01_el_nombre_del_gen_no_altera_la_puntuacion():
    """Si renombrar un gen cambia su score, hay un prior escondido."""
    a = rank([V("BUB1B", loc="15:1000-1000", gt="1/1")])
    b = rank([V("GEN_INVENTADO", loc="15:1000-1000", gt="1/1")])
    assert _score(a, "BUB1B") == _score(b, "GEN_INVENTADO")


def test_02_ningun_gen_del_caso_recibe_trato_especial():
    for g in ("BUB1B", "CEP57", "TRIP13", "FANCD2", "LZTR1", "IGBP1"):
        got = _score(rank([V(g, loc="15:1000-1000", gt="1/1")]), g)
        base = _score(rank([V("ZZZZ", loc="15:1000-1000", gt="1/1")]), "ZZZZ")
        assert got == base, f"{g} puntua distinto que un gen anonimo identico"


def test_03_el_orden_de_entrada_no_cambia_el_resultado():
    vs = [V("A", loc="1:100-100", gt="1/1"),
          V("B", loc="2:200-200", gt="0/1"),
          V("C", loc="3:300-300", gt="0/1", impact="MODERATE",
            consequence="missense_variant")]
    uno = {c.gene: c.score for c in rank(vs)}
    otro = {c.gene: c.score for c in rank(list(reversed(vs)))}
    assert uno == otro


# ─────────── 4-6 · modelo completo por encima de modelo incompleto ───────────

def test_04_homocigoto_puntua_por_encima_de_un_solo_heterocigoto():
    hom = _score(rank([V("HOM", loc="1:100-100", gt="1/1")]), "HOM")
    het = _score(rank([V("HET", loc="2:200-200", gt="0/1")]), "HET")
    assert hom > het, "un modelo recesivo completo debe superar a un solo alelo"


def test_05_dos_alelos_heterocigotos_superan_a_uno_solo():
    """Compound-het candidato es mas que un alelo suelto, aunque falte la fase."""
    dos = rank([V("DOS", loc="1:100-100", gt="0/1", allele="T"),
                V("DOS", loc="1:900-900", gt="0/1", allele="G")])
    uno = rank([V("UNO", loc="2:100-100", gt="0/1", allele="T")])
    assert _score(dos, "DOS") > _score(uno, "UNO")


def test_06_high_no_puntua_por_debajo_de_moderate():
    high = _score(rank([V("H", loc="1:100-100", gt="1/1", impact="HIGH")]), "H")
    mod = _score(rank([V("M", loc="2:200-200", gt="1/1", impact="MODERATE",
                         consequence="missense_variant")]), "M")
    assert high >= mod


# ─────────── 7-8 · los filtros excluyen, no reordenan ───────────

def test_07_una_variante_comun_no_entra_en_el_ranking():
    calls = rank([V("COMUN", loc="1:100-100", gt="1/1", max_af=0.47)])
    assert _score(calls, "COMUN") is None, (
        "un polimorfismo comun al 47 % no puede competir: es el filtro que "
        "cerro FANCD2 y los tres competidores de A0")


def test_08_una_variante_que_no_pasa_calidad_no_entra():
    calls = rank([V("MALA", loc="1:100-100", gt="1/1", filt="LowQual",
                    dp=3, gq=8, ad="1,2")])
    assert _score(calls, "MALA") is None


# ─────────── 9-10 · hemicigosis en varon ───────────

def test_09_la_x_fuera_de_par_es_hemicigota_en_varon():
    assert is_hemizygous("X:60000000-60000000", male=True)
    assert not is_hemizygous("X:60000000-60000000", male=False)


def test_10_un_autosoma_nunca_es_hemicigoto():
    assert not is_hemizygous("15:40000000-40000000", male=True)


# ─────────── 11 · determinismo ───────────

def test_11_el_ranking_es_reproducible():
    vs = [V(f"G{i}", loc=f"{1 + i}:{100 * i + 100}-{100 * i + 100}",
            gt="1/1" if i % 2 else "0/1") for i in range(12)]
    primero = [(c.gene, c.score) for c in rank(vs)]
    for _ in range(3):
        assert [(c.gene, c.score) for c in rank(vs)] == primero
