# Publication figure QA

> One row per publication figure. The column that matters most is
> **possible misleading interpretation**, it is mandatory, and it is where a jury finds the
> problem before we do.
>
> Regenerate everything: `python src/figures/render_all.py` → `figures/pub/*.svg` (vector,
> text kept as text) + `*.png` at 300 dpi + a **separate** small render in `figures/pub/thumb/`.
> Index: `python src/nb/contact_sheet.py`.

## The standard these figures are held to

### fig12_baf_factorial_ablation

SIMULATION / SIMULATED. Renderer: `src/figures/fig12_ablation.py`.
Source: `work/mosaic/baf_ablation.json`, SHA256
`27fdcb62b0f2c82ef6492081eff88bcf68290b9ebc2994df32d227a6eea22f19` (checked before render).
Four readouts, shared rejection-proportion scale, all fractions of the four factorial
`scope=frac` arms. `scope=all` diagnostic clonal controls are deliberately outside this
view. Colour encodes direction with the project-wide concept colours (fixed = `S.CLONAL`
blue, mixed = `S.VARIEGATED` pink, as in fig06); line/marker encodes depth. Ticks mark the
tested fractions only. Error bars (2026-09-29) are Wilson 95 % intervals computed from the
frozen proportions and 200 replicates: post-freeze uncertainty visualization; no model rerun
and no decision threshold changed. Each interval is marginal; overlap is not a test of a
difference, and every arm of `src/mosaic/ablation_baf.py` uses the same seed (`SEED + 1`), so
replicates across conditions may be paired. Residual stated in the notebook caption: at 20 %,
matched depth, panel C, an unregistered post-hoc difference of 0.130 (mixed 0.565, fixed
0.435). No inferential claim is made; adjudicating it would need a separately preregistered
comparison that accounts for the pairing. The provenance strip was cut to two lines; the caveats it carried are in
the caption.
**Misreading to avoid:** preregistered confirmation, patient mosaic fraction or detector
superiority. The experiment is explicitly POST-HOC. SVG/PNG/thumbnail via standard export.

### September narrative integration

Seven editorial diagrams use a separate card layout and labelled navy/teal/amber
palette; these are synthesis, not additional scientific data plots. Source hashes
are checked by `src/figures/story.py` against `docs/story_sources.sha256.json`.
Output hashes and exact claim ceilings are in `docs/story_figure_manifest.json`.
All export SVG with text, PNG 300 dpi and thumbnails. Card text bounds are checked
programmatically; the seven full-size renders were inspected for legibility.

| Figure | Class | Shows | Misleading interpretation to avoid |
|---|---|---|---|
| `story00_overview` | NARRATIVE | Data → causal hypothesis → falsification → next assay | Proven diagnosis or rescue |
| `story02_variant_card` | SYNTHESIS | LP research curation, VUS, unresolved phase | The schematic cis/trans scenarios are measured haplotypes |
| `story03_second_allele` | SYNTHESIS | Scope of the closed structural search | Short reads excluded a complex insertion |
| `story04_evidence_context` | SYNTHESIS | Patient, simulation and external evidence | A cell fraction measured from aggregate WGS |
| `story10_mechanism` | SYNTHESIS | Competing functional hypotheses | External rescue proves this patient's mechanism |
| `story12_safety_gates` | SYNTHESIS | Proposed molecular, CIN and survival vetoes | Completed drug assays or clinical suitability |
| `story13_next_experiment` | SYNTHESIS | Assay matched to uncertainty | RNA/protein/parental measurements already available |

Notebook attachments import nine instances of these diagrams and one frozen
`fig09_cnvpytor_chromosome_rd_baf` image, with explicit captions. They do not
increase the count of executed output figures. Existing technical figures retain
their original data provenance and internal-sharing limits.

| | |
|---|---|
| **Language** | English inside every final figure. Notebooks explain in Spanish; a figure never mixes both. |
| **Panels** | `A B C D` top-left, outside the data area. Reading order is grid order. |
| **Type** | one family, one scale, 6.0 pt floor. No title banners inside the axes. |
| **Axes** | every axis labelled, every label carries its unit. |
| **Colour** | Okabe-Ito, colour-blind safe. Colour is never the only encoder, categories also differ by marker or dash. |
| **Grids** | hairline or absent. No grey page backgrounds. |
| **Caption** | lives in the notebook. Only a provenance strip sits on the figure, outside the axes. |
| **Metadata** | **two axes, both stamped on the figure**: `FIGURE CLASS` (what kind of object it is) and `EVIDENCE ORIGIN` (where what is inside came from). |
| **Export** | SVG (`svg.fonttype=none`, text stays text) + PNG 300 dpi + separate thumbnail. Dense track paths are `rasterized=True` inside the SVG; axes and text stay vector. |
| **Thumbnails** | never a downscale of the 300-dpi raster. The full-size figure is the deliverable; the contact sheet is an index. |

**Not negotiable:** nothing is fabricated. No blots, no microscopy, no karyotypes, no coverage
tracks, no Hi-C, and no confidence interval that nobody computed.

---

## The two metadata axes, and why they are not one

Collapsing them is how a figure starts lying about itself.

| | |
|---|---|
| **`FIGURE CLASS`** | what kind of object the figure is: `DATA` · `MODEL_OUTPUT` · `SIMULATION` · `CURATED_EVIDENCE` · `SYNTHESIS` · `NARRATIVE` |
| **`EVIDENCE ORIGIN`** | where the content came from: `MEASURED` · `DERIVED` · `EXTERNAL` · `PREDICTED` · `SIMULATED` |

Only the first four figure classes may be a notebook's primary scientific figure. Origins
combine with `+`. `src/figures/style.py::export()` refuses to write a figure that does not
declare both, and stamps both on the image so they survive a crop into a slide.

**The two cases that forced the split:**

- **Fig 6, the HPO matrix.** `FIGURE CLASS = DATA`, but `EVIDENCE ORIGIN =
  MEASURED+EXTERNAL+DERIVED`, the proband's own HPO terms, external disease models, and a
  Resnik value we computed. Under one label it read as "patient data". It is not.
- **Fig 8, the Track 2 matrix.** `FIGURE CLASS = CURATED_EVIDENCE`, `EVIDENCE ORIGIN =
  EXTERNAL+DERIVED`. Under one label it read as an experimental matrix. It is a versioned
  literature inventory.

| figure | FIGURE CLASS | EVIDENCE ORIGIN |
|---|---|---|
| `fig00_fastq_qc` | `DATA` | `MEASURED` |
| `fig01_prioritization_genomewide` | `DATA` | `MEASURED+DERIVED` |
| `fig02_gene_browser` | `DATA` | `EXTERNAL+MEASURED` |
| `fig03_pocket_and_conservation` | `MODEL_OUTPUT` | `PREDICTED+EXTERNAL` |
| `fig04_alphagenome_rna_splicing` | `MODEL_OUTPUT` | `PREDICTED` |
| `fig04S_alphagenome_accessibility_tf` | `MODEL_OUTPUT` | `PREDICTED` |
| `fig04I_alphagenome_ism` | `MODEL_OUTPUT` | `PREDICTED` |
| `fig04C_alphagenome_contact_maps` | `MODEL_OUTPUT` | `PREDICTED` |
| `fig05_hpo_disease_matrix` | `DATA` | `MEASURED+EXTERNAL+DERIVED` |
| `fig06_baf_cancellation` | `SIMULATION` | `SIMULATED` |
| `fig07_track2_evidence_matrix` | `CURATED_EVIDENCE` | `EXTERNAL+DERIVED` |
| `fig09_cnvpytor_chromosome_rd_baf` | `DATA` | `MEASURED+DERIVED` |
| `fig10_bub1b_readlevel_assay` | `DATA` | `MEASURED+DERIVED` |
| `fig11_mei_sv_adjudication_map` | `DATA` | `MEASURED+EXTERNAL+DERIVED` |
| `fig13_exp027_phase1_result` | `DATA` | `EXTERNAL+DERIVED` |
| `fig14_track1_convergence` | `DATA` | `MEASURED+EXTERNAL+DERIVED` |

