# EXP-027 · Phase 1 · Resultado sellado

> **METHOD VALIDATION FAIL ≠ PATIENT NEGATIVE.** El paciente no se analizó: Phase 1 no autorizó
> aplicar A1.

## Estado canónico

| Componente | Estado final |
|---|---|
| **EXP-027 Phase 1** | **EXECUTED · METHOD VALIDATION FAIL** |
| **A1 en el paciente** | **NOT EXECUTED · BLOCKED BY PHASE 1 FAIL** |
| **A2** | **UNSCORABLE / UNRESOLVED** |
| **A3** | **RESERVED · NOT EXECUTED** |

**En una frase (para el jurado).** *Before interrogating the patient, we froze a validation benchmark.
The method achieved 94.3 % sensitivity at the preregistered δ = 0.10 and only 0.41 % switch error, but
25.0 % of intact benchmark windows were called positive against a 5 % nominal calibration. Under our own
preregistered rule, the method failed. Mosaic Rescue therefore blocked the patient-level A1 inference
instead of producing an attractive but unvalidated claim. At BUB1B itself, retention was also 87.9 %,
below our frozen 90 % requirement.*

## Puertas preregistradas

Benchmark público: 20 tríos de 1000 Genomes high-coverage (lista en `docs/DECISIONS.md`), 50 ventanas de
evaluación por hijo (BUB1B es la #1), 20 tiles de calibración por hijo, B = 10 000,
δ ∈ {0, 0,02, 0,05, 0,10, 0,15, 0,20}. Ponderación de Amendment 6 (por hijo y luego hijos con peso igual).

| Puerta | Umbral congelado | Resultado | |
|---|---|---|---|
| Centinela de calibración APR (Amendment 7) | FAIL si binomial unilateral vs 0,05 da p < 0,05 | **249 / 995 = 25,03 %**; P(X ≥ 249) ≈ 10⁻⁹⁸·⁹ | **FAIL** |
| Sensibilidad a δ = 0,10, fase inferida | ≥ 0,80 | 0,9426 | PASS |
| Retención frente a fase mendeliana | ≥ 0,90 | 0,9426 (mendeliana 1,0000) | PASS |
| SER de comunes (analítico, MAF ≥ 1 %) | ≤ 2 % | 0,4085 % (scaffold, descriptivo: 0,4525 %) | PASS |
| Veto por superpoblación | SER > 4 % o sensibilidad < 0,80 | SER 0,32–0,58 %; sensibilidad 0,916–0,967 | PASS |
| BUB1B · hijos / estratos evaluables | ≥ 15 / 20 y ≥ 4 / 5 | 19 / 20 · 5 / 5 | PASS |
| BUB1B · sensibilidad | ≥ 0,80 | 0,8795 | PASS |
| **BUB1B · retención** | ≥ 0,90 | **0,8795** | **FAIL** |
| BUB1B · centinela técnico | veto con ≥ 4 positivos (n_e = 19) | 2 | PASS |

`fail_reasons`: `global:apr_calibration`, `bub1b:retention`. **0,8795 no se redondea a 0,90.** Aunque
BUB1B hubiera pasado, el FAIL global de APR ya bloqueaba A1.

**Sobre el p-valor.** El JSON guarda `apr_p_binom_one_sided = 0.0` porque la cola está por debajo de la
precisión de coma flotante; el valor calculado en escala logarítmica es ≈ 10⁻⁹⁸·⁹. No es «p = 0». Además
el binomial presupone independencia aproximada entre pares. Lo que importa es la magnitud: **25,0 %
observado frente a 5 % nominal**, unas cinco veces.

**Qué es y qué no es el APR.** Es un centinela operativo de calibración sobre datos de ADN derivado de
líneas linfoblastoides (LCL), no una tasa biológica de falsos positivos: la propagación de LCL puede
introducir artefactos somáticos (Byrska-Bishop et al. 2022, PMID 36055201,
[10.1016/j.cell.2022.08.004](https://doi.org/10.1016/j.cell.2022.08.004)). Lo correcto es: *failed operational
calibration on the public benchmark*.

## Denominadores

- **1 000 pares hijo × ventana de evaluación → 995 evaluables.** No faltan trabajos: los 5 restantes quedaron
  por debajo de Hmin = 50 tras los filtros preregistrados (marcadores analíticos finales):

  | Hijo | Ventana | Candidatos analíticos | Fuera de la fase (multialélicos) | Marcadores finales |
  |---|---|---:|---:|---:|
  | HG03248 | chr21 (1 de 2) | 115 (88 en segdup) | 20 | 2 |
  | HG03248 | chr21 (2 de 2) | 11 | 8 | 1 |
  | HG01261 | BUB1B | 13 | 12 | 0 |
  | HG03707 | chr7 (1 de 2) | 0 | 0 | 0 |
  | HG03707 | chr7 (2 de 2) | 6 | 2 | 2 |

  HG01261 no fue evaluable en BUB1B **por insuficiencia de marcadores informativos tras los filtros**; no se
  atribuye una causa biológica sin un análisis propio que la demuestre.
- **400 trabajos de calibración** (20 hijos × 20 tiles) sirven para estimar `ρ` (60 hijo×bin propios,
  20 con fallback global por bin). **No forman parte del APR**.
- Run r2: 1 400 / 1 400 trabajos, 0 fallos, 123 850 s (34,4 h).

## Cadena de custodia

| Fecha | Hecho | Ancla |
|---|---|---|
| 2026-10-01 | Contrato + Amendments 1–7 congelados | tag `exp027-prebenchmark-freeze` → `4ca13e4` |
| 2026-10-04 | GO-A: la exclusión por solape ≥ 1 pb dejaba 0 ventanas → Amendment 8 (máscaras de sitio) y regla A de SV | tag `exp027-prephase1-freeze-a8` → `641c857`; regla A `6144573` |
| 2026-10-04/05 | GO-B: 133,0 GB, 110 / 110 piezas válidas; 70 BCF + 20 CRAM derivados 90 / 90 | `1013dd9`, `bba7e1e` |
| 2026-10-05 | Ejecución r1 | tag `exp027-phase1-execution-freeze` → `bba7e1e` |
| 2026-10-05 | r1 **ABORTED_TECHNICAL**: `SHAPEIT5_phase_rare` abortaba con genotipos ausentes en raras (97 fallos confirmados), sin resultado global | EXEC-DEF-PH1-001 en `docs/DECISIONS.md` |
| 2026-10-05 | A′: Phase 1 sin `phase_rare` (etapa no puntuable); validación PASS (5 ventanas antes fallidas completan; 4 antes completadas idénticas en `WindowSites`, SER y auditoría; GT del scaffold idénticos por `CHROM:POS:REF:ALT`) | tag `exp027-phase1-execution-freeze-r2` → `7e20047` |
| 2026-10-06 → 07 | Run r2 completo desde cero, sin reutilizar r1; 1 400 / 1 400 | `RUN_MANIFEST.json` r2; procedencia en `ed1b614` |
| 2026-10-07 | Informe: **FAIL**; reproducción post-hoc **idéntica** al informe | tag de resultado `exp027-phase1-result-r2-fail` |

El cambio entre r1 y r2 fue **técnico, anterior a cualquier resultado científico y sin reciclar
resultados**: r1 no llegó a evaluar nada.

## Afirmaciones prohibidas

- No diagnosticamos mCA ni mosaicismo en el paciente; no estimamos una fracción mosaica.
- No demostramos selección, rescate ni reversión somática.
- No establecimos que los dos alelos de BUB1B estén en *trans*.
- A2 sigue `UNSCORABLE / UNRESOLVED`; A1 no se ejecutó.
- No afirmamos una causa del exceso de APR (ver diagnóstico post-hoc: solo asociaciones).
- El 25 % no es una tasa biológica de falsos positivos.

## Reproducibilidad

`src/exp027/posthoc_phase1.py` reconstruye la evaluación completa desde los 1 400 `result.json` congelados
(mismas semillas, B = 10 000): **idéntica al informe sellado** en todas las métricas adjudicadas
(`identical_to_sealed_report: true`) y el mapa APR da 249 / 995.

Con δ = 0 dentro del modelo de spike-in (beta-binomial con `ρ` estimado en calibración), la tasa de
positivos es **4,7 %** con fase inferida y **5,6 %** con fase mendeliana: el null sintético está calibrado;
los datos reales intactos (25,0 %) tienen estructura que ese modelo no recoge.

| δ | 0,00 | 0,02 | 0,05 | 0,10 | 0,15 | 0,20 |
|---|---:|---:|---:|---:|---:|---:|
| Sensibilidad, fase inferida | 0,047 | 0,762 | 0,902 | 0,943 | 0,952 | 0,960 |
| Sensibilidad, fase mendeliana | 0,056 | 0,975 | 1,000 | 1,000 | 1,000 | 1,000 |

## POST-HOC DIAGNOSTIC — NOT USED FOR ADJUDICATION

Mapa de los 995 pares evaluables (`work/exp027/posthoc/apr_map.csv`); nivel de evidencia **L1**
(asociación). No cambia el FAIL y no puede rescatar A1.

- **Inflación global:** en el QQ-plot de los 995 p-valores intactos, λ ≈ 2,66 (mediana de χ² / 0,4549;
  un test calibrado daría ~1,0). Es descriptivo, no una puerta.
- **Repartido, no concentrado:** 7–17 positivos de 50 en cada hijo; 19–31 % por superpoblación
  (AFR 54/198, AMR 61/199, EAS 38/200, EUR 50/200, SAS 46/198).
- **Efectos pequeños:** mediana de |δ̂| en los positivos 0,0088, frente a 0,0025 en los no positivos y muy por
  debajo de δ* = 0,10.
- **Asociación con la composición REF/ALT del haplotipo:** cuando H1 lleva el alelo de referencia en
  ~la mitad de los hets de la ventana, APR 9 % (31/332); cuando está sesgado a REF o a ALT, 31–35 %. Por
  terciles de la fracción de lecturas REF de la ventana (media 0,517): 16 % → 25 % → 34 %.
- Por profundidad media: 30 % → 27 % → 19 % (de menor a mayor). Por fracción enmascarada y por número de
  hets: sin gradiente claro (23–27 %).

**Hipótesis (L0), no resultado:** un sesgo hacia la referencia en el recuento de lecturas, sumado de forma
coherente por la fase cuando un haplotipo concentra más alelos REF, inflaría `T` bajo el null de signos.
Contrastarla exige un experimento nuevo con su propio preregistro (por ejemplo, un null que conserve la
orientación REF/ALT); nunca podrá reabrir A1 en este proyecto. Loh et al. 2018 muestran que las técnicas
basadas en fase detectan mCA (PMID 29995854), pero eso no valida nuestro `T` con null de signos; SHAPEIT5
valida la fase, no esta calibración (PMID 37386248).

## Artefactos sellados

`work/` no se versiona (contiene coordenadas y datos derivados); estos SHA256 los anclan.

| Artefacto | SHA256 |
|---|---|
| `work/exp027/phase1_r2/RUN_MANIFEST.json` | `29f70878257130af25ce98a506b42f095f14e6344af7515658a42671d3bb9557` |
| `work/exp027/phase1_r2/phase1_report.json` | `37e676ad5137dc4ceee283de7251b403323c3d9dda589907e8eff43a441e1e3e` |
| `work/exp027/phase1_r2/progress.log` (1 403 líneas) | `5730fb7e4503c2f0b6303e723faef6f0163358b189bde3bf31378fd9d1028e38` |
| `work/exp027/phase1_r2/status.json` (DONE) | `38c5759d3e1debed99ebd05a363740c65920402dfe6540f57d151d14f967321b` |
| `work/exp027/posthoc/phase1_posthoc.json` | `923cfb32854c76867bc7fd06a28bef83c624f0e49bb17d6a987d3de4146ae136` |
| `work/exp027/posthoc/apr_map.csv` | `316f0cf7be522f0ca62e1b4e55bcb1c01f1efe65e3591b27babdc23c7897da3d` |
| `figures/pub/fig13_exp027_phase1_result.svg` | `d7fd1bf3f830082f4c0d02807775716804161440fa37b410cbd61bddab2edf31` |
| `figures/pub/fig13_exp027_phase1_result.png` | `4453385899bdd3ecdc0f829fe133ec92217f2c4079b89d705ff8f4c555080aad` |
| `work/exp027/phase1/RUN_MANIFEST.json` (r1, ABORTED_TECHNICAL) | `b0c211c5b4f1fa0b9dad26eeeca9c2183dabbbbe4f1f96c50de4d3d4083ceaae` |
| `work/exp027/phase1/ABORTED_FAILED_WINDOWS.json` (r1) | `f27f44d15f7aaa5c5eabb2168d2a0262eab6e3c3dc4c216e5223c6a1032bf207` |
| `work/exp027/validation_r2/VALIDATION.json` (A′) | `2046f8dabd75f7f73882e1fe155d635c343122c53f17c66c8a6b38585577df52` |

Los dos SHA de `fig13` de la tabla son los de la versión **sellada** en el tag `exp027-phase1-result-r2-fail`.
**Re-render posterior (2026-10-07), solo de redacción, tras revisión del líder:** «healthy data» pasa a ser «intact,
unspiked benchmark data»; «fires without signal», «fires without injected signal»; «the null is broken», «the null is
miscalibrated on the benchmark»; la banda del QQ pasa a «iid Uniform reference envelope (95 %, descriptive)», porque los
995 pares comparten hijos, ventanas y pipeline y no son iid. El titular deja el carácter de flecha y dice «High
sensitivity, failed calibration: the patient test was not performed». Mismas fuentes, mismos SHA de entrada, mismos
números.
SHA del re-render: SVG `5c138b0226769ae99d5d3e449f33c44b155799f9ccbddd4fd346b8f88965e8bd` · PNG
`3f0a21ee0044a612f775c0358d365e75937720d087409b3c02538fc7b775e716`. El resultado sellado no se toca.

Figura: [`figures/pub/fig13_exp027_phase1_result.svg`](../figures/pub/fig13_exp027_phase1_result.svg),
ficha en `PUBLICATION_FIGURE_QA.md`.
