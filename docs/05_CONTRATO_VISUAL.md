# Contrato visual

> **Regla del proyecto.** Ningún análisis importante termina solo en CSV o Markdown.
> Cada hipótesis acaba en **una figura interpretable, una conclusión, una incertidumbre y
> un falsificador**.

Complementa `docs/04_ARQUITECTURA_MAESTRA.md`. Las figuras no son decoración del
resultado: son la forma en que el resultado se somete a juicio.

---

## §1. La estructura obligatoria de cada figura

Ninguna figura se presenta sola. Toda figura lleva esta narrativa, en el pie o al lado:

```
HIPÓTESIS
    ↓
QUÉ ESPERÁBAMOS        ← preregistrado en docs/DECISIONS.md, ANTES de mirar
    ↓
QUÉ OBSERVAMOS
    ↓
QUÉ SIGNIFICA
    ↓
QUÉ LA MATARÍA
```

El segundo campo es el que da valor a los otros cuatro. Si «qué esperábamos» se escribe
después de ver el resultado, la figura no vale nada aunque el gráfico sea correcto —
`CLAUDE.md`, Regla Dura 6.

Ejemplo, MitoRead:

```
HIPÓTESIS      el estrés aneuploide altera la homeostasis mitocondrial
ESPERADO       mtDNA-CN del paciente por debajo de controles compatibles
OBSERVADO      paciente = percentil X de N controles emparejados
SIGNIFICA      apoya / no apoya la rama mitocondrial
LA MATARÍA     mtDNA-CN normal o alto, sin evidencia mitocondrial ortogonal
```

---

## §2. El contrato, hipótesis por hipótesis

**Es condicional, no una lista de entregables.** La mayoría de estas ramas va a morir —
ese es el diseño. El contrato dice: *si una rama sobrevive, debe esta figura*. Nadie
construye una figura para una rama muerta; la muerte se registra en `DECISIONS.md` y
alimenta la última fila de esta tabla.

| Hipótesis | Figura principal | Qué debe entender un jurado |
|---|---|---|
| Variante causal | Heatmap de evidencia por candidato | Por qué sobrevivieron estos 1–3 |
| **Hidden Second Allele** | **Pistas moleculares REF vs ALT (AlphaGenome)** | Qué cambia funcionalmente en el segundo alelo |
| Función residual | Gráfico de dosis funcional | Cuán severo parece cada alelo, sin falsa precisión |
| Bartter / HPO residual | Matriz fenotipo–gen | Qué síntomas explica MVA y cuáles quedan residuales |
| Segundo hit estructural | Diagrama de breakpoints centrado en el gen | Dónde hay un hit que el VCF convencional no veía |
| MitoRead | mtDNA-CN del paciente vs controles compatibles | Si existe señal mitocondrial anómala |
| Mosaic fingerprint | Mapa de dispersión LRR/BAF por cromosoma | Si el WGS bulk conserva firma de mosaicismo |
| Método de dispersión | Curva de sensibilidad por simulación | Si nuestro estadístico gana al baseline |
| Hipótesis terapéutica | Grafo causal mecanismo → fármaco | Por qué ese fármaco y no otro |
| Safe Rescue | Plano rescate vs peligro | Si mejora el mecanismo sin favorecer CIN |
| **Decisión final** | **Cementerio de hipótesis** | Qué murió y por qué |

---

## §3. La familia de figuras de AlphaGenome

AlphaGenome **no recibe los FASTQ y no sustituye al variant caller**. Su lugar es exacto:

```
VCF / variantes candidatas
        │
        ▼
   ¿coding obvio?
   │            │
  sí            no / VUS / intrónica
   │            │
   ▼            ▼
proteína /   ★ ALPHAGENOME ★
NMD             │
                ├─ expresión
                ├─ splicing
                ├─ cromatina
                ├─ actividad reguladora
                └─ otros efectos moleculares predichos
                        │
                        ▼
               PERFIL DE MECANISMO
```

Lo que queremos poder enseñar no es *«usamos AlphaGenome»*, sino:

> *«Esta variante era casi invisible para un pipeline de codificante. AlphaGenome predice
> que cambiar esta única base reconfigura esta salida molecular concreta.»*

### 3.1 Figura A — Pistas REF vs ALT

> **Sustituida por la versión de tres capas del §12.** Se conserva aquí el análisis de
> riesgo, que sigue aplicando íntegro.

