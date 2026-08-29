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

### 4.1 Dosis residual funcional — **PURSUE**

La más fuerte de las seis, y por una razón que no es AlphaGenome.

El brief §3.2 contiene un **umbral cuantificado y publicado**: un gradiente de BubR1
residual (8,5 / 10 / 14 / 58 / 77 %) mostró PCS en todos los niveles pero
**aneuploidía clara solo por debajo del ~50 %** de proteína residual
(`Hum Genet` 2008, DOI 10.1007/s00439-008-0572-y).

Eso convierte una estimación difusa en una **pregunta binaria con umbral externo**:

> ¿La dosis funcional combinada de los dos alelos cae por encima o por debajo del 50 %?

Es preregistrable, tiene respuesta sí/no, y el umbral no lo elegimos nosotros. Conecta
además con el eje progeroide (brief §3.6): los ratones a ~10 % son progeroides, lo que
sugiere clases fenotípicas por nivel residual.

**Riesgo que hay que declarar:** encadena dos predicciones con incertidumbre no
conjunta — AlphaGenome para el alelo regulador, FoldX para el missense. El brief §12
ya documenta que ΔpLDDT correlaciona muy débilmente con ΔΔG (PCC ≈ −0,17). La salida
honesta es **una clase con intervalo** (severo / moderado / leve), nunca un porcentaje.

**Nivel de evidencia de la salida: L1.** Sube a L2 solo si una medida ortogonal
(p. ej. la huella de mosaicismo de la Fase 3) apunta en la misma dirección.

### 4.2 Segundo alelo oculto — **PURSUE, con techo declarado**

Ya está en el brief §9 y es la razón declarada de que entregaran FASTQ y no solo VCF.
La aportación de AlphaGenome es real: extiende la Fase 6.2 más allá del splicing.

**Techo innegociable (brief §9.1):** `unphased ≠ trans`. Sin genotipos parentales, y
salvo SNP heterocigoto puente dentro de la distancia de fragmento, la fase **queda sin
resolver**. Por tanto la afirmación permitida es:

> *"Se identificó un segundo candidato funcional en una región donde el pipeline
> estándar no busca. La fase permanece no resuelta."*

**No** se permite: *"dos mecanismos independientes dañando el mismo gen"*, porque eso
afirma configuración en trans sin poder demostrarla.

### 4.3 Panel renal no codificante — **PURSUE, pero después del email**

Extender el panel de nefrocalcinosis (Fase 1.2) al espacio no codificante es correcto:
si el segundo alelo de una tubulopatía recesiva es regulador, un panel de codificante
lo pierde.

**Pero el orden importa.** El brief §8.5 establece que esta hipótesis tiene **falsación
gratis**: alcalosis metabólica hipopotasémica e hipoclorémica, renina y aldosterona
elevadas, y cociente calcio/creatinina urinario ya están en la historia clínica. Y §8.4
establece que una sola pregunta —¿hubo polihidramnios u oligohidramnios?— decide entre
Bartter y MVA, porque son opuestos.

**Mandar el email antes de gastar cómputo.** Si la bioquímica es normal, la rama muere
sin coste. Si es compatible, se escala de inmediato (tabla de decisión, Fase 1.3).

### 4.4 Huella de mecanismo molecular — **CONDITIONAL, con una trampa de presentación**

Como entrada al enrutador mecanístico (Fase 2.5) es útil: distinguir pérdida de
expresión de alteración de splicing de disrupción de interfaz cambia qué estrategia
terapéutica es siquiera plausible.

**La trampa:** las salidas multimodales de AlphaGenome **no son rutas de evidencia
independientes**. Son varias salidas correlacionadas del mismo modelo. Presentarlas
como convergencia sería el error que `docs/research_protocol.md` §11 prohíbe.

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

Mantener como idea declarada L0. No construir el proyecto encima.

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

| # | Propuesta | Decisión | Fase | Nivel máximo alcanzable |
|---|---|---|---|---|
| 1 | Dosis residual funcional | **PURSUE** | 2.5 + 6.2 | L1 → L2 con apoyo ortogonal |
| 2 | Segundo alelo oculto | **PURSUE** | 6.2 | L1, fase no resuelta |
| 3 | Panel renal no codificante | **PURSUE tras email** | 1.2 | L1 |
| 4 | Huella de mecanismo | **CONDITIONAL** | 2.5 | L0, es una predicción |
| 5 | Palanca reguladora | **PARK** | — | L0 |
| 6 | Caza de modificadores | **REJECT** | — | — |

---

## §6. Límites de uso — no negociables

Por analogía directa con la regla de AlphaFold del brief (§15) y con `docs/claims_we_cannot_make.md`:

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
- usarlo sobre variantes estructurales complejas o combinaciones de múltiples variantes,
  donde el propio modelo tiene limitaciones reconocidas.

**Lenguaje obligatorio:** *"AlphaGenome predice X"*, nunca *"AlphaGenome demuestra X"*.
Un modelo no descubre; produce una predicción con incertidumbre (CLAUDE.md, Regla Dura 4).
