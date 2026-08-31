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
