# Auditoría de la cabecera del VCF — Fase 0.2

> Predicciones escritas **antes** de abrir el fichero: `docs/DECISIONS.md`, sección
> «Preregistro — Fase 0.2». Resultado: **cinco aciertos y un fallo**, y el fallo resultó
> ser menos valioso de lo que parecía en el primer vistazo.
>
> **Saneado:** el nombre de muestra no se leyó ni se imprime. El script lo redacta por
> defecto (Regla Dura 1).

## Lo esencial

| | |
|---|---|
| Formato | VCFv4.2, 2617 líneas de metadatos |
| Build | **GRCh38**, confirmado por longitud de `chr1` = 248 956 422 |
| Referencia | `GRCh38_no_alt_analysis_set_plus_hs38d1`, exclusiones GRC enmascaradas |
| Contigs | **2580, sin prefijo `chr`** |
| Caller | **Sentieon Haplotyper v202308.02** — implementación *funcionalmente equivalente* a GATK HaplotypeCaller |
| Ruta | Haplotyper → gVCF → GVCFtyper → VariantFiltration |
| Muestras | 1 |
| Anotación previa | **Ninguna.** VCF crudo |
| Tipo | VCF de variantes (no gVCF) |
| Variantes | **5 012 204** — recuento normal para WGS de muestra única en GRCh38 |

## Contraste con lo preregistrado

| # | Predicho | Real | |
|---|---|---|---|
| 1 | GRCh38 | GRCh38 | ✅ |
| 2 | Una muestra | Una | ✅ |
| 3 | Sin anotación | Sin anotación | ✅ |
| 4 | `GT` `AD` `DP` `GQ` `PL` | Los cinco | ✅ |
| 5 | **Sin fase física** | **`PGT` y `PID` presentes** | ❌ |
| 6 | No gVCF | No gVCF | ✅ |

---

## El fallo de la predicción 5, y por qué casi no cambia nada

`PGT`/`PID` existen. En el primer vistazo eso parecía levantar el techo del
`unphased ≠ trans`. **Se midió el alcance real, y no lo levanta.**

```
variantes con PID    770 458   (15,37 %)
bloques de fase      337 422

variantes por bloque   mediana 2 · p90 3 · p99 8 · máx 54
envergadura (pb)       mediana 7 · p75 17 · p90 29 · p99 91 · MÁXIMO 288

bloques ≥ 300 pb     0   (0,00 %)
```

**El bloque más largo del genoma entero mide 288 pb.** La mediana, 7 pb.

`PGT`/`PID` es *read-backed phasing*: solo enlaza variantes que el caller pudo colocar
sobre el mismo haplotipo ensamblado, y el límite físico es la longitud del fragmento. Con
reads de 149 bp, el alcance observado (máx 288 pb) encaja con fragmentos de ~300 pb — lo
que **valida de forma cruzada** la estimación de insertos del QC de L001.

Para heterocigosis compuesta esto es, en la práctica, inservible. `BUB1B` mide ~65 kb: el
bloque máximo cubre el **0,44 %** del gen. Dos variantes patogénicas en el mismo gen caerán
en bloques `PID` distintos salvo que estén a menos de 288 pb una de otra, y entre bloques
**no hay relación de fase**.

> **Conclusión.** El techo declarado en `docs/03_ALPHAGENOME_ASSESSMENT.md` §4.2 sigue en
> pie prácticamente intacto. La predicción falló en la letra —los campos están— y acertó
> en el fondo: **sin genotipos parentales, la fase sigue sin resolverse.**

### Para qué sí sirve

Un uso real y estrecho: **corrección de variantes multinucleotídicas (MNV)**. Dos SNV
adyacentes dentro del mismo codón producen un aminoácido distinto según estén en cis o en
trans, y una anotación que las trate por separado da el cambio equivocado. Con mediana de
7 pb, `PID` cubre exactamente ese caso.

No es el hallazgo espectacular. Es un detalle de anotación que, si se ignora, produce una
consecuencia proteica errónea sobre un candidato — y eso sí puede costar caro.

