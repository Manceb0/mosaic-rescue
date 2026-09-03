# MOSAIC RESCUE — Track 1 report

**Variant identification in one paediatric genome with suspected mosaic variegated aneuploidy**

Rare Disease, Real Kid: MVA Hackathon 2026
Repository: <https://github.com/Manceb0/mosaic-rescue>

---

## 1 · Summary

A panel-free, genome-wide search over the proband's WGS nominates **compound-heterozygous
`BUB1B`** (MVA1, OMIM 257300) as the leading causal hypothesis: a truncating allele plus a
missense allele, both rare, both on the MANE transcript.

Two things are reported that a submission optimised for appearances would omit.

**First, the frozen ranking does not put `BUB1B` first.** The preregistered genetics-only
ranking `A0` places it **#4**. Three genes scored above it. Auditing them showed all three
were common polymorphisms with rsIDs whose frequency the annotation had failed to attach. A
later sensitivity analysis, `A0-FREQFIX`, repairs those 33 alleles and returns `BUB1B` to
**#1**. Both numbers are reported together, always. `A0` is never rewritten.

**Second, the phase is unresolved.** No parental samples were provided, and the two alleles
are separated by a gap 13.8× the sequencing fragment length, so read-backed phasing cannot
reach. `PM3` is therefore blocked and the biallelic configuration is a **candidate**, not a
demonstrated finding. The correct description is *candidate compound heterozygosity with
phase unresolved*, and nothing stronger.

A **research secondary/incidental candidate** is also reported: a heterozygous nonsense
variant in `LZTR1`, ClinVar pathogenic/likely pathogenic. It is not proposed as the cause of
this phenotype, and it is **not** presented as a returnable clinical finding: it would require
independent clinical confirmation and appropriate return-of-results handling before it meant
anything to anyone.

## 2 · Data and its limits, established before analysis

Eleven gated files. FASTQ (lane 1, R1/R2) and a VCF are what carry the analysis.

Read quality was assessed before any variant was examined: invariant 149 bp read length, GC
41.3 % against the genome's 41 %, **92.9 % of bases at Q30 or better**, and no poly-G drift.
The data are fit for the question.

What does **not** exist, and what each absence blocks:

| Missing | Consequence |
|---|---|
| Parental genotypes | Phase unresolved; `PM3` blocked |
| Full-depth BAM/CRAM | Structural and copy-number variants untested at the locus |
| RNA-seq | No expression evidence for any regulatory hypothesis |
| Single-cell or longitudinal data | Cell-resolved mosaicism and forecasting not attempted |
| Clinical karyotype | No ground truth for any mosaicism signature |
| Contemporaneous blood count | Mitochondrial readout uninterpretable |

Five of sixteen analysis branches are blocked by missing data, not by method. They are marked
`BLOCKED`, not quietly dropped.

## 3 · Method

**No panel was used for the primary search.** Choosing a panel first and finding `BUB1B` in it
would have been confirmation bias, and the project's own rules forbid it. The pipeline
extracted **13 191 positions → 13 216 alleles** of HIGH and MODERATE consequence across
**6 321 genes**, and scored them on genotype configuration, rarity, consequence severity,
transcript status and quality, with no gene-level prior.

Fifteen ranking analyses were run, differing in whether phenotype and ClinVar were used:

| Analysis | What it uses | `BUB1B` |
|---|---|---|
| `A0_GENETICS` (frozen, preregistered) | genetics only | **#4** |
| `A0-FREQFIX` (later sensitivity) | genetics only, 33 frequency annotations repaired | **#1** |
| `A1_GENETICS_CLINVAR` | + ClinVar | #1 |
| `B0_FULL_PROBAND` | + HPO phenotype (Resnik / Best Match Average) | #1 |
| 11 further leave-one-out and ablation analyses | varies | #1 in 14 of 15 overall |

**An independent external baseline was run on the same VCF.** Exomiser, a method this project
did not write, places `BUB1B` **#2 of 398 distinct genes**, autosomal-recessive model, in both
runs. Agreement between an in-house score and an independent tool is worth more than either
alone.

**Phenotype handling.** Seven HPO terms from the clinical document, plus one family-history
term kept on a separate channel so it cannot contaminate the primary result. A frozen polarity
rule applies: **only documented terms count as positive; anything unmentioned is UNKNOWN,
never negative.** Semantic similarity uses Resnik information content in bits with Best Match
Average aggregation.

