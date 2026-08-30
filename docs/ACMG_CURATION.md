# Curación de evidencia estilo ACMG/AMP — investigación, no clínica

> **Esto no es una clasificación clínica.** Es una curación de evidencia en formato
> ACMG/AMP para uso en investigación. Ninguna afirmación de este documento constituye un
> informe diagnóstico ni sustituye la interpretación de un laboratorio acreditado.
>
> **Saneado:** sin coordenadas, rsID ni cambios proteicos. Detalle en `work/acmg/`.

## Relación gen-enfermedad

`BUB1B` – MVA1: **Definitive**, herencia **autosómica recesiva** (ClinGen). Ese es el marco
que hace aplicable el criterio `PVS1` y el que obliga a exigir **dos alelos** — de ahí que
la fase sea el bloqueo central.

---

## `PVS1` para el alelo truncante — árbol recorrido, no asumido

El criterio no se aplica por ser `stop_gained`. Hay que pasar el árbol de decisión.

| Paso del árbol | Estado |
|---|---|
| ¿Es LoF un mecanismo de enfermedad establecido para el gen? | **Sí** — MVA1 por `BUB1B` es recesiva por pérdida de función |
| ¿Está en el transcrito clínicamente relevante? | **Sí** — MANE Select y canónico |
| ¿Se espera degradación por NMD? | **Sí — medido, ver abajo** |
| ¿Afecta a una región crítica? | No es necesario dirimirlo si NMD aplica |

### La medición que exige el árbol

«Exón 17 de 23» **no es suficiente**: la regla de los 50–55 nt se define respecto a la
**última unión exón-exón**, no respecto al número de exón.

Se reconstruyó la estructura del transcrito MANE sondeando la región con variantes
sintéticas sobre la secuencia de referencia del propio caché — **a resolución de una base**,
y usando el mismo *release* de VEP que se empleará en todo el análisis, así que las
coordenadas salen de los metadatos del propio transcrito y no de una fuente paralela:

```
exón 17  ← aquí está el codón de parada prematuro
exón 18
exón 19
exón 20
exón 21
exón 22
─────────  ÚLTIMA UNIÓN EXÓN-EXÓN
exón 23  ← aquí está la missense
```

| | |
|---|---|
| Última base del exón 22 | CDS **2957** |
| Primera base del exón 23 | CDS **2958** |
| Posición del PTC | CDS **2210** |
| **Distancia del PTC a la última unión exón-exón** | **748 nt aguas arriba** |
| Umbral de la regla | 50–55 nt |
| Margen | **13,6×** |

**NMD predicho con holgura.** Ahora es un número, no un «exón interno, seguro que sí».

> Sigue siendo **predicción**. El NMD puede ser incompleto, y no se ha medido transcrito en
> este paciente. Salida permitida: `NMD predicho`. **Nunca** `expresión cero`.

**Veredicto:** `PVS1` **CANDIDATO**, con la ruta del árbol favorable. Fuerza final pendiente
de confirmar que no hay transcritos alternativos relevantes que rescaten el exón.

---

## `PM2` — no automático por «AF ~10⁻⁴»

ClinGen rebajó `PM2` a **Supporting**, y la frecuencia se evalúa contra lo plausible para
la enfermedad, no contra un umbral fijo.

**Alelo truncante:**

| Población | Frecuencia |
|---|---|
| Máxima poblacional | **≈ 1,0 × 10⁻⁴** (europea no finlandesa) |
| Africana, americana, este-asiática, sur-asiática | **0** |
| Genomas (global) | ≈ 3,3 × 10⁻⁵ |

Compatible con un alelo recesivo raro. **Pero hay un pendiente que no se puede resolver
offline:** la propia entrada de ClinVar advierte que los datos de frecuencia de gnomAD en
esa posición pueden tener problemas de calidad. La distribución —presente solo en una
población, cero en las demás— es compatible tanto con un alelo raro de origen europeo como
con un artefacto concentrado en un dataset. **No se puede distinguir sin revisar cobertura y
métricas de calidad de gnomAD en esa posición.**

