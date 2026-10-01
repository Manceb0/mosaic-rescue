# AlphaGenome — evaluación de encaje y decisión de uso

> Estado: **propuesta, no ejecutada.** Ninguna afirmación de este documento se ha
> comprobado sobre los datos del paciente. Ver `docs/DECISIONS.md` para el registro
> de lo que se decida antes de cada fase.

Complementa `docs/01_MASTER_BRIEF.md`. El brief planea `SpliceAI` (Fases 2.2 y 6.2)
y no menciona AlphaGenome. Este documento evalúa si añadirlo, dónde, y con qué límites.

---

## §1. El hueco que justifica su uso

El dataset **no contiene RNA-seq** (brief §1). Eso significa que no podemos *medir*
expresión ni splicing en este paciente: solo inferirlos desde secuencia.

AlphaGenome predice desde secuencia, con contexto de hasta 1 Mb, sobre expresión
génica, splicing, accesibilidad de cromatina, modificaciones de histonas, unión de
factores de transcripción y contactos de cromatina.

**Ese es el encaje, y es estructural, no decorativo:** ocupa el lugar de una modalidad
que el dataset no tiene. Sin ese argumento, su uso caería bajo la prohibición explícita
del brief §15 ("usar AlphaFold decorativamente"), aplicada por analogía.

### Referencia

Avsec et al., *Advancing regulatory variant effect prediction with AlphaGenome*,
**Nature 649(8099):1206-1218, enero 2026**. Iguala o supera a los mejores modelos
externos en **25 de 26** evaluaciones de efecto de variante. ✔ verificado.

---

## §2. Por qué no sustituye a SpliceAI, sino que lo complementa

Esta es la justificación operativa. No es "un modelo mejor": es cobertura distinta.

| Consecuencia posible del segundo alelo | SpliceAI | AlphaGenome |
|---|---|---|
| Alteración de sitio de splicing | **Sí** (especializado) | Sí |
| Intrónica profunda → junción críptica | **Sí** | Sí |
| Promotor → caída de expresión | No | **Sí** |
| Enhancer / contacto regulatorio | No | **Sí** |
| Unión de TF | No | **Sí** |
| Accesibilidad de cromatina | No | **Sí** |

AlphaGenome **no ganó todos** los benchmarks de splicing. SpliceAI sigue siendo la
herramienta específica para lo suyo. Se usan **juntos**: SpliceAI cubre splicing,
AlphaGenome cubre el resto del espacio regulador, donde SpliceAI es ciego.

---

## §3. Dónde entra en el plan

Modificación propuesta a `docs/02_ANALYSIS_PLAN.md`:

- **Fase 2.2** (anotación y priorización) — sin cambios. SpliceAI sigue siendo crítico
  dado el patrón de alelos de sitio de splicing canónico en `BUB1B` (brief §3.2).
- **Fase 6.2** (segundo hit no codificante) — **añadir AlphaGenome junto a SpliceAI.**
  Es la fase que existe precisamente para el problema del segundo hit ausente (brief §9).

No entra en ninguna otra fase. En particular **no** se usa para nominar fármacos
(ver §6 de este documento).

---

## §4. Las seis propuestas, evaluadas

Orden por relación valor/riesgo, no por atractivo.

### 4.1 Dosis residual funcional — **PURSUE CONDICIONAL**

> **Corregido.** La primera version de este documento la puso en el puesto #1 absoluto.
> Es un error: el umbral que la sostiene es especifico de BubR1, no universal.

El brief §3.2 contiene un **umbral cuantificado y publicado**: un gradiente de BubR1
residual (8,5 / 10 / 14 / 58 / 77 %) mostro PCS en todos los niveles pero
**aneuploidia clara solo por debajo del ~50 %** de proteina residual
(`Hum Genet` 2008, DOI 10.1007/s00439-008-0572-y).

Ese umbral es **evidencia BUBR1-especifica**. No existe un gradiente equivalente
publicado para `TRIP13` ni para `CEP57`. Si Track 1 termina apuntando a otro gen, la
pregunta pierde su ancla externa y se convierte en una estimacion nuestra — justo lo que
el umbral publicado evitaba.