---

## Fig 1 · FASTQ QC: `fig00_fastq_qc`

| | |
|---|---|
| **notebook** | `00_DATA_REALITY` |
| **source data** | lane L001, read 1, reproducible subsample, first 300 000 records |
| **n** | 300 000 reads · 149 bp · 44.7 M bases |
| **axes / units** | A: cycle (bp) × % of bases outside top bin · B: % GC per read × density · C: mean Phred per read × reads · D: cycle (bp) × % of bases at cycle |
| **statistic represented** | per-cycle occupancy of four discrete quality bins; per-read GC and mean quality; per-cycle base composition |
| **FIGURE CLASS** | `DATA` |
| **EVIDENCE ORIGIN** | `MEASURED` |
| **uncertainty represented?** | yes, the whole of panel A is the dispersion; C is a full distribution |
| **uncertainty quantified?** | yes for sampling (n stated); **no** for subsample-to-lane extrapolation |
| **possible misleading interpretation** | that good QC means the data are **sufficient**. It does not: five branches of the project are blocked by modalities that do not exist. Second risk: reading the four bins as a continuous quality distribution, two earlier versions of panel A did exactly that and had to be discarded. |
| **correction applied** | provenance strip states n, read length as the degenerate value it is, and Q30 fraction; panel A states the four bins by name; the notebook's decision cell says in as many words that fit ≠ sufficient |
| **full-size render checked?** | yes |

---

## Fig 2 · Genome-wide prioritization: `fig01_prioritization_genomewide`

| | |
|---|---|
| **notebook** | `01_TRACK1_GENOME_WIDE` |
| **source data** | `work/gw/mode_b_results_v4.pkl` (A0 **frozen**) + contig lengths read from the VCF header |
| **n** | 6 321 genes in the HIGH/MODERATE universe · 151 scored under an inheritance model |
| **axes / units** | A: chromosome, 1 Mb bins × A0 genetics-only prioritization score (dimensionless) · B: genes per Mb |
| **statistic represented** | a weighted sum of preregistered terms. **Not a test statistic.** |
| **FIGURE CLASS** | `DATA` |
| **EVIDENCE ORIGIN** | `MEASURED+DERIVED`, patient variant calls, plus a score we computed |
| **uncertainty represented?** | partly, the frozen/FREQFIX pair is stated, but no interval is drawn |
| **uncertainty quantified?** | **no**, and deliberately: there is no null distribution for this score |
| **possible misleading interpretation** | **that this is a Manhattan plot of association.** A reader who has seen a thousand GWAS figures will supply a p-value axis and a significance line that do not exist. Second risk: that only 151 genes competed. |
| **correction applied** | y axis reads literally `A0 genetics-only prioritization score`; no `−log10(p)`, no threshold line, no "hits"; the provenance strip says NOT a p-value in the first sentence. The 6 321-gene universe is drawn twice (as a baseline rug in A and as density in B) so the subset cannot be mistaken for the field. Frozen rank #4 is the one plotted, with A0-FREQFIX #1 stated alongside. |
| **full-size render checked?** | yes |

---

## Fig 3 · BUB1B gene browser: `fig02_gene_browser`

| | |
|---|---|
| **notebook** | `02_BUB1B_ALLELE_CURATION` |
| **source data** | Ensembl REST release 116 (exons, InterPro/Pfam domains) + `work/clinvar/landscape_missense.json` |
| **n** | 23 exons · 1 050 aa · 1 497 ClinVar missense records at 835 distinct residues |
| **axes / units** | protein position (aa) shared by all four panels; C: records per residue; D: records per 25 aa |
| **statistic represented** | counts. Nothing is smoothed, fitted or interpolated. |
| **FIGURE CLASS** | `DATA` |
| **EVIDENCE ORIGIN** | `EXTERNAL+MEASURED`, meaning Ensembl and ClinVar plus the two case-allele markers |
| **uncertainty represented?** | no interval, counts are exact |
| **uncertainty quantified?** | n/a; the real uncertainty is ascertainment, stated in the caption |
| **possible misleading interpretation** | that ClinVar density maps where the important mutations are. It maps **how much the gene has been sequenced and reported**. Second risk: reading "no hotspot" as evidence *against* the candidate. |
| **correction applied** | caption states the ascertainment bias and that absence of a hotspot means PM1 does not apply *anywhere*, which is not the same as evidence against; the candidate marker is a thin guide line, not an oversized point that would distort the distribution |
| **full-size render checked?** | yes |

---

## Fig 4 · Pocket geometry and evolutionary constraint: `fig03_pocket_and_conservation`

| | |
|---|---|
| **notebook** | `03_BUBR1_MECHANISM` |
| **source data** | `work/struct/AF-O60566-F1.pdb` (coordinates, B-factor = pLDDT) + `work/conservation/orthologs.json` |
| **n** | 9 neighbours ≤ 5 Å · 3 candidate H-bonds · 153 one-to-one orthologs · 117–122 aligned per column |
| **axes / units** | A: Å (3-D, axes hidden) · B: contact shell to scale, radius = minimum heavy-atom distance (Å) to the candidate side chain, angle only separates sequence-local (left, circles) from tertiary (right, squares); rings at 3.5 Å and 5 Å · C: information (bits) and n aligned · D: pLDDT, position relative to candidate (aa) |
| **statistic represented** | Euclidean distances between heavy atoms; Shannon information per alignment column; AlphaFold pLDDT |
| **FIGURE CLASS** | `MODEL_OUTPUT` |
| **EVIDENCE ORIGIN** | `PREDICTED+EXTERNAL`, meaning AlphaFold coordinates plus Ensembl orthologs |
| **uncertainty represented?** | yes, pLDDT is a confidence track, and alignment coverage is its own sub-track |
| **uncertainty quantified?** | pLDDT yes; phylogenetic non-independence **no**, stated, not drawn |
| **possible misleading interpretation** | **that "3 candidate H-bonds" are demonstrated interactions.** They are donor/acceptor pairs within 3.5 Å in a *predicted* structure that carries no hydrogens, so no angle was checked. Second risk: reading 153 orthologs as 153 independent observations. |
| **correction applied** | the word CANDIDATE is in the legend entry, the panel and the provenance strip; the strip states that the effective clade-level count is ~5–6; the coverage sub-track shows that alignment depth is not constant and that the deepest clades drop out first. **2026-10-07 redesign (idea-level):** panel B was a bar chart repeating A's distances; it is now the contact shell to scale (class by marker shape as well as colour); A no longer prints the overlapping H-bond distances (read in B); thesis title and a computed subtitle that says "3 candidate H-bonds to 2 residues" and states the ceiling (predicted structure, correlated sequences, not a measured destabilisation) |
| **full-size render checked?** | yes (redesign: three renders; label/marker collisions in B fixed) |

---

