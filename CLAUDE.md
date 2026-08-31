# CLAUDE.md — Instrucciones operativas del proyecto

Proyecto: **Rare Disease, Real Kid — MVA Hackathon 2026**.
Análisis genómico de un paciente pediátrico real con sospecha de Mosaic Variegated Aneuploidy (MVA).

Antes de escribir código, lee en este orden:
1. `docs/01_MASTER_BRIEF.md` — contexto científico completo, hallazgos, evidencia y contraevidencia.
2. `docs/02_ANALYSIS_PLAN.md` — plan ejecutable por fases, con tablas de decisión preregistradas.
3. `docs/04_ARQUITECTURA_MAESTRA.md` — jerarquía científica vigente y regla de hipótesis competidoras. **Manda sobre cualquier módulo o idea previa.**

No empieces a programar sin haber leído los tres. El plan tiene un orden deliberado por coste-beneficio; ejecutarlo desordenado desperdicia días de cómputo.

---

## REGLAS DURAS

Estas no son preferencias. Romper cualquiera de ellas invalida el proyecto.

### 1. Datos del paciente — nunca en el repositorio

Se trata de información clínica real de un menor vivo cuya familia consintió compartir su historia. El documento fuente dice literalmente: *no redistribuir*, y *nada que pueda reidentificar al paciente o la familia más allá de lo que ya es público a través de las entradas del blog de la propia familia*.

Por tanto, **nunca** se commitean, ni siquiera temporalmente:
- FASTQ, BAM, CRAM, VCF, índices, o cualquier derivado que contenga genotipos
- El documento de fenotipo original (`Challenge_Clinical_Phenotype_1.docx`)
- Listas de variantes con coordenadas y genotipos del paciente
- Tablas de salida con IDs de muestra reales
- Logs que impriman rutas locales con nombres de usuario

`.gitignore` **no es un control de seguridad**. Si algo se commiteó una vez, sigue en el historial aunque borres el archivo. Antes del primer commit, verifica:

```bash
git log --all --numstat | awk '$1 ~ /^[0-9]+$/ {print $3}' | sort -u | \
  grep -Ei '\.(vcf|bam|cram|fastq|fq|gz|docx)$' || echo "limpio"
```

El repositorio debe ser **privado**. Confirma esto antes de escribir el primer archivo.

No busques a la familia. La mención de que tienen blog público es un vector de reidentificación, no una fuente.

### 2. Los datos viven fuera del repositorio

Todas las rutas van en `config/paths.yaml`, que está en `.gitignore`. El código nunca contiene rutas absolutas hardcodeadas. Hay un `config/paths.example.yaml` versionado con rutas ficticias.

### 3. Nada de recomendaciones clínicas

El entregable es una **hipótesis falsable para investigación preclínica**. Nunca:
- una pauta, una dosis, una recomendación de tratamiento
- la afirmación de que algo "trata", "cura" o "mejoraría" al paciente
- lenguaje que implique acción clínica

La forma correcta es: *"la hipótesis X predice Y; el experimento que la falsaría es Z"*.

### 4. Calibración del lenguaje: cero exageración

Este proyecto ya fue sometido a red-team y las exageraciones detectadas están documentadas en el brief. No repitas el patrón.

- Una medida derivada de cobertura de secuenciación **no** es "un ensayo funcional". Es un proxy genómico.
- Una correlación **no** es un mecanismo.
- Un score de CMap **no** es evidencia farmacológica.
- Un modelo **no** "descubre"; produce una predicción con incertidumbre.
- "Enormemente más potente" requiere una simulación que lo demuestre. Sin ella, es una hipótesis metodológica.

Etiqueta cada afirmación con su nivel de evidencia (ver `docs/01_MASTER_BRIEF.md`, §15): `L0` especulación, `L1` asociación, `L2` apoyo ortogonal, `L3` evidencia funcional, `L4` evidencia funcional replicada, `L5` evidencia humana/clínica establecida.

### 5. No inventes identificadores bibliográficos

Nunca escribas un PMID o un DOI que no hayas verificado en esta sesión. Si no lo tienes, escribe `PMID: no verificado` y sigue adelante. Un identificador inventado en un póster científico es descalificatorio.

### 6. Los resultados negativos se reportan

Este proyecto tiene tablas de decisión **preregistradas** en `docs/02_ANALYSIS_PLAN.md`. Están escritas antes de ver los datos precisamente para que un resultado negativo sea publicable en lugar de vergonzoso. Si una rama muere, se documenta que murió, con la evidencia. No se reorienta el análisis hasta que dé positivo.

### 7. Reproducibilidad desde cero

- Entorno bloqueado (`environment.yml` o `requirements.txt` con versiones fijas).
- Semillas fijas en cualquier proceso estocástico, declaradas en `config/`.
- Los notebooks **no** son fuente de verdad. El código vive en `src/`, los notebooks solo exploran.
- Todo paso pesado escribe un log con versión de herramienta, parámetros y checksum de entrada.

