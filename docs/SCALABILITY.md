# Escalabilidad — qué se transfiere a otro caso y qué no

> **Por qué existe este documento.** La escalabilidad pesa **15 %** en la evaluación oficial
> del hackathon, y hasta ahora este repositorio no la respondía: explicaba muy bien **un**
> caso y dejaba implícito qué parte del método sobreviviría a cambiar de paciente o de
> enfermedad. Implícito no es una respuesta.
>
> La regla que se sigue aquí es la misma que en el resto del proyecto: **se mide, no se
> afirma**. Y donde algo NO escala, se dice.
>
> **Qué mide el número de abajo, exactamente.** Que el 39 % del código actual es agnóstico al
> caso **bajo un censo léxico conservador**. No que el proyecto sea «un 39 % escalable». La
> escalabilidad real incluye qué entradas se pueden sustituir, cuántos módulos dependen de
> `BUB1B` o del fenotipo MVA en concreto, y qué partes reutilizan maquinaria genérica de HPO y
> VCF — nada de eso lo puede responder una búsqueda de texto. Es un **proxy técnico**, y como
> tal se presenta.

## La medida, primero

Recuento sobre `src/`, buscando menciones a lo específico del caso (`BUB1B`, `BUBR1`, `MVA`,
nefrocalcinosis, los tres compuestos, `HSF1`, OMIM 257300):

| | módulos | líneas |
|---|---:|---:|
| **Sin ninguna mención al caso** — se transfieren tal cual | **41** | **6 554** |
| Con menciones al caso — hay que adaptarlos | 38 | 8 573 |
| Total | 84 | 16 757 |

**El 39 % de las líneas de `src/` no sabe que este paciente existe.** Ese es el **suelo**, no
el techo, por dos motivos: la medida es de dependencia **textual**, y buena parte de los 38
módulos restantes solo nombra el caso en títulos de figura y cadenas de texto, no en la
lógica.

> **Estas cinco cifras las recalcula `src/verify.py`** y el control falla si este documento y el
> censo dejan de coincidir. La versión anterior publicaba 29 de 65, 4 214 de 11 818 y 36 % bajo
> el encabezado *«medido, no afirmado»*, y llevaba meses sin cuadrar con el comando que la propia
> frase invitaba a ejecutar. Un número escrito a mano en un documento que dice «medido» se queda
> obsoleto en silencio. Si duda, el censo cuenta como específico, para que el número de genéricos no se
infle.

Reproducir el recuento:

```bash
python src/scalability_census.py
```

---

## Capa 1 · Transferible sin tocar nada

Funciona sobre **cualquier** paciente único con WGS, sin importar el gen ni la enfermedad.

| Componente | Qué hace | Por qué es genérico |
|---|---|---|
| `src/prioritization/genome_wide.py` | Priorización codificante sin panel, con cigosidad, calidad y frecuencia | No contiene ningún gen. El panel es un **argumento**, no una constante |
| `src/prioritization/allele_key.py` | Cruce de alelos entre VCF y anotación | Puro problema de identidad de alelo |
| `src/phenotype/run_mode_b.py` | Resnik + *Best Match Average* sobre HPO | El fenotipo entra por YAML |
| `src/qc_fastq_sample.py` · `src/vcf_variant_census.py` · `src/vcf_header_audit.py` | Aptitud del dato antes de analizarlo | Preguntas sobre el fichero, no sobre la enfermedad |
| `src/baseline/fetch_exomiser.py` | Línea base **externa e independiente** sobre el mismo VCF | Protege del sesgo de panel en cualquier caso |
| `src/sanitize_scan.py` | Escáner de fuga: patrones estructurales (coordenadas, HGVS, genotipos, rutas locales) + valores prohibidos del caso | Los patrones son universales; los valores del caso se cargan de un fichero ignorado |
| `src/figures/style.py` | Estándar de figura: paleta apta para daltonismo, escala tipográfica, **los dos ejes de metadatos**, exportación determinista | No sabe de biología |
| `src/nb/nbutil.py` · `src/nb/figlib.py` | Construcción y verificación de notebooks; una figura **solo cuenta si está embebida y declara su clase** | Contabilidad, no ciencia |
| `src/verify.py` | Un comando: tests, importaciones, conteos publicados, ambas matrices, ambos controles | Los checks son estructurales |
| `src/structure/pocket_geometry.py` · `clades.py` | Vecindad, enlaces de hidrógeno candidatos, pLDDT; robustez filogenética | Geometría sobre un PDB cualquiera |

## Capa 2 · El método, que es lo que de verdad escala

Esto no es código: son **plantillas de razonamiento**. Es la parte que valdría la pena copiar
aunque se tirara todo el repositorio.

