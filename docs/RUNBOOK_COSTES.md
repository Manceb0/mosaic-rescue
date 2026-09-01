# Runbook de costes — qué es caro y por qué

> Escrito porque una corrida completa se estaba comiendo la máquina. La RAM es el recurso
> escaso (16 GB) y el disco estaba al 95 %.

## Lo que se midió, antes de tocar nada

| Operación | Antes | Después | Causa |
|---|---|---|---|
| `load()` — cruce VEP↔VCF | **17,0 s** | **0,13 s** | Recorría las 5 M líneas del VCF **en cada llamada**, y lo llaman seis scripts |
| `run_mode_b.py` — 15 análisis | **41,3 s** | **1,6 s** | Resnik+BMA sobre ~7 000 modelos × 8 conjuntos de términos |
| `03_TRACK1_GENOME_WIDE.ipynb` completo | **113 s** | **7 s** | Suma de los dos anteriores, varias veces |
| Exomiser, heap | `-Xmx8g` | `-Xmx4g` | 8 GB de heap en una máquina de 16 GB deja al sistema sin aire |

**16× más rápido el notebook completo, con 6 MB de caché.**

## Cómo funciona la caché, y por qué es segura

Vive en `work/cache/` (gitignored). Dos niveles:

| Caché | Clave |
|---|---|
| `load_*.pkl` | tamaño y fecha de **el TSV anotado**, **el VCF**, `genome_wide.py`, `allele_key.py` y `ranking_v1.yaml` |
| `pheno_*.pkl` | conjunto de términos HPO **+ huella del corpus de modelos** |

**La huella incluye el código, no solo los datos.** Si se cambia la lógica del cruce o la
fórmula congelada, la caché se invalida sola. Sin eso, una caché es una forma silenciosa de
seguir usando un resultado obsoleto — que es peor que no tener caché.

La escritura es atómica (`.tmp` + `os.replace`): nunca queda una caché a medias si se
interrumpe.

Para forzar recálculo:

```bash
rm -rf work/cache
```

## Lo que sigue siendo caro, y no se puede cachear

| Operación | Coste | Cuándo hace falta |
|---|---|---|
| Anotación VEP sobre 4,9 M variantes | horas + 27 GB de caché | Solo si cambia el VCF o la versión de VEP. **No se reejecuta** |
| Exomiser, corrida completa | ~1 min 25 s + 4 GB de RAM | Solo al repetir el baseline |
| Exomiser en modo `FULL` sin filtro de frecuencia | **>10 min, abortada** | **No usar.** Para consultar unas pocas variantes, hacer un **VCF mínimo**: 0,9 s |
| Piloto MitoRead, 2 M lecturas | ~3 min | Solo al repetir el piloto |
| Descarga de datos de Exomiser | 24 GB / 44 min | Una vez |

### El truco del VCF mínimo

Consultar la base de frecuencias de Exomiser para unas pocas variantes **no** requiere
reprocesar el genoma. Se extraen esos registros a un VCF de tres líneas y Exomiser responde en
**0,9 s** en vez de más de diez minutos. Está implementado en
`src/prioritization/freqfix_sensitivity.py`.

## Disco — 25 GB recuperables ahora mismo

Los `.zip` de Exomiser siguen en disco **además** de su contenido ya extraído y verificado:

| Fichero | Tamaño |
|---|---|
| `work/exomiser/2402_hg38.zip` | 22 GB |
| `work/exomiser/2402_phenotype.zip` | 3,0 GB |
| `work/exomiser/exomiser-cli-14.1.0-distribution.zip` | 135 MB |

Son **redundantes**: los datos están extraídos y Exomiser corre contra ellos. Y son
recuperables — `src/baseline/fetch_exomiser.py` los vuelve a descargar (44 min).

**No se borran automáticamente.** Es decisión del dueño del disco:

```bash
rm work/exomiser/*.zip
```

## Reglas para que esto no se vuelva a degradar

1. **Nada que recorra el VCF entero debe llamarse más de una vez por sesión.** Si hace falta,
   va a la caché con huella de entradas y código.
2. **Heap de Java al mínimo que funcione**, nunca al máximo disponible.
3. **Para consultar pocas variantes, VCF mínimo.** Nunca una corrida completa.
4. **Todo lo pesado escribe a `work/`**, que está gitignored.
5. Antes de optimizar, **medir**. Los 17 s de `load()` no eran obvios hasta cronometrarlos.
