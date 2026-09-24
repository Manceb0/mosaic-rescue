"""Inserta figuras revisadas como adjuntos, sin reejecutar análisis históricos."""
from pathlib import Path
import base64
import nbformat

ROOT = Path(__file__).resolve().parents[2]
TAG = "reviewed-visual-integration"
PANELS = {
    "00": [("story00_overview", "NARRATIVE", "Una muestra biológica, cuatro carriles técnicos. El BAM completo ya existe; el QC original de abajo conserva su alcance L001.")],
    "01": [("story00_overview", "NARRATIVE", "El ranking A0 congelado y su revisión A0-FREQFIX son etapas distintas. La convergencia de herramientas sobre el mismo VCF no es replicación biológica.")],
    "02": [("story02_variant_card", "SYNTHESIS", "Dos alelos priorizados; fase sin resolver. Cis y trans son escenarios conceptuales, no haplotipos medidos.")],
    "03": [("story10_mechanism", "SYNTHESIS", "Hipótesis funcional; no hay ensayo de proteína ni rescate demostrado en este caso.")],
    "04": [("story03_second_allele", "SYNTHESIS", "Cierre GO 2B: sin llamada CNV RD+BAF o MEI solapante al cuerpo de BUB1B. Una inserción compleja no queda excluida."),
           ("story13_next_experiment", "SYNTHESIS", "RNA-seq y lecturas largas son propuestas. Las pistas AlphaGenome siguientes son predicciones existentes, no RNA medido ni calibración EXP-024 completada.")],
    "05": [("story13_next_experiment", "SYNTHESIS", "Mapa general de decisiones. El fenotipo residual requiere además revisión clínica; no establece un segundo diagnóstico.")],
    "06": [("story04_evidence_context", "SYNTHESIS", "WGS del caso, simulación y literatura responden preguntas diferentes."),
           ("fig09_cnvpytor_chromosome_rd_baf", "DATA", "GO 2B, resultado agregado ya congelado: RD/BAF descriptivos por cromosoma. No es cariotipo ni estima fracción mosaico. Fuente y hash en el pie original y ficha QA.")],
    "07": [("story12_safety_gates", "SYNTHESIS", "Reglas propuestas para vetar un rescate aparente que favorezca células inestables; todavía no son resultados experimentales.")],
}


def integrate(nb, name):
    """Idempotente; conserva todas las celdas originales y sus salidas."""
    nb.cells = [c for c in nb.cells if TAG not in c.metadata.get("tags", [])]
    additions = []
    for slug, kind, caption in PANELS.get(Path(name).name[:2], []):
        image = ROOT / "figures/pub" / (slug + ".png")
        encoded = base64.b64encode(image.read_bytes()).decode("ascii")
        cell = nbformat.v4.new_markdown_cell(
            "### Integración visual · 24 septiembre 2026\n\n"
            f"![{caption}](attachment:{slug}.png)\n\n"
            f"**{kind} · {'MEASURED / DERIVED' if kind == 'DATA' else 'DERIVED / EXTERNAL'}.** {caption}\n\n"
            "Figura importada del artefacto revisado, sin reejecutar el análisis original. "
            "[Fuentes y límites](../docs/STORYBOARD.md) · "
            "[QA](../PUBLICATION_FIGURE_QA.md).",
            metadata={"tags": [TAG]},
            attachments={slug + ".png": {"image/png": encoded}},
        )
        additions.append(cell)
    nb.cells[1:1] = additions
    return nb


def main():
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        nb = integrate(nbformat.read(path, as_version=4), path.name)
        nbformat.validate(nb)
        nbformat.write(nb, path)
        print(path.name, "visual integration OK")


if __name__ == "__main__":
    main()
