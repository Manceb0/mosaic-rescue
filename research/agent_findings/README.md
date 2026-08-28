# Agent Findings

Each research agent should create one Markdown report in this folder. Use the format below so independent work can be compared and merged.

## File naming

`YYYY-MM-DD_<topic>_<agent>.md`

Example:

`2026-08-28_ghost-karyotypes_agent-a.md`

## Required structure

```markdown
# Finding title

## Research question

## Why this matters

## Bottom line
- Pursue / Conditional / Park / Reject
- Current evidence level: L0-L5

## Key findings
1.
2.
3.

## Primary evidence
| Claim | Source | Model / population | Evidence type | Level | Notes |
|---|---|---|---|---|---|

## Contradictory evidence
| Claim challenged | Source | Why it matters |
|---|---|---|

## What is directly supported vs inferred
### Directly supported

### Inferred

## Required hackathon data

## Proposed analysis

## Expected scientific visualization

## Alternative explanations

## Falsification test

## What result would make us abandon this idea?

## Transferability beyond MVA

## “How did you notice that?” factor

## Recommended next action

## References
```

## Quality rules

- Link or identify the primary source for every major factual claim.
- Do not copy a review's conclusion without tracing key claims to primary evidence.
- Say when a study uses cancer cells, yeast, mouse models, iPSC, fibroblasts, or another context.
- Do not silently transfer a cancer vulnerability into a pediatric constitutional disease.
- If a method requires single-cell or longitudinal data, state that dependency explicitly.
- Every report must contain a real contradiction search.
- Every report must contain a falsification criterion.
- A clever idea with no test remains L0.

## Promotion to core hypothesis

A report can be promoted into `hypotheses/` when it has:

1. a precise measurable prediction,
2. a defined data source,
3. at least one independent validation route,
4. a contradiction search,
5. a falsification test,
6. a clear decision it would change.
