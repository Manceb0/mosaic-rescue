# PLAN DE ANÁLISIS

Ordenado por **coste-beneficio**, no por narrativa. Las primeras fases pueden matar hipótesis enteras en horas; las caras van al final.

Regla operativa: **antes de cada fase**, escribir en `docs/DECISIONS.md` qué se espera encontrar y qué resultado mataría la hipótesis. Después, no reescribir la predicción.

---

## PRINCIPIO DE ECONOMÍA COMPUTACIONAL

Alinear 86 GB de FASTQ cuesta decenas de core-horas y ~500 GB de disco. **No lo hagas hasta la Fase 6.** El orden aprovecha tres atajos:

1. **El VCF ya existe.** Si trae `FORMAT/AD` y `FORMAT/DP`, se puede calcular BAF directamente sin realinear. Comprobar primero.
2. **Para `mtDNA-CN` basta un submuestreo aleatorio.** El cociente mtDNA/nuclear se preserva en una muestra aleatoria de lecturas — `fastMitoCalc` usa deliberadamente el 0,1 % del genoma nuclear. Un 2-5 % de las lecturas alineadas da una estimación buena a coste ridículo.
3. **La cobertura por bin para LRR** tolera submuestreo mucho mejor que el llamado de variantes.

Solo el llamado de SV (Fase 6) requiere el BAM completo.

---

## FASE 0 — Higiene y verificación (día 1, ~2 h)

### 0.1 Seguridad del repositorio

```bash
# ANTES del primer commit
git log --all --numstat 2>/dev/null | awk '$1 ~ /^[0-9]+$/ {print $3}' | sort -u | \
  grep -Ei '\.(vcf|bam|cram|fastq|fq|docx)' || echo "historial limpio"
```
Confirmar que el repositorio es **privado**. Crear `config/paths.yaml` (gitignored) con las rutas locales.

### 0.2 Integridad y procedencia de los datos

```bash
# Checksums, para reproducibilidad
sha256sum *.fastq.gz *.vcf.gz > work/checksums.txt

# ¿Qué build de referencia? ¿Qué pipeline? ¿Hay AD?
bcftools view -h "$VCF" | grep -E '^##(reference|source|GATKCommandLine|contig=<ID=(chr)?1,)'
bcftools view -h "$VCF" | grep -E 'FORMAT=<ID=(AD|DP|GQ|PL),'
bcftools query -l "$VCF"            # nombre de muestra
```

**Decisión inmediata:** si `FORMAT/AD` existe, la Fase 3a se hace desde el VCF sin realinear. Si no existe, hay que alinear antes.

### 0.3 Cobertura real

```bash
zcat "$L001_R1" | awk 'NR%4==2 {n++; b+=length($0)} END {print n" reads, "b" bases, readlen~"b/n}'
```
`cobertura ≈ (bases_L001_R1 × 2 × 4) / 3.1e9`

### 0.4 ¿PCR-free?

Preguntar a los organizadores (§14 del brief). Proxy si no responden: tras alinear un submuestreo, la tasa de duplicados. `<5 %` sugiere PCR-free; `>15 %` sugiere librería con PCR y ruido de cobertura elevado.

**Registrar todo en `docs/DECISIONS.md` antes de seguir.**

---

## FASE 1 — Auditoría HPO Residual (día 1, ~4 h) — PUEDE INTERRUMPIR TODO

Se ejecuta primero porque es barata y porque un resultado positivo reordena las prioridades del proyecto entero (ver brief §8).

### 1.1 Consanguinidad

```bash
bcftools roh -G30 --AF-dflt 0.4 "$VCF" -o work/roh.txt
# resumir: nº de ROH >1 Mb, longitud total, F_ROH
```
`F_ROH > 0.0156` (~primos segundos) cambia sustancialmente el prior de recesivas y de diagnóstico dual.

### 1.2 Panel de nefrocalcinosis / tubulopatías

Filtrado bialélico (hom o compuesto het) y hemicigoto en X, con `gnomAD AF < 0.005`, sobre `config/panels/nephrocalcinosis.txt`:

```
# Bartter antenatal
SLC12A1 KCNJ1 BSND CLCNKA CLCNKB MAGED2 CASR
# Acidosis tubular renal distal
SLC4A1 ATP6V0A4 ATP6V1B1 FOXI1 WDR72
# Hipercalciuria / nefrolitiasis / Dent
CLDN16 CLDN19 CYP24A1 SLC34A1 SLC34A3 CLCN5 OCRL VDR
# Hiperoxaluria primaria
AGXT GRHPR HOGA1
# Otros
ALPL SLC9A3R1 KCNJ16 SLC12A3 HNF1B
```

