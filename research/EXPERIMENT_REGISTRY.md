# Registro de experimentos

> Una página para ver **dónde está la investigación**. Cada entrada apunta a su origen
> ejecutable. Si un resultado no tiene origen ejecutable, se marca como tal — no se disimula.

## Estado

| ID | Experimento | Estado | Origen ejecutable |
|---|---|---|---|
| **EXP-001** | QC de FASTQ (L001) | **SURVIVES** | `src/qc_fastq_sample.py` → **falta notebook** |
| **EXP-002** | Censo del VCF | **SURVIVES** | `src/vcf_variant_census.py` → **falta notebook** |
| **EXP-003** | Anotación VEP, pasada 1 | **SURVIVES** | `src/run_vep_pass1.sh` |
| **EXP-004** | Escaneo del panel MVA | **SURVIVES** | `src/build_funnel.py` |
| **EXP-005** | Escaneo del panel renal | **SURVIVES** | `src/build_funnel.py` |
| **EXP-006** | **Ranking genome-wide sin panel** | **SURVIVES** — #1 en 14/15; `A0` corregido a #4 | `notebooks/03_TRACK1_GENOME_WIDE.ipynb` (reproduce desde las entradas) |
| **EXP-006b** | **Baseline externo independiente (Exomiser)** | **SURVIVES** — `BUB1B` #2 de 398, modelo AR, en las dos corridas | `src/baseline/` → `src/make_fig8.py` |
| **EXP-017** | Auditoría renal / tubulopatía | **NEGATIVE** (barrido codificante) · la pregunta clínica sigue **BLOQUEADA** | `docs/RENAL_RESIDUAL.md` |
| **EXP-018** | Residual · atrofia muscular esquelética | **PARKED** — no anotado y no cuantificado; **no se cierra** | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-019a** | Residual · crecimiento y fallo de medro | **NEGATIVE** — la literatura MVA1 los cubre al 93,5 %; el bajo soporte era hueco de anotación | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-019b** | Residual · parto prematuro | **PARKED** — no anotado y no cuantificado en la serie; el eje perinatal lo hace plausible pero no resuelto | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-019c** | Residual · **nefrocalcinosis** | **UNRESOLVED** — único rasgo sin anotación **y** sin respaldo en la literatura MVA1 | `docs/PHENOTYPE_RESIDUAL_AUDIT.md` |
| **EXP-007** | Curación ACMG de los alelos | **SURVIVES** | disperso → **falta notebook** |
| **EXP-008** | Alelo regulador oculto | **NEGATIVE** | disperso → **falta notebook** |
| **EXP-009** | Prueba con AlphaGenome | **NEGATIVE** | `src/alphagenome_*.py` |
| **EXP-010** | Estructura de BUBR1 | **UNRESOLVED** | disperso → **falta notebook** |
| **EXP-011** | Conservación ortóloga | **SURVIVES** — con robustez filogenética | `src/structure/ortholog_conservation.py` + `clades.py` → `src/make_fig7.py` |
| **EXP-021** | **Tres deleciones homocigotas que superan a `BUB1B` en `A0`** | **NEGATIVE** — polimorfismos comunes con rsID (hasta 313 150 homocigotos en gnomAD); resuelto **localmente** | `src/prioritization/audit_a0_competitors.py` |
| **EXP-021b** | `A0-FREQFIX` · sensibilidad del defecto de anotación | **SURVIVES** — reparando los 33 alelos, `BUB1B` vuelve al puesto 1. Los dos números se reportan | `src/prioritization/freqfix_sensitivity.py` |
| **EXP-020** | **`FANCD2` como hipótesis competidora** | **NEGATIVE** — los tres alelos al ~47 % de frecuencia, todos heterocigotos | `docs/FANCD2_AUDIT.md` |
| **EXP-011b** | *Siguiente de esa rama:* abundancia y recambio de BUBR1 específico de variante | **PARKED** — no lo ejecuta este proyecto | — |
| **EXP-012** | SV / CNV en `BUB1B` | **BLOCKED** — BAM/CRAM de profundidad completa | — |
| **EXP-013** | Fase parental | **BLOCKED** — muestras de los padres | — |
| **EXP-014a** | MitoRead · prototipo sobre L001 | **UNRESOLVED** — *naive mtDNA-equivalent estimate* ≈259 bajo los supuestos del piloto. **No calibrado, no interpretable** | `src/mito/pilot_l001.py` |
| **EXP-014a-v2** | MitoRead · piloto **con alineamiento** para excluir NUMT | **PARKED** — sin alineador instalable (`mappy` no compila sin toolchain de C) y descargar binarios ejecutables está prohibido por política. El prototipo ya demostró factibilidad | — |
| **EXP-014b** | MitoRead · **interpretación biológica** | **BLOCKED** — exige profundidad completa comparable, controles con pipeline idéntico, y hemograma (plaquetas + fórmula) | — |
| **EXP-015a** | **Mecanismo de cancelación de BAF** | **SURVIVES** — modo de fallo reproducido y cuantificado | `src/mosaic/simulate_dispersion.py` |
| **EXP-015b** | **Índice de dispersión como detector** | **UNVALIDATED · PARKED** — el comparador usado no es MoChA y no reproduce su ventaja de BAF faseado de largo alcance | — |
| **EXP-015** | Huella de mosaicismo aplicada | **BLOCKED** — faltan controles con pipeline idéntico | — |
| **EXP-016** | **Track 2 · dos rutas, ocho puentes** | **UNRESOLVED** — T2-A y T2-B separadas. Puentes 1 y 3 huecos; **puente 7 `UNRESOLVED` con contraevidencia verificada (E18, E19)**; puente 8 **vacío**. Sin nominación | `docs/TRACK2_MECHANISM_MAP.md` → `src/make_fig10.py` |
| **EXP-016b** | **Puente 7 · búsqueda acotada de literatura** | **UNRESOLVED** — cero evidencia DIRECT; dos fuentes CONTRADICTORY verificadas | `docs/EVIDENCE.md` E18/E19 |

