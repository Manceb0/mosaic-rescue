# MASTER BRIEF: MVA Hackathon 2026

> **Repositorio privado obligatorio.** Este documento contiene fenotipo clínico de un menor real. Ver `CONTRIBUTING_RESEARCH.md`, Regla Dura 1.

---

## §0. El reto

**Track 1**, identificar la(s) variante(s) causal(es).
**Track 2**, proponer fármacos ya aprobados científicamente plausibles para investigación terapéutica.

La meta **no** es afirmar que hay una cura. Es producir **una hipótesis terapéutica novedosa, falsable, reproducible y defendible** para investigación posterior, más un diagnóstico causal bien argumentado.

---

## §1. Inventario de datos: lo que existe y lo que no

### Existe

| Archivo | Tamaño | Notas |
|---|---|---|
| VCF del paciente + índice (nombre real en `config/paths.yaml`, gitignored) | — | VCF de WGS |
| `..._S16_L001_R1_001.fastq.gz` | 10,5 GB | Carril 1, lectura 1 |
| `..._S16_L001_R2_001.fastq.gz` | 11 GB | Carril 1, lectura 2 |
| `..._S16_L002/L003/L004_R1/R2_001.fastq.gz` | — | Carriles 2-4 |
| **Total** | **~86 GB** | |
| `Challenge_Clinical_Phenotype_1.docx` | — | Fenotipo HPO |

El identificador de flowcell del nombre de fichero sigue el patrón NovaSeq S4, y el sufijo de muestra indica su posición en la hoja de muestras. Los valores concretos no se reproducen aquí: identifican la corrida y la muestra.

### NO existe (no lo asumas, no lo inventes)

- RNA-seq, single-cell, proteómica
- Muestras longitudinales o de múltiples tejidos
- Cariotipo celular directo
- Genotipos parentales o material de productos de la concepción
- Tejido tumoral del rabdomiosarcoma

### Estimación de cobertura: resolver el día 1

21,5 GB por carril × 4 ≈ 86 GB comprimidos. Eso **no** son 30x; el rango probable es **45-60x**, posiblemente más si las calidades están binarizadas (NovaSeq). Comando exacto sobre un carril:

```bash
zcat "$FASTQ_L001_R1" | \
  awk 'NR%4==2 {n++; b+=length($0)} END {print n" reads, "b" bases"}'
```

Multiplica ×2 (R1+R2) y ×4 (carriles), divide entre 3,1e9.

**Por qué importa.** Más profundidad reduce el ruido estadístico de BAF y LRR, pero **no hace nada contra el problema de cancelación** descrito en §6. La cancelación es estructural, no de profundidad. Si son 60x, la ruta de dispersión de cobertura se refuerza mucho; la ruta de BAF faseado sigue con el mismo techo.

Nota importante: a 45-60x el factor limitante deja de ser el ruido binomial y pasa a ser el **sesgo sistemático** (GC, mapabilidad, sesgo de alelo de referencia). Eso convierte los controles procesados con pipeline idéntico de "deseables" en **obligatorios**.

---

## §2. Fenotipo clínico (verbatim del documento de los organizadores)

| Rasgo clínico | Término HPO | HPO ID | Presentación / notas |
|---|---|---|---|
| Rabdomiosarcoma | Rhabdomyosarcoma | HP:0002859 | Tumor maligno de partes blandas, el evento oncológico primario que desencadenó la investigación urgente |
| Nefrocalcinosis | Nephrocalcinosis | HP:0000121 | Depósitos de calcio en tejido renal; **presente desde el nacimiento** |
| Talla baja | Short stature | HP:0004322 | Talla muy por debajo del rango esperado para edad y contexto familiar |
| Baja masa muscular / fallo de medro | Failure to thrive | HP:0001508 | Documentado repetidamente; escasa ganancia ponderal y desarrollo muscular desde etapa temprana |
| Baja masa muscular / fallo de medro | Skeletal muscle atrophy | HP:0003202 | Masa muscular reducida clínicamente junto al fallo de medro |
| Parto prematuro | Premature birth | HP:0001622 | Nacido a las **32 semanas** de gestación |
| Muy bajo peso al nacer | Small for gestational age | HP:0001518 | **~1 kg al nacer**, bajo peso severo, compatible con CIR |
| Abortos de repetición parentales | Recurrent spontaneous abortion | HP:0200067 | Múltiples pérdidas gestacionales previas al nacimiento del probando; historia materna/parental |

**Notas de los organizadores, textuales en su intención:**
- Ningún rasgo aislado es diagnóstico. La relevancia está en la coocurrencia de predisposición tumoral, restricción de crecimiento, anomalías renales, historia perinatal adversa y pérdida reproductiva parental como un **clúster fenotípico coherente**.
- *"La historia de abortos de repetición es clínicamente significativa y debe tratarse como parte del input fenotípico, no como mero contexto."* En trastornos de inestabilidad cromosómica, la pérdida reproductiva puede reflejar mecanismos heredables o de novo.

### §2.1 Análisis de lo que ESTÁ y lo que NO ESTÁ

Frecuencias en una serie de 31 casos de MVA1 (`Neurol Sci` 2022, DOI 10.1007/s10072-022-06247-w):

| Rasgo | Frecuencia en MVA1 | ¿Presente en el probando? |
|---|---|---|
| Retraso de crecimiento pre/postnatal | 93,5 % | **Sí** |
| Microcefalia | 87 % | **No listado** |
| DI / retraso del desarrollo | 77,4 % | **No listado** |
| Convulsiones epilépticas | 45,1 % | **No listado** |
| Anomalías cerebrales (incl. CAA) | 32,2 % | No listado |
| Malformación Dandy-Walker | 25,8 % | **No listado** |
| Malignidad | 38,7 % (Wilms, RMS, leucemia) | **Sí, rabdomiosarcoma** |
| Disfunción renal | 12,9 % | Sí (nefrocalcinosis) |
| Anomalías genitales | 12,9 % | No listado |
| Disfunción endocrina | 12,9 % | No listado |