**Atención especial a `MAGED2`** (Xp11.2, X-ligado recesivo): si el probando es varón, basta **una** variante hemicigota. Un pipeline que filtre por "bialélico" la perderá. Buscar explícitamente hemicigotos en X.

### 1.3 Tabla de decisión preregistrada — Fase 1

| Resultado | Interpretación | Acción |
|---|---|---|
| Variante(s) convincente(s) en panel de Bartter/tubulopatía | Hipótesis de diagnóstico dual viva | **Escalar de inmediato.** Solicitar electrolitos, renina, aldosterona, Ca/Cr urinario e historia de líquido amniótico. Documentar como hallazgo principal candidato |
| Variante de significado incierto en el panel | Insuficiente | Registrar, no perseguir salvo que la bioquímica encaje |
| Nada en el panel, `F_ROH` bajo | Segunda enfermedad monogénica improbable | Documentar como **resultado negativo preregistrado**: "se auditó sistemáticamente el fenotipo no explicado; MVA + prematuridad lo cubre". Esa frase es un entregable |
| Nada en el panel, `F_ROH` alto | Ampliar a panel de exoma completo bajo modelo recesivo | Una iteración más, luego cerrar |

---

## FASE 2 — Track 1: mecanismo causal (días 1-3)

### 2.1 Panel MVA ampliado

`config/panels/mva.txt`:
```
BUB1B CEP57 TRIP13 BUB1 BUB3 MAD1L1 MAD2L1 MAD2L1BP
CENATAC CCDC84 SLF2 SMC5 CEP192 PLK4 CENPE KNL1 CASC5
CENPF NDC80 ZW10 ZWILCH RZZ TUBB CDC20 ANAPC1
```

Modelos a probar: bialélico (hom / comp-het), hemicigoto X, de novo (no verificable sin padres — marcar como "no confirmable"), y **un solo alelo patogénico** (bandera roja que dispara la Fase 6).

### 2.2 Anotación y priorización

- VEP / SnpEff con LOFTEE
- `gnomAD` v4: AF, pLI, LOEUF, homocigotos observados
- `ClinVar`
- `AlphaMissense` + `ESM-1b` para missense
- `SpliceAI` para variantes de splicing — **crítico**, dado que el patrón típico de BUB1B incluye alelos de sitio de splicing canónico
- Predicción de **NMD**: aplicar la regla de los 50 nt respecto a la última unión exón-exón. Determina si el alelo truncante produce proteína truncada o nada, y eso cambia la dirección terapéutica

### 2.3 Priorización fenotípica no convencional

Además de conservación y predicción de patogenicidad, priorizar por **fenotipo mitótico observado**: genes cuyo knockdown produce en **MitoCheck** (`Nature` 464:721) las clases fenotípicas de retraso mitótico, cromosomas no alineados y missegregación. Es respaldo funcional independiente que ningún predictor de secuencia aporta. Datos en `mitocheck.org` / Cellular Phenotype Database del EBI.

### 2.4 Faseo — sin prometer de más

```bash
whatshap phase --reference "$REF" -o work/phased.vcf "$VCF" "$BAM"   # requiere BAM (Fase 6)
```
Reportar tres estados: `cis`, `trans`, **`no resuelto`**. Nunca convertir "no resuelto" en "trans". Ver brief §9.1.

### 2.5 Estructura del enrutador mecanístico

Para la variante missense candidata, clasificar el **mecanismo**, no solo la patogenicidad:

| Clase | Firma computacional | Implicación terapéutica |
|---|---|---|
| Desestabilización de plegamiento | ΔΔG alto (FoldX sobre AF2 con pLDDT>70), región de alta confianza | Rama de proteostasis viva |
| Disrupción de interfaz | AF3 del complejo MCC: ipTM cae, PAE inter-cadena sube, contactos perdidos | Sin ruta farmacológica clara — decirlo |
| Pérdida catalítica | Residuo en sitio activo, conservación alta, ΔΔG bajo | Otra rama |
| Truncante / sin transcrito | — | Cuenta como dosis 0 |

**Benchmark obligatorio antes de aplicarlo:** correr el clasificador sobre variantes `BUB1B` de MVA ya publicadas con caracterización funcional. Si no recupera el mecanismo conocido, no sirve para la del paciente. Dos días de trabajo que separan un póster de un resultado.

**No usar ΔpLDDT como proxy de efecto de variante.** Ver brief §12.

---

## FASE 3 — Huella de mosaicismo (días 3-6)

### 3a. BAF desde el VCF (si hay `AD`) — barato

