# EXP-020 · `FANCD2` — auditoría rápida de la hipótesis competidora

> **`DERIVED`** — todo lo de aquí sale de la anotación local y de la salida de Exomiser.
> Ninguna consulta externa.
>
> **Origen ejecutable:** `src/prioritization/genome_wide.py` (`load`) sobre el TSV anotado.

## Por qué se auditó

El baseline externo (EXP-006b) situó `FANCD2` en el **puesto 4**, modelo recesivo. El
preregistro dice que un gen del top-10 externo que nosotros no habíamos mirado **entra en el
camino crítico**, gane quien gane. Y `FANCD2` no es un gen cualquiera aquí: es la vía de
anemia de Fanconi —inestabilidad cromosómica, fallo de medro, predisposición tumoral—, que
solapa con MVA en fenotipo **y** en mecanismo. Descartarlo por incómodo habría sido el sesgo
que el baseline existe para detectar.

**Regla aplicada: falsificación barata primero.** Una auditoría completa solo si sobrevive.

## Resultado: **NEGATIVE**, por cuatro vías independientes

### 1 · Frecuencia poblacional — el filtro que lo mata

| Alelo | Consecuencia | `MAX_AF` |
|---|---|---|
| 1 | missense | **0,478** |
| 2 | splice donor | **0,472** |
| 3 | splice donor, 5.ª base | **0,471** |

**Los tres son polimorfismos comunes, al ~47 % de frecuencia poblacional.** No son alelos de
enfermedad rara.

### 2 · Configuración de herencia — no hay ninguna

Los tres son **heterocigotos** (`0/1`). No hay homocigoto ni pareja en *trans*. Para una
enfermedad autosómica recesiva, **no existe configuración causal posible** con estos alelos.

### 3 · Profundidad — compatible con colapso de parálogo

| | DP | Frente a la mediana |
|---|---|---|
| Mediana del conjunto | 44× | — |
| `FANCD2`, tres alelos | 89–102× | **2,0–2,3×** |

`FANCD2` tiene pseudogenes conocidos. Una profundidad del doble de la mediana es **compatible
con** lecturas de parálogo colapsando sobre el locus. **No lo demuestra** —haría falta
inspeccionar mapeo y calidad de alineamiento—, pero concuerda con las otras tres señales.

### 4 · Por qué Exomiser lo puso #4, y qué enseña

Exomiser dejó `MAX_FREQ` **vacío** en las cuatro variantes, así que pasaron su filtro de
frecuencia como si fueran raras. Nuestra anotación VEP/gnomAD **sí tiene el dato**: ~0,47.

> **Las dos bases de frecuencia discrepan, y aquí la nuestra es la que tiene el dato.** Es el
> reverso exacto del valor del baseline: sirvió para destapar candidatos que no habíamos
> mirado, y a cambio nosotros corregimos un candidato que él no pudo filtrar. **Ninguno de los
> dos motores es el bueno; se comprueban mutuamente.**

## Cierre

| | |
|---|---|
| **Estado** | **NEGATIVE** |
| Qué reduce | La única hipótesis competidora mecanísticamente plausible que produjo el baseline externo |
| Qué NO afirma | Que `FANCD2` esté descartado como gen; que las variantes sean artefactos demostrados. Lo demostrado es que **estos alelos concretos, con estas frecuencias y esta configuración, no pueden causar una enfermedad recesiva en este paciente** |
| Qué lo reabriría | Un alelo raro de `FANCD2` que hoy no vemos: variante estructural, intrónica profunda o mal mapeada. Eso depende de EXP-012, bloqueado por falta de BAM/CRAM |
| Coste | Una pasada de filtros. Ninguna consulta externa |

## Nivel de evidencia

`L2` — la frecuencia poblacional es evidencia externa establecida; la configuración de
herencia es medición directa sobre el VCF.
