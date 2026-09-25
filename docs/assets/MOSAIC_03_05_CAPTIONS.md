# Figures 03–05 — captions, sources and review

Generated using built-in imagegen, with approved `mosaic-01-causal-workflow.png` as style reference. These are editorial scientific schematics, not replacements for quantitative figures. Source claims were checked against the existing Track 1 and Track 2 reports; no new biological findings or drug nominations were made.

## Figure 03 — ranking audit

Asset: `mosaic-03-ranking-audit.png`. Placement: README chapter 2, research-story candidate section immediately before the actual genome-wide plot.

**Paper caption:** The original frozen A0 analysis places BUB1B fourth. An audit found missing frequency annotations for common alleles in the three higher-ranked genes. Repair of 33 allele annotations yields BUB1B rank one in the later A0-FREQFIX sensitivity analysis; the original analysis is retained. Exomiser ranks BUB1B second among 398 distinct genes using the same VCF. Agreement is methodological, not independent biological replication. Ranks are actual reported analysis outputs; read glyphs, table cells and rank bars are schematic and encode no quantitative scores. “Aligned reads (subset)” is an illustrative glyph, not a patient alignment screenshot. Phase and missense function remain unresolved.

Sources: [Track 1 report, sections 1–3](../../reports/TRACK1_REPORT.md), [quantitative genome-wide plot](../../figures/pub/fig01_prioritization_genomewide.svg), [notebook 01](../../notebooks/01_TRACK1_GENOME_WIDE.ipynb).
Review: #4/#1/#2 of 398 and 33 annotations match report; Exomiser has independent method branch from same source; original A0 not overwritten.

## Figure 04 — bounded hidden-allele search

Asset: `mosaic-04-hidden-allele.png`. Placement: README chapter 3, research-story section between predictions and mosaicism methods.

**Paper caption:** Parallel computational investigations constrain a hidden-allele hypothesis without establishing its absence. AlphaGenome outputs lack convincing support for the assessed regulatory candidate; this is not a global exclusion of splicing defects. Within the scoped BUB1B gene-body search, CNVpytor RD+BAF emitted no overlapping CNV and xTea/SCRAMble emitted no overlapping MEI call. The read-level assay compares the body with matched flanks and remains descriptive, without an inferential excess/no-excess threshold. Complex insertion remains unresolved. RNA and targeted long-read investigations are proposed. GO 2B is closed within its frozen scope; AE2 population lookup was not executed because of data policy. Miniature tracks, read alignments and RNA/long-read glyphs are schematic, not measured plots or evidence of an insertion.

Sources: [Track 1 report, sections 7 and 7b](../../reports/TRACK1_REPORT.md), [read-level metrics](../../figures/pub/fig10_bub1b_readlevel_assay.svg), [frozen artifact manifest](../go2b_final_artifacts.sha256.json).
Review: corrected unsupported tumor/normal wording to one blood sample; removed sequence-to-CNV branch; corrected read-level scope to body plus matched flanks. This overview does not enumerate every structural caller or raw genome-wide record.

## Figure 05 — proposed rescue experiment

Asset: `mosaic-05-rescue-test.png`. Placement: README chapter 5 and research-story rescue section beside evidence/portfolio material.

**Paper caption:** Proposed preclinical discrimination of three experimental roles: azithromycin as an allele-directed hypothesis, arimoclomol as a falsification sentinel and sirolimus as an adversarial safety comparator. Vehicle is the negative control; constitutively active HSF1 is a contextual genetic positive control and HSP70 overexpression is a mechanistic comparator. Control suitability must be established in the experimental system. Molecular engagement, chromosome segregation, clonogenic survival and viability are read jointly. Unsupported mechanism rejects the proposed route; increased survival of unstable cells triggers a safety veto. Improved function and reduced instability without increased unstable-cell survival support further preclinical testing, not clinical use. Symbols depict proposed readouts, not molecular structures, colony counts or observed treatment effects. No thresholds, exposures or efficacy results are encoded. Other inconclusive outcomes are possible; this is a decision schematic, not an exhaustive executable assay protocol.

Sources: [Track 2 report](../../reports/TRACK2_REPORT.md), [portfolio and controls](../../figures/pub/fig08_track2_portfolio.svg), [evidence matrix](../../figures/pub/fig07_track2_evidence_matrix.svg).
Review: three roles, three controls and four readouts present; contextual-control qualification retained; rejection and veto terminate separately from conditional advancement.