```bash
bcftools query -i 'GT="het" && FORMAT/DP>20' \
  -f '%CHROM\t%POS\t[%AD]\n' "$VCF" > work/het_ad.tsv
```
BAF por SNP = `alt / (ref + alt)`. Agregar por bins de 1 Mb y por cromosoma.

### 3b. Cobertura / LRR

Sobre BAM submuestreado (5 %) o completo: cobertura mediana por bin de 1 Mb, corregida por GC y mapabilidad. Normalizar contra controles procesados **con pipeline idéntico**. Base sugerida: 1000 Genomes 30x de NYGC (procesamiento uniforme, público) — con la advertencia de que la profundidad difiere.

### 3c. MoChA

Ejecutar como referencia y suelo de sensibilidad. Requiere genotipos faseados; sin padres, faseo estadístico contra un panel de referencia.

### 3d. Índice de dispersión aneuploide

Definición: varianza de la desviación log-ratio de cobertura **a través de** los cromosomas, y lo mismo para BAF, comparadas contra una nula empírica de controles.

**Etiqueta de evidencia: `L1`.** La afirmación "más potente que el llamado por cromosoma" **no está demostrada** y no debe escribirse sin la simulación de 3e.

### 3e. Simulación — no opcional

Simular in silico, a la profundidad real del paciente:
1. **mCA clonal**: un solo homólogo ganado, fracciones 0,5-5 %.
2. **Aneuploidía variegada**: N eventos independientes, homólogo aleatorio, fracción total 10-40 % repartida.
3. **Mixta trisomía/monosomía** del mismo cromosoma.

Medir sensibilidad de: MoChA, llamado por cromosoma con umbral, e índice de dispersión. **Esto convierte la afirmación L1 en L3 o la mata.** Es el análisis que más credibilidad aporta por hora invertida.

### 3f. Predicción preregistrada

MVA debería producir **dispersión de LRR elevada con dispersión de BAF relativamente preservada** — asimetría que las mCA clonales no producen. El BAF residual no cancelado informa sobre selección clonal.

### 3g. Tabla de decisión preregistrada — Fase 3

| Resultado | Interpretación |
|---|---|
| Dispersión LRR ↑, BAF preservada | Firma consistente con aneuploidía variegada. Cuantificar carga |
| Dispersión LRR ↑ **y** BAF ↑ | Sugiere componente clonal (¿expansión?). Interesante, distinto de lo predicho — **documentar la sorpresa, no reescribir la predicción** |
| Ninguna dispersión elevada | Techo de detección del WGS bulk. Reportar como hallazgo metodológico con la simulación 3e como respaldo cuantitativo |
| MoChA llama eventos que la dispersión no ve | Revisar; probablemente componente clonal real |

---

## FASE 4 — MitoRead (día 4, ~4 h)

### 4.1 Cálculo

```bash
# Submuestreo de lecturas, alineamiento, y cociente de cobertura
seqtk sample -s42 "$R1" 0.03 > work/sub_R1.fq
seqtk sample -s42 "$R2" 0.03 > work/sub_R2.fq
bwa-mem2 mem -t "$THREADS" "$REF" work/sub_R1.fq work/sub_R2.fq | \
  samtools sort -@4 -o work/sub.bam && samtools index work/sub.bam

samtools idxstats work/sub.bam > work/idxstats.txt
```

`mtDNA-CN ≈ 2 × (cobertura_media_chrM / cobertura_media_autosómica)`

Semilla fija (`-s42`) declarada en `config/`. Alternativa validada: `fastMitoCalc` (PMID 28453676).

### 4.2 Salidas gratuitas del mismo alineamiento

- Heteroplasmia mitocondrial (`mutserve` / `mtDNA-Server`)
- Haplogrupo mitocondrial (`HaploGrep`) — sirve además como control de identidad de muestra
- NUMTs

### 4.3 Controles — la parte difícil

Requisitos mínimos del control: edad pediátrica comparable, mismo tejido, misma extracción, misma preparación de librería, misma plataforma, mismo pipeline. **Y el hemograma contemporáneo** (plaquetas + fórmula), porque las plaquetas aportan mtDNA sin ADN nuclear y sesgan el cociente al alza.

Si no se consigue un control comparable, la conclusión honesta es: *"el valor absoluto no es interpretable; se reporta el método y el número, sin comparación"*. Un control de otro protocolo produce un wow falso.

### 4.4 Lenguaje obligatorio

Escribir siempre: **"medida genómica derivada de cobertura de secuenciación"**, un proxy del contenido mitocondrial. **Nunca** "ensayo funcional".

