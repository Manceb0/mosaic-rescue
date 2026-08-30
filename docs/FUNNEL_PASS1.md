# The Genomic Funnel — pasada 1

> Predicciones escritas antes de ejecutar: `docs/DECISIONS.md`, «Preregistro — Fase 2.1».
>
> **⚠ Saneado de forma conservadora.** Este documento nombra genes y clases de
> consecuencia, pero **no** incluye coordenadas genómicas, cambios proteicos concretos,
> profundidades ni genotipos. Ese detalle vive en `work/lanes/` (ignorado por Git).
> **Decisión pendiente del responsable del dato:** si la memoria final debe nombrar la
> variante —cosa habitual e inevitable en un entregable de Track 1—, hay que decidir
> explícitamente qué nivel de detalle se versiona. Ver `CLAUDE.md`, Regla Dura 1.

## El funnel, con números reales

```
5 012 204   variantes en el VCF
      │
      ▼
4 943 948   anotadas por VEP        (68 256 saltadas: contigs decoy sin genes)
      │
      │     6 608 298 filas de anotación — más de una por variante (alelo × gen)
      ▼
    ┌──────────────────────────────────────────┐
    │  por variante, tomando el IMPACT máximo  │
    ├──────────────────────────────────────────┤
    │  HIGH          928        0,019 %        │
    │  MODERATE   12 653        0,256 %        │
    │  LOW        21 076        0,426 %        │
    │  MODIFIER 4 909 291       99,299 %       │
    └──────────────────────────────────────────┘
      │
      ├── carril MVA          →  2 HIGH · 23 MODERATE
      ├── carril RENAL        →  2 HIGH · 21 MODERATE
      └── carril GENOME-WIDE  →  928 HIGH en 533 genes
```

**Advertencia sobre el conteo:** `--pick_allele_gene` emite una fila por alelo y gen, así
que una variante entre dos genes produce dos filas. 6,6 M filas sobre 4,94 M variantes.
Contar filas inflaría el funnel; todo lo de arriba está contado **por variante**.

## Contraste con lo preregistrado

| # | Predicción | Resultado | |
|---|---|---|---|
| 1 | ~1–2 % con consecuencia codificante | **0,70 %** (HIGH+MODERATE+LOW) | ≈ |
| 2 | Mayoría intergénicas e intrónicas | 99,3 % `MODIFIER` | ✅ |
| 3 | ~10–15 k codificantes raras | Pendiente: necesita gnomAD | — |
| 4 | **0 o 1 HIGH en el panel MVA** | **2** | ❌ |
| 5 | **0 HIGH en el panel renal** | **2** | ❌ |
| 6 | Genome-wide = más ruido que señal sin frecuencia | Confirmado | ✅ |

### Lección sobre mi propio preregistro

La predicción #4 estaba **mal redactada** y hay que decirlo. Escribí *«0 o 1 variantes de
alto impacto en el panel MVA»* y, como falsificador, *«≥2 de alto impacto en un gen MVA»*.
Son dos cosas distintas —contar en el panel entero o dentro de un solo gen— y las mezclé.

El resultado real: 2 HIGH en el panel, pero **en genes distintos**. Y el patrón que de
verdad importaba aparece de otra forma, que mi predicción no contemplaba.

Un preregistro sirve para no reinterpretar después. Éste, mal escrito, admite dos
lecturas. **Se registra como fallo de método, no solo de predicción.**

---

## Carril MVA

De 25 genes del panel, con variantes anotadas en 22.

| Gen | HIGH | MODERATE |
|---|---:|---:|
| **BUB1B** | **1** | **1** |
| ANAPC1 | 1 | 1 |
| CEP192 | 0 | 6 |
| KNL1 | 0 | 5 |
| CENPF | 0 | 4 |
| CENPE | 0 | 2 |
| MAD1L1, SLF2, SMC5, ZWILCH | 0 | 1 cada uno |

### `BUB1B` — dos candidatos, y el patrón coincide con el publicado

En `BUB1B` aparecen **dos variantes, ambas `PASS`, ambas en heterocigosis, ambas con
balance alélico limpio y ninguna presente en dbSNP**:

- una **truncante** sobre el transcrito MANE;
- una **missense** en la región C-terminal, la que contiene el dominio quinasa.

Eso reproduce el patrón descrito en la literatura para MVA por `BUB1B`: en pacientes con
mutaciones bialélicas, **una missense se empareja con una truncante**, y en el grupo de
mutantes missense el cambio ocurre de forma consistente **en el dominio quinasa de BubR1o
cerca de él** ([Suijkerbuijk et al., PMID 20516114](https://pubmed.ncbi.nlm.nih.gov/20516114/);
[Hanks et al., PMID 15475955](https://pubmed.ncbi.nlm.nih.gov/15475955/)).

El mecanismo descrito encaja además con la rama de dosis residual: la baja abundancia de
proteína resulta de **la ausencia de transcrito del alelo truncante combinada con el alto
recambio proteico del mutante missense**.

### Lo que NO se puede afirmar todavía

> **La fase no está resuelta.** Las dos variantes distan ~11 kb. El bloque `PID` más largo
> de todo el genoma mide 288 pb (`docs/VCF_HEADER.md`), así que **no hay relación de fase
> entre ellas** y no hay genotipos parentales.
>
> Formulación permitida, la del `docs/05_CONTRATO_VISUAL.md` §7:
>
> > *Two candidate variants in the same gene; phase unresolved. A recessive biallelic
> > mechanism cannot be claimed unless trans configuration is established or independently
> > supported.*

Falta además, y es pasada 2:

1. **Frecuencia poblacional (gnomAD).** La ausencia de rsID sugiere rareza, pero no la
   demuestra: depende de la versión de dbSNP con que anotó el caller.
2. **ClinVar** para ambas.
3. **Predicción de patogenicidad** para la missense (CADD, REVEL).
4. **Predicción de NMD** para la truncante: determina si el alelo produce proteína
   truncada o ninguna, y eso cambia el cálculo de dosis residual.

### Consecuencia sobre una decisión ya congelada

`docs/03_ALPHAGENOME_ASSESSMENT.md` §4.1 dejó la rama de **dosis residual funcional** como
`PURSUE CONDICIONAL`, con una condición de activación explícita:

> *«Se activa solo si Track 1 resuelve a `BUB1B`…»*

**Esa condición se ha cumplido, provisionalmente.** No se activa aún: primero hay que
descartar que la missense sea un polimorfismo común. Pero el umbral publicado del ~50 % de
proteína residual (brief §3.2) pasa de ser una nota a ser la pregunta operativa.

---

## Carril renal

Dos HIGH, y las dos ilustran por qué el filtro de frecuencia es imprescindible: ambas son
`start_lost` **con rsID conocido**, en `ATP6V1B1` y `VDR`. Un `start_lost` en un
polimorfismo frecuente es exactamente el falso positivo que `IMPACT=HIGH` produce cuando se
lee sin frecuencia poblacional.

`CLCNKB` (5 MODERATE) y `CLCNKA` (3) son los que merecen mirada en pasada 2. **`MAGED2`:
17 variantes, ninguna HIGH ni MODERATE** — consistente con la corrección de prioridad de
`docs/04_ARQUITECTURA_MAESTRA.md` §4.

La rama del fenotipo mixto **no se activa** con esto. Sigue condicional, y sigue
dependiendo del email sobre líquido amniótico y bioquímica.

---

## Carril genome-wide

928 variantes HIGH en 533 genes; 88 genes con ≥2. **Sin filtro de frecuencia esto es
ruido**, como se predijo: la mayoría serán variantes comunes y anotaciones sobre
pseudogenes y transcritos mal soportados.

Este carril **no se abandona**: se reevalúa en pasada 2 con gnomAD. Su función es impedir
que los paneles actúen como anteojeras, y esa función sigue viva precisamente hasta que se
pueda filtrar bien.

---

## Procedencia

VEP 116.1, caché `116_GRCh38`, modo `--offline --cache`. Hashes sha256 de entrada y salida
en `work/pass1/*.provenance.txt`. Reproducible con `src/run_vep_pass1.sh` y
`src/build_funnel.py`.
