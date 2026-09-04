# Auditoría transversal — 2026-08-31

> No es una limpieza cosmética. El objetivo era **encontrar dónde una afirmación vieja quedó
> invalidada o estrechada por evidencia posterior**, y separar el rastro histórico del estado
> actual.
>
> **Regla que gobierna la auditoría:**
>
> ```
> HISTORIA DE INVESTIGACIÓN          ESTADO CANÓNICO ACTUAL
> «qué creímos → qué lo falsó»       «qué sostenemos hoy»
>        docs/DECISIONS.md            research/CANONICAL_CLAIMS.md
> ```
>
> Las dos hacen falta. Anotar la corrección debajo de la afirmación vieja está bien **en la
> bitácora**; en un documento que un jurado lee como verdad actual **parece incoherencia, no
> rigor**, y ahí la afirmación se sustituye.

---

## AUDIT 1 · Afirmaciones canónicas

**Entregable:** `research/CANONICAL_CLAIMS.md` — 32 afirmaciones con formulación vigente,
evidencia, clase, confianza, qué sustituyen y **qué formulación más fuerte queda prohibida**.

Cubre las 16 áreas exigidas. Esa tabla manda: si otro documento la contradice, el otro
documento está obsoleto.

## AUDIT 2 · Escáner de afirmaciones obsoletas

**Entregable:** `src/audit_stale_claims.py` — mecánico y repetible. Clasifica cada hallazgo
según **dónde** aparece, que es lo que decide qué hacer con él.

| Antes | Después |
|---|---|
| **11 coincidencias en documentos canónicos** | **0** |

Las 12 restantes están todas en `docs/DECISIONS.md` y **son correctas ahí**: son el rastro.
Una de ellas es literalmente la corrección tachada de «#1 en los 15».

### Lo que encontró y se corrigió

| Dónde | Afirmación obsoleta | Sustituida por |
|---|---|---|
| brief §10.1 | «**Arimoclomol.** La nominación…» | **Se nomina una cartera experimental de tres brazos para discriminación preclínica, no un ganador terapéutico**, y la compuerta de cinco condiciones sigue sin cerrarse |
| brief §10.2 | «muy buena hipótesis farmacológica» | «hipótesis mecanística con el puente farmacológico **sin resolver**», con la contraevidencia |
| brief §10.3 · plan §306 | «lo que mantiene la hipótesis viva: dependiente de estrés» | La **tensión** en tabla: el mismo rasgo es razón y pasivo |
| arquitectura · contrato visual | «mtDNA-CN del paciente» | «estimación mtDNA-equivalente (prototipo)» |
| **figura hero** | **`MECHANISTIC CONVERGENCE`** | **`CONSISTENCY CHECK`** |
| roadmap | «Mechanistic convergence» en el diagrama | «Consistency check» |

> **El peor hallazgo fue la figura hero.** Llevaba la frase que el propio brief §5 prohíbe
> —«convergencia mecanística»— en lo primero que ve un jurado. El escáner ahora trata
> `figures/` como **canónico**, porque una figura se lee antes que cualquier documento.

## AUDIT 3 · Histórico frente a canónico

Se retiraron las anotaciones que yo había puesto en el brief y el plan, y su contenido se
movió a `docs/DECISIONS.md` § *lo que se creía sobre Track 2*, con la tabla
«creencia → qué la falsó».

**Ninguna idea vieja se borra.** Todas eran la mejor lectura con la evidencia de su momento.
Lo que cambia es **dónde viven**.

## AUDIT 4 · Grafo de independencia de la evidencia

```
                        DATOS DEL PACIENTE
                              │
                    ┌─────────┴─────────┐
                    │   VCF (4 carriles) │
                    └─────────┬─────────┘
          ┌───────────┬───────┴────────┬──────────────┐
          ▼           ▼                ▼              ▼
   nuestro ranking  Exomiser      panel renal    huella mosaico
   (EXP-006)        (EXP-006b)    (EXP-017)      (no ejecutada)
          │           │
          └─────┬─────┘
                │  A0-FREQFIX usa la BASE DE FRECUENCIAS de Exomiser
                ▼
          A0-FREQFIX  ── NO independiente de Exomiser

                        L001 FASTQ  ──►  MitoRead prototipo

   ══ SIN datos del paciente ══
   conservación  ← Ensembl Compara      estructura   ← AlphaFold DB
   AlphaGenome   ← modelo de secuencia  simulación   ← sin datos
```