Y el encuadre correcto (brief §7.3): esto podría identificar un **mecanismo aguas abajo que contribuye** a fenotipos ya conocidos de MVA. No "explica lo que MVA no explica" — el retraso de crecimiento está en el 93,5 % de los casos de MVA.

### 4.5 Limitación n=1

Una sola muestra bulk = un punto, no una curva dosis-respuesta. No se puede demostrar el enlace carga-aneuploide → déficit mitocondrial dentro de este paciente. Declararlo en la diapositiva.

---

## FASE 5 — Consistency check y tabla 2×2 preregistrada

**Escribir esta tabla en `docs/DECISIONS.md` ANTES de ejecutar las Fases 3 y 4.** Su valor es que demuestra ausencia de p-hacking.

| | **mtDNA-CN reducida** | **mtDNA-CN normal** |
|---|---|---|
| **Mosaicismo detectado** | Cadena consistente con el mecanismo publicado (E1). Pasar a hipótesis farmacológica. *Nota: consistencia, no demostración causal* | El mosaicismo detectable no basta para producir déficit mitocondrial medible en sangre → **la rama MitoRead se cierra**; MOSAIC RESCUE continúa sin ella |
| **Mosaicismo no detectado** | Señal mitocondrial sin sustrato aneuploide medible → buscar segunda causa; reactivar Fase 1 con panel mitocondrial | Ambas ramas negativas → el WGS bulk tiene un techo de detección. **Hallazgo metodológico**, respaldado por la simulación 3e |

Tres de las cuatro celdas son publicables.

---

## FASE 6 — Variantes estructurales y segundo hit (días 6-9) — CARA

Solo ahora se justifica el alineamiento completo.

```bash
bwa-mem2 mem -t "$THREADS" -R "$RG" "$REF" "$R1" "$R2" | \
  samtools sort -@8 -m4G -o work/full.bam
samtools index work/full.bam
# marcar duplicados; conservar la métrica (proxy de PCR-free, Fase 0.4)
```

Requisitos aproximados: ~40-80 core-horas, ~500 GB de disco temporal.

### 6.1 Llamado de SV

Al menos dos llamadores, e intersecar: `manta`, `delly`, y opcionalmente `gridss`. Buscar:
- **Translocaciones equilibradas** (motivación: abortos de repetición, brief §9)
- Rupturas dentro o cerca de genes del panel MVA
- Deleciones/duplicaciones intragénicas que expliquen un segundo alelo ausente
- Inserciones de elementos móviles en genes del panel

### 6.2 Segundo hit no codificante

Si la Fase 2 encontró **un solo** alelo patogénico:
- Variantes intrónicas profundas con `SpliceAI` alto
- Región promotora / 5'UTR / 3'UTR del gen
- CNV intragénicas por profundidad (`CNVpytor`, `cn.mops`)
- Verificar cobertura exón a exón en el gen candidato — una deleción de un exón se ve como caída local de cobertura

### 6.3 Faseo definitivo

Con el BAM completo, `whatshap`. Reportar honestamente los tres estados posibles.

---

## FASE 7 — Hipótesis farmacológica y análisis de seguridad

### 7.1 Nominación

Ver brief §10. **No empezar por una base de datos de fármacos.** La secuencia es:
`defecto del paciente` → `consecuencia mecanística` → `punto de intervención` → *y solo entonces* → `¿existe un aprobado que perturbe ese punto en la dirección requerida?`

Un fármaco aprobado con relevancia mecanística débil es **peor** que no tener candidato.

### 7.2 Capa de seguridad — la que nadie más va a construir

Tres filtros duros por candidato:

**a) Riesgo oncológico.** ¿El candidato aumenta tolerancia a aneuploidía, proliferación, escape de apoptosis, atenuación de p53, debilitamiento del checkpoint o tolerancia al daño del ADN? Si sí, bandera roja y trade-off documentado. Precedente a citar: la hormona de crecimiento en el caso de MVA2 (brief §3.3).

Para arimoclomol específicamente: declarar la colisión frontal con la oncología (brief §10.3). Las células cancerosas están adictas a HSF1; el campo desarrolla **inhibidores** de HSF1 como antitumorales. Se está proponiendo un coinductor en un niño que ya tuvo un rabdomiosarcoma. Ser coinductor **dependiente de estrés** es a la vez la razón y el riesgo: actuaría donde hay estrés, pero la inducción HSF1-dependiente está al 50–60 % en células aneuploides (`docs/EVIDENCE.md` E19). **Tensión no resuelta — es el puente 7**, y es exactamente lo que hay que testar.




