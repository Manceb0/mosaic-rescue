# Bitácora de decisiones

Se escribe **antes** de cada fase, no después. Para cada una: qué se espera encontrar,
qué resultado mataría la hipótesis, y qué se decidió. Si el resultado contradice lo
preregistrado, no se reescribe la predicción — se documenta la sorpresa.

Ver `CLAUDE.md`, Regla Dura 6 y Flujo de trabajo.

| Fecha | Fase | Qué esperamos | Qué lo mataría | Resultado | Decisión |
|---|---|---|---|---|---|
| 2026-08-29 | Integración | — | — | Master Brief integrado al repositorio; ramas sin datos que las sostengan marcadas como superadas | Ver `docs/00_ESTADO_Y_OBSOLESCENCIA.md` |
| 2026-08-29 | Arquitectura | Que el ranking de AlphaGenome aguantara revisión | Que el umbral del ~50 % resultara ser BubR1-específico y no universal | **Lo era.** Dosis residual pasa a condicional; segundo alelo oculto sube a prioridad general | `docs/04_ARQUITECTURA_MAESTRA.md` |
| 2026-08-29 | Fase 1 — QC de L001 | Reads de 150 bp, R1/R2 balanceados, profundidad en rango 45-60x | Longitud variable (indicaria recorte previo), desbalance R1/R2, calidad baja | **149 bp**, varianza cero en 136 586 642 reads; R1==R2 exacto; 52,5x bruta / ~43x efectiva; 92,9 % ≥ Q30 | Datos aptos para Fase 1. Ver `docs/QC_L001.md` |
| 2026-08-29 | Fase 1 — PCR-free | Que el QC resolviera si la librería es PCR-free | Que el adaptador no discriminara entre kits | **No discrimina.** Tagmentación confirmada, pero `Illumina DNA Prep` y `Illumina DNA PCR-Free` comparten adaptador | Pregunta reformulada para el email: *¿cuál de los dos kits?* |
| 2026-08-29 | Panel renal | Que MAGED2 fuera el primer candidato por el eje perinatal | Que el fenotipo MAGED2 fuera transitorio y la nefrocalcinosis persistente | **Es transitorio** (PMID 27120771). Si persiste hoy, MAGED2 baja y suben SLC12A1/KCNJ1/CLCNKB/BSND | `config/panels/nephrocalcinosis.txt` |

## Pendiente de preregistro

~~- **Fase 0.2**~~ — **preregistrada 2026-08-29, antes de abrir el fichero.** Ver abajo.
- **Fase 1** — auditoría HPO Residual. Tabla de decisión ya preregistrada en el plan §1.3.
- **Fase 3** — predicción de la huella de mosaicismo. Ya preregistrada en el brief §6.4.
- **Fase 7** — simulación del índice de dispersión contra método estándar de mCA, a fracciones celulares de 1/2/5/10/20 %. Preregistrada en `docs/04_ARQUITECTURA_MAESTRA.md` §2: si pierde, se reporta que perdió y se usa el método estándar.

---

## Preregistro — Fase 0.2, auditoría de la cabecera del VCF

Escrito **antes** de abrir el fichero (301 MB en `Downloads`). Solo cabecera: ninguna
variante del paciente se mira en este paso.

| # | Qué espero | Por qué importa | Qué cambia si me equivoco |
|---|---|---|---|
| 1 | Build **GRCh38** | El brief lo asume y los paneles están en esas coordenadas | Si es GRCh37, hay que remapear los dos paneles y toda coordenada del proyecto |
| 2 | **Una sola muestra** | Sin padres, la fase no se resuelve por trío | Si hubiera más de una, cambia todo el planteamiento del §9.1 |
| 3 | **Sin anotación previa** (VCF crudo del caller) | Determina si la Fase 2.2 empieza de cero | Si trae `CSQ`/`ANN`/`dbNSFP`/gnomAD, la Fase 2.2 se acorta mucho |
| 4 | `FORMAT` con `GT`, `AD`, `DP`, `GQ`, `PL` | `AD` es imprescindible para balance alélico: sostiene heterocigosis compuesta y la rama de mosaicismo | **Sin `AD` se cae la confianza en compound-het y en §6** |
| 5 | **Sin `PS`/`PGT`/`PID`** | Son los campos de fase física | **Si están, la pregunta cis/trans deja de ser irresoluble y pasa a parcialmente resoluble.** Sería el hallazgo de mayor valor de esta fase |
| 6 | No es un gVCF | Un gVCF con `<NON_REF>` necesita parseo distinto | Cambia el pipeline de lectura entero |

**La predicción que más quiero ver fallada es la #5.** Todo el techo que le pusimos al
segundo alelo (`unphased ≠ trans`, `docs/03_ALPHAGENOME_ASSESSMENT.md` §4.2) asume que no
hay fase. Si el caller dejó bloques de fase física, parte de ese techo se levanta.

**Falsificador de la fase entera:** si la cabecera no declara build ni caller, no se puede
confiar en nada aguas abajo y hay que pedirlo al laboratorio antes de seguir.
