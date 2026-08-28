# External Dataset Manifest

Deliverable for [Issue #4](https://github.com/Manceb0/mosaic-rescue/issues/4) ("datasets/tools
shortlist"). Promoted from the Synthetic Rescue audit
(`research/agent_findings/2026-08-28_synthetic-rescue_agent-c.md`, §3).

Patient data tells us what may be happening in this child. These resources tell us whether the
interpretation survives independent evidence.

## The distinction that matters

**Rescue-queryable** means the resource can answer *"what second perturbation compensates for the
first defect?"*

**Dependency-only** means it can answer *"what kills this cell?"* — a different question that is
routinely mistaken for the first one.

Inverting a dependency into a rescue claim is the most likely way this project produces a
confident, wrong result.

## Rescue-queryable

| Resource | ID / URL | Content | Notes for MVA |
|---|---|---|---|
| **BioGRID** | thebiogrid.org | Curated genetic interactions with explicit `Synthetic Rescue`, `Dosage Rescue`, `Phenotypic Suppression` evidence codes (PMID 33070389) | **The only structured rescue ontology that exists.** Overwhelmingly *S. cerevisiae*. Query BUB1B/TRIP13/CEP57/MAD2L1BP orthologs (BUB1, MAD3, PCH2, MAD2, CDC5) first. Expect thin human returns |
| **Ünlü et al. human suppression network** | PMID 37821946 · DOI 10.1186/s13073-023-01232-0 | 476 human suppression interactions, 93 query genes, 484 genes | **The only human rescue dataset in existence.** 302 from cultured cells, 180 from patient studies, **only 6 overlap** — 99% of interactions come from exactly one study type. Includes an RF suppressor predictor (AUC 0.69) |
| **TheCellMap / yeast SGA** | thecellmap.org | Quantitative yeast GI scores including positive (buffering/suppressive) interactions | Positive GIs are the systematic, quantitative version of rescue. Best-powered rescue resource on Earth — in yeast |
| **SGD / PomBase / FlyBase / WormBase** | yeastgenome.org et al. | Curated allele-level "suppressor of" annotations | FlyBase suppressor annotations are how the `polo`/`bubR1` result is findable |
| **Horlbeck et al. human GI map** | PMID 30033366 | CRISPRi double-knockdown, 222,784 gene pairs, K562 + Jurkat; classifies buffering (positive) GIs | Buffering interactions are rescue-adjacent **in human cells**. Two cancer lines only; treat any single-line GI as context-specific |
| **Norman et al. combinatorial Perturb-seq** | PMID 31395745 | CRISPRa, 105 single + 131 dual perturbations, ~91k cells, K562; classifies suppression/epistasis/neomorphic | True epistasis, but tiny and K562-only. Best existing **template** for the analysis we want; not a source of MVA answers |

## Partial — signature reversal, not epistasis

| Resource | ID / URL | Why partial |
|---|---|---|
| **Replogle et al. genome-scale Perturb-seq** | PMID 35688146 | Single perturbations only. Supports transcriptional signature-reversal queries, **not** epistasis. Its **RPE1 arm is the single most constitutionally-relevant human perturbation dataset available** — near-diploid, hTERT-immortalised, TP53-WT, non-cancer. This is the resource to build on |
| **BioGRID ORCS** | orcs.thebiogrid.org | ~2,200+ curated genome-wide CRISPR screens. Positive-selection/resistance screens *are* rescue signal — but of a drug or toxin, not of a constitutional mutation, and they are a minority of screens |
| **LINCS / CMap** | clue.io | Signature reversal only. Belongs to Workstream I. Do not let signature reversal masquerade as genetic rescue |
| **JUMP Cell Painting** | broad.io/jump | Morphological reversal only. Same caution as CMap |
| **MGI / IMPC** | informatics.jax.org · mousephenotype.org | MGI curates modifier/suppressor alleles. Where the BubR1/p16 and BubR1-overexpression results live |
| **MaveDB / DMS** | mavedb.org | No use for inter-genic rescue. Relevant **only** for intragenic second-site suppressors where a DMS assayed double mutants (rare) — that is Workstream F's call |

## Dependency-only — do not use for candidate generation

| Resource | Why it is excluded |
|---|---|
| **DepMap** (CRISPR/Chronos, RNAi) | Gene-effect scores across ~1,100 **cancer** lines. Positive Chronos scores mean "KO speeds up this cancer line" — a proliferation-suppressor statement about a transformed cell, not a rescue statement about a query defect. **Actively hazardous for this project** (see below) |

### Why DepMap is worse than merely irrelevant here

1. **Its principal artefact is copy number.** Cas9 cutting produces a copy-number-proportional,
   gene-independent antiproliferative effect — the entire reason CERES and Chronos exist
   (Meyers et al., *Nat Genet* 2017, PMID 29083409). A disease defined by variable chromosome copy
   number is the worst possible consumer of a dependency map whose main artefact *is* copy number.
2. **The reference panel is p53-crippled.** Cas9 editing is p53-dependently toxic and selects
   p53-deficient cells (Ihry et al., *Nat Med* 2018, PMID 29892062). The panel has therefore
   **already solved aneuploidy tolerance** — the exact phenotype we want to study.
3. **Chromosome-level fitness is tissue-specific**, not chromosome-intrinsic (Sack et al., *Cell*
   2018, PMID 29576454).

**Retain DepMap for one purpose only: safety inversion.** Ask "is our candidate axis an aneuploid
dependency — i.e. are we about to make genomically unstable cells fitter?"

## Bottom line

Rescue signal exists in public data, but essentially all of it is (i) yeast, (ii) two human cancer
cell lines, or (iii) 476 hand-curated human facts.

**There is no public dataset containing rescue evidence for any MVA gene in any human cell.**
Anyone who claims otherwise is reading a dependency map.
