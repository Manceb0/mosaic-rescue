#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Barrera de correccion para EXP-006.

Todos los datos son SINTETICOS. Ninguna prueba toca el genoma del paciente, asi
que esta suite puede ejecutarla cualquiera al clonar el repositorio.

Cada prueba corresponde a un fallo que ya ocurrio o que puede ocurrir:
  1-4   union variante<->anotacion
  5,7   duplicados por transcrito que fabrican compound-het falsos
  6     compound-het legitimo
  8-11  genotipos y modelos de herencia, incluido X en varon
  12-14 filtros que no deben eliminar candidatos en silencio
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.prioritization.allele_key import parse_uploaded, vcf_keys, build_index, join_report
from src.prioritization.genome_wide import Variant, rank, is_hemizygous


# ─────────── 1-4 · union por identidad exacta ───────────

def test_01_snv_exacto():
    kind, val = parse_uploaded("1_12719616_C/T")
    assert kind == "coord" and val == ("1", 12719616, "C", "T")
    assert ("coord", ("1", 12719616, "C", "T")) in vcf_keys("1", "12719616", ".", "C", "T")


def test_02_indel_minimizado_casa_por_representacion_no_por_posicion():
    """VEP desplaza la coordenada de los indels. La union NO usa la posicion
    reportada por VEP, usa la representacion de entrada que VEP conserva."""
    up = "1_1919188_CAGCGGCAGG/C"
    kind, val = parse_uploaded(up)
    assert kind == "coord"
    assert val == ("1", 1919188, "CAGCGGCAGG", "C")
    idx = build_index([["1", "1919188", ".", "CAGCGGCAGG", "C", ".", "PASS"]])
    assert ("coord", val) in idx


def test_03_dos_indels_vecinos_NO_se_cruzan():
    """El fallo que la tolerancia +-1 podia provocar: emparejar mal dos indels
    a un solo pb de distancia."""
    a = ["1", "1000", ".", "CT", "C", ".", "PASS"]
    b = ["1", "1001", ".", "TG", "T", ".", "PASS"]
    idx = build_index([a, b])
    ka = parse_uploaded("1_1000_CT/C")[1]
    kb = parse_uploaded("1_1001_TG/T")[1]
    assert idx[("coord", ka)] is a
    assert idx[("coord", kb)] is b
    assert idx[("coord", ka)] is not idx[("coord", kb)]


def test_04_multialelico_da_una_clave_por_alelo():
    keys = vcf_keys("2", "500", ".", "A", "G,T")
    assert ("coord", ("2", 500, "A", "G")) in keys
    assert ("coord", ("2", 500, "A", "T")) in keys
    # y el informe de union declara si algo no se recupero
    rep = join_report({("coord", ("2", 500, "A", "G"))}, set())
    assert rep["one_to_one"] is False and rep["missing"] == 1


# ─────────── utilidades ───────────

def V(loc, gene, cons, impact, gt, af=None, sift="", poly="", clin="", dp=40, gq=99, ad=None):
    if ad is None:
        ad = "20,20" if gt == "0/1" else "0,40"
    return Variant(loc=loc, gene=gene, consequence=cons, impact=impact, max_af=af,
                   sift=sift, polyphen=poly, clinsig=clin, hgvsp="", canonical=True,
                   mane="", gt=gt, dp=dp, gq=gq, ad=ad, filt="PASS")


# ─────────── 5-7 · duplicados y compound-het ───────────

def test_05_varios_transcritos_de_un_alelo_no_duplican_el_gen():
    same = [V("1:100", "G1", "missense_variant", "MODERATE", "0/1"),
            V("1:100", "G1", "missense_variant", "MODERATE", "0/1")]
    c = rank(same)[0]
    locs = {v.loc for v in c.variants}
    assert len(locs) == 1, "un solo alelo genomico"


def test_06_compound_het_legitimo_con_dos_alelos_distintos():
    vs = [V("1:100", "G1", "stop_gained", "HIGH", "0/1"),
          V("1:900", "G1", "missense_variant", "MODERATE", "0/1", sift="deleterious(0.01)")]
    c = rank(vs)[0]
    assert "compuesto" in c.model
    assert "fase no resuelta" in c.model, "la fase NUNCA se da por resuelta"


def test_07_mismo_alelo_repetido_no_finge_compound_het():
    """El fallo mas peligroso: dos filas del mismo alelo pareciendo dos alelos."""
    vs = [V("1:100", "G1", "missense_variant", "MODERATE", "0/1", sift="deleterious(0.01)"),
          V("1:100", "G1", "missense_variant", "MODERATE", "0/1", sift="deleterious(0.01)")]
    c = rank(vs)[0]
    assert len({v.loc for v in c.variants}) == 1
    # y la agregacion debe verlo: no hay dos alelos
    assert len({v.loc for v in c.variants if v.gt == "0/1"}) < 2


# ─────────── 8-11 · genotipos y herencia ───────────

def test_08_homocigoto_autosomico_no_lo_filtra_el_balance_alelico():
    """Un 1/1 tiene balance ~1,0. Si el umbral 0,20-0,80 se aplicara a todo,
    se eliminarian justo los homocigotos recesivos."""
    v = V("1:100", "G1", "stop_gained", "HIGH", "1/1", ad="0,40")
    assert v.allele_balance == 1.0
    assert v.passes_quality, "un homocigoto no puede caer por el filtro de het"