**Interpretación.** La ausencia de microcefalia, retraso del desarrollo, convulsiones y Dandy-Walker en una lista curada de "rasgos que llevaron al diagnóstico" es informativa. Dos lecturas posibles:
1. La lista es deliberadamente parcial (solo los rasgos que dispararon el WGS).
2. El caso es atípico para MVA1 clásica.

En Track 1 esto debe **redistribuir peso entre genes MVA**, no ignorarse. Nota incómoda: MVA2 (`CEP57`) cursa con tamaño cefálico normal y sin microcefalia ni retraso del desarrollo comunes, pero tampoco con predisposición tumoral, y este niño tuvo un rabdomiosarcoma. Ese conflicto hay que resolverlo con la variante, no con la narrativa.

**La nefrocalcinosis es el rasgo anómalo.** No es un rasgo reconocido de MVA (la serie reporta "disfunción renal" genérica al 12,9 %, no nefrocalcinosis), y **"presente desde el nacimiento"** descarta el mecanismo adquirido habitual del prematuro (furosemida, NPT, carga de calcio), que es postnatal y se desarrolla en semanas. Ver §8.

---

## §3. Genética de la MVA: base que restringe todo

### §3.1 Universo génico (NO hardcodear BUB1B)

Genes clásicos: **BUB1B** (MVA1), **CEP57** (MVA2), **TRIP13** (MVA3).

Ampliación documentada (`Clin Cancer Res` 30:5009, 2024): **CENATAC** (=CCDC84), **SLF2**, **SMC5**, **MAD2L1BP** (p31^comet^). Fuentes clínicas añaden **BUB1**, **BUB3**, **MAD1L1**, **CEP192**. Variantes en `SMC5`/`SLF2` causan el cuadro emparentado **síndrome de Atelis**.

Un panel de tres genes tiene probabilidad no trivial de fallar.

### §3.2 Arquitectura alélica en BUB1B: la palanca terapéutica

Patrón dominante: **compuesto heterocigoto, un alelo truncante (nonsense / splice / transcrito ausente) más un alelo missense, típicamente en el dominio quinasa**. Hay familias con missense materno y ausencia total de transcrito paterno demostrada por RT-PCR. Existe además un haplotipo hipomórfico común que actúa como segundo alelo.

Mecanismo clave: **los niveles de proteína BubR1 son muy bajos en pacientes con mutaciones en BUBR1, incluso con missense, en gran parte porque las proteínas mutantes tienden a ser inestables.**

Umbral cuantificado (`Hum Genet` 2008, DOI 10.1007/s00439-008-0572-y): un gradiente de BUBR1 residual (8,5 / 10 / 14 / 58 / 77 %) generado con shRNA mostró PCS en todos los niveles, pero **aneuploidía clara solo por debajo del ~50 % de proteína residual**. La función es marcadamente dependiente de dosis.

> Consecuencia conceptual: la MVA1 es, al menos en parte, **una enfermedad de dosis proteica con umbral conocido**, como la FQ o Gaucher. Eso abre la vía de estabilización postraduccional en vez de corrección genética.

### §3.3 Riesgo tumoral: el limitante duro

~1 de cada 3 individuos con MVA desarrolla cáncer, típicamente antes de los 5 años: tumor de Wilms, rabdomiosarcoma embrionario, LLA, tumor de células de la granulosa. También SMD. Vigilancia recomendada: ecografía renal cada 3-4 meses hasta los 5 años; sin cribado establecido para los demás tumores.

El riesgo convincente está descrito sobre todo para MVA1 (`BUB1B`) y MVA3 (`TRIP13`).

**Caso de advertencia que hay que citar:** en un informe de MVA2 diagnosticada por exoma, los autores señalan que de haberse conocido el diagnóstico antes, **posiblemente no se habría prescrito hormona de crecimiento**. En un trastorno de inestabilidad cromosómica, un fármaco proliferativo aparentemente benigno es una decisión de riesgo oncológico.

### §3.4 Biología celular de la aneuploidía

- **Estrés proteotóxico.** Las células aneuploides humanas muestran función de HSF1 y HSP90 comprometida y capacidad de plegamiento deficiente, que moldea directamente la expresión génica.
- **Compensación de dosis proteica.** La mayoría de proteínas no cambia lo que predice el número de copias. El amortiguamiento es fuerte para subunidades de complejos y ribosomas. Las subunidades excedentes se degradan **o se agregan**; la agregación es casi tan eficaz como la degradación, y explica por qué el estrés proteotóxico es universal en el estado aneuploide.
- **Asimetría ganancia/pérdida** (`Cell` 2025, modelo isogénico 3q gain / 3p loss): la ganancia se compensa por **mayor degradación** de subunidades excedentes; la pérdida **no** se contrarresta por degradación global sino por **mayor síntesis** de las proteínas del segmento perdido que forman complejos estables. Dos mecanismos, dos dianas distintas.
- **Autofagia saturada.** Se activa en cariotipos anormales, pero funcionar cerca de saturación compromete la mitofagia, acumula mitocondrias disfuncionales y ROS.
- **mPOS.** Ver §7.
- **Inflamación.** La CIN puede evocar respuesta inflamatoria vía cGAS-STING por micronúcleos rotos o puentes de cromatina, **fuertemente cuestionado**, ver §12.

### §3.5 Supresores genéticos y adaptación