**1 · El congelado que no se reescribe.** `A0` se preregistró y dio `BUB1B` **#4**.
`A0-FREQFIX` es una sensibilidad **posterior** y lo devuelve al **#1**. Los dos números se
reportan siempre juntos. Cualquier proyecto puede adoptar la regla: *el ranking congelado no
se toca cuando el resultado incomoda*.

**2 · La matriz de puentes.** Descomponer «este gen causa la enfermedad, luego este fármaco
ayudará» en **N puentes explícitos × 10 dimensiones de evidencia**, con vocabulario cerrado
(`DIRECT` / `NEAR` / `GENETIC` / `CONTRADICTORY` / `ABSENT`) y la **regla dura de que ninguna
celda no vacía puede quedarse sin fuente**. Aquí produjo 8 × 10 = 80 celdas, **61 vacías**.
Cambia la enfermedad, cambian los puentes; la estructura y la regla no.

**3 · La cartera con papeles, en vez de un ranking.** `ALLELE` / `SENTINEL` / `ADVERSARIAL` /
`CONTROL`. Elimina la pregunta equivocada («¿cuál es el mejor?») y la sustituye por la útil
(«¿qué muere si cada uno falla?»). Cada brazo lleva su **regla de descarte escrita por
adelantado**.

**4 · La auditoría barata de competidores.** Orden de agotamiento: **frecuencia → cigosidad →
mecanismo → replicación**. Mató a `CTU2`/`PEX5`/`SLC22A1` por frecuencia, a `FANCD2` por
frecuencia y cigosidad, a `LZTR1` por cigosidad y mecanismo, a `IGBP1` por mecanismo y
frecuencia. El orden importa: lo barato primero.

**5 · La regla de polaridad del fenotipo.** *Lo no documentado es **desconocido**, nunca
negativo.* Impide el descarte más común y más silencioso en genética clínica.

**6 · El registro de contradicciones.** 13 entradas contra nuestras propias ideas preferidas,
con gravedad y decisión. Incluye las veces que **nos equivocamos** y lo dice.

**7 · Los dos ejes de metadatos de figura.** `FIGURE CLASS` (qué tipo de objeto es) y
`EVIDENCE ORIGIN` (de dónde viene lo de dentro), declarados por separado o no hay exportación.
Impide que una simulación se lea como dato de paciente.

## Capa 3 · Específico de este caso — **no** escala, y hay que decirlo

| Componente | Por qué no transfiere |
|---|---|
| `src/mosaic/simulate_dispersion.py` (cancelación de BAF) | El mecanismo depende de que el mosaicismo sea **variegado**: homólogo distinto por linaje, contribuciones que se cancelan. En mosaicismo **clonal** el BAF **no** se cancela y la simulación no aplica. Transfiere a otras condiciones variegadas, no al mosaicismo en general |
| Los ocho puentes concretos | La *estructura* escala; el contenido (chaperonas → BUBR1) es de este mecanismo |
| El brazo de readthrough | Exige un **codón de parada prematuro**. Sin alelo truncante, no hay brazo `ALLELE` |
| `src/figures/fig03_pocket.py` (bolsillo + conservación) | Exige una missense en un dominio modelable y una hipótesis estructural concreta. `CLAUDE.md` prohíbe usar AlphaFold decorativamente |
| `src/mito/pilot_l001.py` (MitoRead) | Genérico en principio, pero **no calibrado**: hoy es un prototipo, no una medida. Transferir un prototipo sin calibrar sería propagar el problema |
| Las listas de genes de `config/panels/` | Específicas de MVA y de tubulopatías renales |

## Qué habría que tocar para el paciente siguiente

Cinco ficheros, y ninguno es código:

1. `config/paths.yaml` — rutas del dataset nuevo.
2. `config/phenotype_v2.yaml` — los términos HPO, con su procedencia y la regla de polaridad.
3. `config/panels/` — solo si se quiere una comparación con panel; el camino principal **no
   usa panel**.
4. `research/track2_evidence.tsv` — los puentes del mecanismo nuevo.
5. `research/track2_candidates.tsv` — los candidatos nuevos; **los papeles se conservan**.

Y una decisión humana: qué se congela como `A0` **antes** de mirar.

## Los límites honestos de esta escalabilidad

- **No está probado en un segundo paciente.** Todo lo anterior es una afirmación de
  arquitectura, respaldada por el recuento de dependencias, **no** por una segunda ejecución.
  Sería el primer experimento para demostrarla.
- **El pipeline solo ve variantes codificantes de SNV/indel.** SV, CNV y reguladoras siguen
  fuera del alcance, aquí y en cualquier caso al que se transfiera.
- **Sin genotipos parentales no hay fase.** Esa limitación viaja con el método.
- **El escáner de privacidad depende de una lista de valores del caso** que vive fuera del
  repositorio. En otra máquina comprueba patrones estructurales, no valores concretos, y eso
  se declara en cada ejecución.
