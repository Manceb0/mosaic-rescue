# EXP-017 · Fenotipo renal residual — ¿exige la nefrocalcinosis un segundo diagnóstico?

> **`DERIVED`** — barrido del panel renal sobre la anotación local, con el cruce de alelos
> ya corregido. Ninguna consulta externa.
>
> **Origen ejecutable:** `src/prioritization/genome_wide.py` sobre `config/panels/nephrocalcinosis.txt`.

## Por qué esta rama no se cerraba antes

El documento clínico dice **«nefrocalcinosis presente desde el nacimiento»**. La
nefrocalcinosis del prematuro es adquirida y postnatal —furosemida, nutrición parenteral,
carga de calcio— y tarda semanas. Si está al nacer, es antenatal, y eso **invierte el prior**
hacia una causa genética (brief §8.1).

Además el modo B añadió señal: la nefrocalcinosis **aporta poco soporte semántico** al modelo
MVA anotado. Un rasgo que el diagnóstico principal no explica bien es exactamente donde vive
un diagnóstico mixto.

Tasa base: los diagnósticos duales ocurren en el 2–7,5 % de los casos diagnosticados.

## Qué se hizo

Barrido del panel de 28 genes —Bartter antenatal, acidosis tubular renal distal,
hipercalciuria/Dent— **con el cruce de alelos corregido**, que era la razón real para
repetirlo: la corrección recuperó 420 posiciones y podía haber destapado un alelo renal que
antes se perdía.

**Comprobación explícita de `MAGED2`**, como el propio panel exige: es X-ligado recesivo y en
un varón basta **una** variante hemicigota. Un filtro «bialélico» la perdería.

## Resultado: **NEGATIVE** en el barrido codificante

| | |
|---|---|
| Genes del panel | 28 |
| Alelos HIGH/MODERATE encontrados | 23 |
| **Alelos raros al umbral del propio panel (AF < 0,005)** | **0** |
| Variantes de `MAGED2`, cualquier impacto | **0** |

El alelo **más raro de todo el panel** está al **1 %**. El resto son polimorfismos comunes:
varios por encima del 50 %, y cinco cerca del 100 % —alelos donde la referencia es el minoritario—.

Las dos `start_lost` de alto impacto que en su día llamaron la atención resultan estar al
**51 %** y **81 %** de frecuencia poblacional.

## Lo que esto cierra, y lo que NO

**Cierra:** la hipótesis de una tubulopatía mendeliana **codificante** detectable con este
panel. Con el cruce corregido y el umbral del propio panel, no hay candidato.

**NO cierra la pregunta clínica.** La nefrocalcinosis congénita **sigue sin explicación
mecanística propia**. Quedan abiertas tres salidas, y ninguna se resuelve desde este VCF:

| Salida | Cómo se resolvería |
|---|---|
| Es parte de la «disfunción renal» de MVA (12,9 % de la serie) | Literatura — EXP-019 |
| Causa no codificante, reguladora o estructural | Depende de EXP-012, **bloqueado** por falta de BAM/CRAM |
| Causa antenatal adquirida | **Una línea de la historia obstétrica** |

> **La pregunta que decide sigue sin contestar: ¿hubo polihidramnios u oligohidramnios?**
> El Bartter antenatal produce **poli**hidramnios severo desde la semana 18–22; la MVA se
> asocia a **oligo**hidramnios. Son opuestos. Es la pregunta de mayor valor por unidad de
> esfuerzo de todo el proyecto y **es un email**.
>
> Y hay falsación gratis, ya en la historia clínica: alcalosis metabólica hipopotasémica e
> hipoclorémica, renina y aldosterona elevadas, cociente calcio/creatinina urinario alto.
> Si son normales, la hipótesis muere sin gastar un core-hora.

## Cierre

| | |
|---|---|
| **Estado del barrido codificante** | **NEGATIVE** |
| **Estado de la pregunta fenotípica** | **ABIERTA · BLOQUEADA por datos clínicos** |
| Incertidumbre reducida | Que existiera un segundo diagnóstico mendeliano codificante evidente que estuviéramos pasando por alto |
| Qué NO reduce | Por qué este niño tiene nefrocalcinosis desde el nacimiento |
| Qué lo reabriría | Respuesta de polihidramnios, electrolitos/renina/aldosterona, o BAM/CRAM que permitan buscar SV y reguladoras |

## Nivel de evidencia

`L2` — frecuencias poblacionales externas sobre medición directa del VCF. El negativo es del
**alcance evaluado**, no de la hipótesis clínica.