- **UBP6** (levadura): pérdida de función mejora el crecimiento de cuatro cepas aneuploides distintas atenuando los cambios de composición proteica. Homólogo humano relevante: `USP14`.
- **SSD1** (levadura silvestre): aislados silvestres toleran amplificación cromosómica; la base es Ssd1, regulador traduccional de unión a ARN, vía fisiología mitocondrial + mitigación del estrés de proteostasis. **Recapitular los defectos de `ssd1Δ` con tratamiento farmacológico combinatorio bloqueó selectivamente la proliferación de aneuploides frente a euploides**, prueba de concepto de que un estado supresor genético puede imitarse farmacológicamente.
- **Adaptación humana** (`EMBO Rep` 25:5169, 2024): clones aneuploides de RPE-1 p53−/− adaptados tras cultivo prolongado proliferan más manteniendo cariotipos aberrantes; **todos muestran CIN reducida e inflamación reducida**.

### §3.6 El eje progeroide

Ratones `BubR1^H/H` (~10 % de proteína) son progeroides y acumulan células p16^Ink4a^-positivas. En ese fondo, INK-ATTAC elimina esas células y **la eliminación de por vida retrasa los fenotipos; la tardía atenúa los ya establecidos**, pero **sin aumento significativo de la esperanza de vida**, y eliminando solo ~30 % de las células p16+. En dirección opuesta, la sobreexpresión sostenida de BubR1 preserva integridad genómica, reduce tumorigénesis y retrasa el envejecimiento.

Vías farmacológicas hacia arriba (ambas con conflicto interno, ver §12):
- **K250**: acetilación por PCAF protege a BubR1 de la degradación por APC/C-Cdc20; HDAC2/3 la revierten.
- **K668**: la acetilación **promueve** la degradación; SIRT2 (NAD+-dependiente) la revierte y aumenta los niveles de BubR1.

---

## §4. Marco conceptual: los dos ejes opuestos

Toda la literatura oncológica de aneuploidía busca **matar** células aneuploides. En MVA el paciente **es** un mosaico de células aneuploides. Eso define dos ejes literalmente contrarios:

| | **Eje A (Tolerancia** | **Eje B) Poda clonal** |
|---|---|---|
| Objetivo | Que las células aneuploides funcionen mejor | Que los clones más inestables desaparezcan |
| Fenotipo diana | Crecimiento, proteostasis | Riesgo tumoral |
| Precedentes | `ubp6Δ`, `SSD1`, HSF1↑, adaptación RPE-1 | KIF18A, AICAR+17-AAG |
| Riesgo dominante | **Tolerar aneuploidía = fenotipo precanceroso** | Matar células en un niño en desarrollo |

**Esta tensión es la aportación intelectual central del proyecto.** Todos van a proponer "un fármaco que ayude". Casi nadie va a formalizar que ayudar a la célula a tolerar la aneuploidía es exactamente lo que la oncología define como paso temprano de tumorigénesis, en un niño que **ya tuvo un rabdomiosarcoma**.

Desambiguación: es una cuestión de compartimento celular (postmitótico vs. progenitor proliferativo), no filosófica.

---

## §5. Arquitectura acordada (híbrida)

```
                    PATIENT WGS + HPO
                           │
                           ▼
                  1. CAUSAL MECHANISM
                     (Track 1)
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
    2. MOSAIC        3. MITOREAD    4. SV / SEGUNDO HIT
    FINGERPRINT      mtDNA-CN       pares discordantes
    BAF/LRR          medida          split reads
    MoChA            ortogonal       translocación equilibrada
    dispersión            │                │
              └────────────┼────────────────┘
                           ▼
                  CONSISTENCY CHECK
             (no "convergencia mecanística")
                           │
                  tabla 2×2 preregistrada
                           │
                           ▼
                   DRUG HYPOTHESIS
                    (ARIMOCLOMOL?)
                           │
                           ▼
                    TRY TO KILL IT
              ┌────────────┴────────────┐
              ▼                         ▼
      ¿rescata mitocondrias?   ¿hace más viables
                               las células CIN?
              └────────────┬────────────┘
                           ▼
                  SAFE RESCUE CORRIDOR
                           │
                           ▼
                  NEXT BEST EXPERIMENT

  ═══ EN PARALELO, COMO ALARMA QUE PUEDE INTERRUMPIR TODO ═══
                  HPO RESIDUAL AUDIT  (§8)
```

**Cambios respecto a versiones previas, deliberados:**
- El nodo que une las ramas se llama **consistency check**, no "convergencia mecanística". Con n=1 bulk tienes **un** número de carga aneuploide y **un** número de mtDNA-CN: un punto, no una regresión. No puedes demostrar el enlace dentro de este paciente. Lo que tienes son dos observaciones independientes compatibles con un mecanismo publicado.
- `HPO Residual` corre en paralelo con capacidad de interrumpir la línea principal.
- Módulos eliminados por falta de datos que los sostengan: *aneuploid fitness landscapes*, *Rescue Replay*, *forecasting evolutivo*. Presuponen resolución de célula única o series temporales que este dataset no tiene. O se reetiquetan explícitamente como simulación, o se quitan. Un experto lo detectará en el minuto tres.

---

## §6. El núcleo técnico: por qué MVA es más difícil que las mCA clonales

### §6.1 El problema de cancelación de BAF

Este es el hallazgo técnico más importante del proyecto y hay que presentarlo, no esconderlo.

Trisomía del cromosoma X presente en fracción *f* de células.

**Caso clonal** (todas las células ganaron el mismo homólogo, p.ej. el materno):
- Alelos A totales = (1−f)·1 + f·2 = 1+f ; alelos B totales = 1
- BAF = 1/(2+f) ≈ 0,5 − f/4. Para f = 0,02 → desplazamiento ≈ **0,5 %**

**Caso variegado** (eventos independientes entre linajes; qué homólogo se gana es aleatorio; fracción f/2 ganó A y f/2 ganó B):
- A = (1−f) + 2(f/2) + 1(f/2) = 1 + f/2
- B = (1−f) + 1(f/2) + 2(f/2) = 1 + f/2
- **BAF = 0,5 exacto. Cancelación completa.**
- Cobertura: copias totales = 2 + f → **la señal de LRR sobrevive intacta.**

