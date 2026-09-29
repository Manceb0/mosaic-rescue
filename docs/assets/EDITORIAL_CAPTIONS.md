# Editorial figure captions and sources

Conceptual illustrations were generated with AI and reviewed for scientific meaning. Mini-plots and assay glyphs are schematic; quantitative evidence remains in the original scientific figures. Production prompts are maintained locally.


## Figure 02 — phase and function

Two independent uncertainties in the BUB1B hypothesis. A and B denote the prioritized truncating and missense variant records, respectively. The trans alternative places A and B on different homologous copies; the cis alternative places both on one copy. Neither configuration is established. Segment lengths, marker positions and h1/h2 labels are schematic and do not specify patient coordinates or parental origin. Parental phasing is proposed. Independently, the missense allele remains a VUS and its functional effect is unresolved. Protein-abundance, checkpoint-function and assay symbols denote proposed readouts, not measured bands, patient microscopy or experimental results. Phase alone does not resolve the VUS.

## Visual and semantic review

- Trans: A on h1, B on h2; cis: A and B on h1, h2 unmarked.
- Both phase configurations explicitly marked possible, neither established.
- Parental and functional testing marked proposed.
- Protein-abundance symbol is an illustrative glyph, not a blot or quantitative comparison.
- Existing first overview remains unchanged.

## Figure 03 — ranking audit

Asset: `mosaic-03-ranking-audit.png`. Placement: README chapter 2, research-story candidate section immediately before the actual genome-wide plot.

**Paper caption:** The original frozen A0 analysis places BUB1B fourth. An audit found missing frequency annotations for common alleles in the three higher-ranked genes. Repair of 33 allele annotations yields BUB1B rank one in the later A0-FREQFIX sensitivity analysis; the original analysis is retained. Exomiser ranks BUB1B second among 398 distinct genes using the same VCF. Agreement is methodological, not independent biological replication. Ranks are actual reported analysis outputs; read glyphs, table cells and rank bars are schematic and encode no quantitative scores. “Aligned reads (subset)” is an illustrative glyph, not a patient alignment screenshot. Phase and missense function remain unresolved.

Sources: [Track 1 report, sections 1–3](../../reports/TRACK1_REPORT.md), [quantitative genome-wide plot](../../figures/pub/fig01_prioritization_genomewide.svg), [notebook 01](../../notebooks/01_TRACK1_GENOME_WIDE.ipynb).
Review: #4/#1/#2 of 398 and 33 annotations match report; Exomiser has independent method branch from same source; original A0 not overwritten.

## Figure 04 — bounded hidden-allele search

Asset: `mosaic-04-hidden-allele.png`. Placement: README chapter 3, research-story section between predictions and mosaicism methods.

**Paper caption:** Parallel computational investigations constrain a hidden-allele hypothesis without establishing its absence. AlphaGenome outputs lack convincing support for the assessed regulatory candidate; this is not a global exclusion of splicing defects. Within the scoped BUB1B gene-body search, CNVpytor RD+BAF emitted no overlapping CNV and xTea/SCRAMble emitted no overlapping MEI call. The read-level assay compares the body with matched flanks and remains descriptive, without an inferential excess/no-excess threshold. Complex insertion remains unresolved. RNA and targeted long-read investigations are proposed. GO 2B is closed within its frozen scope; AE2 population lookup was not executed because of data policy. Miniature tracks, read alignments and RNA/long-read glyphs are schematic, not measured plots or evidence of an insertion.

Sources: [Track 1 report, sections 7 and 7b](../../reports/TRACK1_REPORT.md), [read-level metrics](../../figures/pub/fig10_bub1b_readlevel_assay.svg), [frozen artifact manifest](../go2b_final_artifacts.sha256.json).
Review: corrected unsupported tumor/normal wording to one blood sample; removed sequence-to-CNV branch; corrected read-level scope to body plus matched flanks. This overview does not enumerate every structural caller or raw genome-wide record.

## Figure 05 — proposed rescue experiment

Asset: `mosaic-05-rescue-test.png`. Placement: README chapter 5 and research-story rescue section beside evidence/portfolio material.

**Paper caption:** Proposed preclinical discrimination of three experimental roles: azithromycin as an allele-directed hypothesis, arimoclomol as a falsification sentinel and sirolimus as an adversarial safety comparator. Vehicle is the negative control; constitutively active HSF1 is a contextual genetic positive control and HSP70 overexpression is a mechanistic comparator. Control suitability must be established in the experimental system. Molecular engagement, new errors per completed mitosis at matched proliferation, clonogenic survival and viability are read jointly. Unsupported mechanism rejects the proposed route; increased survival of unstable cells triggers a safety veto. Improved function and reduced instability without increased unstable-cell survival support further preclinical testing, not clinical use. Symbols depict proposed readouts, not molecular structures, colony counts or observed treatment effects. No thresholds, exposures or efficacy results are encoded. Other inconclusive outcomes are possible; this is a decision schematic, not an exhaustive executable assay protocol.

