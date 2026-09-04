# -*- coding: utf-8 -*-
"""El artefacto que de verdad viaja al jurado, bajo test.

POR QUE EXISTE ESTE FICHERO. Una auditoria adversarial busco `submission` en
`tests/`, `src/verify.py`, el `Makefile` y CI, y no lo encontro en ninguno. El
repositorio tenia 71 tests, diez comprobaciones, fichas de QA de figuras, un
escaner de privacidad y un auditor de afirmaciones obsoletas, y el unico fichero
que se sube a la plataforma vivia fuera de todo eso.

No es casualidad que el unico error de contenido del entregable -- un
denominador de Exomiser que el resto del repositorio clasifica como error de
conteo -- viviera justo ahi. Era la superficie sin control.

Ninguno de estos tests necesita el dataset del paciente: comprueban el CONTRATO
del generador. Los que si tocan el CSV en disco se saltan solos cuando no existe,
y lo dicen en voz alta en vez de pasar en verde sin haber mirado nada.
"""
import csv
import io
import os

import pytest

from src.submission import track1_csv as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ESQUEMA_OFICIAL = ["proband_id", "chrom_1", "pos_1", "ref_1", "alt_1",
                   "chrom_2", "pos_2", "ref_2", "alt_2",
                   "epcr", "finding_type", "notes"]

FUENTE = io.open(os.path.join(ROOT, "src/submission/track1_csv.py"),
                 encoding="utf-8").read()


def _csv_rows():
    p = os.path.join(ROOT, T.OUT)
    if not os.path.exists(p):
        pytest.skip(f"{T.OUT} no existe: hay que generarlo con el dataset local")
    return list(csv.reader(io.open(p, encoding="utf-8")))


# --------------------------------------------------------------- el esquema --
def test_columnas_son_el_esquema_oficial():
    """El orden importa: el evaluador lee por posicion, no por nombre."""
    assert T.COLUMNS == ESQUEMA_OFICIAL


def test_epcr_en_rango_abierto():
    """`epcr` es una probabilidad en (0, 1]. Un cero declarado no es una
    prediccion, es una retirada, y el formato no lo admite."""
    for gen, (epcr, _) in T.EPCR_RATIONALE.items():
        assert 0 < epcr <= 1, f"{gen}: epcr {epcr} fuera de (0, 1]"


def test_cada_epcr_lleva_su_justificacion_escrita():
    """Un numero subjetivo sin justificacion es un numero inventado."""
    for gen, (_, razon) in T.EPCR_RATIONALE.items():
        assert len(razon.strip()) > 200, f"{gen}: justificacion demasiado corta"


# ------------------------------------------------------- vocabulario cerrado --
def test_finding_type_es_vocabulario_cerrado():
    assert "primary" in FUENTE and "secondary" in FUENTE


@pytest.mark.parametrize("fila", [0, 1])
def test_finding_type_del_csv_es_valido(fila):
    filas = _csv_rows()
    assert filas[fila + 1][10] in ("primary", "secondary")


def test_el_csv_tiene_la_cabecera_oficial():
    assert _csv_rows()[0] == ESQUEMA_OFICIAL


def test_el_csv_declara_un_primario_y_un_secundario():
    tipos = [r[10] for r in _csv_rows()[1:]]
    assert tipos.count("primary") == 1, "exactamente un hallazgo primario"
    assert tipos.count("secondary") == 1, "LZTR1 es secundario/incidental"


# ------------------------------------------------- denominadores ya superados --
@pytest.mark.parametrize("superado, porque", [
    ("#2/470", "470 son filas gen x modelo de herencia, no genes distintos"),
    ("de 470", "470 son filas gen x modelo de herencia, no genes distintos"),
    ("6 322", "conteo superado en todo el repositorio"),
    ("6,322", "conteo superado en todo el repositorio"),
])
def test_el_generador_no_lleva_denominadores_superados(superado, porque):
    """El repositorio corrigio estos conteos en todas partes menos aqui, que
    era el unico sitio sin control. Este test es el control."""
    assert superado not in FUENTE, f"{superado!r} sigue en el generador: {porque}"


def test_el_csv_en_disco_tampoco_los_lleva():
    """El fichero en disco no se regenera solo: si el generador cambia y nadie
    lo vuelve a correr, se sube la version vieja."""
    for fila in _csv_rows()[1:]:
        assert "470" not in fila[11], "el CSV en disco esta obsoleto: regeneralo"


def test_el_denominador_correcto_esta_presente():
    assert "398" in FUENTE, "hay que declarar los 398 genes distintos"