## Fig 5 / 5S · AlphaGenome browser: `fig04_alphagenome_rna_splicing`, `fig04S_alphagenome_accessibility_tf`

| | |
|---|---|
| **notebook** | `04_HIDDEN_SECOND_ALLELE` |
| **source data** | `work/alphagenome/arrays_*.json`, nine tracks frozen before the call was repeated |
| **n** | 5 tracks in the main figure, 4 in the supplement · ±5 000 bp window |
| **axes / units** | offset from the candidate variant (bp), shared; per-track predicted signal in the model's own units; Δ = ALT − REF in the same units |
| **statistic represented** | model output per bin. **Not a measurement.** |
| **FIGURE CLASS** | `MODEL_OUTPUT` |
| **EVIDENCE ORIGIN** | `PREDICTED`, no measurement of any kind is behind these tracks |
| **uncertainty represented?** | no, the model returns a point prediction |
| **uncertainty quantified?** | **no**, and nothing is drawn that would imply otherwise |
| **possible misleading interpretation** | **that these are measured genome-browser tracks.** They look exactly like ENCODE tracks because that is what the model was trained to emit. Second risk: that a flat Δ proves no second allele exists. |
| **correction applied** | PREDICTED is in the figure title, in the class stamp and in the first line of the provenance strip; the strip states there is no patient tissue and no tissue of any kind behind the tracks; the caption states this is one candidate, not a sweep. Nine tracks were split into two figures rather than compressed, the split is by **modality**, stated on the figure, so it cannot be read as track-picking. |
| **full-size render checked?** | yes, both |

---

## Fig 5I · AlphaGenome in silico mutagenesis: `fig04I_alphagenome_ism`

**Post-freeze characterisation of the same frozen candidate.** Produced under a pre-run manifest
(`work/alphagenome/run_manifest.json`, sha256-sealed before the first prediction) that fixes the
window, context, scorers, ontology and reading rule; `src/verify.py` (control *AlphaGenome model
outputs*) checks that every artefact cites that manifest.

| | |
|---|---|
| **notebook** | `04_HIDDEN_SECOND_ALLELE` |
| **source data** | `work/alphagenome/ism/primary_*_matrix.json.gz` + `metadata.json`, written by `src/model_outputs/alphagenome_ism.py`; raw per-substitution scores in `*_raw_scores.json.gz` |
| **regenerate** | `work/venv-ag/Scripts/python src/model_outputs/alphagenome_ism.py` (calls the model) · `python src/figures/fig04_ism.py` (renders from the artefacts, no model call) |
| **n** | 256 positions × 3 alternatives = 768 synthetic substitutions per readout; 16 kb sequence context; one pre-declared 100 kb context check, reported only |
| **axes / units** | offset from the candidate (bp), shared by every panel; heatmap rows A/C/G/T; colour and bar height = per-position centred score in the scorer's own units (splice sites: CenterMask 2001 bp diff-mean; DNase: CenterMask 501 bp diff-mean on one pre-declared track) |
| **statistic represented** | model attribution: score of a substitution minus the mean of the three alternatives at that position, exactly the official `ism_matrix` transform. **Not a measurement.** |
| **FIGURE CLASS** | `MODEL_OUTPUT` |
| **EVIDENCE ORIGIN** | `PREDICTED` |
| **result visible** | candidate at position rank 62 of 256 (primary) and 168 of 256 (secondary); the window's most responsive base is 125 bp away (primary) and 109 bp away (secondary); 16 kb and 100 kb matrices agree, r = 0.95 and 0.98 |
| **conclusion supported** | *no concentrated local ISM sensitivity at the candidate under the pre-specified readout*, the pre-declared negative reading; consistent with the frozen negative of Fig 5, and adding nothing to it |
| **uncertainty represented?** | no, the model returns point predictions |
| **uncertainty quantified?** | **no**; the only robustness shown is the context check, and it is stated as such |
| **possible misleading interpretation** | **that a hot column proves a functional element, or a cold column proves the region is inert.** Both are model attribution under one scorer. Second risk: reading the DNase readout as tissue evidence; it is one pre-declared track, chosen before the run by a rule, not the tissue of the patient. Third risk: assuming the scorer was picked after seeing the result. |
| **correction applied** | PREDICTED and *model attribution only* in the provenance strip; the reading rule is quoted on the figure and was fixed in the manifest before the prediction; the candidate is outlined and its ranks printed so a reader sees it is *not* at the maximum; reference bases are marked so alternative and reference cells cannot be confused; the manifest hash chain is enforced by `verify.py` |
| **changes frozen science?** | **NO** |
| **full-size render checked?** | yes |
| **reading rule status** | the top-5 % rule is an **internal decision rule**, pre-declared to prevent cherry-picking; not a literature-validated threshold and not a significance level. Empirical calibration against a matched null is EXP-024 |

---

## Fig 5C · AlphaGenome predicted contact maps: `fig04C_alphagenome_contact_maps`

**Post-freeze characterisation, same manifest as Fig 5I.**

| | |
|---|---|
| **notebook** | `04_HIDDEN_SECOND_ALLELE` |
| **source data** | `work/alphagenome/contacts/{ref,alt,delta}.json.gz` + `robustness_scores.json` + `metadata.json`, written by `src/model_outputs/alphagenome_contacts.py` |
| **regenerate** | `work/venv-ag/Scripts/python src/model_outputs/alphagenome_contacts.py` (calls the model) · `python src/figures/fig04_contacts.py` (renders from the artefacts) |
| **n** | one 1 Mb window, 512 × 512 bins of 2 048 bp, one pre-declared biosample (skin fibroblast, `CL:0002620`); 28 contact tracks scored with the official `ContactMapScorer` for panel D |
| **axes / units** | offset from the candidate (kb) on both axes of A–C; colour = log10(1 + predicted contact signal), one scale shared by REF and ALT, unclipped (the transform is stated on the figure); ALT − REF in linear model units on its own zero-centred symmetric scale, unclipped; D: local-disruption score (×10⁻³) per track |
| **statistic represented** | model output per bin pair; D is the official per-track scalar. **Not Hi-C.** |
| **FIGURE CLASS** | `MODEL_OUTPUT` |
| **EVIDENCE ORIGIN** | `PREDICTED` |
| **result visible** | REF and ALT are indistinguishable by eye; max \|ALT − REF\| = 0.0625 against max REF = 5.75 (1.09 %), below the 5 % threshold fixed before the prediction; the pre-declared track ranks 8 of 28 on the official score, inside the bulk of the distribution |
| **conclusion supported** | *no compelling predicted contact effect* in the pre-declared biosample; consistent with the frozen negative and adding nothing to it |
| **uncertainty represented?** | only the 28-track spread in D, which is biosample variation of a point prediction, not statistical uncertainty |
| **uncertainty quantified?** | **no** |
| **possible misleading interpretation** | **that these are Hi-C maps, or the patient's chromatin.** They look like Hi-C because that is what the model was trained on. Second risk: reading the diagonal speckle of ALT − REF as a structural change; it is 1 % of the REF scale. Third risk: assuming the biosample was chosen for effect. |
| **correction applied** | *not Hi-C, not patient chromatin, not any tissue* in the first line of the provenance strip; the log transform is identical for REF and ALT and declared, and nothing is clipped; ALT − REF is linear and never transformed; the biosample choice and its reason live in the manifest, sealed before the run; panel D shows the whole distribution so the reader can see the choice was not an outlier hunt |
| **changes frozen science?** | **NO** |
| **full-size render checked?** | yes |
| **reading rule status** | the 5 % of max REF rule is an **internal decision rule**, pre-declared; the official `ContactMapScorer` summarises disruption around the variant's bin, and its calibration against a matched null is EXP-024 |

