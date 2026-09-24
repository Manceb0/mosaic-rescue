import base64
import nbformat
from src.nb.story_integration import integrate, TAG


def test_attachments_preserve_executed_cells_and_are_idempotent():
    original = nbformat.v4.new_code_cell("answer = 42", execution_count=7,
        outputs=[nbformat.v4.new_output("stream", name="stdout", text="original output")])
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell("# Original"), original])
    integrate(nb, "06_MOSAIC_AND_MITOREAD.ipynb")
    integrate(nb, "06_MOSAIC_AND_MITOREAD.ipynb")
    nbformat.validate(nb)
    added = [c for c in nb.cells if TAG in c.metadata.get("tags", [])]
    assert len(added) == 2
    assert nb.cells[-1] == original
    for cell in added:
        for filename, data in cell.attachments.items():
            assert "attachment:" + filename in cell.source
            assert base64.b64decode(data["image/png"]).startswith(b"\x89PNG\r\n\x1a\n")