## Exact generation prompts

### Figure 03

Create figure 03 in the MOSAIC RESCUE scientific illustration series. Attached image is STYLE MASTER only: match continuous black fine grid, understated frosted translucent charcoal glass, fine white rims, compact white sans serif, restrained blue and amber diffuse interior reflections, slim constant-width connectors with clean arrowheads. English. 16:9 high resolution. No bright node balls. One original elegant composition for a paper/README.

Title "MOSAIC RESCUE"
Subtitle "Why BUB1B rose to the top"
Actual verified ranking audit, not invented data:
Left source "One WGS / same VCF", small aligned-read glyph; blue line forks into two INDEPENDENT methods.
Upper large path: three distinct stages with meaningful technical details:
"Frozen A0" with a restrained ordered ranking glyph (four evenly spaced rows, top three muted unnamed marks, fourth amber mark labeled BUB1B). Exact prominent text "BUB1B #4". Small "Original result retained".
Then a shallow glass magnifying lens over a tiny annotation table (no invented scores or gene identities) label "Frequency audit"; small exact lines "3 higher-ranked genes: common alleles" and "33 allele annotations repaired". Connect audit forward, not back to overwrite frozen result.
Then "A0-FREQFIX" with restrained rank glyph BUB1B at top, exact "BUB1B #1"; small "Later sensitivity analysis".
Use blue connection between frozen result and audit and audit and corrected sensitivity. Both original #4 and later #1 must remain equally legible, no crossed-out original.
Lower independent path from SAME left source: "Exomiser" module, exact large "BUB1B #2 / 398 genes"; small "Same VCF · different method". No arrow implying Exomiser receives the corrected ranking. Merge only at right into interpretation.
Right final glass lens "Leading causal hypothesis". Beneath amber small "Phase unresolved · missense VUS". A subtle amber short stopping line before a modest label "Not a confirmed diagnosis".
Near lower center an unboxed neutral annotation "Method agreement is not biological replication".
Small bottom footer "Source: Track 1 report · ranks are analysis results, not leaderboard scores".
All exact numbers visible and correct. Schematic ranking glyphs show order only, never numerical scores, p-values or invented effect sizes. No unrelated variants, no patient coordinates, no drug imagery. Moderate negative space; coherent continuous flow, not giant bulky UI cards. Match reference glass material and uniform quiet light, no uneven glow, no decorative corner slogans.

### Figure 04

Create figure 04 in MOSAIC RESCUE paper schematic series. Match attached style master: continuous fine black grid, quiet translucent smoked-glass surfaces, white hairline edges, compact white sans-serif, subtle blue/green/amber interior glow, clean thin arrows without endpoint balls. English, wide 16:9, original composition, legible short text, refined technical details.

Title "MOSAIC RESCUE"
Subtitle "A bounded search. An unresolved hidden allele."
Explain the actual scope of completed analyses without implying hidden allele was found or absent globally.

Left two DISTINCT sources vertically:
"Candidate sequence" with paired REF / ALT conceptual strips, feeds ONLY the prediction branch.
"Full-depth BAM" with schematic short-read alignments, feeds ONLY the structural and read-level branches.
Center has four horizontal evidence lanes, separated by subtle whitespace/rules rather than big dashboard cards:
1 "AlphaGenome" (green tint) -> "Assessed regulatory candidate" -> small restrained endpoint text "No convincing model support". Tiny "Predicted · not patient RNA". Use two nearly overlapping schematic wave glyphs, no numbers or actual signal claims.
2 "CNVpytor RD + BAF" (blue tint) -> short schematic depth track -> endpoint "No CNV call overlapping BUB1B".
3 "xTea + SCRAMble" (blue tint) -> short read stack glyph, no insertion detected icon or universal red X -> endpoint "No MEI call overlapping BUB1B".
4 "Read-level assay" (blue tint) -> sparse equal-length short read glyphs -> endpoint "Descriptive only"; below small "No inferential excess threshold".
Full-depth BAM splits independently into lanes2,3,4, never from predictions. Exact scope of lanes2,3 is gene-body overlap, not the whole genome; add short bracket label beneath them "BUB1B gene-body scope".
All lanes lead via restrained neutral lines to a single right-center amber glass lens, exact text "Complex insertion not excluded".
From lens one dashed amber arrow into small lower-right clear glass proposed-next-measurement module:
"RNA + targeted long reads"
small "Proposed"
minimal RNA splice glyph and long continuous read glyph, NOT results or actual intronic architecture.

