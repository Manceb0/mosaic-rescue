# Pasada visual-científica: qué se ve en cada notebook

> **Segunda pasada, `PUBLICATION-GRADE`.** El código de cada figura principal salió de los
> generadores de notebook y vive ahora en `src/figures/`, un módulo por figura. El notebook y
> la figura de publicación **son literalmente el mismo código**: ya no pueden divergir.
>
> - Renderizar todo a tamaño completo, sin ejecutar un notebook:
>   `python src/figures/render_all.py` → `figures/pub/*.svg` (vectorial, el texto sigue siendo
>   texto) + `*.png` a 300 dpi + un render **aparte** y pequeño en `figures/pub/thumb/`.
> - Índice: `python src/nb/contact_sheet.py`.
> - Auditoría figura a figura, con la columna obligatoria *possible misleading
>   interpretation*: [`PUBLICATION_FIGURE_QA.md`](../PUBLICATION_FIGURE_QA.md).
>
> **El contact sheet no define el tamaño ni la composición de nada.** Es un índice. La versión
> completa manda, y la miniatura es un render propio, nunca un reescalado brutal del PNG de
> 300 dpi, ese reescalado era justo lo que estaba deformando el diseño de las figuras densas.
>
> **Idioma:** las figuras finales hablan inglés; los notebooks explican en español. Ninguna
> figura mezcla los dos.

> **Pregunta que ordenó esta pasada:** *¿estoy viendo ciencia, o estoy viendo una explicación
> dibujada?* Varias figuras eran infografías hechas con Matplotlib: cajas, flechas y estados.
> Útiles para explicar, pero **nunca** la figura principal de un análisis.

## Clases de figura

Toda figura declara su clase **en el pie y estampada en la propia imagen**, para que la
etiqueta viaje con ella si alguien la recorta y la pega en una diapositiva.

| Clase | Qué es | ¿Puede ser la figura principal? |
|---|---|---|
| `DATA` | objeto o distribución calculada desde datos del caso | **Sí** |
| `MODEL_OUTPUT` | salida de un modelo (AlphaFold, AlphaGenome, Exomiser) | **Sí** |
| `SIMULATION` | distribución generada por simulación, sin datos del paciente | **Sí** |
| `CURATED_EVIDENCE` | tabla de evidencia versionada, con fuente por celda | **Sí** |
| `SYNTHESIS` | integra resultados ya obtenidos; no expone el dato crudo | No |
| `NARRATIVE` | explica una conclusión; no contiene dato | No |

`CURATED_EVIDENCE` se añadió en la segunda pasada. Llamar `DATA` a la matriz de Track 2
invitaba a leer sus 80 celdas como observaciones experimentales del paciente, que es
exactamente lo que no son.

## Definición de HECHO: cambiada

**Antes:** «al menos 3 figuras embebidas». Ese requisito produjo relleno.

**Ahora:** cada notebook mayor necesita **al menos una figura científica**
(`DATA` / `MODEL_OUTPUT` / `SIMULATION` / `CURATED_EVIDENCE`). Las demás pueden ser
`SYNTHESIS` o `NARRATIVE`, y son legítimas, lo que ya no pueden es contar para el mínimo. `src/nb/nbutil.py::verify()`
lo comprueba leyendo la clase declarada en el pie de cada figura embebida.

---

## El objeto científico principal de cada notebook

Cada uno vive en su propio módulo, se renderiza a tamaño completo sin ejecutar el notebook, y
el notebook llama a **esa misma función**.

