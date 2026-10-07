# EXP-006b. Baseline externo: método independiente sobre el mismo VCF

> **`EXTERNAL`**: Exomiser 14.1.0 con datos `2402_hg38` + `2402_phenotype` y su propia base
> de conocimiento. **`DERIVED`**: la comparación con nuestro ranking, calculada aquí.
>
> Preregistro y umbral de lectura en `docs/DECISIONS.md`, ambos escritos **antes** de ejecutar.
>
> **Origen ejecutable:** `src/baseline/fetch_exomiser.py` → `run_exomiser.py` → `compare_baseline.py`.

## Qué comprueba, y por qué hacía falta

`BUB1B` queda #1 en catorce de los quince análisis del modo B (ver `docs/DECISIONS.md`: en `A0` queda #4 tras corregir el cruce de alelos). Ese resultado lo produce **nuestro propio
motor**. Un motor puede ser internamente consistente y estar sistemáticamente sesgado; los
quince análisis comparten código, así que no son quince comprobaciones independientes.

Exomiser no comparte con nosotros ni el ranking, ni la métrica semántica, ni la base de
conocimiento.

> ### Qué tipo de evidencia es esto, congelado antes de que se infle
>
> **`Convergencia metodológica sobre el MISMO VCF del paciente.`**
>
> **NO es evidencia biológica independiente.** Los dos motores observan el mismo genoma, las
> mismas llamadas de variante y los mismos errores de secuenciación y mapeo. Lo independiente
> es el **método**: la lógica de priorización, el emparejamiento fenotípico y la base de
> conocimiento.
>
> Un artefacto compartido del VCF los engañaría a los dos a la vez, y de hecho **ocurrió**:
> ambos señalan `SERPINA1`. Esa es la demostración de que este límite es real, no retórico.

## Independencia, lo que se le pasó y lo que no

| Se le dio | **No** se le dio |
|---|---|
| El VCF original completo | Nuestras 142 candidatas |
| GRCh38, sexo masculino | La shortlist de `BUB1B` |
| Los 7 términos HPO del documento clínico | Nuestras puntuaciones |
| Su propia base de conocimiento | Nuestros paneles o genes candidatos |

Los términos se leen de `config/phenotype_v2.yaml` en tiempo de ejecución, no se reescriben
en el script: dos copias de una lista acaban desincronizándose.

> **Independencia parcial, declarada.** El preset de exoma de Exomiser usa **REVEL** y MVP
> como fuentes de patogenicidad, y REVEL también intervino en nuestra decisión sobre `PP3`.
> En ese eje concreto los dos análisis comparten una entrada. Lo que sí es independiente: el
> motor de priorización, el emparejamiento fenotípico (hiPhive), la base de conocimiento y
> toda la lógica de ranking.

## Resultado

Ambas corridas: **`BUB1B` puesto 2 de 398 genes**, con el modelo **autosómico recesivo** como
el de mayor puntuación.

| Corrida | Puesto de `BUB1B` | Score | Mejor modelo | Veredicto preregistrado |
|---|---|---|---|---|
| `BASELINE-PRIMARY` | **2 / 398** | 0,9598 | AR | **Convergencia independiente (top 10)** |
| `BASELINE-FH` | **2 / 398** | 0,9494 | AR | **Convergencia independiente (top 10)** |

Nuestro `B0_FULL_PROBAND` lo pone #1. Dos motores sin código común coinciden en el mismo gen
y (esto no estaba preregistrado, pero es la parte más informativa) **en el mismo modelo de
herencia**, que es el que nuestro análisis había etiquetado `CANDIDATE_COMPATIBLE` para
OMIM:257300.

### Un error de conteo que había que corregir

La primera lectura decía «puesto 2 de 470». **470 son filas, no genes:** Exomiser emite una
fila por gen **y modo de herencia**, y son 398 genes únicos. Con el conteo por filas,
`BUB1B` y `ADAMTS1` aparecían dos veces en el top-10 y el solapamiento contaba genes
repetidos. Corregido en `compare_baseline.py`.

## El #1 no es lo que parece, y el #2 sí

`HLA-DRB1` queda por encima. Antes de aceptarlo o descartarlo, se miró **qué evidencia
sostiene a cada gen del top-10**:

| # | Gen | Variantes | Sin frecuencia poblacional | ClinVar P/LP |
|---|---|---|---|---|
| 1 | HLA-DRB1 | 35 | **28** | 0 |
| **2** | **`BUB1B`** | **4** | **0** | **2** |
| 3 | ADAMTS1 | 4 | 0 | 0 |
| 4 | FANCD2 | 4 | **4** | 0 |
| 5 | HLA-DQA1 | 46 | **29** | 0 |
| 6 | SERPINA1 | 52 | **32** | 0 |
| 7–10 | ARL9, ITPKB, ZNF254, CACNB1 | 1 c/u | 0 | 0 / 1 / 0 / 0 |

**`BUB1B` es el único gen del top 6 en el que todas las variantes tienen frecuencia
poblacional y hay aserciones patogénicas en ClinVar.** Los que lo rodean son acumulaciones de
30–52 variantes de alto impacto en un solo gen, la mayoría sin frecuencia asignable.

