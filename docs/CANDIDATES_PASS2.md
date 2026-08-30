# Candidatos — pasada 2: frecuencia, clínica y función

> **⚠ Saneado conservador**, por decisión del responsable del dato. Este documento no
> contiene coordenadas, rsID, cambios proteicos concretos, profundidades ni genotipos. Ese
> detalle vive en `work/pass2/` (ignorado por Git).
>
> Anotación con el caché de VEP 116, que incluye **gnomAD v4.1** (exomas y genomas),
> **ClinVar**, **dbSNP 156**, SIFT, PolyPhen-2 y MANE. Todo **offline**: ninguna variante
> salió de la máquina.

---

## Corrección importante — un error de la pasada 1

La pasada 1 afirmó que **ninguna** de las dos candidatas de `BUB1B` estaba en dbSNP. **Eso
era falso**, y el método para deducirlo era malo.

Lo deduje de que la **columna `ID` del VCF venía vacía**. Pero esa columna solo está
poblada si el *caller* hizo anotación contra dbSNP — y estar vacía no significa que la
variante sea nueva, solo que **ese pipeline no la anotó**.

Al consultar el caché con `--check_existing`, el resultado cambia por completo:

| Alelo candidato | En dbSNP | En ClinVar |
|---|---|---|
| **Truncante** | **Sí** | **`pathogenic` / `likely_pathogenic`** |
| **Missense** | No | No |

El error **reforzó** el hallazgo en lugar de debilitarlo, pero eso no lo hace menos error:
afirmé novedad a partir de un proxy que no la sostiene. Queda registrado en
`docs/DECISIONS.md`.

**Lección de método:** la columna `ID` de un VCF no es una fuente de novedad. La fuente son
dbSNP, gnomAD y ClinVar consultados explícitamente.

---

## `BUB1B` — los dos candidatos, ahora con evidencia externa

Ambos: **`PASS`**, **heterocigotos**, balance alélico limpio, sobre el transcrito
**MANE Select** y canónico.

### Alelo A — truncante

| | |
|---|---|
| Consecuencia | `stop_gained` |
| Posición en el gen | **exón 17 de 23** |
| gnomAD (máx. poblacional) | **~1 × 10⁻⁴** — muy raro, compatible con alelo recesivo |
| **ClinVar** | **`pathogenic` / `likely_pathogenic`** |
| NMD | **Predicho.** El codón de parada está muy por encima de la última unión exón-exón, así que la regla de los 50–55 nt aplica con holgura |

**No es una variante nueva ni una interpretación nuestra: está clasificada como patogénica
en una base clínica pública.**

### Alelo B — missense

| | |
|---|---|
| Consecuencia | `missense_variant` |
| Posición en el gen | **exón 23 de 23** — el último |
| gnomAD | **Ausente.** Ni en exomas ni en genomas de v4.1 |
| dbSNP / ClinVar | Ausente de ambos. **Novel** |
| Dominio | **Dominio quinasa** (`Gene3D:1.10.510.10`, `CDD:cd14029`) |
| SIFT | `deleterious` (0,01) |
| PolyPhen-2 | `probably_damaging` (0,997) |
| NMD | **No aplica.** Al estar en el último exón, escapa a NMD y produce proteína completa |

### La asimetría de NMD es el mecanismo publicado

Esto no es una coincidencia bonita: es exactamente lo que describe la literatura de MVA por
`BUB1B`.

```
Alelo A  →  truncante en exón 17/23  →  NMD  →  sin transcrito  →  aporte ≈ 0
Alelo B  →  missense en exón 23/23   →  escapa NMD  →  proteína completa
                                          en el dominio quinasa
                                          → alto recambio proteico
```

