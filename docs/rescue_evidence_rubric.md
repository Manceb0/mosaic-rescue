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
| 4 | **Two independent routes** — from different systems *and* different assay directions | `docs/research_protocol.md` §11 |
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

## Recording

Every scored candidate goes into `research/evidence_registry.md` with its score, the criteria it
failed, and whether a veto was triggered. A candidate that fails a veto is still recorded — a
documented rejection is a project asset, not a dead end.
