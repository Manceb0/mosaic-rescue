# EXP-022 · `LZTR1` e `IGBP1` — auditoría de los competidores que quedaban

> **`DERIVED` + `EXTERNAL`** — la genética sale de la anotación local; la asociación
> gen-enfermedad, de literatura verificada en sesión. **No se envió ningún dato del paciente
> a ningún servicio externo**: las consultas fueron por símbolo de gen.
>
> **Origen ejecutable:** `src/prioritization/genome_wide.py` (`load`) sobre `work/gw/highmod_ann.tsv`.
>
> **Saneado:** sin coordenadas, sin HGVS completo, sin rsID. Se describe la clase de
> consecuencia, la cigosidad y la clasificación ClinVar, que es el nivel al que este
> repositorio ya documenta `BUB1B`.

## Por qué se auditaron, y por qué el enunciado anterior estaba mal

`research/SCIENTIFIC_CRITICAL_PATH.md` tenía la rama 5 **EN CURSO** con el texto
«`LZTR1` #2, `IGBP1` #3». Ese enunciado no corresponde a ningún ranking del proyecto:

| Ranking | `LZTR1` | `IGBP1` | `BUB1B` |
|---|---|---|---|
| `A0` congelado | #16 | #5 | **#4** |
| `A1_GENETICS_CLINVAR` | #5 | #6 | **#1** |
| `B0_FULL_PROBAND` | #4 | #6 | **#1** |
| Exomiser `BASELINE-PRIMARY` (398 genes distintos, 470 filas gen × modelo de herencia) | #24 | #61 | **#2** |

Lo que sí es cierto, y es lo que la rama quería decir: **son el 2.º y el 3.er competidor sin
auditar** por detrás de `BUB1B`, una vez descartados `CTU2`, `PEX5` y `SLC22A1` (EXP-021,
polimorfismos comunes) y `FANCD2` (EXP-020). El texto se corrige con los puestos reales.

## Lo que la anotación local dice, sin adornos

| | `LZTR1` | `IGBP1` |
|---|---|---|
| Consecuencia | **stop_gained** (`HIGH`) | missense (`MODERATE`) |
| Transcrito | MANE, canónico | MANE, canónico |
| Cigosidad | **heterocigoto** | **hemicigoto** (X, varón) |
| `FILTER` | PASS | PASS |
| Profundidad / `GQ` | **48 / 99** | 23 / 69 |
| Balance alélico | 0,50 | 1,00 |
| `MAX_AF` | 2,99 × 10⁻⁵ | 1,02 × 10⁻⁴ |
| ClinVar | **patogénica / probablemente patogénica** | significado incierto |
| Predictores | — | SIFT deletérea (0,01) · PolyPhen posiblemente dañina (0,767) |

**Ninguno de los dos se cae por calidad ni por frecuencia.** Ese fue el filtro que mató a
`FANCD2` y a los tres de EXP-021; aquí no aplica. Hay que argumentar de verdad.

## Restricción metodológica que se respeta

`config/phenotype_v2.yaml` fija la **regla de polaridad**: solo los términos documentados
cuentan como positivos, y **lo no mencionado es DESCONOCIDO, nunca negativo**. Por tanto
**no** se puede argumentar «el paciente no tiene discapacidad intelectual». Los descartes de
abajo se sostienen en cigosidad, mecanismo y frecuencia, **no** en ausencia de rasgos.

---

## `LZTR1` — **NEGATIVE como explicación del fenotipo MVA**, pero **hallazgo real que se reporta**

### 1 · La forma sindrómica exige dos alelos, y solo hay uno

Los variantes bialélicos de pérdida de función en `LZTR1` causan **síndrome de Noonan
autosómico recesivo** (Johnston et al., *Genet Med*, DOI 10.1038/gim.2018.5). Aquí hay **un
solo alelo, en heterocigosis**. La configuración recesiva no existe: mismo argumento que
cerró `FANCD2`, y es un argumento de cigosidad, no de conveniencia.

El Noonan **dominante** por `LZTR1` no se produce por pérdida de función, sino por missense
concretas que afectan a la superficie de reconocimiento de sustrato del dominio Kelch y
**aumentan** la señalización RAS-MAPK (Motta et al., *Hum Mol Genet* 28:1007, 2019).
Nuestro alelo es una parada prematura, es decir, la clase equivocada para ese mecanismo.

### 2 · Lo que sí produce un LoF heterocigoto no es aneuploidía

La pérdida de función en heterocigosis se asocia a **schwannomatosis**: predisposición a
schwannomas múltiples **de inicio adulto**, y con menor frecuencia meningiomas; el mecanismo
es pérdida de función con segundo golpe somático. También se ha descrito asociada a
**manchas café con leche múltiples aisladas** (*Genet Med*, 2024).

`LZTR1` actúa en el eje **RAS-MAPK**. **No tiene función establecida en el punto de control
de ensamblaje del huso ni en la segregación cromosómica**, que es lo que habría que explicar
para competir con `BUB1B` por la aneuploidía variegada. Un gen no compite por una hipótesis
solo por estar arriba en una lista: tiene que poder producir el fenómeno.

El tumor del probando es un **rabdomiosarcoma**, un sarcoma de partes blandas. No es un
schwannoma. La coincidencia es «predisposición tumoral» en abstracto, que es demasiado
grueso para sostener nada.

### 3 · Pero **no se archiva como ruido**

