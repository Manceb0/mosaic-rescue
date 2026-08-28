# Synthetic Rescue for Constitutional MVA: the evidence route is real, but it is not the one cancer genomics would hand us

Agent: Agent C (Hypothesis 4 audit, Issue #4 — "Agent stream — Synthetic rescue and functional validation")
Date: 2026-08-28
Scope: **evidence route only.** No drug is nominated anywhere in this report. Drug repurposing is Track 2 / Workstream I and is explicitly out of scope here.

---

## Research question

Hypothesis 4 claims that instead of asking "what kills a diseased cell?", we should ask "what second perturbation compensates for the first defect?" — and that such compensatory mechanisms are discoverable by combining patient evidence with independent perturbation screens.

I audited three things, adversarially:

1. Is **synthetic rescue / genetic suppression** an established, quantified methodology, or a rhetorical frame?
2. Do **public perturbation resources actually contain rescue signal**, or only dependency signal that we would be re-labelling?
3. Does the frame survive the transfer from **cancer cell lines to pediatric constitutional aneuploidy**?

---

## Why this matters

Hypothesis 4 is the load-bearing joint of the whole project. It is the step that converts "we observed karyotype states in one child" (H1–H3, correlational, N-of-1) into "here is a mechanism that could be acted on" (H6–H7). If the rescue route is not real, MOSAIC RESCUE degrades into a descriptive mosaicism paper with a drug list bolted on — which is exactly the failure mode `docs/research_protocol.md` §12 forbids.

It also matters negatively: the *entire* aneuploidy functional-genomics literature is written in the opposite direction. Nearly every screen ever run on aneuploid cells asks **what kills aneuploid cells** (aneuploidy-selective antiproliferation, aneuploid-specific dependencies), because the funders are oncology. We are proposing to read that literature backwards. That inversion is either the project's best idea or its most seductive error.

---

## Bottom line

- **CONDITIONAL — with a hard structural condition.**
- **Current evidence level: L2** for the *methodology* (genetic suppression is an established, quantified, replicated experimental discipline with global-scale maps). **L1 at best, mostly L0,** for *MVA-specific rescue* (no suppressor screen has ever been run on a human MVA gene in a human cell).
- The condition: Hypothesis 4 may proceed **only as a cross-species, mechanism-level suppressor hypothesis anchored on the causal gene's own pathway**, not as a DepMap-derived candidate list. If the project tries to source rescue candidates from cancer dependency data, it will produce confident nonsense. See §"How badly cancer-to-constitutional transfer fails".
- The **single highest-value finding** is not in the synthetic-rescue literature at all. It is in the orphaned Workstream G: a 2025 human paper showing that chromosome gains cause a **mitochondrial protein-import defect with cytosolic precursor accumulation into p62 bodies**, *and* that **HSF1/HSP27/HSP90α overexpression partially rescues it — but only below a chromosome-burden threshold.** That is a dose-limited, measurable, falsifiable compensatory axis with a yeast dosage-suppressor network sitting behind it. **Workstream G should get a GitHub Issue.**

---

## 1. Executive finding — what changes for MOSAIC RESCUE

**Four things change.**

**(a) "Synthetic rescue" is a real discipline with real numbers, and the human numbers are humbling.**
The entire curated global map of human genetic suppression is **476 interactions across 484 genes**, assembled by manually reading 2,400 papers (Ünlü et al., *Genome Medicine* 2023, PMID 37821946). For comparison, the yeast suppression network is orders of magnitude larger and was built from systematic screens (van Leeuwen et al., *Science* 2016, PMID 27811238). So: the field exists, it is rigorous, and **human rescue evidence is roughly five hundred facts total.** Any claim that we will "search human suppressors" for an MVA gene is a claim about a resource that, for our genes, is empty. We should say that out loud rather than discover it in week three.

**(b) The human suppression network is mechanistically *different* from the yeast one, in a direction that is bad for naive cross-species transfer and good for the proteostasis hypothesis.**
Ünlü et al. found **33% of human suppression pairs are functionally related, vs 55% in yeast (p < 0.0005)**, while **38% of human suppression interactions act through general stress-response/signaling mechanisms, vs 19% in yeast (p < 0.0005)**. Read that carefully: in humans, suppression is *less* likely to be a tidy same-complex compensation and *more* likely to be a generic stress/signaling buffer. That is simultaneously (i) a warning that yeast pair-level suppressors will not map over, and (ii) a direct statistical argument that **the stress-response axis — proteostasis, chaperones, apoptosis regulation (48% of the "signaling & stress" suppressors involve apoptosis regulation, 60% protein phosphorylation) — is where human suppression actually lives.** Workstream G is not a side quest. It is where the base rate points.

**(c) Almost no public resource contains rescue signal. The ones that do are small, and none of them cover MVA genes.** Full inventory in §"Named datasets" below. Short version: **BioGRID's `Synthetic Rescue` / `Dosage Rescue` / `Phenotypic Suppression` evidence codes are the only structured, queryable rescue ontology in existence**, and they are overwhelmingly populated with yeast. DepMap contains **no rescue query at all** in the sense we need. Perturb-seq contains *signature-reversal* evidence, which is rescue-adjacent but not epistasis.

**(d) There is one genuine, published, mechanism-level suppressor relationship inside the MVA gene set itself, and the project has not noticed it.**
`TRIP13` causes MVA. `MAD2L1BP`/p31^comet causes mosaic aneuploidy with juvenile granulosa cell tumours (Abdel-Salam et al., *JCI Insight* 2023, PMID 37796616). TRIP13 and p31^comet are physical partners and functional antagonists in MAD2 conformational cycling — and **loss of p31^comet partially suppresses the requirement for TRIP13** in Mad2 kinetochore localisation and checkpoint signalling (Nelson et al., *J Cell Biol* 2015, PMID 26527744; *C. elegans*). Separately, in *Drosophila*, reduced `polo` dosage suppresses `bubR1` nondisjunction, cutting NDJ from ~27% to 6.6% (Sousa-Guimarães et al., *G3* 2011, PMID 22384328). So for **two of the three classic MVA genes there is a documented cross-species dosage-suppressor relationship in the correct pathway.** That is the most concrete "route exists" evidence in this report — and also, see §Safety, the most dangerous, because both suppressors point toward *weakening the mitotic checkpoint further*.

---

## 2. Established methodology and its false-positive behaviour

### What the methodology actually is

Genetic suppression has three formal experimental classes, and they are not interchangeable:

| Class | Definition | BioGRID evidence code |
|---|---|---|
| Genomic / loss-of-function suppression | A second mutation (usually LOF) rescues the query mutant's defect | `Synthetic Rescue` |
| Dosage suppression | *Over*expression of a second gene rescues the query mutant | `Dosage Rescue` |
| Phenotypic suppression | Rescue of a non-lethality phenotype | `Phenotypic Suppression` |

(van Leeuwen et al., *BioEssays* 2017, PMID 28582599; BioGRID curation guide.) For MVA the relevant class is almost certainly **dosage suppression / phenotypic suppression**, not synthetic rescue of lethality — the patient's cells are alive. This distinction matters practically: it means the useful screen design is an **ORF-overexpression / CRISPRa dosage-suppressor screen against a stress phenotype**, not a CRISPR-KO viability screen. Most public data is the latter.

### False-positive behaviour — this is worse than the field's reputation suggests

Four systematic failure modes, in decreasing order of danger for us:

1. **Adaptive passenger mutations that look like suppressors.** van Leeuwen et al. (*Science* 2016) whole-genome-sequenced their suppressor strains and found frequent secondary mutations in a specific subset of genes that **delay entry into stationary phase**, which enriches those clones during propagation regardless of any relationship to the query defect. This is a *reproducible* false positive: it will recur in every lab, it validates in a growth assay, and it is biologically meaningless for the query gene. Of their candidate interactions, **221 gave a positive result in at least one validation assay** — i.e., validation was a real filter, not a formality.
2. **Aneuploidy itself is one of the most common spontaneous suppressor mutations.** Whole-chromosome gain is a standard, rapid, reversible adaptive solution: chromosome III duplication under heat stress (Yona et al., *PNAS* 2012, DOI 10.1073/pnas.1211150109), aneuploidy driving adaptation after loss of the cytokinesis motor Myo1 (Rancati et al., *Cell* 2008, DOI 10.1016/j.cell.2008.09.039), aneuploidy generating quantitative proteome and phenotype variation (Pavelka et al., *Nature* 2010, DOI 10.1038/nature09529). **For MOSAIC RESCUE this is a double-edged sword and the team must hold both edges at once.** Edge one: it is direct precedent that karyotype change *is* a suppressor mechanism — which is the intellectual core of "the disease is running an evolutionary experiment". Edge two: it is a devastating confounder, because it means an observed karyotype in this child may be suppressing *something unrelated to the causal variant* — culture stress, tissue-specific selection, sampling — exactly the generation-vs-selection problem flagged for Ghost Karyotypes (H2), now recurring inside H4.
3. **Genetic compensation / transcriptional adaptation is a mutation-class artefact.** Alleles that produce decaying mutant mRNA trigger homology-dependent upregulation of related genes; alleles that fail to transcribe do not, and give *more severe* phenotypes (El-Brolosy et al., *Nature* 2019, PMID 30944477; zebrafish + mouse; foreshadowed by Rossi et al., *Nature* 2015, DOI 10.1038/nature14580). Consequence for us: **the same gene, knocked out two different ways, gives two different "rescue" answers.** Any suppressor inferred from a knockout model may be an artefact of the allele, not a property of the gene. This directly threatens transferring any published MVA-gene knockout result onto a patient missense/hypomorphic allele.
4. **Allele specificity.** Suppression is frequently allele-specific rather than gene-specific. MVA is a hypomorph disease (BubR1 dose; see JCI 2019 allelic series, PMID 31738183). A suppressor of a null is not evidence about a hypomorph.

**Net:** the false-positive structure of suppressor genetics is *not* random noise that replication averages away. It is composed of confounders that are reproducible, growth-validated, and mechanistically plausible. That is the worst kind. It is why the project's two-independent-route rule (§11 of the protocol) is not bureaucratic — it is the only defence that works here.

---

## 3. Named datasets and resources: what is queryable for RESCUE vs only for DEPENDENCY

This is the deliverable Issue #4 asks for. **Verdict column is the important one.**

| Resource | URL / ID | Content | Rescue-queryable? | Notes for MVA |
|---|---|---|---|---|
| **BioGRID** | thebiogrid.org | Curated genetic interactions with explicit `Synthetic Rescue`, `Dosage Rescue`, `Phenotypic Suppression` evidence codes (Oughtred et al., *Protein Sci* 2021, PMID 33070389) | **YES — the only structured rescue ontology that exists.** Directly filterable by evidence code | Overwhelmingly *S. cerevisiae*. Query BUB1B/TRIP13/CEP57/MAD2L1BP orthologs (BUB1, MAD3, PCH2, MAD2, CDC5) here first. Expect thin human returns |
| **Ünlü et al. human suppression network** | DOI 10.1186/s13073-023-01232-0 (supplementary tables) | 476 human suppression interactions, 93 query genes, 484 genes | **YES — the only human rescue dataset in existence** | 302 from cultured cells, 180 from patient studies, **only 6 overlap; 99% of interactions come from exactly one study type.** Contains an RF predictor (AUC 0.69) — usable to *predict* suppressors of an MVA gene, with honest error bars |
| **TheCellMap / yeast SGA** | thecellmap.org | Quantitative yeast GI scores incl. **positive (buffering/suppressive) interactions** | **YES** for positive GI; note positive GI ≠ curated suppression | Positive GIs are the systematic, quantitative version of rescue. Best-powered rescue resource on Earth — in yeast |
| **SGD / PomBase / FlyBase / WormBase** | yeastgenome.org etc. | Curated allele-level "suppressor of" annotations | **YES** | FlyBase suppressor annotations are how the `polo`/`bubR1` result is findable |
| **Horlbeck et al. human GI map** | PMID 30033366, DOI 10.1016/j.cell.2018.06.010 | CRISPRi double-knockdown, 222,784 gene pairs / 1,044,484 sgRNA pairs, K562 + Jurkat; classifies **buffering (positive)** as well as synergistic GIs | **YES — buffering interactions are rescue-adjacent in human cells** | Two cancer lines only. Secondary analyses report very low cross-line overlap of synthetic-lethal calls (order 5–20%); treat any single-line GI as context-specific until re-derived from primary data |
| **Norman et al. combinatorial Perturb-seq** | PMID 31395745, DOI 10.1126/science.aax4438 | CRISPRa, 105 single + 131 dual perturbations, ~91k cells, K562; explicitly classifies GI types incl. suppression/epistasis/neomorphic | **YES — true epistasis, but tiny (131 pairs) and CRISPRa-only, K562-only** | Best existing *template* for the analysis we would want to run; not a source of MVA answers |
| **Replogle et al. genome-scale Perturb-seq** | PMID 35688146, DOI 10.1016/j.cell.2022.05.013 | ~11,000-gene GWPS in K562; essential-gene libraries in K562 **and RPE1 (hTERT-immortalised, near-diploid, TP53-WT, non-cancer)** | **PARTIAL — single perturbations only.** Supports *transcriptional signature reversal* queries ("does knocking down B move cells opposite to knocking down A?"), **not epistasis** | The **RPE1 arm is the single most constitutionally-relevant human perturbation dataset available**, precisely because RPE1 is near-diploid and p53-competent. This is the resource to build on |
| **BioGRID ORCS** | orcs.thebiogrid.org | ~2,200+ curated genome-wide CRISPR screens, 825 cell lines | **PARTIAL** — includes positive-selection/resistance screens, but these are a minority (~6.7% of screens by one survey, iCSDB, *Nucleic Acids Res* 2021, DOI 10.1093/nar/gkaa989) | Positive-selection hits *are* rescue signal, but of a drug or a toxin, not of a constitutional mutation |
| **DepMap (CRISPR/Chronos, RNAi)** | depmap.org | Gene-effect scores across ~1,100 cancer lines | **NO — dependency only.** Positive Chronos scores exist but mean "KO speeds up this cancer line", which is a proliferation-suppressor statement about a transformed cell, not a rescue statement about a query defect | See §4. Actively hazardous for this project |
| **LINCS / CMap (shRNA, CRISPR xpr)** | clue.io | Knockdown/knockout transcriptional signatures | **PARTIAL — signature reversal only** | Belongs to Workstream I, not here. Do not let signature reversal masquerade as genetic rescue |
| **MaveDB / deep mutational scanning** | mavedb.org | Variant-effect maps | **NO for inter-genic rescue; YES only for intragenic second-site suppressors** where a DMS assayed double mutants (rare) | Relevant only if the causal variant is missense and an interface-level intragenic suppressor is plausible — that is Workstream F's call, not ours |
| **JUMP Cell Painting** | broad.io/jump | Morphological profiles incl. CRISPR/ORF perturbations | **PARTIAL — morphological reversal only** | Same caution as CMap |
| **IMPC, MGI** | mousephenotype.org, informatics.jax.org | Mouse phenotypes; MGI curates modifier/suppressor alleles | **PARTIAL (MGI)** | Where the BubR1/p16 and BubR1-overexpression results live |

**Summary answer to the audit question:** rescue signal exists in public data, but essentially all of it is (i) yeast, (ii) two human cancer cell lines, or (iii) 476 hand-curated human facts. **There is no public dataset that contains rescue evidence for any MVA gene in any human cell.** Anyone who claims otherwise is reading a dependency map.

---

## 4. How badly does cancer-to-constitutional transfer fail? Concretely.

The brief asks for evidence, not caution-flavoured hedging. Here it is, strongest first.

**(a) DepMap's measurement is confounded by exactly the variable MVA is made of.** Cas9 cutting produces a gene-independent, **copy-number-proportional** antiproliferative effect; amplified regions are a major source of false-positive dependencies, which is why CERES/Chronos exist at all (Meyers et al., *Nat Genet* 2017, PMID 29083409, DOI 10.1038/ng.3984). **A disease defined by variable chromosome copy number is the worst possible consumer of a dependency map whose principal artefact is copy number.** The correction is fitted across a cancer-line panel; it is not validated for cell-to-cell mosaic copy-number variation within one individual. This alone should bar DepMap from generating candidates for us.

**(b) The screening platform selects against p53, and MVA cells are p53-competent.** Cas9-induced double-strand breaks are p53-dependently toxic; editing efficiency is severely reduced in TP53-wild-type human pluripotent cells, and editing enriches p53-pathway-deficient cells (Ihry et al., *Nat Med* 2018, PMID 29892062, DOI 10.1038/s41591-018-0050-6; concordant: Haapaniemi et al., *Nat Med* 2018, DOI 10.1038/s41591-018-0049-z). DepMap's panel is overwhelmingly TP53-mutant. So the reference organism for "human genetic dependency" is a p53-crippled, already-aneuploidy-tolerant cell. **Aneuploidy tolerance is the phenotype we are trying to study, and the cancer panel has already solved it and thrown away the intermediates.** Screening for aneuploidy-tolerance suppressors in DepMap is like screening for altitude adaptation in a population that already lives at 4,000 m.

**(c) Proliferation control — and therefore chromosome-level fitness — is profoundly tissue-specific.** In systematic ORF-overexpression screens across mammary, fibroblast and pancreatic cells, ~10% of genes regulate proliferation and **most do so in a highly tissue-specific manner**; the tissue-specific density of these STOP/GO genes is what explains tissue-specific aneuploidy patterns in cancer (Sack et al., *Cell* 2018, PMID 29576454, DOI 10.1016/j.cell.2018.02.037; see also Davoli et al., *Cell* 2013, PMID 24183448). **The fitness effect of gaining or losing a given chromosome is not a property of the chromosome. It is a property of the chromosome × the tissue.** MVA is a whole-organism, multi-tissue, developmental disease. A chromosome-fitness value read off cancer data is a value for the wrong tissue at the wrong developmental stage.

**(d) Genetic interactions do not even transfer between two cancer cell lines.** Horlbeck et al. mapped the same 222,784 gene pairs in K562 and Jurkat; secondary analyses of that data report on the order of 1,523 synthetic-lethal pairs in K562, 374 in Jurkat, and ~82 shared. Whatever the precise numbers (I flag these as secondary-source and worth re-deriving from the primary supplementary tables before quoting them in a deliverable), the qualitative result is not in dispute in the field: **GI calls are strongly context-dependent even between two human leukaemia lines.** The prior that they transfer from a cancer line to a child's fibroblast is therefore low, not merely "uncertain".

**(e) The direction of clinical interest is inverted.** Every well-powered aneuploidy screen in the literature asks what *kills* aneuploid cells: aneuploid-specific dependencies on mitochondrial metabolism and nucleotide biosynthesis (aneuploidy epistasis map in isogenic diploid/aneuploid hTERT-HMECs, bioRxiv 2024 DOI 10.1101/2024.09.30.615609; peer-reviewed as *Genes Dev* 2025;39(11–12):770 on enhanced nucleotide dependency; further preprint evidence for mitochondrial metabolism and UBE2H as aneuploid-specific dependencies, bioRxiv 2026). These are excellent papers and they are **anti-rescue** data. Reading a dependency and asserting its inverse is a rescue is a logical error: a gene whose loss kills aneuploid cells is not thereby a gene whose gain saves them. There is no theorem that makes dependency maps invertible.

**Conclusion of §4: DepMap and cancer GI maps may be used in this project as *counter-evidence and safety screens only* — "does our candidate compensatory axis coincide with a cancer dependency, i.e. are we about to make unstable cells fitter?" That is a legitimate, even excellent, use. They must not be used as a candidate-generation source.** I recommend this be written into `docs/claims_we_cannot_make.md` as an operational rule, not just a caution.

---

## 5. Cross-species suppressor conservation: how well does it actually transfer?

Honest numbers, from three independent angles:

- **Negative GI networks between two yeasts:** ~23–29% conserved (Dixon et al., *PNAS* 2008, PMID 18931302; Roguev et al., *Science* 2008, PMID 18818364, DOI 10.1126/science.1162609). Between two *yeasts*. Not to humans.
- **Gene-level functional replaceability, yeast→human:** ~**47%** of 414 essential yeast genes can be replaced by their human ortholog, and replaceability is predicted by **module membership, not sequence identity** (Kachroo et al., *Science* 2015, PMID 25999509, DOI 10.1126/science.aaa0769). This is the most encouraging number available, and it is about *gene function*, not about *interaction*.
- **Suppression mechanism, yeast vs human:** qualitatively different. Human suppression is less within-pathway (33% vs 55%) and more general-stress/signaling (38% vs 19%) than yeast (Ünlü et al. 2023).

**Synthesis:** pair-level suppressor transfer from yeast to human should be assumed to fail. **Module-level and mechanism-level transfer is defensible.** The operational rule this implies — and I think it is the correct rule for the whole project — is:

> Transfer the *axis* (e.g. "cytosolic proteostasis capacity buffers mitochondrial import failure"), never the *gene pair* (e.g. "overexpress the human ortholog of GIS2").

Note that within a species, suppression is robust: suppression interactions are highly conserved across genetically diverse yeast isolates (*G3* 2025, DOI 10.1093/g3journal/jkaf047). So the fragility is phylogenetic distance, not experimental irreproducibility. That is a useful distinction: it means a suppressor validated in *human* cells would likely hold across human genetic backgrounds — the problem is getting one.

---

## 6. Aneuploidy tolerance: what is actually known

**Supporting the proteostasis frame:**
- Loss-of-function of the deubiquitinase **UBP6** improves proliferation of four different disomic yeast strains by attenuating aneuploidy-induced changes in protein composition (Torres et al., *Cell* 2010, PMID 20850176, DOI 10.1016/j.cell.2010.08.038). **This is the canonical proof that a single second mutation can be a general aneuploidy-tolerating suppressor.** It is also a *loss*-of-function suppressor of a proteasome antagonist — mechanistically, "give the proteasome more throughput".
- `SCH9`-W377C improves proliferation across many disomic strains — a second general aneuploidy adaptation, implicating nutrient/TOR signalling.
- Human primary fibroblasts with trisomy 21 and other constitutional trisomies show reduced viability, altered lipid metabolism, increased serine dependency, and ~1.5-fold mRNA/protein increases with post-transcriptional attenuation of complex subunits (*PNAS* 2021;118(6):e2014723118, DOI 10.1073/pnas.2014723118). **This is the only entry in this report that is human, primary, constitutional and aneuploid — i.e. the closest existing model to our patient.**

**Contradicting it (mandatory contradiction search):**
- **Six aneuploid yeast strains carrying 438–1,242 excess ORFs grew comparably to euploid controls, with no acquired tolerating mutations, no large-scale dosage compensation, and no chronic activation of the environmental stress response or heat shock response.** Strains with duplicated chromosome II were *more* resistant to proteotoxic drugs. Excess DNA content did not correlate with growth defect (Larrimore et al., *BMC Biol* 2020, PMID 32900371, DOI 10.1186/s12915-020-00852-x). This is a direct, well-powered contradiction of the deterministic "aneuploidy ⇒ proteotoxic stress ⇒ needs a suppressor" model. **It says tolerance is karyotype-specific, sometimes intrinsic, and sometimes requires nothing at all.**

**What this contradiction actually implies for us — and this is a genuinely useful reframing:** if tolerance is karyotype-specific rather than universal, then the *correct* question for MVA is not "what compensates for aneuploidy" but **"which karyotypes in this child needed compensation and which did not"**. That is a within-patient, state-stratified question. It is more falsifiable than the generic one, and it is the version that H1/H3 data could actually address. I recommend the project adopt the karyotype-stratified phrasing.

---

## 7. mPOS / mitochondrial import stress — the Workstream G finding

This is where the report's highest-value material is, and it is currently outside the issue tracker.

**The human anchor (2025, peer-reviewed, human cells):**
Amponsah, Bökenkamp, Kurpa et al., *Nat Commun* 2025;16:5328. PMID **40527892**, DOI 10.1038/s41467-025-60857-4. System: near-diploid **HCT116** plus isogenic microcell-transferred derivatives — trisomy 3, trisomy 5, tetrasomy 5, trisomy 13, trisomy 21.

Findings:
- Accumulation of **precursor forms** of mitochondrial proteins (HADHA, HADHB, MRPL45) in whole-cell lysates.
- **Kinetically delayed import** of su9-DHFR and SOD2 into isolated mitochondria from polysomic cells, **despite normal membrane potential** — i.e. a genuine import-capacity defect, not a bioenergetic artefact.
- p62/SQSTM1 expression **scales with chromosome-gain burden**; APEX2-p62 proximity proteomics finds **mitochondrial proteins as the dominant polysomy-specific p62 proxitome**, and they are *not* enriched in autophagosomal p62 cargo — i.e. cytosolic sequestration, not disposal.
- ROS up; mtDNA down to ~60–80%; nuclear-encoded respiratory chain proteins down >20%; complex-I-dependent respiration ~50% of parental.
- **Rescue experiment:** transient overexpression of **HSP27, HSP90α, HSF1 and constitutively active HSF1** each decreased p62-positive foci and reduced p62–TOMM20 colocalisation in the mild-burden lines (trisomy 13, trisomy 3), and decreased aggresome formation across lines — **but tetrasomy 5 showed no rescue.**

That last clause is the most scientifically valuable sentence I found in this entire audit. **The rescue is dose-limited: chaperone capacity compensates below a chromosome-burden threshold and saturates above it.** That converts a vague "proteostasis is involved" story into a **quantitative, falsifiable dose–response hypothesis** — and it maps directly onto MVA, which is *by definition* a within-patient distribution of chromosome burdens. It predicts a threshold in the patient's own data.

**The independent second route (yeast, dosage-suppressor screen):**
Wang & Chen, *Nature* 2015;524:481–484. PMID **26192197**, DOI 10.1038/nature14859. A **multicopy (dosage) suppressor screen** against mitochondrial damage (AAC2^A128P) recovered **40 suppressor genes**, 32 falling into five categories: **TOR signalling; mRNA silencing/turnover (Dcp2, Edc3); ribosome function and translation (Ssb1, Ssb2, Zuo1, Rpl40A/B, Rpl38); tRNA methylation (Trm9); cytosolic chaperoning and degradation** — plus four uncharacterised (SDD1–4). They named the phenotype **mPOS: mitochondrial precursor over-accumulation stress.** Gis2's human ortholog is ZNF9/CNBP. Companion paper: Wrobel et al., *Nature* 2015;524:485 (UPRam).

**The mammalian relay is known and named:** mitochondrial import/processing perturbation is relayed to the cytosol via **OMA1–DELE1–HRI**, activating the integrated stress response (Guo et al., *Nature* 2020;579:427, DOI 10.1038/s41586-020-2078-2; Fessler et al., *Nature* 2020;579:433, DOI 10.1038/s41586-020-2076-4). DELE1 also directly tracks perturbed import (*Nat Commun* 2022, DOI 10.1038/s41467-022-29479-y).

**Why this is a legitimate two-route convergence and not a story:**
1. *Independent systems:* yeast dosage-suppressor genetics (2015) and human isogenic aneuploid cells (2025) were done by different labs, in different organisms, with different assays, for different reasons.
2. *Independent directions:* one is a forward rescue screen (what suppresses import-failure death), the other is a phenotype-first characterisation with a confirmatory rescue.
3. *Convergent axis:* both land on **cytosolic proteostasis capacity — chaperones, translation load, degradation throughput — as the buffer for unimported mitochondrial precursors.**
4. *Convergent with the human base rate:* Ünlü et al. found human suppressors are disproportionately general stress-response genes. This axis is exactly that class.
5. *Convergent with the oldest aneuploidy suppressor:* UBP6 loss (Torres 2010) is also a "increase degradation throughput" suppressor.

That is four independent evidence routes pointing at one axis. Under `docs/research_protocol.md` §11 that clears the two-route bar comfortably. **I score this L2 approaching L3** — L3 would require the rescue to be demonstrated in a constitutionally aneuploid, p53-competent human cell, which has not been done.

**Adversarial note, and it is serious:** HCT116 is a colorectal *cancer* line (MMR-deficient, near-diploid, TP53-WT). It is much better than a typical DepMap line for our purposes, but it is not a constitutional cell. And the entire mPOS suppressor network is yeast. Per §5, we transfer the **axis**, never the **gene list**.

**Recommendation: open a GitHub Issue for Workstream G.** It is the only workstream with a written prompt and no Issue, and on this audit's evidence it carries more usable rescue signal than the synthetic-rescue literature proper.

---

## 8. Primary evidence

| Claim | Source | Model / population | Evidence type | Level | Notes |
|---|---|---|---|---|---|
| Genetic suppression is a systematically mappable, quantified interaction class | van Leeuwen et al., *Science* 2016;354:aag0839. PMID 27811238, DOI 10.1126/science.aag0839 | *S. cerevisiae* | Peer-reviewed, experimental (yeast) | L4 (in yeast) | 221 interactions positive in ≥1 validation assay; frequent adaptive secondary mutations |
| The complete human genetic-suppression map is 476 interactions / 484 genes | Ünlü et al., *Genome Medicine* 2023;15. PMID 37821946, DOI 10.1186/s13073-023-01232-0 | Human (literature curation: cultured cells + patients) | Peer-reviewed, curation + computational | L2 | 302 cell-culture, 180 patient, 6 overlap; 99% single-study-type |
| Human suppression is less within-pathway and more stress/signaling than yeast | Same | Human vs yeast | Peer-reviewed, computational | L2 | 33% vs 55% functionally related; 38% vs 19% general stress/signaling; both p<0.0005 |
| A single LOF mutation (ubp6Δ) improves fitness of multiple different aneuploidies | Torres et al., *Cell* 2010;143:71. PMID 20850176 | *S. cerevisiae* disomes | Peer-reviewed, experimental | L3 (yeast) | Canonical general aneuploidy-tolerating suppressor |
| Chromosome gains cause mitochondrial import delay and cytosolic precursor accumulation into p62 bodies in human cells | Amponsah et al., *Nat Commun* 2025;16:5328. PMID 40527892, DOI 10.1038/s41467-025-60857-4 | Human HCT116 isogenic tri/tetrasomies | Peer-reviewed, experimental (human cancer line, near-diploid) | L3 | Import delay with normal Δψ; mtDNA 60–80%; complex-I respiration ~50% |
| Chaperone/HSF1 upregulation partially rescues aneuploidy-induced aggregation, but saturates with chromosome burden | Same | Same | Peer-reviewed, experimental | L3 | Rescue in trisomy 13/3; **no rescue in tetrasomy 5** |
| A genome-wide dosage-suppressor network buffers mitochondrial-import-failure death (mPOS) | Wang & Chen, *Nature* 2015;524:481. PMID 26192197, DOI 10.1038/nature14859 | *S. cerevisiae* | Peer-reviewed, experimental | L3 (yeast) | 40 suppressors; TOR, mRNA turnover, translation, tRNA methylation, chaperone/degradation |
| Mitochondrial import stress is relayed to cytosol via OMA1–DELE1–HRI in human cells | Guo et al. *Nature* 2020;579:427 (DOI 10.1038/s41586-020-2078-2); Fessler et al. *Nature* 2020;579:433 (DOI 10.1038/s41586-020-2076-4) | Human cell lines, iPSC | Peer-reviewed, experimental | L3 | Provides the measurable human readout for the axis |
| Loss of p31^comet partially suppresses the requirement for TRIP13 in checkpoint signalling | Nelson et al., *J Cell Biol* 2015;211:503. PMID 26527744, DOI 10.1083/jcb.201505114 | *C. elegans* | Peer-reviewed, experimental (animal) | L3 (worm) | Human cells **not** used in that paper |
| Biallelic MAD2L1BP (p31^comet) LOF causes human mosaic variegated aneuploidy + juvenile granulosa cell tumours | Abdel-Salam et al., *JCI Insight* 2023;8(22):e170079. PMID 37796616 | Human patients (n=3, 2 families) + isogenic HeLa complementation | Peer-reviewed, human + cell line | L5 (for causation) | Makes the TRIP13–p31 axis a *human MVA* axis |
| Reduced polo dosage suppresses bubR1 nondisjunction | Sousa-Guimarães et al., *G3* 2011;1:161. PMID 22384328, DOI 10.1534/g3.111.000265 | *Drosophila* | Peer-reviewed, experimental (animal) | L3 (fly) | NDJ ~27% → 6.6% with polo² |
| BubR1 dose is the disease variable; increasing it is protective in vivo | Baker et al., *Nat Cell Biol* 2013;15:96. PMID 23242215, DOI 10.1038/ncb2643 | Mouse transgenic | Peer-reviewed, animal | L3 | Dosage rescue: less aneuploidy, fewer tumours, longer healthspan |
| p16^Ink4a inactivation attenuates progeroid features of BubR1 hypomorphs; p19^Arf inactivation worsens them | Baker et al., *Nat Cell Biol* 2008;10:825. PMID 18516091, DOI 10.1038/ncb1744 | Mouse | Peer-reviewed, animal | L3 | A *bona fide* in vivo genetic suppressor of a BUB1B hypomorph — and a warning: the two INK4a/ARF products go opposite directions |
| CRISPR dependency scores are confounded by copy number | Meyers et al., *Nat Genet* 2017;49:1779. PMID 29083409, DOI 10.1038/ng.3984 | Cancer cell lines | Peer-reviewed, computational | L4 | Disqualifies DepMap as a candidate source for a copy-number disease |
| Cas9 editing is p53-dependently toxic and enriches p53-deficient cells | Ihry et al., *Nat Med* 2018;24:939. PMID 29892062, DOI 10.1038/s41591-018-0050-6 | Human PSC | Peer-reviewed, human cell | L3 | The screening platform selects against the patient's genotype class |
| Proliferation control, and thus chromosome-level fitness, is profoundly tissue-specific | Sack et al., *Cell* 2018;173:499. PMID 29576454, DOI 10.1016/j.cell.2018.02.037 | Human ORF screens, 3 tissues | Peer-reviewed, experimental | L3 | ~10% of genes control proliferation, mostly tissue-specifically |
| Yeast→human functional replaceability ~47%, predicted by module not sequence | Kachroo et al., *Science* 2015;348:921. PMID 25999509, DOI 10.1126/science.aaa0769 | Yeast + human genes | Peer-reviewed, experimental | L3 | Basis for "transfer the axis, not the pair" |
| Aneuploidy is itself a common, rapid, reversible suppressor mechanism | Yona et al. *PNAS* 2012 (DOI 10.1073/pnas.1211150109); Rancati et al. *Cell* 2008 (DOI 10.1016/j.cell.2008.09.039); Pavelka et al. *Nature* 2010 (DOI 10.1038/nature09529) | *S. cerevisiae* | Peer-reviewed, experimental | L4 (yeast) | Direct precedent for the project's core metaphor — and its worst confounder |
| Genetic compensation is triggered by mutant mRNA decay and is allele-class-dependent | El-Brolosy et al., *Nature* 2019;568:193. PMID 30944477, DOI 10.1038/s41586-019-1064-z | Zebrafish, mouse | Peer-reviewed, animal | L3 | Knockout-derived "rescue" may not transfer to a hypomorphic patient allele |
| Human primary constitutional trisomy fibroblasts show aneuploidy-associated stress phenotypes | *PNAS* 2021;118(6):e2014723118, DOI 10.1073/pnas.2014723118 | Human primary fibroblasts, trisomy 21 and others | Peer-reviewed, human primary | L3 | Closest available model to the patient |

---

## 9. Contradictory evidence

| Claim challenged | Source | Why it matters |
|---|---|---|
| "Aneuploidy necessarily causes proteotoxic stress requiring a compensatory suppressor" | Larrimore et al., *BMC Biol* 2020;18:117. PMID 32900371, DOI 10.1186/s12915-020-00852-x. Yeast, peer-reviewed | Six strains with 438–1,242 excess ORFs grew like euploids with **no** tolerating mutations, **no** dosage compensation, **no** chronic ESR/HSR; chr II disomes were *more* proteotoxin-resistant; excess DNA did not correlate with growth defect. Tolerance is karyotype-specific and sometimes free. **Severity: high.** Forces the karyotype-stratified reframing in §6 |
| "Rescue candidates can be derived from perturbation screens in cancer cells" | Meyers 2017 (PMID 29083409); Ihry 2018 (PMID 29892062); Sack 2018 (PMID 29576454) | Copy-number confounding, p53-selection of the platform, and tissue-specific proliferation control each independently break the transfer. **Severity: high.** Disqualifies DepMap as a generator |
| "Suppressor screens yield suppressors" | van Leeuwen et al., *Science* 2016, PMID 27811238 | Reproducible, growth-validating false positives (stationary-phase-delaying passengers). Suppressor screens have a structured, not random, error mode. **Severity: medium-high** |
| "A gene's suppressor is a property of the gene" | El-Brolosy et al. *Nature* 2019, PMID 30944477; allele-specificity of suppression (van Leeuwen *BioEssays* 2017, PMID 28582599); BubR1 allelic series (PMID 31738183) | Suppression is often allele-specific, and compensation depends on the mutant-mRNA class. MVA is a hypomorph disease. **Severity: medium-high.** Any knockout-derived rescue is weak evidence for a patient hypomorph |
| "Yeast suppressors will point us at human suppressors" | Ünlü 2023 (33% vs 55% functionally related; 38% vs 19% general stress); Dixon *PNAS* 2008 / Roguev *Science* 2008 (~23–29% GI conservation between two yeasts) | Pair-level transfer should be assumed to fail. **Severity: medium.** Survivable only via axis-level transfer |
| "The aneuploidy field supports a rescue frame" | Aneuploidy epistasis map (bioRxiv 2024, DOI 10.1101/2024.09.30.615609; *Genes Dev* 2025;39:770); aneuploid-specific dependency preprints | The field is overwhelmingly written in the kill direction. Dependency is not invertible into rescue. **Severity: medium.** It also means we have no field-standard rescue baseline to benchmark against |
| "Improving aneuploid-cell fitness is good" | Abdel-Salam 2023 (PMID 37796616): MAD2L1BP-MVA patients develop juvenile granulosa cell tumours; Baker 2008 (PMID 18516091): p19^Arf loss *worsens* BubR1 phenotypes while p16 loss improves them | Same locus, opposite directions. A suppressor can improve one readout while removing tumour surveillance. **Severity: high (safety).** Directly triggers §13 of the protocol |

---

## 10. What is directly supported vs inferred

### Directly supported
- Genetic suppression / synthetic rescue is an established experimental discipline with global-scale maps, formal evidence codes, and characterised false-positive modes. (Yeast: L4. Human: L2.)
- Aneuploidy-tolerating suppressor mutations exist and generalise across several karyotypes — **in yeast** (UBP6, SCH9).
- Chromosome gains impair mitochondrial protein import and drive cytosolic precursor sequestration into p62 bodies **in human cells**, and chaperone/HSF1 upregulation partially rescues this **below a chromosome-burden threshold**.
- A genome-wide dosage-suppressor network for mitochondrial-import-failure death exists in yeast, and the mammalian import-stress relay (OMA1–DELE1–HRI) is characterised.
- Documented cross-species suppressor relationships exist for two MVA-relevant genes (TRIP13↔p31^comet in *C. elegans*; polo↔bubR1 in *Drosophila*), and an in vivo mouse suppressor of BubR1 insufficiency exists (p16^Ink4a).
- Cancer dependency data are confounded by copy number, platform p53-selection, and tissue-specificity of proliferation control.

### Inferred (explicitly not established)
- That any of the above constitutes a compensatory mechanism **in this patient**. Nothing here is patient-specific; `data/` is empty and the gated dataset is not downloaded.
- That the mPOS/import axis is engaged in MVA specifically. MVA is *mosaic variegated* — a distribution of karyotypes across cells — whereas every human dataset above is a *uniform* engineered trisomy in a clonal line. The step from "trisomy-13 HCT116" to "a child whose cells each carry a different aneuploidy" is a real inferential jump, not a formality.
- That a chromosome-burden threshold for chaperone rescue exists in human constitutional cells. It was observed in one cancer-line panel with one set of constructs.
- That the TRIP13/p31 or bubR1/polo suppressions are therapeutically-directional. They are not; both plausibly point toward *more* checkpoint weakening.

---

## 11. Alternative explanations

1. **Cell-autonomous fitness isn't the operative variable at all; cell competition is.** Apparent "compensation" in a mosaic tissue may be the relative fitness of neighbours, not an intrinsic suppressor. Under this model there is no suppressor gene to find — only a competition topology. This alternative is fully consistent with all patient-side observations H1–H3 would produce, and it makes the entire H4 search a category error. It cannot be excluded without cell-resolved, spatially-aware data.
2. **Survivorship, not suppression.** The karyotypes we observe are the ones that got to the sampling needle. No compensatory mechanism is required to explain a biased survivor distribution — only generation probability × sampling. (This is the H2 Ghost-Karyotype confounder reappearing inside H4, and the project should note it is the *same* confounder, not a new one.)
3. **The stress signature is a consequence, not a compensable defect.** Elevated p62, ROS and precursor accumulation may be a terminal readout of dying cells rather than a buffered steady state. Rescuing a marker of dying cells is not rescuing anything.
4. **Chaperone/HSF1 "rescue" is generic proteotoxic-load relief, not aneuploidy-specific compensation.** Overexpressing HSP27/HSP90 reduces aggregates in a great many contexts. Without an aneuploidy-specific control (does it also reduce foci in a euploid stressed cell?), this is stress tolerance, not rescue. **This is the exact "what counts as real rescue vs generic stress tolerance?" question Issue #4 asks — and my answer is below.**
5. **Allele-class artefact.** Any suppressor inherited from knockout literature may be an artefact of mutant-mRNA-decay-triggered transcriptional adaptation and may simply not exist for the patient's hypomorphic allele.

### Rescue-evidence scoring rubric (Issue #4 deliverable)

A candidate compensatory mechanism scores one point per criterion. **Below 4/7 it is not a rescue claim, it is a stress-tolerance observation.**

| # | Criterion | Rationale |
|---|---|---|
| 1 | **Query-specific**: the effect is larger in the defective state than in an isogenic control subjected to comparable generic stress | Separates rescue from generic proteostasis relief (alt. explanation 4) |
| 2 | **Dose-responsive**: effect size tracks the magnitude of the primary defect (e.g. chromosome burden) | The Amponsah saturation result shows this is measurable |
| 3 | **Mechanism-directional**: the direction of modulation is predicted a priori by the defect's mechanism, not fitted post hoc | Prevents inverting a dependency into a "rescue" |
| 4 | **Two independent routes**, from different systems *and* different assay directions | `research_protocol.md` §11 |
| 5 | **Functional endpoint, not survival**: improves a defined function (import kinetics, missegregation rate, aggregate load) — not merely viability | `Safe Rescue Corridor`; survival alone is the failure mode |
| 6 | **CIN-neutral or CIN-reducing**: does not increase missegregation | MVA tumour predisposition |
| 7 | **Surveillance-preserving**: p53/apoptosis competence retained | Non-negotiable given juvenile granulosa cell tumours in MAD2L1BP-MVA |

Criteria 5–7 are **veto criteria**: failing any one of them kills the candidate regardless of total score.

---

## 12. Required hackathon data

**Absolute minimum to make H4 anything other than external-literature synthesis: bulk RNA-seq or proteomics from patient cells.** Without an expression modality, H4 cannot touch the patient at all and must be labelled *external-evidence hypothesis*, per `research_protocol.md` §6 VCF-only branch.

Ordered by what each modality unlocks:

| Modality | Unlocks | Necessity |
|---|---|---|
| **Bulk RNA-seq** (fibroblast/lymphoblast) | Mitochondrial-precursor / import-stress signature; ISR (ATF4/CHOP/DDIT3) activation; HSF1 target program; proteasome/autophagy load. Enables an mPOS-like *transcriptional* proxy | **Required** for any patient-side H4 claim |
| **Proteomics** (ideally with a cytosolic/mito fractionation) | The actual readout — cytosolic accumulation of mitochondrial precursors; complex-subunit stoichiometry attenuation | **Ideal.** Directly measures the axis rather than a proxy |
| **Cell-resolved karyotype + expression on the same cells** (scRNA-seq with CNV inference, or single-cell DNA) | The only way to test the karyotype-stratified reframing: *does stress-response magnitude scale with per-cell chromosome burden?* | **Decisive.** This is the experiment that makes H4 patient-specific rather than borrowed |
| Clinical karyotype / cytogenetics | Ground truth for burden per cell; anchors any inferred CNV | High value, low cost |
| WGS/VCF only | Causal gene identity → which suppressor axis to query in BioGRID/Ünlü. Nothing about compensation | Already assumed available |

**Explicit dependency statement:** the central H4 analysis I propose below (§13) **requires per-cell chromosome burden paired with per-cell expression.** If the gated dataset lacks a cell-resolved modality, that analysis is not merely weakened — it is not runnable, and H4 must be demoted to a literature-and-public-data hypothesis with no patient-specific claim. The project must resolve `research/open_questions.md` Q4 before committing to H4 as the scientific core.

---

## 13. Proposed analysis (exact)

**Analysis A — Chromosome-burden dose–response of the compensatory axis (the headline analysis; requires cell-resolved data).**

1. Per cell *i*, compute chromosome burden `B_i` = number of gained/lost chromosome equivalents (from single-cell CNV, or inferCNV-style inference validated against clinical karyotype; circularity caveat per protocol §6 must be stated).
2. Per cell, score three pre-registered gene programs: (i) **mitochondrial import/precursor stress proxy** — nuclear-encoded, MitoCarta3.0 matrix-targeted transcripts with cleavable presequences, relative to outer-membrane transcripts; (ii) **HSF1/chaperone program**; (iii) **ISR program** (ATF4/DDIT3/TRIB3, i.e. the DELE1–HRI output).
3. Fit `score ~ s(B_i)` with a spline plus a changepoint term, and **test explicitly for saturation** — the pre-registered prediction from Amponsah 2025 is a *rising-then-plateauing* chaperone response with continuing stress accumulation above the changepoint.
4. **Pre-register the null:** cell-cycle phase, library depth, ambient RNA, and doublets all correlate with both burden estimates and stress scores. The primary result must survive regressing these out, and must survive a permutation test that shuffles `B_i` within expression-neighbourhood-matched cell groups.

**The scientific claim being tested is a threshold, not a correlation.** A monotone correlation between aneuploidy and stress is expected, boring, and every team will find it. **A changepoint — a burden level above which the chaperone response stops rising while stress keeps rising — is the non-obvious, mechanistically-predicted result**, and it is the one that would make a compensatory mechanism (and its saturation) visible in a single static sample.

**Analysis B — Suppressor-space enumeration for the causal gene (runs today, no patient data).**
Query BioGRID by evidence code (`Synthetic Rescue`, `Dosage Rescue`, `Phenotypic Suppression`) for the causal gene and its orthologs across *S. cerevisiae*, *S. pombe*, *D. melanogaster*, *C. elegans*, mouse; intersect with the Ünlü 2023 human network and its RF predictor; annotate each hit with the 7-criterion rubric; and **collapse gene-level hits to axis-level modules** (per §5, transfer axes not pairs). Deliver a ranked *axis* list, not a gene list.

**Analysis C — Safety inversion (mandatory, runs today).**
For every candidate axis, query DepMap/BioGRID-ORCS in the **opposite** direction: is this axis an aneuploid-specific *dependency*? A candidate that appears as a dependency in aneuploid cancer screens is a candidate whose enhancement may make unstable cells fitter. **This is the correct and only use of cancer dependency data in this project.**

---

## 14. Expected scientific visualization

**Primary figure: the "compensation saturation curve".**
X-axis: per-cell chromosome burden (integer, jittered). Y-axis: two curves on shared axes — chaperone/HSF1 program (compensatory capacity) and mitochondrial-precursor-stress program (unmet load). Each with a bootstrap confidence band. A vertical marker at the fitted changepoint, with its own CI. Cells plotted as a rug or hexbin beneath, coloured by tissue/lineage if known.

Why this figure and not a UMAP: it encodes the *mechanistic quantity* (compensation vs load as a function of the driver), shows uncertainty on both curves and the threshold, and it is falsifiable by eye — if the two curves are parallel there is no saturation and the hypothesis is dead. A UMAP would show clustering and prove nothing.

**How it could mislead** (must be stated on the figure): burden is inferred, not measured, unless single-cell DNA exists; cells that already died are absent (survivorship — the curve is conditioned on survival and will *understate* stress at high burden); and per-cell program scores are depth-dependent.

**Secondary figure: the evidence-route graph** — causal gene → mechanism → candidate compensatory axis, with edges coloured by organism (yeast/fly/worm/mouse/human) and weighted by evidence level, showing at a glance that convergence comes from independent species rather than from one lab repeating itself. This is also the honest way to display how *thin* the human layer is.

---

## 15. Falsification test

**H4 is falsified for this patient if:** the compensatory-axis programs show **no changepoint and no burden-dependence** in cell-resolved patient data after covariate control — i.e. stress and chaperone programs rise in lockstep, or neither varies with burden. Under that result there is no evidence of a saturating compensatory mechanism, and "synthetic rescue" for this child reduces to borrowed cancer framing.

**The mPOS/proteostasis axis specifically is falsified if:** mitochondrial-presequence-containing transcript/protein programs show no elevation relative to matched controls, or the ISR (ATF4/DDIT3) output is unengaged, in patient material with confirmed aneuploid burden.

**The whole rescue frame is falsified experimentally if:** in a patient-derived (or constitutional-trisomy) p53-competent cell, chaperone/HSF1 elevation reduces aggregate load **without** improving any functional endpoint (import kinetics, respiration, missegregation rate) — that would demote the observation from *rescue* to *generic stress tolerance* under criterion 5 of the rubric.

## 16. What result would make us abandon this idea?

Any one of:
- The gated dataset contains **no expression or proteomic modality**. Then H4 cannot be tested in this patient, and presenting it as the project's scientific core would be dishonest. (Demote to external-evidence hypothesis; do not abandon the axis, abandon the *claim of patient specificity*.)
- The compensatory-axis signal exists but **disappears under cell-cycle and depth correction** — the single most likely mundane explanation.
- Every candidate axis fails a **veto criterion** (5, 6 or 7): improves survival without function, or increases CIN, or compromises p53/apoptosis. Given MVA tumour predisposition, a rescue that fails these is worse than no rescue.
- Independent evidence shows the child's persistent karyotypes are explained by **generation probability × sampling alone** — then there is no selection signal for a compensatory mechanism to explain.

---

## 17. Transferability beyond MVA

**High, and this is one of H4's genuine strengths.** The structure — *constitutional mosaic disease → per-cell burden → dose-response of a compensatory axis → saturation threshold* — is not MVA-specific. It applies directly to:
- constitutional mosaic trisomies and mosaic Down syndrome,
- Pallister-Killian / mosaic tetrasomy 12p,
- other CIN syndromes (Warsaw breakage, Roberts, cohesinopathies),
- somatic mosaic overgrowth disorders (PIK3CA/AKT1 spectrum), where per-cell variant allele fraction substitutes for chromosome burden,
- revertant mosaicism syndromes, where the burden axis is inverted.

The transferable artefact is the **saturation-curve analysis plus the 7-criterion rescue rubric**, not any specific gene. That is the right kind of generalisation: a method, not a hit list.

---

## 18. "How did you notice that?" factor — **4 / 5**

Not 5. The synthetic-rescue frame itself is well known to anyone who has read Boone/Andrews, and inverting synthetic lethality is a standard move — the hackathon will likely see several teams say "synthetic rescue".

It earns 4 for three specific things a competent team would probably miss:

1. **The saturation clause.** Everyone who reads Amponsah 2025 will note "chaperones rescue aneuploidy stress". The sentence that matters is *"5/4 cells showed no rescue"* — a dose-limited compensation. In a disease that is definitionally a *distribution* of chromosome burdens, a saturating compensator predicts a **threshold visible in a single static sample**, which is exactly what a project with one bulk/one-timepoint dataset needs. That is a non-obvious match between an obscure negative result and our specific data constraint.
2. **Aneuploidy is itself the classic suppressor.** The yeast literature says whole-chromosome gain is one of the most common spontaneous suppressor mutations. Most teams will treat MVA's karyotype variety as pathology-to-be-explained. Reading it as a *suppressor-generating machine* is the project's core metaphor arriving with independent experimental precedent attached — and simultaneously arriving with its own worst confounder attached, which is why it is worth 4 and not 5.
3. **The size of the human suppression corpus.** Knowing that "search human suppressors" means "consult 476 hand-curated facts" is the kind of thing that changes a project plan and is invisible until you look it up.

---

## 19. Verdict: **CONDITIONAL**

**Should this be the scientific core of MOSAIC RESCUE?** Only in one specific form.

- **PURSUE** — the **mPOS / mitochondrial-import / cytosolic-proteostasis axis with the burden-saturation prediction** (Workstream G). It has four convergent evidence routes, a human anchor, a quantitative prediction, and a clean falsification test.
- **CONDITIONAL** — the **general synthetic-rescue frame**, conditional on (i) an expression or proteomic modality existing in the gated dataset, and (ii) the project committing in writing to axis-level, not pair-level, cross-species transfer.
- **PARK** — the **TRIP13↔p31^comet and bubR1↔polo suppressor axes.** Real, mechanistically documented, in the right pathway, and **directionally alarming**: both suppress by further weakening checkpoint function in a tumour-predisposition disease. Keep them as mechanism-router evidence and as safety counter-examples. Do not develop them as rescue candidates.
- **REJECT** — **any use of DepMap or cancer GI maps as a candidate-generation source for compensatory mechanisms.** Copy-number confounding, platform p53-selection, and tissue-specific proliferation control each independently break the transfer, and the disease is defined by the exact variable that confounds the measurement. Cancer dependency data are retained for **safety inversion only** (Analysis C).

---

## 20. Recommended next action (Next Best Experiment)

**Next best *computational* action (this week, no patient data required):** run Analysis B — the cross-species suppressor-space enumeration over BioGRID evidence codes plus the Ünlü 2023 network — for each candidate causal gene coming out of Track 1, and deliver **ranked axes with rubric scores**, plus Analysis C safety inversion. This is the concrete Issue #4 deliverable and it is not blocked by the gated dataset.

**Next best *experiment* to reduce uncertainty between surviving hypotheses:**
In a patient-derived (or, failing that, constitutional-trisomy) **p53-competent, non-transformed** fibroblast line, measure **mitochondrial protein import kinetics** (radiolabelled or split-fluorophore presequence reporter) and **cytosolic precursor load** as a function of **per-cell chromosome burden**, ± chaperone/HSF1 elevation, with three endpoints read simultaneously: import kinetics (function), aggregate/p62 load (stress), and **missegregation rate + p53 competence (safety)**.

This single experiment discriminates all four live hypotheses: generic stress tolerance (aggregates fall, import unchanged), true compensation (both improve), saturation (both improve only below a burden threshold), and unsafe rescue (both improve but missegregation rises). It is the only design in this report where the safety veto and the efficacy readout come from the same assay.

**Repository action:** open a GitHub Issue for **Workstream G**. It is the only workstream with a written prompt (`docs/agent_prompts.md`, Prompt G) and no Issue, and on this audit it carries more usable compensatory-mechanism evidence than the synthetic-rescue literature proper.

---

## 21. Repository infrastructure gaps observed (beyond those listed in the brief)

Verified against HEAD on 2026-08-28. Reporting, not inventing.

- **Workstream G has no Issue.** Open Issues are #1–#9, mapping to prompts A, C, D, E, B, F, H, I+J, K. Prompt G is unrepresented. Confirmed.
- **No rescue-evidence scoring rubric existed anywhere in the repo** before this report. Issue #4 lists it as a deliverable; §11 above supplies a first version. It should be promoted out of this report into a standalone file (suggest `docs/rescue_evidence_rubric.md`) so other workstreams can cite it.
- **No external-dataset manifest.** `docs/` has no file recording which public resources the project will use, their access terms, versions, or licences. Given that Issue #4's deliverable is explicitly "shortlist of external datasets/tools", the repo has nowhere to put it. Suggest `research/external_datasets.md`.
- **`research/evidence_registry.md` and `research/contradictions.md` remain empty templates (E001, C001).** This report generates ~20 registry rows and ~7 contradiction rows; they are not yet transcribed, per AGENTS.md the transcription is a separate accepted step.
- **No `requirements.txt` / `environment.yml` / `pyproject.toml` / LICENSE.** Analyses B and C above need at minimum a pinned Python environment (pandas, scanpy/anndata, statsmodels or pyGAM for the changepoint fit) before they are reproducible under `research_protocol.md` §15.
- **"Track 2" still appears nowhere in the repository.** Consistent with the brief. Relevant to this workstream because §19's PARK/REJECT decisions are meaningless unless the project has recorded that the final Track 2 intervention must be an approved drug — otherwise a mechanism like "elevate HSF1" can silently drift into the final slot.
- **`data/` is empty; the gated dataset is not downloaded.** Everything in this report is external literature and public data. No patient-specific claim is made anywhere above.

---

## References

Peer-reviewed unless marked. System marked as human / animal / cell line / organoid / computational.

1. van Leeuwen J, et al. Exploring genetic suppression interactions on a global scale. *Science*. 2016;354(6312):aag0839. PMID 27811238. DOI 10.1126/science.aag0839. *Peer-reviewed; yeast (experimental) + computational.*
2. van Leeuwen J, Pons C, Boone C, Andrews BJ. Mechanisms of suppression: the wiring of genetic resilience. *BioEssays*. 2017;39(7):1700042. PMID 28582599. DOI 10.1002/bies.201700042. *Peer-reviewed review; yeast-focused.*
3. van Leeuwen J, et al. Systematic analysis of bypass suppression of essential genes. *Mol Syst Biol*. 2020;16(9):e9828. PMID 32939983. DOI 10.15252/msb.20209828. *Peer-reviewed; yeast.*
4. Ünlü B, Pons C, Ho UL, Batté A, Aloy P, van Leeuwen J. Global analysis of suppressor mutations that rescue human genetic defects. *Genome Medicine*. 2023. PMID 37821946. DOI 10.1186/s13073-023-01232-0. *Peer-reviewed; human (literature curation of cell-line and patient studies) + computational.*
5. Torres EM, et al. Identification of aneuploidy-tolerating mutations. *Cell*. 2010;143(1):71-83. PMID 20850176. DOI 10.1016/j.cell.2010.08.038. *Peer-reviewed; yeast.*
6. Larrimore KE, et al. Aneuploidy-induced proteotoxic stress can be effectively tolerated without dosage compensation, genetic mutations, or stress responses. *BMC Biol*. 2020;18:117. PMID 32900371. DOI 10.1186/s12915-020-00852-x. *Peer-reviewed; yeast.* **Contradictory.**
7. Amponsah PS, Bökenkamp JE, Kurpa O, et al. Aneuploidy-induced proteostasis disruption impairs mitochondrial functions and mediates aggregation of mitochondrial precursor proteins through SQSTM1/p62. *Nat Commun*. 2025;16:5328. PMID 40527892. DOI 10.1038/s41467-025-60857-4. *Peer-reviewed; human cell line (HCT116 isogenic aneuploids).*
8. Wang X, Chen XJ. A cytosolic network suppressing mitochondria-mediated proteostatic stress and cell death. *Nature*. 2015;524(7566):481-484. PMID 26192197. DOI 10.1038/nature14859. *Peer-reviewed; yeast.*
9. Wrobel L, et al. Mistargeted mitochondrial proteins activate a proteostatic response in the cytosol. *Nature*. 2015;524(7566):485-488. DOI 10.1038/nature14951. *Peer-reviewed; yeast.*
10. Guo X, et al. Mitochondrial stress is relayed to the cytosol by an OMA1-DELE1-HRI pathway. *Nature*. 2020;579:427-432. DOI 10.1038/s41586-020-2078-2. *Peer-reviewed; human cell lines/iPSC.*
11. Fessler E, et al. A pathway coordinated by DELE1 relays mitochondrial stress to the cytosol. *Nature*. 2020;579:433-437. DOI 10.1038/s41586-020-2076-4. *Peer-reviewed; human cell lines.*
12. Nelson CR, Hwang T, Chen PH, Bhalla N. TRIP13(PCH-2) promotes Mad2 localization to unattached kinetochores in the spindle checkpoint response. *J Cell Biol*. 2015;211(3):503-516. PMID 26527744. DOI 10.1083/jcb.201505114. *Peer-reviewed; animal (C. elegans).*
13. Abdel-Salam GMH, et al. Biallelic MAD2L1BP (p31comet) mutation is associated with mosaic aneuploidy and juvenile granulosa cell tumors. *JCI Insight*. 2023;8(22):e170079. PMID 37796616. DOI 10.1172/jci.insight.170079. *Peer-reviewed; human patients + cell line.*
14. Sousa-Guimarães S, Sunkel CE, Malmanche N. polo is identified as a suppressor of bubR1 nondisjunction in a deficiency screen of the third chromosome in Drosophila melanogaster. *G3*. 2011;1(2):161-169. PMID 22384328. DOI 10.1534/g3.111.000265. *Peer-reviewed; animal (Drosophila).*
15. Baker DJ, et al. Opposing roles for p16Ink4a and p19Arf in senescence and ageing caused by BubR1 insufficiency. *Nat Cell Biol*. 2008;10(7):825-836. PMID 18516091. DOI 10.1038/ncb1744. *Peer-reviewed; animal (mouse).*
16. Baker DJ, et al. Increased expression of BubR1 protects against aneuploidy and cancer and extends healthy lifespan. *Nat Cell Biol*. 2013;15(1):96-102. PMID 23242215. DOI 10.1038/ncb2643. *Peer-reviewed; animal (mouse).*
17. Wijshake T / Baker DJ et al. BubR1 allelic effects drive phenotypic heterogeneity in mosaic-variegated aneuploidy progeria syndrome. *J Clin Invest*. 2019/2020. PMID 31738183. DOI 10.1172/JCI126863. *Peer-reviewed; animal (mouse).*
18. Meyers RM, et al. Computational correction of copy number effect improves specificity of CRISPR-Cas9 essentiality screens in cancer cells. *Nat Genet*. 2017;49:1779-1784. PMID 29083409. DOI 10.1038/ng.3984. *Peer-reviewed; cancer cell lines + computational.*
19. Ihry RJ, et al. p53 inhibits CRISPR-Cas9 engineering in human pluripotent stem cells. *Nat Med*. 2018;24:939-946. PMID 29892062. DOI 10.1038/s41591-018-0050-6. *Peer-reviewed; human cell (hPSC).*
20. Haapaniemi E, et al. CRISPR-Cas9 genome editing induces a p53-mediated DNA damage response. *Nat Med*. 2018;24:927-930. DOI 10.1038/s41591-018-0049-z. *Peer-reviewed; human cell.*
21. Horlbeck MA, et al. Mapping the genetic landscape of human cells. *Cell*. 2018;174(4):953-967. PMID 30033366. DOI 10.1016/j.cell.2018.06.010. *Peer-reviewed; human cancer cell lines (K562, Jurkat).*
22. Norman TM, et al. Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. *Science*. 2019;365(6455):786-793. PMID 31395745. DOI 10.1126/science.aax4438. *Peer-reviewed; human cancer cell line (K562).*
23. Replogle JM, et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq. *Cell*. 2022;185(14):2559-2575. PMID 35688146. DOI 10.1016/j.cell.2022.05.013. *Peer-reviewed; human cell lines (K562 cancer; RPE1 hTERT-immortalised near-diploid).*
24. Oughtred R, et al. The BioGRID database. *Protein Sci*. 2021;30(1):187-200. PMID 33070389. DOI 10.1002/pro.3978. *Peer-reviewed; database.* Evidence codes: wiki.thebiogrid.org/doku.php/experimental_systems
25. BioGRID ORCS. orcs.thebiogrid.org. *Database.* Screen-type composition figure (~6.7% positive/phenotypic) from iCSDB, *Nucleic Acids Res*. 2021;49(D1):D956. DOI 10.1093/nar/gkaa989. *Peer-reviewed; database.*
26. Kachroo AH, et al. Systematic humanization of yeast genes reveals conserved functions and genetic modularity. *Science*. 2015;348(6237):921-925. PMID 25999509. DOI 10.1126/science.aaa0769. *Peer-reviewed; yeast + human genes.*
27. Dixon SJ, et al. Significant conservation of synthetic lethal genetic interaction networks between distantly related eukaryotes. *PNAS*. 2008;105(43):16653-16658. PMID 18931302. *Peer-reviewed; yeast.*
28. Roguev A, et al. Conservation and rewiring of functional modules revealed by an epistasis map in fission yeast. *Science*. 2008;322(5900):405-410. PMID 18818364. DOI 10.1126/science.1162609. *Peer-reviewed; yeast.*
29. Sack LM, et al. Profound tissue specificity in proliferation control underlies cancer drivers and aneuploidy patterns. *Cell*. 2018;173(2):499-514. PMID 29576454. DOI 10.1016/j.cell.2018.02.037. *Peer-reviewed; human cells (3 tissue types).*
30. Davoli T, et al. Cumulative haploinsufficiency and triplosensitivity drive aneuploidy patterns and shape the cancer genome. *Cell*. 2013;155(4):948-962. PMID 24183448. DOI 10.1016/j.cell.2013.10.011. *Peer-reviewed; computational (cancer genomes).*
31. Hwang S, et al. Consequences of aneuploidy in human fibroblasts with trisomy 21. *PNAS*. 2021;118(6):e2014723118. DOI 10.1073/pnas.2014723118. *Peer-reviewed; human primary fibroblasts (constitutional trisomy).*
32. El-Brolosy MA, et al. Genetic compensation triggered by mutant mRNA degradation. *Nature*. 2019;568:193-197. PMID 30944477. DOI 10.1038/s41586-019-1064-z. *Peer-reviewed; animal (zebrafish, mouse).*
33. Rossi A, et al. Genetic compensation induced by deleterious mutations but not gene knockdowns. *Nature*. 2015;524:230-233. DOI 10.1038/nature14580. *Peer-reviewed; animal (zebrafish).*
34. Yona AH, et al. Chromosomal duplication is a transient evolutionary solution to stress. *PNAS*. 2012;109(51):21010-21015. DOI 10.1073/pnas.1211150109. *Peer-reviewed; yeast.*
35. Rancati G, et al. Aneuploidy underlies rapid adaptive evolution of yeast cells deprived of a conserved cytokinesis motor. *Cell*. 2008;135(5):879-893. DOI 10.1016/j.cell.2008.09.039. *Peer-reviewed; yeast.*
36. Pavelka N, et al. Aneuploidy confers quantitative proteome changes and phenotypic variation in budding yeast. *Nature*. 2010;468:321-325. DOI 10.1038/nature09529. *Peer-reviewed; yeast.*
37. Genetic suppression interactions are highly conserved across genetically diverse yeast isolates. *G3*. 2025;15(5):jkaf047. DOI 10.1093/g3journal/jkaf047. *Peer-reviewed; yeast.*
38. An aneuploidy epistasis map reveals metabolic vulnerabilities associated with supernumerary chromosomes in cancer. bioRxiv 2024. DOI 10.1101/2024.09.30.615609. **PREPRINT**; *human cell line (isogenic hTERT-HMEC).* Peer-reviewed companion: Aneuploidy generates enhanced nucleotide dependency and sensitivity to metabolic perturbation. *Genes Dev*. 2025;39(11-12):770.
39. Paired CRISPR screens identify mitochondrial metabolism and UBE2H as aneuploid-specific dependencies in human cancer cell lines. bioRxiv 2026. DOI 10.64898/2026.04.26.720636. **PREPRINT**; *human cancer cell lines.*
40. DepMap Portal. depmap.org. *Database; cancer cell lines.* Chronos gene-effect scores; dependency signal only.

### Claims flagged as needing primary re-verification before use in a public deliverable

- The K562 (1,523) vs Jurkat (374) vs shared (82) synthetic-lethal counts attributed to Horlbeck 2018 came from secondary analyses (SLKB / a *Front Genet* 2022 review), not from the primary supplementary tables. The qualitative conclusion (strong context-dependence of GI calls between two human cancer lines) is safe; **the exact numbers must be re-derived from the primary data before being quoted.**
- The ~6.7% positive/phenotypic-screen fraction of BioGRID ORCS is from the iCSDB survey, not from ORCS itself; recompute from the current ORCS download before quoting.
- van Leeuwen 2016's full-text counts (literature-curated interaction total, number of query mutants screened) were not obtained — the *Science* full text is paywalled and the author-hosted PDF exceeded fetch limits. The figures used above (221 validated interactions; systematic stationary-phase-delay passenger mutations) are from the abstract and SGD/secondary summaries and should be confirmed against the paper.
