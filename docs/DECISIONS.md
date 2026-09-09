# Bitácora de decisiones

Se escribe **antes** de cada fase, no después. Para cada una: qué se espera encontrar,
qué resultado mataría la hipótesis, y qué se decidió. Si el resultado contradice lo
preregistrado, no se reescribe la predicción — se documenta la sorpresa.

Ver `CLAUDE.md`, Regla Dura 6 y Flujo de trabajo.

| Fecha | Fase | Qué esperamos | Qué lo mataría | Resultado | Decisión |
|---|---|---|---|---|---|
| 2026-08-29 | Integración | — | — | Master Brief integrado al repositorio; ramas sin datos que las sostengan marcadas como superadas | Ver `docs/00_ESTADO_Y_OBSOLESCENCIA.md` |
| 2026-08-29 | Arquitectura | Que el ranking de AlphaGenome aguantara revisión | Que el umbral del ~50 % resultara ser BubR1-específico y no universal | **Lo era.** Dosis residual pasa a condicional; segundo alelo oculto sube a prioridad general | `docs/04_ARQUITECTURA_MAESTRA.md` |
| 2026-08-29 | Fase 1 — QC de L001 | Reads de 150 bp, R1/R2 balanceados, profundidad en rango 45-60x | Longitud variable (indicaria recorte previo), desbalance R1/R2, calidad baja | **149 bp**, varianza cero en 136 586 642 reads; R1==R2 exacto; 52,5x bruta / ~43x efectiva; 92,9 % ≥ Q30 | Datos aptos para Fase 1. Ver `docs/QC_L001.md` |
| 2026-08-29 | Fase 1 — PCR-free | Que el QC resolviera si la librería es PCR-free | Que el adaptador no discriminara entre kits | **No discrimina.** Tagmentación confirmada, pero `Illumina DNA Prep` y `Illumina DNA PCR-Free` comparten adaptador | Pregunta reformulada para el email: *¿cuál de los dos kits?* |
| 2026-08-29 | Fase 0.2 — cabecera VCF | Ver preregistro de 6 predicciones | Cabecera sin build ni caller declarados | **5 de 6 acertadas.** GRCh38, 1 muestra, sin anotar, `AD` presente, no gVCF. Sentieon Haplotyper; 5 012 204 variantes | Las tres rutas de búsqueda quedan desbloqueadas. Ver `docs/VCF_HEADER.md` |
| 2026-08-29 | Fase 0.2 — fase física | **Predije que NO habría `PS`/`PGT`/`PID`** | Que los campos existieran y con alcance útil | **Fallé en la letra: `PGT`/`PID` existen.** Pero al medir: bloque máximo 288 pb, mediana 7 pb, cero bloques ≥ 300 pb | **El techo `unphased ≠ trans` sigue en pie.** Solo sirve para corregir MNV. No se reescribe §4.2 |
| 2026-08-29 | Fase 1 — censo del VCF | Reparto normal de clases y het/hom en rango | Ratio het/hom deprimido (consanguinidad), o exceso de filtradas | **PASS 94,58 %** (4 740 790); rescate 271 414, dominado por `MQ40`. het/hom 1,61. Balance alélico 78,4 % en 0,40–0,60 | Los dos primeros niveles del funnel quedan medidos. El resto espera anotación |
| 2026-08-29 | Estrategia de carriles | — | — | Se decide **no elegir** entre MVA y renal | Tres carriles en paralelo, con un tercero genome-wide sin panel para evitar anteojeras |
| 2026-08-30 | Fase 2.1 — funnel | 0 o 1 HIGH en panel MVA; 0 en renal | ≥2 HIGH en un gen MVA | **Ambas falladas.** 2 HIGH en MVA (genes distintos) y 2 en renal (ambas `start_lost` con rsID conocido). **`BUB1B` con 1 HIGH + 1 MODERATE, ambas PASS, het, sin rsID** | Ver `docs/FUNNEL_PASS1.md`. La rama de dosis residual pasa a condición cumplida, pendiente de frecuencia |
| 2026-08-30 | Fase 2.2 — pasada 2 | Que la missense pudiera ser polimorfismo común y tumbara la rama | Frecuencia poblacional apreciable en cualquiera de las dos | **Truncante: ClinVar `pathogenic`/`likely_pathogenic`, gnomAD ~1e-4, NMD predicho (exón 17/23). Missense: AUSENTE de gnomAD, novel, dominio quinasa, SIFT deleterious, PolyPhen 0,997, exón 23/23 escapa NMD** | La rama de dosis residual se activa. Ver `docs/CANDIDATES_PASS2.md` |
| 2026-08-30 | `PM1` — error de conteo | Conté «0 P/LP vs 35 B/LB» mezclando todas las consecuencias | — | **31 de esos 35 eran sinónimas.** Solo 4 missense. `PM1` se evalúa sobre la clase comparable | Rehecho solo con missense. **Cambia el mensaje**, no solo el número |
| 2026-08-30 | `PM1` — resultado real | — | — | En **todo** `BUB1B`: **1 sola missense P/LP** de 1 497, y **95 % VUS**. Ningún punto del gen tiene hotspot demostrable | `PM1` no aplica por ausencia de hotspot en cualquier parte, no por señal en contra de este candidato |
| 2026-08-30 | `PS1` / `PM5` | — | — | El mismo cambio de aminoácido existe en ClinVar por otra ruta nucleotídica, pero **VUS**. Ninguna P/LP en el residuo | Ninguno aplica. Un submitter independiente llegó a la misma conclusión que nosotros |
| 2026-08-30 | ClinVar del caché | Que el caché de VEP sirviera para curar | — | El caché lleva **ClinVar 2025-09**; el vigente es **2026-08-22** e incluye dos entradas que el caché no tenía | Para curación se consulta la versión vigente, no el caché |
| 2026-08-30 | `PP3` con REVEL | Umbrales sellados antes de mirar: ≥0,932 Strong · 0,773-0,931 Moderate · 0,644-0,772 Supporting · <0,644 nada | Que cayera por debajo de 0,644 | **REVEL = 0,472.** Por debajo del mínimo. Tampoco alcanza `BP4` (>0,29) | **`PP3` NO SE APLICA.** REVEL es no informativo para esta variante |
| 2026-08-30 | Valor del preregistro | — | — | SIFT `deleterious` 0,01 y PolyPhen 0,997 apuntaban fuerte a patogenicidad; el calibrado dice que no hay evidencia asignable | **Sumarlos habría dado un `PP3` injustificado.** Se ve el tamaño del error evitado |
| 2026-08-30 | Techo de la missense | Que ClinVar pudiera sacarla de VUS | — | Sin `PP3`, el máximo con `PM1`+`PM5` es **5 puntos**, y VUS llega hasta 5 | **Nada salvo fase o función mueve esta variante** |
| 2026-08-30 | Fase 3 — curación ACMG | Que «exón 17/23» bastara para `PVS1` | Que el PTC quedara cerca de la última unión | **Medido: el PTC está a ~750 nt de la última unión exón-exón, umbral 50-55 nt, margen ~14×.** NMD predicho con holgura | `PVS1` candidato con árbol recorrido. Ver `docs/ACMG_CURATION.md` |
| 2026-08-30 | Clasificación provisional | — | — | **Truncante ≈ Likely Pathogenic** (`PVS1` + `PM2_Supporting` = 9 pts). **Missense = VUS** y sigue VUS aunque entre `PP3` | Formulación: *one likely pathogenic truncating allele + one rare missense candidate, phase unresolved* |
| 2026-08-30 | `PM3` | — | — | Bloqueado por decisión, más conservador que ClinGen | Es el criterio que convertiría «dos variantes» en «heterocigosis compuesta» |
| 2026-08-30 | `PP5` | — | — | **No usado.** ClinGen recomienda abandonar `PP5`/`BP6` | La etiqueta ClinVar se desglosa como evidencia externa, no como criterio |
| 2026-08-30 | Mecanismo del alelo B | Hablé de «dominio quinasa» sugiriendo pérdida catalítica | — | **BUBR1 es pseudoquinasa** (PMID 22698286): actividad catalítica prescindible; los residuos que unen ATP en quinasas convencionales son aquí esenciales para **estabilidad conformacional** | La pregunta pasa a ser desestabilización → menos proteína disponible. Encaja mejor con MVA, que es de abundancia |
| 2026-08-30 | Fase — sobrealcance | Escribí «ningún análisis sobre estos datos puede establecer trans» | — | **Sobrealcance.** Se midió la cadena de heterocigotos: solo uno intermedio, huecos de 6 769 y 4 142 pb frente a fragmentos de ~300 pb | El refaseado con lecturas cortas no puede conectarlos. **Ahora es medición, no suposición** |
| 2026-08-30 | Track 2 — chaperonas | — | — | Inhibir HSP90 desploma la abundancia de ciertos mutantes missense de BUBR1, no la del silvestre; bloquear el proteasoma rescata parte (PMID 20516114) | Abre pregunta Track 2 con conexión aguas arriba. **No es nominación de fármaco**: colisión oncológica vigente |
| 2026-08-30 | Error propio | Afirmé que ninguna candidata estaba en dbSNP | — | **Falso.** Lo deduje de la columna `ID` del VCF vacía, que solo indica que el caller no anotó. El truncante sí está, y en ClinVar como patogénico | La columna `ID` no es fuente de novedad. Se consulta dbSNP/gnomAD/ClinVar explícitamente |
| 2026-08-30 | Otros HIGH de panel | Que hicieran falta para descartarlos | — | `VDR` AF~0,81, `ATP6V1B1` AF~0,51, `ANAPC1` AF~0,086. **Ninguno sobrevive** | Confirma la predicción #6: sin frecuencia, el genome-wide es ruido |
| 2026-08-30 | Método de preregistro | — | — | **La predicción #4 estaba mal redactada**: mezclaba «HIGH en el panel» con «HIGH en un gen». Admite dos lecturas | Se registra como fallo de método. Los próximos preregistros fijan la unidad de conteo |
| 2026-08-29 | Panel renal | Que MAGED2 fuera el primer candidato por el eje perinatal | Que el fenotipo MAGED2 fuera transitorio y la nefrocalcinosis persistente | **Es transitorio** (PMID 27120771). Si persiste hoy, MAGED2 baja y suben SLC12A1/KCNJ1/CLCNKB/BSND | `config/panels/nephrocalcinosis.txt` |
| 2026-09-01 | Presentación | Que el lenguaje del repositorio pasara por escrito y revisado por un equipo humano | Que humanizar el texto obligara a suavizar un resultado | 31 ficheros con patrones de escritura de asistente. Se reescribieron 390 guiones largos, 137 flechas usadas como puntuación, 22 marcadores de verificación en símbolo, y las ocho etiquetas de pie idénticas. Ninguna cifra, estado ni conclusión se tocó | Solo lenguaje. La disciplina de declarar el límite de la evidencia se conserva, con un encabezado distinto por notebook para que no se lea como plantilla |

## Pendiente de preregistro

~~- **Fase 0.2**~~ — **preregistrada 2026-08-29, antes de abrir el fichero.** Ver abajo.
- **Fase 1** — auditoría HPO Residual. Tabla de decisión ya preregistrada en el plan §1.3.
- **Fase 3** — predicción de la huella de mosaicismo. Ya preregistrada en el brief §6.4.
~~- **Anotación**~~ — **preregistrada 2026-08-29.** Ver abajo.
- **Hidden Second Allele en `BUB1B`** — **abierta como prioridad tras el debilitamiento de la missense.** Orden: intrónico profundo y región de splicing → promotor y regulador aguas arriba (hay precedente humano publicado) → SV/CNV alrededor del gen → AlphaGenome sobre las no codificantes que sobrevivan a rareza y plausibilidad reguladora.
- **FASE de los dos candidatos de `BUB1B`** — **máxima prioridad del proyecto.** Dos vías: genotipos parentales, o secuenciación dirigida de lectura larga sobre los ~11 kb que los separan (no necesita a los padres). Vale más que cualquier análisis adicional sobre los datos actuales.
- **ROH** — análisis de tramos de homocigosis. El ratio het/hom de 1,61 no muestra consanguinidad grosera, pero es un proxy pobre y MVA es recesiva.
- **Fase 7** — simulación del índice de dispersión contra método estándar de mCA, a fracciones celulares de 1/2/5/10/20 %. Preregistrada en `docs/04_ARQUITECTURA_MAESTRA.md` §2: si pierde, se reporta que perdió y se usa el método estándar.

---

## Preregistro — Fase 0.2, auditoría de la cabecera del VCF

Escrito **antes** de abrir el fichero (301 MB en `Downloads`). Solo cabecera: ninguna
variante del paciente se mira en este paso.

