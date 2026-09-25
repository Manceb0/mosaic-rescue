# Figures 06–07 — captions and generation provenance

Built-in imagegen with the approved causal-workflow illustration as style reference. Original scientific plots, scripts and registered artifacts are preserved.

## Figure 06 — next experiments

Asset: `mosaic-06-next-experiments.png`.

Four separate unresolved questions require distinct proposed observations. Parental genotyping or targeted long-molecule phasing addresses the configuration of the candidate pair; trans alone does not establish missense pathogenicity. Protein abundance, turnover and checkpoint function distinguish protein instability from other defects; normal abundance does not establish normal function. RNA and targeted genomic long reads can investigate a missed lesion and its transcript effect, without guaranteed detection. Rescue experiments require joint molecular, segregation, survival and viability readouts with controls; increased survival of unstable cells triggers a veto. All pedigrees, homologs, molecules, tracks and cells are illustrative and not patient measurements or observed outcomes.

Sources: [Track 1 report](../../reports/TRACK1_REPORT.md), [Track 2 report](../../reports/TRACK2_REPORT.md), [existing next-experiment synthesis generator](../../src/figures/story.py).
Review: corrected generated “Long-read transcript” to targeted genomic long read; removed outcome-like green coloring from survival cells. Proposed status and phase/function distinction retained.

## Figure 07 — research route

Asset: `mosaic-07-research-route.png`.

Workstream architecture spanning case inventory/QC/reference checks, variant prioritization and curation, parallel BAM analyses, residual phenotype, model-based mechanism investigations, independent simulation stress tests, causal interpretation, externally informed rescue hypotheses and proposed measurements. The flow is an explanatory sequence, not a software dependency graph: Exomiser operates on the same VCF, not on the in-house rank output; technical recovery is a parallel BAM check, not an SV-caller output. The illustration groups context and model analyses; the adjacent README table supplies their result, source and limitation. Structural/AlphaGenome glyphs are conceptual, not actual molecular structures or quantitative outputs. No patient phase, functional assay, clinically validated rescue or detector superiority is claimed.