---

## Consecuencias operativas

### 1. Sin prefijo `chr` — riesgo de fallo silencioso

Todo BED, lista de regiones o coordenada del proyecto usa `1`, no `chr1`. Un desajuste de
estilo **no da error**: devuelve cero resultados, que se lee como «no hay nada aquí».
Verificar el estilo antes de cada intersección.

### 2. Filtrado duro, no VQSR — el segundo alelo puede estar filtrado

`VariantFiltration` con los umbrales estándar de GATK:

| Filtro | Umbral |
|---|---|
| `QD2` | QD < 2.0 |
| `MQ40` | MQ < 40.0 |
| `FS60` | FS > 60.0 |
| `MQRankSum-12.5` | MQRankSum < −12.5 |
| `RPRS-8` | ReadPosRankSum < −8.0 |
| `LowQual` | baja calidad |

Es lo correcto para una muestra única, pero el filtrado duro es más romo que VQSR.

> **Regla de dos niveles, no de equivalencia.**
>
> - **Nivel primario: `PASS`.** Es la vía normal de candidatos.
> - **Nivel de rescate: las filtradas.** Se abre **solo** cuando hay un alelo huérfano en
>   un gen de interés, y **solo alrededor de ese gen**.
>
> Abrir el nivel de rescate **no devuelve las variantes filtradas a la categoría de
> candidatas**. Obliga a examinar *por qué* falló cada una: `QD` bajo, sesgo de hebra,
> calidad de mapeo, posición en el read. Un filtro puede haber saltado por una razón
> técnica irrelevante en esa región — o por la razón correcta. Hay que mirarlo variante a
> variante, no levantar el filtro en bloque.

### 3. Anotación desde cero

`INFO` trae solo métricas del caller: `AC AF AN BaseQRankSum ClippingRankSum DB DP
ExcessHet FS InbreedingCoeff MLEAC MLEAF MQ MQRankSum QD ReadPosRankSum SOR`.

Sin frecuencias poblacionales, sin términos de consecuencia, sin ClinVar. La Fase 2.2
empieza de cero: hay que anotar nosotros.

`ExcessHet` e `InbreedingCoeff` son métricas de cohorte y **no significan nada con una
muestra única**. Ignorarlas; no usarlas como criterio de calidad.

### 4. `AD` presente — para qué sirve exactamente

**Corrección a la primera versión de este documento**, que decía que `AD` «sostiene la
evaluación de heterocigosis compuesta». Eso es sobreafirmar y hay que dejarlo preciso.

`AD` da **profundidad por alelo**. De ahí sale el balance alélico, que sirve para:

- **QC de llamada** — ¿tiene esta heterocigota un balance creíble, o es artefacto?
- **Señal de mosaicismo** — fracciones alélicas desviadas de 0,5 son la materia prima de
  la rama §6.

**`AD` no dice si dos variantes están en `trans`.** Para afirmar heterocigosis compuesta
hacen falta tres cosas, y la tercera hoy no la tenemos:

1. variante A + variante B en el mismo gen;
2. evidencia de que ambas son funcionalmente relevantes;
3. **fase en trans demostrada — o declarada explícitamente como no resuelta.**

Con bloques `PID` de 288 pb como máximo y sin genotipos parentales, el punto 3 queda sin
resolver salvo que las dos variantes estén a menos de esa distancia. La formulación
permitida sigue siendo la del `docs/05_CONTRATO_VISUAL.md` §7.

---

## Los tres carriles — se corren en paralelo, no se elige uno

Decidido: **no se elige entre MVA y renal.** El coste de añadir un segundo panel es
irrelevante frente al del análisis completo, y elegir uno antes de mirar es sesgo de
confirmación por diseño.