Y si unas células tienen trisomía del cromosoma X y otras monosomía del mismo, **también se cancela el LRR** (2 + f₁ − f₂).

### §6.2 Consecuencia para MoChA

MoChA alcanza sensibilidad reportada por debajo del 1 % de fracción clonal en el estudio de `Nature Genetics` 2023 sobre 67 390 WGS a ~30x, usando genotipos faseados + BAF + cobertura.

**Esa sensibilidad no transfiere directamente a MVA**, y no porque MoChA sea malo. Las mCA de hematopoyesis clonal descienden de **una** célula ancestral: un solo homólogo, cero cancelación, y el faseo de largo alcance amplifica esa asimetría. **MVA viola el supuesto de clonalidad del que MoChA extrae su potencia.**

### §6.3 El índice de dispersión: justificación correcta

El "aneuploid dispersion index" **no** debe venderse como "enormemente más potente". Esa afirmación no está demostrada. Su justificación correcta es mecanística: **es el estadístico que sobrevive a la cancelación.**

Definición operativa: la varianza de la desviación log-ratio de cobertura (y del BAF) *a través de* los cromosomas, comparada con una distribución nula construida con controles procesados con pipeline idéntico.

**Nivel de evidencia: L1 hasta simularlo y compararlo contra MoChA.** Esa simulación es una tarea explícita del plan (Fase 3).

### §6.4 Predicción preregistrable

MVA debería producir **dispersión de LRR elevada con dispersión de BAF relativamente preservada**, una asimetría que las mCA clonales no producen. Esa asimetría *es* la huella. Y el BAF residual que no se cancele informa sobre selección clonal, que es justo lo que la literatura de adaptación a aneuploidía (§3.5) predice.

### §6.5 Metodología recomendada

`detección estándar de mCA (MoChA) + BAF/LRR + índice de dispersión` → **"bulk genomic mosaic fingerprint"**.

No prometer reconstrucción de células individuales. No prometer "cariotipos fantasma". El entregable honesto es una huella agregada.

---

## §7. MitoRead: la medición ortogonal

### §7.1 La idea

El ~1 % de las lecturas de cualquier WGS mapea al genoma mitocondrial y prácticamente todos los pipelines diagnósticos lo filtran por defecto. De ellas sale el **número de copias de ADN mitocondrial por célula**, como cociente de cobertura mtDNA/nuclear.

**Lenguaje correcto:** es una **medida genómica derivada de cobertura**, un proxy. **No** es "un ensayo funcional medido en el paciente". Esa palabra en una presentación destruye credibilidad.

### §7.2 Cadena biológica

El mosaicismo aneuploide produce exceso de proteína de los cromosomas ganados, y ese exceso genera estrés proteotóxico → `saturación de chaperonas → secuestro de precursores mitocondriales en cuerpos p62/SQSTM1` → `importación mitocondrial deficiente` → `red mitocondrial agrupada perinuclearmente, ROS elevado, menos ADNmt`.

### §7.3 Encuadre correcto respecto al fenotipo

**Corrección importante.** No decir que esto "explica lo que MVA no explica". El retraso de crecimiento aparece en el 93,5 % de los casos de MVA; no es un fenotipo residual misterioso.

El encuadre correcto es: **MitoRead podría identificar un mecanismo aguas abajo que contribuya a fenotipos ya conocidos de MVA** (fallo de medro, atrofia muscular, talla baja). Eso es una afirmación de **mediación**, no de explicación, y es más científica.

### §7.4 Confusores: serios

`mtDNA-CN` en sangre depende fuertemente de:
- **Composición celular** (fórmula leucocitaria)
- **Recuento plaquetario**, las plaquetas tienen mitocondrias pero **no núcleo**, así que distorsionan directamente el cociente mtDNA/nuclear
- Edad, sexo, método de extracción, preparación de librería, plataforma, pipeline

Un control pediátrico de otro protocolo de secuenciación puede producir un "wow" completamente falso.

**Petición concreta al equipo clínico: el hemograma contemporáneo a la extracción** (plaquetas + fórmula). Convierte el confusor de fatal a manejable, y es un email.

### §7.5 Limitación adicional: n=1

Con una sola muestra bulk no hay gradiente interno: no puedes demostrar dentro de este paciente que la carga aneuploide causa el déficit mitocondrial. Es un punto, no una curva dosis-respuesta. Declararlo.

### §7.6 Supuesto mayor

Que la `mtDNA-CN` en **sangre periférica** refleja el estado mitocondrial de músculo y riñón. Es el punto más atacable de toda la rama.

---

## §8. HPO Residual: promovido de QC a hipótesis

### §8.1 Qué cambió

El documento clínico dice **"nefrocalcinosis presente desde el nacimiento"**. La nefrocalcinosis del prematuro es adquirida y postnatal: se desarrolla en semanas de furosemida, NPT y carga de calcio. Si está presente al nacer, es antenatal → hipercalciuria fetal, no yatrogenia.

El prior que originalmente favorecía la explicación adquirida **se invierte**.

### §8.2 La hipótesis: síndrome de Bartter antenatal (aBS)

| Rasgo del probando | aBS |
|---|---|
| Parto prematuro 32 sem | Polihidramnios por poliuria fetal → parto pretérmino. Rasgo definitorio |
| Nefrocalcinosis desde el nacimiento | Hipercalciuria antenatal; típica de tipos 1 y 2 |
| Fallo de medro | Rasgo cardinal |
| Talla baja | Rasgo cardinal |
| Atrofia muscular | Debilidad por hipopotasemia |
| Ausencia de microcefalia y retraso del desarrollo | Consistente: aBS no los causa |
| Abortos de repetición | Depende del subtipo, ver abajo |

