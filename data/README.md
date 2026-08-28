# data/ — gated hackathon dataset

This directory is git-ignored in full. Nothing placed here is ever committed.

Put the downloaded hackathon files here and run `notebooks/00_data_inventory.ipynb`
against them. The inventory reads file headers and shapes only; it is designed to
emit the Branch Activation Matrix without printing patient-level variants.

Rules:
- Do not copy anything out of this directory into docs/, research/, or notebook outputs.
- Do not send any file here to a third-party API (no LLM, no web tool, no cloud notebook).
- Aggregate counts and summary statistics may be reported; per-individual genotypes may not.

If a file must be referenced in writing, refer to it by filename and shape
(e.g. "proband WGS CRAM, 38x mean coverage"), never by content.
