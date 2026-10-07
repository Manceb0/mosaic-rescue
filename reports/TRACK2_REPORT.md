# MOSAIC RESCUE — Track 2 report

**A falsification-first drug-repurposing hypothesis for `BUB1B`-related mosaic variegated aneuploidy**

Rare Disease, Real Kid: MVA Hackathon 2026
Repository: <https://github.com/Manceb0/mosaic-rescue>

---

## 1 · What this report proposes

Three approved compounds, in **three different roles**, as a portfolio for a first preclinical
experiment:

| Compound | Role | Mechanism proposed | Status |
|---|---|---|---|
| **Azithromycin** | allele-directed | Readthrough of the premature stop codon, to restore some full-length BUBR1 | Approved, paediatric use established |
| **Arimoclomol** | falsification sentinel | Amplify the heat-shock response to raise chaperone capacity and with it BUBR1 abundance | FDA-approved for Niemann-Pick type C, ≥2 years |
| **Sirolimus** | adversarial safety comparator | Reduce the damage of aneuploidy through mTOR/autophagy **without correcting BUBR1** | Approved, paediatric exposure well characterised |

Plus three controls: **vehicle** (the only true negative control), **ca-HSF1** (contextual
positive control, genetic) and **HSP70 overexpression** (secondary mechanistic comparator).

Read structurally, that is **two candidate pharmacologic hypotheses (azithromycin,
arimoclomol) plus one adversarial comparator (sirolimus)**. Sirolimus is not competing: it is
there to demonstrate why rescuing more aneuploid cells is not automatically a good outcome.

**We nominate pharmacologic arms for preclinical discrimination, not a therapeutic winner and
not a clinical recommendation.** None of these is proposed for administration to any patient.

**There is no ranking, no score and no winner among them**, and that is a deliberate scientific
decision, not an evasion. Combining heterogeneous evidence into a single number requires a preregistered
method for doing so, and no such method exists here. The three arms are not competing for
first place; each one **teaches something different by failing**, and each carries a discard
rule written in advance.

## 2 · The variant mechanism this is built on

Track 1 nominates **candidate compound-heterozygous `BUB1B`** (MVA1, OMIM 257300): a
truncating allele that reaches Likely Pathogenic in research curation, and a missense allele
that remains a VUS. **The phase is unresolved** — no parental samples — so the biallelic
configuration is a candidate, not a demonstrated finding, and everything downstream inherits
that caveat.

