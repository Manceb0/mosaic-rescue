# EXP-016 · Track 2 — dos rutas, ocho puentes, y el corredor de rescate seguro

> **NO HAY NOMINACIÓN DE FÁRMACO, Y ES DELIBERADO.**
>
> **`EXTERNAL`** — toda la evidencia citada procede de la tabla verificada del brief §11.
> Ningún identificador bibliográfico se escribe aquí sin estar ya verificado en el proyecto.
> Donde falta evidencia se escribe **hueco**, no una cita plausible.

## La corrección que reorganiza todo este documento

La versión anterior agrupaba la evidencia bajo una sola etiqueta, «proteostasis». **Eso era un
error de fondo**, porque mete en la misma caja dos intervenciones con **lógica terapéutica
distinta y consecuencias oncológicas potencialmente opuestas**.

```
T2-A · RESCATE AGUAS ARRIBA              T2-B · TOLERANCIA AGUAS ABAJO
                                          
variante -> inestabilidad de BUBR1        celula ya aneuploide
        ↓                                         ↓
 subir abundancia de BUBR1                estres proteotoxico / mitocondrial
        ↓                                         ↓
 mejorar el checkpoint del huso           subir capacidad de HSP
        ↓                                         ↓
 MENOS missegregacion NUEVA               la celula TOLERA MEJOR ser aneuploide
        ↓                                         ↓
 podria REDUCIR CIN                       podria AUMENTAR la supervivencia
                                          de celulas genomicamente inestables
```

**T2-A apunta a que se generen menos células aneuploides. T2-B apunta a que las que ya existen
vivan mejor.** En un niño que ya tuvo un rabdomiosarcoma, esa diferencia lo es todo.

Agruparlas bajo «proteostasis» hacía que la evidencia de una pareciera respaldar a la otra.

---

## Los ocho puentes

Toda afirmación de Track 2 tiene que declarar **qué puente sostiene**. La evidencia de un
puente **no vale** para otro.

| # | Puente | Ruta | Evidencia | Sistema | Fuerza |
|---|---|---|---|---|---|
| **1** | variante concreta de este paciente → inestabilidad de BUBR1 | T2-A | **HUECO** — solo inferencia estructural y conservación | *in silico* | **L0–L1** |
| **2** | inestabilidad de BUBR1 → menos proteína | T2-A | Niveles muy bajos en pacientes con mutaciones en BUBR1, incluso missense, por inestabilidad | pacientes | `L5`, **de otros alelos** |
| **3** | subir capacidad de chaperonas → **subir** abundancia de BUBR1 | T2-A | **HUECO CRÍTICO — la evidencia va en la dirección CONTRARIA.** Ver abajo | células | **L0** |
| **4** | más abundancia de BUBR1 → menos CIN | T2-A | Gradiente 8,5–77 % de proteína residual; aneuploidía clara por debajo del ~50 % (`Hum Genet` 2008, DOI 10.1007/s00439-008-0572-y) | HeLa shRNA | `L4` |
| **5** | aneuploidía → estrés proteotóxico y mitocondrial | T2-B | p62 citosólico con precursores mitocondriales, importación deficiente, ADNmt bajo, ROS alto (`Nat Commun` 16:5328, DOI 10.1038/s41467-025-60857-4) | células isogénicas | `L4` |
| **6** | subir HSP → rescate de ese estrés | T2-B | La **sobreexpresión genética** (HSP27, HSP90α, HSF1 WT y constitutivamente activo) redujo agregados y colocalización p62–TOMM20 — **pero el rescate dependió del cariotipo: una línea aneuploide no respondió igual** | células isogénicas | `L4`, **no universal** |
| **7** | coinducción **farmacológica** → el mismo rescate | T2-B | **UNRESOLVED.** Cero evidencia DIRECT; contraevidencia en otro sistema; **tensión mecanística no resuelta** | — | **L0** |
| **8** | la misma intervención → efecto sobre CIN y supervivencia clonogénica | ambas | **NUNCA MEDIDO** | — | **ausente** |

### El puente 3 es el hallazgo de esta auditoría

Se venía tratando la dependencia de HSP90 como si respaldara «subir chaperonas sube BUBR1».
**No lo hace.**

Lo demostrado (PMID 20516114) es que **inhibir** HSP90 desploma la abundancia de ciertos
mutantes missense de BUBR1 y no la del silvestre. Eso establece que **el mutante ya depende
del sistema de chaperonas para existir**. Es una afirmación sobre la dependencia basal.

> **Que quitar el soporte lo hunda no implica que añadir más soporte lo suba.** Un sistema
> puede estar ya saturado en su punto de trabajo. La inferencia inversa no está demostrada, y
> es el paso del que depende toda la ruta T2-A por vía de chaperonas.

### El puente 1 es el que conecta con ESTE paciente

Toda la cadena descansa en que el mutante **de este niño** sea inestable. Lo que hay es una
inferencia estructural —residuo enterrado, red de puentes de hidrógeno, pérdida
rotámero-independiente de un aceptor— y conservación ortóloga que la acompaña.