| # | Qué espero | Por qué importa | Qué cambia si me equivoco |
|---|---|---|---|
| 1 | Build **GRCh38** | El brief lo asume y los paneles están en esas coordenadas | Si es GRCh37, hay que remapear los dos paneles y toda coordenada del proyecto |
| 2 | **Una sola muestra** | Sin padres, la fase no se resuelve por trío | Si hubiera más de una, cambia todo el planteamiento del §9.1 |
| 3 | **Sin anotación previa** (VCF crudo del caller) | Determina si la Fase 2.2 empieza de cero | Si trae `CSQ`/`ANN`/`dbNSFP`/gnomAD, la Fase 2.2 se acorta mucho |
| 4 | `FORMAT` con `GT`, `AD`, `DP`, `GQ`, `PL` | `AD` es imprescindible para balance alélico: sostiene heterocigosis compuesta y la rama de mosaicismo | **Sin `AD` se cae la confianza en compound-het y en §6** |
| 5 | **Sin `PS`/`PGT`/`PID`** | Son los campos de fase física | **Si están, la pregunta cis/trans deja de ser irresoluble y pasa a parcialmente resoluble.** Sería el hallazgo de mayor valor de esta fase |
| 6 | No es un gVCF | Un gVCF con `<NON_REF>` necesita parseo distinto | Cambia el pipeline de lectura entero |

**La predicción que más quiero ver fallada es la #5.** Todo el techo que le pusimos al
segundo alelo (`unphased ≠ trans`, `docs/03_ALPHAGENOME_ASSESSMENT.md` §4.2) asume que no
hay fase. Si el caller dejó bloques de fase física, parte de ese techo se levanta.

**Falsificador de la fase entera:** si la cabecera no declara build ni caller, no se puede
confiar en nada aguas abajo y hay que pedirlo al laboratorio antes de seguir.

### Resultado — la sorpresa, documentada sin reescribir la predicción

La predicción #5 **falló en la letra y acertó en el fondo**, y merece quedar registrada así
en lugar de apuntarse como acierto.

Escribí que no habría campos de fase física. Los hay: `PGT` y `PID`. Al verlos, la lectura
inmediata fue que el techo del `unphased ≠ trans` se levantaba en parte. **Se midió el
alcance real antes de escribirlo como hallazgo, y no se levanta:** el bloque de fase más
largo de todo el genoma mide **288 pb** y la mediana son **7 pb**; no hay ni un solo bloque
de 300 pb o más.

Para heterocigosis compuesta eso es inservible — el bloque máximo cubre el 0,44 % de
`BUB1B`. Sirve para una cosa concreta y estrecha: corregir variantes multinucleotídicas,
donde dos SNV en el mismo codón dan un aminoácido distinto según la fase.

**No se reescribe `docs/03_ALPHAGENOME_ASSESSMENT.md` §4.2.** El techo se mantiene.

Nota de validación cruzada: un alcance máximo de 288 pb con reads de 149 pb encaja con
fragmentos de ~300 pb, coherente con la distribución de insertos estimada en el QC de L001
(`docs/QC_L001.md`). Dos medidas independientes que concuerdan.

---

## Preregistro — Fase 2.1, anotación de consecuencia con VEP

Escrito **antes** de ejecutar VEP. Decisión de herramienta: **VEP offline con caché local**,
vía Docker. Modo `--offline --cache`, nunca `--database`: ninguna variante del paciente sale
de la máquina.

### Regla de las dos pasadas

**Pasada 1 — mínima, para construir el funnel.** Solo lo necesario para responder *qué
variante afecta a qué gen y de qué forma*: gen, transcrito, consecuencia, canónico, MANE,
biotipo, exón/intrón, consecuencia codificante, posición proteica, región de splicing,
clase de variante. Se conservan `FILTER`, `GT`, `AD`, `DP`, `GQ`, `PGT`, `PID`.

**Prohibido `--everything` sobre las 5 012 204.** Anotación máxima sobre el genoma completo
produce un fichero inmanejable y ninguna decisión mejor.

**Pasada 2 — solo sobre la shortlist.** gnomAD, ClinVar, CADD, SpliceAI, literatura, y
AlphaGenome únicamente sobre candidatos no codificantes, intrónicos profundos o de splicing
que lo justifiquen.

El orden importa y no es negociable:
`5 M → VEP → shortlist → AlphaGenome`, nunca `5 M → AlphaGenome`.

### Qué espero encontrar

| # | Predicción | Qué la falsaría | Qué cambia si falla |
|---|---|---|---|
| 1 | **~1–2 %** de las 5 M con consecuencia codificante (~50–100 k) | Menos de 20 k o más de 200 k | Un número muy distinto sugiere anotación mal configurada, no biología |
| 2 | La inmensa mayoría intergénicas e intrónicas | — | — |
| 3 | **~10–15 k** variantes codificantes raras tras filtrar por frecuencia | — | Requiere gnomAD, que es pasada 2 |
| 4 | **0 o 1** variantes de alto impacto en el panel MVA | ≥2 de alto impacto en un gen MVA | **Sería el mejor desenlace posible**: heterocigosis compuesta candidata |
| 5 | **0** variantes de alto impacto en el panel renal | ≥1 | Elevaría la rama del fenotipo mixto de condicional a activa |
| 6 | El carril genome-wide producirá **más ruido que señal** sin filtro de frecuencia | — | Confirma que gnomAD es imprescindible en pasada 2 |

**La predicción que más quiero ver fallada es la #4.** Si aparecen dos alelos de alto
impacto en un gen de MVA, el proyecto entero cambia de fase en un día.

**Y la que más me preocupa acertar es la #5 combinada con la #4 en cero:** ningún candidato
claro en ninguno de los dos paneles dejaría el carril genome-wide como única vía, que es el
escenario más lento y donde el sesgo de confirmación es más peligroso.

### Trazabilidad — obligatoria

El VCF original **no se modifica**. VEP produce un derivado nuevo en `work/` (ignorado por
Git) acompañado de un fichero de procedencia con:

```
hash del VCF de entrada
version de VEP
version del cache
ensamblado (GRCh38)
comando exacto
fecha
hash de la salida
```

Sin eso no se puede afirmar delante de un jurado cómo se pasó de 5 012 204 variantes crudas
a las candidatas finales — que es justamente la ventaja de haber recibido un VCF sin anotar.

---

## Preregistro — Hidden Second Allele, locus ampliado de `BUB1B`

Escrito **antes** de extraer nada. Busca SNV/indel en el **locus ampliado**, no solo dentro
de los límites del gen: existe precedente humano de un segundo alelo regulador decenas de kb
aguas arriba, así que restringirse al cuerpo del gen sería conceptualmente incorrecto.

**Ventana:** cuerpo del gen ± ~100 kb. Cubre con margen la distancia del precedente.

**Orden de matanza, del filtro barato al caro:**
`frecuencia → calidad → posición funcional → conservación y regulación → AlphaGenome`

### Predicciones

| # | Predicción | Qué la falsaría | Qué significaría |
|---|---|---|---|
| 1 | ~800–2 000 variantes en el locus ampliado | Menos de 200 | Ventana mal construida |
| 2 | **< 5 %** raras o ausentes de gnomAD tras filtrar | > 20 % | Filtro de frecuencia mal configurado |
| 3 | **0–3 candidatos** llegan a AlphaGenome | > 15 | Los filtros previos no están discriminando |
| 4 | **AlphaGenome dará Δ plano** en todos | Un Δ marcado en splicing o expresión | **Sería el hallazgo del proyecto** |
| 5 | Nada en promotor ni región de splicing canónica | Una rara en promotor o splice-region | Escalada inmediata |

**La predicción que quiero ver fallada es la #4.** Predigo que no encontraremos el segundo
alelo por esta vía, y lo escribo antes para que un negativo sea reportable en lugar de
decepcionante.

**Si la #4 se cumple** (todo plano), el resultado se reporta tal cual —*«se rastreó el
paisaje regulador de `BUB1B` y AlphaGenome no apoya un segundo alelo funcional de tipo
SNV/indel»*— y la rama pasa a SV/CNV.

### Regla sobre el nivel de rescate

`PASS` y filtradas se cuentan **por separado** desde el principio. Una filtrada no vuelve a
ser candidata por estar en el locus: hay que examinar por qué falló.

### Regla sobre SV/CNV, adelantada

Cuando toque: **L001 sirve como piloto para demostrar que el pipeline funciona y encontrar
señal grande, pero no para cerrar un negativo.** El VCF se generó con el dataset completo;
afirmar «no hay segundo alelo estructural» exige profundidad equivalente. Un negativo sobre
un carril no es un negativo.

---

## Resultado — Hidden Second Allele, rama SNV/indel: **NEGATIVA**

| # | Predicción | Resultado | |
|---|---|---|---|
| 1 | 800–2 000 variantes en el locus | **321** | ❌ fallé por lo alto |
| 2 | < 5 % raras tras filtrar | **1,2 %** | ✅ |
| 3 | 0–3 candidatos llegan a AlphaGenome | **1** | ✅ |
| 4 | **AlphaGenome dará Δ plano** | **Δ plano** | ✅ *(quería fallarla)* |
| 5 | Nada en promotor ni splicing canónico | nada | ✅ |

**Un único candidato nuevo** en 270 kb: intrónico profundo en el intrón 20, ausente de
gnomAD, sin rsID, `PASS`, heterocigoto. A >1 kb del borde de exón más cercano.

**AlphaGenome:** ningún delta relativo supera el 3,4 %; las tres modalidades de splicing
por debajo del 1,2 %, con el delta local de junciones en **0,0000**. Control de sanidad
pasado: las medias REF y ALT son no triviales, así que el delta plano es resultado y no
llamada fallida.

> *Se rastreó el paisaje regulador de `BUB1B` en 270 kb y AlphaGenome no apoya un segundo
> alelo funcional de tipo SNV/indel.*

**Límite declarado del análisis:** el resumen agrega 1 617 pistas de ChIP-TF y 667 de RNA
con estadísticos; un efecto fuerte en un solo tejido podría diluirse. El argumento que no
depende de ese promedio es el splicing, cuyo delta local es cero.

Fue la **única transmisión de dato del paciente fuera de la máquina** en todo el proyecto,
prevista en `docs/03_ALPHAGENOME_ASSESSMENT.md` §7.

## CNV grande en `BUB1B`: **sin evidencia**, desde el VCF y sin alinear

| Métrica | Región de `BUB1B` | Genómico |
|---|---|---|
| DP mediana | **44×** | ~40× |
| HET/HOM | **2,89** | 1,61 |

Una deleción en heterocigosis daría pérdida de heterocigosidad y DP a la mitad. Se observa
lo contrario: profundidad normal y **más** heterocigosis que la media.

> **Corrección de formulación.** Escribí «CNV grande descartada». Es demasiado fuerte: la
> profundidad del VCF **no está normalizada para llamar número de copia** y varía por
> mapeo local y contenido GC. Lo defendible es:
>
> > *No evidence for a large heterozygous deletion spanning `BUB1B` from VCF depth and
> > heterozygosity. Smaller CNVs, balanced SVs, insertions and breakpoint-local events
> > remain unresolved.*

**Sigue sin resolverse:** CNV pequeñas que quepan entre variantes (el cuerpo del gen es
pobre en variantes), eventos equilibrados —inversiones, translocaciones— que no cambian
número de copia, inserciones, y todo lo local a un punto de rotura.

## Bloqueo de datos descubierto

**Solo `L001` está en disco: 21 GB, no los 86 GB de los cuatro carriles.** El VCF sí se
generó con el dataset completo, pero los FASTQ de `L002`–`L004` no están aquí.

Consecuencia directa sobre la regla preregistrada: **con un solo carril (~13×) no se puede
cerrar un negativo de SV.** La rama estructural queda **bloqueada por disponibilidad de
datos, no por cómputo**.

---

## Resultado — análisis estructural del candidato missense

| Métrica | Valor | Lectura |
|---|---|---|
| pLDDT local del modelo | **91,1** (media global 63,6) | Región fiable, muy por encima de la media |
| RSA relativa | **16,2 %** | **Enterrado** |
| Vecinos a 5 Å | 10, de los cuales **8 hidrofóbicos**, 4 aromáticos | Núcleo compacto |
| Puentes de H de la cadena lateral | **3, todos al esqueleto** (2,83–2,95 Å) | Grapa la conformación local |

**Predicción: desestabilizante.** El cambio mete una carga positiva y una cadena mucho más
larga en un bolsillo hidrofóbico, y destruye tres puentes con el esqueleto que la geometría
del residuo entrante no puede reproducir.

