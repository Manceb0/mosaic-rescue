# Registro de experimentos

> Una página para ver **dónde está la investigación**. Cada entrada apunta a su origen
> ejecutable. Si un resultado no tiene origen ejecutable, se marca como tal, no se disimula.

## Estado

| ID | Experimento | Estado | Origen ejecutable |
|---|---|---|---|
| **EXP-001** | QC de FASTQ (L001) | **SURVIVES** | `src/qc_fastq_sample.py` → **falta notebook** |
| **EXP-002** | Censo del VCF | **SURVIVES** | `src/vcf_variant_census.py` → **falta notebook** |
| **EXP-003** | Anotación VEP, pasada 1 | **SURVIVES** | `src/run_vep_pass1.sh` |
| **EXP-004** | Escaneo del panel MVA | **SURVIVES** | `src/build_funnel.py` |
| **EXP-005** | Escaneo del panel renal | **SURVIVES** | `src/build_funnel.py` |
| **EXP-006** | **Ranking genome-wide sin panel** | **SURVIVES**, #1 en 14/15, con `A0` corregido a #4 | `notebooks/01_TRACK1_GENOME_WIDE.ipynb` · 6 figuras embebidas |
| **EXP-006b** | **Baseline externo (Exomiser), método independiente, mismo VCF** | **SURVIVES**, `BUB1B` #2 de 398, modelo AR, en las dos corridas | `src/baseline/` → `src/make_fig8.py` |
| **EXP-017** | Auditoría renal / tubulopatía | **NEGATIVE** (barrido codificante) · la pregunta clínica sigue **BLOQUEADA** | `docs/RENAL_RESIDUAL.md` |
| **EXP-018** | Residual · atrofia muscular esquelética | **PARKED**, no anotado y no cuantificado; **no se cierra** | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-019a** | Residual · crecimiento y fallo de medro | **NEGATIVE**, la literatura MVA1 los cubre al 93,5 %; el bajo soporte era hueco de anotación | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-019b** | Residual · parto prematuro | **PARKED**, no anotado y no cuantificado en la serie; el eje perinatal lo hace plausible pero no resuelto | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-019c** | Residual · **nefrocalcinosis** | **UNRESOLVED**, único rasgo sin anotación **y** sin respaldo en la literatura MVA1 | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-007** | Curación ACMG de los alelos | **SURVIVES** | disperso → **falta notebook** |
| **EXP-008** | Alelo regulador oculto | **NEGATIVE** | disperso → **falta notebook** |
| **EXP-009** | Prueba con AlphaGenome | **NEGATIVE** | `src/alphagenome_*.py` |
| **EXP-010** | Estructura de BUBR1 | **UNRESOLVED** | disperso → **falta notebook** |
| **EXP-011** | Conservación ortóloga | **SURVIVES**, con robustez filogenética | `src/structure/ortholog_conservation.py` + `clades.py` → `src/make_fig7.py` |
| **EXP-021** | **Tres deleciones homocigotas que superan a `BUB1B` en `A0`** | **NEGATIVE**, polimorfismos comunes con rsID (hasta 313 150 homocigotos en gnomAD); resuelto **localmente** | `src/prioritization/audit_a0_competitors.py` |
| **EXP-021b** | `A0-FREQFIX` · sensibilidad del defecto de anotación | **SURVIVES**, reparando los 33 alelos, `BUB1B` vuelve al puesto 1. Los dos números se reportan | `src/prioritization/freqfix_sensitivity.py` |
| **EXP-020** | **`FANCD2` como hipótesis competidora** | **NEGATIVE**, los tres alelos al ~47 % de frecuencia, todos heterocigotos | `docs/FANCD2_AUDIT.md` |
| **EXP-011b** | *Siguiente de esa rama:* abundancia y recambio de BUBR1 específico de variante | **PARKED**, no lo ejecuta este proyecto | — |
| **EXP-012** | SV / CNV en `BUB1B` | **BLOCKED** (BAM/CRAM de profundidad completa |) |
| **EXP-013** | Fase parental | **BLOCKED**, muestras de los padres | — |
| **EXP-014a** | MitoRead · prototipo sobre L001 | **UNRESOLVED**, *naive mtDNA-equivalent estimate* ≈259 bajo los supuestos del piloto. **No calibrado, no interpretable** | `src/mito/pilot_l001.py` |
| **EXP-014a-v2** | MitoRead · piloto **con alineamiento** para excluir NUMT | **PARKED**, sin alineador instalable (`mappy` no compila sin toolchain de C) y descargar binarios ejecutables está prohibido por política. El prototipo ya demostró factibilidad | — |
| **EXP-014b** | MitoRead · **interpretación biológica** | **BLOCKED**, exige profundidad completa comparable, controles con pipeline idéntico, y hemograma (plaquetas + fórmula) | — |
| **EXP-015a** | **Mecanismo de cancelación de BAF** | **SURVIVES**, modo de fallo reproducido y cuantificado | `src/mosaic/simulate_dispersion.py` |
| **EXP-015b** | **Índice de dispersión como detector** | **UNVALIDATED · PARKED**, el comparador usado no es MoChA y no reproduce su ventaja de BAF faseado de largo alcance | — |
| **EXP-015** | Huella de mosaicismo aplicada | **BLOCKED**, faltan controles con pipeline idéntico | — |
| **EXP-016** | **Track 2 · dos rutas, ocho puentes** | **UNRESOLVED**, con T2-A y T2-B separadas. Puentes 1 y 3 huecos; **puente 7 `UNRESOLVED` con contraevidencia verificada (E18, E19)**; puente 8 **vacío**. Sin nominación | `docs/TRACK2_MECHANISM_MAP.md` → `src/make_fig10.py` |
| **EXP-016b** | **Puente 7 · búsqueda acotada de literatura** | **UNRESOLVED**, cero evidencia DIRECT; dos fuentes CONTRADICTORY verificadas | `docs/EVIDENCE.md` E18/E19 |