**Rama X-ligada, MAGED2** (Xp11.2): causa aBS transitorio, la forma perinatalmente más grave, con polihidramnios desde la semana 18-20 y prematuridad extrema. En la serie original (`NEJM` 2016, DOI 10.1056/NEJMoa1507629): en una familia, **tres gestaciones de varones se complicaron con polihidramnios y prematuridad; un feto murió**; en la cohorte total **dos fetos murieron in utero sin causa reconocible en autopsia**. Herencia recesiva ligada al X, madre portadora sana → **pérdidas recurrentes de fetos varones afectados**, sin invocar aneuploidía.

Detalle notable: MAGED2 codifica una proteína que transloca al nucleoplasma bajo estrés nucleolar, **se considera implicada en regulación del ciclo celular**, y está vinculada a varios cánceres.

**Ramas autosómicas recesivas persistentes:** `SLC12A1` (tipo 1), `KCNJ1` (tipo 2), `BSND` (tipo 4a), `CLCNKA`+`CLCNKB` (tipo 4b).

### §8.3 Contrapesos honestos

- El aBS por `MAGED2` es **transitorio**: se resuelve en semanas, pronóstico de crecimiento normal en seguimiento. Choca con talla baja y fallo de medro persistentes. Las formas AR persistentes encajan mejor con el fenotipo mantenido pero explican peor los abortos.
- **1 kg a las 32 semanas es CIR severo**, y el CIR severo es firma de MVA (93,5 %), no de Bartter, donde el CIR es ocasional. Prematuridad y nefrocalcinosis tiran hacia un lado; CIR severo hacia el otro. **Esa divergencia es la firma de un fenotipo mezclado**, no de un gen que lo explique todo.
- Tasa base: los diagnósticos duales ocurren en ~2-7,5 % de los casos diagnosticados, y son ~3× más frecuentes en familias consanguíneas (`Genet Med` 2019, Smith et al.). Precedente casi con esta forma: microcefalia por `ASPM` homocigoto **+** cistinosis nefropática por `CTNS`, con acidosis tubular renal, microcefalia, restricción de crecimiento y retraso de maduración ósea.

### §8.4 La pregunta que lo resuelve: una sola

**¿Hubo polihidramnios en el embarazo?**

El aBS produce polihidramnios severo desde la semana 18-22. La MVA se asocia a **oligo**hidramnios. Son opuestos. Una línea de la historia obstétrica decide.

### §8.5 Falsación gratis

Ya está en la historia clínica: alcalosis metabólica hipopotasémica e hipoclorémica, renina y aldosterona elevadas, cociente calcio/creatinina urinario alto. Si son normales, la hipótesis muere sin gastar un core-hora.

Si son compatibles: indometacina + reposición electrolítica es tratamiento aprobado que **restituye el crecimiento normal**.

### §8.6 Encuadre estratégico

Esto **no reemplaza** la línea principal, el hackathon es de MVA. Pero el valor esperado de una tarde de trabajo es desproporcionado, y hay una asimetría: si aciertan, el resultado es un niño con una tubulopatía tratable que se estaba perdiendo bajo el diagnóstico de MVA. Ningún candidato de reposicionamiento va a competir con eso.

Diferencial completo a testar en el VCF: ver `config/panels/nephrocalcinosis.txt`.

---

## §9. Variantes estructurales y el segundo hit ausente

Los organizadores dicen expresamente que la pérdida reproductiva es input fenotípico. La indicación clásica ante abortos de repetición es cariotipo parental buscando **translocación equilibrada**.

No tenemos a los padres. Pero si un progenitor la porta, el probando puede portar la forma equilibrada, y eso **solo se ve con llamado de variantes estructurales sobre los FASTQ** (pares discordantes + split reads: Manta, DELLY, GRIDSS). Ningún pipeline centrado en SNVs lo encuentra.

**Corolario decisivo para Track 1:** si el análisis estándar encuentra **un solo** alelo patogénico en un gen MVA, el segundo puede ser un SV, una variante intrónica profunda o una reguladora. Esto es el problema del "segundo hit ausente", es frecuentísimo en diagnóstico real, y es la razón por la que entregaron FASTQ y no solo un VCF.

### §9.1 Sobre el faseo: no prometer de más

**`unphased` ≠ `trans`.** Con short-read PE, dos variantes separadas por más de la distancia de fragmento quedan sin fase salvo que haya un SNP heterocigoto puente. Sin padres, el resultado honesto es *"fase no resuelta"*.

Escribir siempre: *"se intentó faseo respaldado por lecturas / estadístico; la fase no resuelta permanece no resuelta"*. Nunca *"los FASTQ resolverán cis/trans"*.

---

## §10. Hipótesis farmacológica y su colisión con la oncología

### §10.1 La clase mecanística candidata, y qué se nomina exactamente

> **Estado a 2026-09-02.** Se nomina una **cartera experimental**: dos hipótesis farmacológicas
> (azitromicina, arimoclomol) y un comparador adversarial (sirolimus), para **discriminación
> preclínica**. **No** se nomina un ganador terapéutico ni se recomienda administrar ningún
> compuesto.
>
> La compuerta **terapéutica** exige cinco condiciones (aprobado · proximidad mecanística a un
> puente nombrado · evidencia **de ese** puente · predicción de rescate falsable · contra-test
> explícito de CIN/tumor) y **ninguna candidata las reúne**, así que ninguna asciende de brazo
> experimental a candidato terapéutico. Ver `docs/TRACK2_MECHANISM_MAP.md` y
> `research/track2_candidates.tsv`.
>
> El estado anterior, a 2026-08-31, decía «NO hay fármaco nominado». Se corrigió porque
> confundía *no nominar un ganador* con *no responder al entregable*: la cartera sí es una
> nominación, de brazos experimentales.

