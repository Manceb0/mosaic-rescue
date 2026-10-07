#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagramas de síntesis de MOSAIC RESCUE; sin mediciones ni análisis nuevos.

La selección editorial y sus límites se declaran en docs/STORYBOARD.md.
Las fuentes se verifican ANTES de dibujar. Actualizar el manifest de fuentes exige
revisar las conclusiones: el renderer no lo actualiza automáticamente.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.figures import style as S

INK = "#163344"
TEAL = "#00695C"
BLUE = "#145B8A"
AMBER = "#86520B"
RED = "#A43A35"
MUTED = "#536572"
LIGHT = "#F3F6F8"
PALE = "#EAF5F1"
WARM = "#FCF3E6"

SPECS = [
    ("story00_overview", "NARRATIVE", "One genome. A hypothesis. A test that can overturn it."),
    ("story02_variant_card", "SYNTHESIS", "Two alleles are not yet a proven biallelic cause."),
    ("story03_second_allele", "SYNTHESIS", "The second-allele question stays open."),
    ("story04_evidence_context", "SYNTHESIS", "Three evidence layers. Three different meanings."),
    ("story10_mechanism", "SYNTHESIS", "Correct the defect, or merely help cells tolerate it?"),
    ("story12_safety_gates", "SYNTHESIS", "A surviving cell is not a rescued cell."),
    ("story13_next_experiment", "SYNTHESIS", "The next experiment should change the decision."),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_sources():
    manifest = json.loads((ROOT / "docs/story_sources.sha256.json").read_text(encoding="utf-8"))
    if not manifest.get("sources"):
        raise ValueError("Story sources: manifest vacío")
    for source in manifest["sources"]:
        path = (ROOT / source["path"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f"Story source ausente o fuera del repositorio: {source['path']}")
        if digest(path) != source["sha256"]:
            raise ValueError(f"Story source cambió: {source['path']}; revisar la síntesis antes de dibujar")
    return manifest


def label(ax, x, y, value, size=14, color=INK, weight="normal", width=None, **kwargs):
    if width:
        value = "\n".join(textwrap.fill(line, width, break_long_words=False,
                                      break_on_hyphens=False) for line in value.split("\n"))
    return ax.text(x, y, value, fontsize=size, color=color, fontweight=weight,
                   va="top", linespacing=1.35, **kwargs)


def canvas(slug, title, subtitle, height=7.4):
    S.use()
    fig = plt.figure(figsize=(12, height))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 1200), ylim=(height * 100, 0))
    ax.axis("off")
    label(ax, 42, 24, "MOSAIC RESCUE  /  " + slug.replace("story", "").split("_")[0],
          10, TEAL, "bold")
    label(ax, 42, 62, title, 25, INK, "bold")
    label(ax, 42, 113, subtitle, 12, MUTED, width=126)
    label(ax, 42, height * 100 - 29,
          "READING GUIDE · Schematic, not a new measurement · Sources and limits: docs/STORYBOARD.md",
          9, MUTED)
    return fig, ax


def card(ax, x, y, w, h, tag, title, body, accent=TEAL, fill=LIGHT, dashed=False,
         size=13, title_size=18, width=33):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=10",
                          facecolor=fill, edgecolor=accent if dashed else "#C8D4DB",
                          linewidth=1, linestyle=(0, (4, 3)) if dashed else "solid")
    ax.add_patch(patch)
    ax.add_patch(Rectangle((x + 16, y + 20), 4, 17, facecolor=accent, edgecolor="none"))
    label(ax, x + 29, y + 20, tag, 10, accent, "bold")
    label(ax, x + 20, y + 53, title, title_size, INK, "bold")
    text = label(ax, x + 20, y + 99, body, size, INK, width=width)
    # Contrato de layout inspeccionable, además de la revisión visual.
    text._story_bounds = (x + 12, y + 90, x + w - 12, y + h - 10)
    return patch


def arrow(ax, start, end, dashed=False, color=MUTED):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15,
                                linewidth=1.5, color=color,
                                linestyle=(0, (4, 3)) if dashed else "solid"))


def strip(ax, y, tag, message, color=AMBER, fill=WARM, height=70):
    ax.add_patch(FancyBboxPatch((42, y), 1116, height,
                              boxstyle="round,pad=0,rounding_size=8",
                              facecolor=fill, edgecolor="none"))
    label(ax, 60, y + 15, tag, 11, color, "bold")
    label(ax, 60, y + 37, message, 12, INK)


