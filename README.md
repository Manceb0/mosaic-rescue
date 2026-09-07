# MOSAIC RESCUE

**A patient-specific causal hypothesis, a safety-constrained rescue strategy, and the
experiments that can prove both wrong.**

MOSAIC RESCUE is a research-first genomic analysis of one real paediatric patient with
suspected Mosaic Variegated Aneuploidy, for the **Rare Disease, Real Kid: MVA Hackathon
2026**.

The deliverable is not a cure or a treatment recommendation. It is a **traceable, falsifiable
preclinical hypothesis**, plus the record of every branch we killed on the way there.

## The case in 30 seconds

**Track 1 asks what most plausibly explains the case.** A panel-free search makes `BUB1B` the
leading causal hypothesis, but not a diagnosis: one allele is an LP-style truncating variant,
the second remains a VUS, and phase is unresolved.

**Track 2 asks what could be tested without helping genomically unstable cells survive.** The
therapeutic idea is split into eight evidence bridges. The current analysis finds a
translational gap and a completely unmeasured safety gap, so it stops at a falsifiable
preclinical experiment rather than overstating a drug claim.

The eight notebooks below are one decision path: first establish what the data can support,
then test causality, alternatives and mechanism, and only then design a rescue experiment.

## Start with the notebooks

Eight executed notebooks, 30 embedded figures, 25 of them scientific. Every **publication**
figure, the twelve in `figures/pub/`, is regenerated from a module in `src/figures/`, and the
notebooks call that same code, so the publication figure and the notebook figure cannot drift
apart. The remaining notebook figures come from the older `src/make_fig*.py` generators or
from code in the notebook itself; they are reproducible too, but they do not pass through the
publication standard in `src/figures/style.py`.

| Step | Notebook and question | Current conclusion |
|---|---|---|
| 00 | [Data sufficiency](notebooks/00_DATA_REALITY.ipynb) — What can the available data answer? | Sequencing is usable; five branches lack required modalities |
| 01 | [Genome-wide causal search](notebooks/01_TRACK1_GENOME_WIDE.ipynb) — Does `BUB1B` survive without a hand-picked panel? | Leading hypothesis, not a diagnosis |
| 02 | [Evidence for both `BUB1B` alleles](notebooks/02_BUB1B_ALLELE_CURATION.ipynb) — Is the pair established? | Truncating allele reaches LP in research curation; missense VUS; phase unresolved |
| 03 | [Missense mechanism](notebooks/03_BUBR1_MECHANISM.ipynb) — Is the VUS worth a functional assay? | Mechanistically concerning; abundance assay required |
| 04 | [Hidden second allele](notebooks/04_HIDDEN_SECOND_ALLELE.ipynb) — Did the coding pipeline miss a regulatory allele? | No supported SNV/indel; SV/CNV remains untested |
| 05 | [Residual phenotype](notebooks/05_RESIDUAL_PHENOTYPE.ipynb) — Does any trait require a second diagnosis? | Nephrocalcinosis alone remains unexplained |
| 06 | [Mosaic signal and MitoRead](notebooks/06_MOSAIC_AND_MITOREAD.ipynb) — What breaks when aneuploidy is variegated? | Cancellation reproduced in simulation; MitoRead is a prototype |
| 07 | [Safe-rescue hypothesis](notebooks/07_TRACK2_SAFE_RESCUE.ipynb) — What must be true before a therapeutic test? | Translation and safety evidence are still missing. Ends in a three-arm experimental portfolio, not a therapeutic winner |

> An earlier version described a planned architecture of sixteen notebooks and eight
> hypotheses, most of which assumed single-cell, RNA-seq or longitudinal data that this case
> does not have. The superseded plan is kept in `docs/history/` for traceability.

```bash
python src/nb/build_all.py        # rebuild and execute all eight notebooks
python src/figures/render_all.py  # full-size figures: SVG + PNG at 300 dpi
python src/sanitize_scan.py       # privacy scan over everything a commit would add
python src/audit_stale_claims.py  # find claims superseded by later results
```

