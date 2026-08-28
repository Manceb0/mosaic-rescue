# Ghost Karyotypes and the Aneuploid Fitness Landscape — adversarial audit (Hypotheses 2 and 3)

Agent: agent-b (Ghost Karyotypes / Fitness Landscape stream, GitHub Issue #3)
Date: 2026-08-28
Repo HEAD at time of writing: 27299a0. Scope: external literature and public datasets only — `data/` is empty, the gated dataset has not been downloaded, so **no patient-specific analysis was performed or is claimed here.**
Out of scope by assignment: drug search.

---

## Research question

Can a chromosomal state that is **missing or depleted** relative to a missegregation-based expectation be separated from *"never generated"*, *"not sampled"* and *"not detectable"* — using data a hackathon team can realistically obtain?

The project's own decomposition is:

```
observed abundance = generation probability x intrinsic fitness x competition x sampling/tissue/detection
```

Write it per state *k*:

```
E[obs_k] = g_k * s_k * c_k * d_k
```

## Why this matters

Ghost Karyotypes is the most rhetorically attractive idea in MOSAIC RESCUE ("we read the negative space"). It is also the one most likely to produce a beautiful figure with no inferential content. If it cannot be made identifiable it should not be the scientific core, because a hackathon jury with a statistician on it will find the hole in ninety seconds.

---

## Bottom line

- **Hypothesis 2 (Ghost Karyotypes), literal form — REJECT.**
  A single static sample gives one number per state (44 single-chromosome states) and asks for four unknowns per state. It is underdetermined *by construction*: 44 observations, ~176 unknowns. No amount of N fixes a non-identifiability. This is not my opinion; it is the explicitly stated problem the CINner group had to build an entire ABC framework to attack (Xiang, Liu & Dinh 2024, PMID 39085295).
- **Hypothesis 2, reframed as a chromosome x tissue (or chromosome x cell-type) interaction test — CONDITIONAL, and genuinely defensible.** See "The one reframing that survives" below. This is the single most useful thing in this report.
- **Hypothesis 3 (Fitness Landscape) via ALFA-K on patient data — PARK.** ALFA-K requires longitudinal single-cell copy-number data. It is not applicable to a static sample, and its authors state that its estimates for *deleterious* CNAs — precisely the ghost region — are **biased upwards and should be interpreted with caution.** ALFA-K is structurally blind to exactly the thing Hypothesis 2 wants it to see.
- **Hypothesis 3 as an external-data methods demonstration — CONDITIONAL / PURSUE.** Running the pipeline on public longitudinal scDNA data and publishing an honest power curve is a legitimate, defensible hackathon deliverable.
- **Current evidence level for "depletion in this patient reflects selection": L0.** No patient data exist yet. The generic claim "aneuploid states are under negative selection in human cells" is L4 (replicated functional evidence across systems). The claim "*this specific missing state* is missing *because* of selection" is L0 until the null model is measured, not assumed.

---

## Key findings

1. **The null model is the binding constraint, not N.** Chromosome-specific missegregation in human cells is demonstrably non-random *and the bias depends on the perturbation used to induce it* (Worrall et al. 2018, PMID 29898405). Chromosomes 1 and 2 were enriched ~5x over chance among lagging chromatids under nocodazole/monastrol/MG132; under reversine the bias inverted (chr1 reduced, chr17/18 enriched). So the per-chromosome generation prior carries roughly **5-fold, mechanism-dependent uncertainty**. Any depletion smaller than the null's own error bar is unidentifiable **at any sample size**.
2. **Human embryo data give a partly usable, partly contradictory generation prior.** McCoy et al. 2015 (PMID 26491874; 28,052 day-3 blastomeres + 18,387 trophectoderm biopsies) found putative *mitotic*-origin aneuploidy rates that vary by chromosome and correlate with **chromosome length** (r = 0.734, P = 1.0e-4) at day 3 — a mechanistically plausible, quantitative generation prior. *Meiotic* errors instead concentrate on chr15/16/21/22 (4–6% each). MVA is a mitotic-checkpoint disease, so the length-scaled mitotic prior is the relevant one — but it comes from cleavage-stage embryos, not from a child's somatic tissue, and the authors state the rates are "likely particular to the IVF population."
3. **The exact analysis MOSAIC RESCUE wants has already been done at population scale, and it needed ~46,000 biopsies.** McCoy et al. inferred selection against complex mitotic aneuploidy by comparing day-3 vs day-5 stages — i.e. **by using two timepoints**, not by comparing one sample to a theoretical null. That is the precedent, and it is a precedent *for needing longitudinal or paired-stage contrast.*
4. **ALFA-K cannot rescue the ghost region.** Beck, Li & Andor 2025 (Nat Commun 17:1015, PMID 41455703, DOI 10.1038/s41467-025-67750-0) require longitudinal single-cell CNV; landscapes with ≥4 training passages achieved a median cross-validation score of only 0.48; they assume the per-chromosome missegregation rate *p* is "constant and known (or estimated)"; and they state that because evolving populations concentrate in high-fitness regions, "our estimates for the fitness impacts of deleterious CNAs are likely biased upwards and should be interpreted with caution." Forecast advantage over a static baseline decayed over 15–25 days and beat baseline in only **36%** of next-passage cases (vs 56% for biological replicates).
5. **Detection sensitivity is chromosome-specific in the worst possible way.** Interphase FISH systematically *over*-reports aneuploidy while low-coverage single-cell WGS *under*-reports it, on the same cells (Andriani et al. 2019, Sci Rep 9:10508, DOI 10.1038/s41598-019-46606-w): 1-probe FISH gave 2.3±0.7% aneuploidy in mouse adult brain vs 0.9±0.6% with a 2-probe design (p=0.0073), and scL-WGS called 2/9 known trisomy-18 fibroblasts as diploid (~22% false negative). Expression-based single-cell CNV callers need genes to see a chromosome (CopyKAT requires ≥5 expressed genes per chromosome). Gene-poor chromosomes — 13, 18, 21, Y — are simultaneously **the most viable as constitutional trisomies** and **the hardest to call**. A naive ghost analysis on scRNA-derived CNV would therefore produce a chromosome-length/gene-density artifact and mistake it for biology.
6. **The strongest human precedent found its signal in positive space, not negative space.** Villarroya-Beltri et al. 2022 (Sci Adv 8:eabq5914, PMID 36322655) profiled **33,604 PBMCs** by scRNA-seq plus 23 cells by shallow WGS in a MAD1L1-null MVA patient with 30–40% aneuploid blood cells. They found chr21 most frequent, with recurrent chr12 and chr18 gains (10.3% and 9.7% of all aberrations), and — decisively — **chr18 gains concentrated in γδ T cells and chr12 gains in intermediate B cells** (67.9% of intermediate B cells aneuploid). They reported **no expected-vs-observed null model**. The discovery was a *chromosome x cell-type interaction*, which is exactly the identifiable contrast (see below), and it needed ~33k cells.
7. **Whatever "ghost" you find is probably already predicted a priori.** Davoli et al. 2013 (Cell 155:948, PMID 24183448) showed that the cumulative density of tumour suppressors, oncogenes and essential genes on a chromosome predicts aneuploidy patterns across 8,200 tumours. If your depleted chromosomes turn out to be the gene-dense, essential-gene-rich ones, you have rediscovered cumulative haploinsufficiency — a 2013 result — using an N-of-1. Novelty must be argued against this baseline, not against a uniform null.
8. **Fitness is a seascape, not a landscape.** Sunshine et al. 2015 (PLoS Biol 13:e1002155, PMID 26011532; >1,800 yeast telomeric-amplicon strains) found aneuploid fitness effects to be predominantly **condition-specific**. Ya, Deng & Godek 2025 (Stem Cell Reports 20:102506, PMID 40409259) showed that uniformly aneuploid hPSC populations proliferate fine, and elimination happens only in **mosaic** populations via MYC/p53-driven cell competition — "regardless of specific chromosome imbalances," and the direction *reverses* when relative MYC/p53 flip. In other words, in the system most similar to a mosaic patient, the competition term `c_k` dominated and was largely chromosome-agnostic. That is a direct hit on the premise that per-chromosome depletion encodes per-chromosome intrinsic fitness.
9. **Standard clinical karyotyping is nowhere near powered, and adds its own selection.** MVA diagnosis rests on scoring on the order of 25–100 metaphases. My power analysis (below) says you need ~295 aneuploid cells just to call a *completely absent* state significant after multiple-testing correction. Worse, PHA-stimulated lymphocyte culture only yields metaphases from cells that *divide*, so metaphase-based ghosts are partly an in-vitro proliferation filter — real selection, but selection that happened in the incubator, not in the child.
10. **Baseline aneuploidy in normal tissue is low, which helps.** Knouse et al. 2014 (PNAS 111:13409, PMID 25197050) found ~1% aneuploidy in brain and no enrichment over skin by single-cell sequencing, overturning FISH-based claims. Low background means the MVA signal (>25% of cells by diagnostic definition) is genuinely above noise — the problem is resolution *between* states, not detecting aneuploidy at all.

---

## The one reframing that survives

**The identifiable quantity is not the ghost. It is the chromosome x tissue (or x cell-type) interaction.**

For state *k* in tissue *t*:

```
E[obs_kt] = g_k(t) * s_k(t) * c_k(t) * d_k(assay)
```

The mitotic-error machinery is broken *constitutionally and identically* in every tissue of an MVA patient, and detection sensitivity `d_k` is a property of the assay and of chromosome *k* (gene density, mappability, probe design) — **not of the tissue**. So take a log-ratio across two tissues:

```
log( obs_kt1 / obs_kt2 ) = log( g_k(t1)/g_k(t2) ) + log( s_k c_k |t1 / s_k c_k |t2 ) + log( d_k / d_k )
                                                                                        ^^^^^^^^^^ cancels
```

If `g_k` is tissue-invariant (assumption A1, testable — see falsification), the generation term cancels too, and what remains is a **difference-in-differences estimate of tissue-differential selection on chromosome k**. Chromosome-specific detection bias — the confounder I consider most likely to sink a naive analysis — is removed *by construction*, not by modelling.

This is not a rhetorical repair. It is the structure of the only human MVA finding that has actually held up (chr18/γδ-T and chr12/B-cell in MAD1L1), and it converts an unidentifiable absolute claim into an identifiable relative one. The cost: it can no longer say "this state is lethal." It can only say "this state is differentially disfavoured in tissue A relative to tissue B." That is a smaller claim and a true one.

**Corollary the project should adopt as policy:** never report a ghost as an absolute depletion. Report it as a contrast — across tissues, across cell types, or across timepoints. Absolute ghosts are decorative; contrasts are evidence.

---

## Power analysis (concrete numbers)

Setup: 22 autosomes x {gain, loss} = **K = 44** single-chromosome states. Uniform generation null p0 = 1/44 = 0.0227 among aneuploid cells. One-sided tests, Bonferroni across 44 states (alpha = 1.14e-3), 80% power, normal approximation for proportions. `n` = number of **aneuploid cells with a confident whole-chromosome call**. Total cells profiled assumes an aneuploid fraction of 30% (MVA diagnostic threshold is >25%) and, in the last column, a pessimistic 10%.

**Complete absence (0 observed).** Exact one-sided p = (1-p0)^n.

| criterion | aneuploid cells needed | total cells @30% | @10% |
|---|---:|---:|---:|
| uncorrected alpha=0.05 | 131 | 437 | 1,310 |
| Bonferroni across 44 states | **295** | **983** | **2,950** |

**Partial depletion, 80% power, Bonferroni:**

| depletion | aneuploid cells | total cells @30% | total cells @10% |
|---|---:|---:|---:|
| 1.25x | 15,577 | 51,923 | 155,768 |
| 1.5x | 5,419 | 18,062 | 54,187 |
| 2x | **2,292** | **7,641** | 22,923 |
| 3x | 1,214 | 4,045 | 12,136 |
| 5x | 791 | 2,638 | 7,913 |
| 10x | 585 | 1,952 | 5,855 |

**Combinatorial (two-chromosome) ghosts are dead on arrival.** K2 = C(44,2) = 946 pairs; expected pair frequency under independence = 5.17e-4. You need 9,680 aneuploid cells just for an *expected count of 5* per pair, and **19,061 aneuploid cells** to declare a completely absent pair significant after Bonferroni. At 30% aneuploidy that is ~64,000 cells for the weakest possible statement about a single pair. Restrict Ghost Karyotypes to single-chromosome states. (This is also empirically fine: 77.8% of aneuploid cells in the MAD1L1 patient carried a single event.)

**The number that actually matters.** All of the above assumes p0 is *known exactly*. It is not. Worrall 2018 shows ~5-fold, mechanism-dependent per-chromosome generation bias in human cells. **Therefore depletions below roughly 5-fold are not separable from generation-model error at any N.** Cross-referencing the table: 5-fold depletion needs ~791 aneuploid cells (~2,600 profiled). So:

> **Minimum viable design: ~2,500–3,000 cells with confident whole-chromosome calls, and only near-complete or >5-fold depletions may be reported — and only if the generation model is measured in this patient rather than assumed.** Below that, Ghost Karyotypes is a figure, not a result.

For calibration: standard clinical MVA karyotyping (25–100 metaphases) delivers **under 20%** of the cells required for the weakest claim in the table. The MAD1L1 study's 33,604 PBMCs is in the right range — and note that even there the authors made no depletion claim.

---

## Primary evidence

| Claim | Source | Model / population | Evidence type | Level | Notes |
|---|---|---|---|---|---|
| Chromosome missegregation in human cells is non-random and the bias is mechanism-dependent (chr1/2 ~5x enriched under spindle disruption; inverted under reversine) | Worrall et al., Cell Rep 2018;23:3366. PMID 29898405, DOI 10.1016/j.celrep.2018.05.047 | Human cell line (RPE1, BJ, HUVEC, FNE1) | Peer-reviewed, experimental | L3 | **Oppose** a uniform generation null. 268–481 lagging chromosomes/chr; mean±SD, ≥3 experiments. Chr 4,5,13,14,19,21,22 not assayable by their FISH panel |
| Mitotic-origin aneuploidy rate per chromosome correlates with chromosome length (r=0.734, P=1.0e-4); meiotic errors concentrate on chr15/16/21/22 | McCoy et al., PLoS Genet 2015;11:e1005601. PMID 26491874, DOI 10.1371/journal.pgen.1005601 | Human, 28,052 blastomeres + 18,387 TE biopsies | Peer-reviewed, observational | L2 | **Supports** a length-scaled generation prior. IVF-population-specific by authors' own caveat |
| Selection against complex mitotic aneuploidy is demonstrable — but was shown by day-3 vs day-5 *contrast*, not against a theoretical null | same | same | Peer-reviewed | L2 | **Supports** the reframing: contrast, not absolute expectation |
| ALFA-K requires longitudinal single-cell CNV; cannot be applied to a static sample; deleterious-CNA fitness estimates "likely biased upwards" | Beck, Li & Andor, Nat Commun 2025;17:1015. PMID 41455703, DOI 10.1038/s41467-025-67750-0 | Computational; breast cancer lines + 4 PDX series | Peer-reviewed, computational | L2 | **Opposes** patient-specific forecasting. Median CV 0.48 at ≥4 passages; beat static baseline in 36% of next-passage cases |
| CNA rates and selection coefficients are non-identifiable from copy-number data without a dedicated inference framework | Xiang, Liu & Dinh, Sci Rep 2024;14:17699. PMID 39085295, DOI 10.1038/s41598-024-67842-9 | Computational (CINner + ABC), cancer cohorts | Peer-reviewed, computational | L2 | **Opposes** the literal hypothesis. Needs *both* bulk and single-cell cohorts; phylogeny-tip statistics unusable at chromosome level due to low event counts |
| Selection suppresses observed karyotype variance, so observed diversity underestimates missegregation rate | Lynch et al., eLife 2022;11:e69799. PMID 35380536, DOI 10.7554/eLife.69799 | Computational agent-based + human cancer cells | Peer-reviewed | L2 | **Opposes** naive inversion of observed frequencies. ~200 cells from one site for ≥90% accuracy on the *rate*; 300 cells in simulation benchmarks |
| Interphase FISH over-reports and low-coverage scWGS under-reports aneuploidy on the same cells | Andriani et al., Sci Rep 2019;9:10508. DOI 10.1038/s41598-019-46606-w | Human/mouse cells, mock aneuploid controls | Peer-reviewed, methodological | L3 | **Opposes** treating "not observed" as "not present." 1-probe 2.3±0.7% vs 2-probe 0.9±0.6%; scWGS called 2/9 T18 cells diploid |
| Aneuploidy is rare (~1%) in normal mammalian brain/liver/skin by single-cell sequencing | Knouse et al., PNAS 2014;111:13409. PMID 25197050, DOI 10.1073/pnas.1415287111 | Mouse + human tissue | Peer-reviewed | L3 | **Supports** low background; MVA signal is above noise |
| Chromosome-arm gene content (cumulative haploinsufficiency/triplosensitivity) predicts aneuploidy patterns across 8,200 tumours | Davoli et al., Cell 2013;155:948. PMID 24183448, DOI 10.1016/j.cell.2013.10.011 | Human tumours, computational | Peer-reviewed | L2 | **Neutral/threatening**: provides the a-priori baseline any ghost result must beat |
| Aneuploid fitness effects are predominantly condition-dependent (seascape) | Sunshine et al., PLoS Biol 2015;13:e1002155. PMID 26011532 | Yeast, >1,800 strains | Peer-reviewed, functional | L3 (non-human) | **Opposes** a single static fitness value per karyotype |
| Uniformly aneuploid hPSCs proliferate; elimination requires a *mosaic* context and is MYC/p53-driven, "regardless of specific chromosome imbalances" | Ya, Deng & Godek, Stem Cell Reports 2025;20:102506. PMID 40409259, DOI 10.1016/j.stemcr.2025.102506 | Human pluripotent stem cells | Peer-reviewed, functional | L3 | **Opposes** per-chromosome intrinsic-fitness interpretation; supports the `c_k` (competition) term dominating |
| In a human MVA patient (MAD1L1-null), aneuploidy is chromosome- and cell-type-structured: chr18 gains in γδ T cells, chr12 gains in intermediate B cells | Villarroya-Beltri et al., Sci Adv 2022;8:eabq5914. PMID 36322655, DOI 10.1126/sciadv.abq5914 | Human, N-of-1, 33,604 PBMCs scRNA-seq | Peer-reviewed, observational | L2 | **Supports** the interaction reframing. No expected-vs-observed null model was performed |
| Whole-chromosome aneuploidy is inferable from scRNA-seq at 1% FDR; aneuploid cells downregulate proliferation/metabolism genes | Starostik, Sosina & McCoy, Genome Res 2020;30:814. PMID 32641298, DOI 10.1101/gr.262774.120 | Human, 74 embryos, single-cell RNA | Peer-reviewed, computational | L2 | Dual-edged: enables the assay **and** creates an expression-based detection confound |
| MVA lymphocyte aneuploidies involve "all chromosome pairs"; trisomies 42%, monosomies 28% | García-Castillo et al., Am J Med Genet A 2008;146A:1687. PMID 18548531 | Human, MVA patients | Peer-reviewed, clinical | L1 | **Opposes**: if every chromosome is observed, there are no single-chromosome ghosts — only depletions |
| Trisomy 16 is the most common trisomy in conceptions/spontaneous abortion (~18% of trisomies) and is never liveborn | Multiple cytogenetic surveys of products of conception (e.g. Soler et al. 2017, PMID 29236098 domain; reviewed in trisomy-16 literature) | Human, population-scale | Peer-reviewed, observational | L5 | **Supports** the *principle* of negative-space inference — but it took ~10^5 conceptions and a known meiotic generation model |
| Aneuploidy-tolerance can be acquired (BRG1 loss) allowing chromosome gains and fitness recovery | Nat Commun 2022;13:1731. PMID 35365638 | Human cell lines | Peer-reviewed, functional | L3 | **Opposes** fixed per-chromosome fitness; tolerance is a modifiable trait |
| Aneuploidy fitness effects are context-dependent in cancer | Ben-David & Amon, Nat Rev Genet 2020;21:44. PMID 31548659 | Review, human/cancer | Peer-reviewed review | L2 (orientation only) | Used for orientation, not as primary evidence |

Source typing: Worrall, Andriani, Knouse, Ya/Godek, BRG1 = **cell line / human primary cells**. McCoy, Starostik, Villarroya-Beltri, García-Castillo, trisomy-16 surveys = **human**. Sunshine = **yeast**. ALFA-K, CINner, Lynch = **computational**. All peer-reviewed; no preprint is relied on for a load-bearing claim (the ALFA-K bioRxiv v3, DOI 10.1101/2023.07.14.549079, PMID 40667108, is the preprint of the published paper and is cited only as an open-access route to methods detail).

---

## Contradictory evidence

| Claim challenged | Source | Why it matters |
|---|---|---|
| "Generation probability is roughly uniform across chromosomes, so deviations are selection" | Worrall 2018 (PMID 29898405) | Generation is non-uniform *and* the direction of non-uniformity changes with mechanism. Kills the uniform null outright |
| "Depletion reflects intrinsic per-chromosome fitness" | Ya/Godek 2025 (PMID 40409259) | In mosaic human stem cells, elimination was MYC/p53 competition-driven and chromosome-agnostic. The `c_k` term, not `s_k`, may carry the signal |
| "A karyotype has a fitness value" | Sunshine 2015 (PMID 26011532) | Fitness effects are condition-specific — a seascape. A single number per state is a modelling choice, not a biological fact |
| "We can infer selection coefficients from copy-number frequencies" | Xiang/Dinh 2024 (PMID 39085295) | Explicitly frames rate-vs-selection as an untangling problem requiring ABC over bulk **and** single-cell cohorts |
| "Not observed = not present" | Andriani 2019 (DOI 10.1038/s41598-019-46606-w) | scWGS called 22% of known trisomic cells diploid. Detection failure and biological absence are empirically confusable |
| "ALFA-K can give us the fitness of the missing states" | Beck 2025 (PMID 41455703) | The authors state deleterious-CNA fitness estimates are biased upwards because evolving populations concentrate in high-fitness regions. ALFA-K is blind in the ghost region |
| "This finding would be novel" | Davoli 2013 (PMID 24183448) | Chromosome gene content already predicts aneuploidy patterns. A ghost pattern matching gene density is a 2013 result rediscovered at N=1 |
| "There are ghosts to find at all" | García-Castillo 2008 (PMID 18548531) | MVA lymphocytes show aneuploidy across all chromosome pairs. There may be no absent single-chromosome states, only depleted ones — which need the 2,300–5,400-cell regime, not the 295-cell regime |
| "Clinical karyotype data can serve as the substrate" | Methodological (PHA-stimulated culture) | Metaphase analysis only sees cells that divide under mitogen. Apparent depletion is partly an in-vitro proliferation filter, i.e. selection in the incubator rather than in the child |

---

## What is directly supported vs inferred

### Directly supported
- Aneuploidy imposes a fitness cost in most human cellular contexts (L3–L4, replicated).
- Chromosome-specific missegregation bias exists in human cells and is mechanism-dependent (L3).
- Mitotic aneuploidy rate scales with chromosome length in human cleavage-stage embryos (L2).
- Selection against aneuploid states is demonstrable in humans **when two developmental stages are contrasted** (L2).
- ALFA-K requires longitudinal single-cell CNV and is unreliable in the deleterious region (L2, author-stated).
- Rate and selection are non-identifiable from copy-number frequencies without additional structure (L2, author-stated).
- Detection sensitivity for whole-chromosome calls differs by assay and by chromosome (L3).
- In one human MVA patient, aneuploidy is structured by chromosome **and** cell type (L2, N-of-1).

### Inferred (mine, flagged as such)
- That `d_k` cancels in a cross-tissue log-ratio. Follows from `d_k` being an assay+chromosome property. **Assumption A2**: the same assay, depth and calling pipeline are used for both tissues. Violated if tissues are profiled by different modalities.
- That `g_k` is approximately tissue-invariant in a constitutional checkpoint disease. **Assumption A1**, plausible (the lesion is germline and present in every cell) but *not demonstrated*, and threatened by tissue differences in cell-cycle length, proliferative index and checkpoint stringency. This is the weakest link in my reframing and I am flagging it rather than hiding it.
- The ~5-fold identifiability floor. Derived from the magnitude of published generation-bias estimates, not measured in MVA.
- The power table. Standard binomial/normal-approximation statistics under a stated uniform null; the numbers are exact given the assumptions, and the assumptions are the soft part.

---

## Required hackathon data

Stated as a hard gate, per `CONTRIBUTING_RESEARCH.md`:

| Modality | Ghost Karyotypes testable? | Notes |
|---|---|---|
| VCF only | **No** | No cell-level state frequencies exist. Hypothesis 2 does not activate |
| Bulk WGS / BAM–CRAM | **No, for ghosts** | Mosaic CNV detection from WGS reaches roughly 1–2% cell fraction for large events (BAF + coverage, MoChA-class methods), better than SNP arrays (~2–5% floor, clean detection ~10–20%). That yields a handful of detected mCAs with cell fractions — **not 44 state frequencies with counts**. It supports a "mosaic fingerprint" descriptive figure and nothing inferential about absence |
| Bulk RNA-seq | **No** | Cannot resolve per-cell states |
| Clinical karyotype (25–100 metaphases) | **No** | <20% of the cells needed for the weakest claim; plus in-vitro proliferation selection |
| scRNA-seq, one tissue | **Weakly** | ~10^4 cells is the right order of magnitude, but expression-based CNV calling has gene-density-correlated sensitivity, which is confounded with the biology. Would need per-chromosome sensitivity calibration on a euploid control run through the identical pipeline |
| **scRNA-seq or scDNA-seq with ≥2 tissues or ≥2 well-separated cell types, ≥2,500–3,000 confidently-called cells** | **Yes — the reframed interaction test** | This is the minimum viable modality |
| Longitudinal single-cell CNV (≥4 timepoints) | **Yes, incl. Hypothesis 3 / ALFA-K** | Not plausibly available for this child |

**If the gated dataset turns out to be WGS/VCF plus clinical phenotype, Hypothesis 2 must be demoted from "scientific core" to "external-data methods demonstration" before the deliverable is written.** Per `research/open_questions.md` Q12–Q15, that inventory has not been done. Issue #1 gates this entire stream.

---

## Proposed analysis (exact)

**Stage 0 — Formal definition.** A **Ghost Karyotype** is a state *k* whose observed count in a sample of *n* confidently-called aneuploid cells is significantly below its expectation under an explicit, *pre-registered* generation model G, after correction over the 44-state family, **and** after the state has been shown to be detectable by that assay. Formally: reject H0: `obs_k ~ Binomial(n, pi_k^G)` in the lower tail at Bonferroni-corrected alpha, with a detectability certificate for *k*. States failing the detectability certificate are reported as **undetermined**, never as ghosts.

**Stage 1 — Detectability certificate (do this before any biology).** Build per-chromosome sensitivity by in-silico spike-in: take euploid reference cells profiled by the identical pipeline, simulate whole-chromosome gains/losses at the observed depth, and record recall per chromosome per direction. Output: a 44-vector `d_k`. Any chromosome with recall below a pre-set threshold (I suggest 0.7) is excluded from the ghost family and reported as undetermined. **Expected outcome, stated in advance so it cannot be spun later: recall will correlate with gene count/mappability, and chr13/18/21/Y will be worst.**

**Stage 2 — Explicit null model G, pre-registered before looking at counts.** Fit and report *three* nulls, never one:
- G0: uniform over 44 states (deliberately naive; report to show how much it inflates ghosts).
- G1: proportional to chromosome length (McCoy 2015 mitotic prior, PMID 26491874).
- G2: G1 reweighted by published chromosome-specific missegregation bias (Worrall 2018, PMID 29898405), with the reversine-vs-nocodazole discrepancy propagated as a 5-fold uncertainty band.
A state is a ghost only if it is a ghost under **all three**. Anything that is a ghost only under G0 is an artifact of the null.

**Stage 3 — The identifiable test (primary analysis).** Per state *k*, fit a Poisson/negative-binomial GLM across tissues or cell types with offsets:

```
log E[count_kt] = log(N_t) + alpha_k + beta_t + gamma_kt
```

`alpha_k` absorbs generation-plus-detection (shared across tissues); `beta_t` absorbs tissue depth/composition; **`gamma_kt` is the estimand** — chromosome-by-tissue differential selection. Test `gamma_kt = 0` with FDR control over the 44 x T family. Report effect sizes with CIs, not just p-values. Overdispersion is expected (clonal expansion violates independence — see Alternative explanations) and must be modelled, not ignored; use a negative binomial and, if clone labels are available, cluster standard errors by clone.

**Stage 4 — Novelty gate against Davoli.** Regress the fitted `alpha_k`/depletion scores on (i) chromosome length, (ii) number of protein-coding genes, (iii) a Davoli-style cumulative haploinsufficiency/triplosensitivity score. **Report the residual.** If R² against these covariates is high, say so plainly: the pattern is predicted by 2013 gene-dosage theory and the N-of-1 adds nothing. Only the residual is a candidate discovery.

**Stage 5 — Fitness landscape, honestly scoped.** Do **not** run ALFA-K on patient data. Instead run it on public longitudinal scDNA-seq (the Salehi-type DLP+ passaging series ALFA-K was validated on) as an **external-data demonstration**, and publish the power/CV curve as a function of passages and cells. Label the figure "method demonstration on external data — not a patient forecast." This satisfies the brief's prohibition and is still a real deliverable.

**Stage 6 — Negative control that must be run.** Permute chromosome labels within cells and re-run the full pipeline. The ghost count under permutation is the empirical false-discovery floor. If the real analysis does not clear it by a wide margin, the result is reported as null.

---

## Expected scientific visualization

**Primary figure — "Ghost plot with an honest null band."** X axis: 22 autosomes ordered by length. Two facing panels (gains up, losses down). For each state: observed proportion as a point with exact binomial CI; the G1/G2 expected proportion as a shaded band whose width is the *propagated generation-model uncertainty* (the 5-fold Worrall band), not a hairline. Points are greyed out and hatched where the Stage-1 detectability certificate failed. Depletion is only claimed where the observed CI falls entirely below the null band. A cytogeneticist reads this in five seconds and immediately sees how few states clear the bar — which is the point.

**Companion panel — the estimand.** Heatmap of `gamma_kt` (chromosome x tissue/cell type), diverging colour, stippled where FDR > 0.05. This is where the MAD1L1-style chr18-in-γδ-T signal would appear if it exists.

**Companion panel — power curve.** Detectable fold-depletion vs number of confidently-called aneuploid cells, with a vertical line at the N actually obtained and a horizontal line at the 5-fold identifiability floor. This one figure pre-empts the strongest objection a reviewer can raise, by raising it first.

**How each could mislead:** the ghost plot invites reading a grey/hatched (undetermined) state as a ghost — hatching must be legended explicitly; the heatmap invites causal reading of a compositional artifact; the power curve invites the inference that reaching N solves the problem, when the identifiability floor does not move with N. State all three in the caption.

---

## Alternative explanations (ranked by how likely they are to be the real answer)

1. **Chromosome-specific detection sensitivity**, correlated with gene density and mappability, in expression- or low-coverage-based CNV calling. Most likely artifact. Addressed only by Stage 1.
2. **Non-uniform generation.** Worrall 2018 documents ~5-fold, mechanism-dependent bias. The MVA patient's own lesion (BUB1B vs CEP57 vs TRIP13 vs MAD1L1) probably sets a *different* bias than any published cell-line experiment, and none has been measured in MVA.
3. **Cell competition rather than intrinsic fitness.** Ya/Godek 2025: elimination in mosaic human cells was MYC/p53-driven and largely chromosome-agnostic. Depletion may encode relative neighbour context, not chromosome identity.
4. **Sampling / tissue composition.** Blood is a composite of lineages with wildly different clonal expansion histories. A ghost in PBMCs may be a ghost in one lineage that happens to dominate the sample.
5. **In-vitro selection.** Metaphase-based data only sample cells that divide under mitogen; short-term culture before sequencing does the same more subtly.
6. **Developmental timing and lineage bottlenecks.** States generated early and lost to drift through a narrow founder bottleneck are indistinguishable from states selected against, in a static sample.
7. **Clonal non-independence.** One expanded clone contributes hundreds of correlated cells. Treating cells as independent Bernoulli draws inflates significance in both directions; the effective sample size can be an order of magnitude below the cell count.
8. **Trisomy/monosomy rescue and reciprocal-product loss.** A missegregation produces a gain in one daughter and a loss in the other; if one daughter dies, the surviving state's frequency reflects the *pair's* fate, not its own.
9. **Genuine chromosome-specific selection.** The hypothesis. It is ranked ninth deliberately — it is the explanation of last resort, admissible only after 1–8 are excluded.

---

## Falsification test

**Ghost Karyotypes (reframed) is falsified if any of the following holds:**

- **F1 (identifiability).** The Stage-1 detectability certificate shows that per-chromosome recall correlates with chromosome gene count at |r| > 0.5, **and** the ghost set does not survive restriction to well-detected chromosomes. Then the ghosts are a detection artifact.
- **F2 (null dominance).** Ghosts called under G0 do not survive G1 and G2 with the 5-fold uncertainty band. Then the ghosts are a null-model artifact.
- **F3 (no estimand).** No `gamma_kt` interaction is significant at FDR 0.05 across tissues/cell types. Then there is no identifiable selection signal, only an unidentifiable absolute one, and the hypothesis is decorative.
- **F4 (no novelty).** Depletion scores are explained (R² > 0.7) by chromosome length + gene count + Davoli-style dosage score. Then the result is a 2013 finding rediscovered at N=1 and must not be presented as discovery.
- **F5 (permutation floor).** Label-permuted data yield a comparable number of "ghosts."
- **F6 (power).** Fewer than ~800 confidently-called aneuploid cells are available and no state shows complete absence. Then the study is underpowered for anything above the identifiability floor and the correct output is "not testable with these data."

**ALFA-K / Hypothesis 3 is already falsified for patient-specific use** by the data gate: the required modality (≥4 longitudinal single-cell CNV timepoints) will not exist for this child. No experiment is needed; the design is inapplicable. Presenting it otherwise would violate `docs/claims_we_cannot_make.md`.

## What result would make us abandon this idea?

Any of F1–F6. The most likely killer in practice is **F6 followed by F1**: the dataset turns out to be bulk WGS/VCF, in which case there is no cell-level state distribution at all and Hypothesis 2 never activates. The second most likely is F4 — the pattern is real but already predicted by chromosome gene content.

---

## Transferability beyond MVA

The **reframed interaction test** transfers cleanly and is arguably more valuable than the MVA application:

- **Other constitutional mosaic aneuploidy syndromes** (CEP57, TRIP13, MAD1L1, MAD2L1BP, CEP192, SMC5-related near-tetraploid MVA) — same design, and pooling patients across genes gives the N that a single child cannot.
- **Mosaic trisomy syndromes and confined placental mosaicism** — direct, and here the multi-tissue contrast is the standard clinical observation already.
- **Clonal haematopoiesis / mosaic chromosomal alterations in blood** — same estimand at population scale, where N is enormous and the tissue contrast is available.
- **Any disease with a within-patient state distribution and a plausible generation model** — mosaic single-nucleotide variants, TCR/BCR repertoires, somatic reversion. The general lesson is the same: absolute negative space is unidentifiable; contrasts are identifiable.

The **literal** version (single sample, absolute depletion) transfers nowhere, because it does not work anywhere.

---

## "How did you notice that?" factor

**Score: 4 / 5.**

Not 5, because the underlying statistics is textbook — a contrast that cancels nuisance parameters is the oldest trick in the book, and the non-identifiability of rate-vs-selection is stated outright in Xiang/Dinh 2024. Anyone who read that paper would reach the same place.

Not 2 or 3, because of two specific observations that I have not seen made in the MVA literature and that a competing team is unlikely to make:

1. **The chromosomes that are most tolerated as constitutional trisomies (13, 18, 21) are the same gene-poor chromosomes that expression-based single-cell CNV callers detect worst.** Biology and detection artifact point the same direction on the same chromosomes. A team that runs inferCNV/CopyKAT and plots observed-vs-expected will get a clean, publishable-looking, and completely confounded figure. Noticing that the confounder is *aligned* with the hypothesis rather than orthogonal to it is the non-obvious part.
2. **The generation model's own error bar (~5-fold, and sign-flipping with mechanism) sets a floor on the detectable effect size that no increase in N can lower.** Every team that does a power analysis will compute the N column. Almost none will notice that the N column is irrelevant below 5-fold.

The corollary — that the strongest published human MVA result (MAD1L1) found its signal as a chromosome x cell-type interaction and reported no null model at all — is the empirical confirmation that the interaction, not the ghost, is where the biology is.

---

## Recommended next action

1. **Block on Issue #1.** Do not build notebook `04_ghost_karyotypes.ipynb` before the dataset inventory. If there is no cell-resolved modality, close this stream as "not testable with available data" and say so in the deliverable — per `AGENTS.md`, a well-supported rejection is the win condition.
2. **Rewrite the hypothesis statement** in `README.md` and `hypotheses/` from "missing states are informative" to "**chromosome x tissue differential representation is informative; absolute absence is not.**"
3. **Add the identifiability floor to `docs/claims_we_cannot_make.md`**: *"We cannot claim depletion below ~5-fold, because that is smaller than the published uncertainty in chromosome-specific generation probability."*
4. **Populate `research/contradictions.md`** with C002–C007 from the contradictory-evidence table above (currently only the empty C001 template row exists).
5. **Populate `research/evidence_registry.md`** with E002–E018 from the primary-evidence table (currently only the empty E001 template row exists).
6. Build Stage 1 (detectability certificate) and Stage 6 (permutation control) **first**, before any biological analysis. If those two are in the notebook, the analysis is honest whatever it finds.

### Next Best Experiment (the one that reduces uncertainty most)

**Measure `g_k` in this patient's own cells.** Short-term culture of patient fibroblasts or PHA-stimulated lymphocytes, arrest-release, then **chromosome-specific paint or centromeric FISH on anaphase/micronuclei** to count missegregation events per chromosome at a timepoint early enough that selection has not yet acted (the Worrall 2018 design, applied to MVA rather than to drug-induced CIN). Pair it with scDNA-seq at t=0 and t=short to get a two-timepoint contrast.

This is the highest-information experiment because it converts the largest unknown — the generation prior, currently a 5-fold band borrowed from a drug-treated cell line — into a measured, patient-specific quantity. Every other uncertainty in this hypothesis is downstream of it. Nothing else in the Ghost Karyotype pipeline is worth doing until `g_k` is measured or the hypothesis is reframed as a contrast that does not need it.

Second choice, if only computational work is possible: run Stages 1, 2, 5 and 6 on the public 74-embryo single-cell dataset (Starostik/McCoy 2020) as a **fully external methods demonstration with a published power curve**. It is honest, it is reproducible, it requires no gated data, and it demonstrates the exact capability without a single unsupportable patient claim.

---

## Repository infrastructure gaps found (beyond those in the brief)

Confirming and extending the brief's "verified absent" list:

- `research/evidence_registry.md` and `research/contradictions.md` still hold only the empty E001/C001 template rows. Nine research streams have open Issues and zero registry entries; the evidence system exists on paper only.
- `docs/agent_prompts.md` Prompt D (Ghost Karyotypes) and Prompt H (forecasting/ALFA-K) are **two separate prompts**, but Hypothesis 3 is a hard *dependency* of Hypothesis 2, not a parallel stream. Issue #3 covers both; Issue #7 also claims ALFA-K. That overlap should be resolved before two agents write contradictory ALFA-K assessments.
- There is no `notebooks/04_ghost_karyotypes.ipynb` or `05_fitness_landscape.ipynb`; `notebooks/` contains only `00_data_inventory.ipynb`. The README's 16-notebook sequence is aspirational.
- Still no `requirements.txt` / `environment.yml` / `pyproject.toml`. The analysis in this report needs `scipy`, `statsmodels` (negative-binomial GLM) and `numpy` at minimum; nothing pins them.
- `hypotheses/` contains only the template — no hypothesis document exists for H2 or H3 to promote this report into.
- Workstream G (aneuploid stress transfer: proteostasis/mPOS/cell competition) still has no Issue. Note for that stream: cell competition is not a side branch for Hypothesis 2 — Ya/Godek 2025 makes it a *competing explanation* for the entire depletion signal. G should be opened and coupled to Issue #3.

---

## References

1. Beck RJ, Li T, Andor N. ALFA-K: Local adaptive mapping of karyotype fitness landscapes. *Nat Commun* 2025;17:1015. PMID 41455703. DOI 10.1038/s41467-025-67750-0. https://pmc.ncbi.nlm.nih.gov/articles/PMC12848095/ — peer-reviewed; computational (human cancer cell lines + PDX).
2. Beck RJ, Andor N. Local Adaptive Mapping of Karyotype Fitness Landscapes. *bioRxiv* 2023/2025. PMID 40667108. DOI 10.1101/2023.07.14.549079. https://www.biorxiv.org/content/10.1101/2023.07.14.549079v3.full — **preprint** of the above; methods detail only.
3. Worrall JT, Tamura N, Mazzagatti A, et al. Non-random Mis-segregation of Human Chromosomes. *Cell Rep* 2018;23:3366–3380. PMID 29898405. DOI 10.1016/j.celrep.2018.05.047. https://pmc.ncbi.nlm.nih.gov/articles/PMC6019738/ — peer-reviewed; human cell lines (RPE1, BJ, HUVEC, FNE1).
4. McCoy RC, Demko ZP, Ryan A, et al. Evidence of Selection against Complex Mitotic-Origin Aneuploidy during Preimplantation Development. *PLoS Genet* 2015;11:e1005601. PMID 26491874. DOI 10.1371/journal.pgen.1005601. https://pmc.ncbi.nlm.nih.gov/articles/PMC4619652/ — peer-reviewed; human embryos.
5. Starostik MR, Sosina OA, McCoy RC. Single-cell analysis of human embryos reveals diverse patterns of aneuploidy and mosaicism. *Genome Res* 2020;30:814–825. PMID 32641298. DOI 10.1101/gr.262774.120 — peer-reviewed; human embryos, computational inference from scRNA-seq.
6. Xiang Z, Liu Z, Dinh KN. Inference of chromosome selection parameters and missegregation rate in cancer from DNA-sequencing data. *Sci Rep* 2024;14:17699. PMID 39085295. DOI 10.1038/s41598-024-67842-9 — peer-reviewed; computational.
7. Lynch AR, Arp NL, Zhou AS, Weaver BA, Burkard ME. Quantifying chromosomal instability from intratumoral karyotype diversity using agent-based modeling and Bayesian inference. *eLife* 2022;11:e69799. PMID 35380536. DOI 10.7554/eLife.69799. https://pmc.ncbi.nlm.nih.gov/articles/PMC9054132/ — peer-reviewed; computational + human cancer cells.
8. Andriani GA, Maggi E, Piqué D, et al. A direct comparison of interphase FISH versus low-coverage single cell sequencing to detect aneuploidy reveals respective strengths and weaknesses. *Sci Rep* 2019;9:10508. DOI 10.1038/s41598-019-46606-w. https://pmc.ncbi.nlm.nih.gov/articles/PMC6642082/ — peer-reviewed; human/mouse cells, methodological.
9. Knouse KA, Wu J, Whittaker CA, Amon A. Single cell sequencing reveals low levels of aneuploidy across mammalian tissues. *PNAS* 2014;111:13409–13414. PMID 25197050. DOI 10.1073/pnas.1415287111 — peer-reviewed; mouse + human tissue.
10. Davoli T, Xu AW, Mengwasser KE, et al. Cumulative haploinsufficiency and triplosensitivity drive aneuploidy patterns and shape the cancer genome. *Cell* 2013;155:948–962. PMID 24183448. DOI 10.1016/j.cell.2013.10.011 — peer-reviewed; human tumours, computational.
11. Sunshine AB, Payen C, Ong GT, et al. The fitness consequences of aneuploidy are driven by condition-dependent gene effects. *PLoS Biol* 2015;13:e1002155. PMID 26011532. DOI 10.1371/journal.pbio.1002155 — peer-reviewed; **yeast**.
12. Ya A, Deng C, Godek KM. Cell competition eliminates aneuploid human pluripotent stem cells. *Stem Cell Reports* 2025;20:102506. PMID 40409259. DOI 10.1016/j.stemcr.2025.102506. https://pmc.ncbi.nlm.nih.gov/articles/PMC12181964/ — peer-reviewed; human pluripotent stem cells.
13. Villarroya-Beltri C, Osorio A, Torres-Ruiz R, et al. Biallelic germline mutations in MAD1L1 induce a syndrome of aneuploidy with high tumor susceptibility. *Sci Adv* 2022;8:eabq5914. PMID 36322655. DOI 10.1126/sciadv.abq5914 — peer-reviewed; human N-of-1, 33,604 PBMCs.
14. García-Castillo H, Vásquez-Velásquez AI, Rivera H, Barros-Núñez P. Clinical and genetic heterogeneity in patients with mosaic variegated aneuploidy: delineation of clinical subtypes. *Am J Med Genet A* 2008;146A:1687–1695. PMID 18548531 — peer-reviewed; human MVA patients.
15. Malumbres M, Villarroya-Beltri C. Mosaic variegated aneuploidy in development, ageing and cancer. *Nat Rev Genet* 2024;25:864–878. PMID 39169218. DOI 10.1038/s41576-024-00762-6 — peer-reviewed **review**; orientation only.
16. Ben-David U, Amon A. Context is everything: aneuploidy in cancer. *Nat Rev Genet* 2020;21:44–62. PMID 31548659. DOI 10.1038/s41576-019-0171-x — peer-reviewed **review**; orientation only.
17. Aneuploidy tolerance caused by BRG1 loss allows chromosome gains and recovery of fitness. *Nat Commun* 2022;13:1731. PMID 35365638 — peer-reviewed; human cell lines.

### Flagged for the Workstream G agent (outside my scope, found incidentally)
- "Proteostasis failure and mitochondrial dysfunction contribute to chromosomal instability-induced microcephaly." *Nat Commun* 2026. DOI 10.1038/s41467-026-70521-0. Directly on the mPOS/proteostasis branch that currently has a prompt but no Issue.
