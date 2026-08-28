# MOSAIC RESCUE — Multi-Agent Workplan

This file is the operating plan for all research agents. Agents should work in parallel but write findings in a common format so evidence can converge instead of fragmenting.

## Shared output format

Every agent report must include:

- **Question**
- **Why this matters to MOSAIC RESCUE**
- **What is already known**
- **What is genuinely uncertain**
- **Primary papers / datasets**
- **Evidence level for each key claim**
- **Contradictory evidence**
- **What data from the hackathon would be required**
- **Concrete test / analysis**
- **Expected visualization**
- **What result would falsify the idea**
- **Decision recommendation: pursue / conditional / park / reject**

Place reports in `research/agent_findings/`.

## Workstream A — Dataset reality check

### Mission
Determine exactly what the hackathon dataset contains before anyone assumes single-cell, longitudinal, RNA, structural, or cytogenetic data.

### Questions
- What are the exact files and formats?
- VCF only or BAM/CRAM too?
- Single-cell?
- Bulk RNA-seq?
- Longitudinal samples?
- Clinical karyotype?
- Tissue/source metadata?
- Phenotype/HPO data?
- Family data / parental samples?

### Deliverables
- modality table
- data limitations table
- branch activation matrix
- update to `research/open_questions.md`

### Blocking status
**Highest priority.** This decides whether Patient-as-Screen and forecasting are direct patient analyses or only externally supported hypotheses.

---

## Workstream B — Causal variant and MVA mechanism

### Mission
Build the strongest possible Track 1 reasoning without hard-coding only classic MVA genes.

### Research targets
- BUB1B, TRIP13, CEP57
- expanded MVA / MVA-like gene space
- inheritance patterns
- variant consequence
- splice effects
- regulatory effects
- known functional domains
- phenotype match

### Deliverables
- candidate-gene universe
- variant-prioritization rubric
- mechanism-router rules
- primary references

---

## Workstream C — Patient-as-Screen and natural rescue precedent

### Mission
Determine whether constitutional mosaicism can legitimately be treated as a natural perturbation experiment and what precedents exist.

### Research targets
- revertant mosaicism / natural gene therapy
- somatic rescue / somatic reversion
- natural genetic suppressors in human disease
- within-patient clonal selection
- lineage-specific mosaicism
- survivorship and ascertainment bias

### Key question
What would make our use of within-patient variation more than a metaphor?

### Deliverables
- precedent map
- methodological requirements
- failure modes
- falsifiable definition of “natural rescue”

---

## Workstream D — Ghost Karyotypes and fitness landscape

### Mission
Test the idea that **missing states contain information**.

### Research targets
- aneuploid state generation probabilities
- chromosome-specific viability
- fitness landscapes of aneuploid karyotypes
- ALFA-K and related methods
- expected-vs-observed state modeling
- sampling/detection bias
- longitudinal/clonal transition models

### Deliverables
- formal definition of Ghost Karyotype
- null model options
- uncertainty strategy
- conditions under which depletion can be interpreted as selection
- candidate visualization

---

## Workstream E — Synthetic rescue / dosage suppressors

### Mission
Find the strongest functional-genomics route from patient observation to compensatory mechanism.

### Research targets
- synthetic rescue / synthetic viability
- dosage suppressors
- genetic interaction maps
- DepMap limitations
- CRISPR screens
- Perturb-seq
- BioGRID / interaction networks
- cross-species suppressor conservation
- deep mutational scanning where relevant

### Deliverables
- rescue-evidence scoring model
- independent-validation rule
- cancer-to-constitutional-disease transfer limitations
- datasets/tools shortlist

---

## Workstream F — Structural mechanism / AlphaFold decision branch

### Mission
Find cases where structure changes a decision rather than decorating the project.

### Research questions
- Is the candidate variant missense and structurally interpretable?
- Is it in a known interface or catalytic region?
- Are experimental structures available?
- Can FoldX/Rosetta/validated interface metrics estimate a plausible effect?
- Does the result distinguish loss of stability from loss of interaction?
- Could the mechanism make pharmacological chaperoning or stabilization relevant?

### Must investigate
- AlphaFold / AlphaFold 3 appropriate uses and limitations
- experimental MCC / BUBR1/BUB3/MAD2/CDC20 structures if relevant
- AlphaMissense / protein language model evidence as supporting—not decisive—evidence
- licensing / reproducibility constraints

### Deliverables
- structural decision tree
- allowed vs prohibited claims
- tools and controls
- exact trigger conditions for notebook 12

---

## Workstream G — Aneuploid stress transfer biology

### Mission
Identify unexpected but defensible mechanistic transfers from other fields.

### Priority branches
- proteostasis
- mPOS / mitochondrial precursor overaccumulation
- mitochondrial import stress
- ROS
- senescence
- cellular competition
- p53 / MYC relative fitness
- interferon only if a signature is actually present
- aging / neurodegeneration parallels where mechanistically justified

### Deliverables
- pathway evidence matrix
- patient-data requirement per pathway
- measurable endpoints
- therapeutic opportunities and tumor-risk counterarguments

---

## Workstream H — Forecasting and counterfactual intervention

### Mission
Determine what kind of prediction is scientifically defensible.

### Research targets
- longitudinal single-cell forecasting
- state-transition models
- fitness-landscape forecasting
- CellOT / optimal transport perturbation models
- active learning / optimal experimental design
- counterfactual perturbation response
- uncertainty calibration

### Critical distinction
**Forecasting cellular states ≠ predicting the child’s clinical future.**

### Deliverables
- minimum data requirements
- validation plan
- scenario-simulation fallback
- “next best experiment” framework

---

## Workstream I — Intervention mimicry and phenotypic replay

### Mission
Only after a mechanism exists, identify interventions that reproduce the compensatory state.

### Research targets
- LINCS / CMap
- JUMP Cell Painting
- perturbation transcriptomics
- morphological profiling
- target-based drug databases
- approved-drug status
- pharmacological chaperones / pathway modulators when mechanism-specific

### Deliverables
- two-independent-route rule for nomination
- mechanism-to-drug mapping method
- reproducibility limitations
- candidate ranking rubric

---

## Workstream J — Safety, PGx, pediatric context

### Mission
Try to kill every apparently attractive intervention.

### Research targets
- tumor predisposition by causal gene/context
- CIN effects
- proliferation/apoptosis effects
- tissue exposure
- pediatric use/precedent
- pharmacogenomics / CPIC when drug-gene guidance exists
- contraindications and developmental concerns

### Deliverables
- Safe Rescue Corridor metrics
- stop criteria
- PGx checklist
- risk evidence table

---

## Workstream K — Scientific visualization

### Mission
Create figures that make a domain expert stop and inspect the result.

### Deliverables
- karyotype map
- observed-vs-expected chromosome-state view
- Ghost Karyotype map
- 3D / contour fitness landscape
- clonal/state transition graph
- protein-complex damage map if structural branch activates
- rescue trajectory plot
- Safe Rescue Corridor plot
- evidence convergence graph

See `docs/visualization_plan.md`.

---

# Convergence meeting rule

An idea enters the **core project** only if:

1. it addresses the actual dataset or a validated external dataset,
2. at least one agent can state a falsifiable prediction,
3. another independent evidence route exists or is realistically obtainable,
4. major contradictory evidence has been searched,
5. the result changes a decision.

If an idea is merely cool, it stays in `research/crazy_ideas.md` until it earns promotion.