| Relación | Clasificación |
|---|---|
| nuestro ranking ↔ Exomiser | **método independiente sobre datos compartidos** |
| `A0-FREQFIX` ↔ Exomiser | **derivado de la misma fuente** — no cuenta como convergencia |
| conservación ↔ ranking | **datos independientes** (secuencias externas) |
| estructura ↔ conservación | independientes entre sí; ambas `PREDICTED`/`EXTERNAL` |
| simulación de mosaicismo | **sin datos del paciente** — no es evidencia sobre el caso |

> **Consecuencia dura:** el ranking, Exomiser y el barrido renal **no son tres observaciones
> biológicas**. Son tres métodos sobre **el mismo VCF**. Un artefacto compartido los engaña a
> los tres — y hay prueba de que ocurre: los dos primeros señalan `SERPINA1`.
>
> **Las únicas líneas con datos genuinamente independientes son la conservación ortóloga y la
> estructura.** Ambas apoyan el mecanismo del alelo missense, ninguna apoya la causalidad del
> gen.

## AUDIT 5 · Puentes de Track 2

Corregido lo más importante: **el deterioro de HSF1 es razón Y pasivo**, no un prior en contra.

> *HSF1 impairment makes the pathway both mechanistically relevant and pharmacologically
> uncertain. Genetic augmentation can bypass the deficit; whether a stress-dependent
> pharmacological co-inducer can amplify the impaired endogenous response sufficiently
> remains unresolved.*

| Puente | Estado |
|---|---|
| 1 · variante de este paciente → inestabilidad | **UNRESOLVED** — solo inferencia estructural |
| 2 · inestabilidad → menos proteína | evidencia, **de otros alelos** |
| 3 · subir chaperonas → subir BUBR1 | **UNRESOLVED** — dependencia basal demostrada; la dirección de ganancia sigue sin medir |
| 4 · más BUBR1 → menos CIN | evidencia (`L4`) |
| 5 · aneuploidía → estrés proteotóxico | evidencia (`L4`) |
| 6 · subir HSP → rescate | evidencia (`L4`), **pero dependiente del cariotipo** |
| 7 · coinducción farmacológica → mismo rescate | **UNRESOLVED — no direct pharmacological bridge found** |
| 8 · efecto sobre CIN y supervivencia clonogénica | **NO DIRECT SAFETY DATA** |

**Puente 7 es `UNRESOLVED`, no `NEGATIVE`.** Nada lo cierra.

## AUDIT 6 · Realidad de los datos

| Dato | Realidad |
|---|---|
| VCF | de los **cuatro** carriles |
| FASTQ | **solo L001** en disco (~13×) |
| BAM/CRAM de profundidad completa | **no** |
| Genotipos parentales | **no** |
| RNA-seq · single-cell · proteómica | **no** |
| Tejido tumoral · cariotipo previo | **no** |
| Hemograma contemporáneo | **no** |

Toda afirmación de «profundidad efectiva ~43×» describe **un carril**, no el dataset del VCF.
Queda en `DECISIONS.md` como registro histórico; no aparece en canónicos.

## AUDIT 7 · Procedencia de figuras

| Figura | Generador | Estado |
|---|---|---|
| fig2 · fig3 · fig4 · fig5 | `src/make_figN.py` | vigentes; fig2/fig4 **regeneradas saneadas** |
| **fig6 · funnel** | `notebooks/03` | **vigente, con origen en notebook** |
| fig7 · conservación | `src/make_fig7.py` | vigente |
| fig8 · baseline | `src/make_fig8.py` | vigente |
| fig9 · simulación mosaico | `src/make_fig9.py` | vigente |
| fig10 · puentes Track 2 | `src/make_fig10.py` | vigente |
| bubr1_landscape | `src/make_landscape_figure.py` | vigente |
| **hero_pipeline** | **NINGUNO** | **⚠ DEUDA ABIERTA** |

> **`hero_pipeline` no tiene origen ejecutable.** Es HTML escrito a mano, y **viola la regla
> del propio proyecto**: *«ninguna figura final sin un notebook o pipeline reproducible».*
> Es además la figura más visible. Se corrigió su contenido obsoleto, pero la deuda de
> procedencia **queda abierta y registrada**, no disimulada.