La baja abundancia global de BubR1 en pacientes bialélicos resulta de **la ausencia de
transcrito del alelo truncante combinada con el alto recambio de la proteína missense**
([Suijkerbuijk et al., PMID 20516114](https://pubmed.ncbi.nlm.nih.gov/20516114/)). Y el
cambio missense en ese grupo cae de forma consistente **en el dominio quinasa o cerca**
— que es donde cae éste.

El patrón bialélico canónico —**una missense emparejada con una truncante**— está descrito
desde el trabajo original ([Hanks et al., PMID 15475955](https://pubmed.ncbi.nlm.nih.gov/15475955/)),
que además incluía familias con **rabdomiosarcoma embrionario**, el mismo evento oncológico
del probando.

---

## Los otros HIGH, resueltos por frecuencia

La pasada 1 los dejó «sin evaluar». Con gnomAD se resuelven, y **ninguno sobrevive**:

| Gen | Carril | Frecuencia poblacional máx. | ClinVar | Veredicto |
|---|---|---|---|---|
| `VDR` | Renal | **~0,81** | `benign`, conflicting | Polimorfismo muy común |
| `ATP6V1B1` | Renal | **~0,51** | `benign` | Polimorfismo común |
| `ANAPC1` | MVA | **~0,086** | — | Demasiado común para enfermedad recesiva grave; además la consecuencia caía sobre un transcrito NMD |

**Esto valida la corrección sobre los rsID.** No los mató tener identificador: los mató la
frecuencia. Y simétricamente, el alelo truncante de `BUB1B` **tiene** rsID y es el candidato
más fuerte del proyecto. Tener rsID no dice nada por sí solo.

Es además la confirmación de la predicción #6 del preregistro: sin filtro de frecuencia, el
carril genome-wide es ruido. Tres de cuatro HIGH de panel eran polimorfismos.

---

## Lo que sigue sin poder afirmarse

> **La fase no está resuelta.** Los dos candidatos distan ~11 kb; el bloque `PID` más largo
> de todo el genoma mide 288 pb. Ni este VCF ni ningún análisis sobre él pueden establecer
> `trans`.

Formulación permitida:

> *Two candidate variants in the same gene; phase unresolved. A recessive biallelic
> mechanism cannot be claimed unless trans configuration is established or independently
> supported.*

**¿Hay apoyo independiente?** El fenotipo clínico lo aporta en un sentido concreto: si los
dos alelos estuvieran en *cis*, quedaría una copia de `BUB1B` sin ninguna de las dos
variantes. Pero **usar el fenotipo que intentamos explicar como prueba de la configuración
que lo explicaría es un argumento bayesiano, no una demostración.** Se declara como lo que
es y no se presenta como fase resuelta.

---

## El experimento que más reduce la incertidumbre

Por primera vez en el proyecto hay un experimento concreto que convertiría un candidato en
un mecanismo establecido, y son dos vías:

1. **Genotipos parentales.** Una muestra de cada progenitor resuelve la fase de forma
   definitiva. Es la vía barata y estándar.
2. **Secuenciación dirigida de lectura larga** sobre los ~11 kb entre los dos candidatos.
   Resuelve la fase **sin necesidad de los padres**, que es lo relevante si no están
   disponibles.

Esto desplaza la prioridad del proyecto: **pedir esto vale más que cualquier análisis
adicional sobre los datos actuales.**

---

## Consecuencia sobre la rama de dosis residual

`docs/03_ALPHAGENOME_ASSESSMENT.md` §4.1 dejó la rama condicionada a que Track 1 resolviera
a `BUB1B`. **La condición se cumple**, y ahora con evidencia externa en ambos alelos.

La pregunta operativa pasa a ser la del umbral publicado del ~50 % de proteína residual
(brief §3.2). Con un alelo predicho como nulo por NMD y otro produciendo proteína completa
pero con recambio elevado en el dominio quinasa, el escenario es el que la literatura asocia
con abundancia global baja.

> **Sigue prohibido dar un porcentaje.** La salida es una **clase con incertidumbre**
> (`severo` / `intermedio` / `leve`), comparada cualitativamente contra el gradiente
> publicado. No «este niño tiene un 32 %».

### Y esto cambia el papel de AlphaGenome

Si el alelo B se sostiene, **AlphaGenome no es el protagonista de este par**: una missense
es un problema de proteína, no de regulación. Lo que se activa es la rama estructural
—estructura experimental o AlphaFold como andamio, estabilidad, interfaz— y no se mete
AlphaGenome por enseñar el logo (`CLAUDE.md`: no usar herramientas decorativamente).

AlphaGenome vuelve a primer plano **si el alelo B se cae**. Entonces se activa Hidden Second
Allele, que en `BUB1B` tiene precedente humano publicado.
