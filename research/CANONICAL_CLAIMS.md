# Afirmaciones canónicas — el estado ACTUAL del proyecto

> **Esta tabla manda.** Si cualquier otro documento contradice una fila de aquí, el otro
> documento está obsoleto y hay que corregirlo, no discutirlo.
>
> **Dónde vive la historia:** `docs/DECISIONS.md`. Lo que se creyó y qué lo falsó pertenece
> allí, con la corrección al lado. Aquí solo va **lo que sostenemos hoy**.
>
> **Verificación mecánica:** `python src/audit_stale_claims.py` busca formulaciones prohibidas
> en todo lo versionado y separa documentos canónicos de históricos. Debe dar **0 canónicos**.

## Clases de evidencia

| Clase | Significado |
|---|---|
| `MEASURED` | Observación directa sobre los datos del caso |
| `DERIVED` | Calculado por nosotros a partir de lo anterior |
| `EXTERNAL` | Base de datos, literatura o modelo de terceros |
| `PREDICTED` | Salida de un modelo, no una medición |
| `SIMULATED` | Modelo sin datos del paciente |

---

## Track 1 — causalidad

| id | Formulación canónica | Evidencia | Clase | Confianza | Sustituye a | Formulación PROHIBIDA |
|---|---|---|---|---|---|---|
| **C1** | `BUB1B` es #1 en **14 de los 15** análisis del modo B. En el control genético puro `A0`, congelado, queda **#4**; en la sensibilidad `A0-FREQFIX` vuelve a **#1** | notebook 03 · EXP-006 | `DERIVED` | alta | «#1 en los 15 análisis» | «`BUB1B` siempre fue #1»; borrar el #4 |
| **C2** | Los tres genes que superan a `BUB1B` en `A0` son **polimorfismos comunes** (30–93 % de frecuencia, hasta 313 150 homocigotos) cuya frecuencia VEP no supo anotar | EXP-021 · base local de Exomiser | `EXTERNAL` | alta | «tres competidores no explicados» | «artefactos de llamada» — las llamadas son correctas |
| **C3** | `A0-FREQFIX` **no es una línea independiente**: reparó frecuencias con la base local de Exomiser, así que comparte fuente con el baseline | EXP-021b | `DERIVED` | alta | — | contar `A0-FREQFIX` y Exomiser como dos convergencias |
| **C4** | Un alelo truncante, **Likely Pathogenic** (`PVS1` + `PM2_Supporting` = 9 pts). PTC a ~750 nt de la última unión, NMD predicho con margen ~14× | EXP-007 | `DERIVED` | alta | — | «patogénico confirmado» |
| **C5** | Un alelo missense raro, **VUS**. `PP3` no aplica (REVEL 0,472, bajo el umbral preregistrado). `PM1`, `PS1`, `PM5` no aplican. `PM3` bloqueado por decisión | EXP-007 | `DERIVED` | alta | «missense probablemente patogénica» | reabrir `PP3` con conservación o estructura |
| **C6** | **La fase NO está resuelta.** Los dos alelos son *candidatos* a heterocigosis compuesta. Bloques `PGT`/`PID` de máximo 288 pb frente a un hueco de ~11 kb | EXP-013 | `MEASURED` | alta | «heterocigosis compuesta» | «en *trans*»; «compuesto confirmado» |
| **C7** | Sin evidencia de deleción heterocigota grande abarcando `BUB1B` desde profundidad y heterocigosidad del VCF. **CNV pequeñas, SV equilibradas e inserciones siguen sin resolver** | EXP-012 | `MEASURED` | media | «CNV grande descartada» | cerrar un negativo estructural con L001 |
| **C8** | No se encontró segundo alelo SNV/indel en 270 kb; AlphaGenome dio Δ plano. **Negativo del alcance evaluado**, no del espacio de hipótesis | EXP-008/009 | `PREDICTED` | media | — | «AlphaGenome demostró que no existe un segundo alelo» |

## Track 1 — mecanismo del alelo missense

| id | Formulación canónica | Evidencia | Clase | Confianza | Sustituye a | Formulación PROHIBIDA |
|---|---|---|---|---|---|---|
| **C9** | El residuo está **enterrado** (RSA 16,2 %) en región de alta confianza del modelo (pLDDT 91,1), con tres puentes de H al esqueleto | EXP-010 | `PREDICTED` | media | — | usar pLDDT como proxy de efecto de variante |
| **C10** | El argumento estérico y el de carga enterrada están **debilitados** por el análisis geométrico. Lo que queda en pie es la **pérdida rotámero-independiente de un puente aceptor** | EXP-010 | `PREDICTED` | media | «predicción: desestabilizante» | «desestabilizante» sin cualificar |
| **C11** | La posición está en el **percentil 93** de conservación de su propia proteína (cobertura comparable); la capacidad aceptora se conserva en **119 de 120** ortólogos alineados; la clase catiónica entrante aparece en **0** | EXP-011 | `EXTERNAL` | alta | — | usar esto para reabrir `PP3` |
| **C12** | Fuera de mamíferos: 30 alineados en 4 clados. **Pero en peces solo alinean 4 de 33** y en basales ninguno. Las observaciones independientes son del orden de **5–6 a nivel de clado**, no 120 | EXP-011 | `EXTERNAL` | alta | «conservado en todos los vertebrados» | tratar 120 ortólogos como 120 evidencias |
| **C13** | El bolsillo es **hidrofóbico conservado**, pero de los cuatro aromáticos uno **no** está conservado ni en identidad ni en clase | EXP-011 | `EXTERNAL` | alta | «jaula de cuatro aromáticos» | — |
| **C14** | La discrepancia entre REVEL y la estructura **sigue sin explicar**. La explicación que el proyecto había escrito quedó falsada por la conservación | EXP-011 | `DERIVED` | alta | «un residuo crítico puede no estar conservado» | presentarla como resuelta |