## AUDIT 8 · Consistencia de estados

Los estados mezclaban vocabularios: `BLOQUEADO`/`BLOCKED`, `CERRADO · SURVIVES`,
`ABIERTO`, `COMPLETO`, `VIABILIDAD TÉCNICA`, `EN CURSO`, `PLANIFICADO`.

**Normalizado a exactamente cinco.** El texto descriptivo se conserva detrás de la etiqueta.

| Estado | Nº |
|---|---|
| `SURVIVES` | 11 |
| `NEGATIVE` | 6 |
| `UNRESOLVED` | 5 |
| `PARKED` | 4 |
| `BLOCKED` | 4 |

## AUDIT 9 · Privacidad

`python src/sanitize_scan.py` → **LIMPIO**. 95 ficheros versionados, 0 patrones sensibles.

**No se ha reescrito el historial de git**, conforme a la instrucción.

### Exposiciones históricas — para decisión aparte

| Qué | Dónde | Estado hoy |
|---|---|---|
| Número de residuo e identidad de aminoácidos | `fig2_landscape.svg`, `fig4_structural.svg`, commit `2b8d5e6` | **saneado en el estado actual**; sigue en el historial |
| Cambio nucleotídico exacto del paciente | `fig2_landscape.svg`, mismo commit | ídem |
| Identificador de muestra y flowcell | `docs/01_MASTER_BRIEF.md`, `src/` | ídem |
| Ruta local con nombre de usuario | dos scripts de `src/` | ídem |

El repositorio es **privado** (verificado). Reescribir el historial es destructivo y depende
de qué hallazgos se decida conservar en el entregable final.

## AUDIT 10 · Las cinco incertidumbres restantes

Ordenadas por ganancia de información esperada.

| # | Pregunta | ¿Ejecutable ahora? | Datos que exige | Coste | Qué desenlace cambia |
|---|---|---|---|---|---|
| **1** | **¿Hubo polihidramnios u oligohidramnios?** | **NO — es un email** | Historia obstétrica | ~0 | Son **opuestos** entre Bartter antenatal y MVA. Decide si `C16` es un segundo diagnóstico o un rasgo de MVA. **Mayor ganancia por unidad de esfuerzo de todo el proyecto** |
| **2** | **¿Los dos alelos están en *trans*?** | **NO — bloqueado** | Genotipos parentales **o** lectura larga sobre ~11 kb | bajo si llegan | Sin esto `PM3` sigue bloqueado y `C6` no se puede cerrar. Convierte «candidato» en «heterocigosis compuesta» |
| **3** | **¿El mutante de ESTE paciente es inestable?** | **NO — no lo ejecuta este proyecto** | Ensayo de abundancia y recambio, silvestre vs variante | medio | Cierra el **puente 1** y habilitaría `PS3`. Es el único camino que mueve la missense de VUS |
| **4** | **¿Hay un segundo hit estructural?** | **NO — bloqueado** | BAM/CRAM de los 4 carriles | medio | Es la clase de variante que el VCF no ve. Reabriría `FANCD2` y explicaría el segundo alelo ausente |
| **5** | **¿Una coinducción farmacológica reproduce el rescate genético en células con HSR deficiente?** | **NO — requiere laboratorio** | Par isogénico aneuploide/euploide, control positivo genético | alto | Es el **puente 7**. Y con el puente 8 en el mismo diseño, decide si Track 2 entra en el corredor |

> **Las cinco están bloqueadas por datos o por laboratorio. Ninguna es computacional.**
>
> Eso significa que no queda **ciencia nueva sobre los mismos datos**. Sí quedaba trabajo
> computacional —consolidación, procedencia y visualización— y era justo lo que faltaba: ver
> AUDIT 11. Lo que queda no se resuelve con más cómputo, y seguir
> generando análisis sobre los mismos datos produciría volumen, no información.
>
> **Cuatro de las cinco son un email.** Ese es el siguiente movimiento real.

---

## Qué merece el pitch, y qué el apéndice