def overview():
    fig, ax = canvas(SPECS[0][0], SPECS[0][2],
                     "From a genomic finding to a falsifiable preclinical experiment.", 7.1)
    card(ax, 42, 180, 350, 286, "01 / OBSERVE", "One blood genome",
         "4 sequencing lanes; 8 FASTQ\nOne biological sample\nGRCh38 reference\n\nNo parental, RNA or protein measurements available.",
         fill=PALE, width=34)
    card(ax, 425, 180, 350, 286, "02 / CHALLENGE", "BUB1B leads",
         "A0 #4 → A0-FREQFIX #1\nTruncating allele + missense\nPhase unresolved; missense VUS\n\nGO 2B completed. Complex insertion remains possible.",
         accent=BLUE, width=33)
    card(ax, 808, 180, 350, 286, "03 / DISCRIMINATE", "Test a safe rescue",
         "Confirm phase and mechanism.\nTest three experimental roles.\n\nMeasure chromosome instability AND clonogenic survival.",
         accent=AMBER, fill=WARM, width=32)
    arrow(ax, (395, 320), (422, 320)); arrow(ax, (778, 320), (805, 320))
    strip(ax, 498, "THE CENTRAL QUESTION",
          "Can the defect be corrected without increasing survival of genomically unstable cells?")
    label(ax, 60, 595, "AVAILABLE", 10, TEAL, "bold")
    label(ax, 60, 620, "WGS · phenotype · frozen analyses", 12)
    label(ax, 570, 595, "NEXT EVIDENCE", 10, AMBER, "bold")
    label(ax, 570, 620, "Phase · RNA / protein · functional and safety assays", 12)
    return fig


def variant_card():
    fig, ax = canvas(SPECS[1][0], SPECS[1][2],
                     "BUB1B is the leading causal hypothesis. Research curation is not a confirmed diagnosis.", 8.1)
    card(ax, 42, 177, 540, 290, "ALLELE A / RESEARCH CURATION", "Truncating allele · LP",
         "Likely pathogenic: 9 ACMG points.\nTranscript decay is predicted, not measured in this case.\n\nThis allele alone does not establish a recessive diagnosis.",
         fill=PALE, width=53, size=14)
    card(ax, 618, 177, 540, 290, "ALLELE B / UNRESOLVED", "Missense allele · VUS",
         "Conservation supports concern.\nNo variant-specific functional assay.\n\nPM1 not applied; PM3 blocked by phase; PS3 requires functional evidence.",
         accent=AMBER, fill=WARM, width=46, size=14)
    strip(ax, 494, "THE MISSING LINK: PHASE",
          "Are the alleles on opposite copies of BUB1B? Parental genotypes or long-molecule phasing can answer.")
    label(ax, 60, 595, "TRANS SCENARIO (UNMEASURED)", 11, TEAL, "bold")
    label(ax, 60, 620, "Supports configuration; VUS still needs evidence.", 12)
    label(ax, 635, 595, "CIS SCENARIO (UNMEASURED)", 11, RED, "bold")
    label(ax, 635, 620, "Overturns this two-allele recessive explanation.", 12)
    # Esquema conceptual de fase: posiciones arbitrarias, nunca haplotipos del caso.
    for x, marks in ((145, ((205, 666, "A"), (325, 708, "B"))),
                     (720, ((780, 666, "A"), (900, 666, "B")))):
        for y in (666, 708):
            ax.plot([x, x + 300], [y, y], color=MUTED, lw=3, solid_capstyle="round")
            label(ax, x - 85, y - 9, "copy 1" if y == 666 else "copy 2", 11, MUTED)
        for mx, my, name in marks:
            ax.plot(mx, my, marker="s" if name == "A" else "o", ms=14,
                    color=TEAL if name == "A" else AMBER, mec="white", mew=1)
            ax.text(mx, my, name, fontsize=9, color="white", weight="bold", ha="center", va="center")
    label(ax, 60, 750, "Conceptual alternatives only: no measured haplotypes, genomic positions or parental genotypes.", 11, MUTED)
    return fig


def second_allele():
    fig, ax = canvas(SPECS[2][0], SPECS[2][2],
                     "GO 2B tested structural explanations with short reads. Each negative has a defined scope.", 7.6)
    rows = [
        ("Regulatory SNV / indel", "No supported candidate in the assessed branch", "AlphaGenome is prediction, not patient RNA"),
        ("CNV · read depth + BAF", "No emitted call overlaps the BUB1B gene body", "CNVpytor result under this assay"),
        ("Mobile-element insertion", "No xTea / SCRAMble call overlaps the body", "Complex insertion remains possible"),
        ("Read-level metrics", "Body and flanks compared descriptively", "No inferential excess/no-excess threshold"),
    ]
    label(ax, 60, 170, "QUESTION", 10, MUTED, "bold")
    label(ax, 385, 170, "OBSERVED / REPORTED", 10, MUTED, "bold")
    for i, (name, result, limit) in enumerate(rows):
        y = 199 + 93 * i
        ax.add_patch(Rectangle((42, y), 1116, 82, facecolor=LIGHT if i % 2 == 0 else "white", edgecolor="none"))
        label(ax, 60, y + 19, name, 13, INK, "bold", width=29)
        label(ax, 385, y + 13, result, 14, TEAL)
        label(ax, 385, y + 44, limit, 12, MUTED)
    strip(ax, 594, "NOT DETECTED UNDER THIS ASSAY ≠ EXCLUDED",
          "Next: resolve phase; investigate RNA and long molecules if the second-allele question persists.")
    label(ax, 60, 687, "External precedent: Kawakami et al. · PMID 38102195 · A different case, not our result.", 11, MUTED)
    return fig


