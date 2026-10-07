"""El formulario de metodos se escribe DESDE el informe maestro, nunca al reves."""
import pytest

from src.submission.export_reports import END, START, appendix_answers, write_form


MD = f"""# Informe

Texto.

{START}

## Appendix · Methods description (official hackathon form)

**Team name**

mosaic-rescue

**Please describe your model/approach in detail.**

Linea uno.

Linea dos, con **negrita** dentro.

{END}
"""


class _Cell:
    def __init__(self, value=None):
        self.value = value


class _Sheet:
    def __init__(self, questions):
        self.cells = {}
        for r, q in questions.items():
            self.cells[(r, 1)] = _Cell(q)
            self.cells[(r, 2)] = _Cell("respuesta vieja del 26-sep")

    def cell(self, r, c):
        return self.cells.setdefault((r, c), _Cell())


def test_appendix_answers_lee_preguntas_y_respuestas_multiparrafo():
    a = appendix_answers(MD)
    assert a["Team name"] == "mosaic-rescue"
    assert a["Please describe your model/approach in detail."] == \
        "Linea uno.\n\nLinea dos, con **negrita** dentro."


def test_write_form_sobrescribe_el_excel_con_el_informe():
    ws = _Sheet({7: "Team name", 8: None, 9: "Please describe your model/approach in detail."})
    n = write_form({"Hoja": ws}, "Hoja", range(7, 10), appendix_answers(MD))
    assert n == 2
    assert ws.cell(7, 2).value == "mosaic-rescue"
    assert ws.cell(9, 2).value.startswith("Linea uno.")


def test_write_form_falla_si_una_pregunta_no_esta_en_el_informe():
    ws = _Sheet({7: "Una pregunta que el informe no contesta"})
    with pytest.raises(SystemExit):
        write_form({"Hoja": ws}, "Hoja", range(7, 8), appendix_answers(MD))