| Al pitch | Al apéndice |
|---|---|
| El bug del cruce de alelos: **el pipeline encontró un error que favorecía a nuestro candidato, lo corrigió, `BUB1B` bajó, y aun así sobrevivió** | Detalle de la reconciliación de conteos |
| La **cancelación de BAF** reproducida en simulación: potencia 0,000 al 20 % | El índice de dispersión como detector — `UNRESOLVED` |
| Los **ocho puentes** de Track 2 y el corredor de rescate seguro | El mapa completo de las seis clases |
| **Se nominan brazos para discriminación preclínica, no un ganador terapéutico — y por qué** | Prototipo de MitoRead |
| Convergencia metodológica con Exomiser, **declarada como tal** | Auditoría de `FANCD2` |
| Conservación ortóloga: 0 de 120 ortólogos con la clase entrante | Desglose por clado |

**El diferencial no es haber encontrado `BUB1B`.** Es la disciplina con la que el proyecto
intentó romperlo — y las tres veces que falsó sus propias explicaciones y las conservó
anotadas.

---

## AUDIT 11 · Capa de notebooks — el fallo que las auditorías 1–10 no cubrían

**Encontrado por inspección humana de los `.ipynb`, no por ningún escáner.** Las auditorías
leían `.md`, figuras y código, pero **no juzgaban lo que un jurado ve al abrir un notebook**.

### El diagnóstico

| Problema | Evidencia |
|---|---|
| `03_TRACK1_GENOME_WIDE.ipynb` no mostraba **ninguna** figura | 0 salidas `display_data` con imagen. La sección «Figura 6» ejecutaba un script e imprimía el **nombre del fichero** que acababa de escribir fuera |
| `00_data_inventory.ipynb` era una plantilla sin ejecutar | `execution_count: null`, un `../data` que nunca existió, tabla para rellenar a mano |
| Afirmaciones obsoletas **dentro** del notebook ejecutado | decía correctamente `A0 = #4` y después «ganó sin fenotipo ni ClinVar»; y «baseline externo **independiente**», con la salida imprimiendo `CONVERGENCIA INDEPENDIENTE` |

**Por eso «0 obsoletos en canónicos» no era cierto:** el escáner no incluía `notebooks/`.

### Lo corregido en la raíz

- `src/baseline/compare_baseline.py` — el veredicto impreso **era la fuente** del claim
  obsoleto. Ahora imprime *convergencia metodológica sobre el MISMO VCF*.
- `src/audit_stale_claims.py` — `notebooks/` y `figures/` cuentan como **canónicos**, y se
  añadieron los tres patrones que se escaparon.

### El sprint

| Notebook | Ejecutado | Figuras | Mín. | Errores | Estado |
|---|---|---|---|---|---|
| `00_DATA_REALITY` | sí | 3 | 3 | 0 | **OK** |
| `01_TRACK1_GENOME_WIDE` | sí | **6** | 6 | 0 | **OK** |
| `02_BUB1B_ALLELE_CURATION` | sí | 4 | 4 | 0 | **OK** |
| `03_BUBR1_MECHANISM` | sí | 4 | 4 | 0 | **OK** |
| `04_HIDDEN_SECOND_ALLELE` | sí | 3 | 3 | 0 | **OK** |
| `05_RESIDUAL_PHENOTYPE` | sí | 3 | 3 | 0 | **OK** |
| `06_MOSAIC_AND_MITOREAD` | sí | 3 | 3 | 0 | **OK** |
| `07_TRACK2_SAFE_RESCUE` | sí | 3 | 3 | 0 | **OK** |

**29 figuras embebidas. Cero errores. Escáner limpio.**

Una figura solo cuenta si está **dentro** del `.ipynb` como `display_data`. Escribir un SVG en
`figures/` no cuenta — que era exactamente el fallo.

### Lo retirado

`00_data_inventory.ipynb` y el README antiguo (quince notebooks presuponiendo RNA-seq,
single-cell, longitudinal y cariotipo celular — **ninguno existe**) van a `docs/history/`.
`03_TRACK1_GENOME_WIDE.ipynb` queda sustituido por `01_TRACK1_GENOME_WIDE.ipynb`.

### La corrección que esto obliga a hacer sobre AUDIT 10

La frase *«el proyecto ha agotado lo que se puede hacer con este VCF y esta máquina»* **era
falsa cuando la escribí**: quedaba todo este trabajo, y era computacional.

La formulación correcta: **los experimentos restantes de mayor información requieren datos o
evidencia de laboratorio no disponibles en este dataset.** Lo que no queda es *ciencia nueva
sobre los mismos datos*; consolidación, procedencia y visualización sí quedaban — y eran
justo lo que faltaba para que el proyecto se pudiera evaluar.
