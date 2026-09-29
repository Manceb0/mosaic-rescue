"""Inserts reviewed synthesis figures as attachments, without re-running historical analyses."""
from pathlib import Path
import base64
import nbformat

ROOT = Path(__file__).resolve().parents[2]
TAG = "reviewed-visual-integration"
PANELS = {
    "00": [("story00_overview", "NARRATIVE", "One biological sample, four technical lanes. The full BAM now exists; the QC below keeps its original L001 scope.")],
    "01": [("story00_overview", "NARRATIVE", "The frozen A0 ranking and its A0-FREQFIX revision are separate stages. Several tools agreeing on the same VCF is not biological replication.")],
    "02": [("story02_variant_card", "SYNTHESIS", "Two prioritised alleles; phase unresolved. Cis and trans are conceptual scenarios, not measured haplotypes.")],
    "03": [("story10_mechanism", "SYNTHESIS", "A functional hypothesis; there is no protein assay and no demonstrated rescue in this case.")],
    "04": [("story03_second_allele", "SYNTHESIS", "GO 2B closure: no CNVpytor RD+BAF call and no xTea or SCRAMble MEI call overlaps the BUB1B gene body. A complex insertion is not excluded."),
           ("story13_next_experiment", "SYNTHESIS", "RNA-seq and long reads are proposals. The AlphaGenome tracks below are existing predictions, not measured RNA and not a completed EXP-024 calibration.")],
    "05": [("story13_next_experiment", "SYNTHESIS", "Decision map. The residual phenotype also needs clinical review; it does not establish a second diagnosis.")],
    "06": [("story04_evidence_context", "SYNTHESIS", "The case WGS, the simulation and the literature answer different questions and are never merged.")],
    "07": [("story12_safety_gates", "SYNTHESIS", "A surviving cell is not a rescued cell: fewer new errors per completed mitosis and survival of unstable cells are separate questions. A proposed rule shared with other teams, not an experimental result.")],
}


def integrate(nb, name):
    """Idempotent; keeps every original cell and its outputs."""
    nb.cells = [c for c in nb.cells if TAG not in c.metadata.get("tags", [])]
    additions = []
    for slug, kind, caption in PANELS.get(Path(name).name[:2], []):
        image = ROOT / "figures/pub" / (slug + ".png")
        encoded = base64.b64encode(image.read_bytes()).decode("ascii")
        origin = "MEASURED / DERIVED" if kind == "DATA" else "DERIVED / EXTERNAL"
        cell = nbformat.v4.new_markdown_cell(
            f"![{caption}](attachment:{slug}.png)\n\n"
            f"**`{kind}`, {origin}.** {caption} "
            "Reviewed figure, embedded without re-running the original analysis, "
            "[sources and limits](../docs/STORYBOARD.md), "
            "[figure QA](../PUBLICATION_FIGURE_QA.md)",
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