```
POSICIÓN GENÓMICA ─────────────────────────────────────────>
Gen         ─────[exón]──────[exón]────────[exón]──────
                            ★ variante del paciente
                            │
REF expresión  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
ALT expresión  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░
REF splicing            ────────────────►
ALT splicing            ─────►
                             └──────── junción críptica ↑
Cromatina
REF            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
ALT            ▓▓▓▓▓▓▓▓▓░░░░░░░░
Unión de TF
REF                  ▲▲▲▲▲
ALT                  ░░░░░
```

> ### ⚠ Riesgo de diseño — la figura más peligrosa del proyecto
>
> **Esta figura se parece a una captura de un genome browser.** Un jurado con experiencia
> en genómica leerá esas pistas como datos medidos, porque es exactamente así como se ven
> las pistas de RNA-seq y ATAC-seq reales. Y **no hay RNA-seq en este dataset**: no
> medimos expresión, la inferimos.
>
> Reglas de diseño **no negociables** para esta figura:
>
> 1. La palabra **PREDICHO** va en el propio panel, no en el pie ni en una nota al margen.
> 2. Las pistas deben ser **visualmente distinguibles** de un browser: sin ejes de
>    cobertura, sin escala en reads, paleta deliberadamente distinta.
> 3. El eje vertical se etiqueta como **salida del modelo**, nunca como *coverage*,
>    *counts*, *TPM* ni *señal*.
> 4. Si la figura se recorta y se pega en otro sitio sin el pie, **debe seguir diciendo
>    que es una predicción**. Ese es el test.

### 3.2 Figura B — Tarjeta de mecanismo de variante

```
Candidato: Variante B
Anotación estándar: intrónica / VUS

AlphaGenome:
  Expresión           ↓
  Splicing canónico   ↓↓↓
  Splicing críptico   ↑↑↑
  Cromatina           ↔
  Unión de TF         ↓ leve

Interpretación:
  candidato a pérdida de función reguladora / de splicing

Estado de evidencia:
  PREDICHO — no demostrado experimentalmente
```

> **Corrección necesaria: las flechas tienen que estar definidas.** `↓↓↓` frente a `↓`
> sugiere una escala cuantitativa. Si no se define, es falsa precisión — Regla Dura 4,
> el mismo error que prohibimos al hablar de porcentajes de proteína residual.
>
> Cada tarjeta debe llevar la leyenda con los cortes usados, y el valor bruto del modelo
> junto a la flecha. La flecha es un resumen legible; el número es lo auditable.

### 3.3 Figura C — Mapa alelo → mecanismo

```
                        PHASE UNRESOLVED
                  ══════════════════════════

                            GEN X

ALELO A                                        ALELO B
variante codificante                           intrónica profunda
     │                                              │
     ▼                                              ▼
NMD / pérdida de proteína                     AlphaGenome
                                                    │
                                       splicing canónico ↓
                                       splicing críptico ↑
     │                                              │
     └──────────────────────┬───────────────────────┘
                            ▼
      dos variantes candidatas en el mismo gen
        configuración en trans NO establecida
   no se puede afirmar mecanismo recesivo bialélico
```

> **Corrección sobre el texto de cierre.** La versión original terminaba en *«convergent
> gene disruption»*. Esa frase **afirma trans sin querer**: en cis no queda demostrada la
> disrupción bialélica, que es la base del mecanismo recesivo que la figura insinúa.
>
> Formulación correcta, en inglés para la presentación:
>
> > *Two candidate variants in the same gene; phase unresolved. A recessive biallelic
> > mechanism cannot be claimed unless trans configuration is established or independently
> > supported.*
>
> **Dos precisiones sobre la redacción, ambas importantes:**
>
> 1. **No decir «el gen funciona» si están en cis.** Eso presupone haplosuficiencia, que
>    depende del gen, de la dosis y del mecanismo. En genes de MVA hay portadores
>    heterocigotos con fenotipos celulares sutiles descritos — precisamente el gradiente
>    de BubR1 del brief §3.2 muestra PCS por encima del umbral de aneuploidía. Lo único
>    afirmable en cis es que **no hemos demostrado disrupción bialélica**.
> 2. **«dos variantes candidatas», no «dos candidatos independientes».** «Independiente»
>    se lee como independencia alélica o haplotípica, que es justo lo desconocido.
>
> Esto no debilita la figura. La hace defendible.

### 3.4 Figura D — El candidato que AlphaGenome tumba

**La figura más valiosa de la familia**, y la que más credibilidad da:

