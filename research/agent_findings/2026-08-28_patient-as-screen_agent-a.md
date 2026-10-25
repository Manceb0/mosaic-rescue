# Patient-as-Screen: a screen with no input library

**Agent:** agent-a · **Date:** 2026-08-28 · **Workstream:** Issue #2 (Patient-as-Screen and natural rescue precedent)
**Scope note:** drug/repurposing search was explicitly out of scope for this assignment. No patient data were accessed (see *Repository and data state* below).

---

## Research question

Can constitutional mosaicism in MVA legitimately be treated as a naturally occurring perturbation screen, or is "Patient-as-Screen" a storytelling metaphor wearing the costume of a method?

Sub-question that actually decides it: **what would make within-patient chromosomal variation genuine mechanistic evidence instead of an analogy?**

---

## Why this matters

Patient-as-Screen is the load-bearing beam of MOSAIC RESCUE. Hypotheses 2 (Ghost Karyotypes), 3 (Fitness Landscape) and 5 (Mosaic Forecast) all inherit its validity. If the karyotype distribution observed in this child is dominated by physics and sampling rather than by selection, then every downstream inference is a decorated artifact — and a judge who knows the aneuploidy literature will see it in thirty seconds.

---

## Bottom line

- **Verdict: CONDITIONAL** — with a hard split:
  - **REJECT the strong form.** "MVA mosaicism is a perturbation screen whose surviving karyotypes reveal compensatory/rescue mechanisms" is not supported and is actively contradicted on three independent axes.
  - **PURSUE a restricted, reformulated form**, conditional on a data gate: *MVA is a within-patient isogenic natural experiment with an **unobserved input library**; the only analyzable quantity is the deviation of the observed karyotype spectrum from an explicitly estimated generation prior, and its most defensible readout is clone-level competitive advantage — which points at tumor risk, not at rescue.*
- **Current evidence level:**
  - The *design* (within-patient isogenic contrast in a constitutional mosaic) — **L3–L4 in humans**, and one instance carries functional validation.
  - The *specific claim* that MVA karyotype abundance encodes chromosome-specific fitness — **L1 at best**; **L0 for this patient** until cell-resolved data are confirmed to exist.

---

## Key findings

### 1. The screen is missing its T0 library, and that is the entire problem

A CRISPR/perturbation screen produces interpretable depletion because you sequence the **input**: the plasmid library and the T0 cells. Depletion is `log2(T_end / T_0)`. You never infer fitness from endpoint abundance alone.

MVA gives us three of the four ingredients and is *better* than an engineered screen on one of them:

| Screen requirement | MVA status |
|---|---|
| A perturbation library | ✅ continuously generated whole-chromosome dosage changes |
| A constant genetic background | ✅✅ **every cell shares the identical germline genome including the causal variant** — a purer isogenic contrast than any engineered screen |
| A phenotypic readout matched to perturbation resolution | ⚠️ requires per-cell genotype + per-cell phenotype; not yet confirmed to exist for this patient |
| **An input/T0 library representation control** | ❌ **absent. We only ever observe T_end.** |

This is the sharp version of the project's own warning `observed = generation × fitness × competition × sampling`. Without the first term, "depleted" and "never generated" are mathematically indistinguishable. *Every* ghost-karyotype claim is uninterpretable until the denominator exists.

The good news: **an external denominator now exists in the literature.** Klaasen & Kops (Nature 2022, PMID 35831506) measured per-chromosome missegregation probabilities by single-cell karyotype sequencing in untransformed diploid human cells and human intestinal organoids. Chromosomes 1–5, 8, 11 and X missegregate significantly *more* than a random ~4.3% baseline; chromosomes 14, 15 and 19–22 significantly *less*. The cause is nuclear position — peripheral chromosomes congress slowly and missegregate more. Forced relocation of chr9 to the lamina nearly doubled its error rate.

That is a **purely mechanical prior with no relationship to cellular fitness**, and it predicts exactly the pattern a naive analysis would misread: the small, gene-dense chromosomes (19–22) that everyone intuitively calls "lethal to lose" are simply the ones least likely to be missegregated in the first place. Any "ghost karyotype" list produced without this correction will be, in large part, a rediscovery of chromosome territory geometry.

### 2. The closest aneuploidy precedent (MAD1L1) establishes far less than it appears to

Villarroya-Beltri et al., *Science Advances* 2022 (PMID 36322655, DOI 10.1126/sciadv.abq5914; peer-reviewed; **human, n = 1 proband** + 2 heterozygous parents + 2 controls; ~33,604 PBMCs).

**What it did establish:**
- Biallelic germline *MAD1L1* → deficient SAC → 30–40% aneuploid blood cells; a distinct MVA-like syndrome with extreme tumor susceptibility.
- Non-uniform aneuploid cell states: chr12 gain enriched in intermediate B cells, chr18 gain enriched in γδ T cells, both clonally/subclonally expanded, each with a distinct transcriptional program (chr12+ B cells carrying **CLL-associated signatures**; chr18+ γδ T cells hypercytotoxic).
- A **non-cell-autonomous** systemic response: euploid proband cells showed IFN/NFκB inflammation versus control euploid cells, while aneuploid-vs-euploid *within* the proband showed no immune difference. Cell-autonomous effects were down-regulated translation and OXPHOS.

**What it did NOT establish — and this matters:**
- **No perturbation, no causal experiment.** No CRISPR, no MAD1 rescue, no ex vivo challenge. Association only.
- Aneuploidy was inferred by **inferCNV from scRNA-seq**, which called **4.0% of healthy control cells aneuploid**. That is the method's false-positive floor, against 13.6% in the proband. inferCNV is confounded by cell-type-specific expression programs — precisely the confounder for a claim of the form "chromosome X gain is enriched in cell type Y."
- The authors did **not** formally separate biased generation from post-generation selection, and say so.
- The two "selected" karyotypes sit in **lymphoid lineages that possess dedicated clonal-expansion machinery**. An antigen- or oncogenically driven lymphocyte clone drags its passenger aneuploidy along with it. The selection may be on the *clone*, not on the *karyotype*. In a 36-year-old with a dozen neoplasias, the parsimonious reading is that the screen surfaced pre-malignant clones.

