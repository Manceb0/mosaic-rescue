# Película de apertura / fondo de presentación

| Versión | Archivo | Uso |
|---|---|---|
| v1 | `v1/index.html` · `~/Downloads/MOSAIC_RESCUE_opening_v1.mp4` | Cold open de 38 s que termina en *THE PATIENT IS THE SCREEN.* |
| v2 | `v2/index.html` · `~/Downloads/MOSAIC_RESCUE_presentation_v2.mp4` | Primer sistema con capítulos (3:04). Sustituida por la v3 |
| v3 | `v3/index.html` · `~/Downloads/MOSAIC_RESCUE_presentation_v3.mp4` | Cadena de investigación de la v1 + capítulos del speech (2:14) |
| v4 | `v4/index.html` · `~/Downloads/MOSAIC_RESCUE_presentation_v4.mp4` | v3 + prólogo en el mundo real (dibujo, tubo, sangre), mosaico que forma al niño, estilos que cambian (papel ↔ plano navy ↔ mapa) y cierre en bucle (2:23) |
| v5 | `v5/index.html` · `~/Downloads/MOSAIC_RESCUE_presentation_v5.mp4` | (2:59) Fondo grafito sin "papel" en la ciencia · auditoría científica contra el repo · AlphaGenome como lente sobre el candidato real de EXP-023 · interludio *The patient as a screen?* con nuestra propia auditoría y 3 papers verificados en PubMed · trampa de seguridad · cierre limpio |
| **v6** | `v6/index.html` · `~/Downloads/MOSAIC_RESCUE_presentation_v6.mp4` | **Actual (3:00).** Prólogo artesanal (el crayón dibuja trazo a trazo, cinta, luz y polvo, «ojo científico» sobre el tubo) · sangre en 3 planos con plaquetas y linfocito · **transición continua**: la cromatina del núcleo se condensa en los 46 cromosomas de la primera célula · cromosoma rezagado anotado · anillo ISM fiel a EXP-023 (768 celdas, línea del 5 %, candidato 62/256, máximo a +125 pb) · interludio sin cuadros negros · la frase final se convierte en la cadena del capítulo 4 |

Todo se dibuja por código (canvas) con semillas fijas; los datos visuales son **sintéticos**.
Ningún valor, coordenada o genotipo del paciente aparece en pantalla.

## Presentar la v6 en vivo (recomendado)

Abrir `v6/index.html` en Chrome/Edge → **F** (pantalla completa) → **Espacio**.
Se **detiene sola** en cada pausa y sigue viva; el clicker (**→ / PageDown**) la libera.
Un clic durante una animación no la corta: solo indica "no te detengas en la próxima pausa".
**Shift+→** salta, **←** vuelve a la pausa anterior, **H** desactiva pausas, **M** silencia, **D** línea de tiempo.

## Guion por pausa (según `docs/JUDGE_PATH.md`)

| Pausa (MP4 v6) | En pantalla | Qué dice el presentador |
|---|---|---|
| 0:58 | Título · *THE PATIENT IS THE SCREEN.* | «Everyone sees mosaicism as the problem. We asked whether it also contains the experiment.» |
| 1:08 | 4 carriles → 1 muestra → 1 genoma | Una muestra de sangre, cuatro carriles técnicos; sin RNA, proteína ni padres. |
| 1:23 | 6 321 → 151 → A0 #4 → auditoría → #1 · dos alelos · ¿en trans o en cis? | BUB1B #4 congelado y #1 tras reparar frecuencias; truncante + missense; fase sin resolver. |
| 1:33 | CNV / MEI: sin llamada · inserción compleja no excluida | «Cerramos ese análisis, no el caso.» |
| 1:45 | ISM (62/256, bajo la línea del 5 %) → contactos predichos (1,09 % vs 5 %) | Predicción de modelo, no medida; dos negativos preregistrados, y se reportan. |
| 2:01 | Interludio · sin T0 | «Sin punto de partida, "perdido" y "nunca hecho" son indistinguibles.» |
| 2:19 | Interludio · el clon que gana | «Un clon que gana es señal de riesgo tumoral, no de rescate.» |
| 2:29 | Cadena de mecanismo | Qué es del caso, qué es externo y qué falta medir. |
| 2:39 | Azithromycin · Arimoclomol · Sirolimus | Tres roles, no un ranking. Más supervivencia de células inestables = veto. |
| 2:49 | Fase primero · trans / cis | El siguiente experimento más barato y decisivo. |
| 2:54 | Cierre fijo | Conclusión. |

## Rigor

**Fuentes de cada afirmación en pantalla (v6):**
- Prólogo: los glóbulos rojos maduros no tienen núcleo; el ADN de un WGS de sangre procede de los leucocitos (biología básica). El linfocito, la sangre y el dibujo son ilustración genérica, no del paciente.
- Anillo ISM (EXP-023, `docs/DECISIONS.md`): ventana de 256 pb, 768 sustituciones sintéticas, lectura primaria *splice sites*, candidato en la posición 62 de 256 por |efecto|, máximo de la ventana a +125 pb, regla «concentrada» = 5 % superior. **El perfil dibujado es ilustrativo**; rango, ventana y máximo son reales, y así lo dice el panel.
- Contactos: max |ALT − REF| = 1,09 % del máximo de REF (umbral 5 %), fibroblasto de piel `CL:0002620`.
- 6 321 → 151 genes, A0 #4 / A0-FREQFIX #1, Exomiser #2/398: `README.md` §2.
- Alelos (truncante LP, missense VUS, fase sin resolver): `README.md`, `story02`.
- CNVpytor / xTea·SCRAMble / ensayo de lecturas descriptivo / inserción compleja no excluida: `reports/TRACK1_REPORT.md` §7.
- AlphaGenome = candidato intrónico de segundo alelo (EXP-009 → EXP-023, **no** el missense); rango 62/256; ALT−REF 1,09 % vs umbral 5 %: `research/EXPERIMENT_REGISTRY.md`, `docs/DECISIONS.md`.
- Interludio: `research/agent_findings/2026-08-28_patient-as-screen_agent-a.md`, `docs/00_ESTADO_Y_OBSOLESCENCIA.md`; Klaasen 2022 (10.1038/s41586-022-04938-0), Ya 2025 (10.1016/j.stemcr.2025.102506), Villarroya-Beltri 2022 (10.1126/sciadv.abq5914), verificados en PubMed.
- Azithromycin / Arimoclomol / Sirolimus y sus roles: `reports/TRACK2_REPORT.md` (tabla del portafolio). Son del proyecto, no inventados; se muestran como PROPOSED EXPERIMENT, no probados.

- Etiquetas de procedencia arriba a la izquierda: **PATIENT DATA**, **MODEL PREDICTION**,
  **EXTERNAL EVIDENCE**, **HYPOTHESIS**, **PROPOSED EXPERIMENT**.
- El mosaico es una **simulación conceptual**: un WGS de sangre agregado no observa células.
- `docs/JUDGE_PATH.md` pide no usar *The Patient Is the Screen* como **hallazgo**: aparece solo como lema del título.
- Los fármacos se muestran con su **rol experimental**, no como ranking; `CONFIG.SHOW_DRUG_NAMES = false` los oculta.

## Exportar

```bash
python render_mp4.py v6/index.html salida.mp4 60
```

Requiere `pip install playwright imageio-ffmpeg` y Microsoft Edge instalado.
