# Rescue Evidence Rubric

Deliverable for [Issue #4](https://github.com/Manceb0/mosaic-rescue/issues/4). Promoted from the
Synthetic Rescue audit (`research/agent_findings/2026-08-28_synthetic-rescue_agent-c.md`, §11).

This rubric exists because "rescue" is the easiest claim in the project to fake. A candidate that
merely reduces generic cellular stress, or that increases viability without improving function,
will look like rescue in almost any assay. The criteria below are designed to separate the two.

## Scoring

A candidate compensatory mechanism scores **one point per criterion**.

**Below 4/7 it is not a rescue claim. It is a stress-tolerance observation**, and must be recorded
as such in `research/evidence_registry.md`.

| # | Criterion | Rationale |
|---|---|---|
| 1 | **Query-specific** — the effect is larger in the defective state than in an isogenic control under comparable generic stress | Separates rescue from generic proteostasis relief |
| 2 | **Dose-responsive** — effect size tracks the magnitude of the primary defect (e.g. per-cell chromosome burden) | The Amponsah saturation result (PMID 40527892) shows this is measurable |
| 3 | **Mechanism-directional** — the direction of modulation is predicted *a priori* by the defect's mechanism, not fitted post hoc | Prevents inverting a dependency into a "rescue" |
| 4 | **Two independent routes** — from different systems *and* different assay directions | One route can be an artefact of its system; agreement across systems and assay directions cannot |
| 5 | **Functional endpoint, not survival** — improves a defined function (import kinetics, missegregation rate, aggregate load), not merely viability | Survival alone is the failure mode the Safe Rescue Corridor exists to catch |
| 6 | **CIN-neutral or CIN-reducing** — does not increase missegregation | MVA tumour predisposition |
| 7 | **Surveillance-preserving** — p53/apoptosis competence retained | Non-negotiable given tumour susceptibility in MVA forms |

## Veto criteria

**Criteria 5, 6 and 7 are vetoes.** Failing any one of them kills the candidate regardless of total
score. A candidate scoring 6/7 that increases CIN is rejected, not ranked sixth.

## Worked rejection — why this rubric is not theoretical

Two genuine, documented suppressor relationships in the correct pathway were found in the first
literature pass and **parked under this rubric**:

- **TRIP13 ↔ p31^comet**
- **bubR1 ↔ polo** (*Drosophila*)

Both are real. Both are in the right pathway. Both suppress **by weakening the spindle assembly
checkpoint further** — in a disease with tumour predisposition. They fail criteria 6 and 7.

This is the exact case the "rescue ≠ survival" principle was written to catch, and it appeared
immediately. The rubric earns its place.

## BUB1B rescue evidence ladder (literature, verified 2026-09-29)

What has already been rescued in cells with the disease gene, kept in three separate tiers so that
a mechanistic surrogate is never reported as a patient-cell result. Each rung was checked against
the full text (PMC) or, for Matsuura 2006, the PubMed abstract. None of these cells is from this
patient.

**Tier 1 · Direct rescue in cells from BUB1B-MVA/PCS patients (genetic, not therapeutic)**

| Year | Perturbation | Cells | Readout restored | Source |
|---|---|---|---|---|
| 2006 | Microcell transfer of chromosome 15 (carries BUB1B) | PCS patient cells (monoallelic coding mutation found) | Normal BubR1 levels, p55cdc kinetochore localization, normal colcemid response | Matsuura et al., PMID 16411201, [10.1002/ajmg.a.31069](https://doi.org/10.1002/ajmg.a.31069) |
| 2010 | Transient re-expression of BUBR1 | Lymphoblastoid and fibroblast lines from biallelic MVA patients | Nocodazole response about 2-fold; in one line, up to the level of the heterozygous parent (Fig. 1D) | Suijkerbuijk et al., PMID 20516114, [10.1158/0008-5472.CAN-09-4319](https://doi.org/10.1158/0008-5472.CAN-09-4319) |
| 2013 | BUBR1 WT; artificial kinetochore targeting of PP2A-B56 (MIS12-KARD-3D) | Fibroblasts MVA-41C and MVA-12C | Chromosome alignment in MG132-arrested cells, in both lines | Xu et al., PMID 23789096, [10.1242/bio.20134051](https://doi.org/10.1242/bio.20134051) |

Read from the figures, not only the text:
- **Partial, not complete.** In Suijkerbuijk Fig. 1D, re-expressed BUBR1 lifts the patient lines to
  the heterozygous-parent level, about half of the healthy control. In Xu Fig. 4B, aligned cells
  rise from about 25–35 % to about 60–67 %, against about 80 % in the healthy line.
- **Probably not independent patients.** The 2010 and 2013 fibroblast lines carry the same two
  genotypes (one truncation plus one kinase-domain missense; one truncation plus one TPR
  missense) and come from the same group's collection: very likely the same two people, though
  neither paper states it. The ladder has depth of mechanism, not breadth of patients.
- **Transformed lines.** In Suijkerbuijk 2010 the fibroblasts were SV40-transformed and the
  lymphoblastoid lines EBV-transformed (Methods). Transformation is itself a selective passage,
  which matters for a project arguing that the assay can select what we see.
- **A readout that goes the wrong way.** In the 2013 MVA lines a BUBR1 mutant unable to bind B56
  lowered alignment below untreated (dominant-negative). It is part of the benchmark.
- **Thresholds do not transfer between cell types.** The HeLa threshold below (about 13 % BUBR1
  tolerated) sits next to an MVA fibroblast line with about 17 % BUBR1 (Xu Fig. 4A) that is still
  clearly defective.

**Tier 2 · Mechanistic surrogates (not MVA patient cells)**

- Suijkerbuijk 2010, protein replacement in HeLa/U2OS: kinase-domain missense mutants fail mainly
  through **low abundance**; forcing two of them (published alleles from other families) to
  wild-type levels fully restored the nocodazole response. BUBR1 knocked down to about 13 % left segregation almost
  intact, while about 6 % caused missegregation in most cells: a steep abundance threshold.
  These are other patients' alleles, not the variants of this case.
- Xu 2013, HeLa: Aurora B inhibition (ZM447439, or Aurora B siRNA) rescued the congression defect
  of a B56-binding-deficient BUBR1 mutant. Pathway: BUBR1 → PP2A-B56 at the kinetochore → opposes
  Aurora B → stable attachment.

**Tier 3 · Pharmacological direction (hypothesis, not demonstrated in MVA cells)**

- Aurora B inhibition is mechanistically plausible from Tier 2. **It has not been shown to rescue
  BUB1B-MVA patient cells** in these papers; the MVA-cell experiments used BUBR1 or PP2A-B56
  targeting, not ZM447439. Defensible wording: *Aurora B inhibition rescues the mechanistically
  related B56/BUBR1-deficient congression phenotype in an engineered cellular system, while
  PP2A-B56 targeting rescues chromosome alignment directly in BUB1B-MVA patient cells.*
- Raising BUBR1 abundance (proteostasis) is suggested by the abundance threshold of Tier 2. The
  existing Track 2 bridge on chaperones stays unresolved: inhibiting HSP90 lowers mutant BUBR1,
  but adding chaperone capacity has not been shown to raise it.

**What the ladder does not yet contain.** In MVA patient cells every rescue readout is a
checkpoint response or alignment in arrested cells. Anaphase missegregation was measured only in
the HeLa replacement system (Suijkerbuijk Fig. 5B), not in patient cells. So no patient-cell
rescue reports the rubric's criterion 5 endpoint, *new segregation errors per completed mitosis*,
and none measures survival of unstable cells (criterion 7). In two PubMed
searches on 2026-09-29 (MVA/BUB1B/BUBR1 × patient cells × rescue/drug × segregation, 2013–2026)
we found **no small molecule or small perturbation applied directly to BUB1B-MVA patient cells
that reduced segregation errors**. That is the open gap Track 2 should aim at.

## Rescue is layered: endpoint-dependent rescue

There is no single rescue endpoint. At least five layers can recover independently:

| Layer | What recovers | Example readout |
|---|---|---|
| Molecular | the interaction or modification | KARD phosphorylation, PP2A-B56 at the kinetochore |
| Checkpoint | the response and its timing | nocodazole arrest; time to exit after checkpoint inhibition |
| Alignment | congression | misaligned chromosomes in a quantitative alignment-zone assay |
| Segregation | new errors | errors per completed mitosis |
| Safety | no gain for unstable cells | survival and propagation of aneuploid cells (criteria 6–7) |

**Worked example: 731X.** In Suijkerbuijk 2010 this MVA truncation, lacking the pseudokinase
domain, looked fully functional on coarse endpoints (nocodazole response, segregation, alignment,
HeLa/U2OS). Gama Braga 2020 (PMID 33207204, full text read) retested it **at kinetochore levels
matched to wild type** (doxycycline titration, their Fig. S4A): KARD phosphorylation was reduced,
PP2A-B56 was not restored at the kinetochore, checkpoint exit was delayed (half of cells exiting
at about 55–65 min versus about 35 min for wild type) and misaligned chromosomes increased (their
Figs. 3–4). Abundance was controlled, so overexpression is **not** the main explanation; the
difference is readout sensitivity and context. A construct can look rescued on coarse mitotic
endpoints while keeping a proximal signalling defect. Any rescue claim in this project names the
layer it reached.

Two further observations from the same paper bear on the case missense: published MVA
kinase-domain missense mutants were even less hyperphosphorylated in mitosis than catalytic-site
mutants (their Fig. 2D), and HSP90 inhibition lowered KARD phosphorylation **relative to total
BUBR1** (their Fig. 2F–G). Folding therefore affects signalling, not only amount, which is why the
missense must be tested at matched abundance (H2 below). All of this is HeLa, not patient cells.

## What the ladder means for this case's genotype

Sanitized: domains and published analogues only, no residue numbers or amino-acid identities.
Mapping uses UniProt O60566 (protein kinase domain 766–1050) and the frozen local structure files.
Every line is a **prediction to measure**, not a result.

- **The missense lies inside the kinase domain**, buried. Suijkerbuijk 2010 found that every
  tested kinase-domain MVA missense lowered BUBR1 abundance 5–10-fold, with HSP90-dependent
  folding and proteasomal turnover (their Fig. 2D and 3C). Prediction, **class-level only**: this
  allele belongs to the low-abundance class (H1). In the AlphaFold model none of those published
  residues touches the case residue (nearest about 10 Å, others 20–26 Å, minimum heavy-atom
  distance). That only says there is no immediate structural neighbourhood in this model; it
  neither supports nor excludes a shared mechanism. **Alternative (H2):** the C-terminal domain
  is a functional pseudokinase that promotes PP2A-B56 recruitment, checkpoint silencing and
  alignment (Gama Braga 2020, PMID 33207204), and its ATP-binding residues matter for
  conformational stability (Suijkerbuijk 2012, PMID 22698286), so the missense may also impair
  function directly. H1 and H2 are separated only by function **at matched abundance**.
- **The truncation lies just upstream of the kinase domain**, between two published truncations
  whose plasmid-expressed products behaved differently: one restored checkpoint, segregation and
  alignment, the other was unstable (Suijkerbuijk Fig. 2D and 5). NMD is predicted from **this
  case's own transcript architecture**, not by analogy: on the canonical transcript the premature
  stop lies about 750 nt upstream of the last exon–exon junction (`docs/ACMG_CURATION.md`,
  PVS1 section). It is a prediction; no transcript was measured. The first question is therefore
  **not** readthrough but whether the exact truncated product would work if it existed, read on a
  hierarchy of endpoints (next section). If it works on all of them, the bottleneck is transcript
  and protein amount; if not, readthrough gains weight.
- **Closest published genotype class.** A truncation plus a kinase-domain missense (genotype
  printed in Xu Fig. 4A): the fibroblast line MVA-12C, with about 17 % BUBR1, the weakest
  checkpoint in Suijkerbuijk Fig. 1 and about 35 % aligned cells in Xu Fig. 4. Neither of its
  variants is at the case positions, and it is an SV40-transformed line. It is a useful
  **disease-line benchmark** for an assay on this case, not a natural control.
- **Consequence for Track 2.** Only if H1 holds is the most direct route to raise the amount of
  the missense protein (T2-A); forcing kinase-domain missense proteins to wild-type levels
  restored checkpoint function in HeLa/U2OS. That route is untested for this allele and must pass
  the vetoes above. Before choosing any drug, two experiments can show we are solving the wrong
  problem: the truncation-bypass test and the matched-abundance missense test.
- **First measurements.** (1) Missense in isogenic cells with cycloheximide, geldanamycin and
  MG132 arms (Suijkerbuijk Fig. 3C design), then titrated to wild-type abundance and scored for
  kinetochore localisation, nocodazole response, alignment, checkpoint-silencing timing and
  segregation errors per completed mitosis. (2) The exact truncated product from cDNA at matched
  abundance, same readouts. MVA-12C serves as a transformed disease-line benchmark.
- **Route evaluated and parked: PCAF acetylation – HDAC2/3.** It sets the timing of mitotic
  BUBR1 destruction, not folding-dependent turnover; sustained acetylation arrests cells in
  metaphase and HDAC3 loss breaks the spindle (PMID 19407811, 28985013, 28562161, 28935703).
  It is also a worked example for this rubric: an intervention that raises a desirable BUBR1
  property while breaking mitosis another way fails criteria 3 and 6.

## Recording

Every scored candidate goes into `research/evidence_registry.md` with its score, the criteria it
failed, and whether a veto was triggered. A candidate that fails a veto is still recorded — a
documented rejection is a project asset, not a dead end.
