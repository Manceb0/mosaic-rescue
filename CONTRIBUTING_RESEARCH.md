# Contributing Research

MOSAIC RESCUE is a scientific hypothesis project, not an idea dump. Contributions should make the final causal chain stronger or reveal why a current hypothesis is wrong.

## Contribution template

### Claim
State the claim in one sentence.

### Why it matters
Explain what decision this would change.

### Evidence
List primary papers, datasets, or functional screens.

### Evidence level
Use L0 (speculation), L1 (associative), L2 (orthogonal support), L3 (functional evidence), L4 (replicated functional evidence), or L5 (clinically established in humans). Do not upgrade evidence because a result is exciting.

### Required patient data
State the exact modality needed: VCF, BAM/CRAM, bulk RNA-seq, scRNA-seq, proteomics, clinical karyotype, etc.

### Alternative explanation
What else could generate the same observation?

### Falsification test
What result would make us reject this claim?

### Independent validation
Which external dataset or perturbation experiment can test it?

### Safety consequence
Could this mechanism increase CIN, abnormal clonal fitness, apoptosis escape, proliferation, or tumor risk?

### Best visualization
What figure would make the phenomenon obvious to a domain scientist?

## Patient data handling

The hackathon dataset is gated and identifiable. It lives in `data/`, which is
git-ignored in full, and it stays on the machine that downloaded it.

Non-negotiable:

- Never commit anything from `data/`. Never copy patient-level values into
  `docs/`, `research/`, `hypotheses/`, or a notebook cell that gets committed.
- Never send a gated file to a third-party service — no LLM API, no web tool,
  no hosted notebook, no pastebin. Work on streams #2 through #8 (external
  literature and public datasets) must follow these rules: it does not need the
  patient files and must not be given them.
- Report aggregates, not individuals. "17 de novo variants, 3 in dosage-sensitive
  genes" is publishable here; a genotype at a named position is not.

### Strip notebook outputs before committing

An executed `.ipynb` stores its outputs inside the file. A cell that prints a
variant table leaks that table into git even though the source file is ignored.
Clear outputs before staging:

```bash
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```

To make this automatic for everyone who clones the repo:

```bash
git config filter.strip-nb.clean "jupyter nbconvert --clear-output --to notebook --stdin --stdout" && git config filter.strip-nb.smudge cat && echo "*.ipynb filter=strip-nb" >> .gitattributes
```

If you find patient data already committed, do not just delete it in a new
commit — the blob stays in history. Say so immediately so the history can be
rewritten and the repo treated as exposed.

## Merge standard

A contribution should improve at least one of these:

- causal variant confidence
- mechanism resolution
- patient-as-screen validity
- bulk genomic mosaic fingerprint
- fitness landscape estimation
- synthetic rescue evidence
- forecast calibration
- rescue replay
- safe rescue corridor
- drug mechanism convergence
- pharmacogenomic or pediatric context
- falsifiability
- experimental design

Novelty alone is insufficient. Evidence alone is insufficient. We want useful convergence.

## Reglas duras

Estas reglas son de obligado cumplimiento: romper cualquiera invalida el trabajo. Las referencias del
repositorio a «Regla Dura N», a la «regla de A0», a las «Prácticas no permitidas» o a las
«Convenciones» remiten a esta sección.

### Regla Dura 1 · Datos del paciente, nunca en el repositorio

Es información clínica real de un menor vivo; la familia consintió compartir su historia con la
condición de no redistribuir nada que pueda reidentificarle. Nunca se versionan, ni siquiera
temporalmente: FASTQ, BAM, CRAM, VCF, índices ni derivados con genotipos; el documento de fenotipo
original; listas de variantes con coordenadas y genotipos del paciente; tablas con identificadores de
muestra reales; logs con rutas locales que incluyan nombres de usuario. `.gitignore` no es un control de
seguridad: lo que entra en el historial permanece aunque se borre. El repositorio es privado. No se
busca a la familia.

### Regla Dura 2 · Los datos viven fuera del repositorio

Todas las rutas van en `config/paths.yaml` (ignorado); `config/paths.example.yaml` se versiona con rutas
ficticias. El código no contiene rutas absolutas.

### Regla Dura 3 · Nada de recomendaciones clínicas

El entregable es una hipótesis falsable para investigación preclínica. Nunca una pauta, una dosis ni una
recomendación de tratamiento, ni la afirmación de que algo trata, cura o mejoraría al paciente. Forma
correcta: «la hipótesis X predice Y; el experimento que la falsaría es Z».

### Regla Dura 4 · Lenguaje calibrado

Una medida derivada de cobertura es un proxy genómico, no un ensayo funcional; una correlación no es un
mecanismo; un score de CMap no es evidencia farmacológica; un modelo produce una predicción con
incertidumbre, no «descubre»; una afirmación de superioridad metodológica exige una simulación que la
demuestre. Cada afirmación lleva su nivel de evidencia (L0–L5, arriba).

### Regla Dura 5 · No inventar identificadores bibliográficos

Ningún PMID ni DOI que no se haya verificado en la sesión de trabajo. Si no está verificado, se escribe
`PMID: no verificado`.

### Regla Dura 6 · Los resultados negativos se reportan

Las tablas de decisión se preregistran antes de ver los datos. Si una rama muere, se documenta con la
evidencia; no se reorienta el análisis hasta que dé positivo.

**Flujo de trabajo.** Antes de una fase nueva se escribe en `docs/DECISIONS.md` qué se espera encontrar y
qué resultado mataría la hipótesis; después se ejecuta; se registra el resultado, incluido si es
negativo; si contradice lo preregistrado, no se reescribe la predicción: se documenta la sorpresa.

### Regla Dura 7 · Reproducibilidad desde cero

Entorno con versiones fijas; semillas fijas declaradas en `config/`; los notebooks no son fuente de
verdad (el código vive en `src/`); todo paso pesado registra versión de la herramienta, parámetros y
checksum de la entrada.

### Regla de A0

El ranking `A0` congelado (BUB1B en el puesto 4) no se reescribe. `A0-FREQFIX` es una sensibilidad
posterior; los dos números se reportan siempre juntos. Prohibido narrar que BUB1B «siempre fue #1».

### Prácticas no permitidas

- Ninguna figura final sin un notebook o pipeline reproducible que haya generado el resultado;
  «documentado y visualizado» no equivale a «reproducible».
- No usar AlphaFold de forma decorativa: solo con una hipótesis estructural concreta.
- No tratar el enriquecimiento de vías como mecanismo.
- Ninguna cadena mecanística se presenta como evidencia sin referencia primaria.
- No asumir a priori el gen causal ni diseñar hacia atrás desde un gen o un fármaco favorito.
- No hablar de «reconstrucción de cariotipos» ni de «cariotipos fantasma»: el entregable de mosaicismo
  es una huella genómica agregada (bulk genomic mosaic fingerprint).
- MitoRead no es un «ensayo funcional»: es una lectura mitocondrial ortogonal derivada del WGS.
- Las variantes estructurales no se envían a AlphaGenome; sus predicciones llevan la palabra PREDICHO en
  el panel.
- Cada hipótesis importante termina en una figura interpretable, una conclusión, una incertidumbre y un
  falsificador.

### Convenciones

Documentación, comentarios y mensajes de commit en español; nombres de archivos, funciones y variables
en inglés. Python 3.11+. Salidas intermedias en `work/` (ignorado); entregables en `results/` (ignorado
salvo figuras agregadas y no identificables).
