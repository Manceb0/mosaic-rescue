#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye notebooks/04_HIDDEN_SECOND_ALLELE.ipynb."""
from __future__ import annotations
import sys
sys.path.insert(0, ".")
from src.nb.nbutil import SETUP, run                                   # noqa: E402

OUT = "notebooks/04_HIDDEN_SECOND_ALLELE.ipynb"

CELLS = [
("md", """# 04 · El segundo alelo ausente

> **Saneado:** sin coordenadas ni identidad de variantes. El locus se describe por tamaño y
> por posición relativa.

## Pregunta biológica

Si el análisis estándar encuentra **un solo** alelo claramente patogénico en un gen de MVA, el
segundo puede ser una variante **reguladora**, **intrónica profunda** o **estructural**.

**¿Existe un segundo alelo que nuestro pipeline codificante no ve?**

## Hipótesis y preregistro

`docs/DECISIONS.md` § *Hidden Second Allele*. Ventana: cuerpo del gen ± ~100 kb, porque **hay
precedente humano publicado** de un segundo alelo regulador decenas de kb aguas arriba;
restringirse al cuerpo del gen sería conceptualmente incorrecto.

Orden de matanza, del filtro barato al caro:
frecuencia poblacional, calidad de la llamada, posición funcional, conservación y
señal reguladora, y por último AlphaGenome

**La predicción #4 decía que AlphaGenome daría Δ plano, y se escribió queriendo fallarla**,
para que un negativo fuera reportable en vez de decepcionante."""),

("code", SETUP),

("code", 'fl.labels("Que se observa", "Alcance del resultado")'),

("md", """## Método · el funnel del locus"""),

("code", '''LOCUS = [
    ("variantes en el locus ampliado (~270 kb)", 321),
    ("tras filtro de frecuencia poblacional",     4),
    ("raras y de calidad, posicion funcional",    1),
    ("enviadas a AlphaGenome",                    1),
    ("con delta relevante",                       0),
]
for n, v in LOCUS:
    print(f"  {n:<44}{v:>6}")
print()
print("  La prediccion #1 fallo por lo alto: se esperaban 800-2000 variantes y hubo 321.")
print("  Se registra como fallo de calibracion de la prediccion, no como resultado.")'''),

("code", '''fig, ax = plt.subplots(figsize=(9.0, 3.6))
names = [s[0] for s in LOCUS][::-1]
vals = [s[1] for s in LOCUS][::-1]
mx = max(vals)
cols = [fl.DEAD if v == 0 else fl.FLOW for v in vals]
ax.barh(range(len(names)), [max(v, 0.6) for v in vals], color=cols, alpha=0.85, height=0.6)
ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=9)
ax.set_xscale("symlog"); ax.set_xlabel("variantes (escala log)")
for i, v in enumerate(vals):
    ax.text(max(v, 0.6) * 1.25, i, str(v), va="center", fontsize=9.4, fontweight="bold",
            color=fl.DEAD if v == 0 else fl.INK)
ax.set_title("Funnel del locus ampliado de BUB1B")

fl.done(fig, "Figura principal 1 · el funnel del locus", "EXP-008", "MEASURED+DERIVED",
        "DATA",
        "de 321 variantes en 270 kb, una sola sobrevivio a frecuencia, calidad y posicion "
        "funcional: una intronica profunda ausente de gnomAD, sin rsID, PASS, heterocigota, "
        "a mas de 1 kb del borde de exon mas cercano.",
        "que no exista un segundo alelo. Este funnel solo cubre SNV e indel dentro de la "
        "ventana: no ve variantes estructurales, que son EXP-012 y estan bloqueadas.",
        prov="docs/DECISIONS.md § Hidden Second Allele")'''),

("md", """## Resultado primario · AlphaGenome sobre el único candidato

Las pistas que se dibujan **se congelaron antes** de repetir la llamada, para que no se
pudieran elegir las más favorecedoras después de verlas. Y las reglas de dibujo también: REF y
ALT comparten escala Y, y el Δ va en su propio carril con el cero visible.

**Fue la única transmisión de un dato del paciente fuera de la máquina en todo el proyecto**,
prevista en `docs/03_ALPHAGENOME_ASSESSMENT.md` §7. Se envió la shortlist, nunca el VCF."""),

("code", '''import glob
AG = glob.glob("work/alphagenome/chr*_A_G.json")[0]      # ruta no impresa: lleva coordenada
ag = json.load(io.open(AG, encoding="utf-8"))
mods = ag["modalities"]
print(f"  estado de la llamada: {ag.get('status')}  ·  ventana: {ag.get('window_bp'):,} pb")
print()
print(f"  {'modalidad':<22}{'pistas':>8}{'delta rel %':>14}{'delta local max':>18}")
for m in sorted(mods, key=lambda x: -abs(x["delta_rel"])):
    print(f"  {m['modalidad']:<22}{m['pistas']:>8}{m['delta_rel']:>14.3f}"
          f"{m['delta_local_max']:>18.4f}")
peor = max(abs(m["delta_rel"]) for m in mods)
spl = [m for m in mods if "splic" in m["modalidad"]]
print()
print(f"  mayor delta relativo de cualquier modalidad : {peor:.2f} %")
if spl:
    print(f"  delta LOCAL de junciones de splicing        : "
          f"{min(m['delta_local_max'] for m in spl):.4f}")'''),

("md", """### Figura principal 2 · navegador REF / ALT / Δ, pista a pista

La figura resumen agrega por modalidad. Esta **no agrega nada**: dibuja las nueve pistas
congeladas tal y como salieron del modelo, sobre un **eje genómico compartido**, con el modelo
del gen encima.

Dos reglas de dibujo, fijadas antes de mirar:

1. **REF y ALT comparten escala Y exacta** dentro de cada pista. Sin esto, cualquier diferencia
   puede fabricarse reescalando.
2. **El Δ va en su propio carril con el cero visible** y escala simétrica. Nunca superpuesto.

> El eje X es **desplazamiento respecto a la variante**, no coordenada absoluta."""),

("code", '''AR = glob.glob("work/alphagenome/arrays_*.json")[0]
ar = json.load(io.open(AR, encoding="utf-8"))
TRK = ar["tracks"]
VPOS = ar["pos"]
FL = ar["flank_bp"]
print(f"  estado: {ar['status']}  ·  ventana: +/-{FL:,} pb  ·  pistas congeladas: {len(TRK)}")
for t in TRK:
    print(f"    {t['mod']:<20}{t['bp_per_bin']:>8.0f} pb/bin  {len(t['ref']):>6} bins   "
          f"{str(t['meta'])[:52]}")

from src.structure.transcript_model import fetch as fetch_tx
TX = fetch_tx()
EXW = [(e["start"] - VPOS, e["end"] - VPOS) for e in TX["exons"]
       if e["end"] > VPOS - FL and e["start"] < VPOS + FL]
print(f"  exones de {TX['transcript']} dentro de la ventana: {len(EXW)}")'''),

("code", '''from src.figures import fig04_tracks as FT

_figs, _ar = FT.load_and_build()
for _which, _slug, _tag in (("main", "fig04_alphagenome_rna_splicing", "principal 2"),
                            ("supp", "fig04S_alphagenome_accessibility_tf", "suplementaria 2S")):
    _f, _st = _figs[_which]
    fl.pub(_f, f"Figura {_tag}. Navegador REF / ALT / delta: {FT.GROUPS[_which]['title']}",
           "EXP-009", "PREDICTED", "MODEL_OUTPUT",
           f"{_st['n_tracks']} de las nueve pistas congeladas sobre el mismo eje genomico, "
           f"con el modelo del gen encima. REF y ALT comparten escala Y exacta dentro de "
           f"cada pista y el delta va en su propio carril con el cero visible. El mayor "
           f"|delta| de cualquier bin aqui es {_st['max_abs_delta']:.4g}.",
           "que no exista un segundo alelo. Es una PREDICCION de un modelo sobre UN "
           "candidato SNV/indel, no una medida y no un barrido. Estas pistas NO son datos "
           "medidos del paciente ni de ningun tejido suyo.",
           source="work/alphagenome/arrays_*.json · pistas congeladas antes de repetir la "
                  "llamada; el reparto entre figura y suplemento es por MODALIDAD",
           lib="matplotlib", slug=_slug)'''),

("md", """### La figura resumen, que fue la que cerró la rama"""),

("md", """### Control de robustez · se revisaron las pistas individuales

Para descartar que un efecto específico de tejido se estuviera diluyendo en el agregado:

- **El top por cambio relativo es ruido.** Las líneas base locales son ~0,0001–0,005; un 5 %
  sobre cero es división por un número minúsculo.
- **El top por cambio absoluto** son pistas de CTCF y RAD21, con cambios del 1,2–2,3 % sobre
  líneas base de 1 400–7 900. Nada funcionalmente interpretable.
- **Sin coherencia biológica**: los tejidos del top son un surtido disperso. No hay señal renal
  ni hematopoyética."""),

("code", '''TR = glob.glob("work/alphagenome/chr*_tracks.json")[0]
tr = json.load(io.open(TR, encoding="utf-8"))
top = [t for t in tr.get("top_rel", []) if t.get("rloc")]
if top:
    fig, ax = plt.subplots(figsize=(9.4, 3.8))
    rels = [abs(t["rel"]) * 100 for t in top]
    bases = [t["rloc"] for t in top]
    ax.scatter(bases, rels, s=60, c=[fl.DEAD if b < 0.01 else fl.FLOW for b in bases],
               alpha=0.85)
    ax.set_xscale("log"); ax.set_xlabel("linea base local de la pista (escala log)")
    ax.set_ylabel("|cambio relativo| %")
    ax.axvline(0.01, color=fl.DEAD, ls="--", lw=1.2)
    ax.text(0.0105, max(rels) * 0.85, "por debajo de este umbral,\\nun % alto es division\\npor "
            "un numero minusculo", fontsize=7.6, color=fl.DEAD)
    ax.set_title("Robustez · por que el top por cambio relativo es ruido")
    fl.done(fig, "Figura de robustez · el % relativo enganya cuando la base es cero",
            "EXP-009", "PREDICTED", "MODEL_OUTPUT",
            "cada punto es una de las pistas con mayor cambio relativo. Las que producen "
            "porcentajes grandes tienen lineas base proximas a cero: el porcentaje es un "
            "artefacto de la division, no senal.",
            "que no exista efecto en ningun tejido. Es un argumento sobre la METRICA, no una "
            "busqueda exhaustiva por tejido.",
            prov="work/alphagenome/*_tracks.json")
else:
    print("  sin pistas individuales en el fichero; el argumento queda en el texto")'''),

("md", """## Decisión

| Rama | Estado |
|---|---|
| **Segundo alelo SNV/indel regulador** | **NEGATIVE** en el alcance evaluado |
| **Segundo alelo estructural (SV/CNV)** | **BLOCKED**, falta BAM/CRAM de profundidad completa |

**La formulación exacta:** *No candidate survived population filtering plus global and
track-level AlphaGenome interrogation.*

**No:** «AlphaGenome demostró que no existe un segundo alelo».

### Sobre la CNV grande

Desde la profundidad y la heterocigosidad del VCF: la región no muestra pérdida de
heterocigosidad ni caída de profundidad, se observa lo contrario. Pero **la profundidad del
VCF no está normalizada para llamar número de copia**, así que lo defendible es *no evidence
for a large heterozygous deletion*, no «CNV descartada».

**Sigue sin resolverse:** CNV pequeñas que quepan entre variantes, eventos equilibrados que no
cambian número de copia, inserciones, y todo lo local a un punto de rotura.

### Falsificador

Con el BAM/CRAM de los cuatro carriles se llamarían variantes estructurales usando pares
discordantes y *split reads*.
**Prohibido cerrar un negativo estructural con L001**: un carril a ~13× es piloto, no ausencia.

### Siguiente experimento

`05_RESIDUAL_PHENOTYPE`. Si el segundo alelo no aparece, ¿y si parte del fenotipo no es de
`BUB1B`?"""),
]

if __name__ == "__main__":
    run(OUT, CELLS, min_sci=1)
