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

- **Fase 0.2** — qué esperamos encontrar en la cabecera del VCF y por qué importa cada campo. Preregistrar **antes** de mirar. *Siguiente paso inmediato.*
- **Fase 1** — auditoría HPO Residual. Tabla de decisión ya preregistrada en el plan §1.3.
- **Fase 3** — predicción de la huella de mosaicismo. Ya preregistrada en el brief §6.4.
- **Fase 7** — simulación del índice de dispersión contra método estándar de mCA, a fracciones celulares de 1/2/5/10/20 %. Preregistrada en `docs/04_ARQUITECTURA_MAESTRA.md` §2: si pierde, se reporta que perdió y se usa el método estándar.
