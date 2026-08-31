# Registro de experimentos

> Una página para ver **dónde está la investigación**. Cada entrada apunta a su origen
> ejecutable. Si un resultado no tiene origen ejecutable, se marca como tal — no se disimula.

## Estado

| ID | Experimento | Estado | Origen ejecutable |
|---|---|---|---|
| **EXP-001** | QC de FASTQ (L001) | COMPLETO | `src/qc_fastq_sample.py` → **falta notebook** |
| **EXP-002** | Censo del VCF | COMPLETO | `src/vcf_variant_census.py` → **falta notebook** |
| **EXP-003** | Anotación VEP, pasada 1 | COMPLETO | `src/run_vep_pass1.sh` |
| **EXP-004** | Escaneo del panel MVA | COMPLETO | `src/build_funnel.py` |
| **EXP-005** | Escaneo del panel renal | COMPLETO | `src/build_funnel.py` |
| **EXP-006** | **Ranking genome-wide sin panel** | **EN CURSO** | `src/prioritization/` |
| **EXP-007** | Curación ACMG de los alelos | COMPLETO | disperso → **falta notebook** |
| **EXP-008** | Alelo regulador oculto | COMPLETO · **NEGATIVO** | disperso → **falta notebook** |
| **EXP-009** | Prueba con AlphaGenome | COMPLETO · **NEGATIVO** | `src/alphagenome_*.py` |
| **EXP-010** | Estructura de BUBR1 | PARCIAL | disperso → **falta notebook** |
| **EXP-011** | Conservación ortóloga | SIGUIENTE | — |
| **EXP-012** | SV / CNV en `BUB1B` | **BLOQUEADO** — BAM/CRAM de profundidad completa | — |
| **EXP-013** | Fase parental | **BLOQUEADO** — muestras de los padres | — |
| **EXP-014** | MitoRead | PLANIFICADO | — |
| **EXP-015** | Huella de mosaicismo | PLANIFICADO | — |
| **EXP-016** | Track 2 · mecanismo | **CON COMPUERTA** — no se abre hasta cerrar EXP-006 | — |

---

## Deuda reconocida

**Nueve de los diez experimentos completados no tienen notebook de investigación.** Existen
como scripts sueltos en `src/` y como conclusiones en `docs/`, pero no como el recorrido
*pregunta → preregistro → método → ejecución → falsación → decisión* que permite
seguirlos, cuestionarlos y repetirlos.

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
| Fig 6 · Funnel | `03_TRACK1_GENOME_WIDE` |

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
