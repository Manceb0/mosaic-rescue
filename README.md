# MOSAIC RESCUE

Research-first genomic analysis of one real paediatric patient with suspected Mosaic
Variegated Aneuploidy, for the **Rare Disease, Real Kid: MVA Hackathon 2026**.

The deliverable is not a cure or a treatment recommendation. It is a **traceable, falsifiable
preclinical hypothesis**, plus the record of every branch we killed on the way there.

> An earlier version of this file described a planned architecture of sixteen notebooks and
> eight hypotheses, most of which assumed single-cell, RNA-seq or longitudinal data that this
> case does not have. That plan was superseded by what the data actually supported. It is kept
> in `docs/history/` for traceability.

## What is in here

Eight executed notebooks, 27 embedded figures, 22 of them scientific. Every figure is
regenerated from a module in `src/figures/`, and the notebooks call that same code, so the
publication figure and the notebook figure cannot drift apart.

| # | Notebook | Question | Status |
|---|---|---|---|
| 00 | `DATA_REALITY` | What can and cannot be answered with the data that exists? | Fit for use, not sufficient |
| 01 | `TRACK1_GENOME_WIDE` | Which gene explains the case when the whole coding genome competes? | `BUB1B` survives a panel-free search |
| 02 | `BUB1B_ALLELE_CURATION` | What supports each allele, and what would make the pair causal? | Truncating allele Likely Pathogenic; missense stays VUS |
| 03 | `BUBR1_MECHANISM` | The missense will not move by classification. Does it move by mechanism? | `UNRESOLVED`, needs an abundance assay |
| 04 | `HIDDEN_SECOND_ALLELE` | Is there a second allele the coding pipeline cannot see? | `NEGATIVE` for SNV and indel |
| 05 | `RESIDUAL_PHENOTYPE` | Which traits does MVA not explain? | Nephrocalcinosis is the only one failing both checks |
| 06 | `MOSAIC_AND_MITOREAD` | What happens to the mosaicism signal when clonality breaks? | Cancellation mechanism reproduced |
| 07 | `TRACK2_SAFE_RESCUE` | Is there a plausible, falsifiable and safe therapeutic mechanism? | Two bridges of eight are empty |

```bash
python src/nb/build_all.py        # rebuild and execute all eight notebooks
python src/figures/render_all.py  # full-size figures: SVG + PNG at 300 dpi
python src/sanitize_scan.py       # privacy scan over everything a commit would add
python src/audit_stale_claims.py  # find claims superseded by later results
```

## Where the project stands

**Track 1, the causal mechanism.** `BUB1B` ranks first in 14 of 15 phenotype-perturbation
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
instability and clonogenic survival, has never been measured by anyone. **No drug is
nominated**, and no overall score is computed, because combining heterogeneous evidence into
one number would need a preregistered method that does not exist.

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

Contributing: [`AGENTS.md`](AGENTS.md) and
[`CONTRIBUTING_RESEARCH.md`](CONTRIBUTING_RESEARCH.md).
Evidence against our own preferred ideas lives in
[`research/contradictions.md`](research/contradictions.md).

## Scientific boundary

This project produces computational and preclinical research hypotheses. It does not diagnose,
prescribe, recommend administration, or claim a cure. The patient's family consented to their
story being shared; nothing here identifies them, and no attempt was made to find them.
