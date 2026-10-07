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

## 0:30–1:10 · What we found, and its exact ceiling

Show [the convergence figure](../figures/pub/fig14_track1_convergence.svg), then
[the causal card](assets/mosaic-02-phase-function.png).

"We searched 6,321 genes without choosing one in advance, and the genome converged on BUB1B:
first in 14 of 15 sensitivity analyses, second of 398 in an external tool on the same data. The
frozen ranking put it fourth, because three common variants had lost their frequencies; we
always report both numbers. The genotype is the classic one for this disease. What we do not
know yet is whether the two alleles sit on opposite copies, and the missense is still uncertain.
A strong hypothesis, not a diagnosis."

The 15 analyses and Exomiser use the same genome: robustness, not independent replications.
Exomiser's own #1, HLA-DRB1, is an open audit flag.

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

"In cells from other MVA patients, putting BUBR1 back restored the mitotic checkpoint. That
gives us a target we can measure: fewer new segregation errors. But better survival is not
enough: we might be helping the wrong cells survive. So we test three distinct routes: an
allele-directed readthrough arm, azithromycin, which our own computation has already weakened
but not eliminated; a proteostasis sentinel, arimoclomol; and a safety comparator, sirolimus.
They are not a therapeutic ranking."

The published rescue was genetic, its endpoint was the checkpoint, and its alleles were not this
child's. No drug has been tested in a BUB1B patient cell.

External evidence does not demonstrate efficacy in this case. The assay must measure molecular
activity, chromosome segregation and clonogenic survival, as well as viability.
[Rejection rules](assets/mosaic-05-rescue-test.png).

## 2:20–3:00 · The useful result is a decision

Show [the next experiment](assets/mosaic-06-next-experiments.png).

"The most informative next step is phase: if both alleles are on the same copy, this pair no
longer explains a recessive mechanism. Then we need variant-specific function, and RNA and long
reads if the search for a second allele continues. For any rescue, more clonogenic survival of
unstable cells is a reason to reject it, not a win. And the system vetoes its own attractive
ideas: our mosaicism detector failed its validation on public trios, so we never ran it on the
child. We deliver a traceable hypothesis and the tests that can change it. And one open question for the future: MVA keeps generating different
chromosome states in the same child. Can the patient become the screen?"

Say it as a question. Nothing in this project measured cell-level heterogeneity.

## Questions that must be answerable in one sentence

| Question | Answer |
|---|---|
| How many genomes? | One biological sample, four lanes; not a cohort and not a trio |
| Is the case solved? | No: phase and the function of the missense remain open |
| Is the BAM missing? | It exists; GO 2B is closed within its protocol |
| Does the RD/BAF plot show mosaicism? | It is descriptive; it does not count cells or establish a karyotype |
| Which drug won? | None: we propose experimental roles with rejection criteria |
| Is azithromycin the answer? | No: EXP-029 weakened it computationally (lower-tercile stop context; non-wild-type products), it was not eliminated, and it has never been tested in BUB1B |
| Did the mosaicism detector work? | No: EXP-027 failed method validation (249/995 intact benchmark pairs called vs 5 % nominal), so the patient test was not performed; that is not a negative patient result |
| What does this project change? | It makes explicit what supports each inference, what contradicts it and which experiment decides it |
| What about the rest of the phenotype? | The nephrocalcinosis remains a residual question; prioritising BUB1B does not erase it |
| What generalises? | The decision procedure; it has not yet been validated on another patient |
| Is the rescue logic new? | No. Learning from resistant cells, somatic rescue and our safety corridor all have precedent, including another public repository in this hackathon; Track 2 §9 lists them |
| Does the blood genome show the child's mosaic? | Only one view of it: what division generates, what selection removes and which tissue is sampled are mixed in bulk blood (Track 1 §7b) |

## Preparing the submission

Do not use the old slogan "The Patient Is the Screen" as a finding: no selection or cell
persistence was measured. Its only permitted form is the closing question, "Can the patient
become the screen?". Do not present the safety corridor as our invention. Do not use the internal technical figures that carry positions or
genotypes in a public presentation. The new syntheses omit those fields, but a privacy review
of the whole package is still required.

Complete the account and AI-use fields, the formal dataset citation and the submission review.
A green `verify.py` is not a submitted package.

Submission requirements and artifact status: [track deliverables](TRACK_DELIVERABLES.md).
