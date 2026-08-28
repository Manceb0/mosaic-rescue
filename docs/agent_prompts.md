# MOSAIC RESCUE — Ready-to-Run Agent Prompts

These prompts are designed for independent research agents. Each agent should read `README.md`, `AGENTS.md`, `docs/research_protocol.md`, and `research/agent_findings/README.md` before working.

## Universal instruction block

Append this block to every research assignment:

> Work as a skeptical scientific collaborator, not a brainstormer. Prioritize primary literature and official datasets. Separate direct evidence from inference. For every important claim, state the model/system, evidence level L0-L5, and whether the result transfers cleanly to pediatric constitutional MVA. Actively search for contradictory evidence, failed replication, tissue dependence, dosage dependence, cancer-specific artifacts, and methodological confounding. Do not assume any hackathon data modality that has not been confirmed. End with: Pursue / Conditional / Park / Reject; exact data required; proposed analysis; expected scientific visualization; strongest alternative explanation; and a falsification criterion. Write the result in the standard `research/agent_findings/` format.

---

## Prompt A — Dataset reality check

Inventory the exact Rare Disease, Real Kid MVA Hackathon dataset. Determine every file, format, sample, tissue, genome build, family relationship, and timepoint. Explicitly verify whether VCF, BAM/CRAM, bulk RNA-seq, scRNA/single-cell, clinical karyotype, phenotype/HPO, longitudinal samples, proteomics, imaging, fibroblast, iPSC, or organoid data exist. Build a branch-activation matrix for MOSAIC RESCUE. Do not infer a modality from file count or publicity text.

---

## Prompt B — Track 1 and mechanism router

Build a comprehensive MVA/MVA-like causal-gene and variant framework. Include BUB1B, TRIP13, CEP57 but actively search beyond the classic genes. For each relevant gene, map inheritance, phenotype, spindle-checkpoint/centrosomal/cohesion or related function, tumor-predisposition context, known functional domains and key experimental evidence. Propose a variant-ranking rubric and a mechanism router that distinguishes dosage/expression loss, instability/degradation, complex-interface disruption, catalytic loss, splice/regulatory effects and unresolved mechanisms. Search for evidence that would falsify or downgrade a famous-gene-first interpretation.

---

## Prompt C — Patient-as-Screen / natural rescue

Investigate whether constitutional mosaicism can be used as a natural perturbation experiment. Deeply review revertant mosaicism, somatic reversion/rescue, natural gene therapy, compensatory variants, lineage-specific clonal selection and human examples where surviving clones reveal a rescue mechanism. Distinguish direct precedent from analogy. Determine what patient data would be required to claim that MVA states provide mechanistic evidence rather than a storytelling metaphor. Identify survivorship, tissue, sampling and ascertainment biases and design falsification tests.

---

## Prompt D — Ghost Karyotypes / negative space

Investigate whether aneuploid states that are absent or depleted relative to an explicit generation model can reveal selection. Review chromosome-specific aneuploid viability, missegregation probabilities, aneuploid fitness landscapes, ALFA-K and related methods. Propose a formal Ghost Karyotype definition, expected-frequency/null models, confidence/uncertainty criteria, technical detection controls and minimal dataset requirements. Search for reasons observed depletion might not be biological selection.

---

## Prompt E — Synthetic rescue / dosage suppressors

Investigate synthetic rescue, synthetic viability, dosage suppressors and genetic compensation relevant to MVA/aneuploidy. Search CRISPR screens, Perturb-seq, DepMap, BioGRID/genetic-interaction maps, yeast/model-organism suppressors and deep mutational scanning where relevant. Design a rescue-evidence score and a rule requiring independent evidence routes. Explicitly analyze why cancer-cell dependencies may fail to transfer to pediatric constitutional disease.

---

## Prompt F — AlphaFold / structural decision branch

Determine where structural analysis could change a therapeutic decision for an MVA causal variant. Search experimental structures first. Then evaluate appropriate roles for AlphaFold/AlphaFold 3, FoldX, Rosetta, interface analysis, molecular dynamics if justified, AlphaMissense and protein language models. Questions include: stability loss vs interface loss vs catalytic disruption; mitotic-checkpoint complex effects; whether stabilization/pharmacological chaperoning is mechanistically plausible. Do not use naive WT-vs-mutant pLDDT as proof. Verify current licensing/reproducibility constraints. Produce a decision tree specifying when structure should be skipped.

---

## Prompt G — Aneuploid stress transfer biology

Search for unexpected but defensible cross-domain mechanisms caused by aneuploidy/CIN that could explain tolerated versus non-tolerated states. Prioritize proteostasis, mitochondrial precursor overaccumulation stress (mPOS), mitochondrial import stress, ROS, senescence, cell competition, relative MYC/p53 fitness and other mechanistically specific pathways. Investigate transfers from cancer, aging, neurodegeneration and evolution only where the mechanism truly overlaps. For each branch state what patient modality and measurable endpoint would be required.

---

## Prompt H — Forecasting / counterfactuals / active learning

Investigate methods that can forecast future cellular states or perturbation responses without pretending to predict the child's clinical future. Review ALFA-K, longitudinal single-cell state models, optimal transport/CellOT-like methods, fitness landscapes, perturbation-response forecasting and uncertainty calibration. Define minimum data requirements and a scenario-simulation fallback. Then investigate active learning / optimal experimental design to rank the next experiment by expected information gain between competing hypotheses.

---

## Prompt I — Intervention mimicry / Rescue Replay

Once a compensatory mechanism is assumed to be independently validated, investigate how to find approved interventions that reproduce that mechanism. Review LINCS/CMap, JUMP Cell Painting, perturbation transcriptomics, target-based pharmacology and other phenotypic reversal methods. Design a two-independent-route nomination rule. Explicitly investigate CMap/Cell Painting reproducibility limits and prevent generic signature reversal from dominating the evidence.

---

## Prompt J — Safe Rescue Corridor / PGx / pediatric safety

Design an adversarial safety framework for any MVA rescue intervention. Investigate gene-specific tumor predisposition, CIN/missegregation effects, proliferation, apoptosis escape, clonal fitness, tissue exposure, pediatric PK/precedent and actionable pharmacogenomics/CPIC. Define quantitative or categorical stop rules for a Safe Rescue Corridor. The goal is not maximum aneuploid-cell survival; it is improved function without increasing evolutionary danger.

---

## Prompt K — Scientific visualization

Design publication-grade scientific visualizations for this project, not a generic dashboard. For each planned notebook, identify the visual grammar a domain scientist would expect: chromosome ideograms, CNV/BAF tracks, karyotype heatmaps, UMAP only when appropriate, clonal/state graphs, expected-vs-observed residual maps, 3D/contour fitness landscapes, structural interface maps, evidence networks, perturbation manifolds, Rescue Replay trajectories, Safe Rescue Corridor surfaces and Next Best Experiment information-gain panels. Every proposed figure must state the biological quantity encoded, uncertainty representation and common ways it could mislead.

---

# How to use agent outputs

An agent report is **not automatically accepted**. Findings must be entered into `research/evidence_registry.md`, contradictions into `research/contradictions.md`, and only hypotheses satisfying the promotion criteria may move into `hypotheses/`.

The strongest outcome is not consensus by repetition. It is **convergence from independent evidence routes**.