**Condicion de activacion (preregistrada):**

> Se activa **solo si** Track 1 resuelve a `BUB1B` **y** existe al menos una variante
> reguladora, de splicing o de dosis sobre la que AlphaGenome aporte informacion que la
> anotacion estandar no da.

Si Track 1 resuelve a otro gen: la rama no se ejecuta, y se documenta por que
(Regla Dura 6).

**Dos prohibiciones sobre la salida:**

1. **Ningun porcentaje.** AlphaGenome no devuelve "este alelo deja un 37 % de proteina".
   Predice cambios en expresion, splicing, cromatina y union de TF. Convertir eso en un
   porcentaje de proteina es falsa precision, y cae bajo la Regla Dura 4.
2. **Clase, no numero.** La salida honesta es `severo / intermedio / leve`, comparada
   *cualitativamente* contra el gradiente publicado. El brief §12 ya documenta que
   ΔpLDDT correlaciona muy debilmente con ΔΔG (PCC ≈ −0,17): encadenar predicciones sin
   incertidumbre conjunta produce numeros que parecen medidas y no lo son.

**Nivel de evidencia: L1.** Sube a L2 solo con apoyo ortogonal independiente.

**Lo que si produce, si se activa,** es una pregunta terapeutica bien formada: *¿la
magnitud de rescate plausible del candidato mueve el sistema hacia una region mas
estable del gradiente?* — que es mas fuerte que "el farmaco sube la proteina".

### 4.2 Segundo alelo oculto — **PURSUE. Prioridad general #1**

> **Corregido.** Sube al primer puesto. Razon: es la unica de las seis que **no depende
> de saber el gen causal**. Se puede ejecutar en cuanto Track 1 entregue un alelo obvio
> sin pareja, sea cual sea el gen.

Ya esta en el brief §9 y es la razon declarada de que entregaran FASTQ y no solo VCF.
La aportacion de AlphaGenome es real: extiende la Fase 6.2 mas alla del splicing, con
contexto de hasta 1 Mb sobre expresion, cromatina y union de TF.

**Enrutado obligatorio por tipo de variante.** AlphaGenome esta disenado para SNV e
indels relativamente proximos a la referencia. **No es la herramienta para SV grandes.**

| Hallazgo | Herramienta |
|---|---|
| SV / CNV grande, breakpoints | **Manta, DELLY, GRIDSS** + evidencia de reads (pares discordantes, split reads) |
| SNV / indel intronico profundo | **SpliceAI** (splicing) + **AlphaGenome** (resto) |
| SNV / indel promotor, enhancer, UTR | **AlphaGenome** |

No mezclar. Mandar una SV a AlphaGenome produce una salida que parece informativa y no
lo es.

**Techo innegociable (brief §9.1):** `unphased ≠ trans`. Sin genotipos parentales, y
salvo SNP heterocigoto puente dentro de la distancia de fragmento, la fase **queda sin
resolver**. AlphaGenome tiene soporte para evaluar multiples variantes en un haplotipo
dentro de 1 Mb, pero **eso no significa que conozca el haplotipo del paciente**: se le
suministra una hipotesis de haplotipo, no se la infiere.

Afirmacion permitida:

> *"Se identifico un segundo candidato funcional en una region donde el pipeline
> estandar no busca. La fase permanece no resuelta."*

**No** se permite: *"mecanismo heterocigoto compuesto confirmado"* ni *"dos mecanismos
independientes danando el mismo gen"*.

### 4.3 Panel renal no codificante — **PURSUE, pero después del email**

Extender el panel de nefrocalcinosis (Fase 1.2) al espacio no codificante es correcto:
si el segundo alelo de una tubulopatía recesiva es regulador, un panel de codificante
lo pierde.

**Pero el orden importa.** El brief §8.5 establece que esta hipótesis tiene **falsación
gratis**: alcalosis metabólica hipopotasémica e hipoclorémica, renina y aldosterona
elevadas, y cociente calcio/creatinina urinario ya están en la historia clínica. Y §8.4
establece que el líquido amniótico discrimina entre Bartter y MVA.