| Carril | Alcance | Por qué existe |
|---|---|---|
| **1 · Mecanismo MVA** | `config/panels/mva.txt` — universo amplio de inestabilidad cromosómica, no solo `BUB1B`. Codificante, splicing canónico, y segundo hit oculto cuando proceda | Es la hipótesis principal |
| **2 · Residual renal** | `config/panels/nephrocalcinosis.txt` — `MAGED2`, `SLC12A1`, `KCNJ1`, `BSND`, `CLCNKA/B` y diferenciales | La nefrocalcinosis desde el nacimiento mantiene la rama viva. **No demuestra Bartter** |
| **3 · Escape genome-wide** | HPO + raras dañinas + prior de herencia y mecanismo, **sin exigir pertenencia a ningún panel** | **El más importante de los tres.** Impide que los paneles funcionen como anteojeras |

El carril 3 protege contra el fallo más caro posible: que el gen causal sea uno que hoy no
está en ninguna de nuestras ideas — precisamente el tipo de caso que un organizador
plantea para que no se resuelva con una lista de genes.

### La dependencia que ordena todo

**Los tres carriles necesitan anotación.** Sin ella no hay asignación variante→gen, así
que ni siquiera el carril 1 puede arrancar. La anotación no es un paso más: es **el cuello
de botella único** de los tres.

Requisito no negociable: **anotación local y offline**. No se envían bloques de
información genómica del paciente a servicios externos, lo que descarta la API REST de
Ensembl y cualquier anotador en la nube.

### El funnel, y hasta dónde llega sin anotar

```
5 012 204 variantes crudas
        │                        ┌─ computable YA, sin anotación
        ▼                        │
   filtros y genotipo usable     ┤
        │                        │
        ▼                        └─ censo: src/vcf_variant_census.py
   raras                         ┐
        │                        │
        ▼                        │
   consecuencia funcional        ├─ REQUIERE ANOTACIÓN
        │                        │
   ┌────┼────┐                   │
   ▼    ▼    ▼                   │
  MVA renal genome-wide          │
   └────┼────┘                   │
        ▼                        │
  genes con ≥2 candidatos        │
        │                        │
        ▼                        ┘
  shortlist mecanística
        │
        ▼
  AlphaGenome / SV  ← solo sobre la shortlist, nunca sobre los 5 M
```

Cada bifurcación llevará su número real. Los dos primeros niveles salen del censo; del
tercero en adelante, todo espera a la anotación.

### Cuándo entra AlphaGenome, y cuándo no

| Candidato | Herramienta |
|---|---|
| Intrónico profundo | **AlphaGenome** |
| Regulador | **AlphaGenome** |
| VUS en región de splicing | **AlphaGenome** + SpliceAI |
| Segundo alelo invisible a la anotación de codificante | **AlphaGenome** |
| Nonsense / frameshift obvio | No aporta gran cosa |
| SV grande | **No.** Evidencia de reads y SV caller |

---

Reproducible con `src/vcf_header_audit.py`, `src/phasing_span_stats.py` y
`src/vcf_variant_census.py`. Ninguno imprime coordenadas, genotipos ni secuencia.

---

## Censo del VCF — los dos primeros niveles del funnel, medidos

Sin anotación. Todo agregado. `src/vcf_variant_census.py`.

### Filtros — el nivel primario y el de rescate, cuantificados

| Filtro | Variantes | % |
|---|---:|---:|
| **`PASS`** | **4 740 790** | **94,58** |
| `MQ40` | 211 334 | 4,22 |
| `QD2` | 75 477 | 1,51 |
| `LowQual` | 43 111 | 0,86 |
| `FS60` | 2 025 | 0,04 |
| `MQRankSum-12.5` | 762 | 0,02 |
| `RPRS-8` | 222 | 0,00 |

**Nivel primario: 4 740 790. Nivel de rescate: 271 414.**

El filtro dominante es `MQ40` — calidad de mapeo, no calidad de la llamada. Eso concentra
el nivel de rescate en regiones repetitivas y de mapeo ambiguo, que es exactamente donde
un segundo alelo puede esconderse legítimamente. Refuerza la regla de dos niveles: al
abrir el rescate alrededor de un gen candidato, `MQ40` será el motivo más frecuente y hay
que juzgarlo región a región.

### Composición