---

## Deuda reconocida

**Todos los experimentos completados tienen ya notebook de investigación.** El *Notebook Recovery Sprint* cerró la deuda y la *pasada visual-cientifica* la refinó: ocho notebooks ejecutados con 26 figuras embebidas, 21 de ellas científicas (`DATA` / `MODEL_OUTPUT` / `SIMULATION`). Ver `notebooks/VISUAL_SCIENCE_PASS.md`. Antes decía «ocho de doce sin notebook». Existen
como scripts sueltos en `src/` y como conclusiones en `docs/`, pero no como el recorrido
*pregunta, preregistro, método, ejecución, falsación y decisión* que permite
seguirlos, cuestionarlos y repetirlos.

**EXP-011 es la excepción y marca el listón:** su figura nace de un pipeline que reproduce
desde cero (descarga externa incluida) y se verificó que la descarga repetida es idéntica
byte a byte. No es un notebook, pero cumple la regla: origen ejecutable comprobado.

Eso se arregla convirtiéndolos, no rehaciéndolos: los análisis son correctos, lo que falta
es la columna vertebral que los enlaza.

**Nueva regla, en `CLAUDE.md`:**

> **Ninguna figura final sin un notebook o pipeline reproducible que haya generado el
> resultado.**

Todas tienen ya origen ejecutable. La **pasada visual-científica** además retiró de los
notebooks las que quedaron redundantes: siguen generándose y siguen en `figures/`, pero ya no
son el vehículo principal del argumento. El detalle y el motivo de cada retirada están en
`notebooks/VISUAL_SCIENCE_PASS.md`.