**Corrección sobre §8.4.** El líquido amniótico es evidencia fuerte, **no un test
absoluto**. Polihidramnios severo precoz apoya mucho una tubulopatía perdedora de sal;
oligohidramnios apunta en otra dirección. Pero un dato obstétrico aislado no cierra una
etiología, y tratarlo como dicotomía binaria es el atajo que la Regla Dura 4 prohíbe.
Se usa para **ponderar**, no para decidir.

**Corrección de peso sobre MAGED2 — cambia la prioridad del panel.** El síndrome de
Bartter antenatal por `MAGED2` es, por definición, **transitorio**: las manifestaciones
desaparecen por completo en los primeros meses de vida (Laghmani et al.,
*N Engl J Med* 2016;374(19):1853-63, PMID 27120771 ✔ verificado en sesión).

Eso invierte la lectura ingenua. Si la nefrocalcinosis del paciente es **persistente**,
`MAGED2` se vuelve **menos** probable, no más — por bien que explique el periodo
perinatal. La persistencia empuja hacia tubulopatías que **no** remiten: `SLC12A1`,
`KCNJ1`, `CLCNKB`, `BSND`, o una causa no-Bartter del panel.

`MAGED2` sigue en el panel por el eje perinatal (polihidramnios severo precoz,
prematuridad), pero deja de ser el primer candidato si la afectación renal continúa hoy.

**Segunda corrección, sobre cómo se lee el fenotipo.** La ausencia de microcefalia,
discapacidad intelectual u otros rasgos clásicos de MVA en el documento **no es un
negativo clínico**. El documento no declara ser exhaustivo. Ausencia de mención ≠
ausencia del rasgo. Tratarla como evidencia en contra sería fabricar un dato.

> **Nota L0, declarada como especulación.** `MAGED2` está en Xp11.2 y su proteína
> transloca al nucleoplasma bajo estrés nucleolar; se le atribuye un papel en regulación
> del ciclo celular. Es un gancho llamativo junto a un fenotipo de inestabilidad
> cromosómica, y por eso mismo hay que etiquetarlo: **coincidencia interesante, no
> evidencia de conexión mecanística.** No construir nada encima sin hallazgo en el VCF.

**Mandar el email antes de gastar cómputo.** Si la bioquímica es normal, la rama muere
sin coste. Si es compatible, se escala de inmediato (tabla de decisión, Fase 1.3).

### 4.4 Huella de mecanismo molecular — **CONDITIONAL, con una trampa de presentación**

Como entrada al enrutador mecanístico (Fase 2.5) es útil: distinguir pérdida de
expresión de alteración de splicing de disrupción de interfaz cambia qué estrategia
terapéutica es siquiera plausible.

**La trampa:** las salidas multimodales de AlphaGenome **no son rutas de evidencia
independientes**. Son varias salidas correlacionadas del mismo modelo. Presentarlas
como convergencia sería contar dos veces la misma evidencia.

Etiquetado obligatorio: *"perfil de predicción de un modelo"*, nunca *"convergencia de
evidencia"*.

**Nota de visualización:** un gráfico de radar con seis ejes en escalas no comparables
codifica magnitud como área y exagera diferencias. Usar barras divergentes o un heatmap
por modalidad.

### 4.5 Palanca reguladora farmacológica — **PARK (L0)**

La cadena propuesta es: variante → predicción de mecanismo regulador → identificar TF →
fármaco aprobado que module ese TF → que suba el gen correcto → en el tejido correcto →
sin efectos fuera de diana. Siete eslabones, cada uno multiplicando incertidumbre.

Dos problemas estructurales, no de ejecución:

1. **Especificidad inexistente.** Un fármaco que modula un factor de transcripción lo
   modula globalmente, sobre todos sus targets. La especificidad paciente-específica que
   la idea promete no existe farmacológicamente.
2. **Colisión oncológica amplificada.** El brief §10.3 ya documenta que proponer un
   coinductor de HSF1 en un niño con antecedente de rabdomiosarcoma va en dirección
   contraria a la oncología. Un modulador transcripcional general agrava exactamente ese
   problema.

Se mantiene como investigación de techo alto y probabilidad baja: *jackpot
investigation*, no columna vertebral. Si aparece una conexión excepcionalmente limpia
—un TF con modulador aprobado y efecto dominante sobre el gen correcto en el tejido
correcto— vuelve a subir. Mientras tanto, el proyecto no se construye encima.