```
Score de patogenicidad ALTO  (CADD, rareza en gnomAD)
          ↓
Efecto funcional predicho por AlphaGenome ≈ 0
          ↓
candidato DEGRADADO en el ranking
```

Demuestra que AlphaGenome no se está usando para confirmar lo que ya queríamos creer.
Un jurado distingue perfectamente entre una herramienta usada como filtro y una usada
como adorno confirmatorio — y esta figura es la prueba de lo primero.

**Se produce aunque no haya un hallazgo positivo.** De hecho, si la rama del segundo
alelo muere, esta es la figura que queda, y sigue mereciendo estar en la presentación.

---

## §4. Reglas de diseño transversales

0. **Toda figura declara su procedencia** — `MEASURED` / `DERIVED` / `PREDICTED` /
   `EXTERNAL`, en una esquina del panel. Ver §11. Es la regla más importante de esta lista.
1. **Nada de radares.** Seis ejes en escalas no comparables codifican magnitud como área y
   exageran diferencias. Barras divergentes o heatmap por modalidad
   (`docs/03_ALPHAGENOME_ASSESSMENT.md` §4.4).
2. **Las salidas multimodales de AlphaGenome no son rutas de evidencia independientes.**
   Son salidas correlacionadas del mismo modelo. La figura no puede sugerir convergencia
   donde hay un solo origen.
3. **Toda figura declara su nivel de evidencia** (`L0`–`L5`) en el propio panel.
4. **Ninguna figura contiene coordenadas con genotipo del paciente ni secuencia genómica**
   legible. Etiquetas de gen y de mecanismo, sí; secuencia, no (Regla Dura 1).
5. **Si una figura necesita que el jurado adivine qué significa, está incompleta.** La
   estructura del §1 es el mínimo, no un extra.

---

## §5. Los tres niveles visuales

No todas las figuras hacen el mismo trabajo. Confundirlos produce presentaciones que
impresionan y no convencen, o que convencen y aburren.

| Nivel | Función | Qué debe provocar |
|---|---|---|
| **Hero / wow** | Abren y cierran. Cuentan la historia completa de un vistazo | *«espera… ¿qué estoy viendo?»* |
| **Científico** | Justifican el mecanismo. Soportan escrutinio técnico | *«vale, no es humo; aquí hay mecanismo»* |
| **De decisión** | Muestran cómo se descartó lo demás | *«no forzaron la respuesta; la encontraron»* |

El tercero es el que más se descuida y el que más pesa en un jurado.

---

## §6. Catálogo de figuras — el blueprint

**Condicional.** «Depende de» dice qué tiene que existir para que la figura se pueda
construir. Si eso no aparece, la figura no se hace y la rama pasa al cementerio.

| # | Figura | Nivel | Qué la alimenta | Mensaje | Depende de |
|---|---|---|---|---|---|
| 1 | **From one genome to one mechanism** | Hero | El propio pipeline | La historia completa: genoma → mecanismo → hipótesis → filtro de seguridad | **Nada. Única figura sin dependencia de datos** |
| 2 | **AlphaGenome REF vs ALT + DELTA** | Hero + científico | Variante candidata no codificante | Esta base cambia este comportamiento molecular | Que exista candidato no codificante |
| 3 | Mechanism Fingerprint Card | Científico | Salidas de AlphaGenome | Resumen legible del mecanismo predicho | Ídem #2 |
| 4 | Hidden Second Allele | Hero + científico | Alelo A + candidato B | Cómo se buscó lo que el pipeline estándar no ve | Que aparezca alelo huérfano |
| 5 | Mapa de fenotipo mixto | Científico + decisión | HPO + paneles | El caso no es lineal | Fenotipo clínico real + literatura |
| 6 | MitoRead | Científico | mtDNA-CN vs controles | Si hay señal mitocondrial anómala | Controles compatibles |
| 7 | Mosaic fingerprint | Científico | BAF/LRR por cromosoma | Si el bulk conserva firma de mosaicismo | Alineamiento |
| 8 | Curva de sensibilidad | Científico | Simulación 1/2/5/10/20 % | Si nuestro estadístico gana al baseline | Simulación hecha |
| 9 | Grafo mecanismo → fármaco | Científico | Mecanismo causal | Por qué **ese** fármaco | Mecanismo establecido |
| 10 | Plano rescate vs peligro | Decisión | Rúbrica de rescate | Si mejora sin favorecer CIN | Candidato terapéutico |
| 11 | **Hypothesis Graveyard** | Decisión | `docs/DECISIONS.md` | Qué murió y por qué | Decisiones y evidencia ya registradas |

