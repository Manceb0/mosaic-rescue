# Open Questions

These are questions that must be resolved before we lock the final architecture.

## Data availability

1. What are the exact 11 gated files?
2. Do we have only VCF, or also BAM/CRAM?
3. Is there bulk RNA-seq?
4. Is there scRNA-seq or another cell-resolved modality?
5. Is there longitudinal sampling?
6. Is there clinical karyotype information that can serve as ground truth?
7. Are there fibroblasts, iPSC, organoid, proteomic, or imaging-derived data?

## Track 1

8. What is the top causal-variant hypothesis after full-genome prioritization?
9. Does the mechanism fit classic MVA genes or a broader MVA-like pathway?
10. Is phasing/inheritance informative?
11. Does the candidate implicate dosage, stability, interface loss, catalysis, splicing, or regulation?

## Patient-as-Screen

12. Can we estimate cell-level or sample-level chromosomal states with enough confidence?
13. Can we separate state-generation probability from selection/persistence?
14. Which tissues are represented, and how tissue-specific might the observed mosaicism be?
15. Are “ghost” states robust to sampling depth and technical bias?

## Rescue

16. Which external functional datasets best match the patient’s mechanism?
17. Can we find suppressors with orthogonal support in CRISPR/Perturb-seq/model organisms?
18. Do candidate rescue mechanisms increase aneuploid-cell survival in a potentially dangerous way?
19. Is there evidence for protein-dose, mPOS/proteostasis, mitochondrial stress, senescence, IFN, or cell competition in this specific case?

## Forecasting

20. Is the available data sufficient for patient-specific forecasting, or only for simulation under external priors?
21. How will forecasts be calibrated and uncertainty shown?
22. What result would demonstrate that the forecast is not better than a simple baseline?

## Intervention

23. Can any approved drug or tractable intervention reproduce the candidate rescue mechanism at plausible exposure?
24. Is there pediatric precedent?
25. Is pharmacogenomics relevant to the shortlisted intervention?
26. Does the intervention move the state toward a safe rescue corridor rather than simply increasing survival?

## Final scientific test

27. What single finding would make this project truly novel?
28. What is the strongest experiment that could prove our final hypothesis wrong?
