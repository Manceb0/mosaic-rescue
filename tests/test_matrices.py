#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las dos matrices de Track 2 se parsean y son internamente consistentes.

Ningun dato del paciente. Las dos matrices estan versionadas, asi que estas
pruebas corren al clonar el repositorio.

Cada prueba corresponde a un fallo que YA OCURRIO en este proyecto:
  1-3   una afirmacion sin fuente entro en la matriz de evidencia
  4-6   la cabecera decia "3 intervenciones y 2 controles" con tres controles
  7-9   una afirmacion FALSA sobre evidencia farmacologica paso con todo en
        verde porque el control solo miraba la otra matriz
  10-11 el vocabulario cerrado dejo de estar cerrado
"""
import io, pathlib, re, sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.figures.fig07_evidence import read as read_evidence, DIMS      # noqa: E402
from src.figures import fig08_portfolio as FP                           # noqa: E402

TAB, NL = chr(9), chr(10)


# ─────────── 1-3 · matriz de evidencia: 8 puentes x 10 dimensiones ───────────

def test_01_matriz_de_evidencia_completa():
    ev = read_evidence(str(ROOT / "research/track2_evidence.tsv"))
    bridges = sorted({int(e["puente"]) for e in ev})
    assert len(ev) == len(bridges) * len(DIMS), (
        f"la matriz no es rectangular: {len(ev)} filas para "
        f"{len(bridges)} puentes x {len(DIMS)} dimensiones")


def test_02_ninguna_celda_no_vacia_sin_fuente():
    """La regla dura de la matriz. Si esto falla, la matriz no vale nada."""
    ev = read_evidence(str(ROOT / "research/track2_evidence.tsv"))
    huerfanas = [(e["puente"], e["dimension"]) for e in ev
                 if e["clase"] != "ABSENT" and not e["fuente"].strip()]
    assert not huerfanas, f"celdas sin fuente: {huerfanas}"


def test_03_vocabulario_de_clase_cerrado():
    CERRADO = {"DIRECT", "NEAR", "GENETIC", "CONTRADICTORY", "ABSENT"}
    ev = read_evidence(str(ROOT / "research/track2_evidence.tsv"))
    fuera = sorted({e["clase"] for e in ev} - CERRADO)
    assert not fuera, f"clases fuera del vocabulario cerrado: {fuera}"


# ─────────── 4-6 · matriz de candidatos: cabecera contra filas ───────────

def _crudo():
    return io.open(ROOT / "research/track2_candidates.tsv", encoding="utf-8").read()


def test_04_matriz_de_candidatos_rectangular():
    filas = [l.split(TAB) for l in _crudo().split(NL)
             if l.strip() and not l.startswith("#")]
    hdr = filas[0]
    irregulares = [f[0] for f in filas[1:] if len(f) != len(hdr)]
    assert not irregulares, f"filas con numero de columnas distinto: {irregulares}"


def test_05_roles_del_vocabulario_cerrado():
    ROLES = {"SENTINEL", "ALLELE", "ADVERSARIAL", "CONTROL"}
    rows = FP.read(str(ROOT / "research/track2_candidates.tsv"))
    fuera = sorted({r["rol"] for r in rows} - ROLES)
    assert not fuera, f"roles desconocidos: {fuera}"


def test_06_la_cabecera_no_puede_contradecir_a_las_filas():
    """La cabecera llego a decir "3 intervenciones y 2 controles" con 3 controles."""
    rows = FP.read(str(ROOT / "research/track2_candidates.tsv"))
    n_ctl = sum(1 for r in rows if r["rol"] == "CONTROL")
    n_int = len(rows) - n_ctl
    m = re.search(r"(\d+)\s+intervenciones\s+y\s+(\d+)\s+controles", _crudo())
    assert m, "la cabecera no declara cuantas intervenciones y controles tiene"
    assert (int(m.group(1)), int(m.group(2))) == (n_int, n_ctl), (
        f"la cabecera dice {m.group(1)}/{m.group(2)}, las filas son {n_int}/{n_ctl}")


# ─────────── 7-9 · toda afirmacion lleva procedencia ───────────

PROCEDENCIA = ("DOI ", "PMID ", "PMC", "etiqueta MIPLYFFA",
               "notebooks/", "track2_evidence.tsv", "no verificado")
VACIO = ("n/a", "no aplica", "")


@pytest.mark.parametrize("columna", FP.CLAIMS)
def test_07_toda_afirmacion_lleva_identificador_o_hueco_declarado(columna):
    """No solo la evidencia A FAVOR.

    El control original solo exigia identificador en 'evidencia directa' e
    'evidencia indirecta'. Una afirmacion falsa metida en contraevidencia,
    exposicion o seguridad pasaba limpia, que es justo donde este proyecto se
    juega la credibilidad.
    """
    sin_fuente = []
    for r in FP.read(str(ROOT / "research/track2_candidates.tsv")):
        v = r[columna].strip()
        if v.lower() in VACIO or v.lower().startswith(("ninguna", "ninguno")):
            continue
        if not any(t in v for t in PROCEDENCIA):
            sin_fuente.append(r["candidato"])
    assert not sin_fuente, f"'{columna}' sin procedencia en: {sin_fuente}"


def test_08_la_clasificacion_de_la_figura_cubre_todas_las_celdas():
    """classify() no puede devolver None ni una etiqueta fuera de su propio mapa."""
    validas = set(FP.COL)
    for r in FP.read(str(ROOT / "research/track2_candidates.tsv")):
        for c in FP.CLAIMS:
            k = FP.classify(r[c])
            assert k in validas, f"{r['candidato']}/{c} clasificada como {k!r}"


def test_09_ningun_candidato_se_propone_para_administracion():
    """Regla Dura 3. Un cambio de redaccion no puede colar una recomendacion."""
    t = _crudo().lower()
    assert "no se propone para administracion" in t or "ningun candidato" in t, (
        "la matriz debe declarar explicitamente que ningun candidato se propone "
        "para administracion")


# ─────────── 10-11 · la regla de descarte existe en los dos idiomas ───────────

def test_10_cada_intervencion_tiene_regla_de_descarte():
    for r in FP.read(str(ROOT / "research/track2_candidates.tsv")):
        if r["rol"] == "CONTROL":
            continue
        assert len(r["regla de descarte"].strip()) > 40, (
            f"{r['candidato']} no tiene regla de descarte escrita")


def test_11_la_regla_de_descarte_existe_tambien_en_ingles():
    """Las figuras hablan ingles y los documentos espanol.

    Traducirla dentro del codigo de la figura habria creado una segunda fuente
    de verdad. Las dos versiones viven en la misma fila del TSV.
    """
    for r in FP.read(str(ROOT / "research/track2_candidates.tsv")):
        assert r["regla de descarte (EN)"].strip(), (
            f"{r['candidato']} no tiene la regla de descarte en ingles")