---

## Fig 6 · HPO term × disease model: `fig05_hpo_disease_matrix`

| | |
|---|---|
| **notebook** | `05_RESIDUAL_PHENOTYPE` |
| **source data** | `work/hpo/prepared.pkl` (9 155 disease models) + `work/hpo/phenotype.hpoa` (disease names) |
| **n** | 7 proband terms × 12 models = 84 cells |
| **axes / units** | A: rows = proband HPO terms with their own IC · columns = disease models (name, gene, profile BMA in bits in the label) · cell value and colour: **bits**. B: the same rows; check 1 (term annotated in the MVA1 model, read from the matrix), check 2 (MVA1 published series, from `docs/PHENOTYPE_RESIDUAL_AUDIT.md`) and the verdict DERIVED from both: EXPLAINED · ANNOTATION GAP · CANNOT JUDGE (PARKED) · RESIDUAL |
| **statistic represented** | Resnik: IC of the most informative common ancestor. The same quantity the ranking engine consumes. |
| **FIGURE CLASS** | `DATA` |
| **EVIDENCE ORIGIN** | `MEASURED+EXTERNAL+DERIVED`, proband HPO terms, external disease models, computed Resnik. **This is the case the two axes exist for.** |
| **uncertainty represented?** | partly, the IC scale is shown; annotation bias is stated, not drawn |
| **uncertainty quantified?** | **no** for annotation bias, and it cannot be from this corpus |
| **possible misleading interpretation** | **that a low cell means the trait does not occur in that disease.** It means the corpus does not annotate it. Second risk: that literature support has been folded into the bits. Third: that MVA1 covering 3 of 7 terms is evidence against MVA1, it is not, because three of the four uncovered terms have literature support. |
| **correction applied** | literature support is a dashed **ring**, never a number, and the legend says "not a Resnik score"; the provenance strip states the annotation bias explicitly and says the columns are neighbours of the full profile, not a search for renal models; the computed caption names which terms are covered and which are not, rather than asserting a count. **2026-10-07 redesign (idea-level):** the profile-BMA bar panel was replaced by a row-aligned two-check verdict ledger (BMA kept in the column labels); the thesis is the title; the renderer refuses to draw unless the derived RESIDUAL set is exactly nephrocalcinosis and no MVA model covers it. Verdict identity is written in each pill, not carried by colour alone; CANNOT JUDGE is dashed and labelled PARKED, not negative |
| **full-size render checked?** | yes (redesign: two renders; subtitle overflow, panel-heading collisions and truncated Bartter subtypes fixed). 2026-10-07 leader review: title is "Among seven recorded traits, nephrocalcinosis is the only one unsupported by both checks" (not a statement about MVA1 phenotypes in general); check 2 separates **direct** support (rhabdomyosarcoma among the reported malignancies) from **broader** support (pre/postnatal growth retardation 93.5 % covering short stature, SGA and failure to thrive): the series does not report those terms literally. Second pass: "absent from the series" → "not reported in the reviewed MVA1 series" and "no: only generic renal dysfunction" → "not reported; generic renal dysfunction 12.9 %" (not reported ≠ systematically assessed and absent). Third pass: the source is named a **31-case MVA1 literature compilation** (Pavone et al. 2022, PMID 35804254), not a "series": it is a literature review whose own index case carries a single heterozygous BUB1B VUS |

---

## Fig 7 · BAF cancellation: `fig06_baf_cancellation`

| | |
|---|---|
| **notebook** | `06_MOSAIC_AND_MITOREAD` |
| **source data** | `src/mosaic/simulate_dispersion.py`, seed 42 (preregistered), plus the 2x2 ablation `src/mosaic/ablation_baf.py` (EXP-015c) |
| **n** | 200 replicates per cell · 400 sites/chromosome · 3 affected chromosomes · 1 200 sites per panel · depth 44× |
| **axes / units** | A–C: BAF (fraction) × density, identical scales · D: cell fraction (%) × power at fixed FPR 0.05 |
| **statistic represented** | site-level BAF distributions; power against a fixed false-positive rate |
| **FIGURE CLASS** | `SIMULATION` |
| **EVIDENCE ORIGIN** | `SIMULATED`, not one value from the case |
| **uncertainty represented?** | yes, the distributions *are* the uncertainty; power is estimated from 200 replicates and, since 2026-09-29, drawn with Wilson 95 % intervals |
| **uncertainty quantified?** | sampling yes; **model misspecification no**, and that is the dominant term |
| **possible misleading interpretation** | **that the power collapse of panel D is caused by lineage cancellation.** It is not, and this document certified the wrong explanation for months. `\|BAF-0.5\|` is an *absolute* statistic and therefore blind to the sign randomisation; the collapse is driven by copy-number-dependent depth, since the extra copy raises coverage to (2+f)/2 while the null stays at 44x. The post-hoc diagnostic ablation EXP-015c (designed after the audit, **not preregistered**) separates the two: no evidence of a direction effect (0.520 and 0.505 at matched depth, the same result at 200 replicates) and depth changes everything. What cancellation *does* move is the **signed** statistic, 0.980 to 0.050. Second risk: **that the dispersion index beats the standard method.** The comparator is a site-wise *unphased* BAF statistic; MoChA gets its power from long-range phasing and is not reproduced here. Third: reading simulated power as achievable power. |
| **correction applied** | the provenance strip now names the statistic as ABSOLUTE, states that the project's own audit falsified its first explanation, and gives both numbers; the comparator is named `site-wise unphased BAF statistic` in the legend, and a boxed note inside the panel reads "NOT MoChA: no long-range phasing" so it survives a crop; the strip states the power is optimistic, no GC bias, no mappability, no reference-allele bias. The correction is written next to the untouched preregistration in `docs/DECISIONS.md`. |
| **full-size render checked?** | yes, re-checked 2026-09-25: the second line of the provenance strip ran off the canvas and was truncated, and the boxed baseline note covered the variegated BAF curve between 15 and 20 %. The strip is now wrapped onto five lines inside the canvas and the box sits in the empty upper-left of panel D. Layout only: same data, seed and values. Re-checked 2026-09-29 after a journal-style pass (Lynch 2022, Loh 2018 as reference): Wilson 95 % bars in D, ticks only at the tested fractions (1, 2, 5, 10, 20 %), concept colours from `style.py`, panel C label moved off the 0.5 line, strip cut to two lines with the full caveats kept in the notebook caption and in this card. Same data, seed and values |

---

## Fig 8 · Track 2 curated evidence matrix: `fig07_track2_evidence_matrix`