def evidence_context():
    fig, ax = canvas(SPECS[3][0], SPECS[3][2],
                     "PCS/MVA evidence context: no patient-specific mosaic fraction or cell-lineage reconstruction.", 7.2)
    card(ax, 42, 181, 350, 325, "PATIENT / AGGREGATED WGS", "What was measured",
         "Chromosome-level RD and BAF.\nShort-read signals at the locus.\n\nThese summarize blood DNA; they do not count abnormal cells.",
         fill=PALE, width=29, size=14)
    card(ax, 425, 181, 350, 325, "SIMULATION / MODEL", "What was tested",
         "Mixing homolog directions can recenter signed BAF.\n\nThe absolute-statistic collapse was depth-confounded. No validated detector resulted.",
         accent=BLUE, width=32, size=14)
    card(ax, 808, 181, 350, 325, "LITERATURE / OTHER CASES", "What informs the test",
         "RNA and long reads resolved a hidden insertion in another BUB1B case.\n\nThis motivates a test; it does not transfer that finding to this patient.",
         accent=AMBER, fill=WARM, width=32, size=14)
    strip(ax, 539, "KEEP THE LAYERS SEPARATE",
          "A flat aggregate summary cannot establish or exclude cytogenetic MVA; simulation is not patient evidence.")
    label(ax, 60, 639, "Still needed: suitable controls, phase, cell-level validation where relevant, and functional measurements.", 12)
    return fig


def mechanism():
    fig, ax = canvas(SPECS[4][0], SPECS[4][2],
                     "Proposed mechanism for this case: L0–L1. Functional support comes from other alleles and systems.", 8.2)
    card(ax, 42, 180, 350, 265, "CASE / HYPOTHESIS", "Candidate allele pair",
         "Truncation: transcript decay predicted.\nMissense: instability is one possibility.\n\nPhase and function unresolved.",
         accent=BLUE, width=33)
    card(ax, 425, 180, 350, 265, "TO MEASURE", "Residual BUBR1",
         "Abundance, turnover and checkpoint function.\n\nNormal abundance would weaken instability, not rule out every functional defect.",
         accent=AMBER, fill=WARM, dashed=True, width=32)
    card(ax, 808, 180, 350, 265, "EXTERNAL / FUNCTIONAL", "Segregation errors",
         "Published MVA-cell experiments link BUBR1 dysfunction to errors.\n\nThe specific causal chain remains untested in this case.",
         width=33)
    arrow(ax, (395, 310), (422, 310), dashed=True)
    arrow(ax, (778, 310), (805, 310), dashed=True)
    card(ax, 42, 480, 540, 214, "T2-A / UPSTREAM QUESTION", "Restore useful function?",
         "Allele-directed or proteostasis hypotheses require molecular engagement and functional rescue.",
         fill=PALE, width=51, size=14)
    card(ax, 618, 480, 540, 214, "T2-B / SAFETY CHALLENGE", "Increase stress tolerance?",
         "Cell survival may improve while chromosome instability persists. That is not sufficient rescue.",
         accent=RED, fill=WARM, width=51, size=14)
    label(ax, 60, 729, "Required together: molecular function · chromosome instability · clonogenic survival · viability", 13, INK, "bold")
    label(ax, 60, 758, "External support: PMID 20516114, 25205676. Counterexample to drug translation: PMID 34481829.", 10, MUTED)
    return fig


