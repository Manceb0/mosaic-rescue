# AGENTS.md

This repository is designed for multi-agent scientific research. Every agent should optimize for **truth, novelty, falsifiability, and usefulness**, not volume of ideas.

## Mission

Help MOSAIC RESCUE discover an unusually strong, scientifically defensible insight for MVA by combining patient data with external biological evidence.

## Mandatory questions for every finding

1. What did we observe?
2. What is the non-obvious interpretation?
3. Why might another team miss it?
4. What evidence supports it?
5. What evidence contradicts it?
6. What data modality is required?
7. What alternative explanation exists?
8. What would falsify the hypothesis?
9. What external dataset or experiment can validate it independently?
10. Can it generalize beyond MVA?
11. What is the best scientific visualization for it?
12. What is the “how did you notice that?” factor?

## Evidence levels

Use one of these labels:

- **L0 — speculation**: mechanistically conceivable, no direct support yet.
- **L1 — associative**: correlation or observational support.
- **L2 — orthogonal support**: supported by an independent dataset/method.
- **L3 — functional evidence**: perturbation data support the mechanism.
- **L4 — replicated functional evidence**: convergent perturbation evidence in multiple systems.
- **L5 — clinically established**: only when truly established in humans.

Do not upgrade evidence levels because a result is exciting.

## Required research behavior

- Prefer primary literature.
- Record contradictory papers, not only supportive ones.
- Separate evidence from inference.
- Never invent unavailable hackathon data modalities.
- Treat cancer-derived DepMap evidence as context-dependent and requiring caution.
- Treat structural predictions as hypotheses, not proof.
- Treat future-state forecasts as model-based research predictions, not clinical prognosis.
- For drugs, verify approval status, mechanism, pediatric context, exposure plausibility and safety before nomination.
- For MVA, always consider whether a rescue mechanism could increase survival of genomically unstable or tumor-prone cells.

## Where findings go

- New hypothesis → `hypotheses/`
- Evidence → `research/evidence_registry.md`
- Contradiction → `research/contradictions.md`
- Open uncertainty → `research/open_questions.md`
- Weird but promising transfer idea → `research/crazy_ideas.md`
- Agent-specific report → `research/agent_findings/`

## Rule for “crazy ideas”

A crazy idea is welcome only if it can eventually be transformed into:

**observation → mechanism → measurable prediction → falsification test**

Buzzwords without a measurable prediction do not qualify.

## North-star standard

A winning hypothesis should ideally have:

**patient-specific evidence + independent functional evidence + mechanistic coherence + safety stress test + explicit experiment that can prove it wrong.**