**No se ejecutó AlphaFold:** el modelo ya existe en AlphaFold DB. Las dos estructuras
experimentales que VEP mapeaba **no cubren el residuo** — solo resuelven hasta ~345.

### Tensión con REVEL, declarada y no resuelta a conveniencia

REVEL dio 0,472 (indeterminado); la estructura apunta a desestabilización. **`PP3` no se
reabre.** Los umbrales estaban preregistrados y REVEL quedó por debajo. Usar el resultado
estructural para reabrirlo sería buscar el predictor que da la respuesta deseada.

**La clasificación no cambia: sigue VUS.** Lo que cambia es que ahora hay una hipótesis
mecanística **medible**: abundancia de BUBR1 reducida. Ese ensayo habilitaría `PS3` y es,
junto con la fase, uno de los dos únicos caminos que mueven esta variante.

**Pendiente:** conservación (falta el alineamiento múltiple, y es el dato que reconciliaría
o no la discrepancia con REVEL) y un ΔΔG cuantitativo. Se ha preferido no dar un número que
no se puede sostener.

---

## Cierre — AlphaGenome por pista, y matices estructurales

### La rama SNV/indel reguladora queda cerrada

Se revisaron las **pistas individuales** para descartar que un efecto específico de tejido
se estuviera diluyendo en el agregado de 1 617 pistas de ChIP-TF y 667 de RNA.

- **El top por cambio relativo es ruido.** Las líneas base locales de esas pistas son
  ~0,0001–0,005; un 5 % sobre cero es división por un número minúsculo, no señal.
- **El top por cambio absoluto** son pistas de CTCF y RAD21, con cambios relativos del
  1,2–2,3 % sobre líneas base de 1 400–7 900. Nada funcionalmente interpretable.
- **Sin coherencia biológica**: los tejidos del top son un surtido disperso (epitelio
  traqueal, ovario, vía biliar, bazo, hígado). No hay señal renal ni hematopoyética.

> *No candidate survived population filtering plus global and track-level AlphaGenome
> interrogation.*
>
> **No** «AlphaGenome demostró que no existe un segundo alelo». Solo que **no apoyó los
> SNV/indel candidatos que encontramos**.

### El análisis geométrico corrige a la baja mi propio argumento estructural

| Argumento | Estado tras el análisis |
|---|---|
| Choque estérico | **Debilitado.** Densidad de 47,1 át./1000 Å³, por debajo de núcleo (60–90) |
| Carga enterrada | **Debilitado.** La cáscara donde aterrizaría tiene 131 Å² de SASA: hay salida al solvente |
| **Pérdida de puente aceptor** | **En pie, y rotámero-independiente** |

El punto que sobrevive: la cadena lateral silvestre **acepta** un puente del nitrógeno del
esqueleto de un vecino. El grupo entrante es un amonio y **solo dona**. Ese contacto se
pierde por química, y ningún rotámero puede rescatarlo.

**FoldX está bloqueado por licencia** (registro manual). Se ha preferido no sustituirlo por
otro predictor y dar un ΔΔG no validable.

---

## Preregistro — qué pistas de AlphaGenome se dibujan

Congelado **antes** de repetir la llamada, para que no se puedan elegir las más
favorecedoras después de verlas.

| Bloque | Pistas | Criterio de selección |
|---|---|---|
| Splicing | `splice_sites`, `splice_site_usage`, `splice_junctions` | **Obligatorias las tres.** Son el mecanismo por el que un intrónico profundo podría importar |
| Insulador | **CTCF** y **RAD21** | Fueron los mayores cambios **absolutos** en la primera pasada |
| Expresión | Las **2** pistas de RNA con mayor \|Δ\| local | **Solo si superan un mínimo de señal basal**: `ref_local ≥ 0,01`. Sin ese filtro se seleccionarían pistas de línea base nula, donde un Δ minúsculo da un porcentaje relativo enorme |
| Cromatina | 1 de `ATAC` + 1 de `DNASE`, la de mayor \|Δ\| con el mismo mínimo | Representativas |

**Todas se etiquetan con su tejido o modelo.**

### Reglas de dibujo, también congeladas

1. **REF y ALT comparten exactamente la misma escala Y** dentro de cada pista. Tres
   gráficos con escalas distintas harían parecer grande algo minúsculo.
2. **Δ = ALT − REF con el cero visible**, en su propio carril.
3. Eje genómico real, con la posición del candidato marcada.
4. A la derecha de cada pista: `máx |Δ|`, `línea base`, `Δ relativo`, `tejido`.
5. **`PREDICTED — AlphaGenome`** en grande y en ocre, para que un recorte no se confunda
   con medición experimental.

### Qué se espera

Que REF y ALT se vean **prácticamente idénticos** y el carril Δ **plano en el cero**. Si
así sale, la figura muestra el negativo en vez de pedir que se nos crea.

Si alguna pista mostrara un Δ visible, **se reporta igual** — la selección está congelada
y no admite descartar la que no convenga.

---

## Regla de formato de figuras

Toda figura final existe en tres versiones:

| Fichero | Para qué |
|---|---|
| `figX_nombre.svg` | **Publicación y Markdown.** Es la que se embebe |
| `figX_nombre.png` | Diapositivas y compatibilidad |
| `figX_nombre.html` | Solo si aporta interactividad real |

Y en el Markdown se embebe la imagen, no un enlace:

```markdown
![Figura 2 — BUBR1 Variant Landscape](../figures/fig2_landscape.svg)
```

**Motivo:** abrir el repositorio en GitHub tiene que enseñar la ciencia directamente, no
una tarjeta bonita ni un enlace a un artifact.

---

## Preregistro — EXP-006, ranking genome-wide sin panel

Escrito **antes** de ejecutar el ranking. Es el experimento que faltaba: hasta ahora
`BUB1B` apareció fuerte **dentro de un panel que elegimos nosotros**, y eso no es lo mismo
que sobrevivir a una búsqueda sin panel.

**Garantía de diseño:** el script de extracción **no menciona ningún gen**. El único filtro
es consecuencia funcional. 13 109 variantes en **6 322 genes** compiten.

### Modelos de herencia que se evalúan

Sin genotipos parentales, *de novo* no es evaluable y no se finge.

| Modelo | Criterio | Nota |
|---|---|---|
| Recesivo homocigoto | `1/1` raro y dañino | El más limpio |
| Recesivo compuesto **candidato** | ≥2 heterocigotos raros y dañinos en el mismo gen | **Fase no resuelta** — se etiqueta siempre |
| Dominante / *de novo* candidato | LoF heterocigoto raro | No distinguible de heredado sin padres |
| Hemicigoto en X | Depende del sexo del probando | Confirmar en la cabecera |

### Predicciones

| # | Predicción | Qué la falsaría |
|---|---|---|
| 1 | Tras rareza (`MAX_AF < 1e-3`) sobrevive **< 5 %** de las 13 109 | > 20 % |
| 2 | **< 40** genes con ≥2 heterocigotos raros y dañinos | > 200 |
| 3 | **Muy pocos** homocigotos raros dañinos, quizá ninguno | Decenas |
| 4 | **`BUB1B` queda entre los 20 primeros** del ranking sin panel | Que no aparezca |
| 5 | Aparecerán genes **sin relación conocida con el fenotipo** en cabeza | — |

**La #4 es la que importa, y hay que decir por adelantado qué significa cada desenlace:**

- **Si `BUB1B` queda arriba** → *no lo encontramos porque lo buscábamos; sobrevivió a una
  búsqueda en la que 6 322 genes podían ganarle.* La historia se refuerza mucho.
- **Si NO queda arriba** → **acabamos de evitar un error**, y eso vale más que confirmarnos.
  Se reporta igual, y `BUB1B` baja de estatus hasta reevaluar.

**Prohibido** ajustar el ranking después de mirarlo para que `BUB1B` suba. Los criterios
quedan aquí escritos.

### Lo que este experimento NO puede hacer

- No resuelve fase: los pares heterocigotos son **candidatos**, no heterocigosis compuesta.
- No evalúa *de novo* sin padres.
- No cubre variantes estructurales — eso es EXP-012, bloqueado.
- No cubre reguladoras ni intrónicas profundas fuera del filtro de consecuencia.

---

## EXP-006b · Baseline externo independiente — PREREGISTRO

**Fecha:** 2026-08-31. **Escrito ANTES de descargar los datos y antes de ver un solo
resultado.**

### Por qué

`BUB1B` queda #1 en los quince análisis del modo B. Ese resultado lo produce **nuestro
propio motor**, con nuestro ranking, nuestra métrica semántica y nuestras decisiones de
filtrado. Un motor puede ser internamente consistente y estar sistemáticamente sesgado.

Un baseline externo es la única comprobación que **no comparte código ni supuestos** con lo
anterior.

### Herramienta

**Exomiser 14.1.0**, datos `2402_hg38` + `2402_phenotype`. Elegido por ser el baseline
reconocido y preregistrable en priorización de variantes con fenotipo HPO.

### Entradas — y qué queda PROHIBIDO pasarle

| Se le da | No se le da |
|---|---|
| El VCF original completo del paciente | Nuestras 142 candidatas |
| GRCh38 | La shortlist de `BUB1B` |
| Sexo del probando: masculino | Nuestras puntuaciones |
| Los 7 términos HPO del documento clínico | Nuestros paneles de genes |
| Su propia base de conocimiento | Cualquier gen candidato nuestro |

**Si se le pasara cualquier cosa de la columna derecha, el baseline dejaría de ser
independiente y no valdría como convergencia.**

### Las dos corridas, y solo dos

| ID | Fenotipo |
|---|---|
| `BASELINE-PRIMARY` | los 7 términos del probando |
| `BASELINE-FH` | los 7 + historia familiar, como sensibilidad |

### Qué se decide con el resultado — escrito ahora

| Resultado | Lectura |
|---|---|
| `BUB1B` alto en el baseline | **Convergencia independiente.** Dos motores sin código común coinciden. |
| `BUB1B` bajo o ausente | **Hallazgo serio contra nuestro pipeline.** Se investiga la discrepancia ANTES de defender nada. No se descarta el baseline por incómodo. |
| Gana otro gen que no habíamos considerado | Entra en el camino crítico como hipótesis competidora. |

**Prohibido** ajustar nuestro ranking después de ver el baseline. Si se cambia algo, se crea
una versión nueva y se reportan las dos.

### Límite de esfuerzo, declarado

El baseline es una comprobación, no un subproyecto. Si la instalación se atasca en problemas
técnicos más allá de la descarga y una configuración directa, se documenta **BLOCKED** y se
sustituye por otro baseline reconocido. **No se dedica el proyecto a hacerlo arrancar.**

Coste conocido de antemano: ~24 GB de descarga, ~100 min. Eso es espera mecánica y no cuenta
como atasco.

### Defecto encontrado en `config/phenotype_v2.yaml` — anotado, NO corregido

Al leer los términos desde la fuente congelada para el baseline, `yaml.safe_load` falla:
el bloque `analyses:` cierra con `total: 15` a la misma indentación que los elementos de la
lista, lo que **no es YAML válido**.

- **No invalida ningún resultado previo.** `src/phenotype/run_mode_b.py` nunca leyó el
  fichero: lleva los términos escritos a mano. Se ha verificado que esa copia coincide
  exactamente con los 7+1 de la fuente.
- **No se corrige el fichero**, porque está congelado. Corregirlo exigiría una v3, y el
  defecto es de sintaxis, no de contenido científico.
- `src/baseline/run_exomiser.py` extrae el bloque que necesita sin parsear el fichero entero.

> **Lo que sí deja al descubierto:** la lista de términos existe **dos veces** —en el YAML
> congelado y a mano en `run_mode_b.py`—. Hoy coinciden. Que coincidan hoy no es una garantía;
> es una comprobación que hay que repetir. La deuda queda registrada.

### Umbral de lectura del baseline — fijado ANTES de ejecutarlo

El preregistro decía «`BUB1B` alto» sin número. Eso permite elegir el criterio después de ver
el resultado, que es exactamente lo que el preregistro existe para impedir. Se fija ahora,
con Exomiser aún descomprimiéndose y sin ninguna salida generada:

| Rango de `BUB1B` en `BASELINE-PRIMARY` | Lectura |
|---|---|
| **Top 10** | **Convergencia independiente.** Es el criterio estándar de rendimiento en priorización con fenotipo. |
| 11–50 | **Convergencia parcial.** Se reporta el rango exacto; no se presenta como confirmación. |
| Fuera del top 50 | **Discrepancia seria.** Se investiga antes de defender nada nuestro. |
| Ausente de la salida | Se comprueba primero si lo filtró por frecuencia, herencia o efecto, y se reporta la causa. |