---

## CONVENCIONES

- **Documentación, comentarios y mensajes de commit: español.**
- **Nombres de archivos, funciones y variables: inglés**, por interoperabilidad con el ecosistema bioinformático estándar. (Si prefieres español también en el código, dilo y lo cambio; es tu repo.)
- Python 3.11+. `snakemake` o `nextflow` para el pipeline si crece; scripts numerados en `src/` si se mantiene simple.
- Salidas intermedias en `work/` (gitignored), entregables en `results/` (gitignored salvo figuras agregadas y no identificables).

## ESTRUCTURA

```
notebooks/                # LA INVESTIGACION: pregunta -> preregistro -> metodo ->
                          #   ejecucion -> falsacion -> decision -> siguiente experimento
src/                      # METODO REPRODUCIBLE, importable desde los notebooks
  qc/  annotation/  prioritization/  phase/  structure/  regulatory/  sv/  mosaic/
research/
  EXPERIMENT_REGISTRY.md  # donde esta la investigacion, en una pagina
work/                     # IGNORADO: datos sensibles y salidas completas
docs/                     # conclusiones saneadas
figures/                  # evidencia visual DERIVADA de los notebooks

CLAUDE.md
.gitignore
config/
  paths.example.yaml      # versionado, rutas ficticias
  paths.yaml              # IGNORADO, rutas reales
  panels/                 # listas de genes, versionadas
docs/
  00_KICKOFF.md           # prompt inicial para arrancar
  01_MASTER_BRIEF.md      # contexto científico completo
  02_ANALYSIS_PLAN.md     # plan ejecutable + decisiones preregistradas
  03_ALPHAGENOME_ASSESSMENT.md  # encaje, limites y decision de uso
  04_ARQUITECTURA_MAESTRA.md    # jerarquia vigente; manda sobre lo demas
  05_CONTRATO_VISUAL.md         # que figura debe cada hipotesis
  00_ESTADO_Y_OBSOLESCENCIA.md  # que sigue vigente y que quedo superado
  EVIDENCE.md             # tabla de evidencia viva; se actualiza al leer papers
  DECISIONS.md            # bitácora: qué se decidió, cuándo, por qué
src/
work/                     # IGNORADO
results/                  # IGNORADO por defecto
```

## FLUJO DE TRABAJO ESPERADO

1. Antes de una fase nueva, escribe en `docs/DECISIONS.md` qué esperas encontrar y qué resultado mataría la hipótesis. **Antes**, no después.
2. Ejecuta.
3. Registra el resultado, incluido si es negativo.
4. Si el resultado contradice lo preregistrado, no reescribas la predicción. Documenta la sorpresa.

## LO QUE NO HAY QUE HACER

- No alinees los 86 GB completos antes de leer la Fase 1 del plan. Hay atajos que ahorran días.
- No construyas un dashboard. La innovación no es la interfaz.
- No uses AlphaFold decorativamente. Si no hay una hipótesis estructural concreta, no lo uses.
- No trates el enriquecimiento de vías como mecanismo.
- No asumas *a priori* que el gen causal es `BUB1B`.
- No presentes una conexión generada por un LLM como evidencia. Toda cadena mecanística necesita una referencia primaria.
- No diseñes el proyecto hacia atrás desde un gen o un fármaco favorito. `BUB1B`, Bartter, estrés mitocondrial, señal de mosaicismo y cualquier candidato farmacológico siguen siendo hipótesis hasta que los datos del paciente los sostengan (`docs/04_ARQUITECTURA_MAESTRA.md`).
- No digas "reconstrucción de cariotipos" ni "cariotipos fantasma". El entregable de mosaicismo es un *bulk genomic mosaic fingerprint*.
- No llames "ensayo funcional" a MitoRead. Es un *orthogonal WGS-derived mitochondrial readout*.
- No mandes variantes estructurales a AlphaGenome. Las SV van a Manta / DELLY / GRIDSS.
- **Ninguna figura final sin un notebook o pipeline reproducible que haya generado el resultado.** Una figura no es evidencia hasta que tenga origen ejecutable. Ver `research/EXPERIMENT_REGISTRY.md`.
- No trates «documentado y visualizado» como equivalente a «investigación reproducible». No lo es.
- No abras Track 2 mientras EXP-006 (ranking genome-wide sin panel) siga en curso. Saltar de un panel a mecanismo es sesgo de confirmación.
- No termines un analisis importante solo en CSV o Markdown. Cada hipotesis acaba en una figura interpretable, una conclusion, una incertidumbre y un falsificador (`docs/05_CONTRATO_VISUAL.md`).
- No dibujes las predicciones de AlphaGenome como si fueran pistas medidas de un genome browser. La palabra PREDICHO va en el panel, no en el pie.