| | |
|---|---|
| **notebook** | `07_TRACK2_SAFE_RESCUE` |
| **source data** | `research/track2_evidence.tsv`, versioned, one row per cell |
| **n** | 8 bridges × 10 dimensions = 80 cells · 4 distinct publications + 2 internal artefacts |
| **axes / units** | categorical × categorical. **No numeric axis, on purpose.** |
| **statistic represented** | none. It is an inventory with a five-value closed vocabulary: `DIRECT` `GENETIC` `NEAR` `CONTRADICTORY` `ABSENT`. |
| **FIGURE CLASS** | `CURATED_EVIDENCE` |
| **EVIDENCE ORIGIN** | `EXTERNAL+DERIVED`, published literature, plus the project's own in-silico evidence |
| **uncertainty represented?** | structurally: 61 of 80 cells are empty and that emptiness is the message |
| **uncertainty quantified?** | **no**, and it must not be, see below |
| **possible misleading interpretation** | **that these 80 cells are experimental observations of the patient.** Calling it plain "data" would invite exactly that, which is why the class is written out in full in the title and the stamp. Second risk: that the coloured cells can be added up into a score or a winner. |
| **correction applied** | title reads `CURATED EVIDENCE MATRIX (external literature + project evidence, not patient observations)`; the provenance strip states that no overall score, weight or ranking is computed and why, combining heterogeneous evidence needs a preregistered method and none exists; it also states that ABSENT means **no qualifying evidence was identified in our scoped literature search** — not that the claim is false, and not that nobody has ever looked. That last clause is a correction: this card previously certified the absolute wording *nobody measured it*, which is a claim about the world rather than about the scope of our search, and it travelled inside the published SVG. The `bridge coherence` check now reads `src/figures/` too, because the one text a judge actually sees was the one text that check did not read. Build-time assertion: no cell other than ABSENT may lack a source. |
| **full-size render checked?** | yes |

---

## Fig 9 · Track 2 experimental portfolio: `fig08_track2_portfolio`

> **Read the class before the colours.** This is a DECISION instrument, not an evidence
> figure. It records what the project proposes to test and why, not what has been shown.

| | |
|---|---|
| **notebook** | `07_TRACK2_SAFE_RESCUE` |
| **source data** | `research/track2_candidates.tsv`, versioned, one row per arm |
| **n** | 6 rows (3 interventions + 3 controls) × 5 claim columns = 30 claim cells · 12 carrying a published identifier |
| **axes / units** | categorical × categorical. **No numeric axis, no score, no ranking.** |
| **statistic represented** | none. Panel A is a five-value provenance vocabulary: `cited` `internal` `unverified` `none` `n/a`. Panel B is prose: the discard rule each arm carries, written in advance. |
| **FIGURE CLASS** | `CURATED_EVIDENCE` |
| **EVIDENCE ORIGIN** | `EXTERNAL+DERIVED`, regulatory labels and published literature, plus the project's own role assignment |
| **uncertainty represented?** | structurally: an orange cell is a declared gap, and azithromycin's exposure cell stays orange on purpose |
| **uncertainty quantified?** | **no.** No probability, no weight, no total |
| **possible misleading interpretation** | **that green means the evidence favours the arm.** It does not: green means the claim carries a published identifier. A green *counter-evidence* cell means the contrary evidence is well sourced, which is the opposite of favourable. Second risk: that `ALLELE-DIRECTED`, `FALSIFICATION SENTINEL` and `ADVERSARIAL COMPARATOR` are established categories; they are **roles this project assigned**. Third: that panel B contains results; it contains discard rules we wrote. Fourth: that the figure shows how far each experiment sits from this patient; it does not, and the transfer distances are large — other genetic contexts for readthrough, NPC1 fibroblasts for arimoclomol, a *Drosophila* CIN model for sirolimus. |
| **correction applied** | the title says `three roles, not a ranking`; the subtitle says there is no overall score and no winner; the provenance strip states in its own line that **colour encodes provenance, not efficacy or support**, and that none of these is proposed for administration. The transfer-distance table lives in `reports/TRACK2_REPORT.md` §5, where each arm's system, dose and measured outcome are named. |
| **full-size render checked?** | yes |
| **fit for the 3-minute video?** | **no, not at full size.** Too much small text. `docs/JUDGE_PATH.md` records that a reduced version keeping only the three roles and the killing question is what the pitch would use, and that it is not built yet. |

---

## Fig 10 · CNVpytor chromosome-level RD and BAF summary: `fig09_cnvpytor_chromosome_rd_baf`

| | |
|---|---|
| **Figure ID** | `fig09_cnvpytor_chromosome_rd_baf` (final set: Figure 5) |
| **notebook** | none: GO 2B frozen artifact, not a notebook figure |
| **Classification** | `DATA` |
| **Evidence mode** | `MEASURED+DERIVED` (the single derivation, normalisation to the autosomal median `RD_ref`, was preregistered in `CNV_METRICS_PREREG.md` before any value was inspected) |
| **Source artifact(s)** | `work/callers/final/go2b_cnv_hdf5_metrics.json` (per-chromosome metrics written inside the pinned CNVpytor 1.3.2 image, digest `sha256:614b22c8fc1fcef147bcda48bb4d53cb63c988bffc588e186acff7335013fcf1`); `work/callers/final/go2b_cnv_read.json` (record counts only, for the provenance strip) |
| **Source SHA256** | `9b3067218310160d61a8b49f39df36b9a9418c2427d0c6b01a44366ebe65adcf` · `e39e39153929c62c0878efbd576be412e3b8b57925b2e54e02bfe674e246a12e` |
| **Renderer** | `src/figures/fig09_cnv_chromosomes.py` |
| **Output** | `figures/pub/fig09_cnvpytor_chromosome_rd_baf.svg` (+ PNG 300 dpi, thumbnail) |
| **Output SHA256** | `d285e2d58c13b89c093e21db7157f31892a5d12f2ea073441fc687501d8ebef3` |
| **Frozen commit** | data produced under `5b66f58` (stage 4 rerun after `EXEC-OOM-001`); GO 2B SCIENCE FINAL recorded in `docs/DECISIONS.md` |
| **hash verification** | FAIL CLOSED: the renderer loads every source through `src/figures/frozen.py`, which checks its sha256 against `work/callers/final/MANIFEST.json` before drawing. A changed, missing or undeclared artifact raises `FrozenArtifactError` and no figure is produced. |
| **n** | 24 primary chromosomes · 100 kb bins (27 579 autosomal bins with RD > 0 define `RD_ref`) · 1 636 719 heterozygous SNPs over the 24 chromosomes (1 634 791 autosomal) |
| **axes / units** | A: chromosome × median RD / autosomal median, ± MAD · B: chromosome × median per-bin minor-allele fraction, ± MAD · C: chromosome × CNVpytor `i1` and `i2` medians · D: chromosome × heterozygous SNPs (thousands) and fraction of bins with RD > 0 |
| **statistic represented** | medians and unscaled MADs over 100 kb bins of CNVpytor's own emitted per-bin datasets (`his_rd_p_<c>_100000_GC`, `snp_maf`, `snp_i1`, `snp_i2`, `snp_bafc_01/10`); nothing recomputed from reads |
| **uncertainty represented?** | dispersion across bins (MAD), yes; no confidence intervals |
| **uncertainty quantified?** | technical dispersion only; no reference cohort with an identical pipeline, so no comparison against controls (EXP-015 remains blocked for inference) |
| **Claim ceiling** | *Chromosome-level RD/BAF showed the pattern drawn: autosomal medians in a narrow band around the autosomal reference, uniform aggregated BAF statistics, X and Y reported with the same reference without adjustment.* |
| **Forbidden inference** | `cytogenetic aneuploidy detected / excluded`, `mosaic fraction = X %`, `chromosome N is trisomic / monosomic`, and any reading of the 49 RD+BAF caller records as validated CNVs (they are raw inventory, AE4, and are not drawn) |
| **possible misleading interpretation** | that a flat chromosome-level summary of aggregated blood WGS says anything about cell-level variegated aneuploidy. It does not: CNVpytor's segmentation is described for high cell fractions (PMID 34817058) and PCS/MVA is assessed cell by cell (Yamaguchi 2018, Kato 2017). |
| **correction applied** | no copy-number guide lines at 0.5 / 1.5; X and Y separated by a hairline and labelled "no adjustment, no interpretation"; Y BAF annotated with its denominator (10 het SNPs in 2 bins); provenance strip states DESCRIPTIVE ONLY and the PMID |
| **full-size render checked?** | yes (preview render, layout corrected twice: annotation, legends, provenance strip) |