Sources: [README branch inventory](../../README.md#what-each-branch-contributes), [Track 1 report](../../reports/TRACK1_REPORT.md), [Track 2 report](../../reports/TRACK2_REPORT.md).
Review: removed unsupported generated bullet details (knockout/knockdown, phasing signals); corrected simulation description to synthetic BAF and post-hoc audit; removed misleading phenotype-to-structure and caller-to-technical-recovery arrows. Simulation has no incoming patient-data branch. Icon shapes do not encode actual data.

## Exact prompts

### Figure 06

Create next MOSAIC RESCUE illustration replacing a plain next-experiment table. Attached STYLE MASTER defines thin white edges, dark fine grid, muted frosted glass, subtle blue green amber interior reflections, crisp white sans serif. English, landscape16:9, professional technical scientific conceptual diagram. No connector balls, no bright neon, no white panels. Meaningful detailed small assay glyphs, not actual results.

Title "MOSAIC RESCUE"
Subtitle "Choose the experiment that changes the decision"
Small top status "Proposed measurements · not completed results".

Four parallel horizontal question-to-test-to-decision paths, aligned but visually airy with technical icons and slender dashed amber arrows. Do NOT connect rows as a compulsory sequence. Headers only "Question" / "Measurement" / "Decision".
ROW1: "Phase" with two neutral homologous segment glyphs, no assigned variants. Measurement "Parental genotyping" smaller "or targeted long-molecule phasing"; small family outline. Decision two side-by-side brief labels "Cis: this pair is insufficient" and "Trans: configuration supported". Smaller under both "Missense function remains unresolved". Give first row subtle emphasis with "First genetic priority".
ROW2: "Missense function" with blue diamond variant glyph. Measurement "BUBR1 abundance + turnover" and "Checkpoint function"; small neutral protein outline and spindle glyph. Decision "Distinguish instability from other defects". Small "Normal abundance does not prove normal function".
ROW3: "Hidden allele" with gapped read-alignment glyph. Measurement "RNA analysis + targeted long reads"; miniature schematic splice junction and uninterrupted long-read strand. Decision "Test for a missed lesion and transcript effect". Small "Detection is not guaranteed".
ROW4: "Safe rescue" with neutral empty assay-well glyph. Measurement "Engagement + segregation + survival"; small "Include viability and controls". Decision amber stop-bar with "More survival of unstable cells: veto". Small "Joint readouts, not viability alone".

Each row uses distinct thin-glass assay object, not four large opaque UI cards. Symmetrical line thickness, soft uniform local light. No invented data, no probabilities, drug doses, blot bands or real molecular structures. Use all text as specified, short accurate words readable, none cut off. Bottom footer "Conceptual decision map · phase, mechanism and safety answer different questions". The narrative is decision-relevant next experiments and their distinct interpretation, not a promise all experiments will resolve the case.

Targeted edit: replace Long-read transcript with Targeted genomic long read; make survival cell circles equally neutral.

### Figure 07

Generate a detailed scientific architecture illustration for MOSAIC RESCUE, replacing a Mermaid flowchart. Attached image is STYLE MASTER: continuous near-black fine grid, thin white frosted-glass rims, muted translucent charcoal panels, restrained soft directional blue/green/amber internal reflections, clean sans-serif English typography, slim precise arrows without glowing node balls. Landscape 16:9 high resolution, readable. Original composition, no fake plot data.

Title "MOSAIC RESCUE"
Subtitle "Behind the story: the complete research route"

This is a research-workstream map with 4 well-spaced parallel lanes across the image, plus shared synthesis and future output at right. Build coherent hierarchy, moderate amount of text, not tangled spaghetti.

LEFT narrow source column:
"One blood sample"
small "WGS + clinical phenotype"
minimal blood vial/read-stack and human outline.
Downstream small "Inventory · QC · GRCh38".
From these, branch blue case-data arrows into exactly THREE patient-analysis lanes:
TOP lane heading "Variant evidence":
"VCF annotation" → "Genome-wide ranking" → "Frequency audit · HPO · Exomiser" → "BUB1B curation".
Use small annotation-table/rank glyphs, not actual results. Within lane short amber note "Phase unresolved · missense VUS".
SECOND lane heading "Alignment evidence":
"Full-depth BAM" → "Technical allele recovery"
parallel grouped subbranches within same lane:
"CNV / SV / MEI · read metrics"
"DMPK screen · MitoRead"
small under second branch "Scope-limited / descriptive".
Do NOT imply technical recovery is necessary input to callers; these are parallel BAM analyses, use a bracket/branch if easier.
THIRD lane heading "Mechanism and phenotype":
"Residual phenotype review" from clinical input;
"Conservation · structural context" and "AlphaGenome predictions" from BUB1B candidate context via one green arrow. Group model-based outputs with small "Predictions, not validation".
Outputs of these three patient lanes converge via clean neutral lines on one central-right glass synthesis node:
"Causal interpretation"
small "Evidence + unresolved questions".
Do not claim confirmed diagnosis.
BOTTOM separate lane, has OWN source no incoming patient data arrow:
"Simulation assumptions" → "Mosaicism simulation + ablation" → "Method limits".
small "Post-hoc explanation audit". Its endpoint is method limits, not a patient mosaicism diagnosis; attach only by neutral dotted context line to synthesis if needed, preferably no arrow into drug hypotheses.

LOWER-RIGHT separate external-evidence source, small paper-stack glyph:
"External evidence + contradictions" enters frosted processing layer "Rescue hypotheses".
An amber dashed conditional link from Causal interpretation into Rescue hypotheses labeled "Conditional".
Rescue hypotheses → "Experimental roles + safety vetoes", which connects with dashed amber to the FINAL output alongside causal interpretation.
FINAL rightmost slender glass column:
"Next measurements"
small "Proposed"
4 short lines "Phase" / "Variant function" / "RNA / genomic long reads" / "Safe-rescue assay".
No arrow implying available samples or completed tests.

Very bottom one fine neutral provenance rail spanning width:
"Audit trail: frozen artifacts · source hashes · notebooks · reports".
Footer "Research architecture · not a literal execution graph · no diagnosis or rescue demonstrated".

Keep text exact and all branches distinguishable. One sample is not a cohort. Simulation independent from patient. MitoRead descriptive, not mitochondrial dysfunction. No missing BAM claim. No cell atlas, forecasts, measured resistant cells or therapeutic winner. Ref/alt visual glyphs schematic if any. Ensure no line crosses labels, arrow endpoints touch destinations, no branch enters an incorrect lane. Diagram should expose the full research breadth clearly while companion table carries implementation detail. Use restrained illuminated material uniform across modules, not flat white boxes.

### Figure 07 scientific correction

Correct attached research architecture. Preserve dark style, main headings, layout and source/output blocks. REMOVE ALL tiny bullet lists inside EVERY middle-lane submodule; generator invented details. Use ONLY these exact concise sublabels, no new bullet prose:
VCF annotation: "Consequence · frequency · quality"
Genome-wide ranking: "Panel-free prioritization"
Frequency audit · HPO · Exomiser: "Same VCF · complementary methods"
BUB1B curation: "Research LP + VUS"
Full-depth BAM: "Reconstructed alignment"
CNV / SV / MEI · read metrics: "Frozen scoped search"
DMPK screen · MitoRead: "Scope-limited / descriptive"
Technical allele recovery: "Both candidate alleles recovered" (REMOVE phasing signals; phase NOT resolved)
Residual phenotype review: "Unexplained features remain"
Conservation · structural context: "Evolutionary and structural hypotheses"
AlphaGenome predictions: "Sequence-based model outputs"
Simulation assumptions: "Homolog direction × depth"
Mosaicism simulation + ablation: "Synthetic BAF · post-hoc audit" (NO knockout, knockdown, variant-effect simulation or cell experiments)
Method limits: "No detector superiority established"
External evidence module: restructure its heading to "Rescue hypotheses", small second line "External evidence + contradictions"; remove bullet lists, keep document icon. This module combines conditional causal hypothesis with external sources, not the source papers themselves.
Experimental roles + safety vetoes: "Three roles · joint safety readouts".
Do not add any other small text.

Fix connections exactly:
Full-depth BAM independently fans to CNV/SV/MEI, DMPK/MitoRead, AND Technical allele recovery. No arrow from DMPK into allele recovery.
Remove green arrows from Residual phenotype review to conservation and AlphaGenome. Route ONE green thin line from BUB1B curation down the RIGHT margin of lanes to these two model/context submodules. Residual phenotype review independently contributes to causal interpretation using neutral line; it is not the model input.
Keep simulation independent of case input.
Keep amber conditional causal-interpretation -> Rescue hypotheses, and future output -> Next measurements. Keep audit footer. No fabricated details, no extra numbers, no broken spellings. Preserve labels fully readable and uncluttered; fewer words is intended.

Final localized correction: remove CNV/SV/MEI-to-technical-recovery and residual-phenotype-to-structural-context arrows; label technical recovery a parallel BAM check.