**Lecturas secundarias, también fijadas ahora:** solapamiento del top-20 entre el baseline y
nuestro `B0_FULL_PROBAND`; y qué genes entran en el top-10 del baseline que nosotros no
habíamos mirado — esos van al camino crítico como hipótesis competidoras, gane quien gane.

**No se cambia el ranking propio después de ver esto.** Si algo hay que cambiar, se crea una
versión nueva y se reportan las dos.

---

## EXP-006 · el cruce de alelos NO estaba conectado — y al conectarlo cambió A0

**Fecha:** 2026-08-31. Descubierto al construir el notebook 03, que es exactamente para lo
que sirve un notebook reproducible.

### El fallo

`src/prioritization/allele_key.py` existía, tenía **17 tests que pasaban**, y estaba
documentado como la corrección del cruce VEP↔VCF. **Ningún módulo del pipeline lo importaba.**
`load()` cruzaba por posición, que es justo lo que ese módulo venía a arreglar.

Consecuencia medida: **433 posiciones HIGH/MODERATE sin genotipo**, 346 de ellas indels, con
**207 anotaciones de impacto HIGH** perdidas en silencio. `BUB1B` no estaba entre las
afectadas.

### La corrección

No se usó `Uploaded_variation`: **este TSV no la tiene** (VEP se corrió con `--fields`
empezando en `Location`). Se reprodujeron las reglas de representación de VEP sobre cada
registro del VCF y se cruza por `(Location, Allele)`. Sin tolerancias ni distancias.

Hizo falta descubrir una convención: esta corrida de VEP escribe las inserciones como
`pos-(pos+1)`, no como la clásica `(pos+1)-pos`. Se emiten ambas formas; no genera falsos
positivos porque **el alelo también tiene que coincidir**.

**Recuperación: 420 de 433 (97 %).** Las HIGH sin cruzar pasan de 207 a 5.

### La sorpresa, documentada sin reescribir la predicción

**`A0_GENETICS` cambió. `BUB1B` pasa del puesto 1 al 4.**

- **Su puntuación NO baja**: sigue en 13,0. No perdió nada.
- Aparecen **tres genes nuevos con 13,5**: `CTU2`, `PEX5`, `SLC22A1`, los tres bajo el modelo
  más limpio —homocigoto recesivo completo—, que puntúa por encima de un compuesto con fase
  no resuelta.
- **`BUB1B` sigue siendo #1 en los otros 14 análisis** y #2 en el baseline externo.

### Auditoría de los tres competidores — hecha antes de interpretar

Los tres tienen la **misma firma**: una deleción homocigota en sitio donador con `MAX_AF`
**ausente**, y consecuencia idéntica `splice_donor_variant,splice_donor_5th_base_variant`.

| Comprobación | Resultado |
|---|---|
| ¿El cruce les asignó el genotipo correcto? | **Sí.** Cada `Location` corresponde exacta y unívocamente a un registro del VCF. No hay desplazamiento |
| ¿Es sistemático que a los indels les falte frecuencia? | **No.** Solo 1,8 % de los indels y 0,2 % del total. Son tres variantes concretas, no un fallo general |
| ¿Los apoya una fuente de frecuencia independiente? | **No.** Ninguno de los tres aparece en la salida de Exomiser, que analizó el mismo VCF con su propia base de frecuencias local. Las dos variantes de `BUB1B` sí, y las marca como contribuyentes |
| ¿Encajan con el fenotipo? | Soporte semántico 0,691 · 0,943 · **0,000** frente a **2,053** de `BUB1B`. `SLC22A1` no tiene ningún modelo mendeliano |
| Contexto delator | En `SLC22A1`, los otros dos alelos del gen tienen frecuencias de 0,79 y 0,99 |

### La decisión: NO se toca la fórmula

La regla congelada trata `MAX_AF` ausente como raro. Tres deleciones se benefician de eso.
Añadir ahora una regla que las degrade sería **ajustar el ranking después de ver que `BUB1B`
bajó**, que es literalmente lo que el preregistro de EXP-006 prohíbe.

**Se reporta `A0` tal y como salió.** La afirmación del proyecto se corrige en todos los
documentos:

> ~~«`BUB1B` es #1 en los 15 análisis, incluido A0 sin fenotipo ni ClinVar»~~
>
> **«`BUB1B` es #1 en 14 de los 15 análisis. En el control genético puro `A0` queda en el
> puesto 4, con la misma puntuación de siempre, por detrás de tres deleciones homocigotas sin
> frecuencia poblacional asignable que ninguna fuente independiente respalda.»**

**Qué haría falta para resolverlo bien:** una consulta de frecuencia poblacional sobre esas
tres deleciones. Requiere transmitir coordenadas del paciente a un servicio externo, que es
condición de parada declarada. Queda como **EXP-021, BLOQUEADO por política de datos**, no por
cómputo.

---

## EXP-015a · Simulación del índice de dispersión — PREREGISTRO

**Fecha:** 2026-08-31. **Escrito antes de implementar la simulación y antes de ver un solo
número.** Preregistro pendiente desde el inicio del proyecto (`docs/04_ARQUITECTURA_MAESTRA.md`
§2, brief §6.3).

### Por qué esta simulación es una compuerta, no un extra

El brief es explícito: el *aneuploid dispersion index* está en **`L1` hasta simularlo y
compararlo contra el método estándar de mCA**. Saltar directamente a aplicarlo sobre el
paciente sería *invention-first*: presentar un estadístico nuevo sin haber demostrado que
aporta algo sobre lo que ya existe.

**Esta simulación no usa ningún dato del paciente.** Es cómputo puro.

### El fenómeno que se simula — la cancelación de BAF

Trisomía de un cromosoma en fracción celular *f*:

| | Clonal (mCA) | Variegado (MVA) |
|---|---|---|
| Qué homólogo se gana | **El mismo** en todas las células | **Aleatorio** e independiente por linaje |
| BAF | 1/(2+f) ≈ 0,5 − f/4 · **señal** | **0,5 exacto · cancelación completa** |
| Cobertura | 2 + f | 2 + f · **sobrevive intacta** |

Y si unos linajes ganan y otros pierden el mismo cromosoma, **también se cancela la
cobertura** (2 + f₁ − f₂).

### Diseño

- Fracciones celulares: **1, 2, 5, 10, 20 %**
- Profundidad: la real del caso, **44×** mediana
- Escenarios: `CLONAL` (un homólogo) · `VARIEGADO` (homólogo aleatorio por linaje) ·
  `NULO` (euploide, para la distribución de fondo)
- Repeticiones: 200 por celda, **semilla fija** (`config/`, semilla 42)
- Estadístico estándar: desviación media de BAF respecto de 0,5 en los sitios heterocigotos
  del cromosoma afectado — el núcleo de lo que explota MoChA
- Estadístico propuesto: **varianza de la desviación log-ratio de cobertura entre cromosomas**
- Métrica de comparación: **potencia a tasa de falsos positivos fijada en 5 %** contra la
  distribución nula

### Predicciones — escritas antes

| # | Predicción | Qué la falsaría |
|---|---|---|
| 1 | En `CLONAL`, el estadístico de BAF detecta desde fracciones bajas | Que no detecte ni al 20 % |
| 2 | En `VARIEGADO`, el estadístico de BAF **colapsa**: potencia próxima al azar a todas las fracciones | Que detecte igual que en clonal — la cancelación no sería real |
| 3 | En `VARIEGADO`, el índice de dispersión de cobertura **conserva potencia** | Que también colapse |
| 4 | El índice de dispersión **no** supera al BAF en el escenario clonal | Que lo superara en ambos — sería sospechoso |

**La #3 es la que decide.** Si el índice de dispersión no conserva potencia donde el BAF se
cancela, **no aporta nada** y se abandona.

> ### ⟵ CORRECCIÓN POSTERIOR · EXP-015c · el preregistro de arriba NO se ha tocado
>
> Todo lo anterior queda tal como se escribió, antes de ver los datos. Lo que sigue es el
> estado **actual**, y contradice en parte cómo se explicó el resultado.
>
> **Afirmación original:** el desplome de potencia del estadístico de BAF **sitio a sitio y
> absoluto** se debe a la cancelación entre linajes.
> **Resultado: FALSADA.** El estadístico es `abs(alt/dp − 0,5)`, un valor absoluto, y es
> **ciego al signo**: la aleatorización de homólogo no puede moverlo. La ablación 2×2 de
> `src/mosaic/ablation_baf.py` —una ablación **diagnóstica post-hoc**, diseñada después de que
> la auditoría encontrara el problema y por tanto **no preregistrada**— no encuentra evidencia
> de efecto de la dirección: 0,520 y 0,505 con la profundidad igualada, que a 200 repeticiones
> es el mismo resultado. Lo que produce el desplome es que el brazo
> aneuploide se simula a mayor profundidad, porque la copia extra sube la cobertura a (2+f)/2 y
> `|BAF−0,5|` encoge con la profundidad. La pista estaba en el propio número: **0,000 está por
> debajo de alpha = 0,05**, y la predicción #2 de arriba había escrito *«potencia próxima al
> azar»*, no cero.
>
> **Lo que sobrevive:** las mezclas balanceadas de homólogos **sí** recentran el BAF agregado
> **con signo** hacia 0,5. Sobre el estadístico con signo la potencia cae de **0,980 a 0,050**
> al mezclar la dirección, y la profundidad no lo mueve. La predicción #2, leída sobre el
> estadístico correcto, se cumple.
>
> **Lo que sigue sin resolver:** si un detector de WGS bulk clínicamente útil puede explotar la
> dispersión residual o una señal con fase en MVA. `EXP-015b` sigue **`UNVALIDATED · PARKED`**.
> El estadístico normalizado por la varianza binomial esperada elimina el confundido *en
> simulación*: elimina la sensibilidad a la profundidad que se observa en el estadístico de
> desviación absoluta. Lo que sostiene la lectura es el patrón conjunto de la ablación, no ese
> estadístico por sí solo, y nada de esto es un detector.
>
> **La profundidad no era un fallo de codificación.** Con una ganancia cromosómica real, más
> copias producen más lecturas. El error fue comparar contra un nulo de otra profundidad un
> estadístico cuya varianza depende de ella. El confundido es entre **dirección de homólogo** y
> **profundidad dependiente del número de copia**.
>
> Detalle completo en `docs/MOSAIC_SIMULATION.md`.

### Regla de decisión, fijada ahora

| Resultado | Qué se hace |
|---|---|
| El índice de dispersión conserva potencia en `VARIEGADO` donde el BAF colapsa | Queda justificado **mecanísticamente**, y sube de `L1` a hipótesis metodológica sostenida por simulación. **Nunca a «enormemente más potente»** |
| No la conserva | **Se reporta que perdió** y se usa únicamente el método estándar. El índice se archiva |

### Lo que esta simulación NO puede hacer

- **No demuestra nada sobre el paciente.** Es un modelo con supuestos.
- **No sustituye a MoChA sobre datos reales**, que sigue necesitando controles procesados con
  pipeline idéntico — y ésos **no existen**, así que la rama aplicada sigue **BLOQUEADA**.
- No modela sesgo de GC, mapabilidad ni sesgo de alelo de referencia, que a 44× son el factor
  limitante real. La potencia simulada será por tanto **optimista** frente a la real.

---

## EXP-021 · Los tres competidores de `A0` — **NEGATIVE**, resuelto localmente

**Fecha:** 2026-08-31. Resuelto **sin transmitir ninguna coordenada del paciente**.

### Cómo se resolvió

Que no aparecieran en la salida de Exomiser **no demostraba nada**: pudo excluirlas por
frecuencia, efecto, herencia o calidad, y cada motivo significa algo distinto. Había que
recuperar el motivo, no inferirlo.

La corrida permisiva completa se pasó del presupuesto de esfuerzo declarado. Se cambió a un
**VCF mínimo con solo esas tres variantes**, procesado por Exomiser en **0,9 s** contra su
base de frecuencias local ya descargada.

### El resultado

| Gen | rsID | Frecuencia poblacional | Homocigotos en gnomAD |
|---|---|---|---|
| `CTU2` | conocido | 62–93 % | **313 150** (NFE exomas) |
| `PEX5` | conocido | 30–66 % | **12 885** (NFE genomas) |
| `SLC22A1` | conocido | 58–78 % | **183 501** (NFE exomas) |

**Son polimorfismos comunes.** Cientos de miles de individuos son homocigotos para ellas.

> **Los rsID concretos no se escriben aquí.** A estas frecuencias no reidentifican a nadie —la
> mayoría de la población los porta—, pero `src/sanitize_scan.py` los marca y **un control que
> uno esquiva argumentando deja de ser un control**. Los identificadores están en
> `work/exomiser/runs/MINI/`, gitignored. Las frecuencias y los recuentos de homocigotos, que
> son el hallazgo, se conservan enteros.
Que este niño lo sea es lo esperado, no un hallazgo.