**b) Disponibilidad pediátrica.** ¿Existe posología pediátrica establecida? (Arimoclomol sí, ≥2 años. Navitoclax no.)

**c) Farmacogenómica del propio paciente.** Extraer del WGS los genotipos PGx (`CYP2C19`, `CYP2D6`, `CYP3A5`, `TPMT`, `NUDT15`, `DPYD`, `SLCO1B1`, `UGT1A1`, `G6PD`) con `PharmCAT` o `Aldy`, y anotar cada candidato contra las guías CPIC. Trivial de implementar, y casi nadie lo hará. Una hipótesis farmacológica que ignora si el paciente es metabolizador pobre del fármaco propuesto está incompleta.

### 7.3 El experimento "Try to Kill It"

Diseño único con doble lectura (brief §10.4):

```
células aneuploides isogénicas / fibroblastos del paciente
  ± arimoclomol
       │
       ├── LECTURA DE EFICACIA
       │     p62 / TOMM20 (colocalización)
       │     mtDNA-CN por qPCR
       │     consumo de oxígeno
       │     importación mitocondrial
       │     ROS
       │
       └── LECTURA DE RIESGO
             tasa de missegregación (H2B-GFP time-lapse)
             proliferación
             apoptosis
             supervivencia clonogénica: aneuploide vs. euploide isogénica
```

**Test discriminante:** el efecto debe ser **mayor en las células más aneuploides del mismo cultivo**, no uniforme. Si es uniforme, es un efecto trófico inespecífico y el mecanismo propuesto está falsado.

Y la observación que hay que decir en voz alta: si el efecto **sí** es selectivo para las células más aneuploides, esa misma medida es la prueba del mecanismo **y** la prueba de que se está mejorando la supervivencia clonogénica de células genómicamente inestables. Mismo ensayo, dos lecturas opuestas.

---

## FASE 8 — Reproducibilidad y entrega (semana final)

Reservar la semana completa. En un hackathon científico, un repositorio que un juez puede ejecutar es una ventaja competitiva mayor que un modelo adicional.

- Entorno bloqueado (`environment.yml` con versiones fijas)
- Semillas fijas declaradas en `config/`
- Pipeline ejecutable de cero en una máquina limpia con datos de prueba sintéticos
- `docs/EVIDENCE.md` completo, con los `⚠` del brief §11 resueltos en PubMed
- `docs/DECISIONS.md` como bitácora íntegra, **incluidos los resultados negativos**
- Figuras agregadas y no identificables únicamente

---

## ENTREGABLE FINAL

**No** un ranking de fármacos. **No** un dashboard.

Un **dossier de hipótesis única** con:
1. El diagnóstico causal con su mecanismo cuantificado (Track 1)
2. La huella de mosaicismo con su análisis de potencia honesto
3. La medida ortogonal de mtDNA-CN con sus confusores declarados
4. Una hipótesis farmacológica con cadena mecanística completa y hueco declarado
5. El análisis de riesgo oncológico y el perfil PGx del paciente
6. **El experimento de falsación en una frase**
7. Los caminos rechazados y la cita que los mató

Un equipo que entrega una hipótesis bien construida derrota a uno que entrega cincuenta.

---

## PITCH DE 20 SEGUNDOS (versión calibrada)

> Todos los equipos van a llamar variantes. Nosotros miramos las lecturas que los pipelines diagnósticos descartan: el ~1 % que mapea al genoma mitocondrial. De ahí sale el número de copias de ADN mitocondrial de este niño. Las células aneuploides pierden ADN mitocondrial porque el estrés proteotóxico atasca la importación de proteínas a la mitocondria — un mecanismo aguas abajo que podría contribuir a su fallo de medro y su atrofia muscular. Lo calculamos desde su propio WGS, sin un solo experimento nuevo. Y el mismo trabajo que describe la lesión muestra que subir las proteínas de choque térmico la revierte, para lo cual existe un aprobado de 2024 con dosis pediátrica. Ahora bien: subir HSF1 es exactamente lo que la oncología intenta bloquear, y este niño ya tuvo un rabdomiosarcoma. Por eso diseñamos un solo experimento que mide la eficacia y el riesgo con la misma lectura.

## "¿Por qué recordarían los jueces este proyecto 24 horas después?"

Porque será el único que les haya enseñado **un número calculado sobre los datos del paciente** en lugar de un número predicho por un modelo, y el único que haya dicho en voz alta que su propia hipótesis terapéutica empuja en la dirección que la oncología intenta bloquear.

Y porque será el único que haya dicho que la nefrocalcinosis no encaja.
