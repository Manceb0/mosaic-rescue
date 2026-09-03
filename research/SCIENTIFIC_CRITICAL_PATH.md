# Camino crítico científico

> **La reproducibilidad es infraestructura, no el producto.** Este documento existe porque
> el proyecto derivó: se convirtió EXP-006 y su andamiaje en el proyecto entero mientras
> ramas centrales quedaban flotando.
>
> **Regla de parada.** Toda rama abierta termina etiquetada `SURVIVES`, `NEGATIVE`,
> `BLOCKED` o `PARKED`. **Ninguna desaparece por haber aparecido una tarea nueva.**

## Qué es este proyecto, en una frase

Resolver el mecanismo causal del caso lo mejor posible, demostrarlo con **varias líneas de
evidencia independientes**, y convertir ese mecanismo en una **hipótesis terapéutica
aprobada, falsable y segura**.

El ranking, los tests y los notebooks existen para que esa historia sea defendible. **No son
la historia.**

## Filtro para cualquier tarea nueva

> ¿Qué incertidumbre científica del caso reduce, y qué decisión desbloquea?

Si no responde a las dos, va al *backlog* de ingeniería, no al camino crítico.

---

## Tabla viva

| # | Pregunta | Por qué importa | Evidencia actual | Estado | Bloqueo | Siguiente experimento | Impacto |
|---|---|---|---|---|---|---|---|
| 1 | ¿Qué gen explica el caso cuando compite todo el genoma codificante? | Sin esto, elegir `BUB1B` es sesgo de confirmación | **#1 en 14 de los 15 análisis**. En `A0` congelado queda **#4**; los tres que lo superan resultaron ser **polimorfismos comunes con rsID** cuya frecuencia VEP no supo anotar (hasta 313 150 homocigotos en gnomAD). En la sensibilidad `A0-FREQFIX`, que repara los 33 alelos afectados, **vuelve al puesto 1**. Modelo causal: OMIM:257300, compatible con herencia | **CERRADO · SURVIVES** | — | baseline externo hecho (#2 de 398, modelo AR) · notebook 03 reproduce desde las entradas · Figura 6 regenerada desde él. **Bloque de ranking cerrado; no se refina más salvo fallo concreto** | T1 |
| 2 | ¿Los dos alelos de `BUB1B` están en *trans*? | Sin *trans* no hay modelo bialélico | Sin `PGT`/`PID`; hueco 13,8× la longitud de fragmento | **BLOCKED** | genotipos parentales o lectura larga dirigida | pedirlos | T1 · **el de mayor valor** |
| 3 | ¿Hay un segundo alelo SNV/indel oculto en el locus? | El truncante necesita pareja | 270 kb, 1 candidato, AlphaGenome Δ plano | **NEGATIVE** | — | cerrado dentro del alcance evaluado | T1 |
| 4 | ¿El segundo hit es estructural? | Es la clase que el VCF no ve | CNV grande sin evidencia desde profundidad y heterocigosidad | **BLOCKED** | BAM/CRAM de profundidad completa | pedirlo | T1 |
| 5 | ¿Compite algún gen que no habíamos mirado? | Protege del sesgo de panel | **Los cuatro competidores auditados y ninguno sobrevive.** `CTU2`/`PEX5`/`SLC22A1` (`A0` #1–#3): polimorfismos comunes con rsID. `FANCD2` (Exomiser #6): alelos al ~47 %, todos heterocigotos. `LZTR1` (`B0` #4): el recesivo exige dos alelos y solo hay uno; el LoF heterocigoto da schwannomatosis de inicio adulto, sin función establecida en segregación cromosómica. `IGBP1` (`B0` #6): el único mecanismo reportado es 5'UTR y el nuestro es missense, asociación de una sola familia, y `MAX_AF` 1 × 10⁻⁴ **fuertemente inconsistente** con un modelo ultra-raro y penetrante para un síndrome ligado al X descrito una vez. Los tres argumentos juntos, no la frecuencia sola | **CERRADO · NEGATIVE** | — | `docs/COMPETITOR_AUDIT_LZTR1_IGBP1.md` (EXP-022). `LZTR1` se registra además como **candidato secundario/incidental de investigación**, **no** un hallazgo clínico devolvible: parada prematura MANE, heterocigota, ClinVar P/LP, DP 48 · GQ 99. No es la causa del MVA y no se emite recomendación clínica | T1 |
| 6 | ¿La nefrocalcinosis congénita exige un segundo diagnóstico? | No desaparece porque `BUB1B` gane | Primeros HIGH renales comunes. **Y el modo B añade señal: la nefrocalcinosis aporta poco soporte semántico al modelo MVA anotado** | **BARRIDO NEGATIVE · pregunta ABIERTA** | historia obstétrica y electrolitos | 0 alelos raros en 28 genes al umbral del panel; **0 variantes de `MAGED2`**. La nefrocalcinosis congénita sigue sin explicación propia | T1 |
| 6b | ¿La atrofia muscular está cubierta por el modelo MVA? | Mismo patrón que la renal | **No anotada en el modelo y no cuantificada en la serie de 31 casos** | **PARKED** | dato ausente en la literatura | — | T1 |
| 6c | ¿La literatura de MVA respalda crecimiento y perinatales? | Las bases HPO son incompletas | **Sí: 93,5 % de retraso de crecimiento.** El bajo soporte era **hueco de anotación**, no biología | **CERRADO · NEGATIVE como residual** | — | cerrado; no requiere experimento nuevo | T1 |
| 7 | ¿Cuál es el mecanismo, no solo el gen? | Encontrar el gen no es encontrar el mecanismo | Truncante → NMD predicho. Missense: **conservación ortóloga SURVIVES**, posición en el percentil 90 de su propia proteína, propiedad química conservada al 99,2 % en 120 ortólogos, la clase que introduce la sustitución no aparece en ninguno. **No cambia ACMG** | **PARCIAL · avanza** | ΔΔG explícito bloqueado por licencia FoldX | **siguiente mejor experimento registrado: ensayo de abundancia y recambio de BUBR1 específico de variante** | **T1→T2** |
| 8 | ¿El WGS conserva firma de mosaicismo? | Pieza central de originalidad | **Simulación hecha (EXP-015a):** el BAF colapsa a potencia 0,000 al 20 % en escenario variegado; la dispersión de cobertura conserva 1,000. **Superioridad sobre MoChA NO demostrada**, la línea base usada carece de fase | **COMPUERTA SUPERADA · aplicación BLOQUEADA** | controles con pipeline idéntico | conseguir controles; comparar contra un método CON fase | T1 |
| 9 | ¿Hay señal mitocondrial ortogonal? | Lectura independiente del mismo WGS | **Prototipo ejecutado:** 0,069 % de lecturas compatibles, *naive mtDNA-equivalent estimate* ≈259 bajo los supuestos del piloto. **Prototipo, no medida**: los NUMT no se excluyen sin alinear al genoma completo | **VIABILIDAD TÉCNICA · interpretación BLOCKED** | BAM/CRAM de profundidad completa **y** hemograma contemporáneo | pedir ambos; sin el hemograma la medida es ininterpretable | T1 |
| 10 | ¿Qué hipótesis terapéutica sobrevive? | **Es el diferencial del proyecto** | **6 clases evaluadas; la modulación de proteostasis es la superviviente principal ENTRE LAS EVALUADAS.** Separada en T2-A (aguas arriba) y T2-B (aguas abajo), con riesgos oncológicos opuestos. **Puente 7 cerrado como `UNRESOLVED` con contraevidencia verificada**: en fibroblastos NPC1 la sobreexpresión de HSP70 rescató y arimoclomol no, sin inducir HSP70 (PMID 34481829); y en aneuploides humanos la inducción de HSR está al 50–60 % (PMID 25205676). **Se nomina una cartera experimental de tres brazos para discriminación preclínica, no un ganador terapéutico** | **ABIERTO** | puente 7 con prior en contra; puente 8 vacío | **Next Best Experiment redefinido**: par isogénico aneuploide/euploide ± coinductor, con **control positivo genético** y **lectura obligatoria de si el fármaco induce HSP**, midiendo a la vez CIN y supervivencia clonogénica | **T2** |

---

## Lo que no puede volver a perderse

**MitoRead** sigue vivo como *orthogonal WGS-derived mitochondrial readout*, nunca «ensayo
funcional». Con las advertencias de composición celular y controles.

**Mosaic fingerprint** sigue vivo. Línea base estándar de mCA/BAF/profundidad **primero**;
el índice de dispersión experimental **después**, y solo si gana una simulación. Nunca
afirmar reconstrucción de cariotipos desde WGS bulk.

**La discrepancia con REVEL sigue sin explicar.** EXP-011 falsó la explicación que el propio proyecto había escrito. Que un dato nuevo mate una explicación nuestra es el funcionamiento correcto, no un problema, pero queda como incógnita abierta, no como asunto resuelto.

**El argumento de diagnóstico mixto se estrecha a UN solo rasgo.** De los cuatro con bajo soporte semántico, tres resultaron ser huecos de anotación o falta de dato. Solo la nefrocalcinosis carece de anotación **y** de respaldo en la literatura de MVA1.

**El solapamiento entre los dos rankings es del 30 %**, no del 100 %. Los motores coinciden fuertemente en `BUB1B` y poco en el resto. La convergencia es sobre el candidato principal, no sobre el ranking entero, y así hay que presentarla.

**Fenotipo residual** no se cierra porque los primeros HIGH renales fueran comunes. Se
cierra con evidencia.

**Track 2 está ABIERTO desde el cierre de EXP-006.** La búsqueda bibliográfica sobre dosis de BUBR1,
proteostasis y segregación cromosómica **ya está permitida**. Lo prohibido es **elegir el
candidato terapéutico final** antes de establecer suficientemente el mecanismo.

---

## Peticiones externas: bloqueos activos

Estas no desaparecen del registro porque no contesten.

| Petición | Bloquea | Estado |
|---|---|---|
| **BAM/CRAM** de los 4 carriles, con índice, *read groups* preservados y la referencia exacta | #4 SV/CNV, #8 mosaicismo, #9 MitoRead | pendiente |
| **Genotipos o muestras parentales** | #2 fase, el de mayor valor del proyecto | pendiente |
| Tipo de preparación de librería (`DNA Prep` o `DNA PCR-Free`) | peso de #8 | pendiente |
| Hemograma contemporáneo a la extracción | confusor de #9 | pendiente |
| ¿Polihidramnios u oligohidramnios? | pondera #6 | pendiente |

**Solo `L001` está en disco (~13×).** El VCF vino de los cuatro carriles. Prohibido cerrar
un negativo estructural con un carril.

---

## Dónde está el diferencial

`BUB1B` #1 es **Track 1 bien hecho**. No es lo que distingue al proyecto.

El diferencial está en lo que viene después:

```
variante causal
      ↓
MECANISMO
      ↓
señales ortogonales del MISMO WGS   ← mosaicismo · MitoRead
      ↓
hipótesis terapéutica
      ↓
intento sistemático de destruirla
      ↓
experimento que más información aporta
```

Eso es lo que no se puede volver a perder de vista.
