# Judge path — las cuatro figuras del recorrido de 3 minutos

> **Para qué es esto.** El repositorio tiene **28 figuras embebidas, 23 científicas**. Eso está
> bien para un cuaderno de investigación y es demasiado para un vídeo de 3 minutos. Este
> documento fija **cuáles cuatro** se enseñan, en qué orden, y qué se dice exactamente sobre
> cada una.
>
> No se eligen «las más bonitas». Se eligen las cuatro que sostienen el argumento completo, una
> por cada criterio de la evaluación oficial.

## El arco, en una línea

**Buscamos sin panel y contamos el resultado incómodo → encontramos un modo de fallo que nadie
había cuantificado → mapeamos la evidencia terapéutica y salió llena de huecos → y por eso la
propuesta es una cartera de falsación, no un fármaco.**

---

## 1 · `fig01_prioritization_genomewide` — el rigor

**Qué se dice.** `BUB1B` compite contra **6 321 genes**, sin panel. En el `A0` **congelado y
preregistrado** queda **#4**, no #1. Los tres que lo superaban resultaron ser polimorfismos
comunes; la sensibilidad `A0-FREQFIX` lo devuelve al #1. **Los dos números se cuentan
juntos, siempre.**

**Por qué esta y no otra.** Es la figura que un jurado usa para decidir si se fía. Enseñar el
#4 voluntariamente compra más credibilidad que cualquier #1.

**Lo que NO se puede decir.** Que el eje Y sea un p-value. **No lo es.** Es una puntuación
preregistrada, sin distribución nula y sin línea de significación. Si alguien lo llama
Manhattan, hay que corregirlo en el momento.

**Criterio oficial que cubre:** rigor científico (35 %).

## 2 · `fig06_baf_cancellation` — la innovación

**Qué se dice.** En aneuploidía **variegada**, el estadístico BAF sitio a sitio **pierde
potencia según crece el evento**, porque las contribuciones de linajes distintos se cancelan:
la potencia cae a **0,000** al 20 % de fracción celular, mientras un índice de dispersión de
cobertura conserva **1,000**. El genoma vuelve a centrarse en 0,5 **con la aneuploidía
presente**.

**Por qué esta.** Es el único resultado del proyecto que es un hallazgo metodológico general,
no una observación sobre este paciente. Es lo más citable.

**Lo que NO se puede decir.** Que superamos a MoChA. **El comparador no es MoChA**: carece de
fase de largo alcance. Esa rama está marcada `UNVALIDATED · PARKED` y la propia figura lo lleva
escrito en rojo dentro del panel D. Decir «superamos al método estándar» sería exactamente la
exageración que este proyecto documenta haber evitado.

**Criterio oficial:** innovación (25 %).

## 3 · `fig07_track2_evidence_matrix` — la honestidad intelectual

**Qué se dice.** La cadena «este gen causa la enfermedad, luego este fármaco ayudará» se
descompone en **8 puentes × 10 dimensiones = 80 celdas**. **61 están vacías.** El puente 7 es
el hueco **traduccional**, con contraevidencia verificada. El puente 8, si la intervención
mueve a la vez inestabilidad cromosómica y supervivencia clonogénica, está **vacío en las diez
dimensiones: nadie lo ha medido nunca**.

**Por qué esta.** Las celdas vacías **son** el resultado. Un argumento terapéutico parece
fuerte casi siempre porque nadie dibujó la cadena.

**Lo que NO se puede decir.** Que una celda `ABSENT` signifique que la afirmación es falsa.
Significa que **nadie lo ha medido**. Y no hay puntuación global, a propósito.

**Criterio oficial:** impacto potencial (25 %) e innovación.

## 4 · `fig08_track2_portfolio` — la propuesta

**Qué se dice.** Tres brazos farmacológicos aprobados en **tres papeles distintos**, más
tres controles: **dos hipótesis candidatas y un comparador adversarial**. **Azitromicina** es el único brazo dirigido al alelo truncante de este paciente, y
no tiene ninguna evidencia directa. **Arimoclomol** es el único con contraevidencia verificada,
y por eso vale como **centinela de falsación**: informa al fallar. **Sirolimus** no compite:
está para demostrar por qué rescatar más células aneuploides no equivale a un buen desenlace.
Es el único con evidencia farmacológica directa **en un modelo de CIN en Drosophila** —el
calificativo va siempre pegado— y esa evidencia ya es **parcialmente negativa** en el desenlace
que importa.

