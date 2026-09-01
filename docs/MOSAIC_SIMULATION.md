# EXP-015a · Simulación de la cancelación de BAF y del índice de dispersión

> **`DERIVED`** — simulación. **No usa ningún dato del paciente**: cómputo puro, con la
> profundidad real (44×) como único parámetro tomado del caso.
>
> Preregistro con las cuatro predicciones y la regla de decisión en `docs/DECISIONS.md`
> § EXP-015a, escrito **antes** de implementar.
>
> **Origen ejecutable:** `src/mosaic/simulate_dispersion.py` · semilla 42 · 200 repeticiones
> por celda · FPR fijada al 5 %.

## Resultado

| Escenario | Fracción celular | Potencia BAF | Potencia dispersión |
|---|---|---|---|
| Clonal | 1 % | 0,045 | 0,060 |
| Clonal | 2 % | 0,035 | 0,100 |
| Clonal | 5 % | 0,070 | 0,380 |
| Clonal | 10 % | 0,280 | 0,975 |
| Clonal | 20 % | 1,000 | 1,000 |
| **Variegado** | 1 % | 0,055 | 0,060 |
| **Variegado** | 2 % | 0,030 | 0,095 |
| **Variegado** | 5 % | **0,030** | **0,300** |
| **Variegado** | 10 % | **0,015** | **0,960** |
| **Variegado** | 20 % | **0,000** | **1,000** |

## Las cuatro predicciones, con el marcador

| # | Predicción | Resultado |
|---|---|---|
| 1 | En clonal, el BAF detecta desde fracciones bajas | **FALLADA** — solo 0,28 al 10 % |
| 2 | En variegado, el BAF **colapsa** | **CONFIRMADA**, y de forma extrema |
| 3 | En variegado, la dispersión **conserva potencia** | **CONFIRMADA** |
| 4 | La dispersión **no** supera al BAF en clonal | **FALLADA** — lo supera también ahí |

### La #2 es el resultado real, y es fuerte

En el escenario variegado la potencia del BAF **cae al 0,000 en la fracción del 20 %** — es
decir, cuanto mayor es el evento, **peor** detecta. La cancelación no es una preocupación
teórica: es un modo de fallo activo. El estadístico se vuelve *anti*-informativo.

La dispersión de cobertura, en cambio, se comporta **igual en variegado que en clonal**
(0,96 frente a 0,975 al 10 %). Eso es exactamente lo que predice el mecanismo: la cobertura
no se cancela porque no depende de qué homólogo se ganó.

### La #4 falló, y eso obliga a rebajar la conclusión

Preregistré que si la dispersión ganaba **también** en clonal sería sospechoso. Ganó.

**La explicación no favorece al índice de dispersión: mi línea base de BAF es débil.** Es una
desviación media por sitio, sin fase. **MoChA obtiene su potencia del faseo de largo alcance**,
que amplifica una asimetría minúscula a lo largo de haplotipos enteros; por eso alcanza
fracciones clonales por debajo del 1 % sobre datos reales, y mi proxy no pasa de 0,28 al 10 %.

> **Por tanto NO se puede afirmar que el índice de dispersión supere al método estándar.**
> Lo comparado no es MoChA: es un sustituto sin fase, mucho más débil. La comparación
> cara a cara **no se ha hecho**.

## Qué cambia de estado, y qué no

| Afirmación | Antes | Ahora |
|---|---|---|
| «La cancelación de BAF hace fallar a los métodos clonales en MVA» | `L1`, argumento algebraico | **Sostenida por simulación** — modo de fallo reproducido y cuantificado |
| «El índice de dispersión sobrevive a la cancelación» | `L1` | **Sostenida por simulación** |
| «El índice de dispersión es más potente que el método estándar» | `L1` | **Sigue en `L1`.** No demostrada, y esta simulación **no** la demuestra |
| «Enormemente más potente» | prohibida | **sigue prohibida** |

## Límites, declarados sin que nadie los pida

1. **La potencia simulada es optimista.** El modelo tiene ruido técnico de cobertura de
   σ = 0,02 por cromosoma y **no incluye** sesgo de GC, mapabilidad ni sesgo de alelo de
   referencia. A 44× ésos son el factor limitante real, no el ruido binomial. El rendimiento
   sobre datos reales será **peor**, no mejor.
2. **Por debajo del 5 % no hay nada.** Al 1–2 % la potencia de la dispersión es 0,06–0,10, es
   decir, azar. Si el mosaicismo de este paciente está en fracciones bajas, **ningún** método
   de los dos lo ve.
3. **No demuestra nada sobre el paciente.** Es un modelo con supuestos declarados.
4. **La rama aplicada sigue BLOQUEADA**: exige controles procesados con pipeline idéntico, y
   no existen.

## Cierre

| | |
|---|---|
| **EXP-015a · mecanismo de cancelación** | **SURVIVES** — modo de fallo reproducido y cuantificado |
| **EXP-015b · el índice como DETECTOR** | **UNVALIDATED · PARKED** — el comparador no es MoChA |
| Incertidumbre reducida | Si merecía la pena mantener el índice de dispersión. **Sí**: sobrevive donde el estándar se cancela |
| Qué desbloquea | Que el estadístico se pueda usar **si** aparecen controles. No desbloquea aplicarlo hoy |
| Qué NO se puede decir | Que sea más potente que MoChA. Ni comparado |
| Siguiente | Comparación honesta contra un método **con fase**; y controles, que es el bloqueo real |

## Nivel de evidencia

`L1` para el rendimiento relativo — sin cambios. **La novedad es que el mecanismo de
cancelación pasa de argumento algebraico a modo de fallo reproducido**, que es lo que la
compuerta pedía.