| Figura | Origen ejecutable | Sitio en los notebooks |
|---|---|---|
| Fig 2 · Variant landscape | `src/make_fig2b.py` | **retirada**, el navegador de `02` enseña los mismos 1 497 registros de ClinVar con el transcrito y los dominios encima |
| Fig 3 · PVS1 y geometría de fase | `src/make_fig3.py` | vigente en `02_BUB1B_ALLELE_CURATION` |
| Fig 4 · Interrogatorio estructural | `src/make_fig4.py` | **retirada**, `03` calcula en vivo vecinos, puentes de H y pLDDT desde el PDB |
| Fig 5 · AlphaGenome REF/ALT/Δ | `src/make_fig5.py` | **retirada**, `04` dibuja las nueve pistas congeladas sobre un eje genómico compartido |
| Fig 6 · Funnel | `notebooks/01_TRACK1_GENOME_WIDE.ipynb` | vigente, INLINE |
| Fig 7 · Conservación ortóloga | `src/structure/` → `src/make_fig7.py`, reproducible desde la descarga | vigente en `03`, junto al logo de secuencia |
| Fig 8 · Baseline externo | `src/baseline/` → `src/make_fig8.py` | vigente en `01` |
| Fig 9 · Simulación de mosaicismo | `src/mosaic/simulate_dispersion.py` → `src/make_fig9.py` | **retirada**, el panel D de `06` es la misma curva y además trae las distribuciones |
| Fig 10 · Ocho puentes y corredor | `src/make_fig10.py` | vigente en `07` como `SYNTHESIS`, junto a la matriz de evidencia |

**Objetos científicos nuevos de la pasada visual**, todos con origen propio:

| Objeto | Módulo |
|---|---|
| Modelo de transcrito y dominios de BUB1B | `src/structure/transcript_model.py` (Ensembl REST, cacheado) |
| Geometría del bolsillo: vecinos, puentes de H, pLDDT | `src/structure/pocket_geometry.py` |
| Matriz de evidencia de Track 2 | `research/track2_evidence.tsv`, 80 celdas versionadas, cada una con fuente |
| Distribuciones de BAF por sitio | `src/mosaic/simulate_dispersion.py::site_bafs()` |
| Contact sheet de las ocho figuras principales | `src/nb/contact_sheet.py` |

---

## EXP-006: el experimento que faltaba

**Pregunta:** *¿Qué gen o genes explican mejor el caso cuando se deja competir a todo el
genoma?*

**Por qué importa.** Hasta ahora `BUB1B` apareció fuerte **dentro de un panel que nosotros
elegimos**. Eso no es lo mismo que sobrevivir a una búsqueda sin panel. Saltar de aquí a
mecanismo sería exactamente el sesgo de confirmación que el proyecto dice evitar.

**Garantía de diseño:** `src/prioritization/extract_genomewide.py` **no menciona ningún gen**.
El filtro es únicamente consecuencia funcional.

| | |
|---|---|
| Entrada | 4 943 948 variantes anotadas |
| Filtro | `IMPACT` HIGH o MODERATE, sin panel |
| Extraídas | **13 109 variantes en 6 322 genes** |
| Siguiente | frecuencia poblacional, modelos de herencia, agregación por gen |

**Preregistro.** Ver `docs/DECISIONS.md`.

**Los dos desenlaces son buenos:**

- Si `BUB1B` queda arriba compitiendo contra 6 322 genes, entonces *no lo encontramos porque lo
  buscábamos; sobrevivió a una búsqueda sin panel*.
- Si gana otro gen, **acabamos de evitar un error**, que vale más.

---

## Datos disponibles y bloqueos

| Recurso | Estado |
|---|---|
| VCF completo (4 carriles) | **Disponible** |
| FASTQ | **Solo L001** (~13×) de los cuatro esperados |
| BAM / CRAM de profundidad completa | **No disponible, bloquea EXP-012** |
| Genotipos parentales | **No disponibles, bloquean EXP-013** |
| Respuestas clínicas (líquido amniótico, kit de librería, hemograma) | **Pendientes** |

> **Prohibido afirmar un negativo de variante estructural con L001.** Un carril a ~13× sirve
> como piloto, no para cerrar una ausencia.