Es una parada prematura en el transcrito MANE, **heterocigota, de alta calidad (DP 48,
`GQ` 99, balance alélico 0,50, PASS), rara (`MAX_AF` 3 × 10⁻⁵) y clasificada patogénica /
probablemente patogénica en ClinVar**. Eso no es un artefacto.

**Se registra como candidato secundario / incidental DE INVESTIGACIÓN**, no como hipótesis
causal del MVA y **no** como un hallazgo clínico devolvible. La diferencia importa: llamarlo
«hallazgo secundario» a secas le atribuye un estatus clínico que todavía no tiene. Exigiría
confirmación independiente por un método ortogonal y un procedimiento de devolución de
resultados antes de significar nada para nadie.
Es exactamente el tipo de cosa para la que sirve una búsqueda sin panel: aparece algo real
que nadie estaba buscando.

> **Límite explícito.** Este proyecto es investigación preclínica y **no emite
> recomendaciones clínicas** (`CLAUDE.md`, Regla Dura 3). La relevancia clínica de un
> hallazgo secundario, su confirmación por un método ortogonal y cualquier consecuencia
> asistencial **corresponden al equipo clínico**, no a este análisis.

---

## `IGBP1` — **NEGATIVE**, por cuatro vías independientes

### 1 · El mecanismo reportado no es el nuestro

`IGBP1` (Xq13.1, OMIM 300139) se asocia al **trastorno del desarrollo intelectual ligado al
X, sindrómico, 28** (MRXS28, MIM 300472): agenesia del cuerpo calloso, coloboma de iris y
nervio óptico, retrognatia grave y déficit intelectual.

Las únicas alteraciones descritas son **dos cambios en la región 5' inmediatamente anterior
al codón de iniciación AUG** (`-57delT` y `-55T>A`), es decir, un mecanismo de **disrupción
del inicio de la traducción**. Nuestra variante es una **missense codificante**. No es la
misma clase de lesión ni actúa por la misma vía.

### 2 · La asociación descansa en **una sola familia**

Dos hermanos, un único informe (Graham et al., 2003). No replicada. Un gen-enfermedad con esa
base de evidencia no puede desplazar a un modelo causal con OMIM, herencia compatible y
mecanismo conocido.

### 3 · La frecuencia es demasiado alta para el síndrome que tendría que causar

`MAX_AF` = 1,02 × 10⁻⁴ (gnomADe_NFE). En un trastorno ligado al X, **los varones son
hemicigotos**: cada portador estaría afectado. Una frecuencia de ~1 de cada 10 000 alelos es
**fuertemente inconsistente** con un modelo ultra-raro, penetrante y causal para un síndrome
descrito una sola vez en la literatura.

**No se escribe «incompatible».** Esa palabra exigiría certeza sobre penetrancia, sobre el
emparejamiento de ancestría entre la frecuencia y el probando, y sobre la validez del propio
modelo gen-enfermedad, y no se tiene ninguna de las tres. El veredicto `NEGATIVE` se sostiene
en **mecanismo + herencia + frecuencia a la vez**, no en esta frase sola.

### 4 · Y la sustitución es conservadora

Metionina → leucina: los dos residuos son alifáticos hidrofóbicos. PolyPhen la deja en
**0,767**, «posiblemente dañina», por debajo del umbral de «probablemente dañina». SIFT y
PolyPhen no coinciden en fuerza. La llamada además tiene menos apoyo que la de `LZTR1`
(DP 23, `GQ` 69).

---

## Consecuencia para el camino crítico

La rama 5 pasa de **EN CURSO** a **CERRADO**:

| Competidor | Origen | Veredicto |
|---|---|---|
| `CTU2`, `PEX5`, `SLC22A1` | `A0` #1–#3 | **NEGATIVE** — polimorfismos comunes con rsID (EXP-021) |
| `FANCD2` | Exomiser #6 | **NEGATIVE** — alelos al ~47 %, todos heterocigotos (EXP-020) |
| `LZTR1` | `B0` #4 | **NEGATIVE** como causa del MVA — recesivo imposible con un alelo; el LoF heterocigoto da schwannomatosis de inicio adulto, no aneuploidía. **Hallazgo secundario registrado** |
| `IGBP1` | `B0` #6 | **NEGATIVE** — mecanismo distinto del reportado, asociación de una sola familia, y frecuencia fuertemente inconsistente con un modelo penetrante. Los tres juntos, no uno solo |

**Ningún competidor sobrevive.** `BUB1B` es la hipótesis causal en pie, con sus dos números
(`A0` #4, `A0-FREQFIX` #1) y con la fase todavía sin resolver.

## Qué falsaría esta auditoría

- Que apareciera un **segundo alelo de `LZTR1`** no detectado por el pipeline codificante
  (SV, CNV o variante reguladora): reabriría el Noonan recesivo. Es la misma clase de hueco
  que la rama 4 deja abierta para `BUB1B`, y **no está descartada**.
- Que se publicara una función de `LZTR1` en la segregación cromosómica.
- Que MRXS28 se replicara con variantes **codificantes** y a frecuencias compatibles.

## Verificación de identificadores

`CLAUDE.md` Regla Dura 5. Los identificadores de gen y enfermedad (OMIM 300139, MIM 300472)
se comprobaron en sesión el 2026-09-02. Las referencias bibliográficas se citan por
autor, revista y año; **los DOI y PMID concretos de Johnston 2018, Motta 2019, Graham 2003 y
el trabajo de manchas café con leche de 2024 no se transcriben aquí porque no se verificaron
uno a uno en sesión**, y este proyecto no escribe identificadores sin comprobar.
