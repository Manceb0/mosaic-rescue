# Camino crítico científico

> **La reproducibilidad es infraestructura, no el producto.** Este documento existe porque
> el proyecto derivó: se convirtió EXP-006 y su andamiaje en el proyecto entero mientras
> ramas centrales quedaban flotando.
>
> **Regla de parada.** Toda rama abierta termina etiquetada `SURVIVES`, `NEGATIVE`,
> `BLOCKED` o `PARKED`. **Ninguna desaparece por haber aparecido una tarea nueva.**

## Qué es este proyecto, en una frase

Resolver el mecanismo causal del caso lo mejor posible, demostrarlo con **varias líneas de
evidencia independientes**, y convertir ese mecanismo en una **hipótesis terapéutica
aprobada, falsable y segura**.

El ranking, los tests y los notebooks existen para que esa historia sea defendible. **No son
la historia.**

## Filtro para cualquier tarea nueva

> ¿Qué incertidumbre científica del caso reduce, y qué decisión desbloquea?

Si no responde a las dos, va al *backlog* de ingeniería, no al camino crítico.

---

## Tabla viva

| # | Pregunta | Por qué importa | Evidencia actual | Estado | Bloqueo | Siguiente experimento | Impacto |
|---|---|---|---|---|---|---|---|
| 1 | ¿Qué gen explica el caso cuando compite todo el genoma codificante? | Sin esto, elegir `BUB1B` es sesgo de confirmación | **#1 en los 15 análisis**, incluido A0 sin fenotipo ni ClinVar. Modelo causal: OMIM:257300, compatible con herencia | **SURVIVES** | — | baseline externo, y cerrar | T1 |
| 2 | ¿Los dos alelos de `BUB1B` están en *trans*? | Sin *trans* no hay modelo bialélico | Sin `PGT`/`PID`; hueco 13,8× la longitud de fragmento | **BLOCKED** | genotipos parentales o lectura larga dirigida | pedirlos | T1 · **el de mayor valor** |
| 3 | ¿Hay un segundo alelo SNV/indel oculto en el locus? | El truncante necesita pareja | 270 kb, 1 candidato, AlphaGenome Δ plano | **NEGATIVE** | — | cerrado dentro del alcance evaluado | T1 |
| 4 | ¿El segundo hit es estructural? | Es la clase que el VCF no ve | CNV grande sin evidencia desde profundidad y heterocigosidad | **BLOCKED** | BAM/CRAM de profundidad completa | pedirlo | T1 |
| 5 | ¿Compite algún gen que no habíamos mirado? | Protege del sesgo de panel | `LZTR1` #2, `IGBP1` #3 | **EN CURSO** | — | auditar qué modelo de enfermedad sostiene cada uno | T1 |
| 6 | ¿La nefrocalcinosis congénita exige un segundo diagnóstico? | No desaparece porque `BUB1B` gane | Primeros HIGH renales comunes. **Y el modo B añade señal: la nefrocalcinosis aporta poco soporte semántico al modelo MVA anotado** | **ABIERTA · prioridad subida** | — | EXP-017 | T1 |
| 6b | ¿La atrofia muscular está cubierta por el modelo MVA? | Mismo patrón que la renal | Contribución semántica baja en el corpus HPO actual | **ABIERTA** | — | EXP-018 | T1 |
| 6c | ¿La literatura de MVA respalda los rasgos de crecimiento y perinatales más allá de la anotación HPO? | Las bases HPO son incompletas; ausencia de anotación ≠ ausencia de asociación | Contribución semántica baja | **ABIERTA** | — | EXP-019 | T1 |
| 7 | ¿Cuál es el mecanismo, no solo el gen? | Encontrar el gen no es encontrar el mecanismo | Truncante → NMD predicho; missense → hipótesis estructural | **PARCIAL** | — | conservación ortóloga; notebook estructural | **T1→T2** |
| 8 | ¿El WGS conserva firma de mosaicismo? | Pieza central de originalidad | Nada ejecutado | **PARKED** | controles comparables | mCA/BAF/profundidad estándar primero | T1 |
| 9 | ¿Hay señal mitocondrial ortogonal? | Lectura independiente del mismo WGS | Nada ejecutado | **PARKED** | controles y profundidad comparables | mtDNA-CN con controles | T1 |
| 10 | ¿Qué hipótesis terapéutica sobrevive? | **Es el diferencial del proyecto** | Nada | **GATED** | umbral de mecanismo | búsqueda bibliográfica ya permitida | **T2** |

---

## Lo que no puede volver a perderse

**MitoRead** sigue vivo como *orthogonal WGS-derived mitochondrial readout* — nunca «ensayo
funcional». Con las advertencias de composición celular y controles.

**Mosaic fingerprint** sigue vivo. Línea base estándar de mCA/BAF/profundidad **primero**;
el índice de dispersión experimental **después**, y solo si gana una simulación. Nunca
afirmar reconstrucción de cariotipos desde WGS bulk.

**Fenotipo residual** no se cierra porque los primeros HIGH renales fueran comunes. Se
cierra con evidencia.

**Track 2 está `GATED`, no olvidado.** La búsqueda bibliográfica sobre dosis de BUBR1,
proteostasis y segregación cromosómica **ya está permitida**. Lo prohibido es **elegir el
candidato terapéutico final** antes de establecer suficientemente el mecanismo.

---

## Peticiones externas — bloqueos activos

Estas no desaparecen del registro porque no contesten.

| Petición | Bloquea | Estado |
|---|---|---|
| **BAM/CRAM** de los 4 carriles, con índice, *read groups* preservados y la referencia exacta | #4 SV/CNV, #8 mosaicismo, #9 MitoRead | pendiente |
| **Genotipos o muestras parentales** | #2 fase — el de mayor valor del proyecto | pendiente |
| Tipo de preparación de librería (`DNA Prep` o `DNA PCR-Free`) | peso de #8 | pendiente |
| Hemograma contemporáneo a la extracción | confusor de #9 | pendiente |
| ¿Polihidramnios u oligohidramnios? | pondera #6 | pendiente |

**Solo `L001` está en disco (~13×).** El VCF vino de los cuatro carriles. Prohibido cerrar
un negativo estructural con un carril.

---

## Dónde está el diferencial

`BUB1B` #1 es **Track 1 bien hecho**. No es lo que distingue al proyecto.

El diferencial está en lo que viene después:

```
variante causal
      ↓
MECANISMO
      ↓
señales ortogonales del MISMO WGS   ← mosaicismo · MitoRead
      ↓
hipótesis terapéutica
      ↓
intento sistemático de destruirla
      ↓
experimento que más información aporta
```

Eso es lo que no se puede volver a perder de vista.
