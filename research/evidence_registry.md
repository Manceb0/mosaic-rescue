# Registro de evidencia — índice, no almacén

> **Lee esto antes de buscar evidencia aquí.** Este fichero fue una plantilla vacía (una fila
> `E001` sin rellenar) durante casi todo el proyecto, mientras `README.md` y `AGENTS.md`
> afirmaban que aquí vivía la evidencia. **Ya no pretende ser el almacén.** La evidencia vive
> en formatos que se pueden validar por máquina, y este fichero dice dónde.

## Por qué no se rellenó esta tabla

Copiar aquí las 80 celdas de `research/track2_evidence.tsv` habría creado una **segunda fuente
de verdad** que se desincroniza en cuanto alguien edita una sola. Ese es exactamente el fallo
que este repositorio ya cometió con los conteos de figuras (26/21 frente a 27/22) y con cinco
experimentos marcados «falta notebook» cuando sí lo tenían. Un registro que hay que mantener a
mano en dos sitios acaba mintiendo en uno de los dos.

La evidencia está, por tanto, en ficheros **parseables y validados por `src/verify.py`**.

## Dónde vive realmente la evidencia

| Artefacto | Qué contiene | Validado por |
|---|---|---|
| [`research/track2_evidence.tsv`](track2_evidence.tsv) | 8 puentes × 10 dimensiones = **80 celdas**. Vocabulario cerrado `DIRECT/NEAR/GENETIC/CONTRADICTORY/ABSENT`. **61 vacías**, 9 `DIRECT`, 5 `NEAR`, 3 `CONTRADICTORY`, 2 `GENETIC`, sobre 4 publicaciones distintas + 2 artefactos internos | `verify.py`: ninguna celda no-`ABSENT` puede quedarse sin fuente |
| [`research/track2_candidates.tsv`](track2_candidates.tsv) | **3 intervenciones y 3 controles**, con evidencia directa, indirecta, contraria, exposición, seguridad y regla de descarte | `verify.py`: roles cerrados y todo lo afirmado lleva identificador |
| [`research/contradictions.md`](contradictions.md) | **13 contradicciones aceptadas** contra nuestras propias ideas preferidas, con su gravedad y la decisión que provocaron | revisión humana |
| [`docs/EVIDENCE.md`](../docs/EVIDENCE.md) | Referencias verificadas en sesión contra PubMed, con nivel `L0`–`L5`, limitación y falsador | revisión humana |
| [`research/agent_findings/`](agent_findings/) | Informes largos de las ramas exploratorias, **incluidas las que murieron** | histórico, no canónico |

## La regla que sí se cumple en todos ellos

`CLAUDE.md`, Regla Dura 5: **ningún PMID ni DOI que no se haya verificado en sesión.** Si no
se tiene, se escribe `no verificado` y se sigue. Un identificador inventado es descalificatorio.

Y Regla Dura 4: cada afirmación lleva su nivel de evidencia. `L0` especulación · `L1`
asociación · `L2` apoyo ortogonal · `L3` funcional · `L4` funcional replicada · `L5`
humana/clínica establecida.

## Si vas a añadir evidencia nueva

1. Va al **TSV** correspondiente, no a esta página.
2. Si contradice algo que ya afirmamos, va **además** a `contradictions.md`.
3. Ejecuta `python src/verify.py`. Si la celda nueva no lleva fuente, falla.
4. Distingue evidencia **del paciente** de evidencia de **sistemas modelo externos**. No
   colapses hallazgos de células tumorales en enfermedad constitucional pediátrica sin decirlo.
5. Para evidencia farmacológica, registra estado de aprobación, mecanismo, relevancia de
   tejido, contexto pediátrico y riesgo conocido.