Sources: [Track 2 report](../../reports/TRACK2_REPORT.md), [portfolio and controls](../../figures/pub/fig08_track2_portfolio.svg), [evidence matrix](../../figures/pub/fig07_track2_evidence_matrix.svg).
Review: three roles, three controls and four readouts present; contextual-control qualification retained; rejection and veto terminate separately from conditional advancement.

## Figure 06 — next experiments

Asset: `mosaic-06-next-experiments.png`.

Five separate unresolved questions require distinct proposed observations. Parental genotyping or targeted long-molecule phasing addresses the configuration of the candidate pair; trans alone does not establish missense pathogenicity. Protein abundance, turnover and checkpoint function distinguish protein instability from other defects; normal abundance does not establish normal function. RNA and targeted genomic long reads can investigate a missed lesion and its transcript effect, without guaranteed detection. Rescue experiments require joint molecular, errors-per-completed-mitosis, survival and viability readouts at matched proliferation with controls; increased survival of unstable cells triggers a veto. All pedigrees, homologs, molecules, tracks and cells are illustrative and not patient measurements or observed outcomes.

Sources: [Track 1 report](../../reports/TRACK1_REPORT.md), [Track 2 report](../../reports/TRACK2_REPORT.md), [existing next-experiment synthesis generator](../../src/figures/story.py).
Review: corrected generated “Long-read transcript” to targeted genomic long read; removed outcome-like green coloring from survival cells. Proposed status and phase/function distinction retained.

## Figure 07 — compact research route

Asset: `mosaic-07-research-route.png`.

**Caption:** One case supports parallel variant, read and phenotype analyses. Variant-based models add hypotheses, while variant evidence also contributes directly to causal interpretation. Independent simulations evaluate method limits, not additional patient observations. Causal interpretation and external evidence inform conditional rescue hypotheses, safety criteria and proposed experiments. The endpoint is not a confirmed diagnosis or established safe therapy. Symbols, ranked bars and curves are schematic and encode no scores or effect sizes. The associated README branch table documents QC, annotation, frequency audit, Exomiser, allele recovery, CNV/SV/MEI, DMPK, MitoRead, residual phenotype, conservation, AlphaGenome, simulation and evidence curation without crowding the image. This is a conceptual architecture, not an executable dependency graph.

## Figure 08 — function or tolerance?

Asset: `mosaic-08-mechanism.png`.

**Caption:** Candidate BUB1B alleles may alter residual BUBR1 function, but the case-specific mechanism is unresolved. Functional restoration and increased tolerance of unstable cells are distinct proposed routes, not measured before/after outcomes. Restoring function must be distinguished from merely increasing tolerance: fewer new errors per completed mitosis at matched proliferation and clonogenic survival must be interpreted jointly. Engagement, viability and informative controls remain necessary and are shown in the companion assay figure. Increased survival of unstable cells is not evidence of safe rescue. Normal abundance would weaken the protein-instability route without excluding other functional defects. Read glyphs do not establish haplotypes; spindle, cell and dish drawings are conceptual, not patient cytogenetics, protein structures or colony counts.

Sources: [Track 1 report](../../reports/TRACK1_REPORT.md), [Track 2 report](../../reports/TRACK2_REPORT.md), [README branch inventory](../../README.md#what-each-branch-contributes).
Review: simulation isolated from case input; variant direct and model-mediated contributions visible; no organ-specific phenotype icons or safety checkmark; both mechanism routes converge on the same paired readouts; proposed status retained. Original deterministic figures remain registered for technical provenance but are no longer used at the replaced presentation locations.

## Proposed patient-derived screen and interpretation limits

Figures 00 and 06 ask “Can the patient become the screen?” as a future experimental question. The fifth row of Figure 06 proposes comparing lineages sharing the causal genotype, identifying a candidate mechanism associated with fewer new mitotic errors, and testing its transfer to vulnerable cells. New consented cell samples, lineage tracking, genotype verification and functional perturbation would be required. Sharing the causal genotype does not establish whole-genome identity or exclude acquired suppressor variants. Acceptance requires fewer new errors per completed mitosis at matched proliferation and passing the separate safety criteria. No patient lineages or protective mechanism have been measured here. Novelty remains unestablished; these safety principles are not claimed as an invention.

Generation, selection and sampling are a conceptual framework for interpreting an observed sample, not a fitted multiplicative equation. The current single bulk blood genome cannot separate those processes or establish which clone survived. This editorial revision neither reopens GO 2B nor reports a new simulation or phased-BAF analysis. Sources: [Track 2, section 9](../../reports/TRACK2_REPORT.md), [Track 1, section 7b](../../reports/TRACK1_REPORT.md).