**Construibles antes del análisis del VCF: #1, #5 y #11.** Es la etiqueta exacta, y no
«no dependen de datos» — solo la #1 es realmente independiente de todo. La #5 necesita el
fenotipo clínico real y la literatura; la #11 necesita las decisiones y la evidencia que
ya están registradas. Las otras ocho esperan a los datos del paciente.

### 6.1 La adición del panel DELTA

Añadir un tercer panel **DELTA (ALT − REF)** a la figura #2 es una mejora real, y no solo
por legibilidad: **un delta se parece mucho menos a una captura de genome browser** que dos
pistas de cobertura apiladas. Reduce el riesgo de §3.1 en lugar de agravarlo.

El delta es además donde vive la información: dos pistas casi idénticas con una diferencia
local se leen mal a ojo, y la resta la hace evidente.

---

## §7. Corrección — la figura 4 vuelve a afirmar `trans`

El cierre propuesto era:

```
Convergent disruption of the same gene
(phase unresolved, functional convergence supported)
```

**Sigue siendo la afirmación que la fase no permite**, y el paréntesis no la rescata:
en *cis* no queda establecida la disrupción bialélica, y «convergencia funcional apoyada»
describe exactamente lo que no se puede apoyar sin resolver fase.

Cierre correcto:

```
                    PHASE UNRESOLVED
              ══════════════════════════

      dos variantes candidatas en el mismo gen
   cada una con evidencia de disrupción por separado
        configuración en trans NO establecida
```

> *Two candidate variants in the same gene; phase unresolved. A recessive biallelic
> mechanism cannot be claimed unless trans configuration is established or independently
> supported.*

Es igual de impactante y no se cae con la primera pregunta del jurado. Un evaluador que
conozca genética clínica va a preguntar por la fase; que la figura se le adelante juega a
favor.

---

## §8. El tríptico y el orden del pitch

Corazón visual: **#1 Hero pipeline · #2 AlphaGenome REF/ALT/DELTA · #11 Graveyard.**
Historia completa, mecanismo-wow, y honestidad narrativa.

| Slide | Contenido | Si la rama murió |
|---|---|---|
| 1 | El problema | — |
| 2 | Nuestra apuesta: por qué no es un pipeline variante→fármaco estándar | — |
| 3 | **Hero architecture** | — |
| 4 | Candidatos causales y por qué sobrevivieron | — |
| 5 | **AlphaGenome hidden allele** | **→ figura §3.4: el candidato que AlphaGenome tumba** |
| 6 | Fenotipo mixto / diagnóstico residual | → matriz con la rama renal descartada, y por qué |
| 7 | MitoRead / mosaic — evidencia ortogonal | → el resultado negativo, con su falsificador |
| 8 | Mecanismo → fármaco (no ranking de fármacos) | → «no llegamos aquí, y este es el motivo» |
| 9 | Try to kill it | — |
| 10 | **Graveyard + hipótesis final** | — |

**La columna de la derecha es obligatoria.** El slide 5 es el wow, y depende de encontrar
un segundo alelo — cosa que puede no pasar. Un pitch cuyo momento culminante desaparece si
un análisis sale negativo está mal construido. La figura §3.4 cubre ese hueco y, dicho
honestamente, casi lo cubre mejor: *«miramos, y esto es lo que descartamos»*.

---

## §9. Los cuatro roles de AlphaGenome

Explícitos, para que no quede como «usamos AlphaGenome»:

| Rol | Qué hace |
|---|---|
| **1. Hidden second allele** | Buscar efecto funcional en intrónicas, reguladoras y VUS |
| **2. Mechanism fingerprinting** | Traducir una variante a huella molecular visual |
| **3. Variant downranking** | Bajar candidatos que parecían fuertes y no muestran efecto coherente |
| **4. Hypothesis refinement** | Ayudar a elegir qué mecanismo tiene sentido atacar después |

**La frase permitida**, y la única que se usa en la presentación:

> *AlphaGenome provides functional predictions that help prioritize and mechanistically
> interpret candidate noncoding or splice-disrupting variants.*

**Prohibido decir**, en figura, pie o narración: que demostró causalidad · que prueba
patogenicidad · que confirma la segunda variante · que resolvió fase · que encontró la cura.

El rol 3 merece énfasis: es el que demuestra que la herramienta filtra en vez de confirmar
lo que ya queríamos creer, y es el único que produce figura **aunque todo lo demás falle**.

