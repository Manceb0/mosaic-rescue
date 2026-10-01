# Tabla de evidencia

Se actualiza **al leer cada paper**, no al final. Una referencia sin PMID/DOI verificado
en la sesión se marca `no verificado`; no se inventa (`CONTRIBUTING_RESEARCH.md`, Regla Dura 5).

No citar un paper porque su título parezca relevante. Leer métodos y resultados
suficientes para saber qué se demostró realmente.

Niveles: `L0` especulación · `L1` asociación · `L2` apoyo ortogonal · `L3` evidencia
funcional · `L4` funcional replicada · `L5` humana/clínica establecida.

| ID | Afirmación exacta | PMID | DOI | Año | Sistema | Tipo | Apoya/Contradice | Directa o inferida | Nivel | Limitación principal | Qué la falsaría |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |

## Referencias ya verificadas en sesión

Verificadas contra PubMed el 2026-08-28. Ver `research/agent_findings/` para el contexto
en que se usaron.

| PMID | Referencia | Año |
|---|---|---|
| 40065168 | Selection for somatic escape variants in SERPINA1 in the liver of patients with alpha-1 antitrypsin deficiency. *Nat Genet* | 2025 |
| 34283872 | Trisomy 21-associated increases in chromosomal instability... mosaic Down. *PLoS One* | 2021 |
| 36322655 | Biallelic germline mutations in MAD1L1 induce a syndrome of aneuploidy with high tumor susceptibility. *Sci Adv* | 2022 |
| 35831506 | Nuclear chromosome locations dictate segregation error frequencies. *Nature* | 2022 |
| 40409259 | Cell competition eliminates aneuploid human pluripotent stem cells. *Stem Cell Reports* | 2025 |
| 22802626 | Transcriptional consequences of aneuploidy. *PNAS* | 2012 |
| 29470523 | A "late-but-fitter revertant cell" explains the high frequency of revertant mosaicism in epidermolysis bullosa. *PLoS One* | 2018 |
| 39085295 | Inference of chromosome selection parameters and missegregation rate in cancer from DNA-sequencing data. *Sci Rep* | 2024 |
| 26491874 | Evidence of Selection against Complex Mitotic-Origin Aneuploidy during Preimplantation Development. *PLoS Genet* | 2015 |
| 29898405 | Non-random Mis-segregation of Human Chromosomes. *Cell Rep* | 2018 |
| 37821946 | Global analysis of suppressor mutations that rescue human genetic defects. *Genome Med* | 2023 |
| 29083409 | Computational correction of copy number effect improves specificity of CRISPR-Cas9 essentiality screens. *Nat Genet* | 2017 |
| 29892062 | p53 inhibits CRISPR-Cas9 engineering in human pluripotent stem cells. *Nat Med* | 2018 |
| 29576454 | Profound Tissue Specificity in Proliferation Control Underlies Cancer Drivers and Aneuploidy Patterns. *Cell* | 2018 |
| 26192197 | A cytosolic network suppressing mitochondria-mediated proteostatic stress and cell death. *Nature* | 2015 |
| 40527892 | Aneuploidy-induced proteostasis disruption impairs mitochondrial functions and mediates aggregation of mitochondrial precursor proteins. *Nat Commun* | 2025 |
| 27120771 | Polyhydramnios, Transient Antenatal Bartter's Syndrome, and MAGED2 Mutations. *N Engl J Med* 374(19):1853-63 | 2016 |

## Pendiente de verificar antes de uso público

Marcadas por la auditoría de Synthetic Rescue como necesitadas de re-verificación primaria:

- Solapamiento de letalidad sintética entre líneas celulares en Horlbeck et al.
- Fracción de screens de selección positiva en BioGRID ORCS
- Conteos de van Leeuwen et al. 2016 — texto completo en *Science* tras muro de pago

Además, el brief §11 marca con ⚠ las referencias cuyo identificador no está confirmado.

## Track 2 · puente 7 — evidencia añadida 2026-08-31

| # | Referencia | Sistema | Hallazgo usado | Apoya/Contradice | Nivel | Qué lo falsaría |
|---|---|---|---|---|---|---|
| **E18 ✔** | Pipalia NH, Saad SZ, Subramanian K, et al. *J Lipid Res* 2021;62:100114. **PMID 34481829** · DOI 10.1016/j.jlr.2021.100114 | Fibroblastos humanos NPC1 I1061T | La **sobreexpresión de HSP70** redujo el almacenamiento de colesterol; **arimoclomol NO lo reprodujo** hasta 500 µM / 72–120 h, y **no aumentó HSP70** en esos fibroblastos | **CONTRADICE** el puente 7 | `L4` | Que un coinductor sí indujera HSP y sí rescatara en un sistema comparable |
| **E19 ✔** | Donnelly N, Passerini V, Dürrbaum M, Stingele S, Storchová Z. *EMBO J* 2014;33(20):2374–2387. **PMID 25205676** · DOI 10.15252/embj.201488648 | Aneuploides humanos derivados de HCT116 y RPE-1 | La **inducción de la respuesta de choque térmico está deteriorada**: HSP70 inducible al **50–60 %** del control. **HSF1 constitutivamente activo** sí contrarresta la función deficiente de HSP90 | **CONTRADICE** la elección de un coinductor **dependiente de estrés** como clase farmacológica para células aneuploides | `L4` | Que un coinductor lograra inducción normal de HSP en células aneuploides |
| **E20 ✔** | Fernández Comaduran M, Minotti S, Jacob-Tomas S, et al. *Cell Stress Chaperones* 2024;29(3):359–380. **PMID 38570009** · DOI 10.1016/j.cstres.2024.03.010 | Cultivos primarios de neuronas, modelos de ELA familiar (TDP-43, FUS, SOD1) | Arimoclomol **no fue efectivo** en neuronas TDP-43<sup>G348C</sup>; los efectos sobre `Hspa8` fueron **dependientes de la variante**: se mantuvieron en SOD1, no en FUS | **Clase `NEAR`** — contexto proteotóxico distinto. **NO sustituye a evidencia DIRECT** | `L4` | Que la inducción resultara consistente entre modelos |

**Cómo se usan, y cómo NO.**

- `E18` **no** dice que arimoclomol no sirva para nada: dice que **en ese sistema** no reprodujo
  el rescate genético y no indujo HSP70. Es el control negativo que separa el puente 6 del 7.
- `E19` **no** dice que subir HSP no ayude a células aneuploides: dice que **la vía de
  inducción está averiada**, así que la clase farmacológica que la amplifica trabaja a través
  del nodo deficiente. Lo que rescató fue **puentear** el nodo, no amplificarlo.
- `E20` es **clase `NEAR`**: neuronas, no células aneuploides. Por la regla del puente 7 **no
  puede sustituir a evidencia DIRECT**. Lo que aporta es que la inducción de HSP por este
  coinductor **no es fiable entre modelos** — falló en TDP-43 y varió con la variante de ELA.
  Sumado a `E18`, el patrón es que **la inducción farmacológica de HSP no se puede dar por
  supuesta en un sistema nuevo**.

- Ninguna de las tres permite afirmar que T2-B esté muerta. Permiten afirmar que **la
  traslación farmacológica no puede darse por supuesta**, que es distinto y más útil.
