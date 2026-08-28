# Contributing Research

MOSAIC RESCUE is a scientific hypothesis project, not an idea dump. Contributions should make the final causal chain stronger or reveal why a current hypothesis is wrong.

## Contribution template

### Claim
State the claim in one sentence.

### Why it matters
Explain what decision this would change.

### Evidence
List primary papers, datasets, or functional screens.

### Evidence level
Use L0-L5 from `AGENTS.md`.

### Required patient data
State the exact modality needed: VCF, BAM/CRAM, bulk RNA-seq, scRNA-seq, proteomics, clinical karyotype, etc.

### Alternative explanation
What else could generate the same observation?

### Falsification test
What result would make us reject this claim?

### Independent validation
Which external dataset or perturbation experiment can test it?

### Safety consequence
Could this mechanism increase CIN, abnormal clonal fitness, apoptosis escape, proliferation, or tumor risk?

### Best visualization
What figure would make the phenomenon obvious to a domain scientist?

## Patient data handling

The hackathon dataset is gated and identifiable. It lives in `data/`, which is
git-ignored in full, and it stays on the machine that downloaded it.

Non-negotiable:

- Never commit anything from `data/`. Never copy patient-level values into
  `docs/`, `research/`, `hypotheses/`, or a notebook cell that gets committed.
- Never send a gated file to a third-party service — no LLM API, no web tool,
  no hosted notebook, no pastebin. Agents working streams #2 through #8 are
  researching external literature and public datasets; they do not need the
  patient files and must not be given them.
- Report aggregates, not individuals. "17 de novo variants, 3 in dosage-sensitive
  genes" is publishable here; a genotype at a named position is not.

### Strip notebook outputs before committing

An executed `.ipynb` stores its outputs inside the file. A cell that prints a
variant table leaks that table into git even though the source file is ignored.
Clear outputs before staging:

```bash
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```

To make this automatic for everyone who clones the repo:

```bash
git config filter.strip-nb.clean "jupyter nbconvert --clear-output --to notebook --stdin --stdout" && git config filter.strip-nb.smudge cat && echo "*.ipynb filter=strip-nb" >> .gitattributes
```

If you find patient data already committed, do not just delete it in a new
commit — the blob stays in history. Say so immediately so the history can be
rewritten and the repo treated as exposed.

## Merge standard

A contribution should improve at least one of these:

- causal variant confidence
- mechanism resolution
- patient-as-screen validity
- ghost-karyotype inference
- fitness landscape estimation
- synthetic rescue evidence
- forecast calibration
- rescue replay
- safe rescue corridor
- drug mechanism convergence
- pharmacogenomic or pediatric context
- falsifiability
- experimental design

Novelty alone is insufficient. Evidence alone is insufficient. We want useful convergence.