### La causa raíz, y es la misma de antes

Nuestro `MAX_AF` salió **vacío** para las tres porque **VEP no logró anotar la frecuencia de
esos indels**. Es la misma clase de fallo de representación de indels que hizo fallar el cruce
de alelos: la deleción se representa de una forma en el VCF y de otra en la base de
frecuencias.

La regla congelada trata `MAX_AF` ausente como raro. Con la frecuencia real, ninguna de las
tres habría entrado.

### QC de variante — para que conste que no eran llamadas malas

| Gen | QUAL | FILTER | GT | DP | GQ | AD | Transcrito |
|---|---|---|---|---|---|---|---|
| `PEX5` | 416,7 | PASS | 1/1 | 10 | 37 | 0,10 | MANE Select |
| `CTU2` | 1169,7 | PASS | 1/1 | 27 | 82 | 0,27 | MANE Select |
| `SLC22A1` | 2276,7 | PASS | 1/1 | 52 | 99 | 0,52 | MANE Select |

**Las llamadas son correctas.** El defecto no estaba en el genotipo sino en la anotación de
frecuencia. Es importante distinguirlo: descartarlas como «artefactos de llamada» habría sido
falso.

### Qué se hace con `A0` — y qué NO

**`A0` se reporta tal y como salió: `BUB1B` en el puesto 4.** No se edita.

Lo que se añade es el hecho medido: **los tres genes que lo superan son polimorfismos comunes
con rsID conocido**, así que `BUB1B` es el candidato de mayor puntuación **entre los
creíbles**. Las dos cosas se reportan juntas y el lector saca su conclusión.

**No se tocan los pesos.** Corregir la frecuencia de tres variantes elegidas porque estorban
sería exactamente el sesgo que el preregistro prohíbe.

## Preregistro — `A0-FREQFIX`, análisis de SENSIBILIDAD

**Escrito antes de ejecutarlo.**

Un arreglo legítimo del defecto de anotación **debe aplicarse a TODAS las variantes**, no a
las tres incómodas. Son **33 alelos** en todo el conjunto los que carecen de `MAX_AF`
(0,2 % del total; 1,8 % de los indels).

**Qué se hace:** recuperar la frecuencia de esos 33 desde la base local de Exomiser, y
recalcular `A0` **como análisis de sensibilidad etiquetado**, nunca como sustituto.

| Resultado | Lectura |
|---|---|
| `BUB1B` vuelve al puesto 1 | El defecto de anotación explicaba el cambio. **Se reportan los dos números**: `A0` = 4, `A0-FREQFIX` = 1 |
| `BUB1B` sigue por debajo | Hay competidores reales que no habíamos visto. Se auditan igual que estos tres |

**Prohibido** presentar `A0-FREQFIX` como si fuera `A0`. El preregistro de EXP-006 congeló
`A0`, y `A0` es lo que salió.

### Resultado de `A0-FREQFIX`

| | |
|---|---|
| Alelos sin `MAX_AF` reparados | **22 de 33** (los 11 restantes tampoco están en la base de Exomiser) |
| Criterio de aplicación | **A los 33**, no a una selección |
| `BUB1B` en `A0` **congelado** | **puesto 4** |
| `BUB1B` en `A0-FREQFIX` | **puesto 1** |

> ### PROCEDENCIA — `A0-FREQFIX` NO es una línea de evidencia independiente
>
> La reparación de frecuencias usó **la base local de Exomiser**. Eso significa que
> `A0-FREQFIX` **comparte fuente de frecuencia con el baseline externo** y ya no puede
> contarse como una comprobación independiente de él.
>
> **Prohibido presentar «`A0-FREQFIX` #1» y «Exomiser #2» como dos convergencias
> independientes.** La convergencia externa fuerte se evalúa contra el **pipeline congelado**
> y contra el resto de las líneas —conservación, estructura, modelo de herencia—, no contra
> una sensibilidad que bebe de la misma fuente.

**Los dos números se reportan siempre juntos.** `A0` es el resultado preregistrado y no se
sustituye. `A0-FREQFIX` responde a la pregunta acotada de cuánto de ese resultado lo explicaba
un defecto de anotación conocido: **lo explicaba entero**.

Los tres genes que desplazaban a `BUB1B` desaparecen del top-8 al aplicarles su frecuencia
real. Ninguno era un competidor.

**Deuda técnica registrada:** la anotación de frecuencia de indels con VEP falla en el 1,8 %
de los indels de este conjunto. Una v2 del pipeline debería cruzar frecuencias por identidad
de alelo, igual que ya se hace con el genotipo. No se hace ahora porque cambiaría un
componente congelado a mitad de análisis.

---

## EXP-016b · Puente 7 — cerrado como `UNRESOLVED`, con contraevidencia

**Búsqueda acotada, cerrada.** Se buscó evidencia de que la coinducción **farmacológica** de
HSP reproduzca el rescate obtenido por aumento **genético** en células aneuploides.

| Clase | Encontrado |
|---|---|
| **DIRECT** — aneuploides + coinductor + rescate | **NINGUNA** |
| **NEAR** — coinducción en otro contexto proteotóxico | Sí (E20) — **no se admite como sustituto** |
| **GENETIC** — solo sobreexpresión | Sí — es toda la evidencia del puente 6 |
| **CONTRADICTORY** | **Dos, verificadas (E18, E19)** |

**Cierre:** `UNRESOLVED — no direct pharmacological bridge found`. La búsqueda se detiene aquí
por la regla acotada, no porque se haya agotado la literatura mundial.

### La contradicción interna que esto destapó

`docs/01_MASTER_BRIEF.md` §10.3 y `docs/02_ANALYSIS_PLAN.md` sostenían: *«lo que mantiene la
hipótesis viva es que es coinductor **dependiente de estrés**, no activador constitutivo»*.

Ese argumento **sigue en pie como seguridad** y **ha dejado de ser neutro como eficacia**: la
vía dependiente de estrés es exactamente la que está al 50–60 % en células aneuploides (E19).
El fármaco actuaría a través del nodo averiado.

**Los dos textos originales NO se reescriben.** Se anotaron in situ, igual que se hizo con la
explicación falsada de REVEL. Es la tercera vez que el proyecto falsa una explicación propia y
la conserva anotada; ese patrón es parte del entregable.

### Lo que esto le hace a Track 2

**No mata T2-B. Cambia qué habría que buscar.** Para una célula con inducción de HSR
deficiente, la clase farmacológica adecuada probablemente **no** es un coinductor dependiente
de estrés, sino algo que **puentee** el nodo deficiente.

Y convierte el puente 7 en el **corazón falsable** del proyecto:

> *The central translational uncertainty is whether pharmacological co-induction reproduces the
> rescue obtained by genetic HSP augmentation — in cells whose HSF1-dependent induction is
> itself impaired.*

**Sigue sin haber nominación de fármaco.** La compuerta exige cinco condiciones y hoy ninguna
candidata reúne las cinco, porque los puentes 7 y 8 no están cerrados a favor.


---

## AUDITORÍA TRANSVERSAL · lo que se creía sobre Track 2, y qué lo falsó

**Estas formulaciones estaban en documentos canónicos y se han SUSTITUIDO allí.** Se conservan
aquí, que es donde vive el rastro: un documento que un jurado lee como estado actual no puede
llevar la afirmación vieja y la corrección debajo — eso parece incoherencia, no rigor.

| Lo que se creía | Dónde estaba | Qué lo falsó o estrechó |
|---|---|---|
| *«**Arimoclomol.** La nominación es específica de mecanismo»* | brief §10.1 | **Se nomina una cartera experimental, no un ganador terapéutico.** La compuerta exige cinco condiciones y ninguna candidata las reúne: los puentes 7 y 8 no están cerrados a favor |
| *«muy buena hipótesis farmacológica, no rescate demostrado»* | brief §10.2 | El puente 7 está `UNRESOLVED` **con contraevidencia en otro sistema humano** (E18): la sobreexpresión genética de HSP70 rescató y el coinductor no, sin inducir HSP70 |
| *«Lo que mantiene la hipótesis viva: es coinductor **dependiente de estrés**»* | brief §10.3, plan §306 | La inducción HSF1-dependiente está al **50–60 %** en células aneuploides (E19). El mismo rasgo es **razón** (identifica el nodo) y **pasivo** (hace incierta la amplificación). Es una tensión, no una refutación |
| *«mtDNA-CN del paciente»* | arquitectura, contrato visual | El piloto es un **prototipo con k-meros** sin excluir NUMT. La formulación vigente es *naive mtDNA-equivalent estimate bajo los supuestos del piloto* |
| *«MECHANISTIC CONVERGENCE»* | **figura hero** | El propio brief §5 prohíbe esa frase: con n=1 bulk son dos observaciones compatibles, no una regresión. Vigente: **consistency check** |

**Ninguna de estas ideas era inútil.** Todas eran la mejor lectura con la evidencia de su
momento, y el proyecto las mejoró. Ese recorrido es parte del entregable — **en este documento**.

---

## EXP-023 · Caracterización post-congelación con AlphaGenome: ISM y mapas de contacto

**Fecha:** 2026-09-07. **Estado de la ciencia:** congelada; esta entrada no la reabre.

### Qué se preregistró, y antes de qué

Antes de la primera llamada al modelo se escribió y selló con `sha256` un manifest
(`work/alphagenome/run_manifest.json`, gitignored porque lleva el locus) que fija **todo** lo
que se podría haber elegido después de ver un resultado:

| Parámetro | Valor congelado | Por qué ese y no otro |
|---|---|---|
| Candidato | el mismo de EXP-009, resuelto desde la caché congelada, nunca escrito a mano | es el único que el notebook 04 evaluó; ningún otro se busca |
| Gate de ensamblado | build GRCh38 declarado en `config/paths.yaml`; longitudes de contig del VCF; base REF leída del FASTA GRCh38 local de la caché de VEP; identidad REF/ALT en el VCF | la API acepta un REF sin validar; el gate no |
| ISM | ventana 256 pb, contexto 16 kb, 768 sustituciones sintéticas | la escala del tutorial oficial; sintéticas: sale el locus, no un genotipo |
| Lectura primaria | *splice sites*, `CenterMaskScorer` 2 001 pb, `DIFF_MEAN`, escalar = pista de mayor \|score\| de las 4 | la modalidad que decidió EXP-009; el ancho soportado más pequeño que cubre el vecindario |
| Lectura secundaria | *DNase*, `CenterMaskScorer` 501 pb, `DIFF_MEAN`, pista `CL:0001059` | la pista ya congelada en el bloque suplementario por la regla `base ≥ 0,01` |
| Chequeo de contexto | 100 kb, mismos scorers | se reporta; nunca sustituye al primario |
| Regla de lectura ISM | «concentrada» si el candidato queda en el 5 % superior de posiciones por \|efecto\| | escrita antes de mirar |
| Contactos | 1 Mb, 2 048 pb/bin, biosample **fibroblasto primario de piel** (`CL:0002620`) | el tipo celular de los estudios funcionales de PCS/MVA; no tumoral, no embrionario, no linfoide; elegido de las 28 pistas **antes** de predecir |
| Regla de lectura contactos | «visible» si max \|ALT − REF\| ≥ 5 % del máximo de REF | escrita antes de mirar |
| Semilla | `null` | la inferencia no tiene componente aleatorio; escribir 42 sería decorativo |

**Una re-congelación, declarada.** El primer manifest declaró 102 400 pb para el chequeo de
contexto; el SDK sólo admite 131 072. Se borró y se volvió a sellar con 131 072 **antes** de
cualquier llamada. Nota en `work/alphagenome/run_manifest.NOTA.txt`.

### Qué salió

| Salida | Resultado observado | Lectura permitida | Lectura prohibida | ¿Cambia la ciencia congelada? |
|---|---|---|---|---|
| ISM, primaria (*splice sites*) | candidato en la posición **62 de 256** por \|efecto\|; sustitución **251 de 768**; el máximo de la ventana a **+125 pb** | *no concentrated local ISM sensitivity at the candidate under the pre-specified readout* | «la región no es funcional» · «la variante es benigna» | **NO** |
| ISM, secundaria (*DNase*) | posición **168 de 256**; sustitución **268 de 768**; máximo a **−109 pb** | idem, en la lectura de accesibilidad | «no hay efecto en ningún tejido» | **NO** |
| Chequeo de contexto | r(16 kb, 100 kb) = **0,95** (primaria), **0,98** (secundaria) | la atribución **no** depende del contexto | — | **NO** |
| Contactos, `CL:0002620` | max \|ALT − REF\| = **1,09 %** del máximo de REF (umbral 5 %); matrices 512×512 simétricas, Δ exacto | *no compelling predicted contact effect* | «la cromatina del paciente no cambia» · «no hay bucle enhancer-promotor» | **NO** |
| Robustez, 28 pistas | la predeclarada ocupa el puesto **8 de 28** con el scorer oficial | la elección no fue un valor atípico | usar la distribución para elegir otra pista | **NO** |

