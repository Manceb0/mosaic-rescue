# Auditoría de la cabecera del VCF — Fase 0.2

> Predicciones escritas **antes** de abrir el fichero: `docs/DECISIONS.md`, sección
> «Preregistro — Fase 0.2». Resultado: **cinco aciertos y un fallo**, y el fallo resultó
> ser menos valioso de lo que parecía en el primer vistazo.
>
> **Saneado:** el nombre de muestra no se leyó ni se imprime. El script lo redacta por
> defecto (Regla Dura 1).

## Lo esencial

| | |
|---|---|
| Formato | VCFv4.2, 2617 líneas de metadatos |
| Build | **GRCh38**, confirmado por longitud de `chr1` = 248 956 422 |
| Referencia | `GRCh38_no_alt_analysis_set_plus_hs38d1`, exclusiones GRC enmascaradas |
| Contigs | **2580, sin prefijo `chr`** |
| Caller | **Sentieon Haplotyper v202308.02** (reimplementación de GATK HaplotypeCaller) |
| Ruta | Haplotyper → gVCF → GVCFtyper → VariantFiltration |
| Muestras | 1 |
| Anotación previa | **Ninguna.** VCF crudo |
| Tipo | VCF de variantes (no gVCF) |
| Variantes | **5 012 204** — recuento normal para WGS de muestra única en GRCh38 |

## Contraste con lo preregistrado

| # | Predicho | Real | |
|---|---|---|---|
| 1 | GRCh38 | GRCh38 | ✅ |
| 2 | Una muestra | Una | ✅ |
| 3 | Sin anotación | Sin anotación | ✅ |
| 4 | `GT` `AD` `DP` `GQ` `PL` | Los cinco | ✅ |
| 5 | **Sin fase física** | **`PGT` y `PID` presentes** | ❌ |
| 6 | No gVCF | No gVCF | ✅ |

---

## El fallo de la predicción 5, y por qué casi no cambia nada

`PGT`/`PID` existen. En el primer vistazo eso parecía levantar el techo del
`unphased ≠ trans`. **Se midió el alcance real, y no lo levanta.**

```
variantes con PID    770 458   (15,37 %)
bloques de fase      337 422

variantes por bloque   mediana 2 · p90 3 · p99 8 · máx 54
envergadura (pb)       mediana 7 · p75 17 · p90 29 · p99 91 · MÁXIMO 288

bloques ≥ 300 pb     0   (0,00 %)
```

**El bloque más largo del genoma entero mide 288 pb.** La mediana, 7 pb.

`PGT`/`PID` es *read-backed phasing*: solo enlaza variantes que el caller pudo colocar
sobre el mismo haplotipo ensamblado, y el límite físico es la longitud del fragmento. Con
reads de 149 bp, el alcance observado (máx 288 pb) encaja con fragmentos de ~300 pb — lo
que **valida de forma cruzada** la estimación de insertos del QC de L001.

Para heterocigosis compuesta esto es, en la práctica, inservible. `BUB1B` mide ~65 kb: el
bloque máximo cubre el **0,44 %** del gen. Dos variantes patogénicas en el mismo gen caerán
en bloques `PID` distintos salvo que estén a menos de 288 pb una de otra, y entre bloques
**no hay relación de fase**.

> **Conclusión.** El techo declarado en `docs/03_ALPHAGENOME_ASSESSMENT.md` §4.2 sigue en
> pie prácticamente intacto. La predicción falló en la letra —los campos están— y acertó
> en el fondo: **sin genotipos parentales, la fase sigue sin resolverse.**

### Para qué sí sirve

Un uso real y estrecho: **corrección de variantes multinucleotídicas (MNV)**. Dos SNV
adyacentes dentro del mismo codón producen un aminoácido distinto según estén en cis o en
trans, y una anotación que las trate por separado da el cambio equivocado. Con mediana de
7 pb, `PID` cubre exactamente ese caso.

No es el hallazgo espectacular. Es un detalle de anotación que, si se ignora, produce una
consecuencia proteica errónea sobre un candidato — y eso sí puede costar caro.

---

## Consecuencias operativas

### 1. Sin prefijo `chr` — riesgo de fallo silencioso

Todo BED, lista de regiones o coordenada del proyecto usa `1`, no `chr1`. Un desajuste de
estilo **no da error**: devuelve cero resultados, que se lee como «no hay nada aquí».
Verificar el estilo antes de cada intersección.

### 2. Filtrado duro, no VQSR — el segundo alelo puede estar filtrado

`VariantFiltration` con los umbrales estándar de GATK:

| Filtro | Umbral |
|---|---|
| `QD2` | QD < 2.0 |
| `MQ40` | MQ < 40.0 |
| `FS60` | FS > 60.0 |
| `MQRankSum-12.5` | MQRankSum < −12.5 |
| `RPRS-8` | ReadPosRankSum < −8.0 |
| `LowQual` | baja calidad |

Es lo correcto para una muestra única, pero el filtrado duro es más romo que VQSR.

> **Regla para la caza del segundo alelo: no restringir a `PASS`.** Si hay un alelo
> huérfano, su pareja puede estar en el conjunto filtrado. Revisar los `FILTER` no-PASS en
> la región del gen candidato antes de declarar que el segundo alelo no aparece.

### 3. Anotación desde cero

`INFO` trae solo métricas del caller: `AC AF AN BaseQRankSum ClippingRankSum DB DP
ExcessHet FS InbreedingCoeff MLEAC MLEAF MQ MQRankSum QD ReadPosRankSum SOR`.

Sin frecuencias poblacionales, sin términos de consecuencia, sin ClinVar. La Fase 2.2
empieza de cero: hay que anotar nosotros.

`ExcessHet` e `InbreedingCoeff` son métricas de cohorte y **no significan nada con una
muestra única**. Ignorarlas; no usarlas como criterio de calidad.

### 4. `AD` presente — la rama de mosaicismo se sostiene

`AD` permite balance alélico por variante, que es lo que sostiene tanto la evaluación de
heterocigosis compuesta como la huella de mosaicismo. Era la predicción cuyo fallo habría
hecho más daño, y se cumplió.

---

## Qué se puede activar ya

Con build, caller, `AD` y una sola muestra confirmados, las tres rutas de búsqueda están
desbloqueadas y no dependen de nada más:

| Ruta | Panel |
|---|---|
| **MVA causal** | `config/panels/mva.txt` |
| **Renal / tubulopatía** | `config/panels/nephrocalcinosis.txt` |
| **Segundo alelo oculto** | Se activa solo si aparece un alelo huérfano |

Reproducible con `src/vcf_header_audit.py` y `src/phasing_span_stats.py`. Ninguno de los
dos imprime coordenadas, genotipos ni secuencia.
