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
        dos candidatos independientes en el mismo gen
              — configuración en trans NO demostrada —
```

> **Corrección sobre el texto de cierre.** La versión original terminaba en *«convergent
> gene disruption»*. Esa frase **afirma trans sin querer**: si las dos variantes están en
> cis, un alelo queda intacto y no hay disrupción bialélica en absoluto — el gen funciona.
> «Convergen en romper el gen» es precisamente la conclusión que la fase no resuelta no
> permite.
>
> El cierre correcto describe lo que se observa, no lo que implicaría: *dos candidatos
> independientes en el mismo gen, fase no resuelta*. Poner `PHASE UNRESOLVED` arriba y
> «convergent disruption» abajo se contradice, y un jurado atento lo ve.
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