| Clase | Variantes | % |
|---|---:|---:|
| SNV | 4 080 038 | 81,40 |
| Deleción | 441 247 | 8,80 |
| Inserción | 424 059 | 8,46 |
| Multialélica | 66 860 | 1,33 |

Reparto normal para WGS humano. El 97,68 % cae en contigs primarios; el 2,32 % en no
colocados y decoy — que el decoy capture ese 2,3 % es señal de que la referencia
`no_alt + hs38d1` está haciendo su trabajo.

### Genotipos, y una observación relevante para la hipótesis

| Genotipo | Variantes | % |
|---|---:|---:|
| `0/1` | 3 047 077 | 60,79 |
| `1/1` | 1 898 267 | 37,87 |
| `1/2` | 66 860 | 1,33 |

**Ratio het/hom = 1,61**, dentro del rango esperado (~1,5–2,0).

Importa por una razón concreta: MVA es recesiva, y la consanguinidad elevaría la
probabilidad previa de una variante causal en homocigosis. Un ratio het/hom
**deprimido** sería la primera señal de consanguinidad genómica. 1,61 no la muestra.

> **Cuidado con esta inferencia.** El ratio het/hom es un proxy grosero. La prueba que
> vale es un análisis de **ROH** (*runs of homozygosity*): consanguinidad reciente produce
> tramos largos de homocigosis que un promedio genómico diluye. Hasta ejecutarlo, lo
> afirmable es *«no hay señal grosera de consanguinidad»*, no *«no hay consanguinidad»*.

### Balance alélico — la materia prima del mosaicismo

Heterocigotas bialélicas con `DP ≥ 10`, n = 2 999 053.

```
0.10   37 955  ###
0.15   57 081  #####
0.20   56 922  #####
0.25   57 469  #####
0.30   81 545  #######
0.35  150 096  #############
0.40  340 626  ###############################
0.45  532 665  #################################################
0.50  651 527  ############################################################
0.55  515 507  ###############################################
0.60  309 604  ############################
0.65  119 037  ##########
0.70   46 511  ####
0.75   17 904  #
```

**78,36 % entre 0,40 y 0,60**, con moda limpia en 0,50. Heterocigosis germinal sana.

**7,02 % por debajo de 0,30**, con un hombro izquierdo bastante plano entre 0,15 y 0,30.

> **Este 7 % NO es evidencia de mosaicismo.** Es el conjunto donde el mosaicismo *podría*
> estar, mezclado con error de mapeo, regiones repetitivas y salto de índice. Separar una
> cosa de otra necesita tres cosas que aún no tenemos:
>
> 1. restringir a regiones de alta confianza;
> 2. **controles procesados con el mismo pipeline** — el brief §1 los marcaba como
>    obligatorios a 45–60×, y este hombro es exactamente por qué;
> 3. comprobar si las variantes de bajo balance **se agrupan** por región o están
>    dispersas. Agrupadas apunta a artefacto local; dispersas y en contigs primarios con
>    buena profundidad es más interesante.
>
> Sin eso, cualquier lectura del 7 % es una historia, no un resultado.

### Profundidad

Mediana en sitios variantes: **~40×**. Variantes con `DP < 10`: 122 026 (2,43 %).

---

## Tres medidas independientes que concuerdan

Vale la pena registrarlo, porque es lo que da confianza en que el dataset es lo que dice
ser:

| Medida | Vía | Resultado |
|---|---|---|
| Profundidad efectiva | QC de L001, extrapolado a 4 carriles menos duplicados y mapeo | **~42,7×** |
| Profundidad observada | Mediana de `DP` en sitios variantes del VCF | **~40×** |
| Longitud de fragmento | Alcance máximo de bloque `PID` (288 pb) | **~300 pb** |
| Longitud de fragmento | Tasa de adaptador coincidente en R1 y R2 (2,04 / 2,12 %) | ~2 % de insertos < 149 pb |

Las dos primeras se obtuvieron por caminos completamente distintos —una desde FASTQ crudos,
otra desde el VCF— y coinciden. Las dos últimas también.