### 4.6 Búsqueda de modificadores reguladores — **REJECT**

n=1 sin cohorte de comparación. Cualquier genoma humano contiene miles de variantes
reguladoras raras; `gnomAD` da frecuencia poblacional, no efecto fenotípico. Sin una
cohorte de pacientes MVA con fenotipos divergentes no hay forma de atribuir *este*
fenotipo a *ese* modificador.

Produciría una lista de candidatos sin ruta de validación — precisamente lo que el
brief §13 identifica como el patrón a evitar. Se documenta como rama rechazada, con el
motivo, siguiendo la Regla Dura 6.

---

## §5. Resumen de decisiones

Orden corregido respecto a la primera versión. El criterio es **cuándo se puede
ejecutar**, no cuánto promete.

| # | Propuesta | Decisión | ¿Necesita conocer el gen causal? | Fase | Nivel máximo |
|---|---|---|---|---|---|
| 1 | **Segundo alelo oculto** | **PURSUE — prioridad general** | **No** | 6.2 | L1, fase no resuelta |
| 2 | Dosis residual funcional | **PURSUE CONDICIONAL** — solo si Track 1 → `BUB1B` | **Sí** | 2.5 + 6.2 | L1 → L2 con apoyo ortogonal |
| 3 | Panel renal no codificante | **PURSUE tras el email** | No | 1.2 | L1 |
| 4 | Huella de mecanismo | CONDITIONAL | Sí | 2.5 | L0, es una predicción |
| 5 | Palanca reguladora | EXPLORATORIO | Sí | — | L0 |
| 6 | Caza de modificadores | **REJECT** | — | — | — |

El cambio en una línea: **#1 se ejecuta en cuanto haya un alelo huérfano, sea cual sea el
gen; #2 necesita que el gen sea `BUB1B` para tener umbral externo.**

## §6. Límites de uso — no negociables

Por analogía directa con la regla aplicada a AlphaFold en este proyecto:

**Se permite** usar AlphaGenome para:
- priorizar variantes no codificantes que de otro modo no se examinarían;
- generar una hipótesis mecanística concreta sobre *cómo* una variante rompe un gen;
- decidir qué rama del enrutador mecanístico se activa.

**No se permite:**
- presentar una predicción como medida. No hay RNA-seq: no medimos expresión, la inferimos;
- afirmar patogenicidad a partir de la predicción sola;
- tratar las salidas multimodales como evidencia convergente;
- nominar un fármaco a partir de una predicción regulatoria (ver §4.5);
- afirmar configuración en trans que la fase no resuelve (ver §4.2);
- usarlo sobre variantes estructurales: las SV van a **Manta / DELLY / GRIDSS** con
  evidencia de reads, nunca a AlphaGenome;
- **derivar un porcentaje de proteína residual** de una predicción regulatoria. La salida
  es una clase (`severo / intermedio / leve`), nunca una cifra;
- tratar el soporte multi-variante en 1 Mb como conocimiento del haplotipo del paciente:
  se le pasa una hipótesis de fase, no la infiere.

**Lenguaje obligatorio:** *"AlphaGenome predice X"*, nunca *"AlphaGenome demuestra X"*.
Un modelo no descubre; produce una predicción con incertidumbre (CONTRIBUTING_RESEARCH.md, Regla Dura 4).

---

## §7. Acceso y disciplina de uso

La clave vive en `.env` (gitignored), leída como `ALPHAGENOME_API_KEY`. Nunca en código,
nunca en un notebook, nunca en un log. `config/paths.example.yaml` documenta que la
variable existe, sin el valor.

**Volumen.** La API está orientada a lotes pequeños y medianos —del orden de miles de
predicciones, no barridos de millones de variantes—. Entra **solo la shortlist
priorizada** de la Fase 6.2, nunca el VCF completo.

No es solo una restricción técnica: mandar millones de variantes produciría exactamente
la lista de candidatos sin ruta de validación que el brief §13 marca como el patrón a
evitar, y que motivó el REJECT de §4.6.
