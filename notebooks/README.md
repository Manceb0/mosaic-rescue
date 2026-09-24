# Los notebooks: la investigación, ejecutable y visible

> **Ocho notebooks con 30 figuras en sus salidas ejecutadas, 25 de ellas científicas.** No son un
> registro de que algo ocurrió: son la investigación, y se leen de arriba abajo sin salir de
> ellos.
>
> Las figuras de publicación viven en `figures/pub/` (SVG vectorial + PNG 300 dpi) y se
> regeneran con `python src/figures/render_all.py`. El objeto científico principal de cada
> notebook, con su origen y su librería, está en
> [`VISUAL_SCIENCE_PASS.md`](VISUAL_SCIENCE_PASS.md).
>
> El README anterior describía una arquitectura de quince notebooks que presuponía RNA-seq,
> single-cell, series longitudinales y cariotipo celular. **Ninguno de esos datos existe.** Se
> conserva en `docs/history/notebooks_README_SUPERSEDED.md`.

## La regla que se aplica en todos

La integración de septiembre añade **10 imágenes adjuntas autocontenidas**: nueve
paneles narrativos/de síntesis y el gráfico cromosómico RD/BAF congelado de GO 2B.
Están dentro del archivo, visibles sin acceder al disco del autor. No se contabilizan
como nuevas salidas de ejecución. Se regeneran con `python src/nb/story_integration.py`
y también se incluyen al reconstruir los notebooks. Las celdas originales conservan
su fecha y alcance; la introducción visual distingue el estado posterior.

**Generar una figura y escribirla en `figures/` NO basta.** Aparece INLINE, en la misma celda o
la siguiente, con un caption que declara cuatro cosas:

```
experimento · clase de evidencia · qué enseña · QUÉ NO DEMUESTRA
```

La última es la que más cuesta escribir y la que más vale.

**Clases de evidencia:** `MEASURED` (observación directa sobre el caso) · `DERIVED` (calculado
por nosotros) · `EXTERNAL` (base de datos o literatura) · `PREDICTED` (salida de un modelo) ·
`SIMULATED` (modelo sin datos del paciente).

## Estructura obligatoria

Pregunta biológica, hipótesis y preregistro, entradas con su procedencia, QC, método y
resultado primario. Después: visualización, robustez, explicaciones alternativas,
evidencia contradictoria, el límite de lo que se demuestra, la decisión y el siguiente
experimento.

### El mínimo, y por qué cambió

**Antes:** «un mínimo de tres figuras». Ese requisito produjo **relleno**, cajas, flechas y
estados dibujados con Matplotlib para llegar al número.

**Ahora:** cada notebook mayor necesita **al menos una figura CIENTÍFICA**, y toda figura
declara su clase:

| Clase | Qué es | ¿Puede ser la principal? |
|---|---|---|
| `DATA` | objeto o distribución calculada desde datos del caso | **Sí** |
| `MODEL_OUTPUT` | salida de un modelo (AlphaFold, AlphaGenome, Exomiser) | **Sí** |
| `SIMULATION` | distribución generada por simulación, sin datos del paciente | **Sí** |
| `CURATED_EVIDENCE` | tabla de evidencia versionada, con fuente por celda | **Sí** |
| `SYNTHESIS` | integra resultados ya obtenidos; no expone el dato crudo | No |
| `NARRATIVE` | explica una conclusión; no contiene dato | No |

`SYNTHESIS` y `NARRATIVE` siguen siendo legítimas y útiles. Lo que ya no pueden es **contar
para el mínimo**. La clase va en el pie **y estampada en la propia imagen**, para que la
etiqueta viaje con la figura si alguien la recorta y la pega en una diapositiva.

La prueba que decide: *si le quito el título, el pie y la conclusión, ¿un experto reconoce qué
objeto científico está mirando?* Si ve un transcrito, una distribución, una estructura, un
alineamiento, BAF, un heatmap o cobertura, la respuesta es sí. Si ve «SURVIVES», cajas verdes y flechas, es que no.

## Los ocho

| # | Notebook | Pregunta | Objeto científico principal | fig · cient. |
|---|---|---|---|---|
| **00** | `DATA_REALITY` | ¿Qué se puede y qué no responder con los datos que hay? | QC de FASTQ por ciclo, calculado sobre L001 | 1 · 1 |
| **01** | `TRACK1_GENOME_WIDE` | ¿Qué gen explica el caso cuando compite todo el genoma? | Manhattan de priorización sobre `A0` congelado | **7 · 7** |
| **02** | `BUB1B_ALLELE_CURATION` | ¿Qué sostiene cada alelo, y qué haría falta para que el par sea causal? | Navegador del gen: exones, dominios y 1 497 missense de ClinVar | 4 · 3 |
| **03** | `BUBR1_MECHANISM` | El missense no se mueve por clasificación: ¿se mueve por mecanismo? | Bolsillo de AlphaFold con distancias reales + logo de conservación | 3 · 3 |
| **04** | `HIDDEN_SECOND_ALLELE` | ¿Hay un segundo alelo que el pipeline codificante no ve? | Pistas REF/ALT/Δ, ISM y contactos de AlphaGenome, como predicciones | 6 · 6 |
| **05** | `RESIDUAL_PHENOTYPE` | ¿Qué rasgos no explica MVA, y alguno exige un segundo diagnóstico? | Matriz término HPO × modelo de enfermedad, en bits de Resnik | 3 · 2 |
| **06** | `MOSAIC_AND_MITOREAD` | ¿Qué le pasa a la señal cuando se rompe la clonalidad? | Distribuciones de BAF simuladas + curva de potencia | 3 · 1 |
| **07** | `TRACK2_SAFE_RESCUE` | ¿Hay un mecanismo terapéutico plausible, falsable y seguro? | Matriz 8 puentes × 10 dimensiones de evidencia curada, más la cartera experimental de tres brazos | 3 · 2 |

## Cómo reconstruirlos

```bash
python src/nb/build_all.py
```

Reconstruye y ejecuta los ocho, y emite la matriz de verificación. **Los notebooks se generan
desde `src/nb/`**: la fuente de verdad vive en `src/`, y generarlos garantiza que ejecutan las
mismas funciones del pipeline en vez de una copia que puede divergir.

## Definición de HECHO

Un notebook **no** está terminado porque corra sin errores. Lo está cuando:

1. ejecuta de arriba abajo · 2. usa las entradas correctas con su hash · 3. **muestra** sus
resultados, no solo los escribe · 4. tiene QC + principal + robustez · 5. interpreta cada
figura · 6. presenta la evidencia contradictoria · 7. dice qué NO demuestra · 8. termina en una
decisión · 9. nombra el siguiente experimento · 10. está saneado · 11. no contiene afirmaciones
obsoletas · 12. cualquier figura puede regenerarse.

`src/nb/build_all.py` comprueba 1, 3, 4 y 10 mecánicamente. El resto se audita con
`src/audit_stale_claims.py`, que trata `notebooks/` como documentación **canónica**.

## Saneado

Los notebooks se commitean **con sus salidas**, así que las salidas también se sanean: solo
agregados, conteos y símbolos de gen. Nunca coordenadas, genotipos, identidad de variantes,
rutas locales ni identificadores de muestra.

Los notebooks 00 y 01 ejecutan el escáner al final, sobre sí mismos.
