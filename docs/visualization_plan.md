# MOSAIC RESCUE — Scientific Visualization Plan

> ⚠️ **SUPERADO.** El inventario real del dataset (`docs/01_MASTER_BRIEF.md` §1) invalida
> las ramas que este documento describe: no hay RNA-seq, single-cell, longitudinal ni
> cariotipo celular. Ver `docs/00_ESTADO_Y_OBSOLESCENCIA.md`. Se conserva como registro.

---

The goal is not to make generic dashboards. Each figure should expose a biological pattern, a model assumption, or a decision boundary that a geneticist, cell biologist, or computational biologist can inspect.

## Figure 1 — Patient data map

### Purpose
Show exactly which modalities exist and which analyses they activate.

### Visual
A modality matrix with rows = files/samples and columns = WGS, VCF, BAM/CRAM, bulk RNA, single-cell, longitudinal, karyotype, phenotype/HPO, family data.

### Why it matters
This makes methodological honesty visible immediately.

---

## Figure 2 — Causal variant evidence map

### Purpose
Show why the lead variant ranks above alternatives.

### Visual options
- chromosome ideogram with candidate loci,
- gene/domain lollipop plot,
- evidence-convergence heatmap,
- inheritance + phenotype + consequence panel.

### Avoid
A simple ranked bar chart as the headline figure.

---

## Figure 3 — Mechanism Router

### Purpose
Translate genotype into a concrete molecular failure mode.

### Visual
Decision tree: dosage vs stability vs interface vs catalytic vs splice/regulatory.

If structure is activated, place the residue on an experimental/validated complex and show the affected interface/domain.

---

## Figure 4 — Mosaic state atlas

### Purpose
Make the patient-as-screen idea visible.

### If single-cell exists
Possible views:
- UMAP annotated by inferred/measured karyotype,
- alluvial/Sankey from lineage or state to karyotype,
- chromosome-state heatmap per cell cluster,
- clone/state tree.

### If only bulk DNA exists
- B-allele-frequency + read-depth chromosome tracks,
- copy-number state fingerprint,
- mosaic fraction confidence plot.

---

## Figure 5 — Ghost Karyotype map

### Purpose
Show **negative space**: states expected under a null model but depleted/absent in observation.

### Visual
Observed-vs-expected matrix where cells represent chromosome-state combinations.

Recommended derived views:
- depletion residual map,
- uncertainty-aware “ghost score”,
- chromosome-specific enrichment/depletion ideogram.

### Scientific requirement
Expected frequencies must come from an explicit generation/sampling model; absence alone is not evidence of selection.

---

## Figure 6 — Evolutionary fitness landscape

### Purpose
Turn relative persistence into an interpretable state-space.

### Visual options
- 3D surface / contour landscape,
- state graph with node height/size representing inferred fitness,
- valleys and peaks for low/high persistence states.

### Important
The landscape must be labeled as **inferred/model-based**, not literal measured fitness unless the data directly justify it.

---

## Figure 7 — Clonal / state transition graph

### Purpose
Show where states may come from and where they may go.

### Visual
Directed graph:
- nodes = karyotype/cell states,
- edges = plausible transitions,
- edge width = transition support/probability,
- node outline = observed vs predicted vs ghost.

This is the core visual for Mosaic Forecast.

---

## Figure 8 — Synthetic rescue evidence network

### Purpose
Show why one compensatory mechanism has more support than another.

### Visual
Knowledge/evidence graph:
- patient observation,
- candidate gene/pathway,
- CRISPR/Perturb-seq evidence,
- cross-species evidence,
- interaction evidence,
- drug/perturbation connection.

Edge types must indicate **association vs functional support**.

---

## Figure 9 — Structural damage map (conditional)

### Trigger
Only if the causal variant is structurally informative.

### Visual
Side-by-side:
- WT complex/structure,
- variant site,
- interface/contact region,
- FoldX/Rosetta/validated structural metric where appropriate,
- experimental residues/known domains.

### The figure must answer
**What scientific decision changes because of this structure?**

If the answer is “none,” skip the figure.

---

## Figure 10 — Cellular stress mechanism panel

### Purpose
Show a measurable downstream mechanism such as mPOS/proteostasis, mitochondrial stress, senescence, or cell competition.

### Examples
- mitochondrial-import vs precursor-load scatter/manifold,
- p62/proteostasis signature heatmap,
- ROS / mitochondrial signature panel,
- MYC/p53 relative-fitness view for cell competition.

Only include branches supported by available data or strong external validation.

---

## Figure 11 — Rescue Replay

### Purpose
Show how candidate interventions move the state relative to the discovered compensatory state.

### Visual
Trajectory/manifold:
- patient baseline,
- natural tolerated/rescue state,
- candidate A/B/C predicted or observed perturbation states.

### Key idea
The target is not “average healthy”; it is **mechanistically justified rescue**.

---

## Figure 12 — Safe Rescue Corridor

### Purpose
Make the safety trade-off impossible to ignore.

### Visual
2D or 3D decision surface.

Example axes:
- x = desired rescue score,
- y = CIN / abnormal-clone risk,
- optional z = exposure plausibility.

Candidate zones:
- beneficial + low risk = Safe Rescue Corridor,
- beneficial + high evolutionary risk = reject,
- low benefit = reject.

---

## Figure 13 — Hypothesis survival funnel

### Purpose
Show scientific discipline.

### Visual
Candidate ideas passing through:
1. patient evidence,
2. independent validation,
3. mechanism,
4. safety,
5. exposure/PGx,
6. contradiction search.

Final output should be **1–3 surviving hypotheses**, not dozens.

---

## Figure 14 — Next Best Experiment

### Purpose
End with action.

### Visual
Experiment candidates ranked by expected information gain or ability to distinguish hypotheses.

Could show:
- current hypothesis probabilities/weights,
- expected outcome under each hypothesis,
- information gain per experiment.

---

# Notebook visual style

Every major notebook should have:

1. **one diagnostic/QC figure,**
2. **one primary scientific figure,**
3. **one robustness/uncertainty figure.**

Interactive Plotly is appropriate for exploration; static publication-style Matplotlib figures should also be exportable for the report/pitch.

## Visualization stack candidates

- Matplotlib
- Plotly
- NetworkX / igraph
- pyCirclize or chromosome-ideogram tooling where justified
- Scanpy visualizations if single-cell exists
- py3Dmol / Mol* compatible exports for structures
- Sankey/alluvial plots

## Anti-patterns

Do not use:
- 3D for decoration,
- rainbow heatmaps without reason,
- UMAP as proof of biological separation,
- network hairballs,
- a protein structure that changes no decision,
- a “risk score” with arbitrary weights hidden from the reader.

Every visual should let a domain expert ask: **what exactly would I have to believe for this picture to be true?**
