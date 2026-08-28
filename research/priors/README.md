# External Quantitative Priors

Version-pinned external quantitative inputs. Flagged as a gap by the Patient-as-Screen audit:
every proposed normalization analysis consumes one of these, and without pinning the normalization
is not reproducible.

## Why this directory exists

Several planned analyses do not compare patient data against itself. They compare it against an
externally estimated expectation — a per-chromosome missegregation rate, a detection-power curve,
a stress signature. If those numbers drift between notebook runs, or if two agents use different
versions of the same table, the results are not comparable and the normalization is not
reproducible.

Each prior gets its own file recording: source (PMID/DOI), the exact table or figure the numbers
came from, the version or access date, the measurement system, and its uncertainty.

## Required priors

| Prior | Source | Status | Consumed by |
|---|---|---|---|
| Per-chromosome missegregation frequency by nuclear position | Klaasen & Kops, *Nature* 2022 (PMID 35831506) | **Needed** | Ghost Karyotype null model; any observed-vs-expected analysis |
| Mechanism-dependent missegregation bias | Worrall et al., *Cell Rep* 2018 (PMID 29898405) | **Needed** | Error bars on the generation prior — bias is ~5× and flips sign with mechanism |
| Mitotic aneuploidy rate vs chromosome length | McCoy et al., *PLoS Genet* 2015 (PMID 26491874), 28,052 blastomeres | **Needed** | Generation prior (r = 0.734 with chromosome length) |
| Aneuploid transcriptional stress signature | Sheltzer et al., *PNAS* 2012 (PMID 22802626) | **Needed** | Separating chromosome-specific effects from the shared aneuploidy response |
| Expression-based CNV caller false-positive floor | Villarroya-Beltri et al., *Sci Adv* 2022 (PMID 36322655) — 4.0% in healthy controls | **Needed** | Detection-power floor for any scRNA-derived CNV call |
| Tissue-specific chromosome fitness | Sack et al., *Cell* 2018 (PMID 29576454) | **Needed** | Cross-tissue log-ratio analysis |

## Critical caveat carried from the audits

The generation prior is **not** a solved input. Worrall 2018 shows chromosome-specific
missegregation bias of roughly 5× that changes sign depending on the perturbation mechanism, and
none of it was measured in MVA. Depletions below roughly 5-fold are therefore unidentifiable at
**any** sample size — this is a property of the prior, not of the sample.

Any figure built on these priors must display that uncertainty. A clean observed-vs-expected plot
that hides a 5× prior error bar is the most likely way this project produces a confounded result
that looks publishable.

## Format

One Markdown file per prior, named `<short-slug>.md`, containing the numbers themselves in a
Markdown table so they are diffable in git. Do not store priors only as a citation — store the
values, so a reviewer can see exactly what was used.