| notebook | objeto científico principal | módulo | librería | clase | salida |
|---|---|---|---|---|---|
| **00_DATA_REALITY** | QC de FASTQ por ciclo: ocupación de los cuatro bins de calidad, GC por lectura, calidad media por lectura, composición de bases | `src/figures/fig00_qc.py` | matplotlib | `DATA` | `fig00_fastq_qc` |
| **01_TRACK1_GENOME_WIDE** | Priorización genome-wide: los 151 genes puntuados **y** el universo de 6 321 del que salieron, con la puntuación `A0` congelada | `src/figures/fig01_manhattan.py` | matplotlib | `DATA` | `fig01_prioritization_genomewide` |
| **02_BUB1B_ALLELE_CURATION** | Navegador del gen: 23 exones sobre la proteína, dominios de InterPro/Pfam, las 1 497 missense de ClinVar una a una, y su densidad | `src/figures/fig02_browser.py` | `dna_features_viewer` + matplotlib | `DATA` | `fig02_gene_browser` |
| **03_BUBR1_MECHANISM** | Geometría del bolsillo (9 vecinos, 3 puentes de H **candidatos**, pLDDT) **y** logo de conservación con su cobertura, en una sola figura | `src/figures/fig03_pocket.py` | matplotlib 3D + `logomaker` | `MODEL_OUTPUT` | `fig03_pocket_and_conservation` |
| **04_HIDDEN_SECOND_ALLELE** | Navegador REF / ALT / Δ vertical, eje genómico compartido, modelo del gen encima; nueve pistas en **dos** figuras por modalidad | `src/figures/fig04_tracks.py` | matplotlib | `MODEL_OUTPUT` | `fig04_alphagenome_rna_splicing` + `fig04S_…_accessibility_tf` |
| **05_RESIDUAL_PHENOTYPE** | Matriz término HPO × modelo de enfermedad en bits de Resnik, con nombres de enfermedad reales y el soporte de literatura como **anillo**, nunca como número | `src/figures/fig05_hpo.py` | matplotlib | `DATA` | `fig05_hpo_disease_matrix` |
| **06_MOSAIC_AND_MITOREAD** | Distribuciones de BAF con escala idéntica en los tres escenarios + curva de potencia, con el comparador nombrado por lo que es | `src/figures/fig06_baf.py` | matplotlib | `SIMULATION` | `fig06_baf_cancellation` |
| **07_TRACK2_SAFE_RESCUE** | Matriz de evidencia curada: 8 puentes × 10 dimensiones, 80 celdas, cada una con fuente y sin ninguna puntuación global | `src/figures/fig07_evidence.py` | matplotlib | `CURATED_EVIDENCE` | `fig07_track2_evidence_matrix` |

Renderizado completo: `python src/figures/render_all.py`.
Índice: `python src/nb/contact_sheet.py` → `work/nbrender/CONTACT_SHEET.png`.
Auditoría: [`PUBLICATION_FIGURE_QA.md`](../PUBLICATION_FIGURE_QA.md).

---

## Qué se retiró, y por qué

Se retiró una figura solo si (a) otra del mismo notebook enseña **lo mismo con más dato y mejor
procedencia**, o (b) **no contiene dato** y su contenido ya está escrito en la celda de decisión.

| retirada | notebook | motivo |
|---|---|---|
| Inventario de modalidades en barras | 00 | (b) ya se imprime como tabla comprobada en disco |
| `fig2_landscape.svg` | 02 | (a) el navegador enseña los **mismos** 1 497 registros con el transcrito y los dominios encima |
| QC de pLDDT | 03 | (a) el panel C del bolsillo **es** esa pista, calculada en el mismo recorrido del PDB |
| `fig4_structural.svg` | 03 | (a) el bolsillo calcula en vivo lo mismo desde las coordenadas |
| «los dos caminos que quedan» | 03 | (b) dos barras que repiten la tabla de decisión |
| `fig5_alphagenome.svg` | 04 | (a) el navegador dibuja las nueve pistas; el resumen agregaba justo lo que hay que mirar |
| «el fenotipo tira en dos direcciones» | 05 | (b) cajas y flechas |
| `fig9_mosaic_sim.svg` | 06 | (a) el panel D es la misma curva, y además trae las distribuciones que el resumen escondía |
| «la tensión del puente 7» | 07 | (a) esa clasificación está ahora en la matriz, celda a celda y con fuente |
| «los cuatro desenlaces de Try to Kill It» | 07 | (b) cuatro cajas de texto |

**De 36 figuras a 27; de ellas 22 científicas y 5 de síntesis.** Las retiradas siguen en
`figures/` y en el historial: lo que se retira es su sitio en el recorrido del notebook.