---

## Deuda reconocida

**Ocho de los doce experimentos completados no tienen notebook de investigación.** Existen
como scripts sueltos en `src/` y como conclusiones en `docs/`, pero no como el recorrido
*pregunta → preregistro → método → ejecución → falsación → decisión* que permite
seguirlos, cuestionarlos y repetirlos.

**EXP-011 es la excepción y marca el listón:** su figura nace de un pipeline que reproduce
desde cero —descarga externa incluida— y se verificó que la descarga repetida es idéntica
byte a byte. No es un notebook, pero cumple la regla: origen ejecutable comprobado.

Eso se arregla convirtiéndolos, no rehaciéndolos: los análisis son correctos, lo que falta
es la columna vertebral que los enlaza.

**Nueva regla, en `CLAUDE.md`:**

> **Ninguna figura final sin un notebook o pipeline reproducible que haya generado el
> resultado.**

Las seis figuras existentes **no se retiran**, pero cambian de estatus hasta tener origen:

| Figura | Notebook que debe generarla |
|---|---|
| Fig 2 · Variant landscape | `04_BUB1B_ALLELE_CURATION` |
| Fig 3 · PVS1 y geometría de fase | `04_BUB1B_ALLELE_CURATION` |
| Fig 4 · Interrogatorio estructural | `06_BUBR1_STRUCTURE` |
| Fig 5 · AlphaGenome REF/ALT/Δ | `05_HIDDEN_SECOND_ALLELE` |
| Fig 6 · Funnel | **RESUELTO** — la genera `notebooks/03_TRACK1_GENOME_WIDE.ipynb` |
| Fig 7 · Conservación ortóloga | **ya tiene origen ejecutable** — pipeline `src/structure/` → `src/make_fig7.py`, reproducible desde la descarga |
| Fig 8 · Baseline externo | **ya tiene origen ejecutable** — `src/baseline/` → `src/make_fig8.py`, desde las salidas de Exomiser |

---

## EXP-006 — el experimento que faltaba

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
| Filtro | `IMPACT` HIGH o MODERATE — sin panel |
| Extraídas | **13 109 variantes en 6 322 genes** |
| Siguiente | frecuencia poblacional, modelos de herencia, agregación por gen |

**Preregistro.** Ver `docs/DECISIONS.md`.

**Los dos desenlaces son buenos:**

- Si `BUB1B` queda arriba compitiendo contra 6 322 genes → *no lo encontramos porque lo
  buscábamos; sobrevivió a una búsqueda sin panel*.
- Si gana otro gen → **acabamos de evitar un error**, que vale más.

---

## Datos disponibles y bloqueos

| Recurso | Estado |
|---|---|
| VCF completo (4 carriles) | **Disponible** |
| FASTQ | **Solo L001** (~13×) de los cuatro esperados |
| BAM / CRAM de profundidad completa | **No disponible — bloquea EXP-012** |
| Genotipos parentales | **No disponibles — bloquean EXP-013** |
| Respuestas clínicas (líquido amniótico, kit de librería, hemograma) | **Pendientes** |

> **Prohibido afirmar un negativo de variante estructural con L001.** Un carril a ~13× sirve
> como piloto, no para cerrar una ausencia.
