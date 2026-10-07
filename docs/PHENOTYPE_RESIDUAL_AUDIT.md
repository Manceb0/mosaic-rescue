# EXP-018 / EXP-019 · ¿Fenotipo residual, o hueco de anotación?

> **`DERIVED`** sobre corpus HPO local + **`EXTERNAL`** (compilación publicada de 31 casos etiquetados como MVA1,
> `Neurol Sci` 2022, DOI 10.1007/s10072-022-06247-w, ya verificada en el brief §11).
>
> **Nota de auditoría sobre el denominador (verificada en PubMed, texto completo, 2026-10-07; Pavone et al.
> 2022, PMID 35804254, PMC9616775).** *The paper describes 31 cases including the current report; one prose
> sentence refers to a group of 30, while the reported totals and percentages correspond to n=31* (29/31 =
> 93,5 %, 12/31 = 38,7 %, 4/31 = 12,9 %). El cuerpo y los métodos hablan de 30 casos de la literatura más el
> caso índice. Usamos n = 31. Ese caso índice porta una sola VUS heterocigota de `BUB1B`, también presente en
> su padre no afectado: la serie no es exclusivamente bialélica confirmada, lo que no cambia ningún veredicto
> de esta tabla.

## La trampa que este experimento existe para evitar

El modo B midió que varios rasgos del paciente **aportan poco soporte semántico** al modelo
MVA anotado. La lectura tentadora, y equivocada, sería: *MVA no explica esos rasgos, luego hay
un segundo diagnóstico*.

**El brief advierte exactamente de esto:** el retraso de crecimiento aparece en el **93,5 %**
de los casos de MVA1. No es un fenotipo residual misterioso. Si el score semántico dijera lo
contrario, el problema estaría en la anotación, no en la biología.

Así que la pregunta correcta no es *¿aporta poco soporte?* sino **¿está el término anotado en
el modelo de enfermedad?**

## Medición

El modelo `OMIM:257300` (MVA1, gen `BUB1B`) tiene **59 términos anotados** en el corpus HPO.
De los 7 términos del probando:

| HPO | Rasgo | ¿Anotado en el modelo MVA1? | ¿Respaldado por la literatura de MVA1? |
|---|---|---|---|
| HP:0002859 | Rabdomiosarcoma | **SÍ** | Sí, malignidad 38,7 %, RMS entre los típicos |
| HP:0004322 | Talla baja | **SÍ** | Sí, retraso de crecimiento 93,5 % |
| HP:0001518 | Pequeño para edad gestacional | **SÍ** | Sí, retraso pre/postnatal 93,5 % |
| HP:0001508 | Fallo de medro | **NO** | **Sí**: es un fenotipo de crecimiento, 93,5 % |
| HP:0001622 | Parto prematuro | **NO** | Plausible por el eje perinatal; **no cuantificado** en la serie |
| HP:0003202 | Atrofia muscular esquelética | **NO** | **No cuantificado** en la serie de 31 casos |
| HP:0000121 | Nefrocalcinosis | **NO** | **NO**: la serie reporta «disfunción renal» genérica al 12,9 %, **no nefrocalcinosis** |

## Las tres categorías, que no son la misma cosa

### 1. Hueco de anotación, no residual: `HP:0001508`

**Fallo de medro no está anotado en el modelo, pero el retraso de crecimiento está descrito en
el 93,5 % de los casos de MVA1.** Su bajo soporte semántico es un artefacto del corpus HPO, no
una señal de que MVA no lo explique.

> **EXP-018/019 corrigen aquí una lectura del modo B.** El soporte semántico bajo de este rasgo
> **no es evidencia de diagnóstico mixto**. Presentarlo como tal habría sido convertir
> incompletitud de una base de datos en biología.

### 2. Sin cuantificar: `HP:0003202`, `HP:0001622`

Atrofia muscular esquelética y parto prematuro **no están anotados y tampoco están
cuantificados** en la serie de 31 casos. No se puede afirmar ni que MVA los explique ni que no.

**Quedan `PARKED`, no `NEGATIVE`.** La ausencia de un número en una serie de 31 casos no es
evidencia de ausencia del rasgo.

### 3. Residual de verdad: `HP:0000121`

**Nefrocalcinosis no está anotada en el modelo Y tampoco está respaldada por la literatura de
MVA1.** La serie reporta disfunción renal genérica al 12,9 %; nefrocalcinosis es otra cosa.

**Es el único de los siete rasgos que es residual en los dos sentidos a la vez.** Y es
precisamente el que el brief ya había señalado como el rasgo anómalo, y el que `EXP-017` no
pudo explicar con un barrido codificante del panel renal.

## Un matiz metodológico que hay que declarar

La contribución *leave-one-out* de un término **no** es su soporte absoluto. Con Best Match
Average, quitar un término que puntúa por debajo de la media **sube** el promedio, así que
puede dar contribución negativa aunque el término **sí** esté anotado. `HP:0004322` es el caso:
está anotado y aun así su LOO salió negativo.

**Por eso este experimento no se hizo con las contribuciones LOO, sino comprobando la
pertenencia al conjunto anotado.** Es la medida que responde la pregunta.

## Cierre

| Rama | Estado | Qué reduce |
|---|---|---|
| **EXP-018 · atrofia muscular** | **PARKED** | Ni hueco de anotación demostrable ni residual demostrable: falta el dato en la literatura |
| **EXP-019 · crecimiento y perinatales** | **CERRADO · NEGATIVE como residual** | El bajo soporte de fallo de medro es **hueco de anotación**; la literatura lo cubre al 93,5 % |
| **Nefrocalcinosis** | **RESIDUAL EN ESTE AUDIT · AMBAS COMPROBACIONES NEGATIVAS** | Único rasgo sin anotación **y** sin respaldo en la compilación de MVA1. No demuestra que la nefrocalcinosis sea incompatible con MVA1: la compilación reporta disfunción renal genérica (12,9 %) |

**Consecuencia para el proyecto:** el argumento de diagnóstico mixto **se estrecha a un solo
rasgo**, en vez de apoyarse en cuatro. Es más débil en número y **mucho más fuerte en calidad**,
porque ese rasgo sí resiste las dos comprobaciones.

Y la pregunta que lo decide sigue siendo la misma, y sigue sin contestar:
**¿hubo polihidramnios u oligohidramnios?**

## Nivel de evidencia

`L2`: pertenencia al corpus HPO (medición directa) contrastada con frecuencias publicadas en
una serie de casos (`L2`, series pequeñas con sesgo de publicación).
