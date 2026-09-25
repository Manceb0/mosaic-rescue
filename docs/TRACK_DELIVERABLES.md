# Track results and submission readiness

Audit: 25 September 2026. Scientific results, prepared files and confirmed submission are different states. No platform receipt or jury score was verified in this audit.

## Track 1 — causal investigation

**Result:** BUB1B is the leading hypothesis: frozen A0 rank 4, later frequency-corrected sensitivity rank 1; Exomiser ranks it 2 of 398 genes using the same VCF. The truncating allele reaches research Likely Pathogenic; the missense remains VUS and phase is unresolved. These results do not establish a diagnosis.

The closed structural search emitted no CNVpytor RD+BAF CNV or xTea/SCRAMble MEI overlapping the gene body. Read-level metrics remain descriptive; a complex insertion is not excluded. Technical recovery of both alleles is not independent biological validation.

Evidence: [report](../reports/TRACK1_REPORT.md), [ranking notebook](../notebooks/01_TRACK1_GENOME_WIDE.ipynb), [allele curation](../notebooks/02_BUB1B_ALLELE_CURATION.ipynb), [structural and regulatory investigation](../notebooks/04_HIDDEN_SECOND_ALLELE.ipynb).

## Track 2 — rescue hypotheses

**Result:** a preclinical experimental portfolio with three different roles, not a ranked therapeutic winner.

| Arm | Research role | Decision-changing failure |
|---|---|---|
| Azithromycin | Allele-directed readthrough hypothesis | No useful functional product under the tested conditions |
| Arimoclomol | Falsification sentinel for pharmacological engagement | No engagement despite an informative positive control |
| Sirolimus | Adversarial safety comparator, not a therapeutic nominee | Increased clonogenic survival of unstable cells triggers a veto |

The bounded evidence dossier has 8 bridges × 10 dimensions, with 61 of 80 cells empty. These are search gaps, not proof of universal absence. No patient-specific drug efficacy or safe rescue has been demonstrated. Function, segregation and clonogenic survival must be assessed together, with controls.

Evidence: [report](../reports/TRACK2_REPORT.md), [evidence matrix](../figures/pub/fig07_track2_evidence_matrix.svg), [portfolio and controls](../figures/pub/fig08_track2_portfolio.svg), [safe-rescue notebook](../notebooks/07_TRACK2_SAFE_RESCUE.ipynb).

## Official requirements → local artifacts

Requirements checked against the official submission source: [Track 1](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026/blob/main/tabs/submit_track1.py), [Track 2](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026/blob/main/tabs/submit_track2.py).

| Track | Required material | Local status | Remaining action |
|---|---|---|---|
| 1 | Ranked GRCh38 CSV, at most 10 candidate rows, EPCR and finding type | Local ignored CSV exists: two rows, primary and secondary; official column names present | Review subjective EPCR, incidental-finding handling and current rationale; filename needs username/team and approach |
| 1 | PDF or Markdown methods/evidence report | `reports/TRACK1_REPORT.md`; an older packaged copy also exists locally | Reconcile final package with current master; add username/team filename |
| 1 | Reproducible GitHub code and configuration | Repository, scripts and notebooks exist | Review sharing contents; public availability required after event |
| 2 | PDF or Markdown report supporting repositioning and variant mechanism | `reports/TRACK2_REPORT.md` | Final consistency review; username/team filename |
| 2 | GitHub repository | Same repository | Review shareable package |
| 2 | Three-minute pitch hosted on YouTube or Vimeo | Script in `JUDGE_PATH.md`; final hosted video not verified | Record, upload and supply URL |
| Both | AI-use disclosure: provider, plan/tier and data-handling setting | Exact account/settings confirmation remains pending | Document actual settings, not assumed terms |
| Both | Methods template available; standalone methods description recommended | Methods distributed across reports and code | Check completeness against official template |
| Both | Platform submission | No receipt checked | Submit only after package review; retain confirmation |

Track 1 automatic evaluation uses rank points and F-max; local prioritization ranks are **not** leaderboard results. Track 2 is reviewed qualitatively. A completed analysis or passing verifier is not a submission receipt.

## Concrete package gaps found

- The Track 1 generator's EPCR rationale still says BAM/CRAM is missing. That rationale predates the completed structural work and needs reconciliation before regenerating the submission. The current subjective EPCR values are not calibrated model probabilities.
- The generator describes Exomiser as independent; it is another method on the same VCF, not an independent biological sample.
- A local packaged report is present, but synchronization with the current master was not established here.
- Formal dataset citation, maintainer fields, AI settings and final sharing review remain on the existing readiness list.

This audit does not upload files, publish data, change EPCR or claim that missing biological validation can be supplied by documentation.