Los dos negativos **se publican** (Regla Dura 6): figuras `fig04I_alphagenome_ism` y
`fig04C_alphagenome_contact_maps`, clase `MODEL_OUTPUT`, origen `PREDICTED`, con su ficha en
`PUBLICATION_FIGURE_QA.md`.

### Lo que este bloque NO hace

No sube la VUS, no mueve `A0`, no reabre Track 2, no busca otra variante y no convierte una
predicción en evidencia del paciente. Lenguaje obligatorio: *AlphaGenome predice…*, *bajo la
lectura predeclarada…*. `src/verify.py` (control *AlphaGenome model outputs*) y
`tests/test_alphagenome_model_outputs.py` atan figura → JSON → corrida → manifest, y fallan si
alguien cambia scorer, ontología, ventana o ensamblado sin volver a sellar a propósito.

---

## EXP-024 · Preregistro: calibración del score de AlphaGenome y panel tejido × modalidad

**Fecha:** 2026-09-07, revisado el mismo día tras la primera revisión del mantenedor.
**Estado:** **PREREGISTERED, NOT EXECUTED.** Ninguna variante del null, ningún control y ninguna
celda del panel se ha puntuado. Los sellados anteriores (NULL-A `ed8e1f16…`; v2 `ac572937…`/`4eebb2c2…`/`73c78821…`) quedaron
**superados antes de puntuar nada** y se conservan en `work/alphagenome/calibration/superseded/`.

**Orden acordado:** este preregistro se commitea solo (commit A, sin resultados). Después va el
alineamiento de profundidad completa (EXP-012, EXP-014a-v2). EXP-024 se ejecuta **una sola vez**, en
un commit B, y sólo si tras esos resultados sigue respondiendo una pregunta relevante.

### P0 · aclaración sobre EXP-023, sin reescribirlo

Las dos reglas de lectura de EXP-023 («5 % superior de posiciones» en la ISM; «max |ALT − REF| ≥ 5 %
del máximo de REF» en contactos) son **reglas de decisión internas**, predeclaradas para impedir el
cherry-picking. No son umbrales validados por la literatura ni niveles de significación, y no se
convertirán en un «p < 0,05» implícito. La correlación 16 kb frente a 100 kb (0,95 y 0,98) se
describe como *robust to the two tested sequence-context lengths*, nunca como «descarta un
artefacto de ventana». Los picos de la ISM a −85 y +109/+125 pb se anotan; no hay búsqueda de
motivos ni análisis post hoc.

### Conjuntos sellados, cada uno con su sha256

| Conjunto | Definición | n | sha256 |
|---|---|---|---|
| **NULL-LOCAL** | transiciones sintéticas del **mismo entorno del locus**: a ≤ 5 000 pb del candidato, intrónicas, a ≥ 1 000 pb de cualquier borde de exón (la clase «intrónica profunda» del candidato), fuera de la ventana ISM y de CTRL-POS; seleccionadas sólo con rasgos independientes del modelo; semilla 42 | **100** de 1 901 elegibles | `b02d47b8616031a5…` |
| **NULL-TRANSCRIPT** | transiciones intrónicas profundas de **todo el transcrito** (≥ 1 000 pb de exón, fuera de la ventana ISM); misma familia de regla y misma semilla que NULL-A, pero el pool se calcula ahora de forma uniforme y la muestra **no** es idéntica byte a byte a NULL-A | **300** de 27 062 | `f620a1ca2b1b945a…` |
| **CTRL-POS** | las cuatro posiciones canónicas de splicing de cada intrón (donante +1/+2, aceptor −2/−1), mutadas a su transición | **88** (22 intrones) | `ba39386752df0031…` |
| **PANEL** | seis contextos externos × seis modalidades, scorers recomendados oficiales, 1 Mb | 6 × 6 | `05f5aaa3eb5691fc…` |
| índice del preregistro | contrato de puntuación, familias, estadística y reglas de lectura | — | `e9435538824ce722…` |

**Rasgos del candidato, independientes del modelo:** transición A>G, intrón 20 de 22, a 1 026 pb
del exón más cercano, GC del entorno de 101 pb = 0,26. Anotación de la pasada 1 de VEP sellada:
`intron_variant` de `BUB1B` en el transcrito MANE (intrón 20/22), y `upstream_gene_variant` de un
transcrito vecino de `PAK6`. **`candidate_annotation_class = deep_intronic`** ·
**`NULL-LOCAL annotation_class_match = true`**. La anotación de gen vecino no es una dimensión
emparejada y así consta.

**NULL-LOCAL no es «fully matched», y se dice.** Emparejado: clase de sustitución, intrónico,
intrónico profundo, mismo entorno (≤ 5 kb). No emparejado: distancia exacta al exón (el pool va
de 1 016 a 2 004 pb), lado de la hebra (las 100 posiciones quedan aguas arriba, por geometría del
locus) y GC local (se reporta, no se empareja).

### Sensibilidad, por lectura

| Lectura | Calibración de sensibilidad | Lo que un no-significativo puede decir |
|---|---|---|
| splice (primaria) | **CTRL-POS** | depende de la potencia medida |
| DNase (secundaria) | **UNCALIBRATED FOR SENSITIVITY** (no hay conjunto positivo externo defendible sin curación nueva) | sólo *not unusually extreme under the preregistered null* |
| contacto (global) | **UNCALIBRATED FOR SENSITIVITY** | ídem |

La potencia de CTRL-POS **no se propaga** a DNase ni a contactos.

### Familias

**CONFIRMATORY FAMILY = {splice-primary, DNase-secondary, contact-global}.** Exactamente tres
hipótesis; Benjamini-Hochberg sólo entre ellas, con NULL-LOCAL como null primario y
NULL-TRANSCRIPT reportado al lado. **La matriz tejido × modalidad es PRE-SPECIFIED EXPLORATORY /
DESCRIPTIVE**: sus percentiles por celda son descriptivos; ninguna celda se convierte en «significant»
con el q de la familia de tres; ninguna se elige después de ver los scores.

### Estadística

percentil = 100·#{|S_null| < |S_cand|}/N · p_emp = (1 + #{|S_null| ≥ |S_cand|})/(N+1) ·
z robusto = (S_cand − mediana)/(1,4826·MAD). **MAD degenerado** (MAD = 0 o MAD < 10⁻⁶·max|S_null|):
z = *undefined (degenerate null spread)*, se reporta la fracción de nulls exactamente iguales a 0 y
quedan percentil y p_emp como únicos resúmenes. Potencia = fracción de CTRL-POS con p_emp < 0,05
en splicing.

### Contrato de puntuación idéntico (invariante)

candidato == null == controles en: longitud de contexto (16 kb para las dos lecturas de la ISM de
EXP-023, 1 Mb para contactos y panel), scorer, ontología, tratamiento de hebra, máscara central,
agregación escalar, normalización REF/ALT y manejo de salidas ausentes. Una variante que no cumpla
el contrato exacto (error de la API tras 3 reintentos, NaN, pista ausente) **se excluye bajo esta
regla escrita** y se registra el motivo; si las exclusiones superan el 5 % de un conjunto, la corrida
se marca `INCOMPLETE` y no se interpreta.

### Lecturas obligatorias

| Resultado | Lectura |
|---|---|
| q ≥ 0,05 | *not unusually extreme relative to the preregistered null* |
| q < 0,05 | *unusually extreme relative to the preregistered null*: se registra como **contradicción concreta** para adjudicación; **no cambia por sí sola** clasificación, ranking ni rama |
| potencia(splice) < 0,5 | la lectura de splicing no es sensible en este gen; el resultado del candidato en esa lectura se declara **no informativo** |
| panel | descriptivo: *tissue-restricted* si max \|score\| ≥ 3 × mediana \|score\| en la modalidad; en otro caso *broadly consistent (weak or no predicted effect)* |
| prohibido | *negative*, *benign*, *non-functional*, *no regulatory effect*; y cualquier lectura de percentil, p o z como probabilidad de patogenicidad o evidencia ACMG |

**Techo de interpretación.** EXP-024 calibra la salida de AlphaGenome. No calibra patogenicidad,
no reclasifica la VUS, no demuestra ausencia de segundo alelo, no demuestra que el locus carezca de
función y no convierte contactos predichos en cromatina del paciente. El resultado de AlphaGenome
sigue siendo: *The only rare noncoding candidate surviving locus-level filtering was not supported
by global or track-level AlphaGenome predictions.* EXP-024 sólo puede añadir: *and its
pre-specified model scores were / were not unusually extreme relative to defined computational
null distributions.*

**Panel: contextos externos del modelo.** No patient transcriptome, epigenome, chromatin profile or
cell-specific functional assay is available. Psoas y riñón son *phenotype-motivated contexts*, no
tejidos afectados del paciente; fibroblasto es *literature-motivated MVA functional context*;
CD34+ es *proliferative hematopoietic context*; sangre mononuclear, tejido de origen del WGS si
aplica; hígado, *predeclared unrelated comparator*.

### Jerarquía de figuras (ninguna sube por parecer llamativa)

| Figura | Categoría | Qué es |
|---|---|---|
| `fig04Q_alphagenome_calibration` | **MAIN** diagnóstica del bloque AlphaGenome | ECDF/null + candidato + controles, percentil, p y q |
| `fig04C_alphagenome_contact_maps` + panel E | secundaria / principal mecanística de salida de modelo | A–D intactos; E = `ContactMapScorer` del candidato frente a NULL-LOCAL |
| `fig04T_alphagenome_tissue_matrix` | **SUPPLEMENTARY**, contexto exploratorio preespecificado | seis contextos × seis modalidades, celdas ausentes visibles |
| `fig04L_alphagenome_ism_logo` | **SUPPLEMENTARY** | *ISM-derived local sensitivity logo* desde la matriz ya congelada; nunca «motif» |

Los nueve campos (QUESTION, INPUT, METHOD, RESULT, SUPPORTED CLAIM, FORBIDDEN CLAIM, PROVENANCE,
REPRODUCTION COMMAND, TEST) de cada una se rellenan en `PUBLICATION_FIGURE_QA.md` cuando existan;
una figura que no pueda llenar los nueve no entra.

### Lo que no cambia

No se reabre `BUB1B`, no se reclasifica la VUS, no se toca `A0`, no se busca fármaco, no se cambia
Track 2. La clave de la API no se rota hasta que el mantenedor lo indique.

---

## EXP-012 / EXP-014a-v2 · Preregistro del alineamiento de profundidad completa

**Fecha:** 2026-09-07, revisado tras la segunda revisión del mantenedor. **Estado:** **PREREGISTERED,
NOT EXECUTED.** Los ocho FASTQ de las cuatro lanes están en la máquina replicada; nada se ha
descargado ni alineado. Se ejecuta una vez, con estos parámetros, tras el GO explícito.

### Referencia: dos objetos, con procedencia separada

El VCF del proveedor declara `GCA_000001405.15_GRCh38_no_alt_analysis_set_plus_hs38d1_maskedGRC_exclusions_v2_no_chr`
y sus contigs lo confirman: 1–22, X, Y, M, contigs `_random`, `Un_*_decoy` (hs38d1), `EBV`, sin
prefijo `chr`. Fuente primaria: el conjunto canónico de NCBI
`GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz` (md5 publicado
`a056c57649f3c9964c68aead3849bbf8`). **No se enmascara ni se reconstruye la secuencia.**
`GRC_exclusions.bed` no es una instrucción para alterar el FASTA.

| Objeto | Qué es | Procedencia |
|---|---|---|
| `source_reference_fasta` | el FASTA de NCBI **preservado byte a byte** | sha256 y md5 propios; el md5 se compara con el publicado |
| `runtime_reference_fasta` | una **copia** con los identificadores de contig renombrados (`chr1 → 1`, `chrM → M`, `chrEBV → EBV`, `chrUn_*_decoy → Un_*_decoy`) para coincidir con el VCF | sha256 y md5 propios, `.fai` construido por `src/wgs/reference_prepare.py`, mapa explícito de cabeceras, `sequence_content_changed = false` (comprobado con un sha256 por contig de la secuencia en ambos ficheros), `header_names_changed = true` |

