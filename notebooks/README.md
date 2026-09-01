# Los notebooks — la investigación, ejecutable y visible

> **Ocho notebooks, ejecutados, con 29 figuras embebidas.** No son un registro de que algo
> ocurrió: son la investigación, y se leen de arriba abajo sin salir de ellos.
>
> El README anterior describía una arquitectura de quince notebooks que presuponía RNA-seq,
> single-cell, series longitudinales y cariotipo celular. **Ninguno de esos datos existe.** Se
> conserva en `docs/history/notebooks_README_SUPERSEDED.md`.

## La regla que se aplica en todos

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

`pregunta biológica → hipótesis y preregistro → entradas y procedencia → QC → método →
resultado primario → visualización → robustez → explicaciones alternativas → evidencia
contradictoria → qué NO demuestra → decisión → siguiente experimento`

Y un mínimo de **tres figuras**: QC, resultado principal, e incertidumbre o robustez.

## Los ocho

| # | Notebook | Pregunta | Figuras |
|---|---|---|---|
| **00** | `DATA_REALITY` | ¿Qué se puede y qué no responder con los datos que hay? | 3 |
| **01** | `TRACK1_GENOME_WIDE` | ¿Qué gen explica el caso cuando compite todo el genoma? | **6** |
| **02** | `BUB1B_ALLELE_CURATION` | ¿Qué sostiene cada alelo, y qué haría falta para que el par sea causal? | 4 |
| **03** | `BUBR1_MECHANISM` | El missense no se mueve por clasificación: ¿se mueve por mecanismo? | 4 |
| **04** | `HIDDEN_SECOND_ALLELE` | ¿Hay un segundo alelo que el pipeline codificante no ve? | 3 |
| **05** | `RESIDUAL_PHENOTYPE` | ¿Qué rasgos no explica MVA, y alguno exige un segundo diagnóstico? | 3 |
| **06** | `MOSAIC_AND_MITOREAD` | ¿Qué le pasa a la señal cuando se rompe la clonalidad? | 3 |
| **07** | `TRACK2_SAFE_RESCUE` | ¿Hay un mecanismo terapéutico plausible, falsable y seguro? | 3 |

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