---

## §10. Regla de integridad del cementerio

El Graveyard es una figura de credibilidad, y por eso es la más fácil de arruinar.

> **Solo entra una hipótesis que realmente consideramos y matamos con evidencia registrada
> en `docs/DECISIONS.md` o en el brief.**

Nada de lápidas plausibles añadidas para parecer rigurosos. Un jurado que pregunte *«¿y por
qué descartasteis esa?»* y reciba una reconstrucción a posteriori convierte la mejor figura
del proyecto en la peor.

Verificado a fecha de hoy: las cinco entradas propuestas tienen acta de defunción real.

| Hipótesis | Estado | Dónde está la evidencia |
|---|---|---|
| MVA codificante clásico | viva | Track 1, `02_ANALYSIS_PLAN.md` |
| Diagnóstico dual / Bartter | condicional | brief §8; `04_ARQUITECTURA_MAESTRA.md` §4 |
| Rescate mitocondrial / arimoclomol | posible, con colisión oncológica declarada | brief §10.3; plan §306 |
| Estabilización del huso tipo taxano | **rechazada** | brief §455: el paclitaxel breve a dosis baja **induce** husos multipolares y aneuploidía; más neurotoxicidad y mielosupresión en un niño con atrofia muscular y antecedente de rabdomiosarcoma |
| Reconstrucción de cariotipos desde bulk WGS | **rechazada por sobreafirmación** | `00_ESTADO_Y_OBSOLESCENCIA.md`; tres auditorías independientes |

La cuarta es la mejor lápida del conjunto: una idea que era *elegante* —rescatar el modo de
fallo de `CEP57` anclando extremos menos— y que murió por el mecanismo mismo que proponía.
Eso es exactamente lo que el jurado tiene que ver.

---

## §11. Etiqueta de procedencia — obligatoria en toda figura

Regla universal, en una esquina de cada panel. Es ortogonal al nivel `L0`–`L5`: el nivel
dice **cuán fuerte** es la evidencia, la etiqueta dice **de dónde sale**.

| Etiqueta | Qué es | Ejemplos en este proyecto |
|---|---|---|
| `MEASURED` | Sale directamente del instrumento | Calidades Phred, profundidad, longitud de read, GC |
| `DERIVED` | Calculado por nosotros a partir de lo medido | mtDNA-CN, BAF, LRR, ranking de candidatos, índice de dispersión |
| `PREDICTED` | Salida de un modelo. No se midió | AlphaGenome (expresión, splicing, cromatina), SpliceAI, CADD |
| `EXTERNAL` | Viene de literatura o bases de datos | Rescate funcional publicado, gradiente de BubR1, frecuencias de gnomAD |

Parece un detalle menor y no lo es: es lo que separa un proyecto que sabe qué está
enseñando de uno que mezcla medición y predicción en el mismo panel sin darse cuenta.
Y resuelve de raíz el riesgo de §3.1 — una figura de AlphaGenome marcada `PREDICTED` en
la esquina ya no se puede confundir con un browser de RNA-seq.

**Una figura con dos procedencias lleva las dos etiquetas, por panel.** Si un panel mezcla
`MEASURED` y `PREDICTED` en la misma pista, la figura está mal construida: se separan.

---

## §12. La figura de AlphaGenome, versión definitiva — tres capas

Sustituye a la de §3.1. El resultado que interesa no es la pista REF ni la ALT: es
**qué cambió al introducir la variante**.

```
┌─────────────────────────────────────────────── PREDICTED ──┐
│  ALPHAGENOME                                               │
│  Gene:     X                                               │
│  Variant:  candidate B                                     │
│  Context:  kidney-relevant / blood / fibroblast-like       │
│  Window:   1 Mb                                            │
├────────────────────────────────────────────────────────────┤
│  RNA                                                       │
│   REF  ──────────────────████████████──                    │
│   ALT  ─────────────██████──────────────                   │
│   Δ                        ↓                               │
│                                                            │
│  Splicing                                                  │
│   REF  exon 2 ─────────────── exon 3                       │
│   ALT  exon 2 ───┐                                         │
│                  └── cryptic junction ↑                    │
│   Δ                        ↑ cryptic / ↓ canonical         │
│                                                            │
│  Accessibility                                             │
│   REF  ███████████████                                     │
│   ALT  █████████░░░░░░                                     │
│   Δ                    ↓                                   │
├────────────────────────────────────────────────────────────┤
│  Interpretation:  predicted splice/regulatory disruption    │
│  Status:          candidate mechanism —                     │
│                   not experimentally demonstrated           │
└────────────────────────────────────────────────────────────┘
```

