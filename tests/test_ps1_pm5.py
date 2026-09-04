# -*- coding: utf-8 -*-
"""PS1 y PM5: los casos que la implementacion anterior habria aprobado.

El defecto era doble. Construia el conjunto del residuo con TODO lo codificante,
asi que un truncante `P`/`LP` en el mismo residuo entraba como soporte de PM5; y
fundia `Pathogenic` con `Likely pathogenic`, cuando la formulacion clasica exige
patogenicidad ESTABLECIDA.

Ninguno de estos tests toca datos del paciente: son registros sinteticos con la
forma exacta que produce el cruce ClinVar x VEP.
"""
import pytest

from src.annotation.ps1_pm5 import evaluate, is_missense, significance_tier

# el cambio del caso, sintetico: no es el del paciente
REF, ALT = "R", "W"


def rec(con, aa, sig):
    return {"con": con, "aa": aa, "sig": sig}


# ------------------------------------------------------- el nucleo del criterio
def test_missense_patogenica_otra_sustitucion_otorga_pm5():
    """El unico caso que SI cuenta."""
    ev = evaluate([rec("missense_variant", "R/Q", "Pathogenic")], REF, ALT)
    assert len(ev["pm5"]) == 1
    assert not ev["ps1"]


def test_mismo_cambio_de_aminoacido_no_es_pm5_sino_la_via_de_ps1():
    """Si la sustitucion es la MISMA, la via es PS1. Nunca las dos."""
    ev = evaluate([rec("missense_variant", "R/W", "Pathogenic")], REF, ALT)
    assert ev["pm5"] == []
    assert len(ev["ps1_pending_nucleotide_check"]) == 1


def test_ps1_no_se_otorga_sin_comprobar_el_cambio_de_nucleotido():
    """PS1 exige ademas un cambio nucleotidico DISTINTO, y los campos que
    consumimos no bastan para comprobarlo. Se declara pendiente, no concedido."""
    ev = evaluate([rec("missense_variant", "R/W", "Pathogenic")], REF, ALT)
    assert ev["ps1"] == [], "PS1 no puede concederse con los campos disponibles"


# ------------------------------------------- los truncantes, que antes colaban
@pytest.mark.parametrize("consecuencia", [
    "stop_gained",
    "frameshift_variant",
    "stop_gained&splice_region_variant",
    "splice_acceptor_variant",
    "start_lost",
])
def test_truncante_patogenico_en_el_mismo_residuo_no_da_pm5(consecuencia):
    """EL DEFECTO. Un truncante no es un cambio de aminoacido: no dice nada
    sobre la tolerancia del residuo a una sustitucion. De las 84 P/LP de ClinVar
    en BUB1B, 83 son de este tipo."""
    ev = evaluate([rec(consecuencia, "R/*", "Pathogenic")], REF, ALT)
    assert ev["pm5"] == [], f"{consecuencia} no puede otorgar PM5"
    assert ev["ps1_pending_nucleotide_check"] == []
    assert len(ev["excluded_not_missense"]) == 1


def test_el_truncante_excluido_se_reporta_no_se_descarta_en_silencio():
    ev = evaluate([rec("stop_gained", "R/*", "Pathogenic")], REF, ALT)
    assert "no ser missense" in ev["reason"] or "NO ser missense" in ev["reason"]


# ------------------------------------------------ lo que no es soporte de nada
@pytest.mark.parametrize("clnsig", [
    "Benign",
    "Likely benign",
    "Uncertain significance",
    "Conflicting classifications of pathogenicity",
    "not provided",
    "",
])
def test_missense_no_patogenica_en_el_mismo_residuo_no_da_pm5(clnsig):
    ev = evaluate([rec("missense_variant", "R/Q", clnsig)], REF, ALT)
    assert ev["pm5"] == []
    assert ev["pm5_lp_candidates"] == []


def test_conflicting_no_es_soporte():
    """`Conflicting` es justamente el estado en el que los submisores NO se
    ponen de acuerdo. Contarlo como patogenico invertiria su significado."""
    assert significance_tier("Conflicting classifications of pathogenicity") is None


