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
    ("fig00_qc", "fig00_fastq_qc", "00_DATA_REALITY", "DATA", "MEASURED",
     "Reads are fit for use: 149 bp invariant, GC 41.3 % against the genome's 41 %, "
     "92.9 % of bases at Q30+, and quality degrades from 4.52 % to 13.29 % non-Q37."),
    ("fig01_manhattan", "fig01_prioritization_genomewide", "01_TRACK1_GENOME_WIDE",
     "DATA", "MEASURED+DERIVED",
     "BUB1B competes against a 6,321-gene universe and ranks #4 in the frozen A0. "
     "The y axis is a prioritization score, not a p-value."),
    ("fig02_browser", "fig02_gene_browser", "02_BUB1B_ALLELE_CURATION",
     "DATA", "EXTERNAL+MEASURED",
     "No demonstrable hotspot anywhere in the gene: 1,497 ClinVar missense, 98 % VUS, "
     "one P/LP, so PM1 does not apply here or anywhere else."),
    ("fig03_pocket", "fig03_pocket_and_conservation", "03_BUBR1_MECHANISM",
     "MODEL_OUTPUT", "PREDICTED+EXTERNAL",
     "The candidate side chain anchors a pocket of 9 residues with 3 candidate H-bonds, "
     "at pLDDT 91 and in a column carrying 4.04 of 4.32 possible bits."),
    ("fig04_tracks", "fig04_alphagenome_rna_splicing", "04_HIDDEN_SECOND_ALLELE",
     "MODEL_OUTPUT", "PREDICTED",
     "ALT tracks REF across every frozen prediction. Splicing, the modality that "
     "decided the hypothesis, shows neither gain nor loss of a site."),
    ("fig05_hpo", "fig05_hpo_disease_matrix", "05_RESIDUAL_PHENOTYPE",
     "DATA", "MEASURED+EXTERNAL+DERIVED",
     "Nephrocalcinosis is the one proband term with neither HPO annotation nor MVA1 "
     "literature support, while Bartter-type models do cover it."),
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
    print(f"  {'figure':<40}{'FIGURE CLASS':<20}EVIDENCE ORIGIN")
    print("  " + "-" * 92)
    for slug, r in done.items():
        print(f"  {slug:<40}{r['figure_class']:<20}{r['evidence_origin']}")
    print(f"\n  {len(done)} figures written to {S.FULL_DIR} (SVG + PNG 300 dpi) "
          f"and {S.THUMB_DIR}")
    return done


if __name__ == "__main__":
    main()