*The NCBI source FASTA is preserved byte-for-byte. A separate runtime FASTA changes contig
identifiers only; nucleotide sequence is unchanged.* El runtime **no** se describe como «sin
modificar»: cambia como fichero, no como secuencia, y los dos checksums se registran para que nadie
tenga que preguntar cuál se usó para alinear (el runtime).

### Gates de referencia, antes de alinear una sola lectura (`src/wgs/reference_gate.py`)

| Gate | Regla exacta | Si falla |
|---|---|---|
| 1 | procedencia: md5 del *source* == el publicado por NCBI; `sequence_content_changed = false`; sha256 del *runtime* == el del fichero presente | STOP |
| 2 | **todo contig declarado por el VCF existe en el runtime FASTA**; contigs adicionales del FASTA se permiten **sólo si están predeclarados** (lista `PREDECLARED_EXTRA_CONTIGS`, hoy vacía); cualquier otro extra es fallo | STOP |
| 3 | cada contig del VCF tiene **longitud idéntica** en el runtime | STOP |
| 4 | concordancia REF genoma completo: 20 000 variantes PASS muestreadas de todo el VCF con semilla 42, `reference[pos] == REF` en **todas** | STOP |
| 5 | concordancia REF en BUB1B ± 1 Mb: **todas** las variantes PASS | STOP |
| 6 | decoys hs38d1 y EBV presentes, como espera el VCF | STOP |

*Every VCF-declared contig must exist in the runtime FASTA with identical length. Additional
predeclared reference contigs are permitted.* Contig ausente, longitud distinta o REF distinta =
STOP. Con los seis en PASS el gate se **reporta y se detiene**: el alineamiento no arranca solo,
espera el GO explícito del mantenedor. Es un checkpoint separado: preregistro → referencia
validada → alineamiento.

### Contenedores: tag + digest inmutable + versión reportada

El identificador reproducible es el **digest** (un tag puede cambiar de contenido en el registro).
Resueltos desde el registro sin descargar capas (`src/wgs/container_manifest.py resolve`); la
versión que reporta cada herramienta se registra tras la descarga (`versions`) en
`work/align/containers.json`.

| Herramienta | Registro / repositorio | Tag | Digest linux/amd64 |
|---|---|---|---|
| bwa | `quay.io/biocontainers/bwa` | `0.7.18--he4a0461_0` | `sha256:a8ea7d74457b…` |
| samtools | `quay.io/biocontainers/samtools` | `1.21--h50ea8bc_0` | `sha256:783c6646029a…` |
| manta | `quay.io/biocontainers/manta` | `1.6.0--h9ee0642_2` | `sha256:021aabe5f731…` |
| delly | `quay.io/biocontainers/delly` | `1.3.3--h4d20210_1` | `sha256:67ea846395b2…` |
| cnvpytor | `quay.io/biocontainers/cnvpytor` | `1.3.2--pyhdfd78af_0` | `sha256:614b22c8fc1f…` |
| mosdepth | `quay.io/biocontainers/mosdepth` | `0.3.10--h4e814b3_1` | `sha256:94b54a6a5610…` |
| bedtools | `quay.io/biocontainers/bedtools` | `2.31.1--hf5e1c6e_2` | `sha256:38756b5ac5d0…` |

### Metadata de read group: lo que se lee, y lo que NO se infiere

`SM` sale de la columna 10 del VCF. `PU` es `{flowcell}.{lane}.{índice}`, con el índice mayoritario
de las primeras 2 000 lecturas de cada lane. **`LB` no se infiere del código de índice**: que las
cuatro lanes compartan índice demuestra que se demultiplexaron como la misma **muestra**, no que
vengan de una única preparación de **librería**. Se busca metadata de librería en la cabecera del
VCF y en los nombres de lectura; no existe (el propio brief tiene abierta la pregunta de si la
librería es PCR-free). Por tanto el campo `LB` **se omite** del `@RG`, que la especificación SAM
permite, y se registra *library identity unavailable from supplied metadata*. Consecuencia técnica,
comprobada: `samtools markdup` **no agrupa por `LB`** (a diferencia de Picard MarkDuplicates), así
que omitirlo no altera el marcado global de duplicados.

### Marcado de duplicados: alcance global, y la incertidumbre que eso deja abierta

Sin identidad de librería, el marcado global no es neutro y no se disfraza de neutro:

- si las cuatro lanes son de **una misma** preparación de librería, el marcado global es lo correcto;
- si son **librerías independientes**, el marcado global puede **sobremarcar**, tratando como
  duplicados fragmentos que vienen de moléculas distintas.

Como la identidad de librería **no está disponible**, la ausencia de metadata no se convierte en la
certeza implícita de «una sola librería». Se registra en el manifest, literalmente:

| Campo | Valor |
|---|---|
| `library_preparation_identity` | `unavailable` |
| `duplicate_marking_scope` | `global across all four lanes` |
| `duplicate_marking_assumption` | *lanes treated jointly for duplicate marking because library provenance is unavailable; this may overmark if lanes derive from independent library preparations* |

Y se conservan **los dos objetos**, ambos con su `sha256`: el BAM unido **antes** de marcar y el BAM
final marcado. El pre-markdup no se borra hasta que GO 2B haya terminado, de modo que siempre se
puede volver al objeto anterior a esa decisión. **La fracción de duplicados se interpreta como QC del
pipeline, nunca como una propiedad biológica de la muestra.** El propio manual de `samtools`
advierte que su estimación de tamaño de librería descansa en supuestos que pueden no cumplirse.

**Regla de objeto para GO 2B, para que esto no se convierta en dos pipelines:** *The globally
duplicate-marked BAM is the primary downstream alignment object. The pre-markdup BAM is retained
for technical adjudication only when a critical finding is plausibly sensitive to duplicate
handling.* Los llamadores **no** se ejecutan dos veces, con y sin marcado. Primario: el marcado.
Pre-markdup: recurso forense puntual.

### Orden de etapas por lane, explícito

`bwa mem` → `samtools collate -O` (agrupación por nombre **explícita**, sin asumir nada sobre el
orden de salida del alineador) → `samtools fixmate -m` → *coordinate sort*. Después: `merge` de las
cuatro lanes → `samtools markdup` **global** → `index`.

> **Corrida descartada y reiniciada a propósito, 2026-09-07.** Una primera ejecución llegó a
> completar L001 y 50 min de L002 antes de estas dos correcciones. Aplicarlas a mitad de corrida
> habría dejado lanes con procedencias distintas, así que se descartaron y se reinició la etapa 2
> con el código corregido y **commiteado antes de generar el BAM**. El preflight y el índice se
> conservaron porque no dependen de las correcciones. Sobre el L001 descartado se verificó que el
> 100 % de 2 000 000 de lecturas emparejadas llevaban `MC` y `ms`: `fixmate` había funcionado. El
> `collate` explícito es una **garantía**, no la corrección de un fallo observado. Aquella corrida
> consta como **technical pre-commit trial; excluded from all final analyses**, y no se conserva
> ningún BAM intermedio suyo.

### Alineador

**BWA-MEM 0.7.18 was selected as the short-read aligner because its memory requirements fit the
available system (62 GB host, 32 GB for Docker; the bwa-mem2 human index needs ~86 GB). No
bitwise-identity claim with bwa-mem2 is made.** Contenedor y digest en la tabla anterior.
Parámetros fijados: `-t 22 -K 100000000 -Y`, un read group por lane (`ID={flowcell}.{lane}`,
`PL=ILLUMINA`, `PU={flowcell}.{lane}.{índice}`, `SM` y `LB` = identificador de muestra; flowcell e
identificador viven en `work/`, nunca aquí). Después: `samtools fixmate -m`, `sort`, `markdup`,
`index` (`samtools` 1.21). Sin recorte de lecturas. Nada se ajusta después de mirar resultados.
Duración: **estimación** de 20–35 h en esta máquina, nunca una garantía.

### Gate de almacenamiento (`src/wgs/storage_gate.py`, cifras calculadas desde los FASTQ)

| | GB |
|---|---|
| FASTQ (8, medidos) | 78,9 |
| referencia + índice bwa | 9,7 |
| BAM ordenado pre-markdup (1,4 × FASTQ) | 110,4 |
| temporales de sort (1,0 × FASTQ) | 78,9 |
| BAM final markdup + índice (1,4 × FASTQ) | 110,4 |
| Manta + DELLY + CNVpytor + mosdepth + logs | 40,0 |
| **pico** | **349,3** |
| retenido tras limpieza | 160,1 |
| libre ahora | 1 616,1 |
| exigido (1,5 × pico) | 524,0 |

Temporal: `work/align/tmp`, mismo SSD. Limpieza: temporales de sort al terminar el sort; BAM
pre-markdup tras verificar el final (`samtools quickcheck` + `flagstat`); CRAM y borrado del BAM
sólo cuando Manta, DELLY, CNVpytor, mosdepth y MitoRead hayan terminado y sus salidas estén
hasheadas. Margen: **GO**.

### QC que se mide (no se asume)

Profundidad autosómica mediana y distribución; BUB1B ±50 kb y ±1 Mb; calidad de mapeo; fracción de
duplicados; distribución de tamaño de inserto; profundidad chrX/autosomas y chrY/autosomas;
heterocigosidad de chrX fuera de las PAR. El sexo se reporta sólo como *genomic sex concordance
consistent with the declared XY configuration*, nunca como confirmación de identidad. La
profundidad observada **se verifica**; el ~40× del VCF es la expectativa, no el resultado.

### EXP-012 · alelo estructural oculto: cuatro capas, con papeles distintos

| Capa | Herramienta (contenedor fijado) | Qué es |
|---|---|---|
| SV caller | Manta 1.6.0 | split reads + pares discordantes, genoma completo |
| SV caller ortogonal | DELLY 1.3.3 | segundo llamador independiente, genoma completo |
| CNV por profundidad | CNVpytor 1.3.2 | segmentación de número de copia (read depth, corrección GC), muestra única |
| Cobertura / QC | mosdepth 0.3.10 | **profundidad cruda y local; no es un llamador de CNV** |
| Adjudicación | revisión reproducible del locus | soporte a nivel de lectura sólo de los candidatos que sobrevivan |

Interrogación primaria de BUB1B ±1 Mb tras las llamadas genoma completo: extracción de todo evento
que interseque exones, intrones o región reguladora extendida, con split reads, pares discordantes y
profundidad normalizada. **Techo del negativo:** *No supported structural or copy-number second
allele was detected by the specified short-read WGS workflow; classes poorly accessible to short
reads remain unresolved.* Prohibido: *structural second allele excluded*.

### Fase

**No se ejecuta WhatsHap para unir los dos alelos principales.** Distancia 10 911 pb; el mayor hueco
entre heterocigotos puente es 6 769 pb; los fragmentos cortos miden ~400–500 pb. Se congela:
*Current short-read WGS cannot establish trans; parental DNA or a long-molecule phasing assay is
required.* `unphased ≠ trans` permanece.

### EXP-014a-v2 · MitoRead con alineamiento

*NUMT-aware mtDNA:nuclear coverage estimate*: profundidad de chrM con lecturas MAPQ ≥ 30 (y sin
filtro, para ver la diferencia), denominador autosómico robusto (mediana) y sensibilidad a
denominadores alternativos por cromosoma, bootstrap por ventanas de chrM si es viable. Wording
máximo: *NUMT-aware filtering / reduction of likely nuclear-mitochondrial mappings*; prohibido
«NUMTs excluded». Sigue siendo un *orthogonal WGS readout*, no prueba de disfunción mitocondrial, y
lleva el caveat de composición celular y plaquetas.

### Deuda técnica declarada durante la corrida

**Gate de sexo del GO 2A: FAIL preregistrado, adjudicado post hoc, no bloqueante.**
La regla exigía `chrY/autosoma > 0,25` sobre el contig completo y dio **0,170**, así que **falló y
se conserva como fallida**. El umbral **no se ha cambiado** después de ver el resultado. Registro
literal, fechado 2026-09-09:

```text
sex_check_preregistered = FAIL
sex_check_adjudication  = XY-consistent
sex_check_blocking      = false
reason:
  The preregistered whole-chrY/autosome threshold was misspecified because
  the denominator included large masked/unmappable portions of chrY.
  The threshold was not changed after observing the result.
support:
  chrX/autosome                     = 0.512
  chrX non-PAR heterozygosity       = 0.0127
  chrY covered-bases depth          = 22.8x
  chrX covered-bases depth          = 22.4x
  autosomal covered-bases depth     ≈ 44.4x
  chrY fraction of contig covered   = 31.1 %
future_rule:
  For future samples, define a callable-region or predefined Y-region metric
  before looking at sample results. Do not calibrate a new threshold from this patient.
```