## Fenotipo residual

| id | Formulación canónica | Evidencia | Clase | Confianza | Sustituye a | Formulación PROHIBIDA |
|---|---|---|---|---|---|---|
| **C15** | Barrido codificante del panel renal: **0 alelos raros** en 28 genes al umbral del propio panel; **0 variantes de `MAGED2`** | EXP-017 | `MEASURED` | alta | — | «se descartó una tubulopatía» — solo el barrido codificante |
| **C16** | **Nefrocalcinosis es el único rasgo residual en los dos sentidos**: no anotado en el modelo MVA1 **y** no respaldado por la literatura de MVA1 | EXP-019c | `EXTERNAL` | alta | «cuatro rasgos residuales» | — |
| **C17** | Crecimiento y fallo de medro **NO son residuales**: el bajo soporte semántico era **hueco de anotación**; la literatura los cubre al 93,5 % | EXP-019a | `EXTERNAL` | alta | «MVA no explica el fallo de medro» | convertir incompletitud de una base de datos en biología |
| **C18** | Atrofia muscular y prematuridad: **no anotadas y no cuantificadas**. No se puede decidir | EXP-018 · EXP-019b | `EXTERNAL` | — | — | contarlas como residuales |

## Ramas ortogonales

| id | Formulación canónica | Evidencia | Clase | Confianza | Sustituye a | Formulación PROHIBIDA |
|---|---|---|---|---|---|---|
| **C19** | La **cancelación de BAF** es un modo de fallo real y reproducido: en escenario variegado la potencia del estadístico de BAF cae a **0,000 al 20 %** de fracción celular | EXP-015a | `SIMULATED` | alta | — | extrapolarlo al paciente |
| **C20** | El índice de dispersión **sobrevive a la cancelación**, pero su superioridad **no está demostrada**: el comparador usado no reproduce el faseo de largo alcance de MoChA | EXP-015b | `SIMULATED` | baja | «enormemente más potente» | «supera a MoChA» |
| **C21** | MitoRead es **prototipo**: *naive mtDNA-equivalent estimate ≈259 bajo los supuestos del piloto*. NUMT no excluidos, un carril, sin controles ni hemograma | EXP-014a | `DERIVED` | — | «mtDNA-CN del paciente = 259» | presentarlo como medida del paciente |
| **C22** | Exomiser sitúa `BUB1B` **#2 de 398** con modelo AR. Es **convergencia metodológica sobre el mismo VCF**, no evidencia biológica independiente | EXP-006b | `EXTERNAL` | alta | «comprobación independiente» | contarlo como observación biológica separada |

## Track 2

| id | Formulación canónica | Evidencia | Clase | Confianza | Sustituye a | Formulación PROHIBIDA |
|---|---|---|---|---|---|---|
| **C23** | **NO hay fármaco nominado.** La compuerta exige cinco condiciones y ninguna candidata las reúne | EXP-016 | — | — | «Arimoclomol. La nominación…» | nominar antes de cerrar los puentes 7 y 8 |
| **C24** | La modulación de proteostasis y chaperonas es la **clase superviviente principal entre las seis evaluadas** | EXP-016 | `EXTERNAL` | media | «la única que sobrevive» | implicar barrido exhaustivo del espacio terapéutico |
| **C25** | **T2-A (aguas arriba) y T2-B (aguas abajo) son rutas distintas** con consecuencias oncológicas potencialmente opuestas. No se agrupan bajo «proteostasis» | EXP-016 | `DERIVED` | alta | agrupación única | usar evidencia de una para respaldar la otra |
| **C26** | **Puente 3 `UNRESOLVED`:** que inhibir HSP90 hunda al mutante demuestra dependencia basal, **no** que aumentar chaperonas lo suba | EXP-016 | `EXTERNAL` | alta | — | inferir la dirección inversa |
| **C27** | **Puente 7 `UNRESOLVED`:** cero evidencia DIRECT. Contraevidencia en otro sistema humano (E18) y **tensión mecanística** (E19): el deterioro de HSF1 hace la vía **relevante Y la farmacología incierta** | EXP-016b | `EXTERNAL` | alta | «prior mecanístico en contra» | `NEGATIVE`; «el coinductor fallará» |
| **C28** | **Puente 8 `NO DIRECT SAFETY DATA`:** nadie ha medido el efecto de ninguna de estas intervenciones sobre CIN o supervivencia clonogénica | EXP-016 | — | — | — | presentar rescate como beneficio neto |
| **C29** | Ni siquiera el rescate **genético** es universal: dependió del cariotipo, y una línea aneuploide no respondió igual | E1 | `EXTERNAL` | media | «subir HSP rescata la aneuploidía» | generalizar el rescate genético |

## Datos disponibles — realidad, no supuesto

| id | Formulación canónica |
|---|---|
| **C30** | El VCF procede de los **cuatro carriles**. En disco solo está **L001** (~13×). Cualquier afirmación de profundidad efectiva ~43× describe un carril, no el dataset del VCF |
| **C31** | **No existen**: genotipos parentales · BAM/CRAM de profundidad completa · RNA-seq · single-cell · proteómica · tejido tumoral · cariotipo previo · hemograma contemporáneo |
| **C32** | Todo módulo que asuma esos datos está **obsoleto o es solo simulación** |
