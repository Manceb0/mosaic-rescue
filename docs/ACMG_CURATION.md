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
sintéticas sobre la secuencia de referencia del propio caché (offline, resolución 20 pb):

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
| Distancia del PTC a la última unión exón-exón | **≈ 750 nt aguas arriba** |
| Umbral de la regla | 50–55 nt |
| Margen | **~14×** |

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

La tabla lo señala sin ambigüedad. Los dos criterios que moverían la missense de VUS son:

1. **Resolver `trans`** → desbloquea `PM3`. Genotipos parentales o lectura larga dirigida.
2. **Demostrar efecto variante-específico sobre abundancia o estabilidad de BUBR1** →
   habilita `PS3`.

Todo lo demás —`PP3` calibrado, `PM1` por distribución— refina, pero no cambia la categoría.

### Bloqueos que requieren descarga

| Necesidad | Para qué | Estado |
|---|---|---|
| REVEL / BayesDel / MutPred2 / VEST4 | `PP3` calibrado | No disponible offline |
| VCF completo de ClinVar | `PM1` por distribución + figura del mapa proteico | No descargado |
| Cobertura y calidad de gnomAD en la posición | Auditar `PM2` del truncante | No disponible offline |