---

## Fig 11 · BUB1B read-level breakpoint assay: `fig10_bub1b_readlevel_assay`

| | |
|---|---|
| **Figure ID** | `fig10_bub1b_readlevel_assay` (final set: Figure 6) |
| **notebook** | none: GO 2B post-final exploratory lookup AE3, frozen artifact |
| **Classification** | `DATA` |
| **Evidence mode** | `MEASURED+DERIVED` (per-bin fractions are counts divided by the preregistered denominator `n_reads`; region medians are the ones in the frozen summary) |
| **Source artifact(s)** | `work/callers/final/ae3_bub1b_readlevel.json`, written by `go2b_stop_tools/ae3_bub1b_readlevel.py` with pysam 0.23.0 inside the pinned CNVpytor image from the GO 2A BAM (sha256 `6388cd66d9d412ec167733802c00a70831d2edcd4ee78bfa0f644cb81296f278`) |
| **Source SHA256** | `3e845787eb27217ede5e97f86aba2691dcccf668dc47a5292e732c234b321231` |
| **Renderer** | `src/figures/fig10_bub1b_readlevel.py` |
| **Output** | `figures/pub/fig10_bub1b_readlevel_assay.svg` (+ PNG 300 dpi, thumbnail) |
| **Output SHA256** | `540f9af27f40f53ab117b8ba72e6ffeb6a6dce5a0100cc84a0dc2dca7df121de` |
| **Frozen commit** | assay preregistered in `AE_PREREG_LOOKUPS.md` § AE3 and adjudicated FINAL · PASS; data under `5b66f58`; GO 2B SCIENCE FINAL in `docs/DECISIONS.md` |
| **hash verification** | FAIL CLOSED: the renderer loads every source through `src/figures/frozen.py`, which checks its sha256 against `work/callers/final/MANIFEST.json` before drawing. A changed, missing or undeclared artifact raises `FrozenArtifactError` and no figure is produced. |
| **n** | 181 bins of 1 kb on 15:40101001-40282000 · 60 upstream / 60 body / 60 downstream by midpoint inside exact 60 055 bp intervals · 1 CONTEXT_ONLY bin excluded · reads: upstream 18 906, body 19 850, downstream 19 332 · intron 2: 5 bins, 1 828 reads · intron 8: 11 bins, 3 747 reads |
| **axes / units** | A–D: fraction of bin reads; E: clusters per bin (Σ per region annotated); F: reads per bin (bins per region annotated); x = region groups |
| **statistic represented** | per-bin values of the six preregistered metrics (`f_softclip` ≥ 20 bp clip; `f_split` SA tag; `f_discordant` preregistered definition; `f_mapq0`; `n_clip_clusters` ≥ 3 clipped reads at the same coordinate + side; `n_reads`) and the frozen region medians |
| **uncertainty represented?** | the spread of bins is shown in full; no confidence intervals |
| **uncertainty quantified?** | no: no threshold, no test, no model was preregistered, so none is drawn |
| **Claim ceiling** | *The preregistered short-read breakpoint metrics for the BUB1B body and equal-length flanks are reported side by side; no inferential excess/no-excess threshold was defined, and complex insertion is not excluded.* |
| **Forbidden inference** | `excess`, `no excess`, `complex insertion excluded`, and any post-hoc selection of individual bins or of introns 2/8 as evidence: they appear only because the literature highlighted them (Kawakami 2024, PMID 38102195; Kato 2017, PMID 28611924) |
| **possible misleading interpretation** | reading the body median of `f_discordant` (0.0157 vs 0.0100 / 0.0121) or the body cluster sum (17 vs 10 / 11) as an "excess". No threshold existed before the read, so no such statement is licensed; and a short-read assay cannot exclude a composite intronic insertion (Kawakami 2024). |
| **correction applied** | groups plotted on identical axes with the frozen medians only; region sizes stated as exact 60 055 bp intervals; introns marked with an asterisk explained in the header; the approved sentence printed verbatim in the provenance strip |
| **full-size render checked?** | yes (preview render, layout corrected once: titles, tick labels, provenance strip, bottom margin) |

---

## Fig 12 · MEI/SV adjudication map around BUB1B: `fig11_mei_sv_adjudication_map`

| | |
|---|---|
| **Figure ID** | `fig11_mei_sv_adjudication_map` (final set: Figure 7) |
| **notebook** | none: GO 2B frozen artifacts and post-final lookup AE1 |
| **Classification** | `DATA` |
| **Evidence mode** | `MEASURED+EXTERNAL+DERIVED` (caller records are measured; GENCODE v33 gene context is external; the only derived numbers are distances between frozen coordinates, used as labels) |
| **Source artifact(s)** | `work/callers/final/tier1_sv_manta_delly.json` (Manta and DELLY records in the Tier 1 window, STOP of 2026-09-09, stages 2/3 under `47d24da`); `work/callers/final/go2b_mei_read.json` (xTea and SCRAMble records in the window, `ffb3c09`); `work/callers/final/ae1_gene_context.json` (AE1 gene context, frozen GENCODE v33, `5b66f58`) |
| **Source SHA256** | `26e0013c51d8d6108731fa08eda001fec9aae0e108d215eb24b6aef7caa74f00` · `410e706efb9ab83198cb39389fcf510467712a5452625570df5c1d8c8244faf0` · `7db6d9324e1339dc50281d86b873d3c63839af92af3596482d089819c1bf4334` |
| **Renderer** | `src/figures/fig11_mei_sv_adjudication.py` |
| **Output** | `figures/pub/fig11_mei_sv_adjudication_map.svg` (+ PNG 300 dpi, thumbnail) |
| **Output SHA256** | `ac081e282a2182e8c758e8c2e3745fd6f6bde2ad19e468c90c8b44ebd598b049` |
| **Frozen commit** | Tier 1 SV `47d24da`; MEI `ffb3c09`; AE1 `5b66f58`; GO 2B SCIENCE FINAL in `docs/DECISIONS.md` |
| **hash verification** | FAIL CLOSED: the renderer loads every source through `src/figures/frozen.py`, which checks its sha256 against `work/callers/final/MANIFEST.json` before drawing. A changed, missing or undeclared artifact raises `FrozenArtifactError` and no figure is produced. |
| **n** | Tier 1 window 15:39161069-41221123 · Manta 10 records (9 PASS) · DELLY 28 records (16 PASS) · xTea 2 records · SCRAMble 1 record · 12 frozen loci annotated by AE1 |
| **axes / units** | A: chr15 position (Mb, GRCh38) × caller rows; B: schematic, no axes |
| **statistic represented** | none: emitted records at their coordinates, caller-GT as emitted, AE1 gene context printed verbatim |
| **uncertainty represented?** | no; not applicable to a map of emitted records |
| **uncertainty quantified?** | no |
| **Claim ceiling** | *None of these loci overlaps the BUB1B gene body or the two prioritised positions.* Per locus: 39.70 Mb *geometry consistent with insertion of non-local chr12-derived sequence; xTea annotates an L1-family orphan/sibling transduction, consistent with an L1-mediated transduction hypothesis*; 40.56 Mb *breakpoints overlap exonic and intronic regions of CBX3; another partner overlaps an exon of CBX3P9, which GENCODE annotates as a processed pseudogene; gene-associated breakpoint context, not a retrocopy or processed-pseudogene insertion architecture*. |
| **Forbidden inference** | `retrocopy established`, `processed pseudogene insertion established`, `mechanism established`, any diagnosis or exclusion from these loci, and any reading of caller-GT as biological zygosity |
| **possible misleading interpretation** | that the partner mapping to CBX3 and CBX3P9 demonstrates a CBX3 retrocopy. The preregistered condition for even the weaker "consistent with a gene-derived insertion/retrocopy hypothesis" sentence (all three chr7 partners in exons) was not met: one partner is transcript-dependent, one intronic, one exonic. |
| **correction applied** | the leader's frozen sentences are printed verbatim inside the ceiling boxes; SCRAMble's absence at 39.70 Mb is explained by its method, not read as evidence; AE2 is shown as NOT EXECUTED (data policy) rather than as a negative |
| **full-size render checked?** | yes (preview render, layout corrected twice: label staggering, text wrapping, box heights, provenance strip) |

