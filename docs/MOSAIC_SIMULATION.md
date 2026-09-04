# EXP-015a · Simulación de la cancelación de BAF y del índice de dispersión

> **Corregido por EXP-015c.** La atribución causal que este documento publicó —que el desplome
> de potencia del estadístico **absoluto** se debía a la cancelación entre linajes— quedó
> **falsada por una auditoría del propio proyecto**. Lo que sobrevive, lo que cae y por qué,
> en la sección «La #2 era el resultado real». El preregistro no se ha tocado.

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

### La #2 era el resultado real, y una auditoría propia la partió en dos

> **Corrección, EXP-015c.** Lo que sigue reemplaza a la lectura original de la predicción #2.
> El preregistro de `docs/DECISIONS.md` §EXP-015a **no se reescribe**: la predicción se escribió
> antes de ver los datos y se queda como está. Lo que cambia es qué explica el resultado.

La afirmación publicada era: *en escenario variegado el estadístico de BAF pierde potencia
según crece el evento **porque las contribuciones de linajes distintos se cancelan***. Una
auditoría adversarial del propio repositorio la falsó, y el argumento es de una línea:

El estadístico que EXP-015a mide es `abs(alt/dp - 0,5)`, un **valor absoluto**. La
aleatorización de signo por sitio —que el código llamaba literalmente *«el mecanismo de
cancelación»*— **le es invisible**, porque `Binomial(dp, 0,5+d)` y `Binomial(dp, 0,5−d)` son
imágenes especulares y `|BAF−0,5|` tiene la misma distribución en las dos. La señal de alarma
estaba a la vista desde el principio y nadie la leyó: **la potencia caía a 0,000, por debajo de
alpha = 0,05**. Un mecanismo que solo puede *añadir* dispersión nunca baja del azar. El propio
preregistro había escrito *«potencia próxima al azar»*, no cero.

**EXP-015c · ablación diagnóstica POST-HOC.** Nació **después** de que la auditoría detectara
el problema, así que **no es un experimento preregistrado** y no puede leerse como una
confirmación: es una **auditoría de mecanismo**, y su resultado *apoya la interpretación
revisada*. La distinción importa porque si apareciera junto a los experimentos preregistrados
con el mismo marcador, un juez podría entender que la hipótesis estaba fijada antes de mirar
el resultado. No lo estaba. Cruzando los dos factores que estaban confundidos, con el mismo
generador, la misma semilla y el mismo nulo euploide a 44× (`src/mosaic/ablation_baf.py`):

| dirección del homólogo | profundidad | `signed` | `absdev` | `disp` | `znorm` |
|---|---|---:|---:|---:|---:|
| fija | escalada por nº de copia | **0,980** | 0,010 | 0,000 | 0,510 |
| fija | igualada al nulo | **0,975** | **0,520** | 0,435 | 0,540 |
| mezclada | escalada por nº de copia | **0,050** | 0,010 | 0,005 | 0,520 |
| mezclada | igualada al nulo | **0,040** | **0,505** | 0,565 | 0,495 |
| *control diagnóstico post-hoc* · clonal, fija, todos los sitios | escalada | 1,000 | **1,000** | 0,000 | 1,000 |
| *control diagnóstico post-hoc* · clonal, fija, todos los sitios | igualada | 1,000 | **1,000** | 0,030 | 1,000 |

Potencia con alpha = 0,05, fracción celular del 20 %, 200 repeticiones, 3 cromosomas afectados,
400 sitios cada uno. `signed` = |media por sitio de (BAF − 0,5)| · `absdev` = media de
|BAF − 0,5|, que es **el que usó EXP-015a** · `disp` = varianza por sitio del BAF, que **no es**
el índice de dispersión de *cobertura* de EXP-015b — mismo apodo, otro objeto — · `znorm` =
media de |z| con `z = (alt − dp/2)/√(dp/4)`, es decir el mismo estadístico **normalizado por la
varianza binomial esperada a la profundidad observada**.

Las cuatro primeras filas viven dentro del modelo **variegado**, donde la perturbación alcanza a
una fracción `f` de los sitios y **lo único que cambia entre celdas es el signo**. Las dos
últimas son la referencia **clonal**, donde se desplazan todos los sitios; están para que la
tabla se pueda situar y no se lean como si contradijeran el 1,000 clonal publicado. Esas dos
filas se añadieron **después** de ver la primera ablación, así que son un **control diagnóstico
post-hoc**, no parte del diseño original. Decirlo lo hace más fuerte, no más débil.