## 4 · Curation of the two alleles

Research-grade ACMG/AMP curation, Bayesian points.

**Truncating allele** — `PVS1` (nonsense on the MANE transcript, NMD-predicted),
`PM2_Supporting` (rare). **9 points → Likely Pathogenic.**

**Missense allele** — remains **VUS**. Three criteria were considered and rejected with the
data in front of us:

- **`PM1` does not apply.** The intuition that the residue sits in a hot domain does not
  survive the data: **1 497 ClinVar missense variants across `BUB1B`, 98 % of them VUS, and a
  single P/LP.** There is no demonstrable hotspot anywhere in the gene.
- **`PM3` is blocked** by unresolved phase.
- **`PS3` needs a functional assay** that does not exist for this variant.

Orthologous conservation does support concern: the position sits in the 90th percentile of its
own protein, the chemical property is conserved in 99.2 % of 120 orthologs, and the class of
substitution introduced appears in none of them. **This does not change the ACMG call**, and
it is reported as mechanism, not as evidence of pathogenicity.

## 5 · Competing hypotheses, all audited

The value of a panel-free search is that it surfaces competitors. Every gene that outranked or
closely approached `BUB1B` was audited, cheapest falsifier first: **frequency → zygosity →
mechanism → replication.**

| Competitor | Where it appeared | Verdict |
|---|---|---|
| `CTU2`, `PEX5`, `SLC22A1` | `A0` #1–#3 | **NEGATIVE** — common polymorphisms with rsIDs, up to 313 150 homozygotes in gnomAD |
| `FANCD2` | Exomiser #6 | **NEGATIVE** — three alleles at ~47 % population frequency, all heterozygous, no recessive configuration possible |
| `LZTR1` | `B0` #4 | **NEGATIVE as a cause of MVA** — the syndromic form is recessive and only one allele is present; heterozygous LoF causes adult-onset schwannomatosis, and `LZTR1` has no established role in chromosome segregation |
| `IGBP1` | `B0` #6 | **NEGATIVE** — the only reported disease mechanism is 5'UTR disruption of translation initiation, not coding missense; the association rests on a single family; and `MAX_AF` 1 × 10⁻⁴ is strongly inconsistent with an ultra-rare, penetrant, causal model. The verdict rests on all three together, not on the frequency argument alone |

`FANCD2` deserves a note: it is the Fanconi anaemia pathway, which overlaps MVA in **both**
phenotype and mechanism. It was the most uncomfortable competitor and was audited rather than
avoided.

## 6 · Research secondary / incidental candidate

The proband carries a **heterozygous nonsense variant in `LZTR1`** on the MANE transcript:
high quality (DP 48, GQ 99, allele balance 0.50, PASS), rare (`MAX_AF` 3 × 10⁻⁵), and
classified **pathogenic/likely pathogenic in ClinVar**. It is not an artefact.

It does not explain the reported phenotype, for the reasons in §5. It is submitted with
`finding_type = secondary` and a low `epcr` because it is real and the submission format has a
field for exactly this; the hackathon rules state that secondary and incidental findings are
welcome and do not penalise the automated Track 1 score.

**It is a research candidate, not a returnable clinical result.** Calling it a "secondary
finding" without that qualifier would imply a clinical status it has not earned. Independent
confirmation by an orthogonal method, clinical interpretation and any return-of-results
decision belong to the clinical team, and this project makes no clinical recommendation. It is
also deliberately kept out of the main MVA narrative: it would distract from `BUB1B` and open a
separate and much larger clinical conversation.

## 7 · What would falsify this

- **Parental genotypes showing both alleles in *cis*.** This is the single highest-value
  missing datum, and it would end the biallelic hypothesis outright.
- A variant-specific **BUBR1 abundance assay** showing the missense does not reduce protein
  level or turnover.
- A structural or copy-number variant at another locus explaining the phenotype more
  economically; not excluded, because the pipeline sees only coding SNV/indel.
- A second `LZTR1` allele found by a method this pipeline cannot run, which would reopen
  recessive Noonan syndrome.

## 8 · Submission file

`work/submission/track1_predictions.csv`, generated by `src/submission/track1_csv.py`.

**The CSV is not in the repository, deliberately.** The required format carries chromosome,
position, reference and alternate alleles and the proband identifier for a living minor. That
is precisely what the project's first hard rule forbids committing, even temporarily. The
generator lives in the repository; the file it writes lands in a gitignored directory and is
uploaded by hand. The method is auditable without anyone seeing a coordinate.