**Ninguna de las dos es una medición de abundancia.** Y REVEL, el único predictor calibrado
que se aplicó, salió indeterminado.

Es exactamente lo que `EXP-011b` mediría.

### El puente 7 — búsqueda acotada, cerrada como `UNRESOLVED`

Se buscó específicamente evidencia de que la **coinducción farmacológica** de HSP reproduzca
el rescate obtenido por **aumento genético** de HSP en células aneuploides. Clasificación
preacordada:

| Clase | Qué sería | Encontrado |
|---|---|---|
| **DIRECT** | células aneuploides + coinductor farmacológico + rescate relevante | **NINGUNA** |
| **NEAR** | coinducción farmacológica en otro contexto proteotóxico | Existe, pero **no se admite como sustituto** |
| **GENETIC** | solo sobreexpresión de HSP o HSF1 | Sí — es toda la evidencia del puente 6 |
| **CONTRADICTORY** | rescate genético **no** reproducido farmacológicamente | **Sí, y es decisiva** |

#### El contraejemplo, verificado

**Pipalia NH, Saad SZ, Subramanian K, et al. *J Lipid Res* 2021;62:100114. PMID 34481829 ·
DOI 10.1016/j.jlr.2021.100114.**

En fibroblastos NPC1 I1061T, la **sobreexpresión de HSP70 redujo el almacenamiento de
colesterol** — «incluso una pequeña cantidad de sobreexpresión de HSP70» bastó. **Arimoclomol
no lo reprodujo**, hasta **500 µM durante 72–120 h**. Y el detalle que más pesa:

> *«arimoclomol treatment by itself does not upregulate HSP70 expression in GM18453
> fibroblasts»*

**No es que el fármaco subiera HSP70 y no bastara: es que no subió HSP70.**

Esto demuestra literalmente, en un sistema humano de enfermedad, que
**`aumento genético de chaperona` ≠ `coinducción farmacológica`**.

#### Y hay una razón mecanística para esperar que falle EN CÉLULAS ANEUPLOIDES

**Donnelly N, Passerini V, Dürrbaum M, Stingele S, Storchová Z. *EMBO J* 2014;33(20):2374–2387.
PMID 25205676 · DOI 10.15252/embj.201488648.**

Las células aneuploides humanas **tienen deteriorada la capacidad de inducir la respuesta de
choque térmico**: la inducción de HSP70 quedó reducida al **50–60 %** del control en
aneuploides derivados de HCT116 y de RPE-1. Lo que sí rescató fue **HSF1 constitutivamente
activo**, que *«es suficiente para contrarrestar la función deteriorada de HSP90 de las células
aneuploides humanas»*.

> **CORRECCIÓN: esto es una TENSIÓN MECANÍSTICA, no evidencia en contra.**
>
> El deterioro de HSF1 hace **dos cosas a la vez**, y ambas hay que decirlas:
>
> | A favor | En contra |
> |---|---|
> | **Identifica el nodo.** Si la vía HSF1/chaperonas está deficiente y aumentarla rescata, esa vía **es** el punto de intervención correcto | **Hace incierta la farmacología.** Un coinductor depende de una respuesta HSF1 que la célula ya haya disparado, y esa respuesta está al 50–60 % |
>
> **No se puede concluir que un coinductor fallará.** Un coinductor **amplifica y prolonga** una
> respuesta ya iniciada; no exige una HSF1 intacta, y su mecanismo exacto no está del todo
> resuelto. Lo que sí se puede afirmar es que **el resultado es impredecible desde la evidencia
> actual**.
>
> **Formulación congelada:**
>
> > *HSF1 impairment makes the pathway both mechanistically relevant and pharmacologically
> > uncertain. Genetic augmentation can bypass the deficit; whether a stress-dependent
> > pharmacological co-inducer can amplify the impaired endogenous response sufficiently
> > remains unresolved.*

#### Consecuencia para Track 2, sin suavizar

Esto **no mata T2-B**, pero **cambia qué habría que buscar**. La clase farmacológica adecuada
para una célula con inducción de HSR deficiente probablemente **no es un coinductor
dependiente de estrés**, sino algo que puentee el nodo deficiente.

Y convierte el puente 7 en el **corazón falsable de Track 2**. La incertidumbre traslacional
central del proyecto se enuncia así:

> *The central translational uncertainty is whether pharmacological co-induction reproduces
> the rescue obtained by genetic HSP augmentation — in cells whose HSF1-dependent induction is
> itself impaired.*

Esa es una pregunta mucho mejor que «¿funciona arimoclomol?».

### El puente 8 no existe en ninguna dirección

Nadie ha medido qué le hace ninguna de estas intervenciones a la CIN o a la supervivencia
clonogénica de células aneuploides frente a euploides isogénicas. **Ese es el puente de
seguridad, y está vacío.**

---

## Reglas de sustitución prohibida

Tres errores concretos que este documento existe para impedir:

| Prohibido | Por qué |
|---|---|
| Usar la dependencia de HSP90 de **otros** mutantes de BUBR1 como evidencia de que **esta** variante es dependiente de HSP90 | Puentes 1 y 3 son distintos, y la evidencia disponible es de otros alelos |
| Usar el rescate por **sobreexpresión genética** de HSP como evidencia de que un **coinductor aprobado** lo reproduce | Puente 6 ≠ puente 7. Es el hueco farmacológico |
| Tratar el rescate del estrés proteotóxico como beneficio neto | Si aumenta la supervivencia de células con CIN, el puente 8 puede convertir el rescate en daño |

---

## El corredor de rescate seguro

El candidato bueno **no es el que más rescata**. Es el que mejora mecanismo o fenotipo **sin
aumentar la tolerancia clonal de células aneuploides**.

```
                    BENEFICIO
                        ↑
                        │
   T2-A                 │
   mas BUBR1            │   CORREDOR
   menos CIN NUEVA      │   DE RESCATE
                        │   SEGURO
   ─────────────────────┼──────────────────────→
                        │        mayor supervivencia
                        │        de celulas con CIN
   ZONA PROHIBIDA       │
   rescata, pero        │              T2-B
   hace viable el       │              tolerancia
   clon inestable       ↓
                    RIESGO ONCOLOGICO
```

**T2-A puede caer en el corredor. T2-B, por construcción, empuja hacia el eje de riesgo.**

> **Actualización tras la búsqueda del puente 7.** La posición de T2-B en este plano tiene ahora
> una incertidumbre añadida **antes incluso del eje de riesgo**: no se sabe si un coinductor
> llega siquiera a producir el efecto, porque la vía que amplifica está deteriorada en la
> célula diana. **T2-B podría no llegar a entrar en el plano.**

Eso no descarta T2-B: la coinducción es **dependiente de estrés**, no activación constitutiva,
y eso podría concentrar el efecto donde más se necesita. **Pero es una propiedad farmacológica
declarada, no una garantía demostrada en este contexto** — y el puente 8 está vacío
precisamente ahí.

## El experimento que decide, y por qué es la mejor diapositiva

**La señal de eficacia y la señal de riesgo oncológico son la misma medición.**

Si una intervención rescata preferentemente a las células **más** aneuploides, eso es a la vez
la prueba de que el mecanismo es el propuesto **y** la prueba de que se está mejorando la
supervivencia clonogénica de células genómicamente inestables.

Diseño mínimo aceptable — las dos mitades **a la vez**:

| Mitad de eficacia | Mitad de riesgo |
|---|---|
| p62 / TOMM20 | CIN |
| mtDNA-CN | proliferación |
| ROS | apoptosis |
| importación mitocondrial | **supervivencia clonogénica, aneuploide vs euploide isogénico** |

**Un diseño que mida solo la eficacia no es un experimento: es una demostración.**

## La compuerta del fármaco — condiciones, fijadas ahora

No se nomina candidato hasta que reúna **las cinco**:

1. **Estatus aprobado**, con perfil pediátrico viable
2. **Proximidad mecanística** a un puente concreto, nombrado
3. **Evidencia del puente relevante** — no de un puente vecino
4. **Predicción de rescate falsable**, con el número que la mataría
5. **Contra-test explícito de CIN / tumor** en el mismo diseño

Hoy **ningún candidato reúne las cinco**, porque los puentes 7 y 8 están vacíos.

## Estado de las rutas

> **Calibración del lenguaje.** Lo correcto es *«la modulación de proteostasis y chaperonas es
> la clase mecanística superviviente principal **entre las evaluadas**»*, **no** «la única que
> sobrevive». Lo segundo implicaría haber barrido el espacio terapéutico completo, y no se ha
> hecho: se evaluaron seis clases elegidas desde la cadena mecanística del caso.

| | Estado | Puente que la bloquea |
|---|---|---|
| **T2-A · rescate aguas arriba** | **ABIERTA · la más deseable** | **Puente 3** — la evidencia va en dirección contraria. Y el puente 1 la ancla a este paciente |
| **T2-B · tolerancia aguas abajo** | **ABIERTA · clase mecanística superviviente principal de las evaluadas** | **Puentes 7 y 8** — el hueco farmacológico y el contra-test que nadie hizo |
| Modulación del proteasoma | **NEGATIVE** | Sin fármaco aprobado con perfil aceptable; tolerancia dependiente de cariotipo |
| Poda clonal | **NEGATIVE** — cerrado en brief §13 | Sin inhibidor aprobado; antimitóticos inaceptables en un niño |
| Estabilización directa por acetilación | **PARKED** | Dos dianas opuestas en la misma proteína (`K250` vs `K668`) |
| Senolíticos | **PARKED** | Retrasan fenotipos sin aumentar esperanza de vida |

## El puente más débil, nombrado

**Para la traslación farmacológica: el puente 7.** Sin él, T2-B es una hipótesis sobre
biología, no sobre un fármaco.

**Para la conexión con este paciente: el puente 1.** Sin él, toda la cadena es sobre BUBR1 en
general, no sobre este niño.

**Y para la seguridad: el puente 8**, que no está débil — está **vacío**, y es el que decide si
la hipótesis entra en el corredor o solo hace que una célula aneuploide se sienta mejor.
