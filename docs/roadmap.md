# MOSAIC RESCUE — Execution Roadmap

> ⚠️ **SUPERADO.** El inventario real del dataset (`docs/01_MASTER_BRIEF.md` §1) invalida
> las ramas que este documento describe: no hay RNA-seq, single-cell, longitudinal ni
> cariotipo celular. Ver `docs/00_ESTADO_Y_OBSOLESCENCIA.md`. Se conserva como registro.

---

This roadmap separates **scientific discovery** from **presentation polish**. We do not build a flashy demo before we know what the data can support.

## Phase 0 — Data reality (blocking)

### Goal
Inventory the exact hackathon files and activate only justified branches.

### Deliverables
- `00_data_inventory.ipynb`
- modality matrix
- data provenance
- file sizes / genome build / sample metadata
- branch activation table

### Exit criteria
We can answer: **What can the patient data actually prove?**

---

## Phase 1 — Causal diagnosis / Track 1

### Goal
Build the strongest causal-variant shortlist and mechanism classification.

### Deliverables
- candidate variants with inheritance and phenotype support
- broader MVA/MVA-like gene search
- mechanism router assignment
- confidence and uncertainty table

### Exit criteria
At least one plausible causal hypothesis has a traceable evidence chain.

---

## Phase 2 — Discover the unusual signal

### Goal
Find the project's central non-obvious observation.

Potential activated modules:
- Patient-as-Screen
- WGS mosaic fingerprint
- Ghost Karyotypes
- chromosome-state enrichment/depletion
- allele-specific effects
- protein-dose threshold
- structural mechanism

### Exit criteria
We have at least one result that is both **patient-linked** and **falsifiable**.

---

## Phase 3 — Explain selection / compensation

### Goal
Move from pattern to mechanism.

### Deliverables
- fitness / persistence model
- candidate compensatory genes/pathways
- synthetic-rescue evidence
- dosage/proteostasis/mPOS/cell-competition branch if supported

### Exit criteria
At least one compensatory mechanism reaches L2 and has a realistic path to L3 functional support.

---

## Phase 4 — Independent validation

### Goal
Prevent the project from becoming a story built from one dataset.

### External evidence routes
- CRISPR screens
- Perturb-seq
- DepMap, explicitly cancer-contextualized
- cross-species suppressor genetics
- BioGRID / curated interactions
- morphology / Cell Painting
- perturbation transcriptomics
- primary experimental literature

### Exit criteria
The lead mechanism survives at least two independent evidence routes, preferably including functional perturbation.

---

## Phase 5 — Forecast and counterfactual branch

### Goal
Ask what might happen next and what changes under intervention **only if data permit**.

### Direct forecast path
Requires appropriate longitudinal/cell-resolved data and validation.

### Fallback
Scenario simulation using external calibration and explicit assumptions.

### Deliverables
- state-transition graph
- uncertainty bands
- held-out/external validation where possible
- intervention counterfactuals

### Exit criteria
We can defend the statement as either:
- **cellular-state forecast**, or
- **scenario simulation under assumptions**.

Never clinical prognosis.

---

## Phase 6 — Rescue Replay

### Goal
Search for an intervention that reproduces the **compensatory mechanism**, not merely a generic reverse signature.

### Deliverables
- mechanism-to-intervention map
- evidence convergence score
- transcriptomic/morphological support if applicable
- approved-status verification

### Exit criteria
At most a few intervention hypotheses remain.

---

## Phase 7 — Safe Rescue Corridor

### Goal
Reject interventions that improve one metric while increasing evolutionary danger.

### Required checks
- CIN / missegregation
- abnormal clonal fitness
- proliferation
- apoptosis escape
- tumor-like adaptation
- exposure / tissue plausibility
- pediatric context
- PGx where actionable guidance exists

### Exit criteria
Lead candidate has an explicit **benefit vs evolutionary-risk** argument.

---

## Phase 8 — Try to Kill It

### Goal
Attack the final hypothesis harder than a judge will.

### Required output
- strongest contradictory papers
- model mismatch
- potential confounders
- alternate mechanism
- negative-control analysis
- stop criteria

### Exit criteria
The lead hypothesis either survives with downgraded uncertainty or is rejected.

---

## Phase 9 — Next Best Experiment

### Goal
End with the most informative experiment, not with overconfidence.

### Candidate experiments may include
- chromosome missegregation assay
- protein abundance/stability
- rescue perturbation
- p62/proteostasis readout
- mitochondrial import / ROS readout
- cell competition assay
- candidate intervention in relevant patient-derived/model cells

### Exit criteria
One experiment is ranked highest for reducing uncertainty between the remaining hypotheses.

---

## Phase 10 — Hackathon package

### Final deliverables
- reproducible notebooks
- concise hypothesis dossier(s)
- 3-minute story
- visual architecture
- key scientific figures
- explicit caveats
- GitHub reproduction instructions

## Recommended build order

```mermaid
flowchart LR
    A[Data inventory] --> B[Variant discovery]
    B --> C[Mechanism router]
    C --> D[Non-obvious patient signal]
    D --> E[Independent validation]
    E --> F[Mechanistic convergence]
    F --> G[Forecast / replay if justified]
    G --> H[Intervention mimicry]
    H --> I[Safety]
    I --> J[Falsification]
    J --> K[Next experiment]
    K --> L[Pitch]
```

## Stop rules

We stop or park a branch if:

- required modality is absent,
- signal disappears under a reasonable null model,
- external functional evidence strongly contradicts it,
- the intervention only helps by increasing dangerous aneuploid tolerance,
- the method cannot be calibrated or validated in the available time,
- the result is visually impressive but scientifically non-decisive.