Two rows are submitted. Up to ten are allowed, and padding the file with the already-audited
competitors would have been hedging against our own analysis.

`epcr` values are **declared subjective probabilities, not model output**. Their full
justification is in `EPCR_RATIONALE` inside the generator. `BUB1B` is set at 0.75 rather than
higher because the phase is unresolved, the missense is still a VUS, and SV/CNV at the locus
has not been excluded.

## 9 · Reproducibility

```bash
pip install -r requirements.txt
python src/verify.py
```

`verify.py` runs without any patient data: unit tests, module imports (discovered, not
hand-listed), published figure counts recomputed from the executed notebooks, both Track 2
matrices, the privacy scanner and the superseded-claim auditor.

Figures regenerate from `src/figures/` and are **deterministic**: fixed `svg.hashsalt` and no
embedded date, so a re-render produces byte-identical SVGs. The environment moved from
matplotlib 3.7.2, which has no CPython 3.12 wheel on any platform and so could not be
installed by anyone else, to **matplotlib 3.8.4**; the nine publication figures that
existed at that point were then
re-rendered and compared pixel by pixel against the originals: **0 differing pixels, maximum
channel deviation 0.**

One honest caveat: the privacy scanner reads its list of case-specific forbidden values from a
gitignored file. Elsewhere it still checks structural patterns (coordinates, HGVS, genotypes,
local paths) but not the case values, and it says which of the two it did on every run.

## 10 · AI use disclosure

Required by the submission rules.

| | |
|---|---|
| **Provider** | Anthropic |
| **Interface** | Claude Code |
| **Model** | Claude Opus 5 |
| **Plan / tier** | *To be completed by the maintainer* |
| **Data-handling setting** | *To be completed by the maintainer* |

**What the assistant did:** wrote and refactored the analysis code, figure modules and
notebooks; drafted documentation; performed literature searches; audited the repository for
internal inconsistencies and stale numbers.

**What it did not do:** it did not choose the final therapeutic candidate, and it did not
commit or push to the repository. The project's operating rules define explicit stop
conditions, and the choice of therapeutic candidate is one of them; those decisions are the
maintainer's.

**Patient data and external services.** No patient data was sent to the AI assistant's
provider as part of an analysis request beyond what appears in this repository, and this
repository contains no patient data. One external service did receive patient-derived values:
**AlphaGenome**, which was given a variant shortlist, never the VCF. It runs in an isolated
virtual environment so that no ordinary run of this repository can reach it, its outputs are
cached, and the call is not repeated on a normal build. This is documented in
`docs/03_ALPHAGENOME_ASSESSMENT.md`.

> **Note on the two blank fields.** The plan or tier and the account's data-handling
> configuration are properties of the maintainer's own account. They are deliberately left blank
> rather than guessed: this project's rules forbid writing an unverified fact, and an invented
> compliance statement would be worse than an incomplete one. **They must be filled in before
> submission.**

## 11 · Acknowledgements and data citation

This work was carried out for the Rare Disease, Real Kid: MVA Hackathon 2026, organised by
**Sage Bionetworks**, the **MVA Society**, **Hugging Face**, **BEACON**, **AWS** and
**Anthropic**.

> **Dataset citation: to be completed before submission.** The rules require the hackathon
> dataset to be cited using the reference provided on the hackathon Synapse page. That
> reference was not retrieved in this session and is therefore not transcribed here, per the
> project's rule against writing unverified identifiers.

**Dataset provenance.** The hackathon dataset is distributed through the Synapse project [`syn76251147`](https://www.synapse.org/Synapse:syn76251147/wiki/642892). The **formal citation is not reproduced here**: it is not visible on the public page without an authenticated session, and this project does not write a reference it has not read. It must be copied verbatim from the authorised session before submission.

**Privacy.** This report contains no information that could re-identify the data subject or
their family. No variant coordinate, HGVS string, genotype or sample identifier appears in
this document or anywhere in the repository. No attempt was made to locate the family; the
existence of a public family blog is a re-identification vector, not a source.

## 12 · Licence

Documentation, notebooks and figures: CC BY 4.0. Code: dual-licensed **MIT OR CC BY 4.0**, so
that the whole submission is available under CC BY as the rules require, while code reuse gets
a licence built for software. See `LICENSE` and `LICENSE-DOCS`.