> **Esto es una HIPÓTESIS DE AUDITORÍA, no una conclusión.**
>
> Treinta y cinco truncantes en un gen **sugiere** complejidad de mapeo o de representación en
> una región polimórfica o con parálogos. **No lo demuestra.** Nada de lo hecho aquí comprueba
> la unicidad de mapeo, la calidad de las llamadas ni el contexto de pseudogén; «sin frecuencia
> poblacional» también puede significar «variante genuinamente nueva».
>
> Lo único que se afirma: **el perfil de evidencia de `BUB1B` es de otra clase** que el de los
> genes que lo rodean (pocas variantes, todas con frecuencia asignable, dos con asersión
> patogénica). Llamar «artefactos» a los demás exigiría la auditoría que aún no se ha hecho.

### `SERPINA1`: los dos motores convergen, sobre la misma peculiaridad de los datos

`SERPINA1` sale #6 aquí con **52 variantes**, 32 sin frecuencia. Nuestro propio pipeline ya lo
había marcado: 33 variantes fasadas que colapsan en un único evento haplotípico local.

**Que dos motores independientes lo señalen no es apoyo biológico independiente.** Ambos leen
el mismo VCF, y lo que comparten es la misma peculiaridad local de los datos. Es un buen
recordatorio de que la convergencia solo vale cuando las entradas difieren.

**No se afirma que sea un artefacto**, por la misma razón del recuadro anterior: nadie ha
comprobado todavía el mapeo ni la calidad de esas llamadas. Se afirma que **no cuenta como
segunda evidencia independiente**.

### `FANCD2` sí entra en el camino crítico

**Puesto 4, modelo recesivo, 4 variantes, pero las cuatro sin frecuencia poblacional.**

No se descarta, por dos razones. Primera, el perfil es sospechoso pero no concluyente.
Segunda, y más importante: **`FANCD2` es mecanísticamente adyacente al caso**. Es la vía de
anemia de Fanconi (inestabilidad cromosómica, fallo de crecimiento, predisposición tumoral),
que solapa con MVA tanto en fenotipo como en mecanismo. Descartarlo por incómodo sería
exactamente el sesgo que el baseline existe para detectar.

> **Entra como hipótesis competidora**, con una advertencia técnica anotada: `FANCD2` tiene
> pseudogenes conocidos, y eso es una causa habitual de variantes espurias. Hay que
> distinguir las dos explicaciones antes de darle peso.

## Solapamiento entre los dos rankings

**6 de 20 genes en común** en el top-20: `BUB1B`, `ADAMTS1`, `SERPINA1`, `SOCS5`, `THUMPD3`,
`LZTR1`.

Un solapamiento del 30 % es **modesto, y hay que decirlo así**. Los dos motores coinciden
fuertemente en `BUB1B` y poco en el resto. Eso es esperable, porque los alcances y los filtros
difieren, pero significa que la convergencia es **sobre el candidato principal**, no sobre el
ranking entero.

Genes del top-10 externo fuera de nuestro top-50: `HLA-DRB1`, `FANCD2`, `HLA-DQA1`, `ARL9`,
`ITPKB`, `ZNF254`, `CACNB1`.

## Diferencias de alcance, declaradas

| | Nuestro EXP-006 | Exomiser |
|---|---|---|
| Variantes de partida | 4 943 948 anotadas | 4 962 047 leídas |
| Regla de filtrado | dos niveles: `PASS` primario + rescate examinado variante a variante | `PASS_ONLY` |
| Efecto | HIGH + MODERATE | preset de exoma, sin UTR/intrón/regulador |
| Tras filtros | 6 321 genes | 398 genes / 835 variantes |

El preset de exoma se eligió porque corresponde al alcance que declaramos en EXP-006 (pasada
codificante y de splicing), no al genoma regulador. Usar el preset de genoma habría comparado
alcances distintos.

## Coste real, para el registro

Tres ajustes de configuración antes de arrancar, los tres con causa identificada y corrección
de una línea: rutas de Windows con barra invertida en un `.properties` de Java (se comen los
separadores), el VCF pasado como URI sin esquema `file://`, y el nombre de muestra del
phenopacket, que debe coincidir con el del VCF. Ese nombre **se lee de la cabecera en tiempo
de ejecución**, nunca se escribe en el código.

Descarga 24 GB / 44 min, descompresión 15 min, análisis **1 min 25 s** por corrida. Dentro
del límite declarado.

## Cierre

| | |
|---|---|
| **Estado** | **SURVIVES**: convergencia independiente confirmada |
| Qué sostiene | **Convergencia metodológica**: un motor sin código común, partiendo del mismo VCF y de los mismos 7 términos, sitúa `BUB1B` en el puesto 2 de 398 bajo modelo recesivo, y es el único del top 6 con perfil de evidencia limpio. |
| Qué NO sostiene | **Que sea evidencia biológica independiente**: ambos motores leen el mismo VCF. Que la variante sea patogénica; que la fase esté resuelta; que el ranking entero converja (solapamiento 30 %). |
| Efecto en ACMG | **Ninguno.** |
| Nuevas ramas abiertas | `FANCD2` como hipótesis competidora mecanísticamente plausible. |
| Pendiente para cerrar el bloque | `notebooks/03_TRACK1_GENOME_WIDE.ipynb` que reproduzca EXP-006 desde las entradas, y regenerar la Figura 6 desde ahí. |

**No se ha tocado nuestro ranking después de ver esto**, conforme al preregistro.

## Nivel de evidencia

`L2`: apoyo ortogonal. Comprobación independiente que concuerda con nuestro resultado,
producida por un motor que no comparte lógica de priorización. No es `L3`: no hay ensayo
funcional.
