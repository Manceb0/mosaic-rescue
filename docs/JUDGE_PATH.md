# Three-minute script: from finding to experiment

This version integrates the closed GO 2B and keeps the narration separate from the technical
results. The thirteen visual questions and their files are listed in [STORYBOARD.md](STORYBOARD.md).

## 0:00–0:30 · The question

Show [the cover](assets/mosaic-00-project-map.png).

"We have one blood genome from a child with a suspected chromosome-segregation disorder. We
want to answer two questions: what best explains the case, and what experiment could test a
rescue without favouring genomically unstable cells."

If asked: four sequencing lanes are still one sample. There is no RNA, no protein data and no
parental genotyping. GRCh38 is the reference.

## 0:30–1:10 · The hypothesis and its weak point

Show [the causal card](assets/mosaic-02-phase-function.png).
Optional detail: [the original ranking](../figures/pub/fig01_prioritization_genomewide.svg).

"We searched without choosing a gene in advance. BUB1B came fourth in the frozen ranking. An
audit found that three competitors were common variants whose frequencies were missing; once
repaired, BUB1B ranked first. We report both numbers. The child carries a truncating allele and
a missense, which is exactly the classic genotype of this disease. What we do not yet know is
whether they sit on opposite copies of the gene. The missense is still a variant of uncertain
significance."

Do not call this a diagnosis. Exomiser uses the same VCF: another tool, not evidence from
another patient.

## 1:10–1:40 · Trying to refute it

Show [the second-allele search](assets/mosaic-04-hidden-allele.png).

"In this disease the second allele has often hidden outside the exons. So we rebuilt the full
alignment and searched the structural classes we had preregistered. No copy-number or
mobile-element call overlaps BUB1B. The read metrics are descriptive and do not exclude a
complex insertion. We closed that analysis, not the case."

The RNA/long-read precedent comes from another published case. Never show its blots as if they
belonged to this patient. GO 2B details are for questions.

## 1:40–2:20 · The problem a rescue has to solve

Show [the mechanism](assets/mosaic-08-mechanism.png).
If asked about compounds, open [the portfolio](../figures/pub/fig08_track2_portfolio.svg).

"Better survival is not enough: we might be helping the wrong cells survive. We separate an
allele-directed hypothesis, a sentinel that tests whether the pharmacology works at all, and a
comparator that challenges safety. Azithromycin, arimoclomol and sirolimus fill those three
roles. They are not a therapeutic ranking."

External evidence does not demonstrate efficacy in this case. The assay must measure molecular
activity, chromosome segregation and clonogenic survival, as well as viability.
[Rejection rules](assets/mosaic-05-rescue-test.png).

## 2:20–3:00 · The useful result is a decision

Show [the next experiment](assets/mosaic-06-next-experiments.png).

"The most informative next step is phase: if both alleles are on the same copy, this pair no
longer explains a recessive mechanism. Then we need variant-specific function, and RNA and long
reads if the search for a second allele continues. For any rescue, more clonogenic survival of
unstable cells is a reason to reject it, not a win. We deliver a traceable hypothesis and the
tests that can change it."

## Questions that must be answerable in one sentence

| Question | Answer |
|---|---|
| How many genomes? | One biological sample, four lanes; not a cohort and not a trio |
| Is the case solved? | No: phase and the function of the missense remain open |
| Is the BAM missing? | It exists; GO 2B is closed within its protocol |
| Does the RD/BAF plot show mosaicism? | It is descriptive; it does not count cells or establish a karyotype |
| Which drug won? | None: we propose experimental roles with rejection criteria |
| What does this project change? | It makes explicit what supports each inference, what contradicts it and which experiment decides it |
| What about the rest of the phenotype? | The nephrocalcinosis remains a residual question; prioritising BUB1B does not erase it |
| What generalises? | The decision procedure; it has not yet been validated on another patient |

## Preparing the submission

Do not use the old slogan "The Patient Is the Screen" as a finding: no selection or cell
persistence was measured. Do not use the internal technical figures that carry positions or
genotypes in a public presentation. The new syntheses omit those fields, but a privacy review
of the whole package is still required.

Complete the account and AI-use fields, the formal dataset citation and the submission review.
A green `verify.py` is not a submitted package.

Submission requirements and artifact status: [track deliverables](TRACK_DELIVERABLES.md).
