# MOSAIC RESCUE

### *The disease is running an evolutionary experiment. We decode it.*

MOSAIC RESCUE is a research-first, Jupyter/Python project for the **Rare Disease, Real Kid: MVA Hackathon 2026**. The goal is not to claim a cure or recommend treatment. The goal is to generate **patient-specific, traceable, falsifiable therapeutic hypotheses** from real genomic and clinical data.

## Core idea

Mosaic Variegated Aneuploidy (MVA) continuously generates chromosomally distinct cellular states. Instead of treating that mosaicism only as a consequence of disease, we ask whether the cellular states that **persist, disappear, or are predicted to emerge** reveal endogenous rules of cellular fitness and compensation.

Those rules can then be independently tested using functional-genomics evidence and, only after convergence, used to nominate approved drugs or other interventions that may mimic a naturally tolerated state.

> **The patient is not only the case. The patient may also contain the experiment.**

## Scientific story

```text
PATIENT DATA
   ↓
CAUSE
Which variant(s) plausibly drive this MVA phenotype?
   ↓
MECHANISM ROUTER
What is actually broken: dosage, stability, interface, catalysis, splicing, regulation, other?
   ↓
PATIENT-AS-SCREEN
Which chromosomal/cellular states persist?
   ↓
NEGATIVE SPACE
Which states should exist but are depleted or absent?  → “Ghost Karyotypes”
   ↓
FITNESS LANDSCAPE
What rules appear to govern persistence, elimination and transition?
   ↓
SYNTHETIC / NATURAL RESCUE
Which genes or pathways could explain compensation?
   ↓
INDEPENDENT VALIDATION
CRISPR / Perturb-seq / DepMap / interaction data / literature / cross-species genetics
   ↓
FORECAST
What states are plausible next under explicit model assumptions?
   ↓
RESCUE REPLAY
How would candidate interventions alter the predicted cellular trajectory?
   ↓
SAFE RESCUE CORRIDOR
Can function improve without increasing CIN, abnormal clonal fitness or tumor-like behavior?
   ↓
NEXT BEST EXPERIMENT
What experiment would reduce uncertainty the most?
   ↓
FALSIFIABLE THERAPEUTIC HYPOTHESIS
```

## The “wow” hypotheses we will test

1. **Patient-as-Screen** — MVA may create a natural perturbation screen inside one patient.
2. **Ghost Karyotypes** — missing or depleted chromosomal states may be as informative as surviving ones.
3. **Evolutionary Fitness Landscape** — the distribution of states may reveal rules of cellular selection.
4. **Natural / Synthetic Rescue** — compensatory mechanisms may be discoverable by combining within-patient evidence with independent functional screens.
5. **Mosaic Forecast** — under suitable data and assumptions, the inferred landscape may support probabilistic forecasting of plausible future cellular states.
6. **Rescue Replay** — interventions should be evaluated by whether they move cells toward a patient-specific tolerated state, not merely toward an average “healthy” signature.
7. **Safe Rescue Corridor** — rescue is not equal to survival; a useful intervention should improve function without increasing chromosomal instability or dangerous cellular fitness.
8. **Next Best Experiment** — the system should end by proposing the experiment that most sharply distinguishes competing hypotheses.

## Data-dependent design

We will not invent data modalities.

- If **single-cell** data exist, we can test cell-state and karyotype-level hypotheses directly.
- If only **WGS/VCF/BAM/CRAM** are available, we will build a WGS-based mosaic fingerprint and shift more weight to external functional-genomics validation.
- If **bulk RNA-seq** exists, pathway and stress-state analysis becomes possible but cannot be treated as cell-level evidence.
- Structural modeling (AlphaFold/experimental structures/FoldX/Rosetta) is **conditional** and used only when a specific variant mechanism makes it decision-relevant.

## What we are NOT doing

- We are **not** claiming a cure.
- We are **not** recommending a drug to a child.
- We are **not** treating model output as clinical prediction.
- We are **not** using AlphaFold as decoration.
- We are **not** ranking drugs before establishing a mechanism.
- We are **not** calling association “causality” without identification assumptions and independent evidence.

## Repository map

```text
mosaic-rescue/
├── README.md
├── AGENTS.md
├── CONTRIBUTING_RESEARCH.md
├── requirements.txt
├── hypotheses/
│   ├── README.md
│   └── hypothesis_template.md
├── research/
│   ├── evidence_registry.md
│   ├── contradictions.md
│   ├── open_questions.md
│   ├── crazy_ideas.md
│   └── agent_findings/
├── notebooks/
│   ├── 00_data_inventory.ipynb
│   ├── 01_variant_discovery.ipynb
│   ├── 02_mechanism_router.ipynb
│   ├── 03_mosaic_landscape.ipynb
│   ├── 04_ghost_karyotypes.ipynb
│   ├── 05_fitness_landscape.ipynb
│   ├── 06_synthetic_rescue.ipynb
│   ├── 07_cell_competition.ipynb
│   ├── 08_mosaic_forecast.ipynb
│   ├── 09_rescue_replay.ipynb
│   ├── 10_safe_rescue_corridor.ipynb
│   ├── 11_drug_mimicry.ipynb
│   ├── 12_structural_mechanism.ipynb
│   ├── 13_pgx_safety.ipynb
│   ├── 14_try_to_kill_hypothesis.ipynb
│   └── 15_next_best_experiment.ipynb
├── src/
│   ├── variants/
│   ├── mosaic/
│   ├── fitness/
│   ├── rescue/
│   ├── structure/
│   ├── drugs/
│   ├── safety/
│   └── visualization/
├── figures/
├── references/
└── docs/
```

## Every notebook must answer

- What biological question are we asking?
- What data support the analysis?
- What assumptions are required?
- What result would support the hypothesis?
- What result would falsify it?
- What is the strongest alternative explanation?
- What uncertainty remains?
- What visualization best exposes the phenomenon to a domain scientist?
- What is the next best experiment?

## North-star output

We do **not** want a list of 50 drugs.

We want at most a few hypothesis dossiers of the form:

```text
Causal variant
→ molecular mechanism
→ within-patient mosaic evidence
→ compensatory mechanism
→ independent functional validation
→ candidate intervention that mimics the mechanism
→ pediatric / PK / PGx context where relevant
→ CIN / tumor-risk stress test
→ explicit uncertainty
→ exact experiment that could prove us wrong
```

## Hackathon principle

**No rescue without a do-no-harm test.**

MVA can involve tumor predisposition. A mechanism that helps aneuploid cells survive may also help dangerous cells persist. Safety is therefore part of the scientific hypothesis itself, not an afterthought.

---

This repository is a collaborative research workspace. New ideas are welcome, but every idea must earn its place through evidence, explicit assumptions, and falsifiability.
