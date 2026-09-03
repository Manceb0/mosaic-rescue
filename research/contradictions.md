# Registro de contradicciones

Evidencia que **debilita, complica o falsa** nuestras ideas preferidas.

## Por qué existe

Una hipótesis que sobrevive a la contradicción vale más que una sostenida solo con
literatura escogida a favor. Este fichero estuvo vacío durante casi todo el proyecto, con una
única fila plantilla `C001`, mientras `README.md` y `AGENTS.md` afirmaban que aquí vivía la
evidencia en contra. Eso convertía el sistema de evidencia en decoración. Las filas de abajo
son las contradicciones realmente aceptadas, cada una con su origen.

**Regla de admisión.** Una fila entra aquí solo si tiene identificador verificado o documento
del repositorio que la sostenga. Ninguna se ha suavizado para que encaje mejor con la
hipótesis principal. `CLAUDE.md` Regla Dura 5 y Regla Dura 6.

| ID | Hipótesis atacada | Evidencia contradictoria | Fuente | Gravedad | Decisión |
|---|---|---|---|---|---|
| **C002** | «`BUB1B` ganó la búsqueda genome-wide» | En el `A0` **congelado y preregistrado**, `BUB1B` sale **#4**, no #1. Solo vuelve al #1 en la sensibilidad `A0-FREQFIX`, hecha **después** de ver el resultado | `src/prioritization/freqfix_sensitivity.py` · EXP-021b | **alta** | **Se conserva la contradicción.** Los dos números se reportan siempre juntos. Prohibido narrar «siempre fue #1» (`CLAUDE.md`) |
| **C003** | «La missense cae en un dominio caliente, luego `PM1` aplica» | 1 497 missense de ClinVar repartidas por el gen, 98 % VUS y una sola P/LP: **no hay hotspot demostrable en ningún punto de `BUB1B`** | `docs/ACMG_CURATION.md` §`PM1` · figura `fig02_gene_browser` | media | **`PM1` NO se aplica.** El criterio se retiró con el dato delante, no por intuición |
| **C004** | «Los dos alelos están establecidos en *trans*» | La fase no está resuelta y no hay muestras parentales. `PM3` queda bloqueado | EXP-013 **BLOCKED** · `docs/ACMG_CURATION.md` | **alta** | La missense se queda en **VUS**. No se promociona por conveniencia |
| **C005** | «Subir chaperonas sube BUBR1» (puente 3, ruta T2-A) | Inhibir HSP90 **desploma** mutantes missense de BUBR1: eso demuestra **dependencia basal**, la misma dirección de dependencia, y **no** que añadir soporte suba la abundancia. Falta la dirección de **ganancia**, que nadie ha medido | PMID 20516114 | media | Puente 3 **SIN RESOLVER**, no contradicho: las dos celdas pasan de `CONTRADICTORY` a `NEAR`. Era un error lógico nuestro, y como la corrección **nos favorece**, se declara en la cabecera del propio TSV |
| **C006** | «El rescate genético por proteostasis se traduce farmacológicamente» (puente 7, ruta T2-B) | En fibroblastos NPC1 I1061T la sobreexpresión de HSP70 **sí** redujo el almacenamiento de colesterol, pero **arimoclomol no lo reprodujo hasta 500 µM** durante 72–120 h, y por sí solo no subió HSP70 en esas células | PMID 34481829 · DOI 10.1016/j.jlr.2021.100114 | **alta** | Puente 7 es el **hueco traduccional** declarado. Arimoclomol pasa a **centinela de falsación**, no a candidato principal |
| **C007** | «Si arimoclomol falla, cae toda la biología de chaperonas» | En **ese mismo trabajo**, inhibir HSP90 **sí** funcionó, subiendo HSP70. El fallo de un compuesto no cierra la vía | PMID 34481829 · DOI 10.1016/j.jlr.2021.100114 | media | **Corrige una sobreafirmación nuestra.** Un negativo de arimoclomol mata la traducción *arimoclomol → coinducción HSP*, no el brazo de chaperonas |
| **C008** | «El rescate aguas abajo de la aneuploidía basta» | Rapamicina a 40 µM en larvas de un modelo CIN/MVA en *Drosophila* rescató el **número de neuroblastos aneuploides**, pero **no** restauró adecuadamente las células Pros+ **ni el tamaño cerebral**: recupera el compartimento de células madre sin recuperar el resultado tisular | DOI 10.1038/s41467-026-70521-0 | **alta** | Sostiene el **Safe Rescue Corridor**: ya hay señal de que el corredor importa. Sirolimus se mantiene como comparador **adversarial** |
| **C009** | «El control positivo genético funciona siempre» | El rescate por `ca-HSF1` **dependió del cariotipo**: una línea aneuploide no respondió igual | DOI 10.1038/s41467-025-60857-4 | media | Se declara en `research/track2_candidates.tsv`. Un negativo del control positivo no es interpretable sin esta advertencia |
| **C010** | «Nuestro detector de mosaicismo supera a MoChA» | La línea base usada es un estadístico **BAF site-wise sin fase**. **No es MoChA** y no reproduce su ventaja de fase de largo alcance. La superioridad **no está demostrada** | EXP-015b `UNVALIDATED · PARKED` · `research/SCIENTIFIC_CRITICAL_PATH.md` | **alta** | La afirmación de superioridad se retiró. La simulación se reporta como **modo de fallo del BAF**, no como victoria de nuestro índice |
| **C011** | «MVA1 explica el fenotipo completo» | La **nefrocalcinosis** no tiene anotación HPO en MVA1 **ni** respaldo en la serie de literatura, que reporta «disfunción renal» genérica al 12,9 %, que es otra cosa | EXP-019c `UNRESOLVED` · `docs/PHENOTYPE_RESIDUAL_AUDIT.md` | media | Se mantiene abierta la posibilidad de **diagnóstico mixto**. No se cierra el rasgo por comodidad narrativa |
| **C012** | «Arimoclomol es seguro para este paciente» | La etiqueta declara pérdida de peso entre las reacciones más frecuentes y aumentos de creatinina sérica del 10–20 %. Inhibe OCT2, cuyo sustrato endógeno es la creatinina. **Ambas colisionan con el fenotipo**: fallo de medro y nefrocalcinosis | Etiqueta MIPLYFFA (arimoclomol) | **alta** | Registrado en la columna `seguridad` de `research/track2_candidates.tsv`. **Ningún candidato se propone para administración** |
| **C013** | «`FANCD2` era una hipótesis competidora seria» | Los tres alelos están al **~47 % de frecuencia poblacional** y los tres son **heterocigotos** (`0/1`). No hay homocigoto ni pareja en *trans* | EXP-020 · `docs/FANCD2_AUDIT.md` | baja | Rama cerrada **NEGATIVE**. Se reporta el negativo, no se esconde |
| **C014** | «Un solo gen explica a este paciente» | El probando porta **además** una parada prematura en `LZTR1`, heterocigota, en el transcrito MANE, de alta calidad (DP 48, `GQ` 99, balance alélico 0,50, PASS), rara (`MAX_AF` 3 × 10⁻⁵) y clasificada **patogénica / probablemente patogénica en ClinVar**. No causa aneuploidía variegada, pero es real | EXP-022 · `docs/COMPETITOR_AUDIT_LZTR1_IGBP1.md` | media | **No se archiva como ruido.** Se registra como **candidato secundario / incidental de investigación**, no como hallazgo clínico devolvible: exigiría confirmación independiente y un procedimiento de devolución de resultados. No cambia la hipótesis causal del MVA, se mantiene fuera del pitch principal y **no se emite recomendación clínica** (Regla Dura 3) |

## Contradicciones que aún no podemos resolver

| ID | Conflicto | Qué lo resolvería |
|---|---|---|
| **C005 vs C006** | Una fuente dice que quitar chaperonas hunde BUBR1; otra, que un inductor farmacológico no sube la chaperona en un contexto proteotóxico distinto | Un ensayo de abundancia de BUBR1 **específico de variante** en células del paciente, con brazo genético (`ca-HSF1`) y brazo farmacológico en la misma placa |
| **C008** | El rescate parcial en mosca puede ser techo del modelo o techo del mecanismo | Medir en el mismo sistema si el rescate del número de células madre **aumenta** el fitness clonogénico. Si lo aumenta, el rescate se convierte en daño |

## Preguntas obligatorias para cada fila

- ¿La contradicción ataca la observación, el mecanismo, la generalización o la seguridad?
- ¿Viene del mismo contexto biológico? *(C006 y C007 vienen de fibroblastos NPC1, no de células aneuploides: esa distancia se declara.)*
- ¿Pueden ser ciertas las dos bajo tejidos, dosis, estadios o cariotipos distintos?
- ¿Qué experimento nuevo resolvería el conflicto?