**Dos elementos que no son opcionales:**

1. **La capa Δ.** Es donde vive el resultado. Dos pistas casi idénticas con una diferencia
   local se comparan mal a ojo; la resta la hace evidente. Y un delta se parece mucho menos
   a una captura de browser que dos pistas apiladas, así que reduce el riesgo de §3.1 en
   vez de agravarlo.
2. **El contexto declarado.** Tejido, tipo celular y ventana. Una predicción de expresión
   sin decir en qué contexto se predijo no es interpretable — y en este caso importa
   especialmente, porque el fenotipo tiene eje renal y eje hematopoyético, y el modelo no
   predice lo mismo en cada uno.

---

## §13. Plan B para cada slide, no solo para el 5

Generalización de la columna de respaldo del §8. **Un resultado negativo no elimina un
slide: le cambia el título.**

| Rama | Si sale positiva | Si sale negativa |
|---|---|---|
| Segundo alelo / AlphaGenome | *This single base rewires this molecular output* | *The strongest-looking noncoding candidate failed functional prediction* |
| MitoRead | *An orthogonal mitochondrial signal supports the branch* | *A mechanism we expected — and the patient's genome did not support* |
| Bartter / fenotipo residual | *Congenital nephrocalcinosis opened a second diagnosis* | *Congenital nephrocalcinosis triggered a second-diagnosis search. The genome did not support it* |
| Mosaic fingerprint | *The bulk genome retains a mosaic signature* | *We looked for a mosaic signature in bulk WGS and report what we could not resolve* |
| Índice de dispersión | *Our statistic beats the standard method* | *Our statistic lost to the standard method, and here is the simulation that showed it* |

Esto es lo que hace que el pitch **deje de depender de tener suerte**. Cada rama produce
material presentable en los dos desenlaces, y el conjunto de los negativos es el
cementerio — que es, él solo, una de las tres figuras hero.

---

## §14. Regla dura — una figura no se acepta por ser bonita

Regla añadida tras revisar las primeras figuras y encontrar que eran **envoltorios de
presentación**, no evidencia: tarjetas, barras resumen, tiras de densidad y pistas
decorativas que se podían haber dibujado **antes** de mirar los datos.

> **Ninguna figura se acepta solo por ser visualmente atractiva. Cada figura debe contener
> al menos una cantidad, relación espacial, estructura molecular, señal genómica u objeto
> derivado de medición o predicción que NO se hubiera podido dibujar antes de ver los
> datos.**

### El test

Tapa el pie de figura. **¿Puede un científico entender qué se midió, dónde ocurre
biológicamente, qué cambió y qué sigue incierto?** Si no, se rediseña.

### Sustituciones obligatorias

Siempre que sea posible, la barra resumen se sustituye por **el objeto científico
subyacente**:

| En vez de | Dibujar |
|---|---|
| Barras por gen | Coordenadas de proteína con *lollipops* de variantes |
| «exón 17/23 → NMD probable» | Arquitectura de exones con el PTC, la última unión y los 55 nt sombreados |
| «los reads no alcanzan» | Coordenadas genómicas con los huecos y fragmentos a escala |
| «dominio afectado» | Estructura molecular con contactos atómicos |
| «RNA 3,4 %, ATAC 1,2 %» | Pistas genómicas REF / ALT / Δ |
| «residuo conservado» | Logo de conservación del alineamiento |
| «sin CNV» | Pistas de profundidad y BAF |
| Diagrama de cajas | Grafo causal con la evidencia que mató cada rama |

### Ejemplo del fallo, para no repetirlo

En la primera versión de la Figura 2, la barra del **dominio pseudoquinasa** se podía
dibujar antes de analizar al paciente. Era decoración con aspecto de dato.

En cambio **sí** superan el test: el residuo con sus vecinos reales a 5 Å, sus tres puentes
de hidrógeno con distancias medidas, la RSA del 16,2 %, los 748 nt del PTC a la última
unión, los 4 142 pb que impiden la fase, los REF/ALT/Δ de AlphaGenome, y cada variante de
ClinVar en su posición. **Todo eso existe solo porque se analizaron los datos.**

### Formato

El Markdown puede ir cuidado, pero **el gráfico se genera desde los datos medidos**. La
evidencia central no se construye con rectángulos de HTML y CSS.