def safety():
    # Two separate questions: does the intervention lower NEW segregation errors (rescue gate),
    # and does it let chromosomally unstable cells survive or expand (tolerance veto)?
    fig, ax = canvas(SPECS[5][0], SPECS[5][2],
                     "Proposed decision rule for preclinical experiments. No intervention has been tested in this case.", 8.2)
    strip(ax, 162, "BEFORE ANY RESULT IS SCORED",
          "Molecular engagement shown; errors counted per completed mitosis at matched proliferation;\n"
          "viability and controls interpretable. Otherwise it is a false rescue or uninterpretable.", height=86)
    x_row, x1, x2, cw = 42, 330, 753, 405
    y1, y2, ch = 308, 478, 160
    label(ax, x1 + 8, 272, "Survival of unstable cells: NOT INCREASED", 12, INK, "bold")
    label(ax, x2 + 8, 272, "Survival of unstable cells: INCREASED", 12, RED, "bold")
    label(ax, x_row, y1 + 20, "New segregation errors\nper completed mitosis:\nLOWER", 14, INK, "bold")
    label(ax, x_row, y2 + 20, "New segregation errors\nper completed mitosis:\nNOT LOWER", 14, INK, "bold")
    card(ax, x1, y1, cw, ch, "ADVANCE", "Candidate rescue",
         "Go to the next, independent test.", accent=TEAL, fill=PALE, width=38)
    card(ax, x2, y1, cw, ch, "VETO", "Correction with a cost",
         "Fewer errors do not license survival of unstable cells.", accent=RED, fill=WARM, width=38)
    card(ax, x1, y2, cw, ch, "REJECT", "No rescue",
         "The route does not correct the defect.", accent=MUTED, fill=LIGHT, width=38)
    card(ax, x2, y2, cw, ch, "VETO", "Tolerance",
         "Unstable cells survive better without correction.", accent=RED, fill=WARM, width=38)
    label(ax, 60, 662, "Controls belong to the experiment: vehicle, genetic rescue control, matched euploid and "
          "aneuploid context, direct molecular readout.", 12, INK, width=125)
    label(ax, 60, 712, "Shared rule: another public repository in this hackathon defines rescue the same way. "
          "Not claimed as new. Thresholds must be fixed before testing; this diagram invents none.", 11, MUTED, width=135)
    return fig


def next_experiment():
    fig, ax = canvas(SPECS[6][0], SPECS[6][2],
                     "Choose the assay for the unresolved question. These are proposed experiments, not completed results.", 8.1)
    rows = [
        ("PHASE", "Parental genotypes or long-molecule phasing", "A cis result would overturn this pair; a trans result would support configuration."),
        ("MISSENSE", "BUBR1 abundance, turnover and checkpoint assay", "Separates instability from other functional defects."),
        ("HIDDEN ALLELE", "Appropriate RNA-seq + targeted long reads", "Can reveal a missed insertion and its transcript effect."),
        ("SAFE RESCUE", "Molecular engagement + CIN + clonogenic survival", "Improved survival of unstable cells vetoes the route."),
    ]
    for i, (tag, assay, decision) in enumerate(rows):
        y = 178 + i * 114
        ax.add_patch(Rectangle((42, y), 1116, 98, facecolor=PALE if i == 0 else LIGHT, edgecolor="none"))
        label(ax, 60, y + 20, tag, 11, TEAL if i == 0 else BLUE, "bold")
        label(ax, 255, y + 16, assay, 16, INK, "bold")
        label(ax, 255, y + 55, decision, 12, MUTED)
    strip(ax, 665, "WHY THIS ORDER?",
          "Phase has the highest immediate leverage on the causal pair; mechanism and safety are separate tests.")
    return fig


BUILDERS = [overview, variant_card, second_allele, evidence_context, mechanism, safety, next_experiment]


def audit_layout(fig):
    """Comprueba que el texto de cada tarjeta cabe; complementa la inspección visual."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    errors = []
    for ax in fig.axes:
        for text in ax.texts:
            if not hasattr(text, "_story_bounds"):
                continue
            x0, y0, x1, y1 = text._story_bounds
            p0, p1 = ax.transData.transform((x0, y0)), ax.transData.transform((x1, y1))
            box = text.get_window_extent(renderer)
            if box.x0 < p0[0] - 1 or box.x1 > p1[0] + 1 or box.y0 < p1[1] - 1 or box.y1 > p0[1] + 1:
                errors.append(text.get_text().splitlines()[0])
    if errors:
        raise ValueError("Texto fuera de tarjeta: " + "; ".join(errors))


def render_all():
    sources = verify_sources()
    results = {}
    manifest = {"method": "Editorial synthesis only; no new analysis", "sources": sources["sources"],
                "base_commit": sources["base_commit"], "source_state": sources["source_state"],
                "renderer": "src/figures/story.py", "renderer_sha256": digest(__file__), "figures": []}
    for (slug, classification, takeaway), builder in zip(SPECS, BUILDERS):
        fig = builder()
        audit_layout(fig)
        out = S.export(fig, slug, classification, "DERIVED+EXTERNAL")
        results[slug] = out
        manifest["figures"].append({"figure_id": slug, "classification": classification,
                                   "evidence_mode": "DERIVED+EXTERNAL", "claim_ceiling": takeaway,
                                   "forbidden_inference": "Patient RNA/protein/phase measured, diagnosis or therapeutic rescue established",
                                   "output_svg": out["svg"], "output_sha256": digest(out["svg"]),
                                   "output_png": out["png"], "png_sha256": digest(out["png"])})
        plt.close(fig)
        print(f"  {slug}: layout OK; {classification}; verified source hashes")
    (ROOT / "docs/story_figure_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    render_all()