## Where the project stands

**Track 1, the causal mechanism.** No panel was used for the primary search: `BUB1B` competed
against a universe of **6 321 genes** carrying a HIGH or MODERATE consequence allele, and 151
of them scored under an inheritance model. It ranks first in 14 of 15 phenotype-perturbation
analyses. In the frozen, preregistered `A0` it ranks **fourth**; in the later `A0-FREQFIX`
sensitivity it ranks first. Both numbers are always reported together, because the difference
is what shows why allele-frequency provenance matters. An independent method on the same VCF,
Exomiser, places it second of 398 under a recessive model.

The truncating allele reaches Likely Pathogenic (9 ACMG points). The missense allele is a VUS
and stays there: `PM3` is blocked because **phase is unresolved** without parental genotypes,
and `PS3` needs a functional assay this project does not run. So the correct statement is
*candidate compound heterozygosity with phase unresolved*, and nothing stronger.

**Track 2, the therapeutic hypothesis.** The mechanistic chain is broken into eight bridges and
audited against ten dimensions of evidence. Of 80 cells, **61 are empty**. Bridge 7, whether
pharmacological co-induction reproduces the rescue that genetic overexpression achieves, has
verified counter-evidence. Bridge 8, whether the same intervention affects chromosome
instability and clonogenic survival, turned up no qualifying evidence in our bounded
literature search. No overall score is
computed, because combining heterogeneous evidence into one number would need a preregistered
method that does not exist.

What Track 2 proposes is therefore **a portfolio, not a winner**: three interventions in three
distinct roles, plus three controls, each with its discard rule written in advance.
What is nominated is **two candidate pharmacologic hypotheses plus one adversarial
comparator**. **Azithromycin** is the only arm aimed at this patient's own truncating allele,
and it has no direct evidence at all. **Arimoclomol** is a falsification sentinel: it is the
only arm with verified counter-evidence, so its *failure* is the informative outcome and would
close bridge 7. **Sirolimus** is not a candidate at all: it is there to probe the safety
boundary, and it is the one arm with direct pharmacological evidence *in a Drosophila CIN
model*, already partly negative on the outcome that matters.

Stated precisely: **we nominate pharmacologic arms for preclinical discrimination, not a
therapeutic winner and not a clinical recommendation.** No compound is proposed for
administration to any patient.

**What blocks the rest.** Parental genotypes, full-depth BAM or CRAM, a contemporaneous blood
count, and the obstetric history. Five of sixteen branches are blocked by missing data, not by
missing compute.

## Results we did not want

These are here because the decision tables were written before the analyses ran.

- The allele join was broken. `allele_key.py` existed, had passing tests, and **no module
  imported it**. Fixing it moved `BUB1B` from first to fourth in the frozen `A0`. The number
  was reported, not buried.
- AlphaGenome predicted no coherent molecular effect for the only regulatory candidate. That
  closed the hidden second allele branch as `NEGATIVE`.
- Three homozygous deletions outranked `BUB1B` in `A0`. They turned out to be common
  polymorphisms VEP had failed to annotate.
- `FANCD2` as a competing hypothesis: all three alleles at about 47 % frequency, all
  heterozygous. `NEGATIVE`.
- The HPO matrix shows `MVA1` covers three of seven proband terms by annotation, not six as an
  earlier caption claimed. The caption is now computed from the matrix.

## Rules this repository is held to

**No rescue without a do-no-harm test.** MVA carries tumour predisposition. A mechanism that
helps aneuploid cells survive can be dangerous. Safety is part of the hypothesis, not a
disclaimer appended to it.

**Nothing is fabricated.** No blots, no microscopy, no karyotypes, no coverage tracks, no
Hi-C, and no confidence interval that nobody computed. Where uncertainty is declared
unquantified, the figure shows an open-ended range rather than inventing a bound.