# --------------------------------------- Likely pathogenic exige especificacion
def test_likely_pathogenic_no_otorga_pm5_por_defecto():
    """Aceptar LP con la fuerza de P es una decision de ESPECIFICACION. Para
    BUB1B no existe hoy ninguna VCEP que la autorice."""
    ev = evaluate([rec("missense_variant", "R/Q", "Likely pathogenic")], REF, ALT)
    assert ev["pm5"] == []
    assert len(ev["pm5_lp_candidates"]) == 1
    assert "especificacion" in ev["reason"]


def test_likely_pathogenic_cuenta_solo_con_especificacion_declarada():
    ev = evaluate([rec("missense_variant", "R/Q", "Likely pathogenic")], REF, ALT,
                  lp_specification="VCEP ficticia, declarada explicitamente")
    assert len(ev["pm5"]) == 1


def test_agregado_en_disputa_tampoco_cuenta_por_defecto():
    """`Pathogenic/Likely pathogenic` es un agregado donde los submisores
    discrepan entre las dos fuerzas. Se trata como LP, no como P."""
    ev = evaluate([rec("missense_variant", "R/Q", "Pathogenic/Likely pathogenic")], REF, ALT)
    assert ev["pm5"] == []
    assert len(ev["pm5_lp_candidates"]) == 1


# ------------------------------------- la variante EVALUADA tiene que ser missense
@pytest.mark.parametrize("ref, alt", [(None, "W"), ("R", None), ("R", "R"), (None, None)])
def test_sin_cambio_de_aminoacido_los_criterios_no_son_aplicables(ref, alt):
    """`no aplica` y `no es aplicable` no son lo mismo. Si la variante evaluada
    no es una missense declarada, devolver un `no` haria pasar por resultado lo
    que es una pregunta mal planteada."""
    ev = evaluate([rec("missense_variant", "R/Q", "Pathogenic")], ref, alt)
    assert ev["applicable"] is False
    assert ev["pm5"] == []


# ------------------------------------------------------------------ auxiliares
def test_is_missense_acepta_consecuencias_concatenadas():
    assert is_missense("missense_variant&splice_region_variant")
    assert not is_missense("synonymous_variant")


def test_los_dos_formatos_de_aminoacido_son_el_mismo_par():
    """VEP escribe `R/Q`; otras fuentes escriben `RQ`."""
    a = evaluate([rec("missense_variant", "R/W", "Pathogenic")], REF, ALT)
    b = evaluate([rec("missense_variant", "RW", "Pathogenic")], REF, ALT)
    assert len(a["ps1_pending_nucleotide_check"]) == len(b["ps1_pending_nucleotide_check"]) == 1


# -------------------------------------------------- el veredicto del caso, intacto
def test_un_residuo_sin_ninguna_patogenica_no_otorga_nada():
    """Es la situacion real del residuo candidato, y la razon de que esta
    correccion no cambie ningun veredicto publicado."""
    ev = evaluate([rec("missense_variant", "R/Q", "Uncertain significance"),
                   rec("synonymous_variant", "R/R", "Likely benign")], REF, ALT)
    assert ev["applicable"] is True
    assert ev["pm5"] == [] and ev["ps1"] == []
    assert "PM5 NO aplica" in ev["reason"]


def test_mezcla_realista_solo_cuenta_la_missense_patogenica():
    ev = evaluate([
        rec("stop_gained", "R/*", "Pathogenic"),                    # excluida
        rec("frameshift_variant", "R/X", "Pathogenic"),             # excluida
        rec("missense_variant", "R/Q", "Likely pathogenic"),        # candidata LP
        rec("missense_variant", "R/G", "Pathogenic"),               # LA que cuenta
        rec("missense_variant", "R/H", "Benign"),                   # nada
    ], REF, ALT)
    assert len(ev["pm5"]) == 1
    assert len(ev["excluded_not_missense"]) == 2
    assert len(ev["pm5_lp_candidates"]) == 1
