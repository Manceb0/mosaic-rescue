#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye notebooks/06_MOSAIC_AND_MITOREAD.ipynb."""
from __future__ import annotations
import sys
sys.path.insert(0, ".")
from src.nb.nbutil import SETUP, run                                   # noqa: E402

OUT = "notebooks/06_MOSAIC_AND_MITOREAD.ipynb"

CELLS = [
("md", """# 06 · Mosaicismo y MitoRead

> **Este notebook tiene dos partes y NO se mezclan.**
>
> | Parte | Qué es |
> |---|---|
> | **A · simulación** | `SIMULATED`. **Ningún dato del paciente.** Cómputo puro |
> | **B · MitoRead** | `DERIVED`. Un **prototipo técnico**, no una medida del paciente |
>
> Confundirlas sería exactamente el error que el brief prohíbe: presentar una medida derivada
> de cobertura como si fuera un ensayo funcional."""),

("code", SETUP),

("md", """# Parte A · La cancelación de BAF

## Pregunta biológica

MVA es **variegada**: cada linaje gana o pierde cromosomas de forma independiente. Los métodos
estándar de mosaicismo asumen **clonalidad** — una célula ancestral, un solo homólogo.

**¿Qué le pasa a la señal cuando ese supuesto se rompe?**

## Hipótesis y preregistro

`docs/DECISIONS.md` § EXP-015a, escrito **antes** de implementar. Cuatro predicciones con su
regla de decisión. La #3 era la que decidía: si el índice de dispersión no conserva potencia
donde el BAF se cancela, **no aporta nada y se abandona**.

El álgebra que se pone a prueba:

```
CLONAL      todas las celulas ganan el MISMO homologo
            BAF = 1/(2+f) ~ 0,5 - f/4        senal
VARIEGADO   cada linaje gana uno al azar
            BAF = 0,5 EXACTO                 cancelacion completa
            cobertura = 2 + f                SOBREVIVE
```"""),

("code", '''sim = json.load(io.open("work/mosaic/dispersion_simulation.json", encoding="utf-8"))
print(f"  semilla {sim['seed']} · {sim['n_rep']} repeticiones · profundidad {sim['depth']}x"
      f" · FPR fijada {sim['alpha']}")
print()
print(f"  {'escenario':<14}{'fraccion':>10}{'potencia BAF':>15}{'potencia DISPERSION':>22}")
for r in sim["results"]:
    print(f"  {r['mode']:<14}{r['fraction']*100:>9.0f}%{r['power_baf']:>15.3f}"
          f"{r['power_dispersion']:>22.3f}")'''),

("md", """### Figura principal · el modo de fallo, reproducido"""),

("code", '''fl.svg("figures/fig9_mosaic_sim.svg",
       "Figura principal A · la cancelacion de BAF en simulacion",
       "EXP-015a", "SIMULATED",
       "en el escenario variegado la potencia del estadistico de BAF cae a 0,000 en la "
       "fraccion del 20 %: cuanto MAYOR es el evento, PEOR detecta. Se vuelve "
       "anti-informativo. La dispersion de cobertura conserva 1,000, igual que en clonal, "
       "porque no depende de que homologo se gano.",
       "que el indice de dispersion supere al metodo estandar. La linea base usada es una "
       "desviacion de BAF POR SITIO, SIN FASE; MoChA obtiene su potencia del faseo de largo "
       "alcance. La comparacion cara a cara NO se ha hecho.",
       generator="src/mosaic/simulate_dispersion.py → src/make_fig9.py")'''),

("md", """### Robustez · las cuatro predicciones, con el marcador

Dos se confirmaron y **dos fallaron**. La #4 falló de una forma que obliga a rebajar la
conclusión, y por eso las dos hipótesis se separan."""),

("code", '''PRED = [
 ("#1 el BAF detecta clonal desde\\nfracciones bajas",      0, "solo 0,28 al 10 %"),
 ("#2 el BAF COLAPSA en variegado",                        1, "cae a 0,000 al 20 %"),
 ("#3 la dispersion CONSERVA potencia\\nen variegado",      1, "0,96 al 10 %"),
 ("#4 la dispersion NO supera al BAF\\nen clonal",          0, "lo supera tambien ahi"),
]
fig, ax = plt.subplots(figsize=(8.8, 3.4))
labs = [p[0] for p in PRED][::-1]
ok = [p[1] for p in PRED][::-1]
note = [p[2] for p in PRED][::-1]
ax.barh(range(len(labs)), [1]*len(labs), color=[fl.ALIVE if o else fl.DEAD for o in ok],
        alpha=0.85, height=0.6)
ax.set_yticks(range(len(labs))); ax.set_yticklabels(labs, fontsize=8.6)
ax.set_xticks([]); ax.set_xlim(0, 1.5); ax.grid(False)
for i, (o, n) in enumerate(zip(ok, note)):
    ax.text(1.03, i, ("CONFIRMADA · " if o else "FALLADA · ") + n, va="center",
            fontsize=8.4, color=fl.ALIVE if o else fl.DEAD)
ax.set_title("Las cuatro predicciones preregistradas")

fl.done(fig, "Figura de robustez A · marcador de las predicciones", "EXP-015a", "SIMULATED",
        "la #2 y la #3 confirman el mecanismo: la cancelacion es un modo de fallo real y la "
        "dispersion sobrevive a el. La #4 fallo, y eso REVELA que la linea base de BAF usada "
        "es debil, no que nuestro estadistico sea superior.",
        "nada sobre el paciente. Y la potencia simulada es OPTIMISTA: el modelo no incluye "
        "sesgo de GC, mapabilidad ni sesgo de alelo de referencia, que a 44x son el factor "
        "limitante real. Por debajo del 5 % de fraccion celular no hay potencia en ninguno "
        "de los dos metodos.",
        prov="work/mosaic/dispersion_simulation.json · semilla 42")'''),

("md", """### Decisión de la parte A

| Hipótesis | Estado |
|---|---|
| **EXP-015a · el mecanismo de cancelación** | **SURVIVES** — modo de fallo reproducido y cuantificado |
| **EXP-015b · el índice como DETECTOR** | **PARKED · no validado** — el comparador no es MoChA |

**Prohibido decir** «enormemente más potente» o «supera a MoChA». Lo que subió de estatus es el
**mecanismo**, no el rendimiento relativo.

**La rama aplicada sigue BLOCKED:** exige controles procesados con pipeline idéntico, y no
existen."""),

("md", """---

# Parte B · MitoRead

## Corrección de una clasificación propia errónea

Esta rama se declaró bloqueada porque «el VCF no contiene variantes mitocondriales». **Eso es
irrelevante**: `mtDNA-CN` es un **cociente de cobertura** y no necesita ninguna variante. La
rama estaba mal clasificada.

| | |
|---|---|
| **EXP-014a · piloto técnico** | ejecutable con L001 |
| **EXP-014b · interpretación biológica** | **BLOCKED** |"""),

("code", '''mp = json.load(io.open("work/mito/pilot_l001.json", encoding="utf-8"))
print(f"  lecturas examinadas          : {mp['reads']:,}")
print(f"  compatibles con mitocondrial : {mp['mito_reads']:,}  ({100*mp['fraction']:.4f} %)")
print(f"  estimacion ingenua           : {mp['mtdna_cn_estimate']:.0f} copias-equivalentes")
print()
print(f"  interpretable: {mp['interpretable']}")
print(f"  por que no   : {mp['why_not']}")'''),

("md", """### Figura · el número, y por qué no es un resultado

**No** se dibuja una barra que diga «paciente = 259». Se dibuja **la estimación junto a las
fuentes de incertidumbre que no están cuantificadas**, para que sea imposible confundirla con
una medida."""),

("code", '''fig, axes = plt.subplots(1, 2, figsize=(11.2, 3.8),
                         gridspec_kw={"width_ratios": [1, 1.5]})

est = mp["mtdna_cn_estimate"]
axes[0].bar(["estimacion\\ningenua"], [est], color=fl.SOFT, alpha=0.55, width=0.45)
axes[0].errorbar([0], [est], yerr=[[est * 0.6], [est * 0.9]], fmt="none",
                 ecolor=fl.DEAD, elinewidth=2.2, capsize=9)
axes[0].axhspan(50, 500, color=fl.ALIVE, alpha=0.10)
axes[0].text(0.42, 300, "rango fisiologico\\nhabitual en sangre", fontsize=7.8, color=fl.ALIVE)
axes[0].set_ylabel("copias-equivalentes por celula")
axes[0].set_title("PROTOTIPO — no es una medida")
axes[0].text(0, est * 1.55, "incertidumbre\\nNO cuantificada", ha="center", fontsize=8.4,
             color=fl.DEAD, fontweight="bold")

SRC = [("NUMT no excluidos (sesgo AL ALZA)", 1.0),
       ("un solo carril, no profundidad completa", 0.8),
       ("sin alineamiento al genoma completo", 0.8),
       ("sin controles con pipeline identico", 0.9),
       ("plaquetas (mitocondrias sin nucleo)", 0.85),
       ("formula leucocitaria", 0.7),
       ("tipo de libreria sin confirmar", 0.5)]
axes[1].barh(range(len(SRC)), [s[1] for s in SRC][::-1], color=fl.DEAD, alpha=0.8, height=0.6)
axes[1].set_yticks(range(len(SRC)))
axes[1].set_yticklabels([s[0] for s in SRC][::-1], fontsize=8.4)
axes[1].set_xticks([]); axes[1].set_xlim(0, 1.05); axes[1].grid(False)
axes[1].set_title("Fuentes de incertidumbre, ninguna cuantificada")

fl.done(fig, "Figura B · el prototipo y su incertidumbre, juntos", "EXP-014a", "DERIVED",
        f"la senal es extraible: {100*mp['fraction']:.3f} % de las lecturas de L001 son "
        f"compatibles con el genoma mitocondrial, y el cociente da ~{est:.0f} "
        "copias-equivalentes. **Eso valida que la rama es tecnicamente ejecutable.**",
        "NADA sobre la biologia del paciente. Que el valor caiga en el rango fisiologico es "
        "precisamente lo que lo hace peligroso, no lo que lo respalda. La formulacion correcta "
        "es *naive mtDNA-equivalent estimate bajo los supuestos del piloto*, NUNCA "
        "'mtDNA-CN del paciente'.",
        prov="submuestra de L001 R1 · k-meros de 31 pb contra la referencia mitocondrial")'''),

("md", """### Decisión de la parte B

| | |
|---|---|
| **EXP-014a** | **UNRESOLVED · prototipo** — la señal es extraíble; nada está calibrado |
| **EXP-014b** | **BLOCKED** — BAM/CRAM completo · controles · hemograma |
| **EXP-014a-v2** (alineamiento para excluir NUMT) | **PARKED** — sin alineador instalable y descargar binarios está prohibido por política |

### El supuesto más atacable de toda la rama

Que la `mtDNA-CN` en **sangre periférica** refleje el estado mitocondrial de músculo y riñón.
Y con n=1 bulk **no hay gradiente interno**: es un punto, no una curva dosis-respuesta.

### Siguiente experimento

Alineamiento al genoma completo con exclusión de NUMT, **controles** procesados con pipeline
idéntico, y el **hemograma contemporáneo** — que sigue sin respuesta y es un email."""),
]

if __name__ == "__main__":
    run(OUT, CELLS, min_figs=3)