`BUB1B` encodes BUBR1, a core component of the spindle assembly checkpoint. Its C-terminal
domain is an unusual **pseudokinase**: catalysis is dispensable for error-free segregation, but
residues that bind ATP in conventional kinases are needed for its conformational stability
([Suijkerbuijk et al. 2012](https://doi.org/10.1016/j.devcel.2012.03.009)), and the domain
itself promotes kinetochore PP2A-B56 recruitment, checkpoint silencing and chromosome alignment
([Gama Braga et al. 2020](https://doi.org/10.1016/j.celrep.2020.108397)). For this genotype,
protein abundance and stability is a leading therapeutic hypothesis, but direct functional
impairment of the pseudokinase domain remains an alternative that must be tested at matched
protein abundance. Biallelic loss produces mosaic variegated aneuploidy, in which different
cells carry different chromosome complements.

Two loss mechanisms, and they may need different interventions:

- The **truncating** allele is predicted to lose its transcript to nonsense-mediated decay. Whether
  its truncated product would work if it existed is **not known**: of two published MVA
  truncations nearby, one plasmid-expressed product restored checkpoint, segregation and
  alignment and the other was unstable ([Suijkerbuijk et al. 2010](https://doi.org/10.1158/0008-5472.CAN-09-4319)).
  Retested at kinetochore levels matched to wild type, that "functional" truncation still
  showed reduced PP2A-B56 recruitment, slower checkpoint silencing and more misaligned
  chromosomes (Gama Braga et al. 2020): rescue depends on the endpoint measured. Whether the
  exact truncated product of this case works, on a hierarchy of endpoints, comes **before**
  readthrough: recovery would be compatible with abundance being a dominant bottleneck
  for the measured endpoints under those conditions, not proof of complete function. Azithromycin stays in the portfolio as the only arm aimed at this allele, pending
  that answer.
- The **missense** allele is hypothesised to destabilise the protein (the T2-A route), but it may
  also impair the pseudokinase domain directly. A proposed expression-response comparison must measure total and kinetochore abundance
  separately, then molecular function and distal outcomes. Recovery does not automatically
  exclude additional unmeasured defects. See the [figure-by-figure audit](../research/BUBR1_ENDPOINT_AUDIT.md).

The premature stop codon is **UGA with adenine at +4**, and the two halves of that fact
point in opposite directions. UGA is generally readthrough-permissive. The +4 adenine is
**less favourable than C or U**, so it is not part of a favourable context.

But the decisive point is that **neither half licenses a prediction**. Readthrough efficiency
depends on the *extended* stop-codon context, not on the +4 nucleotide alone, and that context
is what has to be measured (DOI 10.1038/s41467-024-46703-z). So: permissive at the codon, less
favourable at +4, and **not predictable without an assay**.

Two earlier drafts of this paragraph were wrong in opposite directions. The first called the
context "genuinely favourable", which overstated it. The second gave a strict ordering,
C > U > G > A, and attributed it to a source that does not establish it; recent human-cell data
group A and G together rather than ranking A last. Both are corrected here.

EXP-029 adds a preregistered in silico estimate of this PTC context under the G418-trained Assay
model. A4a is SCORABLE and falls in the LOWER tercile (19.09th percentile among UGA references;
n=2064). A4b provides a separate adverse axis: none of the three preregistered UGA readthrough
products supported by external experimental systems (R/W/C) restores the wild-type residue; all
remain NON-WT FULL-LENGTH PRODUCT · FUNCTION UNKNOWN.

Together, these results computationally weaken the allele-directed readthrough hypothesis, but they
do not eliminate the azithromycin arm. The A4a model is G418-conditioned, not azithromycin-specific;
mutant-transcript availability (A4c) and actual product function (A5) remain unmeasured.

## 3 · The method: eight bridges, ten dimensions, and the gaps are the result

The claim *"this gene causes the disease, therefore this drug will help"* is not one claim. It
is a chain, and a chain is only as good as its weakest link. So it was decomposed into **eight
explicit bridges**, each audited across **ten dimensions of evidence**, with a closed
vocabulary (`DIRECT` / `NEAR` / `GENETIC` / `CONTRADICTORY` / `ABSENT`) and one hard rule
enforced at build time: **no non-absent cell may exist without a source.**

Result: **80 cells, of which 61 are empty.**

Two things that matrix is not, and both matter. **The 80 cells are not 80 independent pieces of
evidence** — a single paper fills several of them, and **4 distinct publications plus 2 internal
project artefacts** are the honest
denominator. And **an empty cell records that no qualifying evidence was found in our bounded
literature search**, not that the world has never looked; the search was scoped to the bridges
named here, and a wider one could fill cells we left empty.

| Bridge | Claim | Status |
|---|---|---|
| 1 | This patient's variant destabilises BUBR1 | Only one non-empty cell, and it is `NEAR`, not `DIRECT` |
| 2 | Destabilised BUBR1 lowers protein level | Supported, but from other alleles |
| 3 | Raising chaperone capacity raises BUBR1 | **`NEAR` in two dimensions; bridge unresolved.** Basal dependence is established; the gain direction is unmeasured |
| 4 | More BUBR1 means less chromosome instability | Partial |
| 5 | Aneuploidy causes proteotoxic and mitochondrial stress | Supported |
| 6 | Raising HSP levels rescues that stress | `GENETIC` only |
| 7 | **Pharmacological co-induction reproduces the rescue** | **The translational gap.** `CONTRADICTORY` in three dimensions |
| 8 | **The same intervention affects CIN and clonogenic survival** | **The safety gap. Empty in all ten dimensions: no qualifying evidence was found in our bounded literature search** |

The empty cells are the finding. A therapeutic argument that looks strong usually looks that
way because nobody drew the chain.

## 4 · The counter-evidence, stated first

Verified findings that constrain the preferred hypothesis. They are not all counter-evidence: bridge 3 was reclassified from `CONTRADICTORY` to `NEAR` because necessary-direction evidence is not evidence against.

**Bridge 3 is unresolved, not contradicted.** Inhibiting HSP90 *collapses* missense BUBR1
mutants (PMID 20516114). That demonstrates **basal dependence** on chaperones — the same
direction of dependence, not the opposite one. It does not demonstrate that *adding* chaperone
capacity raises BUBR1, because capacity may already be saturated. Removing a support and adding
one are different experiments, and only the first has been done.

An earlier version of the matrix classified these two cells as `CONTRADICTORY`. That was our
own logical error: absence of evidence in the gain direction is not evidence against. They are
now `NEAR` — necessary-direction evidence — and bridge 3 is **unresolved**. The correction
removes a mark against our own preferred route, which is why it is stated here rather than left
in a diff.

**Bridge 7 has a direct counterexample.** In NPC1 I1061T fibroblasts (PMID 34481829, DOI 10.1016/j.jlr.2021.100114),
HSP70 overexpression **did** reduce cholesterol storage, but **arimoclomol did not reproduce
it up to 500 µM** over 72–120 hours, and did not itself raise HSP70. The genetic rescue
worked; the pharmacological one did not.

**But that does not close chaperone biology.** In the very same study, **inhibiting HSP90 did
work**, by raising HSP70. A failure of one compound kills the translation *arimoclomol → HSP
co-induction*, not the chaperone arm. An earlier draft of this project overstated that, and
the correction is recorded.

**The heat-shock response is itself impaired in aneuploid cells**, running at 50–60 % of
control (PMID 25205676). What rescued was **constitutively active HSF1** — a genetic
perturbation. And even that **depended on the karyotype**: one aneuploid line did not respond.
The positive control is not universal, and that is declared.

## 5 · The three arms, and what each one falsifies

**Before the arguments, the distances.** Every one of these results comes from a system that is
not this patient, and the gap is the single most important thing to see. A figure that shows
role and provenance does not show transfer distance, so it is written out here.

| Arm | System actually studied | Intervention / dose | Outcome measured | What it supports | What it does **not** show |
|---|---|---|---|---|---|
| **Azithromycin** | Patient-derived lines in *other* genetic contexts (`ATM`, `MECP2`, `SMN`, `APC`) | Absolute active concentration **not published in verifiable form**; the claim is "100-fold lower than earlier compounds" | Readthrough of a premature stop | Mechanistic plausibility of macrolide-induced readthrough | Readthrough **in `BUB1B`**, at any concentration, in any cell |
| **Arimoclomol** | Human NPC1 I1061T fibroblasts (PMID 34481829) | Up to 500 µM, 72–120 h | HSP70 induction and cholesterol storage | A **verified pharmacological counterexample**: the genetic rescue worked and the drug did not | Anything in MVA, in aneuploid cells, or about BUBR1 |
| **Sirolimus** | *Drosophila* CIN/MVA model, larvae | Rapamycin 40 µM | Aneuploid neuroblast number; Pros+ cells; brain size | Partial rescue of the stem-cell compartment | Restoration of the tissue outcome, human relevance, or any safety claim |
| **ca-HSF1** *(control)* | Isogenic human aneuploid cells | Genetic, constitutively active HSF1 | Aggregates, p62–TOMM20 colocalisation | That the proteostasis biology can work in aneuploid cells | That it works in every karyotype — the rescue **depended on karyotype** |

**None of these systems is a `BUB1B` patient cell.** That is not a hedge, it is the reason the
portfolio exists: the first experiment is what would close the distance.

### Azithromycin — the only arm aimed at this patient's own allele

Macrolides induce readthrough of premature termination codons in patient-derived lines
carrying `ATM`, `MECP2`, `SMN` and `APC` mutations, and azithromycin is active at a
concentration 100-fold lower than earlier compounds (PMID 26620677, DOI
10.1007/s00109-015-1364-1).

**Direct evidence in `BUB1B`: none. In MVA: none.** Readthrough is sequence-dependent and no
one has tested this gene. UGA is generally readthrough-permissive; the +4 A is less favourable
than C or U; and the extended context makes the response unpredictable without an assay
(DOI 10.1038/s41467-024-46703-z).

**Exposure, now quantified rather than assumed.** Paediatric serum Cmax is 0.216 µg/mL at ages
1–5 and 0.383 µg/mL at 5–15 on 10 mg/kg day 1 then 5 mg/kg days 2–5, and 0.5 ± 0.4 µg/mL on
12 mg/kg/day for five days in children weighing ≤41.7 kg (FDA ZITHROMAX label). At
C38H72N2O12 = 749.0 g/mol that is **0.29, 0.51 and 0.67 µM**. The 68–72 h terminal
half-life quoted on the same label comes from the **adult** pharmacokinetic studies; the
paediatric tables give Cmax and AUC, not a paediatric half-life, and the distinction is
kept because a half-life is not transferable across age groups by assumption.

**That number alone does not settle the arm, and it matters to say why.** Two quantities decide
it and neither could be verified here:

1. **The readthrough EC50 for azithromycin is not published in a form we could verify.** The
   literature gives the relative claim — active at a concentration 100-fold lower than earlier
   compounds (PMID 26620677) — without the absolute value, and three reviews repeat the ratio
   without the number.
2. **The magnitude of intracellular accumulation is unverified**, and it matters more than the
   serum figure, because the ribosome is intracellular. The label documents extensive tissue
   distribution but states no fold-difference, and no specific factor was verified here.

Without both, the exposure-to-potency ratio cannot be computed. **Paediatric serum Cmax is
submicromolar. Whether that is sufficient for readthrough cannot currently be determined**,
because neither the relevant intracellular exposure nor an experimentally anchored potency
threshold for this sequence context is available.

An earlier draft of this report wrote that submicromolar exposure is "low for a readthrough
agent". That was an overclaim: it asserts a potency threshold that the cited evidence does not
establish. Measuring both quantities is precisely what a first experiment would do.

**A second safety consideration, and it is conditional, not established.** The label warns in
section 5.4 of QT prolongation and torsades de pointes with macrolides including azithromycin,
and names **uncorrected hypokalaemia or hypomagnesaemia** among the factors that raise that
risk.

**Nephrocalcinosis alone does not establish either electrolyte abnormality, nor a renal
tubulopathy.** It is a heterogeneous finding: it occurs with tubular disorders, but also with
idiopathic hypercalciuria, hyperoxaluria, metabolic disturbances and iatrogenic causes. This
becomes a patient-specific concern **only if** clinical evaluation demonstrates electrolyte
wasting or an associated tubular disorder. An earlier draft presented the collision as if the
phenotype established it; it does not.

The paediatric profile is otherwise well characterised (diarrhoea
1.8–5.8 %, vomiting 1.1–5.6 %, abdominal pain 1.2–3.4 %), with infantile hypertrophic pyloric
stenosis reported in neonates treated up to 42 days of life. **No clinical recommendation
follows from any of this.**

*Discarded if* PTC transcript abundance is too low to permit detectable rescue at attainable
exposure, if readthrough does not exceed noise at attainable exposure, or if the inserted
amino acid does not restore BUBR1 function. Note that NMD and readthrough **compete**: this is
not an all-or-nothing switch, and an earlier draft wrote the first clause as though degradation
simply precluded readthrough.

### Arimoclomol — informative by failing

This is the arm most likely to be misread as a favourite. It is not. It is in the portfolio
**because bridge 7 is `CONTRADICTORY` and someone has to resolve it.**

Paediatric steady-state Cmax is 523 ± 194 ng/mL, trough 206 ± 60 ng/mL (MIPLYFFA label). Using
the free-base mass, C14H20ClN3O3 = 313.78 g/mol, Cmax corresponds to **≈1.67 µM** — worth
confirming that the assay quantifies free base rather than salt before fixing an exposure
window. In the NPC study, arimoclomol failed at concentrations far above that.

The safety profile collides with this specific phenotype: weight loss is among the most
frequent reactions, and mean serum creatinine rises 10–20 %, reversible on discontinuation. It
inhibits OCT2, whose endogenous substrate is creatinine. **This patient has failure to thrive
and nephrocalcinosis.** That collision is recorded, not smoothed over.

*Discarded if* it does not raise HSP at attainable exposure, or if it raises HSP without
raising BUBR1. **That does not discard chaperone biology as a whole**: the HSP90 route stays
open in the very study that discards arimoclomol.

### Sirolimus — the adversarial comparator, and the reason the corridor exists

This is the only arm with **direct pharmacological evidence in a *Drosophila* CIN model** —
the qualifier travels with the claim, because "direct evidence" unqualified reads far too close
to human or patient data. And that evidence is already partly negative in the way that matters
most.

Rapamycin at 40 µM, fed to larvae in a *Drosophila* CIN/MVA model, rescued the **number of
aneuploid neuroblasts** — but **did not adequately restore Pros+ cells or brain size** (DOI
10.1038/s41467-026-70521-0). The equivalent genetic perturbations of TOR and autophagy (Rheb
depletion, heterozygous *Tor* mutants, Atg1 overexpression) give the same partial rescue.

It **recovers the stem-cell compartment without recovering the tissue outcome.** That is a
signal that the corridor is real: you can improve the survival of unstable cells without
improving the organism. The authors themselves note that TOR inhibition and autophagy may
negatively affect the proliferative capacity of those highly aneuploid neuroblasts, which is
the same tension from the other side.

Sirolimus is an immunosuppressant in a child with tumour predisposition and failure to thrive.
**That collision is exactly why it is included** — not as a candidate, but as the boundary
marker.

*Discarded as a therapeutic candidate* the moment it increases CIN, micronuclei, segregation
errors or clonogenic survival. **As an adversarial comparator it is not discarded: there, its
failure is the result.**

> A note on how this arm was corrected. An earlier version of the candidate table asserted
> that the pharmacological evidence for this route was zero, based on reading only the bioRxiv
> preprint, which describes genetic interventions alone. The published article **does** include
> rapamycin administration. The claim was false and has been corrected; the preprint/published
> discrepancy is documented in the table itself, because anyone verifying from the preprint
> would reach the same wrong conclusion.

## 6 · The Safe Rescue Corridor

The organising idea, and the reason this is not a standard repurposing pitch.

**The efficacy signal and the oncological risk signal are the same measurement.** If an
intervention preferentially rescues the *most* aneuploid cells, that is simultaneously
evidence that the mechanism is the proposed one **and** evidence that the clonogenic survival
of genomically unstable cells has been improved — in a child who already has a tumour
predisposition syndrome.

So any candidate must be shown to move the system toward a corridor in which chromosome
instability falls *and* clonogenic survival does not rise. Bridge 8 asks exactly this, and it
is **empty in all ten dimensions**. Our bounded literature search found no qualifying evidence
for it, for any of these compounds, in any system.

The corridor is a shared rule, not an invention of this project. Another public repository
from this hackathon defines a true MVA rescue in the same terms: fewer segregation errors per
completed mitosis, with cell-cycle transit, clonogenic recovery and transformation risk checked
alongside (§9, prior art). We adopt it as good practice and do not claim it as new.

## 7 · The experiment

Isogenic aneuploid/euploid pair, ± candidate compound, with:

- a **genetic positive control** (constitutively active HSF1), because without it a negative
  result cannot distinguish "the drug did not reach" from "the biology does not work in
  aneuploid cells";
- a **mandatory readout of whether the drug induces HSP at all**, because the counterexample
  shows it may not, and without measuring it you cannot tell whether the drug failed or the
  hypothesis did;
- **CIN and clonogenic survival measured simultaneously**, because that is the corridor.

Four outcomes are prescribed in advance. **Two of them kill the hypothesis.** That is what
makes it falsifiable rather than merely plausible.

## 8 · What is nominated, and what is not

**Nominated:** three pharmacologic arms for preclinical discrimination — two candidate
hypotheses and one adversarial comparator — each with its discard rule written in advance.

**Not nominated:** a therapeutic winner, and any clinical recommendation.

The distinction is not a hedge, it is the drug gate. Promotion from *experimental arm* to
*therapeutic candidate* requires five conditions together: approved status · mechanistic
proximity to a **named** bridge · evidence **from that** bridge · a falsifiable rescue
prediction · an explicit counter-test for CIN and tumour risk.

**No arm meets all five today**, and bridge 8 is empty for all of them. The portfolio exists
precisely to find out which one could.

## 9 · Innovation, and what is genuinely new here

**The bridge matrix as an instrument.** Decomposing a therapeutic argument into N bridges × 10
evidence dimensions, with a closed vocabulary and a build-time rule that no non-absent cell may
lack a source, turns "the mechanism is plausible" into a map with 61 measurable holes.

**Roles instead of a ranking.** `ALLELE` / `SENTINEL` / `ADVERSARIAL` / `CONTROL` replaces the
wrong question ("which is best?") with the useful one ("what dies if each fails?").

**A preregistered simulation, and our own falsification of how we first explained it.**
Under simulation, balanced variegated homolog gains **recenter the signed aggregate BAF** toward
0.5: the power of the signed statistic falls from **0.980** to **0.050** — chance — when the
homolog direction is mixed, and matching the depth does not move it.

We first published a second, stronger claim: that the power collapse of the **site-wise absolute**
statistic `|BAF − 0.5|` was caused by that same cancellation. **Our own adversarial audit falsified
it.** An absolute statistic is blind to sign, so cancellation cannot move it; a **post-hoc
diagnostic ablation** (EXP-015c, designed *after* the audit found the problem, so not
preregistered) shows **no evidence of a direction effect** — 0.520 and 0.505 at matched depth,
which at 200 replicates is the same result — while depth changes everything. The collapse *below* alpha came from comparing a depth-sensitive statistic
against a null at a different depth, because the extra copy raises coverage to (2+f)/2. That is a
confound between homolog-direction mixing and copy-number-dependent depth, not a coding slip: more
copies really do produce more reads.

Four limits travel with what is left, and none is optional. The recentering was reproduced **under
simulation**, not observed in patient data. **The comparator is not MoChA** and carries no
long-range phasing. **No superiority over a phased method is demonstrated**; that branch stays
`UNVALIDATED · PARKED`. And the depth-normalised statistic that removes the confound in simulation
is **not** a validated detector. The depth-normalised statistic removes the depth sensitivity
observed for the absolute-deviation statistic *in this simulation*; what supports the revised
reading is the ablation's combined pattern, not that statistic on its own.

### Prior art, and what we do not claim

Every component of the rescue logic in this report has precedent. We list it so that the
design can be judged on what it assembles, not on what it appears to invent.

| Idea | Precedent | Relation to this project |
|---|---|---|
| Learn a protective mechanism from resistant cells and transfer it to vulnerable ones | Resistant motor neurons led to IGF-2 in ALS ([Allodi et al. 2016](https://doi.org/10.1038/srep25960)) and to GDF15 in SMA ([Nichterwitz et al. 2020](https://doi.org/10.1101/gr.265017.120)); single-cell survival profiling in retina ([Tran et al. 2019](https://doi.org/10.1016/j.neuron.2019.11.006)); intracellular CFH in multiple sclerosis ([Mayer et al. 2026](https://doi.org/10.1038/s41586-026-10981-y)) | Established paradigm; not claimed |
| A patient's own clones as a natural experiment | Somatic genetic rescue: *EIF6* suppressor mutations in Shwachman-Diamond syndrome, proposed as a model for suppressor mimics ([Tan et al. 2021](https://doi.org/10.1038/s41467-021-24999-5)); adaptive and maladaptive rescue events coexisting in the same SAMD9/9L patients ([Sahoo et al. 2021](https://doi.org/10.1038/s41591-021-01511-6)) | Established; in those cases the rescued cells changed genotype |
| Aneuploid cells are selected against in regenerating tissue | *Bub1b* hypomorphic mice ([Pfau et al. 2016](https://doi.org/10.1101/gad.278820.116)) | A persisting cell is not necessarily a protected cell |
| MVA cells can be rescued experimentally | Ectopic BUBR1 restored checkpoint activity in cells from patients with biallelic mutations ([Suijkerbuijk et al. 2010](https://doi.org/10.1158/0008-5472.CAN-09-4319)) | Defines what a true functional rescue looks like |
| Chromosomal instability as a discovery platform | Patent application WO2025101836A1 (Dartmouth; pending) induces aneuploidy in pluripotent stem cells and names MVA among the conditions it can model | Induced, not patient-derived, variation |
| Rescue measured as fewer errors per completed mitosis, with clonogenic and transformation checks | The public hackathon repository `dhruv575/mva-evidence-lanes` (published 28 August 2026, `wiki/translation/rescue-assay-matrix.md`) | Our corridor entered this repository on 31 August 2026. Likely independent, but not first; not claimed |

**What we do not claim.** That studying resilient cells is new, that using a patient's mosaic
as a clue is new, that transferring protective mechanisms is new, or that our safety corridor
is new.

**What remains a candidate, pending a completed audit of papers, patents and repositories.**
Using the chromosomal heterogeneity that MVA keeps generating inside one patient as the source
of a protective hypothesis, and accepting that hypothesis only if transferring it lowers new
segregation errors per completed mitosis at matched proliferation. It is a proposal: this project
has one bulk blood genome and has measured no cell-level heterogeneity. The observed mosaic in
any sample is shaped by what division generates, what selection removes and what tissue and
method are used to look (Track 1 report, §7b), and bulk blood cannot separate the three. So the
honest form of the idea is a question: *can the patient become the screen?*

## 10 · Scalability

Measured, not asserted: **59 of 115 modules in `src/`, 9 411 of 22 723 lines (41 %), contain no
reference to this case at all** (`python src/scalability_census.py`).

**Read that number for what it is.** It says *41 % of the current codebase is case-agnostic
under a conservative lexical census*. It does **not** say the project is 41 % scalable. Real
scalability also asks which inputs can be substituted, how many modules depend on `BUB1B` or on
the MVA phenotype specifically, and which parts reuse generic HPO and VCF machinery — none of
which a text search can answer. Treat it as a **technical proxy**, not a measure of scalability.
It is a floor rather than a ceiling, since the measure is textual and many of the remaining
modules name the case only in figure titles. These five numbers are recomputed by
`src/verify.py`, which fails if this report and the census drift apart — a hand-written number
under the words *measured, not asserted* goes stale in silence.

What transfers is the **method**: the frozen preregistered ranking that is never rewritten, the
bridge matrix, the role-based portfolio, the cheap-falsifier competitor audit
(frequency → zygosity → mechanism → replication), the phenotype polarity rule, and the
two-axis figure metadata.

What does **not** transfer is stated too: the BAF cancellation result depends on mosaicism being
*variegated* and does not apply to clonal mosaicism; the readthrough arm requires a premature
stop codon; the mitochondrial readout is an uncalibrated prototype. Full detail in
`docs/SCALABILITY.md`.

**The honest limit: none of this has been tested on a second patient.** It is an architectural
claim backed by a dependency census, not by a second run.

## 11 · Reproducibility

```bash
pip install -r requirements.txt
python src/verify.py
```

Checks include unit tests, module imports (discovered rather than
hand-listed), published figure counts recomputed from the executed notebooks, both Track 2
matrices, the contradiction count, the privacy scanner and the superseded-claim auditor.

`research/track2_evidence.tsv` and `research/track2_candidates.tsv` are versioned and
machine-checked: roles come from a closed vocabulary, the header count must match the rows,
and **every claim across five columns — including counter-evidence, exposure and safety — must
carry a published identifier or an explicitly declared gap.** That last rule was added after a
false claim about pharmacological evidence passed with everything green, because the checker
only looked at the other file. A control that does not cover the new artefact does not protect
against the new error.

## 12 · AI use disclosure

Required by the submission rules.

| | |
|---|---|
| **Provider** | Anthropic |
| **Interface** | Claude Code |
| **Model** | Claude Opus family (including Claude Opus 5.5) |
| **Plan / tier** | Claude Pro (consumer plan) |
| **Data-handling setting** | Model-training on user content **disabled** in the account settings |

**What the assistant did:** wrote and refactored analysis code, figure modules and notebooks;
drafted documentation; performed literature searches; audited the repository for internal
inconsistencies and stale numbers.

**What it did not do:** it did not choose the final therapeutic candidate, and it did not
commit or push to the repository. The project's operating rules define explicit stop
conditions, and the choice of therapeutic candidate is one of them; the portfolio framing in
this report was decided by the maintainer.

**Second provider: OpenAI, for illustrations only.**

| | |
|---|---|
| **Provider** | OpenAI |
| **Interface** | ChatGPT, image generation |
| **Plan / tier** | ChatGPT Plus (consumer plan) |
| **Data-handling setting** | Model-training on user content **disabled** in the account settings |
| **Use** | The conceptual editorial diagrams (`docs/assets/mosaic-*.png`). No patient data was provided. Each image was reviewed against the reports before use and is captioned as an AI-generated schematic (`docs/assets/EDITORIAL_CAPTIONS.md`); quantitative evidence stays in the code-generated figures |

**Patient data and external services.** The assistant reviewed local project documents,
user-supplied figures and selected tool outputs, under the account settings above. This is
not a claim of zero disclosure to an AI provider: derived results were visible to the
assistant during the work.
Raw sequencing files are excluded from version control, while some internal technical
figures contain case-specific locus information. The earlier project record documents
**AlphaGenome** receiving patient-derived values: a variant shortlist and never
the VCF. It runs in an isolated virtual environment, its outputs are cached, and the call is
not repeated on a normal build. See `docs/03_ALPHAGENOME_ASSESSMENT.md`.

## 13 · Acknowledgements and data citation

Carried out for the Rare Disease, Real Kid: MVA Hackathon 2026, organised by **Sage
Bionetworks**, the **MVA Society**, **Hugging Face**, **BEACON**, **AWS** and **Anthropic**.

> **Dataset citation: to be completed before submission**, using the reference provided on the
> hackathon Synapse page. It was not retrieved in this session and is therefore not
> transcribed here, per the project's rule against unverified identifiers.

**Dataset provenance.** The hackathon dataset is distributed through the Synapse project [`syn76251147`](https://www.synapse.org/Synapse:syn76251147/wiki/642892). The **formal citation is not reproduced here**: it is not visible on the public page without an authenticated session, and this project does not write a reference it has not read. It must be copied verbatim from the authorised session before submission.

**Privacy.** This report omits variant coordinates, HGVS strings, genotypes and sample
identifiers. Internal technical figures elsewhere need review before any public release.
No attempt was made to locate the family.

## 14 · Verified sources

| Claim | Identifier |
|---|---|
| Macrolide readthrough of PTCs; azithromycin active at 100× lower concentration | PMID 26620677 · DOI 10.1007/s00109-015-1364-1 |
| HSP70 overexpression rescued, arimoclomol did not up to 500 µM and did not induce HSP70; HSP90 inhibition did work | PMID 34481829 · DOI 10.1016/j.jlr.2021.100114 |
| Rapamycin 40 µM partially rescued a *Drosophila* CIN/MVA model without restoring Pros+ cells or brain size | DOI 10.1038/s41467-026-70521-0 |
| ca-HSF1 reduced aggregates in isogenic human aneuploid cells; rescue depended on karyotype | DOI 10.1038/s41467-025-60857-4 |
| Heat-shock response impaired to 50–60 % in human aneuploid cells | PMID 25205676 |
| HSP90 inhibition collapses missense BUBR1 mutants | PMID 20516114 |
| Arimoclomol paediatric exposure, safety profile, OCT2 inhibition, mechanism in NPC unknown | MIPLYFFA label |
| Azithromycin paediatric Cmax, half-life, adverse reactions, neonatal IHPS, and the section 5.4 QT / torsades warning naming uncorrected hypokalaemia and hypomagnesaemia | FDA ZITHROMAX label |
| Aneuploid haematopoietic cells show reduced fitness; regenerating tissues of *Bub1b* hypomorphic mice are largely euploid | PMID 27313317 · DOI 10.1101/gad.278820.116 |
| Resistant motor neurons identify IGF-2 as protective in ALS | PMID 27180807 · DOI 10.1038/srep25960 |
| Resilient retinal ganglion cell types identified by single-cell profiling, with functional tests | PMID 31784286 · DOI 10.1016/j.neuron.2019.11.006 |
| Resistant SMA motor neurons identify GDF15, which rescues vulnerable human motor neurons | PMID 32820007 · DOI 10.1101/gr.265017.120 |
| Intracellular CFH correlates with and mediates neuronal resilience in multiple sclerosis | PMID 42686909 · DOI 10.1038/s41586-026-10981-y |
| Somatic *EIF6* events rescue the germline defect in Shwachman-Diamond syndrome | PMID 34413298 · DOI 10.1038/s41467-021-24999-5 |
| Somatic genetic rescue in SAMD9/9L: maladaptive and adaptive events, often competing in the same patient | PMID 34621053 · DOI 10.1038/s41591-021-01511-6 |
| Lymphocyte cultures and buccal FISH give different aneuploidy pictures in MVA patients without detected *BUB1B* mutations | PMID 18548531 · DOI 10.1002/ajmg.a.32315 |
| CIN-inducing platform for pluripotent stem cells; MVA named as a modelled condition | WO2025101836A1 (Google Patents, pending) |
| Rescue defined as fewer errors per completed mitosis, with clonogenic and transformation checks | github.com/dhruv575/mva-evidence-lanes, `wiki/translation/rescue-assay-matrix.md`, created 2026-08-28 |

No identifier appears in this report that was not verified. Where a fact could not be verified,
it is written as a declared gap rather than cited.

## 15 · Licence

Documentation, notebooks and figures: CC BY 4.0. Code: dual-licensed **MIT OR CC BY 4.0**, so
the whole submission is available under CC BY as the rules require. See `LICENSE` and
`LICENSE-DOCS`.

<!-- methods-form:start -->

## Appendix · Methods description (official hackathon form)

Answers to the organisers' methods-description template, reproduced here because the submission accepts a single report file.

**Team name**

mosaic-rescue

**Please describe your approach in detail (how you went from variant/mechanism to candidate medication(s)).**

From variant to candidates by decomposition, not by association. (1) Mechanism from Track 1: candidate compound-heterozygous BUB1B (MVA1) — a truncating allele with predicted NMD but an untested exact protein product, and a missense hypothesised to affect abundance and/or function. BUBR1 pseudokinase function requires testing expression, kinetochore localization and layer-specific outcomes; abundance is a leading hypothesis, not an established exclusive mechanism. (2) The claim 'this gene causes the disease, therefore this drug helps' was split into 8 explicit bridges (variant → BUBR1 stability → protein level → chaperone capacity → CIN → aneuploidy stress → pharmacological co-induction → effect on CIN and clonogenic survival), each audited over 10 evidence dimensions with a closed vocabulary (DIRECT / NEAR / GENETIC / CONTRADICTORY / ABSENT) and a build-time rule that no non-absent cell may lack a source: 80 cells, 61 empty. (3) Candidates were chosen for ROLES, not ranked: azithromycin (allele-directed: readthrough of the premature stop codon), arimoclomol (falsification sentinel: heat-shock co-induction → BUBR1 abundance) and sirolimus (adversarial safety comparator: mTOR/autophagy without correcting BUBR1), plus vehicle, a genetic positive control (constitutively active HSF1) and HSP70 overexpression. (4) A drug gate of five joint conditions (approved status, proximity to a named bridge, evidence from that bridge, a falsifiable rescue prediction, an explicit CIN/tumour-risk counter-test); no arm meets all five today. (5) A 'safe rescue corridor': any arm must lower chromosome segregation errors WITHOUT raising clonogenic survival of unstable cells, measured together in an isogenic aneuploid/euploid assay with four pre-declared outcomes, two of which kill the hypothesis. No clinical recommendation is made.

**(required) If commercially-available Generative AI was used, record the provider, the plan or tier, and the relevant setting in your methods description. A line is enough, for example, "Anthropic API, Claude Sonnet, commercial terms, no training on customer content."**

Anthropic — Claude Pro (consumer plan), used through Claude Code with Claude Opus models; model-training on user content disabled in the account settings. Used for code, documentation and literature search; the portfolio framing and candidate roles were decided by the team. OpenAI — ChatGPT Plus (consumer plan), image generation for the conceptual editorial diagrams only; model-training on user content disabled; no patient data provided.

**Was candidate identification automated (e.g., via a drug-target database query or LLM-assisted search), or primarily manual literature review and expert curation?**

Primarily manual literature review and expert curation, with assistant-supported PubMed searches. The evidence and candidate matrices are machine-checked (research/track2_evidence.tsv, research/track2_candidates.tsv via src/verify.py): closed role vocabulary, and every claim — including counter-evidence, exposure and safety — must carry a published identifier or an explicitly declared gap.

**Please describe any manual literature review or expert curation in detail.**

Each bridge was searched for direct, near, genetic or contradictory evidence and every non-empty cell was tied to a verified identifier (4 distinct publications + 2 internal artefacts). Counter-evidence was recorded first: arimoclomol did not reproduce HSP70-mediated rescue up to 500 µM in NPC1 I1061T fibroblasts and did not induce HSP70 (PMID 34481829), while HSP90 inhibition did; the heat-shock response runs at 50–60 % in aneuploid cells (PMID 25205676); HSP90 inhibition collapses missense BUBR1 mutants (PMID 20516114). Two of our own errors were corrected and recorded (bridge 3 reclassified from CONTRADICTORY to NEAR; a false claim of zero pharmacological evidence for rapamycin, corrected after reading the published article rather than the preprint). Exposure and safety were checked against the FDA labels (ZITHROMAX, MIPLYFFA), including patient-relevant collisions (QT/electrolytes; OCT2 and creatinine with nephrocalcinosis).

**Please state whether you relied solely on publicly available drug/target databases and literature (preferred), or whether proprietary data sources were also used.**

Publicly available literature and public drug labels only. No proprietary data sources.

**Please describe the public data sources used in detail (e.g., DrugBank, ChEMBL, ClinicalTrials.gov, OMIM, PubMed literature search).**

PubMed / peer-reviewed literature: PMID 26620677 (macrolide readthrough of PTCs; azithromycin), PMID 34481829 (arimoclomol vs HSP70 in NPC1 fibroblasts), PMID 25205676 (impaired heat-shock response in aneuploid cells), PMID 20516114 (HSP90 dependence of missense BUBR1), DOI 10.1038/s41467-025-60857-4 (ca-HSF1 in isogenic aneuploid cells), DOI 10.1038/s41467-026-70521-0 (rapamycin in a Drosophila CIN/MVA model), DOI 10.1038/s41467-024-46703-z (stop-codon context and readthrough), plus MVA/BUB1B literature (Hanks 2004, Matsuura 2006, Wijshake 2012). OMIM 257300 (MVA1). FDA prescribing information for ZITHROMAX and MIPLYFFA.

**Please describe any proprietary data sources used in detail.**

None.

**How did you characterize the variant's mechanism (e.g., loss-of-function vs. gain-of-function, pathway disrupted, downstream biological consequence)?**

Loss of function by two routes that need different interventions: the truncating allele is a premature stop (UGA, adenine at +4) predicted to trigger NMD — only an allele-directed approach (readthrough) can recover anything from it, and its efficiency cannot be predicted without an assay; the missense is hypothesised to destabilise BUBR1 (a proteostasis problem). Pathway: BUBR1 is a core spindle-assembly-checkpoint component; reduced dose weakens the checkpoint → chromosome segregation errors → mosaic variegated aneuploidy → proteotoxic and mitochondrial stress in aneuploid cells, with tumour predisposition. Key consequence for drug selection: the efficacy signal (better survival of aneuploid cells) and the oncological risk signal are the same measurement, hence the safe-rescue corridor. The phase of the two alleles is unresolved, so the biallelic mechanism is a candidate and every downstream step inherits that caveat.

**Please provide an estimate of time or effort spent on this analysis (if possible).**

Not formally timed. The work ran iteratively during the hackathon (late August–September 2026) in the same repository as Track 1; the Track 2 matrices are rebuilt and machine-checked in under a second by src/verify.py.

**Provide a method abstract (up to 500 words). Please include strengths and limitations of your approach as well as methodological detail.**

MOSAIC RESCUE Track 2 proposes a falsification-first repurposing portfolio for candidate compound-heterozygous BUB1B mosaic variegated aneuploidy, not a therapeutic winner. Because BUBR1 is a pseudokinase, the lever is protein dose and stability. We decomposed the therapeutic argument into eight bridges from variant to clinical-relevant effect and audited each across ten evidence dimensions with a closed vocabulary and a sourcing rule enforced at build time. Of 80 cells, 61 are empty; the empty cells are the finding. The translational bridge (pharmacological co-induction) is contradictory in three dimensions, and the safety bridge (effect on chromosome instability and clonogenic survival) is empty in all ten.

Three approved compounds are nominated for preclinical discrimination in three roles: azithromycin, the only arm aimed at this patient's own truncating allele (readthrough); arimoclomol, a sentinel whose failure is informative (it did not induce HSP70 or reproduce HSP70 rescue in a published fibroblast model); and sirolimus, an adversarial comparator — the only arm with direct drug evidence in a Drosophila MVA model, where rapamycin rescued the number of aneuploid neural stem cells but not brain size. It marks the boundary: improving the survival of unstable cells is not rescue, and in a child with tumour predisposition it is a risk. Controls include vehicle, a genetic positive control (constitutively active HSF1) and HSP70 overexpression.

The proposed experiment uses an isogenic aneuploid/euploid pair, measures whether each drug engages its target, and reads chromosome segregation errors and clonogenic survival together; four outcomes are pre-declared and two of them kill the hypothesis. A five-condition drug gate separates experimental arms from therapeutic candidates; none passes today.

Strengths: explicit mechanism-to-drug chain; counter-evidence stated first; roles instead of ranking; every claim tied to a verified identifier or a declared gap; machine-checked matrices; our own errors corrected on the record. Limitations: all evidence comes from systems other than this patient; the phase of the two alleles is unresolved; the missense effect is unmeasured; readthrough efficiency cannot be predicted without an assay; the literature search was bounded, so empty cells mean 'not found in our search', not 'never studied'; nothing has been tested on a second patient. No compound is recommended for administration to any patient.

<!-- methods-form:end -->