So the closest published precedent is a **single-patient, association-only, inferCNV-based observation**. It proves the *readout is technically achievable*. It does not prove the karyotype spectrum encodes fitness rules.

### 3. Human cell competition says elimination is chromosome-*agnostic* — the screen may carry ~1 bit

Stem Cell Reports 2025 (PMID 40409259, DOI 10.1016/j.stemcr.2025.102506; peer-reviewed; **human** hESC H1/H9, iPSC WTC-11, CSES lines; preprint bioRxiv 2024.05.08.593217).

- Uniformly aneuploid hPSC populations proliferate fine. Aneuploid cells are eliminated **only in mosaic populations**, by cell-non-autonomous competition with diploid neighbours.
- Elimination occurred **irrespective of which chromosome was imbalanced**.
- The determinant was **relative** MYC/p53 versus *adjacent* cells, not absolute levels: non-neighbouring trisomic vs disomic cells showed no MYC difference. Flip the relative abundance and the aneuploid cell wins.

If fitness in a mosaic human tissue is set by a neighbour-relative MYC/p53 comparison rather than by chromosome identity, then survival/depletion encodes **local competitive context**, not chromosome-specific biology. The screen's information content collapses toward a single bit — *aneuploid vs euploid* — which is not a discovery.

Same direction from Pfau et al., *Genes Dev* 2016 (PMID 27313317; **mouse**): aneuploidy impairs HSC competitive fitness and is selected against in regenerating tissue generically, via reduced proliferative potential.

### 4. Even the phenotypic readout is mostly chromosome-agnostic

Sheltzer, Torres, Dunham & Amon, *PNAS* 2012 (PMID 22802626, DOI 10.1073/pnas.1209227109; peer-reviewed; **computational meta-analysis** across yeast, *Arabidopsis*, mouse, human): aneuploid cells across species share a common transcriptional signature — stress response up, cell-cycle/proliferation down — resembling an environmental stress response, **independent of which chromosome is affected**.

Dürrbaum et al., *BMC Genomics* 2014 (PMID 24548329, DOI 10.1186/1471-2164-15-139; peer-reviewed; **human cell lines**) partially rescues the FOR side by identifying chromosome-specific components alongside the shared response — so the per-karyotype signal is not zero, but it is a residual after a dominant shared axis.

Practical consequence: any scRNA-based Patient-as-Screen must **explicitly regress out the shared aneuploidy-stress axis first** and report how much variance survives. If the shared axis absorbs nearly everything, the hypothesis is dead in the data.

### 5. Where aneuploid clones demonstrably DO win in humans, the winners are oncogenic — not compensatory

This is the reframe I think the project most needs.

- hPSC culture adaptation: recurrent 20q11.21 gain, driven by **BCL2L1/BCL-XL** — an anti-apoptotic gene. Avery et al., *Stem Cell Reports* 2013 (PMID 24286026) showed BCL-XL overexpression phenocopies the 20q gain's selective advantage; Nguyen et al. (PMID 24217388) independently attributed improved survival to Bcl-xL. **Human cell line, functional perturbation — L3/L4.**
- The MAD1L1 patient's expanded chr12+ B cells carried **CLL-associated** signatures.
- In MVA, the classic clonal outcome documented in the clinical literature is **monosomy 7 → myelodysplastic syndrome**.

Every human case where an aneuploid clone reproducibly outcompetes its neighbours points down the anti-apoptotic / pro-proliferative axis. **A within-patient positive-selection screen in a CIN patient is therefore biased by construction toward discovering oncogenic drivers, not therapeutic rescue mechanisms.** MOSAIC RESCUE's Hypothesis 7 (Safe Rescue Corridor) is not a disclaimer bolted on at the end — it is a direct prediction about what Patient-as-Screen will find.

### 6. Revertant mosaicism is a real, strong precedent — for a different phenomenon

The precedent is genuine and well documented: first described in Lesch–Nyhan (1988); Hirschhorn's ADA-deficiency reversion (*Nat Genet* 1996, PMID 8673127); reversion identified across all major epidermolysis bullosa subtypes; Pasmooij et al. (*J Invest Dermatol* 2012, PMID 22318390) reported reversion in effectively all patients with generalized non-Herlitz JEB carrying *COL17A1* mutations. Mechanisms include true back mutation, intragenic crossover, mitotic gene conversion, second-site compensatory mutation, and copy-neutral LOH.

**But the analogy fails at exactly the point that matters.** In revertant mosaicism the *variable across cells is the causal lesion itself*, and the fitness gradient is directional and interpretable (corrected > mutant). In MVA the causal biallelic variant (*BUB1B* / *CEP57* / *TRIP13*) is **invariant in every cell**; what varies is a stochastic downstream *consequence* of the defect. MVA aneuploidy is the screen's *noise source*, not its *perturbation of the causal gene*. Calling MVA "natural gene therapy" is a category error, and the brief's own conditional-modules section already flags this — the literature confirms the flag was correct.