La clase candidata es **modulación de proteostasis y chaperonas**, y lo es por mecanismo, no por enriquecimiento de vías: en el trabajo de aneuploidía-p62 (`Nat Commun` 16:5328, 2025), **la sobreexpresión de proteínas de choque térmico mitigó la agregación proteica y redujo la colocalización de p62 con TOMM20**, es decir, subir HSPs revierte precisamente la lesión que MitoRead propone medir.

Arimoclomol es coinductor de HSP70, aprobado por la FDA el 20 de septiembre de 2024 para Niemann-Pick C en pacientes de 2 años o más, en combinación con miglustat; oral, con posología pediátrica por peso. Actúa **solo bajo estrés celular**, lo que implicaría acción preferente en las células más aneuploides del mosaico.

### §10.2 El hueco que hay que declarar

**Sobreexpresar HSPs genéticamente ≠ administrar arimoclomol.** No hay evidencia de que arimoclomol haya sido probado en esas células aneuploides y haya restaurado la importación mitocondrial. Estado actual: **hipótesis mecanística con el puente farmacológico SIN RESOLVER.** Y hay contraevidencia en otro sistema humano: en fibroblastos NPC1 la sobreexpresión de HSP70 rescató y el coinductor **no lo reprodujo, sin llegar a inducir HSP70** (`docs/EVIDENCE.md` E18). Eso no mata la idea; la vuelve **falsable y concreta**.

### §10.3 La colisión con la oncología: peor de lo que parece

La literatura es explícita: las células cancerosas están **adictas** a HSF1; el HSF1 nuclear alto se asocia a mal pronóstico en varios tumores; y el campo desarrolla **inhibidores** de HSF1 como estrategia antitumoral.

Estamos proponiendo un coinductor de HSF1 en un niño que **ya tuvo un rabdomiosarcoma**. Es la dirección opuesta a lo que hace la oncología.

**La tensión, formulada como corresponde.** Ser coinductor **dependiente de estrés** es a la vez lo que hace la hipótesis atractiva y lo que la hace incierta:

| A favor | En contra |
|---|---|
| Actuaría preferentemente donde hay estrés, es decir en las células más aneuploides del mosaico | La inducción HSF1-dependiente está **al 50–60 %** en células aneuploides (E19): la respuesta que un coinductor amplifica es justo la que está deficiente |

> *HSF1 impairment makes the pathway both mechanistically relevant and pharmacologically
> uncertain. Genetic augmentation can bypass the deficit; whether a stress-dependent
> pharmacological co-inducer can amplify the impaired endogenous response sufficiently
> remains unresolved.*

**No está demostrado que falle.** Un coinductor amplifica una respuesta ya iniciada y no exige una HSF1 intacta. Lo que se afirma es que **el resultado es impredecible desde la evidencia actual**, y por eso es el puente 7.




### §10.4 El experimento que es la mejor diapositiva del proyecto

En "Try to Kill It", **la señal de eficacia y la señal de riesgo oncológico son la misma medición**.

Si arimoclomol rescata preferentemente a las células más aneuploides, eso es simultáneamente:
- la prueba de que el mecanismo es el propuesto, y
- la prueba de que se está mejorando la supervivencia clonogénica de células genómicamente inestables.

Mismo ensayo, dos lecturas opuestas. Diseño: células aneuploides / del paciente ± arimoclomol → p62/TOMM20, mtDNA-CN, ROS, importación mitocondrial, **y simultáneamente** CIN, proliferación, apoptosis y supervivencia clonogénica aneuploide vs. euploide isogénica.

---

## §11. Tabla de evidencia

Marcador de verificación: ✔ = identificador confirmado en búsqueda; ⚠ = conocido en la literatura pero **PMID/DOI no verificado, resolver en PubMed antes de uso público**.

