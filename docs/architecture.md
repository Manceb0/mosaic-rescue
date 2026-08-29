# MOSAIC RESCUE — Scientific Architecture

> ⚠️ **SUPERADO.** El inventario real del dataset (`docs/01_MASTER_BRIEF.md` §1) invalida
> las ramas que este documento describe: no hay RNA-seq, single-cell, longitudinal ni
> cariotipo celular. Ver `docs/00_ESTADO_Y_OBSOLESCENCIA.md`. Se conserva como registro.

---

## Goal

Build a reproducible research pipeline that converts patient-specific MVA data into a small number of mechanistically coherent, independently supported, safety-aware, falsifiable therapeutic hypotheses.

## Core stages

### 1. Data Inventory
Inventory exactly which modalities exist before choosing methods.

### 2. Variant Discovery
Prioritize causal variants using inheritance, consequence, phenotype, known MVA biology, broader MVA-like genes, and orthogonal evidence.

### 3. Mechanism Router
Classify the likely molecular failure mode:
- dosage loss
- protein instability
- disrupted complex/interface
- catalytic loss
- splicing defect
- regulatory defect
- other

This stage determines whether structural modeling, dosage modeling, transcript analysis, or another branch is justified.

### 4. Patient-as-Screen
If cell-resolved data exist, test whether the patient’s own mosaic states behave like a natural perturbation screen.

### 5. Ghost Karyotypes
Estimate which states are unexpectedly depleted or absent relative to a defensible generation model.

### 6. Fitness Landscape
Estimate which chromosomal or cellular states appear relatively tolerated, selected against, or transitional. Separate generation probability from selection whenever possible.

### 7. Synthetic / Natural Rescue
Nominate compensatory genes and pathways, then require independent functional support from perturbation datasets, cross-species genetics, interaction data, or experimentally grounded literature.

### 8. State Mechanism
Determine whether the rescue signal maps to protein dosage, proteostasis, mPOS, mitochondrial stress, cell competition, senescence, inflammatory signaling, or another measurable mechanism.

### 9. Mosaic Forecast
Only with appropriate data and calibration, estimate plausible next cellular states under explicit assumptions. This is a research forecast, not a patient prognosis.

### 10. Rescue Replay
Ask whether an intervention shifts molecular/cellular state toward the patient-specific tolerated state rather than merely reversing a generic disease signature.

### 11. Safe Rescue Corridor
Optimize for improvement without increased evolutionary danger. Key safeguards include CIN, abnormal clonal fitness, proliferation, apoptosis escape, and tumor-like adaptation.

### 12. Drug / Intervention Mimicry
Only after a mechanism is established, search for approved drugs or other experimentally tractable interventions that reproduce the compensatory mechanism.

### 13. Structural Mechanism — Conditional
Use experimental structures first. AlphaFold/AlphaFold 3, FoldX, Rosetta, conservation, interface metrics, and related tools are used only when structural mechanism changes a scientific decision.

### 14. PGx / Pediatric / Exposure Context
Where relevant, assess pharmacogenomic guidance, pediatric precedent, tissue exposure, PK plausibility, and contraindications.

### 15. Try to Kill the Hypothesis
Actively search for contradictory biology, insufficient exposure, tumor risk, context mismatch, and alternative explanations.

### 16. Next Best Experiment
Rank experiments by their ability to distinguish the surviving hypotheses and reduce uncertainty.

## Mandatory vs conditional modules

### Mandatory
- data inventory
- variant discovery
- mechanism router
- evidence registry
- independent validation
- safety stress test
- falsification
- next best experiment

### Conditional on data/mechanism
- patient-as-screen
- ghost karyotypes
- fitness landscape
- forecast
- cell competition
- protein-dose model
- mPOS/proteostasis
- structural modeling
- PGx

## Design philosophy

The architecture is intentionally modular. We do not force every impressive technique into the project. The patient data and the strongest mechanism decide which modules activate.
