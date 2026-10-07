#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders every publication figure at FULL size, without running a notebook.

Why this is separate from the notebooks
    A figure that can only be produced by executing a notebook cannot be checked
    at full size, cannot be regenerated for a poster, and cannot be diffed. Each
    hero now lives in its own module with a `load_and_build()`; the notebook
    calls the same function it does.

Output
    figures/pub/<slug>.svg   vector, text kept as text
    figures/pub/<slug>.png   300 dpi
    figures/pub/thumb/<slug>.png   a SEPARATE small render for the index
"""
from __future__ import annotations
import sys, time

sys.path.insert(0, ".")
from src.figures import style as S                                     # noqa: E402

# Dos ejes separados, no uno:
#   figure class     que tipo de objeto es la figura
#   evidence origin  de donde viene lo que hay dentro
# La matriz HPO es DATA y a la vez MEASURED+EXTERNAL+DERIVED; colapsarlos
# la hacia parecer 'datos del paciente'. Track 2 tenia el problema inverso.
#
# (module, slug, notebook, figure class, evidence origin, takeaway)
FIGURES = [
    ("fig12_ablation", "fig12_baf_factorial_ablation", "06_MOSAIC_AND_MITOREAD",
     "SIMULATION", "SIMULATED", "Post-hoc factorial ablation separates homolog direction and depth effects; no new simulation."),
    ("fig00_qc", "fig00_fastq_qc", "00_DATA_REALITY", "DATA", "MEASURED",
     "Reads are fit for use: 149 bp invariant, GC 41.3 % against the genome's 41 %, "
     "92.9 % of bases at Q30+, and quality degrades from 4.52 % to 13.29 % non-Q37."),
    ("fig01_manhattan", "fig01_prioritization_genomewide", "01_TRACK1_GENOME_WIDE",
     "DATA", "MEASURED+DERIVED",
     "BUB1B competes against a 6,321-gene universe and ranks #4 in the frozen A0. "
     "The y axis is a prioritization score, not a p-value."),
    ("fig02_browser", "fig02_gene_browser", "02_BUB1B_ALLELE_CURATION",
     "DATA", "EXTERNAL+MEASURED",
     "No demonstrable hotspot anywhere in the gene: 1,497 ClinVar missense, 95.3 % VUS, "
     "one P/LP, so PM1 does not apply here or anywhere else."),
    ("fig03_pocket", "fig03_pocket_and_conservation", "03_BUBR1_MECHANISM",
     "MODEL_OUTPUT", "PREDICTED+EXTERNAL",
     "The candidate side chain anchors a pocket of 9 residues with 3 candidate H-bonds, "
     "at pLDDT 91 and in a column carrying 4.04 of 4.32 possible bits."),
    ("fig04_tracks", "fig04_alphagenome_rna_splicing", "04_HIDDEN_SECOND_ALLELE",
     "MODEL_OUTPUT", "PREDICTED",
     "ALT tracks REF across every frozen prediction. Splicing, the modality that "
     "decided the hypothesis, shows neither gain nor loss of a site."),
    # Post-freeze characterisation of the SAME frozen candidate. Both read
    # work/alphagenome/{ism,contacts}/, written by src/model_outputs/ under a
    # pre-run manifest; neither re-queries the model.
    ("fig04_ism", "fig04I_alphagenome_ism", "04_HIDDEN_SECOND_ALLELE",
     "MODEL_OUTPUT", "PREDICTED",
     "Under the pre-declared splice-site readout the candidate ranks 62 of 256 positions "
     "for local sensitivity and the window's most responsive base is 125 bp away. "
     "Model attribution only: it characterises the frozen negative, it does not add evidence."),
    ("fig04_contacts", "fig04C_alphagenome_contact_maps", "04_HIDDEN_SECOND_ALLELE",
     "MODEL_OUTPUT", "PREDICTED",
     "In the pre-declared skin-fibroblast track, ALT − REF reaches 1.1 % of the REF maximum, "
     "below the 5 % threshold fixed before the prediction; the track ranks 8 of 28 on the "
     "official local-disruption score. Predicted contacts, not Hi-C and not the patient."),
    ("fig05_hpo", "fig05_hpo_disease_matrix", "05_RESIDUAL_PHENOTYPE",
     "DATA", "MEASURED+EXTERNAL+DERIVED",
     "Among seven recorded traits, nephrocalcinosis is the one with neither HPO "
     "annotation nor MVA1 literature support, while Bartter-type models do cover it. Two traits "
     "cannot be judged (PARKED, not negative)."),
    ("fig06_baf", "fig06_baf_cancellation", "06_MOSAIC_AND_MITOREAD",
     "SIMULATION", "SIMULATED",
     "A variegated genome re-centres on BAF 0.5 with the same aneuploidy present, and "
     "the unphased BAF statistic loses power as the event grows."),
    ("fig07_evidence", "fig07_track2_evidence_matrix", "07_TRACK2_SAFE_RESCUE",
     "CURATED_EVIDENCE", "EXTERNAL+DERIVED",
     "Bridge 7 is the translational gap and bridge 8 the safety gap: 61 of 80 evidence "
     "cells are empty and no overall score is computed."),
    ("fig08_portfolio", "fig08_track2_portfolio", "07_TRACK2_SAFE_RESCUE",
     "CURATED_EVIDENCE", "EXTERNAL+DERIVED",
     "Three interventions in three different roles, not a ranking: azithromycin is the only "
     "allele-directed arm, arimoclomol is informative by failing, and sirolimus exists to "
     "probe the safety boundary. None is proposed for administration."),
    # GO 2B, falsificacion estructural. No salen de un notebook: leen artefactos congelados
    # bajo work/callers/final/ y src/figures/frozen.py aborta si un sha256 no coincide.
    ("fig09_cnv_chromosomes", "fig09_cnvpytor_chromosome_rd_baf", "GO2B_STRUCTURAL_FALSIFICATION",
     "DATA", "MEASURED+DERIVED",
     "Chromosome-level RD and BAF of the patient's blood WGS, descriptive only: autosomal medians in a "
     "narrow band, uniform aggregated BAF. No mosaic fraction is estimated and no aneuploidy is asserted "
     "or excluded."),
    ("fig10_bub1b_readlevel", "fig10_bub1b_readlevel_assay", "GO2B_STRUCTURAL_FALSIFICATION",
     "DATA", "MEASURED+DERIVED",
     "Short-read breakpoint metrics for the BUB1B body and two equal-length flanks, side by side. No "
     "inferential excess/no-excess threshold was defined, and a complex insertion is not excluded."),
    # EXP-027 Phase 1 (r2), resultado sellado: lee phase1_report.json y la reproducción post-hoc,
    # ambos comprobados por SHA256. Enseña el FAIL; el paciente nunca se analizó.
    ("fig13_exp027_phase1", "fig13_exp027_phase1_result", "EXP027_PHASE1",
     "DATA", "EXTERNAL+DERIVED",
     "High sensitivity (0.943 at δ = 0.10), failed calibration (APR 249/995 = 25.0 % vs 5 % nominal): "
     "method validation FAIL, so the patient-level A1 test was not performed."),
    # Track 1, la idea central: lee el pkl congelado, la anotación (A0-FREQFIX recalculado con la fórmula
    # del notebook 01) y el baseline de Exomiser, los tres comprobados por SHA256.
    ("fig14_track1_convergence", "fig14_track1_convergence", "01_TRACK1_GENOME_WIDE",
     "DATA", "MEASURED+EXTERNAL+DERIVED",
     "Without a gene panel, BUB1B is top-ranked in 14 of 15 sensitivity analyses of the same genome and Exomiser places it #2 of 398 (same VCF). It is #4 in "
     "the frozen A0 and #1 in A0-FREQFIX; both are reported. Strong candidate, not a diagnosis."),
    ("fig11_mei_sv_adjudication", "fig11_mei_sv_adjudication_map", "GO2B_STRUCTURAL_FALSIFICATION",
     "DATA", "MEASURED+EXTERNAL+DERIVED",
     "The four alternative structural signals near BUB1B, their breakpoint partners and the gene context "
     "of each. None overlaps the gene body; no retrocopy architecture is established."),
]

EXTRA = [("fig04_tracks", "fig04S_alphagenome_accessibility_tf",
          "04_HIDDEN_SECOND_ALLELE", "MODEL_OUTPUT", "PREDICTED",
          "Accessibility and TF tracks, same rules, kept separate so nine tracks stay "
          "legible.")]


def main():
    import importlib
    done = {}
    for mod, slug, nb, cls, origin, _tl in FIGURES:
        t0 = time.time()
        m = importlib.import_module(f"src.figures.{mod}")
        out = m.load_and_build()
        if mod == "fig04_tracks":
            figs, _ = out
            done[slug] = S.export(figs["main"][0], slug, cls, origin)
            e = EXTRA[0]
            done[e[1]] = S.export(figs["supp"][0], e[1], e[3], e[4])
        else:
            fig, _ = out
            done[slug] = S.export(fig, slug, cls, origin)
        print(f"  {slug:<40}{time.time() - t0:6.1f}s  "
              f"{done[slug]['size_in'][0]}x{done[slug]['size_in'][1]} in")

    print()
    # Capa narrativa: síntesis verificadas contra sus fuentes, no resultados nuevos.
    from src.figures.story import render_all as render_story
    done.update(render_story())
    print(f"  {'figure':<40}{'FIGURE CLASS':<20}EVIDENCE ORIGIN")
    print("  " + "-" * 92)
    for slug, r in done.items():
        print(f"  {slug:<40}{r['figure_class']:<20}{r['evidence_origin']}")
    print(f"\n  {len(done)} figures written to {S.FULL_DIR} (SVG + PNG 300 dpi) "
          f"and {S.THUMB_DIR}")
    return done


if __name__ == "__main__":
    main()
