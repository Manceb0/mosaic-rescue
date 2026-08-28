# MOSAIC RESCUE — Visual Diagrams

GitHub renders these Mermaid diagrams directly.

## 1. End-to-end architecture

```mermaid
flowchart TD
    A[Patient data] --> B[Inventory + QC]
    B --> C[Variant discovery]
    C --> D{Mechanism router}
    D --> E1[Dosage / expression]
    D --> E2[Stability / degradation]
    D --> E3[Interface / complex]
    D --> E4[Splicing / regulatory / other]
    E1 --> F
    E2 --> F
    E3 --> F
    E4 --> F
    F{Cell-resolved data?}
    F -- Yes --> G[Patient-as-Screen]
    F -- No --> H[WGS / bulk mosaic fingerprint]
    G --> I[Observed state atlas]
    H --> I
    I --> J[Ghost Karyotypes]
    J --> K[Fitness landscape]
    K --> L[Compensatory mechanism candidates]
    L --> M[Independent functional validation]
    M --> N{Convergent?}
    N -- No --> O[Reject / revise]
    O --> I
    N -- Yes --> P[State mechanism]
    P --> Q[Forecast - conditional]
    Q --> R[Rescue Replay]
    R --> S[Safe Rescue Corridor]
    S --> T[Intervention mimicry]
    T --> U[PGx / pediatric / PK]
    U --> V[Try to Kill It]
    V --> W{Survives?}
    W -- No --> X[Reject candidate]
    X --> T
    W -- Yes --> Y[Next Best Experiment]
    Y --> Z[Final hypothesis dossier]
```

## 2. Patient-as-Screen logic

```mermaid
flowchart LR
    A[MVA creates chromosomal diversity] --> B[Different cellular states]
    B --> C[Some persist]
    B --> D[Some are depleted]
    B --> E[Some may emerge later]
    C --> F[Observed survivors]
    D --> G[Ghost Karyotypes]
    E --> H[Forecast states]
    F --> I[Infer candidate fitness rules]
    G --> I
    H --> I
    I --> J[Candidate compensation]
    J --> K[Independent perturbation validation]
```

## 3. Ghost Karyotype logic

```mermaid
flowchart TD
    A[Possible chromosome state space] --> B[Generation model]
    B --> C[Expected frequencies]
    D[Observed patient states] --> E[Observed frequencies]
    C --> F[Expected vs observed]
    E --> F
    F --> G{Large depletion beyond uncertainty?}
    G -- No --> H[No ghost claim]
    G -- Yes --> I{Sampling / detection artifact?}
    I -- Yes --> H
    I -- No --> J[Ghost Karyotype candidate]
    J --> K[Selection / viability hypothesis]
    K --> L[Independent validation]
```

## 4. Evidence convergence

```mermaid
flowchart LR
    A[Patient observation] --> H[Lead mechanism]
    B[CRISPR / Perturb-seq] --> H
    C[Cross-species genetics] --> H
    D[Protein / interaction evidence] --> H
    E[Transcriptomic / morphology] --> H
    F[Primary literature] --> H
    G[Contradiction search] -. challenges .-> H
    H --> I{Enough convergence?}
    I -- No --> J[Park / reject]
    I -- Yes --> K[Intervention hypothesis]
```

## 5. Structural branch

```mermaid
flowchart TD
    A[Lead causal variant] --> B{Missense / structurally interpretable?}
    B -- No --> C[Skip structural branch]
    B -- Yes --> D{Experimental structure available?}
    D -- Yes --> E[Map residue on experimental structure]
    D -- No --> F[Use validated predicted structure cautiously]
    E --> G[Interface / stability / catalytic analysis]
    F --> G
    G --> H{Does structure change a decision?}
    H -- No --> C
    H -- Yes --> I[Mechanism classification refined]
    I --> J[Choose relevant rescue strategy]
```

## 6. Forecasting logic

```mermaid
flowchart TD
    A[Current state distribution] --> B{Longitudinal / cell-resolved evidence?}
    B -- Yes --> C[Fit transition / fitness model]
    B -- No --> D[Scenario simulation only]
    C --> E[Calibration + validation]
    E --> F[Probabilistic next-state forecast]
    D --> G[Assumption-conditioned scenarios]
    F --> H[Uncertainty intervals]
    G --> H
    H --> I[No clinical prognosis claim]
```

## 7. Rescue Replay and Safe Rescue Corridor

```mermaid
flowchart LR
    A[Patient baseline state] --> B[Candidate intervention A]
    A --> C[Candidate intervention B]
    A --> D[Candidate intervention C]
    B --> E[Predicted / observed state shift]
    C --> E
    D --> E
    F[Natural tolerated state] --> G[Similarity to rescue mechanism]
    E --> G
    G --> H[Benefit score]
    E --> I[CIN / clonal / tumor-risk score]
    H --> J{Safe Rescue Corridor?}
    I --> J
    J -- No --> K[Reject]
    J -- Yes --> L[Advance]
```

## 8. Closed-loop discovery

```mermaid
flowchart LR
    A[Observe] --> B[Explain]
    B --> C[Validate]
    C --> D[Forecast]
    D --> E[Replay intervention]
    E --> F[Stress-test safety]
    F --> G[Choose next experiment]
    G --> H[Generate new evidence]
    H --> A
```

## 9. Final hypothesis funnel

```mermaid
flowchart TD
    A[Many ideas] --> B[Patient-data compatibility]
    B --> C[Mechanistic coherence]
    C --> D[Independent functional support]
    D --> E[Intervention mimicry]
    E --> F[Exposure / pediatric / PGx]
    F --> G[CIN / tumor safety]
    G --> H[Contradiction search]
    H --> I[Falsification experiment]
    I --> J[1-3 final dossiers]
```