Bottom left two compact status labels, outside the completed-evidence lanes:
"GO 2B: closed scope"
"AE2 population lookup: not executed"
Do NOT connect AE2 as a negative finding.
Bottom right concise "Negative within scope is not universal exclusion".
Footer "Conceptual evidence map · no hidden allele demonstrated · graphics schematic".

Science constraints: no patient coordinates, genotypes, fictional exon diagrams, percentages, statistically significant no-excess conclusion, fake Sanger traces, parent data or false expression assays. The assessed regulatory candidate lacks convincing model support; that never globally excludes splicing effects. The mobile-element/no-CNV claims refer only to specified callers and overlapping BUB1B body. Complex insertion remains unresolved. Make uncertainty salient but not overpowering. Soft consistent frosted light matching reference. Keep all text crisp and unobstructed.

Targeted correction: replace tumor/normal with one blood sample; remove green input to CNVpytor; change read-level scope to body plus matched flanks. Only the corrected output was integrated.

### Figure 05

Create figure 05 in MOSAIC RESCUE scientific paper illustration series. Use attached style master: near-black continuous fine grid, quietly frosted translucent charcoal shapes with uniform soft interior light, fine white outlines, restrained blue/green/amber, compact clean English sans serif, coherent technical motion-design aesthetic. Wide 16:9, readable. No endpoint balls or gratuitous neon. No empirical graphs: all assays are PROPOSED.

Title "MOSAIC RESCUE"
Subtitle "What would count as rescue — and what would reject it?"
Small visible status "Proposed preclinical design · no efficacy demonstrated".

LEFT third: three equal treatment-arm modules vertically arranged, unranked, each has same single empty assay-well glyph:
"Azithromycin" / "Allele-directed hypothesis"
"Arimoclomol" / "Falsification sentinel"
"Sirolimus" / "Adversarial safety comparator"
Do not show drug structures, dose, rankings or success colors. These are proposed research roles, not treatments for a child.
Below left a compact independent frosted controls strip heading "Controls" with exact three lines:
"Vehicle · negative"
"ca-HSF1 · contextual genetic positive"
"HSP70 overexpression · mechanistic comparator"
Small "Control suitability must be checked".
Controls and all arms converge via thin neutral lines into an assay design junction without a circular node.

CENTER: one broad translucent evaluation layer heading "Measure together". Four concise scientifically meaningful readout vignettes arranged as a disciplined 2 by2:
"Molecular engagement" (generic neutral protein/readout outline, not actual structure or fake blot)
"Chromosome segregation" (schematic mitotic spindle outline, no specific measured abnormality)
"Clonogenic survival" (neutral empty dish with faint template positions, no colony outcomes)
"Viability" (neutral empty well).
Each glyph explicitly conceptual by overall footer. All tests proposed, no actual measured results, no arbitrary thresholds, no numeric axes.
One dashed amber arrow from all readouts together to right-hand decision lens heading "Joint decision". Do not branch from viability alone.

RIGHT: exactly THREE distinct terminal branches from Joint decision, visibly independent, not a chain:
Top: "Mechanism unsupported" then smaller "Reject the proposed route".
Middle: "Unstable-cell survival increases" then smaller amber "Safety veto". This is a DEAD END. Use small amber stop-bar, not bright red alarm.
Bottom: "Function improves; instability falls" then smaller "No increase in unstable-cell survival"; endpoint "Further preclinical testing". This is CONDITIONAL future advancement, not demonstrated success. Use neutral white/amber, no green checkmark. Dashed amber lines to all endpoints. NO arrows from reject or veto to advancement.

Bottom central concise principle "Survival alone is insufficient".
Bottom footer "Conceptual assay design · control effects are context-dependent · no clinical recommendation".
Keep design refined with ample space for exact words and consistently aligned labels. All compound spelling exact. ca-HSF1 is contextual, never universal guaranteed positive. These criteria are proposed discriminating outcomes, not observed drug results. Show all four readouts plus three controls, no patient dosing, no invented success rates. Use same glass lighting as prior approved series.
