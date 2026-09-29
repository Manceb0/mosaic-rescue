# What is still needed for a convincing submission

Editorial and scope audit, 24 September 2026. This is not a new clinical assessment, a
reopening of GO 2B, or a prediction of the jury's score.

## Verified rubric and the 26 September target

The [official site](https://sagebio-rare-disease-real-kid-mva-hackathon-2026.hf.space/),
checked on 24 September 2026, publishes for Track 2: scientific rigour **35 %**, potential
impact **25 %**, innovation **25 %**, scalability **15 %**. Track 1 combines rank points and
F-max with a separate review of the method. Track 2 asks for a report, a repository and a
three-minute video. The published calendar closes submissions on **24 October, 23:59 UTC**;
the maintainer's own target is **26 September**.

| Criterion | Documented strength | Priority improvement for our submission |
|---|---|---|
| Rigour, 35 % | Frozen artifacts, controls and contradictions | Align statuses, mechanism and limits; resolve EXP-012c documentally |
| Impact, 25 % | Case-specific questions | Explain which decision each experiment enables, without promising efficacy |
| Innovation, 25 % | Audit of the BAF explanation; an assembled, falsifiable design. The safety corridor is shared with another public hackathon repository and is not claimed as ours | Put the ablation in the foreground; state prior art openly (Track 2 §9); present "Can the patient become the screen?" only as a proposal |
| Scalability, 15 % | Modular code and traceability | Show replaceable inputs; state that no second case has validated the method |

Plan to the 26th: **24**, coherence and the written story; **25**, review of the reports
against the rubric and pitch rehearsal; **26**, package checks, pending fields, review of the
shareable material and submission by the maintainer. None of this implies a submission made.

## Diagnosis of the project

There is technical depth and falsifiable results. The presentation problem is that the reader
receives many objects before understanding which decision each one changed. Computational
robustness (tests, hashes, controls) is further developed than patient-specific biological
validation. No figure can close that gap.

## Priorities by scientific value

| Priority | Gap | Useful action | What it would allow us to claim |
|---|---|---|---|
| P0 | Contradictory statuses across documents | Reconcile registry, reports and script; "BAM missing" and "splicing ruled out" already corrected | One verifiable version of what was done |
| P0 | EXP-012c remains preregistered in the registry | Locate its output and check it against the protocol before concluding | PRESENT / ABSENT / TECHNICALLY UNRESOLVED status with provenance |
| P0 | Rubric, fields and formal dataset citation | Complete the package against the official requirements | A complete submission, not scientific superiority |
| P1 | Phase unresolved | Parents or targeted long-molecule phasing | Configuration of the pair; not pathogenicity on its own |
| P1 | Specific missense function | Abundance/turnover and checkpoint assay with controls | Separate compatible mechanisms from refuted ones |
| P1 | Rescue not demonstrated | Measure activity, segregation and clonogenic survival with informative controls | Evaluate rescue and the veto for tolerance of instability |
| P2 | Validity of the mosaicism detector | Matched controls and comparison with a phased method | Comparative performance; not demonstrated today |
| P2 | MitoRead has no validated interpretation | Controls with an identical pipeline and cell composition | An interpretable difference, not only a descriptive ratio |
| P2 | Generalisation from one case | Blinded evaluation on previously solved cases, without changing rules after seeing labels | Empirical transferability; the code census does not show it |
| Conditional | EXP-024 not executed | Review relevance and the conditions of the frozen protocol | Calibration of a prediction, never an experimental function |

Clinical data that would clarify the residual nephrocalcinosis are also missing. The AE2 query
remains not executed under data policy; Docker does not change that condition. PGx is not
evaluated, but it does not displace phase or function and does not demonstrate efficacy: it
would only make sense with a concrete pharmacological question and within the authorised scope.

## Figures with the most remaining value

1. **The ranking change under the frequency audit.** Notebook 01 already contains the A0 /
   A0-FREQFIX comparisons. Promoting that evidence to a main piece shows why the decision
   changed; another decorative Manhattan plot is not needed.
2. **The 2 × 2 BAF ablation, figure added.** Shows homolog direction × depth and separates
   the signed from the absolute statistic, using only the EXP-015c output, labelled POST-HOC.
   It says more about originality than an illustration of chromosomes.
3. **Controls and decisions of the rescue assay.** A visual protocol with readouts, positive
   controls and rejection rules; no fictitious efficacy bars.
4. **Causal uncertainty map.** Already present in the syntheses. It must accompany the measured
   figures, not replace them.

ISM and contacts are not missing: they exist and are in the atlas. A cell × chromosome atlas,
survival curves of the patient's cells, and RNA/protein validation would all need new
observations. They cannot be obtained by restyling the current files.

## The story for the jury

**Question → observation → adversarial test → limit → experiment that changes the decision.**
Three moments: the frequency audit changes the ranking; the structural negative narrows without
excluding; the safety criterion can reject an apparent rescue. The falsification of our initial
BAF explanation is a methodological result that deserves space. The patient's mechanism and any
intervention remain to be demonstrated.

## Reading format

The primary reading path is the [Track 1 report](../reports/TRACK1_REPORT.md), the
[Track 2 report](../reports/TRACK2_REPORT.md) and the executed notebooks, all of which render
directly on GitHub. The interactive [HTML article](research_story.html) is an optional extra
that has to be opened locally; nothing in the argument depends on it.

Docker Engine responded (29.7.2) with no containers visible in the active context during this
review. That describes infrastructure, not the availability of samples.