| # | Referencia | Año / tipo | Sistema | Hallazgo usado | Apoya/Contradice | Nivel | Limitación |
|---|---|---|---|---|---|---|---|
| E1 (verificado) | Amponsah PS et al. *Nat Commun* 16:5328. DOI 10.1038/s41467-025-60857-4 | 2025, primario | Células humanas aneuploides isogénicas | p62 citosólico enriquecido en precursores mitocondriales; importación deficiente; **ADNmt reducido**; ROS↑. **HSPs↑ mitigan agregación y colocalización p62–TOMM20** | Apoya + da la diana | L4 | Aneuploidía inducida en líneas, no mosaicismo constitucional |
| E2 (verificado) | Qian Y et al. *Bioinformatics* 33:1399. PMID 28453676, DOI 10.1093/bioinformatics/btw835 | 2017, método | Computacional / WGS | mtDNA-CN estimable desde WGS por cociente de cobertura | Apoya (método) | L5 método | Sensible a cobertura y composición celular |
| E3 (verificado) | Hintzen DC et al. *EMBO Rep* 25:5169. DOI 10.1038/s44319-024-00252-0 | 2024, primario | RPE-1 p53−/− | Adaptación a aneuploidía = menos CIN + menos inflamación | Apoya marco tolerancia | L4 | p53-deficiente; el paciente no lo es |
| E4 (verificado) | *Hum Genet* 2008. DOI 10.1007/s00439-008-0572-y | 2008, primario | HeLa shRNA | Gradiente BUBR1 8,5-77 %; aneuploidía < ~50 % | Apoya umbral de dosis | L4 | Línea cancerosa, no célula primaria |
| E5 (verificado) | García-Castillo H et al. PMID 18548531 | 2008, primario | Pacientes MVA | PCS en 8/8 probandos y **7/7 padres portadores** | Apoya marco familiar | L3 | Cohorte pequeña |
| E6 (verificado) | *Clin Cancer Res* 30:5009 | 2024, guía | Humano | Universo génico MVA ampliado (CENATAC, SLF2, SMC5, MAD2L1BP) | Apoya (no hardcodear) | L5 | Guía, no primario |
| E7 (verificado) | *Neurol Sci* 2022. DOI 10.1007/s10072-022-06247-w | 2022, serie + revisión | 31 casos MVA1 | Frecuencias por rasgo (§2.1) | Define línea base | L2 | Series pequeñas, sesgo de publicación |
| E8 (verificado) | Laghmani K et al. *NEJM* 2016. DOI 10.1056/NEJMoa1507629 | 2016, primario | Humano, 13 varones / 7 familias | `MAGED2` → aBS transitorio; polihidramnios 19-20 sem; **2 fetos muertos in utero**; nefrocalcinosis en 6, persistente en 4 | Apoya §8 | L5 | Fenotipo transitorio; no explica talla baja persistente |
| E9 (verificado) | Consenso ERKNet Bartter. *Kidney Int* 2021 | 2021, guía | Humano | Poliuria, deshidratación, fallo de medro, retraso de crecimiento, polihidramnios con parto prematuro; hipercalciuria y nefrocalcinosis típicas de algunas formas | Apoya §8 | L5 | Guía |
| E10 (verificado) | *Bioinformatics/AJHG*: Bi-allelic TRIP13 y ovocitos. PMID 32473092, DOI 10.1016/j.ajhg.2020.05.001 | 2020, primario | Humano + HeLa | Variantes TRIP13 reducen proteína y acumulan HORMAD2; **sin efecto mitótico detectable**; cRNA de TRIP13 rescató ovocitos | Contexto mecanístico | L4 | Rescate en meiosis/infertilidad, **no** en MVA |
| E11 (verificado) | Ahlmann-Eltze C et al. *Nat Methods* 22:1657. PMID 40759747 | 2025, benchmark | Computacional | Modelos fundacionales **no superan** líneas base lineales en predicción de perturbación | **Contradice** uso acrítico de DL | L5 | Rebatido en parte (bioRxiv oct-2025: sesgo de métricas) |
| E12 (verificado) | Keam SJ. *Drugs* 85:111 | 2025, regulatorio | Humano | Arimoclomol: aprobación FDA 20-sep-2024, NPC, ≥2 años, oral, dosis por peso | Apoya viabilidad | L5 seguridad / L0 para MVA | Sin datos en aneuploidía |
| E13 (sin verificar) | Benatar M et al., arimoclomol en ELA | 2024, ECA | Humano | **No efectivo** para modificar progresión | **Contradice** | L5 | Subir HSPs no es universalmente beneficioso |
| E14 (sin verificar) | Torres EM et al. *Cell* 143:71 | 2010, primario | Levadura | Mutaciones tolerantes a aneuploidía; `UBP6` | Apoya §3.5 | L4 | Ortología imperfecta; dependiente de cariotipo |
| E15 (sin verificar) | Smith ED et al. *Genet Med* 21:2199 | 2019, retrospectivo | Humano | Diagnósticos múltiples ~3× más frecuentes en consanguíneos | Apoya §8 (tasa base) | L4 | Cohorte de laboratorio comercial |
| E16 (sin verificar) | Loh PR et al. / MoChA, *Nature Genetics* 2023, 67 390 WGS ~30x | 2023, primario | Humano | mCA detectadas con genotipos faseados + BAF + cobertura; sensibilidad reportada <1 % de fracción clonal | Apoya método, **con la salvedad de §6.2** | L5 | Validado en mCA **clonales**, no variegadas |
| E17 (sin verificar) | Neumann B et al. *Nature* 464:721. PMID 20360735 | 2010, primario | HeLa, RNAi genómico | MitoCheck: perfilado fenotípico de ~21 000 genes por imagen time-lapse; ~600 genes con papel en mitosis | Priorización fenotípica Track 1 | L4 | HeLa; RNAi con off-targets |

---

## §12. Contraevidencia consolidada: leer antes de afirmar nada

| Afirmación | Evidencia en contra | Consecuencia |
|---|---|---|
| Reversión/matching de firma CMap es fiable | CMap 2 no reproduce la priorización de CMap 1; reproducibilidad de niveles de expresión menor de lo esperado; al comparar con un tercer dataset, mutuamente discordantes | Exigir convergencia de ≥2 rutas independientes; nunca un único ranking |
| AlphaFold predice efecto de variante | ΔpLDDT correlaciona muy débil con ΔΔG (PCC ≈ −0,17); pLDDT global sin correlación; AF2 en gran medida **incapaz** de predecir plegamiento defectuoso por mutación puntual | Usar AF como fuente de estructura + FoldX (pLDDT>70); nunca pLDDT como proxy de efecto |
| Controlabilidad estructural de redes nomina dianas | No eficiente ni óptima funcionalmente; el conjunto mínimo de drivers puede incluir gran parte de los nodos; control energéticamente prohibitivo en algunas direcciones; input puede no ser implementable; **las dinámicas nodales, no los grados, determinan la controlabilidad** | Degradar a análisis exploratorio |
| Micronúcleos → cGAS-STING → IFN | Micronúcleos por radiación, estrés de replicación o errores de segregación **no** activan cGAS-STING (`Mol Cell` 2024); el micronúcleo no es inductor potente; serían los **puentes de cromatina** | Testar la firma IFN empíricamente, nunca asumirla |
| STING como diana | La depleción de STING **no bastó** para superar el defecto de proliferación de clones aneuploides tempranos | No proponer inhibición de STING |
| `UBP6` es supresor universal | Su deleción comprometió el control de calidad citosólico también en cepa aneuploide; solo mejoró un subconjunto de cromosomas (5, 8, 9, 11); no rescató `bir1Δ` | Tolerancia dependiente de cariotipo |
| Senolíticos rescatan MVA | En `BubR1^H/H`, la eliminación de senescentes protegió de patologías **pero no aumentó la esperanza de vida**; solo ~30 % eliminadas; falta prueba rigurosa de que p16+ = senescente | Hipótesis de calidad de vida, no de supervivencia |
| Subir HSPs es terapéutico | Arimoclomol **no efectivo** en ELA | Beneficio específico de contexto |
| DL predice perturbaciones mejor que baselines | Cinco modelos fundacionales y dos de DL **no superaron** líneas base simples; la media de entrenamiento superó a scGPT y scFoundation. *Contrapunto oct-2025: atribuido en parte a calibración de métricas* | Baseline lineal obligatorio como comparador |
| MoChA <1 % transfiere a MVA | Ver §6.2: MVA viola el supuesto de clonalidad | Usar MoChA como suelo comparativo, no como primaria |
| La aneuploidía tiene una cascada única | Ganancia (3q) se compensa por degradación; pérdida (3p) por **mayor síntesis** | Ganancia y pérdida requieren hipótesis distintas |
| Nefrocalcinosis en prematuro es genética | Alta incidencia adquirida asociada a furosemida y NPT en <32 sem / <1500 g | **Pero** "presente desde el nacimiento" invierte el prior (§8.1) |