**Veredicto:** `PM2_Supporting` **CANDIDATO**, pendiente de auditar cobertura y calidad, no
solo el AF.

**Alelo missense:** ausente de **todas** las poblaciones, exomas y genomas. `PM2_Supporting`
**CANDIDATO**, más limpio que el del truncante.

---

## `PP3` — no se construye sumando SIFT y PolyPhen

Esto es un error frecuente y hay que evitarlo explícitamente: **SIFT y PolyPhen no son dos
evidencias independientes**. ClinGen recomienda **una sola aplicación** de `PP3`/`BP4`,
usando un **predictor calibrado** y asignando la fuerza por umbrales publicados, no por
mayoría de herramientas.

Lo que tenemos hoy (`deleterious` 0,01 y `probably_damaging` 0,997) es **una señal
direccional**, no un `PP3` asignable.

**Veredicto:** `PP3` **PENDIENTE**. Requiere REVEL, BayesDel, MutPred2 o VEST4 — ninguno
disponible offline en el caché actual.

### Umbrales de REVEL — **preregistrados antes de ver el score**

Congelados aquí para que la asignación de fuerza no se elija después de conocer el
resultado. Umbrales calibrados de ClinGen:

| Rango de REVEL | Criterio | Puntos |
|---|---|---|
| **≥ 0,932** | `PP3_Strong` | **4** |
| 0,773 – 0,931 | `PP3_Moderate` | 2 |
| 0,644 – 0,772 | `PP3_Supporting` | 1 |
| < 0,644 | **Ningún `PP3`** | 0 |

`BP4` tiene sus propios umbrales calibrados en el extremo bajo, en la misma publicación.

**Reglas de uso, también congeladas:**

1. **Una sola aplicación.** REVEL sustituye a SIFT y PolyPhen; **no se suman**.
2. La fuerza sale del umbral, no de que «tres herramientas coincidan».
3. Si REVEL cae por debajo de 0,644, `PP3` **no se aplica** — y se registra como tal en
   lugar de buscar otro predictor que dé el resultado deseado.

---

## `PM1` — no por intuición

Que la missense caiga en el dominio C-terminal **no basta**. `PM1` exige demostrar una
región funcional crítica con **enriquecimiento de variantes patogénicas y escasez de
benignas**.

Se puede demostrar, y produce además una figura útil:

> **Mapa de BUBR1 a lo largo de la proteína** con las variantes de ClinVar `P`/`LP` frente a
> las `B`/`LB`/`VUS`, y el candidato marcado. Si el dominio C-terminal concentra
> efectivamente la enfermedad, `PM1` pasa a ser defendible **con el dato delante**.

**Veredicto:** `PM1` **PENDIENTE**. Requiere el VCF completo de ClinVar.

---

## `PP5` — deliberadamente NO usado

El alelo truncante figura en ClinVar como patogénico por un *submitter* con criterios. **Eso
no se convierte en `PP5`.** ClinGen recomienda **abandonar `PP5`/`BP6`** y evaluar la
evidencia primaria de forma independiente.

La etiqueta de ClinVar se registra como **evidencia externa a desglosar**, no como criterio.

---

## `PM3` — bloqueado por decisión del proyecto

Algunas implementaciones de ClinGen permiten puntuación reducida de `PM3` con fase
desconocida. **Para este proyecto se bloquea por completo.**

Motivo: es el criterio que convertiría «dos variantes en el mismo gen» en «heterocigosis
compuesta», que es exactamente la afirmación que la fase no sostiene. Ser más conservadores
aquí nos conviene.

---

## Tabla de curación

| Criterio | Truncante | Missense |
|---|---|---|
| Gen-enfermedad | `BUB1B`–MVA1 **Definitive, AR** | ídem |
| `PVS1` | **CANDIDATO** — árbol recorrido, NMD medido a ~750 nt | No aplica |
| `PM2_Supporting` | **CANDIDATO** — pendiente auditar calidad gnomAD | **CANDIDATO** — ausente de todas las poblaciones |
| `PP3` | No central | **PENDIENTE** — predictor calibrado |
| `PM1` | No aplica | **PENDIENTE** — distribución ClinVar en el gen |
| `PS3` | Sin ensayo variante-específico | Sin ensayo variante-específico |
| `PM3` | **BLOQUEADO** | **BLOQUEADO** |
| `PP4` | No usado todavía | No usado todavía |
| `PP5` | **NO USADO** por recomendación de ClinGen | n/a |

