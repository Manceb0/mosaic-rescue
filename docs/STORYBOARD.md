# Visual guide and state of the story

Updated 24 September 2026. Integrates the GO 2B closure in `dd7ce71` and the three
technical figures in `8d2383a`. It does not reopen any frozen analysis.

## The story in one sentence

**One genome, a causal hypothesis that survives every available test, and an experiment
that must tell correction of the defect apart from survival of unstable cells.**

The reader should understand, in this order: what question we answer, what data we have,
what we found, how we tried to refute it, what is missing, and what we would do to resolve
it. Tools appear in the method; decisions organise the narrative.

## The hook

The candidate genotype, one truncating allele plus one missense, is the canonical
configuration of MVA type 1 ([Hanks et al. 2004](https://doi.org/10.1038/ng1449)). And the
history of this disease is a history of missing second alleles: in the early PCS families
only one mutation per family was found in coding sequence
([Matsuura et al. 2006](https://doi.org/10.1002/ajmg.a.31069)), and the hidden alleles later
turned up outside the exons ([Kato et al. 2017](https://doi.org/10.1038/hgv.2017.21);
[Kawakami et al. 2024](https://doi.org/10.1038/s10038-023-01211-8)). This case sits exactly at
that frontier, and the project shows how far one short-read genome can push it.

## What changed since the early discussions

- There is one blood WGS sample, four lanes and eight FASTQ files. The lanes are technical
  partitions, not people or biological replicates. GRCh38 is the reference assembly, not
  another participant. VEP, Exomiser and AlphaGenome are tools.
- The full BAM now exists and GO 2B is finished. The previous README still described it as
  missing; the older notebooks keep the scope they had when they were executed.
- AlphaGenome's RNA tracks are predictions. There is no RNA-seq, no protein assay and no
  parental genotyping for this case behind any of these figures.
- "The Patient Is the Screen" was an early idea. Aggregated WGS of one sample cannot observe
  selection, persistence or resistance of cell lineages. It is not used as a result or as the
  central promise of the README.
- The master set contains thirteen **visual questions**. Their numbering does not match the
  historical file names; AlphaGenome occupies several files.
- The existing piece 8 corresponds to EXP-023 and earlier predictions. EXP-024 is the
  preregistered calibration, **not executed**; EXP-023 is never relabelled as EXP-024.

## Design of the new reading layer

The new diagrams are `SYNTHESIS` or `NARRATIVE`: they reorganise existing conclusions and
produce no new measurements, scores, statistical inferences or evidence levels. Explicit
labels are used in addition to colour. Arrows describe questions or proposed mechanisms, never
observed traces. No blots, pedigrees, altered exons or fictitious mosaic percentages are drawn.

The derivation is editorial and declared before drawing: selection of already documented
conclusions, separation by provenance, and a link to each conclusion's uncertainty or
falsifier. Original statistics and technical figures are not recomputed. The new diagrams omit
coordinates, alleles and sample identifiers; the existing technical MEI/SV figure keeps
case-specific information and is not a public cover image.

## Map of the master set

| # | Visual question | File / representation | Correct reading |
|---|---|---|---|
| Cover | What does Mosaic Rescue do? | `story00_overview` | Synthesis of the process and its limit |
| 1 | Why BUB1B? | `fig01_prioritization_genomewide` + Mermaid funnel in README | A0 #4; A0-FREQFIX #1; Exomiser uses the same VCF |
| 2 | What supports the two alleles? | `story02_variant_card` | Truncating allele LP in research curation; missense VUS; phase unresolved |
| 3 | Which second allele was searched for? | `story03_second_allele` + GO 2B figures | No overlapping CNV RD+BAF or MEI call in the gene body; complex insertion not excluded |
| 4 | What do we know about mosaicism? | `story04_evidence_context` + `fig06_baf_cancellation` and `fig09_cnvpytor_chromosome_rd_baf` | Patient, simulation and literature are distinct layers |
| 5 | What do RD and BAF say? | `fig09_cnvpytor_chromosome_rd_baf` | Chromosome-level description, not a karyotype |
| 6 | What do the reads at the locus show? | `fig10_bub1b_readlevel_assay` | Descriptive metrics, no inferential threshold |
| 7 | Where do the alternative signals fall? | `fig11_mei_sv_adjudication_map` | Call context, not a diagnosis or a demonstrated architecture |
| 8 | What did AlphaGenome predict? | `fig04I_alphagenome_ism`, `fig04C_alphagenome_contact_maps` and tracks | Existing prediction; EXP-024 not executed |
| 9 | Which bridges have evidence? | `fig07_track2_evidence_matrix` | Full 8 × 10 matrix; not reduced to six columns to fit a sketch |
| 10 | How would the mechanism connect? | `story10_mechanism` | Specific hypothesis, levels L0–L1; external functional evidence comes from other alleles and systems |
| 11 | What is proposed for testing? | `fig08_track2_portfolio` + arms table in README | Three experimental roles, no therapeutic winner |
| 12 | Which result rules a route out? | `story12_safety_gates` | Proposed experimental rules, not obtained results |
| 13 | What is the next experiment? | `story13_next_experiment` | Phase, mechanism and safety answer different questions |

## What is genuinely missing

| Priority | Uncertainty / pending item | Data or action that reduces it | What changes the decision |
|---|---|---|---|
| 1 | Phase of the two alleles | Parental genotypes or targeted long-molecule phasing | In *cis*, this pair falls as a biallelic explanation; *trans* does not by itself establish pathogenicity |
| 2 | Function of the missense | Abundance/turnover and checkpoint function, with controls | Normal abundance weakens the instability route but does not rule out every functional defect |
| 3 | A complex second allele is still possible | Appropriate RNA-seq and targeted long reads, if the question persists | An event with a demonstrated splicing effect could replace the candidate pair |
| 4 | Pharmacological rescue and its risk | Assay measuring molecular activity, segregation errors and clonogenic survival, in addition to viability | Greater survival of unstable cells vetoes the route, even if another indicator improves |
| 5 | Generality of the method | Run the frozen pipeline, unchanged, on previously solved cases with known causal genes, blinded to the answer | Tells whether the procedure transfers; the code census alone does not show it |
| 6 | Residual phenotype | Obstetric history, electrolytes and clinical review of the nephrocalcinosis | May justify reopening the mixed-diagnosis hypothesis |
| 7 | MitoRead and the mosaicism detector | Matched controls; blood count/cell composition; validation against a phased method | The available BAM solves infrastructure, not the confounders or the validation |
| 8 | AE2 population lookup | Documented conditions that allow the external query | Remains NOT EXECUTED (data policy); not a negative frequency |
| 9 | EXP-024 calibration | Decide whether it still answers a relevant uncertainty, then run the existing protocol under its conditions | An existing prediction is never confused with a completed calibration |
| 10 | Delivery | Maintainer fields, dataset citation, privacy review and final package review | Technical verification does not equal a submitted package or permission to publish |

The rest of the complete genomic inventory is not presented as "finished": raw calls outside
the locus are not adjudicated alternative diagnoses. The local report
`REPORTE_GO2B_STOP_CIENCIA.md` was checked against its frozen hash in
`docs/go2b_final_artifacts.sha256.json`: EXP-025 recovers both alleles in the reads (technical
replication); EXP-026 has a negative DMPK screen within short-read scope; aligned MitoRead
produces a descriptive ratio, without cell-composition adjustment or comparable controls.
EXP-012c keeps its own reconciliation pending. The older CNV/MEI limitations in that report
were superseded by the FINAL closure.

## Verified sources for the external connections

Queried through the PubMed MCP on 24 September 2026, using gene names and public PMIDs; no
case coordinates were sent to PubMed.

- Hanks et al., *Nature Genetics*: truncating and missense BUB1B mutations in the first MVA
  families. [PubMed 15475955](https://pubmed.ncbi.nlm.nih.gov/15475955/),
  [DOI 10.1038/ng1449](https://doi.org/10.1038/ng1449).
- Matsuura et al., *Am J Med Genet A*: seven PCS families with a single coding BUB1B mutation
  found and reduced expression; links a >50 % loss of BUBR1 to the syndrome.
  [PubMed 16411201](https://pubmed.ncbi.nlm.nih.gov/16411201/),
  [DOI 10.1002/ajmg.a.31069](https://doi.org/10.1002/ajmg.a.31069).
- Wijshake et al., *PLoS Genetics*: human MVA1 is biallelic (typically missense plus nonsense)
  or monoallelic with variants that lower wild-type BUBR1; mouse model of a monoallelic allele.
  [PubMed 23300461](https://pubmed.ncbi.nlm.nih.gov/23300461/),
  [DOI 10.1371/journal.pgen.1003138](https://doi.org/10.1371/journal.pgen.1003138).
- Kawakami et al., *Journal of Human Genetics*: an external case in which RNA-seq and long reads
  resolved an intronic insertion that short-read GS had not identified. It does not show that our
  case carries that insertion.
  [PubMed 38102195](https://pubmed.ncbi.nlm.nih.gov/38102195/),
  [DOI 10.1038/s10038-023-01211-8](https://doi.org/10.1038/s10038-023-01211-8).
- Suvakov et al., CNVpytor: depth and allelic balance are complementary signals.
  [PubMed 34817058](https://pubmed.ncbi.nlm.nih.gov/34817058/),
  [DOI 10.1093/gigascience/giab074](https://doi.org/10.1093/gigascience/giab074).
- Suijkerbuijk et al.: functional evidence in other MVA alleles and cells; distinguishes
  abundance defects from specific functional defects.
  [PubMed 20516114](https://pubmed.ncbi.nlm.nih.gov/20516114/),
  [DOI 10.1158/0008-5472.CAN-09-4319](https://doi.org/10.1158/0008-5472.CAN-09-4319).
- Pipalia et al.: pharmacological counterexample in NPC1 fibroblasts, not in this MVA case.
  [PubMed 34481829](https://pubmed.ncbi.nlm.nih.gov/34481829/),
  [DOI 10.1016/j.jlr.2021.100114](https://doi.org/10.1016/j.jlr.2021.100114).
- Donnelly et al.: proteostasis and HSF1 in aneuploid human cells; tolerance of aneuploidy is
  precisely why safety must be measured together with the molecular effect.
  [PubMed 25205676](https://pubmed.ncbi.nlm.nih.gov/25205676/),
  [DOI 10.15252/embj.201488648](https://doi.org/10.15252/embj.201488648).

## Provenance and reproduction

`src/figures/story.py` generates seven original diagrams. Before drawing, it compares its
sources with `docs/story_sources.sha256.json`; a mismatch aborts. The diagrams are not direct
readings of the BAM: they are an editorial synthesis of documented sources. SVG/PNG, renderer
and source hashes are recorded in `docs/story_figure_manifest.json`.

The `scientific-visualization` skill guided the separation of provenance, the explicit
representation of what is absent, and inspection at reading size. Methodological reference:
Kassis T, Agarwal V, He Y, Patel D, Brueckner AM (2026), *Scientific Agent Skills: A Library
of Procedural Knowledge for Research Agents*,
[DOI 10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065).

No accessibility certification or journal conformance is claimed.