La cuenta subió de 26 a 27 porque las nueve pistas de AlphaGenome pasaron a **dos** figuras.
Meterlas en una sola las hacía ilegibles, y la legibilidad manda sobre el recuento.

---

## Reglas visuales que quedan en vigor

1. **Nunca fabricar un dato.** Ni blots, ni microscopía, ni cariotipos, ni cobertura, ni Hi-C,
   ni intervalos de confianza que nadie ha calculado. Consecuencia concreta: la figura de
   MitoRead **perdió sus barras de error**, la incertidumbre está declarada *no cuantificada*,
   así que dibujar un intervalo era inventarse el número que falta. En su lugar van flechas
   **sin extremo**: el sesgo no está acotado, y eso es lo único cierto.
2. **El dato primero.** Si una figura puede enseñar la distribución, no enseña el resumen.
3. **Cero coordenadas del paciente.** El eje del Manhattan son bins de 1 Mb; el bolsillo va en
   coordenadas **relativas**; el navegador de AlphaGenome, en desplazamiento respecto a la
   variante. Ningún número absoluto aparece en un fichero versionado.
4. **Toda figura reproducible**, y su conjunto de datos compacto guardado al lado.
5. **No se tocó ninguna conclusión científica** en esta pasada. Donde una figura mejor exigía
   un dato que no existe, se marcó como no ejecutable en vez de dibujarlo.

### Lo que esta pasada destapó: dos cosas, ninguna cosmética

- **Calidades binadas.** El QC real enseña que este secuenciador entrega **4 valores de calidad**
  (Q2, Q11, Q25, Q37), no un continuo. Dos versiones de la figura fallaron por ignorarlo:
  con percentiles las bandas se colapsan en una caja gris que parece un artefacto, y con mapa
  de densidad el bin alto se lleva el 93 % y el panel sale plano. La versión que informa es la
  masa que **abandona** el bin alto: de 4,52 % en el ciclo 1 a 13,29 % en el 149.
- **El escáner de saneado se disparó dos veces contra mí.** `py3Dmol` incrusta en el `.ipynb`
  el PDB completo y los números de residuo **absolutos**; y `01` imprimía el informe del escáner
  íntegro, que **cita** el texto que encuentra, un canal de fuga creado por el propio control.
  Los dos corregidos: la vista interactiva se escribe en `work/`, y el notebook imprime solo el
  veredicto.

### Un pie de figura que estaba mal, corregido

La matriz de fenotipo residual destapó que MVA1 cubre **3 de los 7** rasgos del probando, no 6
como decía un pie que escribí antes de mirar el dato. Ahora el pie se **calcula** de la matriz.
No cambia ninguna conclusión: la nefrocalcinosis sigue siendo el único rasgo que falla las dos
comprobaciones (la de anotación **y** la de literatura MVA1) y eso lo decide la figura
siguiente, no esta.

---

## Lo que destapó la segunda pasada

- **El escáner de saneado no miraba los ficheros nuevos.** Listaba solo `git ls-files`, es
  decir lo ya versionado. Una figura recién generada quedaba fuera del escaneo y el informe
  salía LIMPIO sin haberla leído. Ahora también lista
  `git ls-files --others --exclude-standard`, que es lo que un commit añadiría de verdad: 156
  ficheros revisados antes, **181** después.
- **El TSV de Track 2 tenía las columnas desalineadas** en las siete filas que llevan nota pero
  no fuente: la nota caía en la columna `fuente` y acababa impresa en la figura como si fuera
  una referencia bibliográfica. Corregido; ahora la figura cita **7 fuentes** reales.
- **Panel A de QC, tercer intento.** Con percentiles salía una caja gris que parecía un
  artefacto. Con mapa de densidad salía plano, porque un bin se lleva el 93 %. Lo que
  informa es la masa que **abandona** el bin alto, que sube del 4,52 % al 13,29 % a lo
  largo de la lectura.
- **`set_xticks([])` en un eje compartido** borraba los ticks de las nueve pistas del navegador
  de AlphaGenome, no solo los del modelo del gen.