### Clasificación provisional

**Truncante:** con `PVS1` (Muy Fuerte, 8 puntos) + `PM2_Supporting` (1 punto) = **9 puntos**
en el marco bayesiano de puntos, lo que cae en **Likely Pathogenic** (6–9). Queda a un solo
punto de `Pathogenic`, y ese punto depende de evidencia que hoy no tenemos.

**Missense:** `PM2_Supporting` sola = 1 punto → **VUS**. Aunque `PP3` entrara como Moderado,
serían 3 puntos: sigue **VUS**. Solo saldría de ahí con `PM3` (bloqueado), `PS3` (no hay
ensayo) o evidencia de dominio y segregación.

---

## La formulación correcta

Esto evita el error de decir «tenemos dos variantes patogénicas»:

> **one likely pathogenic truncating allele + one rare missense candidate in the BUBR1
> stability domain, phase unresolved.**

Nótese *stability domain*, no *kinase domain*: BUBR1 es pseudoquinasa y lo que ese dominio
aporta es integridad conformacional (`docs/CANDIDATES_PASS2.md`).

---

## Qué añade más valor ahora

### Corrección — «ninguno de los tres cambia la categoría» era falso

Una versión anterior afirmó que los criterios pendientes refinan pero **no** cambian la
categoría de la missense. **Es incorrecto**: individualmente probablemente no, pero
**combinados sí**.

| Escenario | Puntos | Categoría |
|---|---|---|
| `PM2_Supporting` sola | 1 | VUS |
| `+ PP3_Moderate` | 3 | VUS |
| `+ PP3_Strong` | 5 | VUS |
| **`PM2_Supporting` + `PP3_Strong` + `PM1_Moderate`** | **7** | **Likely Pathogenic** |

Es decir: **la evidencia pendiente sí puede sacar la missense de VUS sin resolver la fase.**
Eso cambia la prioridad de las descargas — dejan de ser refinamiento cosmético.

Pero con una condición dura: **`PM1` no se gana por «está en el stability domain»**. Hay
que demostrar que es una región funcional crítica bien establecida y que no estamos viendo
simplemente una zona con mezcla de benignas y patogénicas. Si el mapa de ClinVar muestra esa
mezcla, `PM1` no se aplica y el escenario de 7 puntos no ocurre.

### `PM5` — posibilidad que el mapa de ClinVar puede revelar

Si existe **otra variante `P`/`LP` en el mismo residuo** con una sustitución distinta,
aplica `PM5` (Moderado, 2 puntos). Es un criterio que no habíamos considerado y que sale
del mismo VCF de ClinVar que hace falta para `PM1`.

### Lo que sigue siendo insustituible

1. **Resolver `trans`** → desbloquea `PM3`. Genotipos parentales o lectura larga dirigida.
2. **Demostrar efecto variante-específico sobre abundancia o estabilidad de BUBR1** →
   habilita `PS3`.

Estos dos no los sustituye ninguna descarga, y son los que llevarían el conjunto de
«candidato fuerte» a «mecanismo establecido».

### Bloqueos que requieren descarga

Orden de prioridad, decidido:

| # | Necesidad | Para qué | Puede cambiar categoría |
|---|---|---|---|
| **1** | **REVEL** | `PP3` — Supporting, Moderate, Strong o nada | Sí, en combinación |
| **2** | **VCF de ClinVar** | `PM1` por distribución, `PM5` por residuo, mapa proteico | Sí, en combinación |
| **3** | Cobertura y calidad de gnomAD | Auditar `PM2_Supporting` del truncante | No, pero lo asegura |

El tercero cierra el truncante: su frecuencia concentrada en una sola población merece
comprobar cobertura antes de dar `PM2` por bueno.