**Por qué esta.** Es la respuesta literal al entregable de Track 2, y a la vez la demostración
de que no se ha convertido en una carrera con ganador.

**La frase exacta, en voz alta, no en un pie de figura.** *Nominamos brazos farmacológicos
para discriminación preclínica, no un ganador terapéutico ni una recomendación clínica.*
Ninguno de los tres se propone para administración a ningún paciente.

**Y no se dice «no hay nominación».** Suena a que no se respondió la pregunta del entregable,
cuando sí se responde: lo que se nomina son brazos experimentales, no un ganador.

> **Para vídeo, versión reducida.** La `fig08` completa es una figura de **informe**: a tamaño
> de vídeo tiene demasiado texto pequeño. Para el pitch sobreviven solo **los tres papeles y la
> pregunta que mata cada brazo**; el panel A de procedencia se cuenta de palabra. Esa versión
> reducida **todavía no está construida**: se hace al preparar el vídeo, no antes.

**Criterio oficial:** impacto (25 %) y rigor.

---

## Reparto de los 3 minutos

| Tramo | Contenido | Figura |
|---|---|---|
| 0:00–0:25 | El caso y la pregunta. Un niño real, MVA sospechada, WGS y nada más | — |
| 0:25–1:00 | Búsqueda sin panel y el `A0` #4 contado de frente | **fig01** |
| 1:00–1:40 | El modo de fallo del BAF en aneuploidía variegada | **fig06** |
| 1:40–2:20 | Los ocho puentes y las 61 celdas vacías | **fig07** |
| 2:20–2:50 | La cartera de tres papeles y su regla de descarte | **fig08** |
| 2:50–3:00 | Escalabilidad en una frase, y la frase de no-recomendación clínica | — |

## Las que se quedan fuera, y por qué

No es que sean peores. Es que **no caben en tres minutos**, y algunas se leen mal a tamaño de
vídeo.

| Figura | Motivo |
|---|---|
| `fig00_fastq_qc` | Fundamental, pero «los datos son aptos» no es un latido narrativo. Se menciona de palabra |
| `fig02_gene_browser` | Excelente a tamaño completo, **demasiado densa** para vídeo: 1 497 variantes de ClinVar. Su conclusión (`PM1` no aplica) se dice en una frase |
| `fig03_pocket_and_conservation` | Sostiene el mecanismo, pero abre una discusión estructural que no cabe |
| `fig04_alphagenome_*` | Es un **negativo**: ALT sigue a REF en todas las modalidades. Importa mucho para el registro y muy poco para el pitch |
| `fig05_hpo_disease_matrix` | Misma razón que fig02: densa, y su conclusión (la nefrocalcinosis es el único rasgo sin cobertura) cabe en una frase |

## Reglas para el vídeo

1. **Los dos números de `BUB1B` van siempre juntos.** `A0` #4 y `A0-FREQFIX` #1. Nunca solo el
   segundo.
2. **Ninguna recomendación clínica.** Ni una pauta, ni una dosis, ni «mejoraría al paciente».
3. **Nada de datos del paciente en pantalla**: ni coordenadas, ni HGVS, ni genotipos, ni el
   identificador de muestra. Las figuras ya están saneadas; el guion también tiene que estarlo.
4. **La fase sigue sin resolver.** Si aparece la palabra «diagnóstico», está mal: es una
   *hipótesis causal candidata*.
5. **Las figuras hablan inglés.** El guion, en el idioma que se decida, pero las figuras no se
   retocan para el vídeo: son las mismas que están en `figures/pub/`.
6. **`LZTR1` no entra en el pitch.** Es un candidato secundario de investigación, va en el CSV
   y en el informe de Track 1, y en tres minutos solo distraería de `BUB1B` y abriría una
   conversación clínica mucho más grande de la que cabe.
7. **Nunca «evidencia directa» a secas para sirolimus.** Siempre «en un modelo de CIN en
   Drosophila». Sin el calificativo, a un jurado clínico le suena a dato humano.

## Cómo obtenerlas

```bash
python src/figures/render_all.py
```

Salen en `figures/pub/` como SVG y PNG a 300 dpi, y en `figures/pub/thumb/` en versión de
índice. Son **deterministas**: dos renderizados producen ficheros idénticos byte a byte, así
que la figura del vídeo y la del repositorio son la misma.
