#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Los numeros que el repositorio PUBLICA coinciden con los artefactos.

Ningun dato del paciente: los notebooks ejecutados estan versionados.

POR QUE EXISTE ESTA SUITE
    El repositorio ha publicado, en momentos distintos, "26 figuras / 21
    cientificas" y "27 / 22" cuando eran otra cosa; ha dicho que el universo
    tenia 6 322 genes cuando el canonico es 6 321; ha marcado cinco
    experimentos como "falta notebook" en una tabla mientras el parrafo de
    debajo afirmaba lo contrario; y tres documentos distintos han declarado 14,
    12 y 12 contradicciones cuando habia 13.

    Ninguno era mentira deliberada. Simplemente nadie recalcula un numero al
    anadir una fila. Por eso lo cuenta una maquina.
"""
import io, pathlib, re, sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.nb.nbutil import verify as nbverify                            # noqa: E402

NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))
DOCS_CON_CONTEO = ("README.md", "research/EXPERIMENT_REGISTRY.md")
DOCS_CON_CONTRADICCIONES = ("docs/SCALABILITY.md", "research/evidence_registry.md",
                            "AGENTS.md")


def _txt(rel):
    return io.open(ROOT / rel, encoding="utf-8").read()


def _totales():
    figs = sci = errs = 0
    for p in NOTEBOOKS:
        e, f, s, _ok = nbverify(str(p))
        errs += e; figs += f; sci += s
    return errs, figs, sci


# ─────────── 1-3 · los notebooks ejecutados ───────────

def test_01_hay_ocho_notebooks_ejecutados():
    assert len(NOTEBOOKS) == 8, f"se esperaban 8 notebooks, hay {len(NOTEBOOKS)}"


def test_02_ningun_notebook_tiene_salidas_de_error():
    errs, _f, _s = _totales()
    assert errs == 0, f"{errs} salidas de error dentro de los notebooks ejecutados"


@pytest.mark.parametrize("nb", [p.name for p in NOTEBOOKS])
def test_03_cada_notebook_tiene_al_menos_una_figura_cientifica(nb):
    """Una infografia con rectangulos no satisface el requisito por muchas que haya."""
    _e, _f, sci, _ok = nbverify(str(ROOT / "notebooks" / nb))
    assert sci >= 1, f"{nb} no tiene ninguna figura cientifica declarada"


# ─────────── 4-5 · los conteos publicados ───────────

@pytest.mark.parametrize("doc", DOCS_CON_CONTEO)
def test_04_el_conteo_de_figuras_publicado_coincide(doc):
    _e, figs, sci = _totales()
    t = _txt(doc)
    assert str(figs) in t, f"{doc} no menciona el total real de figuras ({figs})"
    assert str(sci) in t, f"{doc} no menciona el total real de cientificas ({sci})"


def test_05_las_cientificas_no_superan_al_total():
    _e, figs, sci = _totales()
    assert 0 < sci <= figs, f"cientificas={sci}, total={figs}"


# ─────────── 6 · el universo de genes ───────────

NIEGAN = ("obsolet", "superad", "quedó", "quedo", "ya no", "antes dec",
          "primera pasada", "no es", "incorrect")


def test_06_el_universo_canonico_es_6321_y_el_6322_solo_aparece_negado():
    """El 6 322 quedo obsoleto al arreglar el cruce de alelos.

    OJO: un documento canonico PUEDE nombrar el 6 322 para decir que esta
    superado, y eso es bueno, no un fallo. Esa distincion ya existe en
    src/audit_stale_claims.py como clase NEGADO. Una version anterior de esta
    prueba fallaba sobre la propia frase que explica que el numero es obsoleto,
    es decir, castigaba al documento por ser explicito.
    """
    for doc in ("README.md", "research/EXPERIMENT_REGISTRY.md"):
        for n, line in enumerate(_txt(doc).splitlines(), 1):
            if "6 322" not in line and "6,322" not in line:
                continue
            assert any(k in line.lower() for k in NIEGAN), (
                f"{doc}:{n} afirma el conteo obsoleto 6 322 sin declararlo superado")
        # No se exige que TODO documento nombre el universo. Solo que, si lo
        # nombra, use el canonico: obligar a un numero concreto en un fichero
        # concreto convierte la prueba en una preferencia de redaccion.
        t = _txt(doc)
        if "6 32" in t:
            assert "6 321" in t, f"{doc} nombra el universo pero no con el conteo canonico"


# ─────────── 7 · las contradicciones ───────────

def test_07_el_numero_de_contradicciones_publicado_coincide():
    s = _txt("research/contradictions.md")
    principal = s.split("## Contradicciones que a")[0]
    n = len(re.findall(r"^\| \*\*(C\d+)\*\*", principal, re.M))
    assert n >= 10, f"solo {n} contradicciones registradas: el registro se ha vaciado"
    for doc in DOCS_CON_CONTRADICCIONES:
        for m in re.finditer(r"(\d+)\s+(?:entradas|contradicciones)", _txt(doc)):
            assert int(m.group(1)) == n, (
                f"{doc} dice '{m.group(0)}' pero hay {n} contradicciones")


# ─────────── 8-9 · los dos numeros de BUB1B van siempre juntos ───────────

@pytest.mark.parametrize("doc", ("README.md", "reports/TRACK1_REPORT.md"))
def test_08_a0_cuatro_y_freqfix_uno_se_reportan_juntos(doc):
    """`CLAUDE.md`: prohibido narrar la historia como "BUB1B siempre fue #1"."""
    t = _txt(doc)
    assert "A0-FREQFIX" in t, f"{doc} no menciona la sensibilidad A0-FREQFIX"
    # El puesto puede escribirse como "#4" o en palabras ("fourth", "cuarto").
    # Exigir solo la forma con almohadilla castigaba una redaccion correcta.
    CUARTO = ("#4", "fourth", "cuarto", "puesto 4")
    assert any(k in t.lower() for k in CUARTO), (
        f"{doc} no reporta el puesto #4 del A0 congelado")


def test_09_ningun_documento_canonico_afirma_que_gano_sin_fenotipo():
    PROHIBIDA = "ganó sin fenotipo y sin clinvar"
    for doc in ("README.md", "research/EXPERIMENT_REGISTRY.md",
                "reports/TRACK1_REPORT.md", "reports/TRACK2_REPORT.md"):
        assert PROHIBIDA not in _txt(doc).lower(), (
            f"{doc} contiene la formulacion prohibida sobre el ranking")
