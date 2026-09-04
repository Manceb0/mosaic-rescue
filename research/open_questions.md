# Preguntas abiertas

> **Estado del fichero.** Estas 28 preguntas se escribieron al arrancar el proyecto, antes de
> abrir el dataset. **La mayoría ya están resueltas**, y varias lo están desde hace semanas.
> Dejarlas escritas en presente hacía parecer que aún no sabíamos si existía RNA-seq. Cada una
> lleva ahora su respuesta y dónde se resolvió. Las que siguen abiertas se marcan **ABIERTA**
> y son las únicas que deberían mover trabajo.

Resumen: **16 resueltas · 7 retiradas junto con su arquitectura (bloques 12–15 y 20–22) · 5 abiertas (18, 19, 23, 25, 26).** Suman 28.

## Disponibilidad de datos — todas resueltas en `notebooks/00_DATA_REALITY.ipynb`

| # | Pregunta | Respuesta | Estado |
|---|---|---|---|
| 1 | ¿Cuáles son los 11 ficheros gated? | Inventariados en el notebook 00; FASTQ L001 (R1/R2) + VCF son los que sostienen el análisis | **resuelta** |
| 2 | ¿Solo VCF, o también BAM/CRAM? | **Solo VCF y FASTQ.** Sin BAM/CRAM de profundidad completa. Esto bloquea EXP-012 (SV/CNV) | **resuelta** |
| 3 | ¿Hay RNA-seq masivo? | **No existe** | **resuelta** |
| 4 | ¿Hay scRNA-seq u otra modalidad resuelta por célula? | **No existe.** Es la razón por la que cayó *Patient-as-Screen* | **resuelta** |
| 5 | ¿Hay muestreo longitudinal? | **No existe.** Es la razón por la que cayó *Mosaic Forecast* | **resuelta** |
| 6 | ¿Hay cariotipo clínico que sirva de verdad de campo? | **No entregado.** Sin él, la huella de mosaicismo no se puede validar | **resuelta** |
| 7 | ¿Fibroblastos, iPSC, organoide, proteómica, imagen? | **Ninguno.** Tampoco tejido tumoral ni hemograma contemporáneo (pedido, sin respuesta) | **resuelta** |

## Track 1

| # | Pregunta | Respuesta | Estado |
|---|---|---|---|
| 8 | ¿Cuál es la hipótesis causal principal tras priorizar el genoma completo? | `BUB1B`. **#4 en el `A0` congelado, #1 en `A0-FREQFIX`**; los dos números se reportan juntos | **resuelta** (EXP-006, EXP-021b) |
| 9 | ¿Encaja en genes MVA clásicos o en una vía MVA-*like* más amplia? | Gen MVA clásico: `BUB1B` es MVA1 (OMIM 257300) | **resuelta** |
| 10 | ¿La fase o la herencia son informativas? | **No.** Sin muestras parentales la fase queda sin resolver y `PM3` bloqueado | **resuelta como negativa** (EXP-013) |
| 11 | ¿El candidato implica dosis, estabilidad, pérdida de interfaz, catálisis, *splicing* o regulación? | Alelo truncante (dosis/estabilidad) + missense en bolsillo estructural. **Splicing descartado** por AlphaGenome | **resuelta** (EXP-009, EXP-010) |

## *Patient-as-Screen* — retirada

Preguntas 12–15. La arquitectura que las motivaba se retiró por falta de modalidad resuelta
por célula (pregunta 4). Ver `docs/00_ESTADO_Y_OBSOLESCENCIA.md`. **No se responden porque ya
no se persiguen**, no porque falte trabajo.

## Rescate

| # | Pregunta | Respuesta | Estado |
|---|---|---|---|
| 16 | ¿Qué datasets funcionales externos encajan con el mecanismo? | Los ocho puentes de `research/track2_evidence.tsv`, auditados en diez dimensiones. **61 de 80 celdas vacías** | **resuelta como mapa de huecos** |
| 17 | ¿Hay supresores con apoyo ortogonal en CRISPR / Perturb-seq / organismos modelo? | Sí, parcial: `ca-HSF1` en células aneuploides isogénicas humanas y la vía TOR/autofagia en *Drosophila* | **resuelta** |
| 18 | ¿Los mecanismos de rescate aumentan peligrosamente la supervivencia de células aneuploides? | **Pregunta central del Safe Rescue Corridor y sigue ABIERTA.** Hay señal de que el corredor importa (C008) | **ABIERTA** |
| 19 | ¿Hay evidencia de dosis de proteína, mPOS/proteostasis, estrés mitocondrial, senescencia, IFN o competición celular en **este** caso? | Proteostasis: evidencia externa, no del paciente. Mitocondrial: MitoRead **no calibrado**. El resto, sin datos | **parcial · ABIERTA** |

## *Forecasting* — retirada

Preguntas 20–22. Sin muestreo longitudinal (pregunta 5) no hay pronóstico específico de
paciente. Retirada con su arquitectura.

## Intervención

| # | Pregunta | Respuesta | Estado |
|---|---|---|---|
| 23 | ¿Algún fármaco aprobado reproduce el mecanismo de rescate a exposición plausible? | **Es exactamente lo que no se sabe.** Es el puente 7, el hueco traduccional, y la razón de que arimoclomol entre como **centinela de falsación** | **ABIERTA** |
| 24 | ¿Hay precedente pediátrico? | Sí para los tres: azitromicina, arimoclomol (NPC, ≥2 años) y sirolimus | **resuelta** |
| 25 | ¿La farmacogenómica es relevante para la intervención preseleccionada? | **No evaluada.** No se ha cruzado el genoma del paciente con alelos farmacogenéticos | **ABIERTA** |
| 26 | ¿La intervención mueve el estado hacia un corredor seguro en vez de solo aumentar supervivencia? | Sin medir. Es el criterio de descarte escrito en `research/track2_candidates.tsv` | **ABIERTA** |

## Prueba científica final

| # | Pregunta | Respuesta | Estado |
|---|---|---|---|
| 27 | ¿Qué haría este proyecto verdaderamente novedoso? | Dos candidatos: **(a)** el recentrado del BAF con signo en aneuploidía variegada, cuantificado (EXP-015a) **y la falsación por nosotros mismos de nuestra primera explicación de él** (EXP-015c), que es la parte que un jurado no espera ver; **(b)** el mapa de puentes que localiza el hueco traduccional en vez de saltárselo | **resuelta** |
| 28 | ¿Cuál es el experimento más fuerte que podría demostrar que nos equivocamos? | Un ensayo de abundancia de BUBR1 **específico de variante** en células del paciente, con brazo genético y farmacológico en la misma placa. Si `ca-HSF1` sube BUBR1 y arimoclomol no, cae la traducción farmacológica. Si **ninguno** sube BUBR1, cae la ruta T2-A entera | **resuelta** |