---

## Figures classified as synthesis or narrative

These are legitimate and stay in the notebooks. What they may **not** do is count as a
notebook's scientific figure.

| figure | notebook | class | why not scientific |
|---|---|---|---|
| ACMG points applied and missing | `02_BUB1B_ALLELE_CURATION` | `SYNTHESIS` | integrates a curation already done; exposes no raw data |
| Ortholog conservation with its three controls (`fig7_conservation.svg`) | `03_BUBR1_MECHANISM` | `DATA`, kept | still scientific; retained because the logo does not show the percentile, chemical-class or clade controls |
| HPO annotation vs literature | `05_RESIDUAL_PHENOTYPE` | `SYNTHESIS` | a two-check summary; the underlying quantity is in Fig 6 |
| Preregistered-prediction scorecard | `06_MOSAIC_AND_MITOREAD` | `SYNTHESIS` | the falsification record, 2 confirmed / 2 failed; no distribution |
| MitoRead prototype and its uncertainty | `06_MOSAIC_AND_MITOREAD` | `SYNTHESIS` | a point estimate beside unquantified bias sources |
| Eight bridges and the Safe Rescue Corridor (`fig10_track2_bridges.svg`) | `07_TRACK2_SAFE_RESCUE` | `SYNTHESIS` | the corridor is a scientific synthesis, deliberately kept out of the evidence matrix |

**Withdrawn during the visual pass** (redundant or contentless): modality inventory bars,
`fig2_landscape.svg`, the standalone pLDDT QC, `fig4_structural.svg`, "the two remaining
routes", `fig5_alphagenome.svg`, "the phenotype pulls two ways", `fig9_mosaic_sim.svg`,
"bridge 7 tension", "the four Try-to-Kill-It outcomes". Reasons per figure in
the notebook captions.

---

## Figure 4: the structural upgrade that was tried and abandoned

A time-boxed attempt was made to replace the Matplotlib 3-D panel with a PyMOL/ChimeraX
cartoon-surface render.

| step | result |
|---|---|
| PyMOL / ChimeraX on PATH or as a module | **absent** |
| ChimeraX installer | not attempted, downloading an executable binary is barred by project policy |
| `pymol-open-source` prebuilt wheel | downloads, but `import pymol._cmd` fails: **DLL load failed** (needs the conda-forge native stack) |
| decision | **aborted at the time-box**, exactly as instructed. The Matplotlib figure stands. |

**It left a mess that had to be cleaned up:** the wheel pulled NumPy up to 2.5.2, and the
Matplotlib in this environment is built against NumPy 1.x, so the whole plotting stack broke
with `numpy.core.multiarray failed to import`. Environment restored to `numpy 1.26.4`, PyMOL
uninstalled, every figure re-rendered and verified.

Cost of a real upgrade, for the record: a conda environment or a ChimeraX install. Worth it
for a poster; not worth it inside this time-box.

## One deliberate omission, recorded

**No MitoRead error bars.** The uncertainty is declared *not quantified*; drawing an interval
would be inventing the missing number. The figure shows the point estimate with open-ended
arrows instead: the bias is not bounded, and that is the only true statement available.

## Sanitisation verdict

`python src/sanitize_scan.py` → **CLEAN**. The file count is **whatever that command prints
today**, and it is deliberately not frozen here: it was 181 when this section was written and
206 at the time of writing this correction, because the repository keeps growing. A static
number in a QA document goes stale silently, which is the exact failure this document exists
to catch.

The scanner was fixed during the visual-science pass: it listed only `git ls-files`, so **new,
unignored files were never examined** and reported clean without being read. It now also lists
`git ls-files --others --exclude-standard`, which is what a commit would actually add — 156
files before that fix, 181 immediately after.

Manual check of the SVG text on top of the scanner: no residue number, no HGVS, no genomic
coordinate. The only long numeric tokens are public cell-line ontology identifiers in the
AlphaGenome track metadata (`CL:0000236`, `EFO:0002067`, `EFO:0002784`).

## Fig 13 · EXP-027 Phase 1 result: `fig13_exp027_phase1_result`