**`QC-DEF-002` · un paso de QC fallaba en silencio y escribía un fichero vacío.**
La profundidad en la región de BUB1B no se calculó en la corrida del GO 2A: la mediana se pedía con
`asort()`, una extensión de GNU awk que el `mawk` del contenedor no tiene, y además el fichero de
regiones llevaba fin de línea de Windows, cuyo retorno de carro entraba dentro de la coordenada. El
paso devolvía un fichero **vacío sin fallar**, y sólo se detectó porque el campo apareció vacío en el
resumen final. **Corregido:** la mediana se calcula en Python y la etapa **aborta con ALTO** si el
fichero sale vacío. Clasificación del mantenedor: **`reporting/QC implementation defect; alignment unaffected`**. No se repite el alineamiento: el fallo estaba en el cálculo y el reporte de la profundidad regional, no en bwa, ni en el BAM, ni en el marcado de duplicados, y las cifras corregidas (45,31× en ±50 kb, 45,77× en ±1 Mb) se obtuvieron sobre **el mismo BAM**. *Un paso de QC que falla en silencio es peor que uno que no existe, porque el
resumen parece completo.*

**`QC-OPT-001` · el QC por grupo de lectura recorre el BAM entero varias veces.**
*Per-read-group QC currently performs multiple full BAM scans. Future runs should derive per-RG
statistics in a single traversal, e.g. `samtools stats --split RG` or equivalent validated one-pass
aggregation.*

Medido en esta corrida: cada recorrido completo del BAM de 60 GB tarda **1 h 6 min**, y el QC pide
un recuento por cada uno de los cuatro grupos de lectura, así que son cuatro recorridos donde
bastaría uno. El coste es de horas, no de ciencia: **ninguna métrica ni criterio cambia**.

La causa no es el disco. Medido durante la etapa: lectura de 14 MB/s con **latencia de 0,11 ms** en
un SSD NVMe, CPU al 7 % (≈ 1 hilo de 24) y 48 GB de RAM libres. El límite está en decodificar los
bloques BGZF, filtrar y contar cada registro, no en el hardware.

Verificado en el contenedor fijado (`samtools 1.21`): existen `-S, --split <tag>` y
`-P, --split-prefix <str>` en `samtools stats`, que producen estadísticas separadas por etiqueta en
**una sola pasada**. Nota sobre `-@`: la ayuda de 1.21 lo describe igual en `stats` y en `view`
(*number of additional threads*), así que **no se asume** que añadir hilos acelere un recuento
concreto; eso se mediría antes de fijarlo.

**No se corrige a mitad de corrida.** Cancelar con el recuento global y tres de las cuatro lanes ya
hechos, para ganar una hora en la cuarta, es exactamente la optimización que llega tarde. Se aplica
en la siguiente ejecución.

### Lo que se devuelve antes de interpretar

Manifest del alineamiento; hashes, versiones y referencia; QC completo; resumen de llamadas SV/CNV
sin sobreinterpretar; QC de MitoRead; y qué ramas pasan de BLOCKED a EXECUTED y cuáles siguen
abiertas. Nada del alineamiento ni de los intermedios genómicos entra en el repositorio. No se
modifica Track 1, la clasificación de variantes ni Track 2 hasta que esos resultados se adjudiquen.

---

## v5 · Alcance científico del WGS de profundidad completa: qué clases de variación se interrogan y qué significará cada resultado

**Fecha:** 2026-09-07, tras la tercera revisión del mantenedor. **Estado:** **PREREGISTERED, NOT
EXECUTED.** Ésta es la **última ampliación del preregistro antes de ejecutar**: después de v5 no se
añaden ramas nuevas salvo que aparezca evidencia nueva. v4 respondía «¿podemos reproducir
exactamente el pipeline?»; v5 responde «¿estamos interrogando las clases correctas de variación y
sabemos de antemano qué significará cada resultado?».

### 1 · CNVpytor = análisis bidimensional RD + BAF

`CNVpytor` no se limita a profundidad: combina profundidad de lectura (RD) con la frecuencia del
alelo B (BAF) de los SNP heterocigotos, y puede señalar desequilibrio alélico y LOH neutra en copia.
Salidas preespecificadas: RD normalizada, distribución de BAF, estado de copia (CN), desequilibrio
alélico, y LOH neutra en copia si el soporte lo permite. Interrogación primaria: BUB1B ± 1 Mb.
La pila de evidencia en el locus queda: RD normalizada + BAF de SNP heterocigotos + breakpoints de
Manta + breakpoints de DELLY + estado de CNVpytor.

### 2 · Rama de inserciones de elementos móviles (MEI)

Los retroelementos intrónicos son una clase mendeliana conocida que el SV calling estándar puede
no ver y que puede ser, literalmente, el alelo que falta en una enfermedad recesiva. No decirlo
sería dejar una clase fuera de «search for hidden second allele» sin declararlo.
Herramientas fijadas por digest (tabla al final): **xTea 0.1.9** como llamador primario para WGS
Illumina y **SCRAMble 1.0.2** como llamador ortogonal por clusters de lecturas recortadas; sus
recursos (bibliotecas de repeticiones) se descargan con el GO y se registran con hash.
Alcance, en este orden: genoma completo → locus extendido de BUB1B → genes de MVA y segregación
cromosómica → genes del fenotipo residual. Contrato de adjudicación: *Caller concordance increases technical support but is not required for
candidate retention. Discordant MEI calls are adjudicated using caller-specific QC, split/discordant-read
evidence and local alignment inspection.* Los dos llamadores se usan sólo si pasan sus gates de
compatibilidad de entrada y build. **Un negativo combinado NO excluye todas las inserciones
complejas**; algunas sólo se resuelven con análisis específico o lecturas largas.

### 3 · Adjudicación basada en lecturas de los dos alelos prioritarios de BUB1B

Con el BAM, los dos candidatos dejan de depender sólo del VCF del proveedor. Para cada uno se
preregistran: DP, AD de referencia y alterno, balance alélico, MAPQ, calidad de base, soporte
directo/reverso, recorte blando (soft clipping) y complejidad local (repeticiones e indels
cercanos). Un segundo llamador de variantes pequeñas (`bcftools` 1.21, mpileup/call) se ejecuta
sobre el mismo BAM y se etiqueta **`TECHNICAL REPLICATION FROM THE SAME READS`**, nunca evidencia
independiente. Frase máxima si sobreviven: *Both prioritized BUB1B variants were independently
recovered from the reconstructed full-depth alignment and survived read-level QC.* Si uno no
sobrevive, se reporta igual y con la misma visibilidad.

### 4 · Comprobación explícita del alelo regulador histórico de BUB1B

En PCS/MVA ya ocurrió lo que este caso tiene: un solo alelo de BUB1B visible y, más tarde, una
variante intergénica ~44 kb aguas arriba que reducía BUB1B y reproducía PCS/MVA experimentalmente
(Ochiai H et al., *Proc Natl Acad Sci USA* 2014;111(4):1461-6, **PMID 24344301**, verificado en
esta sesión vía NCBI E-utilities el 2026-09-07). **No se escribe aquí ninguna coordenada GRCh38**:
durante la ejecución se recupera el build y la coordenada original del artículo, se documenta el
liftover si hace falta, se comprueba REF y sólo entonces se clasifica. Fila preregistrada, fuera del filtro genoma completo: la coordenada exacta se toma del
texto del artículo en el momento de ejecutar, se convierte a GRCh38 con liftover documentado, y se
interroga (a) la variante publicada y (b) toda variante rara, SV o MEI en la misma región
reguladora aguas arriba (ventana ±50 kb del inicio del gen), con estados permitidos:
**`PRESENT / ABSENT / TECHNICALLY UNRESOLVED`** (este último si la cobertura MAPQ ≥ 20 en la región
es < 20×).

### 5 · Integridad de la muestra y del alineamiento

El QC del BAM incluye: concordancia de genotipos BAM↔VCF (`bcftools` sobre 20 000 sitios PASS
muestreados con semilla 42), estimación de contaminación (`VerifyBamID2` 2.0.3), tasa de mapeo,
fracción de pares propiamente apareados, fracción de duplicados, distribución de tamaño de
inserto, **los cuatro read groups esperados**, uniformidad de cobertura autosómica, profundidad
X/autosomas e Y/autosomas, heterocigosidad de chrX fuera de las PAR. **Claim máximo:** *The
reconstructed alignment is technically concordant with the supplied variant dataset.* No es prueba
de identidad.

### 6 · Expansiones de repeticiones (P1, nunca P0)

`ExpansionHunter` 5.0.0 sobre su catálogo de loci patogénicos establecidos como **cribado**, pero
**sólo se interpreta el locus con conexión fenotípica preregistrada**: `DMPK`. *DMPK is retained as a
phenotype-driven P1 repeat-expansion screen because congenital/childhood DM1 can include hypotonia and
muscle weakness; this is a residual/second-diagnosis screen, not an MVA-causal hypothesis.* Atrofia
muscular y problemas de crecimiento por sí solos no hacen plausible la DM1: por eso es cribado P1. `CNBP` se excluye
a propósito: la DM2 no tiene formas congénitas ni de inicio infantil, y «atrofia muscular» sola es
una conexión demasiado ancha. No se añade ningún otro locus salvo que, **antes de ejecutar**, exista
un término HPO o antecedente clínico específico que lo justifique. Cualquier otra expansión es
incidental, no se reinterpreta y no reabre nada. Toda llamada positiva requiere
QC e inspección visual reproducible y se considera *screening evidence*. Sitio en la jerarquía:
fenotipo residual / segundo diagnóstico.

### 7 · Gate de escalado a lecturas largas, congelado ahora y no después de un negativo

*If no supported second structural/regulatory allele is detected by short-read WGS, phase remains
unresolved, and BUB1B remains the leading causal hypothesis, long-molecule phasing / long-read
sequencing becomes the highest-value next genomic experiment.*

### 8 · Techo de MitoRead

*Without CBC/platelet/cell-composition data, the result is a cell-composition-unadjusted
WGS-derived blood mtDNA:nuclear ratio.* Con hemograma se puede ajustar e interpretar algo mejor.
Nunca: *mitochondrial dysfunction demonstrated*.

### 9 · Niveles de priorización genoma completo, fijados antes de llamar

| Tier | Alcance |
|---|---|
| 1 | locus extendido de BUB1B |
| 2 | genes establecidos de MVA y segregación cromosómica |
| 3 | genes del fenotipo residual / segundo diagnóstico |
| 4 | SV/CNV/MEI de alto impacto genoma completo |

**Ningún evento de Tier 4 sube a candidato causal sólo por rareza.**

### 10 · Figura preregistrada: BUB1B locus evidence stack

`fig04R_bub1b_locus_evidence_stack`, clase `DATA`, origen `MEASURED+DERIVED`: sobre **el mismo eje
genómico**, estructura del gen y contexto regulador, candidatos SNV/indel, RD normalizada, estado de
CNVpytor, BAF, pares discordantes, split reads, llamadas de Manta, de DELLY y de MEI. Se genera
**sólo** desde los datos ejecutados, nunca desde un mockup; si no aparece ningún evento se publica
como evidencia negativa/suplementaria. Su ficha QA rellena los nueve campos o no entra.

### Contenedores añadidos en v5 (tag + digest inmutable; versión reportada tras el pull)

| Herramienta | Repositorio | Tag | Digest linux/amd64 |
|---|---|---|---|
| bcftools | `quay.io/biocontainers/bcftools` | `1.21--h8b25389_0` | `sha256:969314d56b91…` |
| verifybamid2 | `quay.io/biocontainers/verifybamid2` | `2.0.3--hc004090_0` | `sha256:7f8b271e644c…` |
| expansionhunter | `quay.io/biocontainers/expansionhunter` | `5.0.0--hf366f20_1` | `sha256:a3a227b4c765…` |
| xtea | `quay.io/biocontainers/xtea` | `0.1.9--hdfd78af_0` | `sha256:0855c844a4e6…` |
| scramble | `quay.io/biocontainers/scramble` | `1.0.2--hec16e2b_0` | `sha256:68d1452fa2ca…` |

### Condición de parada

Tras v5 se commitea el preregistro completo, todavía sin descargas, sin alineamiento y sin puntuar
EXP-024. Con el GO: descarga de referencia y contenedores → `reference_prepare` → seis gates →
STOP y reporte → GO explícito del alineamiento. No se añaden ramas nuevas salvo evidencia nueva. **Este commit cierra el preregistro científico del
WGS de lecturas cortas**: a partir de aquí no se agregan herramientas, genes, llamadores, scores ni
figuras porque aparezca otro artículo interesante. La siguiente fase es ejecución.