---

## §13. Ideas exploradas y descartadas (incluir en la presentación)

Mostrar caminos rechazados con la cita que los mata comunica que no se está vendiendo cada correlación encontrada. Un jurado científico lo valora más que una idea adicional.

**Minus-End Anchor / la paradoja del taxano.** Existen líneas celulares que *requieren* paclitaxel para dividirse, y el rescate opera impidiendo el desprendimiento de extremos menos del centrosoma, el modo de fallo de la rama `CEP57`. **Rechazado:** la exposición breve a paclitaxel a dosis baja **induce husos multipolares y aneuploidía**; más neurotoxicidad y mielosupresión en un niño con atrofia muscular y antecedente de rabdomiosarcoma.

**Conformer Flux (TRIP13/MAD2L1BP).** Mecanísticamente sólido: TRIP13 mantiene el pool de O-MAD2; su pérdida vacía el depósito del freno en lugar de apagarlo. **Rechazado para Track 2:** no existe fármaco aprobado que suba `MAD2L1` o `TRIP13`. Forzar una nominación sería peor que no tener candidato. Conservar como marco de Track 1.

**Poda clonal quimiopreventiva (Eje B).** Invertir la letalidad selectiva por aneuploidía como quimioprevención. **Rechazado:** no hay inhibidor de KIF18A aprobado; 17-AAG y AICAR no aprobados; y los antimitóticos causan mielosupresión y neurotoxicidad limitantes en un niño en desarrollo.

**Pedigree Dose–Response.** Interpretar portadores → probando → abortos como tres puntos de una curva humana de función residual. **En pausa condicional:** no verificable sin genotipo parental ni material de productos de la concepción. Reactivar solo si Track 1 confirma arquitectura recesiva convincente. *Nota: el error original de inferir consanguinidad desde los abortos era injustificado; la consanguinidad se mide con ROH desde el VCF.*

---

## §14. Preguntas abiertas al equipo clínico / organizadores

Ordenadas por valor por unidad de esfuerzo. Todas son un email.

1. **¿Hubo polihidramnios u oligohidramnios en el embarazo?** Decide entre §8 y MVA. La pregunta más valiosa del proyecto.
2. **¿La librería es PCR-free?** Si hay amplificación, el ruido de cobertura sube y toda la rama basada en profundidad se tambalea. Condiciona medio proyecto.
3. **Hemograma contemporáneo a la extracción** (plaquetas + fórmula). Necesario para §7.4.
4. **Electrolitos, equilibrio ácido-base, renina, aldosterona, cociente calcio/creatinina urinario.** Falsa o confirma §8 gratis.
5. **Fecha de la primera ecografía renal** que documentó la nefrocalcinosis. Distingue "desde el nacimiento" real de "primera imagen a las 3 semanas".
6. **Historia de medicación neonatal:** furosemida, duración de NPT.
7. **HPO completo, no solo los rasgos que dispararon el WGS.** ¿Hay o no microcefalia, retraso del desarrollo, convulsiones, cataratas?
8. **Tejido de origen del WGS** (sangre, saliva, fibroblasto) y si hubo transfusiones previas. Una transfusión antes de la extracción contamina el mosaicismo con genotipo de donante.
9. **¿Existe cariotipo o array previo?** Sería verdad-terreno gratis para validar §6.
10. **¿Hay resultado de patología del rabdomiosarcoma** con cariotipo/FISH? Los eRMS son hiperdiploides con ganancias cromosómicas recurrentes.

---

## §15. Estándares de evidencia y calibración

Etiqueta toda afirmación:

| Nivel | Significado |
|---|---|
| `L0` | Especulación |
| `L1` | Asociación |
| `L2` | Apoyo ortogonal |
| `L3` | Evidencia funcional |
| `L4` | Evidencia funcional replicada |
| `L5` | Evidencia humana / clínica establecida |

Para cada afirmación importante registra en `docs/EVIDENCE.md`: afirmación exacta, PMID, DOI, URL, año, sistema experimental, humano/animal/celular/computacional, apoya o contradice, relevancia directa o inferida, limitación principal, **y qué resultado la falsaría**.

No citar un paper porque su título parezca relevante. Leer métodos y resultados suficientes para saber qué se demostró realmente.

### Prohibiciones explícitas

- Inventar modalidades de datos que no existen
- Afirmar tratamiento o cura
- Predecir desenlace clínico
- Usar AlphaFold decorativamente
- Tratar el enriquecimiento de vías como mecanismo
- Tratar un score de CMap como prueba
- Presentar una conexión generada por un LLM como evidencia
- Asumir un gen MVA conocido antes de examinar las variantes del paciente
- Lenguaje genérico de "medicina de precisión"
- Proponer un dashboard como la innovación