Worse for the analogy: van den Akker et al., *PLoS ONE* 2018 (PMID 29470523, DOI 10.1371/journal.pone.0192994; peer-reviewed; **computational/mathematical developmental model**) explains the high observed frequency of revertant patches with a "late-but-fitter revertant cell" model — reversion events are common (~216 expected per patient's skin), but which ones become *visible* is governed by developmental timing and stem-cell compartment dynamics, not by the corrected genotype's fitness alone.

Transposed to MVA: **clone size is dominated by when in development the missegregation occurred and in which progenitor.** Genetic drift plus developmental timing can generate a highly structured, non-uniform, entirely selection-free karyotype landscape.

### 7. The best actual precedent for "patient-as-screen" is not aneuploidy at all — and it works because it has a null model

Brzozowska et al., *Nat Genet* 2025 (PMID 40065168, DOI 10.1038/s41588-025-02125-1; peer-reviewed; **human liver tissue**, 5 PiZZ alpha-1 antitrypsin deficiency + 5 hemochromatosis controls; 306 laser-capture microdissections + WGS/WES).

- dN/dS showed **strong positive selection specific to A1ATD livers**: ~783 for truncating, ~1,772 for indels in *SERPINA1* (q < 2 × 10⁻¹⁶).
- **Convergent evolution in all five patients** — one patient had 11 independent *SERPINA1*-mutant clones within 0.3 cm².
- The selected variants were C-terminal truncations that **disrupt the domain-swap required for Z-A1AT polymerization**.
- **Functional validation:** CHO cells expressing truncated HaloTag-A1AT showed reduced ER inclusions and no polymer on native PAGE; pulse-chase showed proteasomal degradation/shorter half-life; immunohistochemistry showed truncation-variant hepatocytes had significantly lower polymer burden *in the patient's own liver*.
- The authors nominate C-terminal blockade/deletion as a therapeutic strategy.

Also in this family: Ng et al., *Nature* 2021 (PMID 34646017, DOI 10.1038/s41586-021-03974-6; **human liver**, 1,590 genomes / 34 samples) — convergent somatic mutation of *FOXO1*, *CIDEB*, *GPAM* in chronic liver disease, up to 9–14 independent clones per patient.

This is the template MOSAIC RESCUE should copy — and note **why** it works: `dN/dS` uses **synonymous sites as an internal neutral denominator**. It is a screen *with* an input control. That is precisely the ingredient MVA lacks, and it is why the A1ATD result is publishable and a naive MVA karyotype-frequency plot would not be.

### 8. Ascertainment and tissue bias are not a footnote — they are a competing complete explanation

- **Culture selection.** MVA is diagnosed on **cultured** cells with an aneuploid fraction typically >25% across multiple different chromosomes. Standard lymphocyte karyotyping requires PHA-driven proliferation, i.e. it is a proliferation-gated assay that discards exactly the slowly cycling or arrested aneuploid cells the screen is supposed to be about. Any depletion measured in cultured cells is confounded with in-vitro selection.
- **Tissue-limited mosaicism.** Pallister–Killian syndrome is the canonical demonstration: i(12p) is frequently **undetectable in cultured blood lymphocytes** while present at high fraction in skin fibroblasts, buccal mucosa and bone marrow (e.g., PMID 12082482; classic report showing normal karyotype in lymphocytes and CVS but mosaic tetrasomy 12p in fibroblasts, PMC1050184; one documented case 43% in lymphocytes vs 90% in fibroblasts). If a whole-chromosome imbalance can be invisible in one tissue and near-fixed in another *in the same person*, then a single-tissue karyotype spectrum measures the tissue, not the fitness landscape.
- **Detection method inflation.** Knouse et al., *PNAS* 2014 (PMID 25197050, DOI 10.1073/pnas.1415287111; **mouse and human tissue**) showed single-cell sequencing yields aneuploidy frequencies at least an order of magnitude below prior FISH-based estimates in liver and brain, overturning a decade of "aneuploidy is adaptive in these organs" speculation. The cautionary tale is exact: a technical artifact was read as a fitness signal by a whole field.
- **Survivorship.** Every published MVA cohort is drawn from children who survived to genetic diagnosis. Karyotypes incompatible with embryonic or fetal survival are absent from the sample for reasons that have nothing to do with cellular fitness in the sampled tissue.

### 9. The one design element that genuinely survives

Rafferty et al., *PLoS ONE* 2021 (PMID 34283872, DOI 10.1371/journal.pone.0254806; peer-reviewed; **human, n = 69** mosaic Down syndrome participants ages 1–44, plus 18 longitudinal over ~4 years).

Within-person comparison of isogenic trisomic vs disomic leukocytes (cytokinesis-block micronucleus assay + FISH for RUNX1/RUNX1T1): trisomic cells showed ~2× micronuclei (0.37 ± 0.35 vs 0.18 ± 0.11, P < 0.0001) and 4.8× abnormal nuclear patterns; longitudinally, trisomic SCINF rose 1.63× vs 1.13× in disomic cells.

This validates **the within-patient isogenic contrast as a real mechanistic instrument** in constitutional mosaicism: genetic background and environmental exposure are controlled by construction, at n = 1 individual. Note carefully what it measured, though — a phenotype **caused by** the aneuploidy, in a **known** karyotype. It did not infer fitness from abundance. That is the honest scope of the design.

---

## Primary evidence

| Claim | Source | Model / population | Evidence type | Level | Notes |
|---|---|---|---|---|---|
| Per-chromosome missegregation probability is strongly non-random and set by nuclear position (chr 1–5, 8, 11, X high; 14, 15, 19–22 low; baseline ~4.3%) | Klaasen & Kops, *Nature* 2022. PMID 35831506 · DOI 10.1038/s41586-022-04938-0 | Human RPE1-hTERT, BJ-hTERT, human intestinal organoids, cancer lines | Peer-reviewed; cell line + organoid; **functional perturbation** (monastrol randomization, Cas9 chromosome tracking, forced lamina relocation → ~2× error increase) | **L4** | Supplies the missing generation prior. Caveat: measured under MPS1i/AurBi, not in a SAC-deficient patient background |
| Cell competition eliminates aneuploid hPSCs **irrespective of which chromosome** is imbalanced, via **relative** MYC/p53 vs neighbours | *Stem Cell Reports* 2025. PMID 40409259 · DOI 10.1016/j.stemcr.2025.102506 | Human hESC (H1, H9), iPSC (WTC-11), CSES lines | Peer-reviewed; human cell line; functional | **L3** | Strongest single argument against chromosome-specific fitness inference. Preprint bioRxiv 2024.05.08.593217 |
| In a human constitutional CIN patient, aneuploid cell states are non-uniform: chr12+ intermediate B cells (CLL signature), chr18+ γδ T cells, both clonally expanded | Villarroya-Beltri et al., *Sci Adv* 2022. PMID 36322655 · DOI 10.1126/sciadv.abq5914 | **Human, n = 1** + 2 parents + 2 controls; ~33,604 PBMCs | Peer-reviewed; human; **association only**, inferCNV-based | **L1** | Closest precedent. 4.0% aneuploid calls in healthy controls = FP floor. No perturbation. Generation vs selection not separated |
| Aneuploidy induces a shared, largely chromosome-independent stress transcriptional response | Sheltzer et al., *PNAS* 2012. PMID 22802626 · DOI 10.1073/pnas.1209227109 | Yeast, *Arabidopsis*, mouse, human — meta-analysis | Peer-reviewed; computational | **L2** | Caps per-karyotype information content in any scRNA readout |
| Chromosome-specific transcriptional components exist alongside the shared response | Dürrbaum et al., *BMC Genomics* 2014. PMID 24548329 · DOI 10.1186/1471-2164-15-139 | Human cell lines (model aneuploidy) | Peer-reviewed; cell line | **L2** | The residual that keeps the hypothesis alive |
| Within-patient somatic variation in a constitutional monogenic disease can be read as a selection screen and yield a validated mechanism + therapeutic strategy | Brzozowska et al., *Nat Genet* 2025. PMID 40065168 · DOI 10.1038/s41588-025-02125-1 | **Human liver**, 5 PiZZ A1ATD + 5 controls, 306 LCM regions | Peer-reviewed; human tissue + CHO functional validation + in-situ IHC | **L4** | The template. Works because dN/dS supplies an internal neutral denominator |
| Convergent somatic mutation of metabolism genes under selection in diseased human tissue | Ng et al., *Nature* 2021. PMID 34646017 · DOI 10.1038/s41586-021-03974-6 | Human liver, 1,590 genomes / 34 samples | Peer-reviewed; human tissue | **L3** | Independent replication of the "diseased tissue as selection screen" design |
| Within-patient isogenic trisomic-vs-disomic contrast is a valid mechanistic instrument in constitutional mosaicism | Rafferty et al., *PLoS ONE* 2021. PMID 34283872 · DOI 10.1371/journal.pone.0254806 | **Human, n = 69** mosaic Down syndrome (+18 longitudinal) | Peer-reviewed; human; assay-based | **L3** | Validates the *design*, not abundance-based fitness inference |
| Somatic reversion of a causal germline variant confers strong lineage-specific selective advantage in humans | Hirschhorn et al., *Nat Genet* 1996. PMID 8673127 (ADA deficiency) | Human patient | Peer-reviewed; human | **L4** | Real precedent — but the variable is the causal lesion, not a downstream consequence |
| Revertant mosaicism is common, not rare — reversion in effectively all generalized non-Herlitz JEB *COL17A1* patients | Pasmooij et al., *J Invest Dermatol* 2012. PMID 22318390 | Human patients | Peer-reviewed; human | **L3** | Establishes the precedent's strength; does not transfer to MVA |
| Visibility of revertant clones is governed by developmental timing and stem-cell dynamics, not corrected-genotype fitness alone | van den Akker et al., *PLoS ONE* 2018. PMID 29470523 · DOI 10.1371/journal.pone.0192994 | Mathematical developmental model of human skin | Peer-reviewed; computational | **L2** | Drift + timing can produce structured, selection-free clone-size landscapes |
| Recurrent aneuploid clones that win in human cells are driven by anti-apoptotic genes (20q11.21 → BCL2L1/BCL-XL) | Avery et al., *Stem Cell Reports* 2013. PMID 24286026; Nguyen et al. PMID 24217388 | Human ESC | Peer-reviewed; human cell line; functional | **L4** | Positive selection in human cells surfaces oncogenic drivers |
| Aneuploidy generically impairs HSC fitness and is selected against in regenerating tissue | Pfau et al., *Genes Dev* 2016. PMID 27313317 | **Mouse** | Peer-reviewed; animal | **L3** | Purifying selection is generic, not karyotype-informative |
| Prior FISH-based aneuploidy frequencies in normal tissue were overestimates by ≥1 order of magnitude | Knouse et al., *PNAS* 2014. PMID 25197050 · DOI 10.1073/pnas.1415287111 | Mouse and human tissue | Peer-reviewed; human/animal | **L3** | A whole field read a detection artifact as a fitness signal |
| Whole-chromosome imbalance can be near-absent in cultured lymphocytes and near-fixed in fibroblasts of the same person | Pallister–Killian literature. PMID 12082482; PMC1050184 | Human patients | Peer-reviewed; human | **L3** | Single-tissue karyotype spectra measure tissue, not fitness |
| MVA is defined and diagnosed on **cultured** cells at typically >25% aneuploid fraction | Hanks et al., *Nat Genet* 2004. PMID 15475955 · DOI 10.1038/ng1449; Nat Rev Genet 2024 review DOI 10.1038/s41576-024-00762-6 | Human patients | Peer-reviewed; human (review for orientation only) | **L5** (diagnostic fact) | Proliferation-gated assay = built-in selection filter |

---

## Contradictory evidence

| Claim challenged | Source | Why it matters |
|---|---|---|
| "Surviving karyotypes reveal chromosome-specific fitness rules" | *Stem Cell Reports* 2025, PMID 40409259 | Elimination is chromosome-agnostic and set by neighbour-relative MYC/p53. Survival encodes local context, not chromosome identity. Reduces the screen to ~1 bit |
| "Missing/depleted karyotypes are informative (Ghost Karyotypes)" | Klaasen & Kops, PMID 35831506 | Chromosomes 14, 15, 19–22 are intrinsically rarely missegregated for reasons of nuclear geometry. Absent normalization, the ghost list is a map of chromosome territories |
| "Per-cell karyotype predicts per-cell state" | Sheltzer 2012, PMID 22802626 | The dominant transcriptional axis in aneuploid cells is shared and chromosome-independent |
| "Clone abundance reflects fitness" | van den Akker 2018, PMID 29470523 | Developmental timing and stem-cell compartment dynamics dominate clone visibility; drift generates structure without selection |
| "The MAD1L1 case proves nonrandom selection" | Villarroya-Beltri 2022, PMID 36322655 (self-limitations) | n = 1; inferCNV calls 4.0% of *healthy control* cells aneuploid; no perturbation; the "selected" karyotypes sit in lymphoid lineages with dedicated clonal-expansion machinery and oncogenic signatures — selection may be on the clone, not the karyotype |
| "MVA is natural gene therapy / revertant mosaicism" | Structural argument + Hirschhorn 1996 / Pasmooij 2012 | In revertant mosaicism the *causal lesion* varies across cells. In MVA the causal lesion is invariant and only its downstream stochastic consequence varies. Category error |
| "Aneuploid states that persist are the ones we should try to mimic therapeutically" | Avery 2013 PMID 24286026; MAD1L1 chr12+ CLL signature; monosomy 7 → MDS in MVA | The winners of within-patient aneuploid competition are anti-apoptotic/pro-proliferative. The screen is biased toward oncogenic, not compensatory, mechanisms |
| "Observed mosaic fractions are biological" | Knouse 2014 PMID 25197050; Pallister–Killian PMID 12082482; MVA cultured-cell diagnostic criteria | Detection method, tissue choice, and PHA-driven culture selection each independently reproduce the observation |

---

## What is directly supported vs inferred

### Directly supported
- MVA generates a genuinely isogenic set of chromosomally distinct human cells within one individual (L5, definitional).
- Within-patient isogenic trisomic-vs-disomic contrast is a valid instrument for measuring aneuploidy-caused phenotypes in constitutional mosaicism (L3, human n = 69).
- Within-patient somatic variation in a constitutional monogenic disease **has** been read as a selection screen and **has** produced a mechanistically validated, therapeutically directed result — in point mutations of the causal gene, with dN/dS as the null model (L4, human).
- Per-chromosome missegregation probability is strongly non-random and driven by nuclear position (L4).
- In a human MVA-like patient, aneuploid single-cell states are non-uniform and some aneuploid clones expand (L1).

### Inferred (and currently unsupported)
- That the persistence/depletion pattern of chromosomes in *this patient* encodes chromosome-specific fitness. **Not supported.**
- That an absent karyotype was eliminated rather than never generated or never detected. **Explicitly forbidden by `docs/claims_we_cannot_make.md` and by Klaasen & Kops.**
- That any persistent aneuploid state represents a compensatory or protective adaptation. **Contradicted in direction** by the 20q11.21/BCL-XL and CLL-signature evidence.
- That findings from cultured patient cells reflect in-vivo selection.

---

## Alternative explanations that generate the same observation

Ranked by how much of the observed karyotype spectrum they can explain on their own:

1. **Generation bias (mechanical).** Nuclear position sets per-chromosome missegregation rate. Could plausibly explain most of the rank order by itself. — Klaasen & Kops PMID 35831506.
2. **Culture / proliferation gating.** MVA karyotyping requires PHA-stimulated proliferating cells; non-proliferating aneuploid cells are structurally invisible. — MVA diagnostic practice.
3. **Tissue composition and tissue-limited mosaicism.** Same imbalance, 43% vs 90% across tissues in one person; sometimes undetectable in one tissue entirely. — Pallister–Killian, PMID 12082482.
4. **Detection power scaling with chromosome size / gene density.** Small chromosomes are harder to call by inferCNV and by low-coverage scWGS; gene-dense chromosomes are exactly where expression-based CN inference is most confounded. — Knouse PMID 25197050 as the cautionary precedent.
5. **Developmental timing + genetic drift.** Early missegregation → large clone regardless of fitness; late → invisible. Produces structured, non-uniform landscapes with zero selection. — van den Akker PMID 29470523.
6. **Neighbour-relative competition rather than intrinsic karyotype fitness.** Same karyotype wins or loses depending on the MYC/p53 of the cell next to it. — PMID 40409259.
7. **Lineage-intrinsic clonal expansion carrying passenger aneuploidy.** Lymphoid clones expand for antigenic/oncogenic reasons; the karyotype is along for the ride. — MAD1L1 chr12+/chr18+ observation.
8. **Shared aneuploidy stress response masquerading as karyotype-specific state.** — Sheltzer PMID 22802626.
9. **Survivorship / ascertainment.** Cohorts contain only children who survived to diagnosis.

**A defensible Patient-as-Screen result must beat all nine.** Numbers 1–4 are addressable computationally with the right data; 5–9 require design choices (multi-tissue, uncultured, longitudinal, cell-type-covaried).

---

## Required hackathon data modality

**Hard gate. Patient-as-Screen at karyotype resolution requires joint per-cell genotype + phenotype in an unselected sample.**

Required (any one of the first two, plus as much of the rest as exists):
1. **Single-cell DNA / karyotype sequencing** (scWGS, scKaryo-seq, DLP+, 10x CNV) on **fresh, uncultured** cells — the gold standard; or
2. **scRNA-seq** with per-cell CN inference (inferCNV/CopyKAT class) — acceptable only with an explicit false-positive floor estimated from matched controls, because the MAD1L1 study's own control floor was 4.0%.
3. **≥2 tissues with different proliferative histories** (e.g., PBMC + fibroblast/buccal) — required to separate tissue composition from fitness.
4. **≥2 timepoints** — required for any depletion/forecast claim.
5. **Deep bulk WGS/BAM** — fallback: allelic-imbalance and coverage-based bulk mosaic fingerprint. Gives a population-level CN spectrum but **no per-cell genotype–phenotype link**, therefore **cannot** support Patient-as-Screen; it can only support a normalized-spectrum test (Analysis A below) at low resolution.
6. Metadata that is easy to forget and decisive: **whether each sample was cultured, and for how long.**

**Decision rule.** If the gated dataset (SageBio/mva-hackathon-2026-data) contains only WGS/VCF and bulk phenotype — the currently confirmed public expectation — then:
- Patient-as-Screen as a *cell-resolved screen* is **not executable for this patient**. It should be declared **PARKED at L0** in `hypotheses/`, and the project must not present a bulk-derived karyotype frequency plot as a fitness landscape.
- What **remains executable** is Analysis A below on the bulk mosaic fingerprint, reported as a **normalized spectrum test with an explicit negative result if it is one**.

---

## Proposed analysis (exact)

### Analysis A — Generation-normalized selection coefficients (the core test)

For each chromosome `c` and direction `d ∈ {gain, loss}`:

```
s(c,d) = log2[ f_obs(c,d) / ( p_gen(c,d) · π(c,d) ) ]
```

- `f_obs(c,d)` — observed fraction of cells (or bulk-inferred clonal fraction) carrying that imbalance.
- `p_gen(c,d)` — **generation prior**, from Klaasen & Kops 2022 per-chromosome missegregation probabilities, renormalized to sum to 1; a missegregation event produces one gain and one loss, so gain/loss are coupled and that coupling is a testable constraint in itself.
- `π(c,d)` — **detection power**, estimated by simulation: spike synthetic CN events of each chromosome into the real data at known frequency, run the identical calling pipeline, measure recall as a function of chromosome length and gene density.

Fit a **beta-binomial / Dirichlet-multinomial** model (aneuploidy counts are overdispersed) with a permutation null over chromosome labels. Report **posterior credible intervals on every `s(c,d)`**, never point estimates.

**Then report the number that decides the hypothesis:** the fraction of variance in `f_obs` explained by `p_gen` alone, via formal model comparison (ΔWAIC or ΔLOO, generation-only vs generation+selection). Publish this whether it is favourable or not.

### Analysis B — Information-content test (does the screen carry more than 1 bit?)

Compute mutual information `I(chromosome identity ; cell state)` against a permutation null, where cell state is the scRNA embedding. Then decompose per-cell phenotype:

```
state ~ shared_aneuploidy_stress_axis  +  Σ_c chromosome_dosage_c  +  cell_type  +  (1|donor/batch)
```

The shared stress axis is defined a priori from the Sheltzer 2012 conserved signature so it cannot be tuned post hoc. **If chromosome-specific terms do not survive inclusion of the shared axis and cell type, the screen has no chromosome-resolved information.**

### Analysis C — Confound partition

Variance partition of `f_obs` across: `p_gen` | tissue | culture status | cell type | detection power | residual. The residual is the only candidate selection signal. State its size as a percentage. If it is small, say so in the headline.

### Analysis D — Coupled gain/loss consistency check

Because a single missegregation yields a reciprocal gain and loss, `f_obs(c,gain)` and `f_obs(c,loss)` should be equal *at generation*. Asymmetry between them is a **selection signal that is internally controlled for generation bias** — the same chromosome serves as its own denominator. This is the cheapest, most robust test in the whole plan and it survives even with mediocre data. **I would run this first.**

---

## Expected scientific visualization

**A screen-normalized volcano, not a karyotype heatmap.**

- x-axis: `log2(observed / generation-expected)` per chromosome × direction.
- y-axis: `-log10(p)` from the permutation null.
- Point size: estimated detection power `π`.
- Point colour: Klaasen nuclear-position rank (periphery → centre), so the reader can see instantly whether the "signal" is just geometry.
- A shaded grey band marking the region where the generation prior alone explains the data.
- A companion inset: the Analysis D reciprocal gain/loss asymmetry plot.

Why this figure: every other team will produce a karyotype-fraction heatmap, which is unfalsifiable eye candy. This one **can kill the hypothesis in a single glance** — if all points fall inside the grey band, the figure *is* the rejection, and publishing it is a stronger result than a decorated confirmation.

---

## Falsification test

Patient-as-Screen is **rejected** if all three hold:

1. **Spectrum test:** after correcting for `p_gen` and `π`, posterior credible intervals on all `s(c,d)` overlap zero, and model comparison favours the generation-only model (ΔWAIC/ΔLOO in favour of the null).
2. **Information test:** `I(chromosome ; cell state)` is not above the permutation null, and chromosome-specific terms do not survive inclusion of the shared aneuploidy-stress axis and cell-type covariates.
3. **Asymmetry test:** reciprocal gain/loss frequencies per chromosome are statistically indistinguishable (no internally-controlled selection signal).

Any **one** of these failing → downgrade to PARK. All three → REJECT and say so in the deliverable.

**Fast pre-registered kill test (run before anything else, if data permit):** if the aneuploid fraction and chromosome spectrum in **cultured** patient cells differ materially from **uncultured** cells of the same tissue, then the "screen" is measuring culture selection and every abundance-based inference must be discarded.

---

## What result would make us abandon this idea?

- The dataset contains no cell-resolved modality → abandon the cell-resolved form immediately, no negotiation. Do not substitute bulk and rename it.
- `p_gen` alone explains the spectrum → abandon Ghost Karyotypes as a discovery engine; it becomes a validation of Klaasen & Kops in a patient, which is a small but honest result.
- The shared aneuploidy-stress axis absorbs the phenotypic variance → abandon per-karyotype mechanistic claims; retain only aneuploid-vs-euploid contrasts.
- Every enriched clone turns out to be lymphoid and antigen/oncogenically driven → the observation belongs to tumour surveillance, not to rescue discovery.

---

## Transferability beyond MVA

**High for the reformulated method, low for the aneuploidy-specific version.**

- The **generation-normalized within-patient selection screen** transfers to any constitutional mosaic disease with a cell-resolved readout: mosaic Down syndrome, Pallister–Killian, mosaic RASopathies/overgrowth syndromes, revertant genodermatoses, A1AT-deficiency liver, GATA2 and other somatic-genetic-rescue immunodeficiencies, clonal haematopoiesis. In the point-mutation setting the denominator problem is already solved (dN/dS), which is why that literature is producing L3–L4 results and the aneuploidy literature is not.
- The **aneuploidy-specific version** transfers poorly, because `p_gen` for whole chromosomes has been measured in only a handful of cell types and under induced (not spontaneous, not SAC-deficient) error conditions.
- **The genuinely portable contribution** would be a reusable statement: *any within-patient natural-screen claim must declare its input-library estimate and its detection-power model, or it is not a screen.* That is a methodological standard other rare-disease teams could adopt directly.

---

## "How did you notice that?" factor

**4 / 5.**

Two things I do not expect other teams to notice:

1. **The missing T0 library.** Framing MVA explicitly as "a pooled screen sequenced only at endpoint" makes the flaw unavoidable and — crucially — makes it *fixable*, because Klaasen & Kops 2022 supplies an external per-chromosome generation prior nobody in the MVA field appears to be using for this purpose. The reciprocal gain/loss asymmetry test (Analysis D) is a self-controlled version of the same idea that needs no external prior at all.
2. **The direction of selection points at cancer, not at rescue.** Every human system where aneuploid clones demonstrably win — 20q11.21/BCL-XL in hPSCs, the CLL-signature chr12+ B cells in the MAD1L1 patient, monosomy 7 → MDS in MVA — selects anti-apoptotic and pro-proliferative states. A within-patient positive-selection screen in a CIN patient is therefore **structurally biased toward discovering oncogenic drivers**. This converts Hypothesis 7 (Safe Rescue Corridor) from a safety disclaimer into a *prediction Patient-as-Screen makes about its own output*, and it suggests the most defensible deliverable is a within-patient clonal-risk instrument rather than a rescue-discovery engine.

Not a 5, because the individual components (generation bias, culture selection, tissue-limited mosaicism) are each well known in their own subfields — the contribution is the assembly and the screen-design framing, not a new observation.

---

## Recommended next action

**Decision for the project (recommend adopting):**

1. **Rename and re-scope the hypothesis** in `hypotheses/` from "Patient-as-Screen" to something like *"Within-patient isogenic contrast with an estimated generation prior."* The current name promises a screen we cannot deliver and invites exactly the criticism above. Keep the tagline for the README; do not let it define the method.
2. **Gate it on Issue #1.** No Patient-as-Screen analysis activates until the dataset inventory confirms a cell-resolved modality. Write that gate into `notebooks/03_mosaic_landscape.ipynb` as an executable assertion, not a comment.
3. **Log the contradictions now.** `research/contradictions.md` currently holds only the empty C001 row; PMIDs 40409259, 35831506, 22802626, 29470523 belong in it today, at severity high/high/medium/high. Same for `research/evidence_registry.md` (only E001 exists).
4. **Reposition the deliverable** — the honest, novel, and *safer* framing is: MVA gives a within-patient clonal-competition readout whose natural output is tumour-risk-relevant clonal advantage. That feeds Hypothesis 7 directly and is defensible even if the fitness-landscape reconstruction fails.

### Next Best Experiment

**Measure the patient's own generation prior — i.e., sequence the input library.**

Preferred (cheapest, most direct): **single-micronucleus sequencing from patient-derived cells.** Klaasen & Kops showed that missegregating chromosomes preferentially become entrapped in micronuclei and that micronuclear content mirrors the missegregation spectrum. Isolating and sequencing single micronuclei from patient fibroblasts therefore yields `p_gen(c)` **in the patient's own SAC-deficient background**, without needing longitudinal culture and without waiting for selection to act.

Alternative if micronucleus isolation is not feasible: short-term patient fibroblast culture with single-cell karyotype sequencing at the earliest post-mitotic timepoint (T0, before selection can operate) versus a late timepoint — a literal T0-vs-Tend screen readout.

**Why this is the highest-information experiment available:** it supplies the single missing term that currently makes every Ghost Karyotype and Fitness Landscape claim uninterpretable. With `p_gen` measured rather than borrowed, `s(c,d)` becomes an estimable selection coefficient instead of an assumption, and the entire hypothesis moves from L0/L1 to a genuinely testable L2–L3. Without it, no amount of additional patient sequencing helps.

**Zero-cost interim step (run this week, requires no wet lab):** implement Analysis D (reciprocal gain/loss asymmetry) on whatever CN data the dataset turns out to contain. It is the only selection test that is internally controlled for generation bias, and it will tell us early whether there is any signal worth pursuing.

---

## Repository and data state (verified 2026-08-28)

Confirming and extending the brief's verified-absent list, at HEAD `554c82b`:

- `research/evidence_registry.md` and `research/contradictions.md` contain only empty template rows (E001, C001). **No evidence has been recorded by any agent yet.** This report's claims table is written to be paste-compatible with both schemas.
- `hypotheses/` contains only `README.md` and `hypothesis_template.md` — no instantiated hypothesis file exists for Patient-as-Screen, so there is currently nothing to promote *into*.
- `research/agent_findings/` contained only the format README before this file.
- No `requirements.txt`, `environment.yml`, `pyproject.toml`, or `LICENSE`.
- No file mentions Hugging Face, SageBio, the dataset ID, or the challenge space; "Track 2" appears nowhere in the repo.
- Nine open GitHub Issues (#1–#9). Workstream G (aneuploid stress transfer biology) has a prompt in `docs/agent_prompts.md` but no Issue — still orphaned.
- `data/` holds only `README.md`; **the gated dataset has not been downloaded.** No patient data were accessed for this report. All evidence here is external literature.

**Additional infrastructure gap this report exposes:** there is no `research/priors/` or equivalent location for **external quantitative priors** (per-chromosome missegregation probabilities, detection-power curves, the Sheltzer shared-stress gene signature). Analyses A–D all consume such priors, and they must be version-pinned and citable or the normalization is not reproducible. Recommend creating `research/priors/` with the Klaasen & Kops per-chromosome table as its first entry.

---

## References

1. Klaasen SJ, et al. Nuclear chromosome locations dictate segregation error frequencies. *Nature* 2022;607(7919):604–609. PMID 35831506 · DOI 10.1038/s41586-022-04938-0 · https://www.nature.com/articles/s41586-022-04938-0 — peer-reviewed; human cell line + organoid; functional.
2. Cell competition eliminates aneuploid human pluripotent stem cells. *Stem Cell Reports* 2025;20(6):102506. PMID 40409259 · DOI 10.1016/j.stemcr.2025.102506 · https://www.cell.com/stem-cell-reports/fulltext/S2213-6711(25)00110-9 — peer-reviewed; human cell line. Preprint: bioRxiv 2024.05.08.593217.
3. Villarroya-Beltri C, et al. Biallelic germline mutations in MAD1L1 induce a syndrome of aneuploidy with high tumor susceptibility. *Sci Adv* 2022;8(44):eabq5914. PMID 36322655 · DOI 10.1126/sciadv.abq5914 · https://www.science.org/doi/10.1126/sciadv.abq5914 — peer-reviewed; human n=1; association only. Preprint: bioRxiv 2022.08.08.503198.
4. Brzozowska N, et al. Selection for somatic escape variants in SERPINA1 in the liver of patients with alpha-1 antitrypsin deficiency. *Nat Genet* 2025;57(4). PMID 40065168 · DOI 10.1038/s41588-025-02125-1 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11985350/ — peer-reviewed; human tissue + cell-line functional validation.
5. Ng SWK, et al. Convergent somatic mutations in metabolism genes in chronic liver disease. *Nature* 2021;598:473–478. PMID 34646017 · DOI 10.1038/s41586-021-03974-6 — peer-reviewed; human tissue.
6. Rafferty K, et al. Trisomy 21-associated increases in chromosomal instability are unmasked by comparing isogenic trisomic/disomic leukocytes from people with mosaic Down syndrome. *PLoS ONE* 2021;16(7):e0254806. PMID 34283872 · DOI 10.1371/journal.pone.0254806 — peer-reviewed; human n=69.
7. Sheltzer JM, Torres EM, Dunham MJ, Amon A. Transcriptional consequences of aneuploidy. *PNAS* 2012;109(31):12644–12649. PMID 22802626 · DOI 10.1073/pnas.1209227109 — peer-reviewed; computational meta-analysis (yeast/plant/mouse/human).
8. Dürrbaum M, et al. Unique features of the transcriptional response to model aneuploidy in human cells. *BMC Genomics* 2014;15:139. PMID 24548329 · DOI 10.1186/1471-2164-15-139 — peer-reviewed; human cell line.
9. van den Akker PC, et al. A "late-but-fitter revertant cell" explains the high frequency of revertant mosaicism in epidermolysis bullosa. *PLoS ONE* 2018;13(2):e0192994. PMID 29470523 · DOI 10.1371/journal.pone.0192994 — peer-reviewed; computational model of human skin.
10. Pasmooij AMG, et al. Natural gene therapy may occur in all patients with generalized non-Herlitz junctional epidermolysis bullosa with COL17A1 mutations. *J Invest Dermatol* 2012. PMID 22318390 — peer-reviewed; human.
11. Hirschhorn R, et al. Spontaneous in vivo reversion to normal of an inherited mutation in a patient with adenosine deaminase deficiency. *Nat Genet* 1996. PMID 8673127 — peer-reviewed; human.
12. Avery S, et al. BCL-XL mediates the strong selective advantage of a 20q11.21 amplification commonly found in human embryonic stem cell cultures. *Stem Cell Reports* 2013. PMID 24286026 — peer-reviewed; human ESC; functional.
13. Nguyen HT, et al. Gain of 20q11.21 in human embryonic stem cells improves cell survival by increased expression of Bcl-xL. PMID 24217388 — peer-reviewed; human ESC; functional.
14. Pfau SJ, Silberman RE, Knouse KA, Amon A. Aneuploidy impairs hematopoietic stem cell fitness and is selected against in regenerating tissues in vivo. *Genes Dev* 2016;30(12):1395–1408. PMID 27313317 — peer-reviewed; mouse.
15. Knouse KA, Wu J, Whittaker CA, Amon A. Single cell sequencing reveals low levels of aneuploidy across mammalian tissues. *PNAS* 2014;111(37):13409–13414. PMID 25197050 · DOI 10.1073/pnas.1415287111 — peer-reviewed; human and mouse tissue.
16. Tissue-limited mosaicism in Pallister-Killian syndrome — a case in point. PMID 12082482 — peer-reviewed; human. See also: normal karyotype in lymphocytes and CVS but mosaic tetrasomy 12p in skin fibroblasts, PMC1050184.
17. Hanks S, et al. Constitutional aneuploidy and cancer predisposition caused by biallelic mutations in BUB1B. *Nat Genet* 2004;36(11):1159–1161. PMID 15475955 · DOI 10.1038/ng1449 — peer-reviewed; human.
18. Mosaic variegated aneuploidy in development, ageing and cancer. *Nat Rev Genet* 2024. DOI 10.1038/s41576-024-00762-6 — peer-reviewed **review**; used for orientation only, no mechanistic claim rests on it.
19. Frattini D, et al. A distinctive type of mosaic variegated aneuploidy: case report and review of the literature. *Am J Med Genet A* 2025. DOI 10.1002/ajmg.a.63901 — peer-reviewed; human case report; orientation.