**Every figure declares two things**, and they are different questions: its `FIGURE CLASS`
(what kind of object it is: `DATA`, `MODEL_OUTPUT`, `SIMULATION`, `CURATED_EVIDENCE`,
`SYNTHESIS`, `NARRATIVE`) and its `EVIDENCE ORIGIN` (where the content came from: `MEASURED`,
`DERIVED`, `EXTERNAL`, `PREDICTED`, `SIMULATED`). Collapsing them is how a figure starts
misrepresenting itself.

**Every claim carries an evidence level.** `L0` speculation, `L1` associative, `L2` orthogonal
support, `L3` functional, `L4` replicated functional, `L5` clinically established.

**No patient data in this repository.** No FASTQ, BAM, CRAM, VCF, variant coordinates,
genotypes or sample identifiers. Paths live in `config/paths.yaml`, which is gitignored, and
`src/sanitize_scan.py` checks everything a commit would add, including files not yet tracked.

## What a therapeutic dossier would have to contain

A causal variant, the molecular mechanism it disrupts, the patient evidence behind it, a
compensatory mechanism, independent validation, an intervention that mimics it, and a safety
and falsification plan. We do not have all seven for any candidate, and the evidence matrix in
notebook 07 says exactly which parts are missing.

## Submission

| Deliverable | Where |
|---|---|
| Track 1 report | [`reports/TRACK1_REPORT.md`](reports/TRACK1_REPORT.md) |
| Track 2 report | [`reports/TRACK2_REPORT.md`](reports/TRACK2_REPORT.md) |
| Track 1 predictions CSV | **not in this repository, by design.** Generated by [`src/submission/track1_csv.py`](src/submission/track1_csv.py) into a gitignored directory, because the required format carries coordinates, alleles and the proband identifier |
| Scalability, what transfers to another case | [`docs/SCALABILITY.md`](docs/SCALABILITY.md) |
| The four figures for the 3-minute video | [`docs/JUDGE_PATH.md`](docs/JUDGE_PATH.md) |
| One-command verification | `python src/verify.py` |

Both reports carry the required AI-use disclosure. **Two fields in it are deliberately blank**,
the plan or tier and the account's data-handling setting: they are properties of the
maintainer's account, and this project does not write unverified facts. They must be completed
before submission, along with the dataset citation from the hackathon Synapse page.

## Reading order

1. [`docs/01_MASTER_BRIEF.md`](docs/01_MASTER_BRIEF.md), the scientific context, evidence and
   counter-evidence.
2. [`docs/04_ARQUITECTURA_MAESTRA.md`](docs/04_ARQUITECTURA_MAESTRA.md), the current scientific
   hierarchy. It overrides any earlier module or idea.
3. [`research/EXPERIMENT_REGISTRY.md`](research/EXPERIMENT_REGISTRY.md), every experiment with
   its status and its executable origin.
4. [`notebooks/README.md`](notebooks/README.md), how the notebooks are built and what makes one
   finished.
5. [`PUBLICATION_FIGURE_QA.md`](PUBLICATION_FIGURE_QA.md), one row per figure, including the
   mandatory column: what a reader could wrongly conclude from it.
6. [`docs/SCALABILITY.md`](docs/SCALABILITY.md), which parts of the method transfer to another
   patient and which are specific to `BUB1B` and MVA, measured rather than asserted.

Contributing: [`AGENTS.md`](AGENTS.md) and
[`CONTRIBUTING_RESEARCH.md`](CONTRIBUTING_RESEARCH.md).
Evidence against our own preferred ideas lives in
[`research/contradictions.md`](research/contradictions.md).

## Scientific boundary

This project produces computational and preclinical research hypotheses. It does not diagnose,
prescribe, recommend administration, or claim a cure. The patient's family consented to their
story being shared; nothing here identifies them, and no attempt was made to find them.