| | |
|---|---|
| **Figure ID** | `fig13_exp027_phase1_result` |
| **notebook** | none: sealed run artifacts of EXP-027 Phase 1 r2 |
| **Classification** | `DATA` |
| **Evidence mode** | `EXTERNAL+DERIVED` (public 1000 Genomes high-coverage trio data; every number is a statistic we computed under the frozen contract) |
| **Source artifact(s)** | `work/exp027/phase1_r2/phase1_report.json` (adjudicated report, tag `exp027-phase1-execution-freeze-r2`, commit `7e20047`); `work/exp027/posthoc/phase1_posthoc.json` (exact reproduction of that report; per-δ curves); `work/exp027/posthoc/apr_map.csv` (per-pair intact calls rebuilt with the same seeds, 249/995 as the report); `work/exp027/plan_execution/plan_windows.json` (window order, BUB1B first) |
| **Source SHA256** | `37e676ad5137dc4ceee283de7251b403323c3d9dda589907e8eff43a441e1e3e` · `923cfb32854c76867bc7fd06a28bef83c624f0e49bb17d6a987d3de4146ae136` · `316f0cf7be522f0ca62e1b4e55bcb1c01f1efe65e3591b27babdc23c7897da3d` · `e3731d525b1980026a5700f2fe8772a02eee6d363fa69e376cdd4b8bfa7c1c80` |
| **Renderer** | `src/figures/fig13_exp027_phase1.py` |
| **Output** | `figures/pub/fig13_exp027_phase1_result.svg` (+ PNG 300 dpi, thumbnail) |
| **Output SHA256** | `2e87124546f97899b5b7b0cd54e739ef94dc96e85edae35cff7220dcef4a8bba` (SVG) · `f99f359c999599735696bfcb0d0528c9c4b116a6957e801ebd24eae76010b328` (PNG); sealed version under tag `exp027-phase1-result-r2-fail`: `d7fd1bf3…` / `44533858…` |
| **Frozen commit** | run `7e20047` (tag `exp027-phase1-execution-freeze-r2`); result sealed under tag `exp027-phase1-result-r2-fail` |
| **hash verification** | FAIL CLOSED: the renderer checks all four source SHA256 before drawing, refuses to draw if the post-hoc reproduction is not identical to the sealed report, and refuses if the per-pair map does not give the report's K/N. |
| **n** | 20 children × 50 evaluation windows = 1000 pairs, 995 evaluable (5 below Hmin = 50 after filters); 20 × 20 calibration tiles for ρ (not part of APR); B = 10 000; δ ∈ {0, .02, .05, .10, .15, .20} |
| **axes / units** | A: unit matrix, 20 children (rows, by superpopulation) × 50 evaluation windows (columns, BUB1B first), each cell one intact pair, lit = called positive; no coordinates printed. B: QQ plot, expected vs observed −log10 p of the 995 intact pairs. C: detection fraction vs spiked δ, inferred vs Mendelian phase. D: decision diagram of the nine preregistered gates feeding the patient gate. |
| **statistic represented** | per-pair intact call (p < 0.05 under the phase-randomized null), QQ inflation λ (median χ² / 0.4549, descriptive), sensitivity per child then children equal-weighted (Amendment 6), retention = inferred / Mendelian, gate values from the sealed report |
| **uncertainty represented?** | B: iid Uniform reference envelope, 95 %, 2 000 draws, seed 42, **descriptive only** (the 995 pairs share children, windows and pipeline, so they are not iid); permutation floor 1/(B+1) marked |
| **uncertainty quantified?** | B only |
| **Claim ceiling** | *Under the frozen contract, the method detects spiked haplotype-coherent imbalance (0.943 at δ = 0.10, retention 0.943, switch error 0.41 %) but fails its calibration sentinel on real benchmark data (APR 249/995 = 25.0 % vs 5 % nominal) and BUB1B-locus retention (0.879 < 0.90). Phase 1: METHOD VALIDATION FAIL; the patient-level A1 test was not performed.* |
| **Forbidden inference** | patient negative, patient positive, any mosaic call or mosaic fraction in the patient, "25 % false-positive rate" as a biological rate, rounding 0.879 to 0.90, any mechanism for the APR excess |
| **possible misleading interpretation** | that the method "works" because panels B–C pass; the decisive panel is A. And that the 25 % is a biological false-positive rate: it is an operational calibration sentinel on LCL-derived benchmark data. |
| **correction applied** | first version (bars) rejected as not conveying the idea; redesigned as a unit matrix + QQ plot + power curve + gate diagram. No dual axis. Legend uses the real fill colours (identity not by colour alone: lit / unlit / ⊠ not evaluable). λ is descriptive only and is not a gate. 2026-10-07 wording pass (leader review): "healthy" → "intact, unspiked benchmark"; "fires without signal" → "without injected signal" (the post-hoc map suggests real REF/ALT structure the null does not capture, so "no signal" cannot be claimed); "null is broken" → "miscalibrated on the benchmark"; QQ band relabelled as a descriptive iid envelope. Numbers unchanged. |
| **full-size render checked?** | yes (five renders: label collisions, text overflow, legend overlap corrected) |

---

## Fig 14 · Track 1 convergence: `fig14_track1_convergence`

| | |
|---|---|
| **Figure ID** | `fig14_track1_convergence` |
| **notebook** | `01_TRACK1_GENOME_WIDE` (A0, A0-FREQFIX and the 15 frozen rankings); Exomiser baseline per `docs/EXTERNAL_BASELINE.md` |
| **Classification** | `DATA` |
| **Evidence mode** | `MEASURED+EXTERNAL+DERIVED` (patient genotypes → our rankings; external population frequencies and an external method, Exomiser, run on the same VCF) |
| **Source artifact(s)** | `work/gw/mode_b_results_v4.pkl` (15 frozen rankings); `work/gw/highmod_ann.tsv` (universe of 13 191 HIGH/MODERATE positions in 6 321 genes; A0-FREQFIX recomputed with the notebook-01 formula via `src.prioritization.freqfix_sensitivity`); `work/exomiser/runs/BASELINE-PRIMARY/BASELINE-PRIMARY.genes.tsv` |
| **Source SHA256** | `3ec4862274fa0f5168d32be8f69d1adacb631936e57aed678cf83a0cd79a8b3d` · `6bb5d13907efa9d576115e5877603321c49eb523cff7c7d7dfbfd3bdba6f5ce2` · `00b8ef31c993095b4b7987d3f17c864feffad1a31dfa5cb66565081ed4c332e7` |
| **Renderer** | `src/figures/fig14_track1_convergence.py` |
| **Output** | `figures/pub/fig14_track1_convergence.svg` (+ PNG 300 dpi, thumbnail) |
| **Output SHA256** | `f98e0c153a264517d938e4d93a0b471bb134d4b3a71160a7f74ebef37c28fd48` (SVG) · `2723becd845e0ae86d331e46fda8ec9fadf04a8747360cbe841254f0348f8d51` (PNG) |
| **hash verification** | FAIL CLOSED: the renderer checks all three source SHA256 before drawing and refuses to draw unless the data give BUB1B #1 in 14/15 frozen rankings, #1 in A0-FREQFIX and #2 in Exomiser. |
| **n** | 13 191 positions · 6 321 genes · 151 genes fitting an inheritance model · 15 frozen rankings + A0-FREQFIX + Exomiser (398 genes) |
| **axes / units** | A: funnel of three FILTERS (counts only), then a dashed arrow "ranked, not filtered" to a separate box: BUB1B top-ranked in 14 of 15 sensitivity analyses, with "same genome: sensitivity analyses, not independent replications" printed under it. B: bump chart, rank (1 = top) per ranking; ranks below #8 folded into one row; Exomiser drawn apart, after a separator, as an external method (same VCF, not independent biological evidence). C: one card per rival with the cheapest falsifier that removed it. No coordinates. |
| **statistic represented** | ordinal rank; prioritization scores are not test statistics and no p-value is shown |
| **uncertainty represented?** | no (ranks); the ceiling "candidate, not diagnosis" and "phase unresolved" are stated in the title and in card C |
| **uncertainty quantified?** | no |
| **Claim ceiling** | *Without a gene panel, BUB1B is #1 in 14 of 15 frozen rankings and #2 of 398 in an external tool run on the same VCF. It is #4 in the frozen A0 (three common polymorphisms ahead) and #1 in A0-FREQFIX. Strong biallelic candidate; phase unresolved; not a diagnosis.* (L2) |
| **Forbidden inference** | "BUB1B was always #1"; hiding the frozen #4; "diagnosis"; "biallelic confirmed"; HLA-DRB1 eliminated (it is flagged as an audit hypothesis, not proven or removed) |
| **possible misleading interpretation** | that the convergence of 15 rankings is 15 independent replications: they share the same genotypes and annotation, so they test robustness to choices, not independent evidence. And that the bump chart shows effect size: ranks are ordinal. |
| **correction applied** | designed idea-first (funnel + bump chart + elimination cards) instead of bars; strike-through marks removed rivals and is not the only cue (each card carries a written verdict); both A0 numbers drawn and annotated. Render fixes: subtitle comma bug, overlapping rotated tick labels vs footer, panel A text overflow, strike-through length. |
| **full-size render checked?** | yes (eight renders; Exomiser relabelled "external, same VCF"; 2026-10-07 leader review: the final "1" is no longer drawn as a fourth funnel stage, the non-independence caveat is in the figure, panel C heading says "what removed it, and what stays open" because HLA-DRB1 is not removed, and TRACK1_REPORT now says the same) |

---
