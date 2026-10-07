# FINAL SUBMISSION READINESS

Audit: 7 October 2026, after the narrative freeze (`docs/DECISIONS.md`). **Science: closed. Narrative:
frozen. Code and figures: ready (`python src/verify.py` green). Hackathon submission: not yet closed.**
Prepared files, uploaded files and a confirmed submission are different states. No platform receipt or
jury score exists at the time of this audit.

## The submission pass, in order

| # | Step | State on 7 Oct 2026 | Who closes it |
|---|---|---|---|
| 1 | **Track 1 CSV** | Regenerated with `src/submission/track1_csv.py`; `validate_track1.py`: **valid**. Byte-identical to the copy in the delivery folder (SHA256 `b86bb4b0…`). Filename `mosaic-rescue_panelfree-genomewide.csv` follows `<team>_<approach>.csv`. Two rows: BUB1B pair (primary, epcr 0.75) and LZTR1 (secondary, epcr 0.05). The generator no longer says BAM/CRAM is missing and no longer calls Exomiser independent biological evidence | Team: confirm the two **subjective** epcr values (rationale in `EPCR_RATIONALE`, not calibrated probabilities) |
| 2 | **Reports (Markdown)** | Exported on 7 Oct from the current masters by `src/submission/export_reports.py` to `work/submission/subir/` and the delivery folder. The 26 Sep package (old narrative) is kept in `work/submission/subir/_superseded_2026-09-26/`; its PDFs were moved out of the upload folder | Done |
| 2b | **Reports (PDF)** | **Not generated**: the exporter needs the Python package `markdown` (not installed). The repository is private, so the Markdown copy's image links will not render for the jury; the PDF embeds the figures | Install `markdown`, rerun the exporter, look at both PDFs |
| 3 | **Methods form (xlsx)** | Now written **from** the report appendices (the master), not the other way round. Before 7 Oct the exporter copied the Excel into the report; with the 26 Sep Excel it would have reverted the HLA-DRB1, «external method» and EXP-029 corrections. Both abstracts are under 500 words (368 and 433) | Done |
| 4 | **Dataset citation** | Both reports still say *«Dataset citation: to be completed before submission»* (Track 1 §11, Track 2 §13) | Copy the exact reference from the authorised Synapse page (`syn76251147`); nothing invented |
| 5 | **AI-use disclosure** | Written in both reports and in the form: Anthropic (Claude Pro via Claude Code, Opus models, training on user content disabled) and OpenAI (ChatGPT Plus, editorial illustrations only, training disabled, no patient data) | Confirm that plan and setting match the accounts actually used |
| 6 | **Privacy / public-release review** | `src/sanitize_scan.py` and `verify.py`: clean of forbidden values and generic patterns (coordinates, HGVS, sample IDs, dbSNP, local paths). **Not sufficient for publication.** Known exception, declared in the README: `figures/pub/fig11_mei_sv_adjudication_map.svg` carries case-specific structural-call positions and is an internal figure, not a presentation asset. The repository must stay private until a human review decides what is shared | Team decision (publishing patient-specific information is a stop condition for the agent) |
| 7 | **Three-minute video** | Script ready and in the final order (`docs/JUDGE_PATH.md`); no hosted video exists | Record, upload to YouTube or Vimeo, keep the URL |
| 8 | **Upload and receipt** | Nothing uploaded | Upload Track 1 (CSV + report), Track 2 (report + repo URL + video URL); save the confirmation |

## What each track delivers

**Track 1.** Panel-free genome-wide analysis converged on `BUB1B`: #1 in 14 of 15 sensitivity analyses
of the same genome; frozen A0 #4 and A0-FREQFIX #1, always reported together; Exomiser, an external
method on the same VCF, #2 of 398. Genotype coherent with MVA1 (truncating Likely Pathogenic + rare
missense VUS); phase unresolved, so a strong causal hypothesis, not a diagnosis. Exomiser's #1,
`HLA-DRB1`, is an open audit flag. [Report](../reports/TRACK1_REPORT.md).

**Track 2.** Human MVA patient cells establish that BUBR1 dysfunction is rescuable at the checkpoint
level (genetic re-expression; other alleles; no drug). Three experimentally distinct arms, not a
winner: azithromycin (allele-directed; computationally weakened by EXP-029, not eliminated),
arimoclomol (proteostasis sentinel, with a verified counterexample) and sirolimus (adversarial safety
comparator), judged by the Safe Rescue Corridor. No drug has been tested in a `BUB1B` patient cell.
[Report](../reports/TRACK2_REPORT.md).

## Official requirements

Checked against the official submission source: [Track 1](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026/blob/main/tabs/submit_track1.py),
[Track 2](https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026/blob/main/tabs/submit_track2.py).

| Track | Required material | Where it is |
|---|---|---|
| 1 | Ranked GRCh38 CSV, at most 10 rows, epcr and finding type | Delivery folder, `mosaic-rescue_panelfree-genomewide.csv` (outside the repository: it holds patient coordinates) |
| 1 | PDF or Markdown methods/evidence report, methods form inside | `mosaic-rescue_track1_report.md` (PDF pending, step 2b) |
| 1 | Reproducible code and configuration | This repository (private until step 6) |
| 2 | Report supporting repositioning and variant mechanism | `mosaic-rescue_track2_report.md` (PDF pending, step 2b) |
| 2 | Repository and three-minute video URL | Repository URL; video pending (step 7) |
| Both | AI-use disclosure | In both reports and the form (step 5 confirms it) |

Track 1 automatic evaluation uses rank points and F-max; local ranks are **not** leaderboard results.
Track 2 is reviewed qualitatively. A green verifier is not a submission receipt.
