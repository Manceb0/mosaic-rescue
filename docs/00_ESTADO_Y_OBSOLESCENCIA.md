# Estado del repositorio y mapa de obsolescencia

> Escrito al integrar el Master Brief. Nada se ha borrado: este documento dice qué
> sigue vigente y qué quedó superado, para que la decisión de retirar archivos sea
> explícita y no un descuido.

## Qué cambió

El inventario real del dataset (`docs/01_MASTER_BRIEF.md` §1) resolvió la pregunta que
bloqueaba el proyecto entero. **Lo que existe:** VCF de WGS + FASTQ (~86 GB, NovaSeq S4,
4 carriles) y un documento de fenotipo HPO.

**Lo que no existe, y no se puede inventar:** RNA-seq, single-cell, proteómica, muestras
longitudinales o multi-tejido, cariotipo celular directo, genotipos parentales, tejido
tumoral del rabdomiosarcoma.

Eso invalida toda rama que presuponga resolución de célula única o series temporales.

## Convergencia que respalda la decisión

Cuatro análisis independientes llegaron a la misma conclusión sin verse entre sí:

| Ruta | Conclusión |
|---|---|
| Auditoría Patient-as-Screen | Screen sin control T0; "depletado" ≡ "nunca generado" |
| Auditoría Ghost Karyotypes | Requiere 2.500–3.000 células cariotipadas; no las hay |
| Auditoría Synthetic Rescue | No ejecutable sin modalidad de expresión resuelta por célula |
| Master Brief §5 | *"Módulos eliminados por falta de datos que los sostengan: aneuploid fitness landscapes, Rescue Replay, forecasting evolutivo"* |

Los tres primeros están en `research/agent_findings/`. El cuarto se escribió por
separado. Que coincidan es la razón para actuar sobre ellos.

---

## Vigente

| Archivo | Estado |
|---|---|
| `CLAUDE.md` | **Autoridad operativa.** Reglas duras, convenciones, prohibiciones |
| `docs/01_MASTER_BRIEF.md` | **Autoridad científica.** Datos, fenotipo, genética, cancelación de BAF, MitoRead, Bartter |
| `docs/02_ANALYSIS_PLAN.md` | **Autoridad de ejecución.** Fases 0-8 con decisiones preregistradas |
| `docs/00_KICKOFF.md` | Prompt de arranque |
| `docs/04_ARQUITECTURA_MAESTRA.md` | **Jerarquía vigente.** Manda sobre cualquier módulo previo |
| `docs/03_ALPHAGENOME_ASSESSMENT.md` | Evaluación de las seis propuestas con AlphaGenome |
| `docs/claims_we_cannot_make.md` | Vigente. Compatible con CLAUDE.md Regla 3 |
| `docs/research_protocol.md` | Vigente en lo metodológico (§§1-5, 12-16) |
| `docs/rescue_evidence_rubric.md` | Vigente. Los vetos 5-7 siguen aplicando |
| `docs/external_datasets.md` | Vigente como referencia de qué recurso sirve para qué |
| `research/priors/` | Vigente, pero varios priors ya no se consumen (ver abajo) |
| `research/agent_findings/` | Vigente como registro histórico de por qué se descartaron ramas |

## Superado por el Master Brief

| Archivo | Motivo |
|---|---|
| `docs/architecture.md` | Las 16 etapas incluyen Patient-as-Screen, Ghost Karyotypes, Fitness Landscape, Mosaic Forecast y Rescue Replay. El brief §5 los elimina por falta de datos |
| `docs/roadmap.md` | Las Fases 0-10 quedan reemplazadas por las Fases 0-8 del plan de análisis, que sí están ancladas al dataset real |
| `docs/agent_workplan.md` | Los streams A-K presuponen modalidades inexistentes |
| `docs/agent_prompts.md` | Mismo motivo. Los prompts C, D, G, H se refieren a análisis no ejecutables |
| `docs/diagrams.md` | Los 9 diagramas dibujan la arquitectura retirada |
| `docs/visualization_plan.md` | Las Figuras 4-8 y 11 requieren datos de célula única |
| `docs/status_board.md` | Los Issues #1-#10 se estructuraron sobre la arquitectura anterior |
| `notebooks/README.md` | La secuencia de 16 notebooks incluye 03-09 no ejecutables |
| `notebooks/00_data_inventory.ipynb` | Su función ya la cumplió el brief §1. Conservable como registro |
| `README.md` | Describe la arquitectura retirada. **Pendiente de reescritura** |
| `research/crazy_ideas.md` | CI-01, CI-02, CI-04, CI-06 y CI-09 dependen de datos inexistentes |

### Issues de GitHub afectados

`#2`, `#3`, `#7` y `#10` se abrieron sobre hipótesis que el inventario invalida. `#10`
conserva valor parcial: el eje mPOS / proteostasis sigue vivo, pero como mecanismo aguas
abajo dentro de MitoRead (brief §7), no como núcleo con predicción de saturación —
esa predicción necesitaba expresión resuelta por célula.

`#1` (inventario) está **resuelto** por el brief §1. `#4`, `#5`, `#6`, `#8` y `#9`
siguen teniendo contenido aprovechable.

### Priors que ya no se consumen

De `research/priors/`, la tabla por cromosoma de Klaasen, las curvas de potencia de
detección y el suelo de falsos positivos de CNV por expresión servían a análisis de
espacio negativo y de célula única que ya no se ejecutan. Se conservan documentados
porque el razonamiento sobre por qué la señal de depleción no era identificable sigue
siendo defendible ante un jurado.

---

## Qué reemplaza a lo retirado

El entregable honesto de la rama de mosaicismo es una **huella genómica agregada**
(brief §6.5), no una reconstrucción celular:

`detección estándar de mCA (MoChA) + BAF/LRR + índice de dispersión`

Con la predicción preregistrable de §6.4: dispersión de LRR elevada con dispersión de
BAF relativamente preservada — la asimetría que las mCA clonales no producen, porque en
MVA el BAF **se cancela por construcción** (§6.1) y esa cancelación es estructural, no
de profundidad.

No prometer reconstrucción de células individuales. No prometer cariotipos fantasma.

**Nombre obligatorio:** *bulk genomic mosaic fingerprint*. Y el índice de dispersión no se
presenta como superior al método estándar hasta ganar la simulación preregistrada en
`docs/04_ARQUITECTURA_MAESTRA.md` §2.

---

## Lo que vale más que cualquier análisis pendiente

Tres preguntas al equipo clínico, todas un email (`docs/00_KICKOFF.md`):

1. **¿Polihidramnios u oligohidramnios?** Bartter y MVA van en direcciones opuestas. Una línea de la historia obstétrica decide entre §8 y la línea principal.
2. **¿La librería es PCR-free?** Si hay amplificación, sube el sesgo de cobertura y la duplicación. Lo que pierde fuerza es usar cambios pequeños de profundidad como evidencia de mosaicismo — **no el proyecto**. Track 1, SV, AlphaGenome y la rama renal sobreviven intactos. Cambia cuánto peso soporta §6, no si se ejecuta.
3. **Hemograma contemporáneo a la extracción.** Sin fórmula ni plaquetas, MitoRead arrastra un confusor fatal: las plaquetas tienen mitocondrias y carecen de núcleo, así que distorsionan directamente el cociente mtDNA/nuclear.
