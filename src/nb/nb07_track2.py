#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye notebooks/07_TRACK2_SAFE_RESCUE.ipynb."""
from __future__ import annotations
import sys
sys.path.insert(0, ".")
from src.nb.nbutil import SETUP, run                                   # noqa: E402

OUT = "notebooks/07_TRACK2_SAFE_RESCUE.ipynb"

CELLS = [
("md", """# 07. Track 2: el corredor de rescate seguro

> **NO HAY NOMINACIÓN DE FÁRMACO EN ESTE NOTEBOOK, Y ES DELIBERADO.**
>
> Toda la evidencia citada tiene identificador **verificado en el proyecto**. Donde falta
> evidencia se escribe *hueco*, no una cita plausible.

## Pregunta

**¿Existe un mecanismo terapéutico plausible, falsable y seguro para este paciente?**

## La corrección que reorganiza todo

Agrupar la evidencia bajo «proteostasis» metía en la misma caja dos intervenciones con lógica
terapéutica distinta y **consecuencias oncológicas potencialmente opuestas**:

| | T2-A · aguas arriba | T2-B · aguas abajo |
|---|---|---|
| Cadena | La variante desestabilizaría BUBR1; subir su abundancia mejoraría el checkpoint | La célula ya aneuploide sufre estrés; subir HSP la haría tolerarlo mejor |
| Efecto buscado | **menos** células aneuploides nuevas | las que existen **viven mejor** |
| Riesgo | podría reducir CIN | podría aumentar la supervivencia de células inestables |

En un niño que ya tuvo un rabdomiosarcoma, **esa diferencia lo es todo**."""),

("code", SETUP),

("code", 'fl.labels("Inventario", "Lo que un hueco no significa")'),

("md", """## Resultado primario 1 · la matriz de evidencia

Un mapa de cajas y flechas explica **la idea**. No enseña **qué evidencia existe**. Esta matriz
cruza los ocho puentes contra diez dimensiones de evidencia y dice, celda a celda, qué hay.

Se lee de **`research/track2_evidence.tsv`**, un fichero versionado: cada celda es una fila con
su fuente. **No hay ni una caja escrita dentro del código de la figura**, que es exactamente el
defecto que esta pasada venía a corregir: una caja no se puede auditar ni comparar entre
versiones; una fila sí.

Regla dura del fichero: **ninguna celda distinta de `ABSENT` puede quedarse sin fuente**, y el
notebook lo comprueba antes de dibujar."""),

("code", '''TSV = "research/track2_evidence.tsv"
raw = [l.rstrip(chr(10)).split(chr(9)) for l in io.open(TSV, encoding="utf-8")
       if not l.startswith("#") and l.strip()]
HDR, EV = raw[0], [dict(zip(raw[0], r + [""] * (len(raw[0]) - len(r)))) for r in raw[1:]]

DIMS = ["paciente", "mva_humana", "celulas_aneuploides", "otro_contexto",
        "perturbacion_genetica", "perturbacion_farmacologica",
        "abundancia_bubr1", "proteostasis", "cin", "supervivencia_clonogenica"]
BR = sorted({int(e["puente"]) for e in EV})
TIT = {int(e["puente"]): e["titulo"] for e in EV}
RUTA = {int(e["puente"]): e["ruta"] for e in EV}
CELL = {(int(e["puente"]), e["dimension"]): e for e in EV}

# La regla dura, comprobada aqui y no solo escrita en el fichero
huerf = [e for e in EV if e["clase"] != "ABSENT" and not e["fuente"].strip()]
assert not huerf, f"celdas sin fuente: {[(e['puente'], e['dimension']) for e in huerf]}"
assert len(EV) == len(BR) * len(DIMS), f"la matriz no esta completa: {len(EV)} filas"

import collections as _c
cnt = _c.Counter(e["clase"] for e in EV)
print(f"  {TSV}  ·  {len(EV)} celdas = {len(BR)} puentes x {len(DIMS)} dimensiones")
print(f"  toda celda distinta de ABSENT lleva fuente: OK")
print()
for k in ("DIRECT", "GENETIC", "NEAR", "CONTRADICTORY", "ABSENT"):
    print(f"    {k:<16}{cnt.get(k,0):>4}  ({100*cnt.get(k,0)/len(EV):.0f} %)")
print()
fuentes = sorted({e["fuente"] for e in EV if e["fuente"].strip()})
print(f"  fuentes distintas citadas: {len(fuentes)}")
for f in fuentes:
    print(f"    {f}")'''),

("md", """### Figura principal 1 · ocho puentes × diez dimensiones de evidencia"""),

("code", '''from src.figures import fig07_evidence as FE

fig, _st = FE.build(EV)
_n_abs = _st["counts"].get("ABSENT", 0)
_n_dir = _st["counts"].get("DIRECT", 0)
_n_con = _st["counts"].get("CONTRADICTORY", 0)
fl.pub(fig, "Figura principal 1 · matriz de evidencia curada de Track 2",
       "EXP-016 · EXP-016b", "EXTERNAL", "CURATED_EVIDENCE",
       f"que evidencia existe de verdad para cada puente. De las {len(EV)} celdas, "
       f"{_n_abs} estan vacias, {_n_dir} tienen evidencia del tipo exacto que el puente "
       f"necesita y {_n_con} apuntan EN CONTRA, sobre {len(_st['sources'])} fuentes "
       f"distintas. La fila 8 esta vacia en las diez dimensiones, que es el hueco de seguridad, y "
       f"la fila 1, la unica que conecta con este paciente, solo tiene una celda no vacia y "
       f"es NEAR, no DIRECT. El puente 7 es el hueco TRASLACIONAL.",
       "que Track 2 sea valido ni invalido. Es un inventario de evidencia curada (literatura "
       "externa mas evidencia del proyecto), no observaciones experimentales del paciente, y "
       "por eso no se etiqueta simplemente DATA. Una celda ABSENT dice que nadie lo ha "
       "medido, no que sea falso. Y NO se calcula ninguna puntuacion global: combinar "
       "evidencia heterogenea en un numero exigiria un metodo preregistrado que no existe.",
       source="research/track2_evidence.tsv · 80 celdas versionadas, cada una con fuente",
       lib="matplotlib", slug="fig07_track2_evidence_matrix")'''),

("md", """## Resultado primario 2 · los ocho puentes, como mapa

Toda afirmación declara **qué puente sostiene**. La evidencia de un puente **no vale** para
otro."""),

("code", '''BRIDGES = [
 (1, "variante de ESTE paciente\\n-> inestabilidad de BUBR1", "T2-A", "hueco",
     "solo inferencia estructural y conservacion"),
 (2, "inestabilidad -> menos proteina", "T2-A", "ok",
     "niveles bajos en pacientes, incluso con missense, pero de otros alelos"),
 (3, "subir chaperonas -> SUBIR BUBR1", "T2-A", "contra",
     "la evidencia va en direccion CONTRARIA: inhibir HSP90 lo hunde"),
 (4, "mas BUBR1 -> menos CIN", "T2-A", "ok",
     "gradiente 8,5-77 %; aneuploidia clara < ~50 % (DOI 10.1007/s00439-008-0572-y)"),
 (5, "aneuploidia -> estres proteotoxico", "T2-B", "ok",
     "p62 con precursores mitocondriales, ADNmt bajo (DOI 10.1038/s41467-025-60857-4)"),
 (6, "subir HSP (GENETICO) -> rescate", "T2-B", "parcial",
     "rescata, PERO el efecto dependio del cariotipo: una linea no respondio"),
 (7, "coinduccion FARMACOLOGICA\\n-> el mismo rescate", "T2-B", "contra",
     "cero evidencia directa; contraejemplo verificado (PMID 34481829)"),
 (8, "la intervencion -> efecto sobre CIN\\ny supervivencia clonogenica", "ambas", "vacio",
     "NUNCA MEDIDO en ninguna direccion"),
]
COL = {"ok": fl.ALIVE, "parcial": fl.OPEN, "hueco": fl.DEAD, "contra": fl.DEAD,
       "vacio": fl.VOID}
for n, t, r, st, note in BRIDGES:
    print(f"  {n}. [{r:<6}] {st.upper():<8} {t.splitlines()[0]:<44} {note[:52]}")'''),

("code", '''fl.svg("figures/fig10_track2_bridges.svg",
       "Figura principal 2 · los ocho puentes y el corredor",
       "EXP-016", "EXTERNAL+DERIVED", "SYNTHESIS",
       "en rojo los puentes rotos, en morado el que nunca se midio. El panel B situa las dos "
       "rutas en el plano beneficio/riesgo: T2-A puede caer en el corredor; T2-B, por "
       "construccion, empuja hacia el eje de riesgo.",
       "que T2-B este muerta ni que T2-A funcione. Ningun puente roto se ha cerrado como "
       "NEGATIVE: estan UNRESOLVED, que es distinto.",
       generator="src/make_fig10.py")'''),

("md", """## Resultado primario 3 · el puente 7, que es el corazón falsable

Búsqueda acotada con clasificación fijada de antemano:

| Clase | Encontrado |
|---|---|
| `DIRECT`: células aneuploides, coinductor y rescate | Ninguna |
| `NEAR`: coinducción en otro contexto proteotóxico | Sí, pero **no se admite como sustituto** |
| `GENETIC`: solo sobreexpresión | Sí, y es toda la evidencia del puente 6 |
| **CONTRADICTORY** | **Dos, verificadas** |

**El contraejemplo (PMID 34481829).** En fibroblastos NPC1, la sobreexpresión de HSP70 redujo
el almacenamiento de colesterol; el coinductor **no lo reprodujo** hasta 500 µM, y el detalle
que más pesa: **no llegó a inducir HSP70**.

**La tensión (PMID 25205676).** En aneuploides humanos la inducción de la respuesta de choque
térmico está **al 50–60 %** del control. Lo que rescató fue **HSF1 constitutivamente activo**."""),

("md", """> **Formulación congelada:**
>
> *HSF1 impairment makes the pathway both mechanistically relevant and pharmacologically
> uncertain. Genetic augmentation can bypass the deficit; whether a stress-dependent
> pharmacological co-inducer can amplify the impaired endogenous response sufficiently
> remains unresolved.*"""),

("md", """## Robustez · «Try to Kill It», y por qué es la mejor diapositiva

**La señal de eficacia y la señal de riesgo oncológico son la misma medición.**

Si una intervención rescata preferentemente a las células **más** aneuploides, eso es a la vez
la prueba de que el mecanismo es el propuesto **y** la prueba de que se está mejorando la
supervivencia clonogénica de células genómicamente inestables."""),

("md", """## Evidencia contradictoria, declarada

| Afirmación | Contraevidencia |
|---|---|
| Subir HSP es terapéutico | Un coinductor **no fue efectivo** en ELA |
| Genético ≈ farmacológico | **PMID 34481829**: el genético rescató, el farmacológico no, y no indujo HSP70 |
| El rescate genético es universal | Dependió del **cariotipo**; una línea aneuploide no respondió |
| Ayudar a la célula aneuploide es bueno | **Es la definición oncológica de un paso temprano de tumorigénesis** |

## Decisión

| | |
|---|---|
| **Clase superviviente principal** | Modulación de proteostasis y chaperonas, entre las seis evaluadas |
| **T2-A, aguas arriba** | `UNRESOLVED`, bloqueada por los puentes 1 y 3 |
| **T2-B, aguas abajo** | `UNRESOLVED`, bloqueada por los puentes 7 y 8 |
| **Nominación de fármaco** | **NINGUNA** |
| Proteasoma · poda clonal | **NEGATIVE** |
| Estabilización por acetilación · senolíticos | **PARKED** |

**La compuerta del fármaco exige las cinco:** estatus aprobado · proximidad mecanística a un
puente nombrado · evidencia **de ese** puente · predicción de rescate falsable · contra-test
explícito de CIN/tumor. **Hoy ninguna candidata las reúne.**

### Qué NO demuestra este notebook

Que la clase sea la correcta · que exista un fármaco que sirva · que rescatar sea seguro. Y
tampoco que se haya barrido el espacio terapéutico completo: se evaluaron **seis clases
elegidas desde la cadena mecanística del caso**.

### Falsificador

El experimento de arriba, con sus cuatro desenlaces preescritos. Dos de los cuatro **matan la
hipótesis**, y eso es lo que la hace falsable.

### Next Best Experiment

Par isogénico aneuploide/euploide ± coinductor candidato, con **control positivo genético**
(HSF1 constitutivamente activo) y **lectura obligatoria de si el fármaco induce HSP**, porque
el contraejemplo enseña que puede **no** inducir, y sin medirlo no se sabe si falló el fármaco
o la hipótesis. Midiendo a la vez CIN y supervivencia clonogénica."""),
]

if __name__ == "__main__":
    run(OUT, CELLS, min_sci=1)