# ------------------------------------------- terminologia vigente de LZTR1 ----
def test_lztr1_no_se_presenta_como_causa():
    """`LZTR1` quedo como candidato secundario/incidental de investigacion
    (EXP-022). Presentarlo de otro modo cambiaria una conclusion cientifica."""
    razon = T.EPCR_RATIONALE["LZTR1"][1] + T.NOTES["LZTR1"]
    bajo = razon.lower()
    assert "secondary" in bajo or "secundario" in bajo
    assert "not" in bajo or "no " in bajo, "tiene que negar que sea la causa"
    assert T.EPCR_RATIONALE["LZTR1"][0] < T.EPCR_RATIONALE["BUB1B"][0]


def test_bub1b_reporta_los_dos_puestos_de_ranking():
    """`A0` congelado da #4 y la sensibilidad `A0-FREQFIX` da #1. Los dos
    numeros se reportan SIEMPRE juntos; contar solo el #1 es la narracion
    prohibida."""
    texto = T.EPCR_RATIONALE["BUB1B"][1] + T.NOTES["BUB1B"]
    assert "#4" in texto and "FREQFIX" in texto


def test_la_fase_se_declara_sin_resolver():
    """Sin muestras parentales no hay fase, luego `PM3` esta bloqueado y la
    configuracion bialelica es candidata, no demostrada."""
    texto = T.NOTES["BUB1B"].upper()
    assert "UNRESOLVED" in texto and "PM3" in texto


# ------------------------------------------------------------- privacidad ----
def test_el_generador_no_lleva_coordenadas_escritas():
    """Las coordenadas salen del VCF en tiempo de ejecucion, nunca del codigo.
    Una coordenada escrita a mano en un fichero versionado es un dato del
    paciente en el historial de git, y de ahi no se borra."""
    import re
    assert not re.search(r"\bchr[0-9XYM]+[:\-]\s?\d{4,}", FUENTE)


def test_la_salida_vive_fuera_del_arbol_versionado():
    assert T.OUT.startswith("work/"), "el CSV lleva coordenadas reales"

# ------------------------------------ el identificador de la PLATAFORMA -------
def test_el_proband_id_es_el_que_acepta_la_plataforma():
    """El generador escribia el nombre de MUESTRA del VCF en esta columna. La
    plataforma keyea su ground truth por otro identificador y responde
    `Unknown proband_id ... Only PROBAND01 is accepted in this challenge`.
    El fallo no habria dado un error de formato sino cero puntos: peor."""
    assert T.SUBMISSION_PROBAND_ID == "PROBAND01"


def test_el_generador_no_alimenta_el_proband_id_desde_el_vcf():
    """Nombre de muestra e identificador de submission son objetos distintos.
    La funcion que lee el VCF se conserva como comprobacion cruzada, pero no
    puede volver a alimentar la columna."""
    assert "pid = SUBMISSION_PROBAND_ID" in FUENTE
    assert "pid = proband_id()" not in FUENTE


def test_el_csv_en_disco_lleva_el_proband_id_correcto():
    for fila in _csv_rows()[1:]:
        assert fila[0] == T.SUBMISSION_PROBAND_ID


def test_todas_las_filas_comparten_proband_id():
    assert len({f[0] for f in _csv_rows()[1:]}) == 1


# ----------------------------------- lo que el evaluador oficial exige --------
def test_como_maximo_diez_filas():
    """`Proband {pid} has {n} rows; max is 10` en el evaluador oficial."""
    assert len(_csv_rows()) - 1 <= 10


def test_el_cromosoma_lleva_prefijo_chr():
    """El evaluador NO anade ni quita el prefijo: compara la cadena tal cual,
    y el ground truth usa `chrN`. Sin prefijo no habria error, habria cero."""
    for fila in _csv_rows()[1:]:
        assert fila[1].startswith("chr")
        if fila[5].strip():
            assert fila[5].startswith("chr")


def test_las_posiciones_son_enteros():
    """`int(pos)` en el evaluador: cualquier cosa que no sea digito revienta."""
    for fila in _csv_rows()[1:]:
        assert fila[2].isdigit()
        if fila[6].strip():
            assert fila[6].isdigit()


def test_los_alelos_van_en_mayusculas():
    """El evaluador normaliza con `.upper()`; enviarlo ya normalizado evita
    depender de esa cortesia."""
    for fila in _csv_rows()[1:]:
        for i in (3, 4, 7, 8):
            if fila[i].strip():
                assert fila[i] == fila[i].upper()


def test_el_segundo_alelo_esta_completo_o_completamente_vacio():
    """Media pareja no es un compuesto heterocigoto: el evaluador devuelve
    None si falta chrom o pos, y la fila valdria como variante unica sin que
    nadie lo hubiera decidido."""
    for fila in _csv_rows()[1:]:
        segundo = [fila[i].strip() for i in (5, 6, 7, 8)]
        assert all(segundo) or not any(segundo)