def test_09_heterocigoto_desviado_si_se_filtra():
    ok = V("1:100", "G1", "missense_variant", "MODERATE", "0/1", ad="20,20")
    bad = V("1:200", "G1", "missense_variant", "MODERATE", "0/1", ad="38,2")
    assert ok.passes_quality
    assert not bad.passes_quality, "balance 0,05 es artefacto probable"


def test_10_hemicigosis_en_X_de_varon():
    assert is_hemizygous("X:70134785", male=True)
    assert not is_hemizygous("X:1000000", male=True), "PAR1: el varon es diploide"
    assert not is_hemizygous("X:70134785", male=False)
    assert not is_hemizygous("7:70134785", male=True)


def test_11_un_alelo_hemicigoto_es_modelo_recesivo_COMPLETO():
    """Correccion v3: no se penaliza la hemicigosis. Para enfermedad recesiva
    ligada a X en un varon, un alelo es el modelo entero."""
    hemi = rank([V("X:70134785", "GX", "stop_gained", "HIGH", "1/1")], male=True)[0]
    hom = rank([V("7:100", "GA", "stop_gained", "HIGH", "1/1")], male=True)[0]
    assert "COMPLETO" in hemi.model
    assert hemi.score == hom.score, "hemicigoto no vale menos que homocigoto"


# ─────────── 12-14 · filtros que no deben borrar en silencio ───────────

def test_12_HIGH_comun_no_sobrevive():
    v = V("1:100", "G1", "start_lost", "HIGH", "0/1", af=0.81)
    assert not v.is_rare, "AF 0,81 es un polimorfismo, no un candidato"


def test_13_missense_rara_SIN_predictor_no_desaparece():
    """El fallo real: 6 missense raras se perdian por no tener SIFT ni PolyPhen.
    La ausencia de dato no es evidencia en contra."""
    v = V("1:100", "G1", "missense_variant", "MODERATE", "0/1", sift="", poly="")
    assert v.enters_ranking, "sin predictor NO puede desaparecer"
    assert v.predictor_support == 0.0, "ausencia de dato no penaliza"
    tol = V("1:100", "G1", "missense_variant", "MODERATE", "0/1",
            sift="tolerated(0.4)", poly="benign(0.01)")
    assert tol.enters_ranking, "un predictor benigno resta puntos, no elimina"
    assert tol.predictor_support < 0


def test_14_la_fase_permanece_sin_resolver():
    vs = [V("1:100", "G1", "stop_gained", "HIGH", "0/1"),
          V("1:900", "G1", "stop_gained", "HIGH", "0/1")]
    c = rank(vs)[0]
    assert "CANDIDATO" in c.model and "fase no resuelta" in c.model
    assert "compuesto confirmado" not in c.model.lower()


# ─────────── 15-16 · agregacion por haplotipo ───────────

def H(loc, gene, cons, impact, pgt="", pid="", **kw):
    v = V(loc, gene, cons, impact, "0/1", **kw)
    v.pgt, v.pid = pgt, pid
    return v


def test_15_variantes_en_cis_probado_son_UN_evento():
    """El fallo real: 33 variantes en 170 pb, todas 0|1 en el mismo bloque PID,
    se contaban como recesivo compuesto. Son UN haplotipo."""
    from src.prioritization.genome_wide import haplotypic_events
    vs = [H(f"14:{94379548+i}", "G1", "missense_variant", "MODERATE",
            pgt="0|1", pid="94379541_G_GA") for i in (0, 6, 15, 17)]
    events, info = haplotypic_events(vs)
    assert len(events) == 1, "mismo PID y mismo PGT = un solo haplotipo"
    assert info["collapsed"] == 3
    assert info["local_trans_proven"] is False
    c = rank(vs)[0]
    assert "compuesto" not in c.model, "un haplotipo NO es compound-het"
    assert "haplotipo" in c.model


def test_16_orientaciones_opuestas_en_un_bloque_apoyan_trans():
    from src.prioritization.genome_wide import haplotypic_events
    vs = [H("1:100", "G1", "stop_gained", "HIGH", pgt="0|1", pid="B1"),
          H("1:150", "G1", "missense_variant", "MODERATE", pgt="1|0", pid="B1")]
    events, info = haplotypic_events(vs)
    assert len(events) == 2
    assert info["local_trans_proven"] is True
    assert "trans LOCAL" in rank(vs)[0].model


def test_17_sin_PID_la_fase_sigue_sin_resolver():
    """BUB1B: dos variantes a 11 kb, sin bloque de fase. NO se colapsan,
    pero tampoco se declara trans."""
    from src.prioritization.genome_wide import haplotypic_events
    vs = [H("15:1000000", "G1", "stop_gained", "HIGH"),
          H("15:1010911", "G1", "missense_variant", "MODERATE")]
    events, info = haplotypic_events(vs)
    assert len(events) == 2 and info["collapsed"] == 0
    assert info["local_trans_proven"] is False
    c = rank(vs)[0]
    assert "CANDIDATO" in c.model and "fase no resuelta" in c.model