**Lo que se lee en la tabla, en tres frases.**

1. **La cancelación es real, y cae sobre el estadístico con signo.** `signed` pasa de 0,980 con
   dirección fija a 0,050 con dirección mezclada —exactamente el azar— y la profundidad no lo
   mueve (0,980 → 0,975; 0,050 → 0,040). Esto **sobrevive**, y es la predicción #2 leída
   literalmente.
2. **La atribución publicada queda falsada.** Sobre `absdev` **no hay evidencia de efecto de la
   dirección**: 0,520 y 0,505 con profundidad igualada, 0,010 y 0,010 con profundidad escalada.
   Con 200 repeticiones, 0,520 y 0,505 son el mismo resultado y no deben leerse como una
   diferencia. Lo que decide es la profundidad. El desplome por debajo de alpha aparece **con
   las dos direcciones**, así que no puede ser la cancelación.
3. **El resultado clonal no era un artefacto de profundidad.** La referencia da 1,000 con las
   dos profundidades. La pregunta obvia que sigue a este hallazgo tiene respuesta, y es que no.

**La profundidad no es un fallo de codificación.** Si hay una ganancia cromosómica real, más
copias producen más lecturas: escalar la cobertura por (2+f)/2 es lo correcto. El error fue
**comparar contra un nulo de otra profundidad un estadístico cuya varianza depende de la
profundidad**, y después adjudicar esa diferencia a la cancelación. El confundido es entre
dirección de homólogo y profundidad dependiente del número de copia.

**Lo que `znorm` sí muestra, y lo que no.** El estadístico normalizado por la profundidad
**elimina la sensibilidad a la profundidad que se observa en el estadístico de desviación
absoluta, en esta simulación**: la potencia queda en 0,49–0,54 en las cuatro celdas, con y sin
escalado de cobertura. `znorm` por sí solo no demuestra nada; lo que sostiene la lectura es **el
patrón conjunto de la ablación**, en el que cada factor mueve un estadístico distinto. Y no
demuestra que exista un detector clínicamente útil: `znorm` no se ha comparado con ningún método
con fase, no se ha aplicado a datos reales, y `EXP-015b` sigue `UNVALIDATED · PARKED`.

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
| «Las mezclas balanceadas de homólogos recentran el BAF **agregado con signo** hacia 0,5» | `L1`, argumento algebraico | **Sostenida por simulación** (EXP-015c): la potencia del estadístico con signo cae de 0,980 a 0,050 al mezclar la dirección |
| «La caída de potencia del estadístico **absoluto** se debe a la cancelación» | publicada como resultado | **FALSADA** (EXP-015c): la dirección no la mueve; la produce la profundidad dependiente del número de copia |
| «La cancelación de BAF hace fallar a **los métodos clonales** en MVA» | `L1`, argumento algebraico | **Sigue en `L1`.** Se simuló **un** estadístico, no una clase de métodos |
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
| **EXP-015a · mecanismo de cancelación** | **PARCIALMENTE FALSADA por EXP-015c.** Sobrevive: las mezclas balanceadas recentran el BAF agregado **con signo**. Falsada: la atribución de la caída del estadístico **absoluto** a la cancelación |
| **EXP-015c · ablación 2×2** | **`POST-HOC DIAGNOSTIC ABLATION` · auditoría de mecanismo, no preregistrada.** Separa dirección de homólogo y profundidad por número de copia, con el estadístico normalizado como control. El resultado **apoya la interpretación revisada**; no la confirma en el sentido preregistrado |
| **EXP-015b · el índice como DETECTOR** | **UNVALIDATED · PARKED** — el comparador no es MoChA |
| Incertidumbre reducida | Qué mecanismo explica cada señal. El estadístico **con signo** se cancela; el **absoluto** no se cancelaba, cambiaba de profundidad |
| Qué desbloquea | Que el estadístico se pueda usar **si** aparecen controles. No desbloquea aplicarlo hoy |
| Qué NO se puede decir | Que sea más potente que MoChA. Ni comparado |
| Siguiente | Comparación honesta contra un método **con fase**; y controles, que es el bloqueo real |

## Nivel de evidencia

`L1` para el rendimiento relativo — sin cambios. **La novedad es que el mecanismo de
cancelación pasa de argumento algebraico a modo de fallo reproducido**, que es lo que la
compuerta pedía.
