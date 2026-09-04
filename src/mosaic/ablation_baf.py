#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-015c · ablacion 2x2: que mecanismo explica cada senal del BAF.

POR QUE EXISTE ESTE FICHERO. EXP-015a publico esta afirmacion:

    en escenario variegado el estadistico de BAF pierde potencia segun crece el
    evento, PORQUE las contribuciones de linajes distintos se cancelan.

Una auditoria adversarial del propio repositorio la falso. El estadistico que
EXP-015a mide es `abs(alt/dp - 0.5)`, un valor ABSOLUTO, y la aleatorizacion de
signo por sitio -- que el codigo llama "el mecanismo de cancelacion" -- le es
INVISIBLE: Binomial(dp, 0.5+d) y Binomial(dp, 0.5-d) son imagenes especulares,
asi que |BAF-0.5| tiene la misma distribucion con signo fijo que con signo
sorteado. Lo que si cambia el resultado es que el brazo variegado se simula con
mas profundidad que el nulo, porque la copia extra sube la cobertura a (2+f)/2,
y `abs(alt/dp - 0.5)` encoge con la profundidad.

El senal de alarma estaba a la vista desde el principio: la potencia publicada
cae a 0,000, POR DEBAJO de alpha = 0,05. Un mecanismo que solo puede anadir
dispersion nunca baja del azar. El preregistro (docs/DECISIONS.md, EXP-015a,
prediccion 2) habia escrito "potencia proxima al azar", no cero.

QUE HACE ESTE FICHERO, Y QUE NO HACE. Cruza los dos factores que EXP-015a tenia
confundidos y mide cuatro estadisticos en cada celda. NO intenta demostrar que
la dispersion "gane". La unica pregunta es que mecanismo explica cada senal.

    factor 1 · direccion del homologo    fixed  -> todos los sitios afectados se
                                                  desplazan en el MISMO sentido
                                         mixed  -> el sentido se sortea por sitio
    factor 2 · modelo de profundidad     cn     -> profundidad escalada por numero
                                                  de copia, DEPTH * (2+f)/2
                                         matched-> profundidad igualada al nulo

    estadistico  signed  |media por sitio de (BAF - 0,5)|   <- lo que SI cancela
                 absdev  media por sitio de |BAF - 0,5|     <- lo que EXP-015a uso
                 disp    varianza por sitio del BAF. OJO: NO es el indice de
                         dispersion de COBERTURA de EXP-015b, que es la varianza
                         del log-ratio de cobertura ENTRE cromosomas. Mismo
                         apodo, otro objeto; aqui se mide el BAF
                 znorm   media de |z|, z = (alt - dp/2) / sqrt(dp/4)

`znorm` es la version normalizada por la varianza binomial esperada A LA
PROFUNDIDAD OBSERVADA. Bajo p = 0,5 cada z es aproximadamente normal tipificada
sea cual sea dp, asi que el estadistico es invariante a la profundidad por
construccion. Es el control que EXP-015a no tenia.

LA PROFUNDIDAD NO ES UN BUG ARTIFICIAL. Si hay una ganancia cromosomica real,
mas copias producen mas lecturas: escalar la cobertura por (2+f)/2 es correcto.
El error de EXP-015a fue comparar contra un nulo de OTRA profundidad un
estadistico cuya varianza depende de la profundidad, y despues adjudicar esa
diferencia a la cancelacion. El confundido es entre direccion de homologo y
profundidad dependiente del numero de copia, no un descuido de codificacion.

NO USA NINGUN DATO DEL PACIENTE. Computo puro, con la profundidad real (44x)
como unico parametro tomado del caso, igual que EXP-015a.

El preregistro historico de docs/DECISIONS.md NO se reescribe. Lo que cambia es
el ESTADO del experimento, y el estado nuevo se anota al lado del viejo.
"""
from __future__ import annotations
import io, json, math, os, statistics, sys, random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.mosaic.simulate_dispersion import _poisson, _binom, DEPTH, N_SITES, N_REP, ALPHA

SEED = 42
FRACTIONS = [0.01, 0.05, 0.10, 0.20]
N_AFFECTED = 3               # cromosomas con el evento, igual que EXP-015a
OUT = "work/mosaic/baf_ablation.json"


def simulate_arm(rng, f, direction, depth_model, scope="frac", n_affected=N_AFFECTED):
    """Un genoma. Devuelve los cuatro estadisticos y la profundidad media real.

    direction: 'none' euploide · 'fixed' mismo sentido · 'mixed' sentido sorteado
    depth_model: 'cn' cobertura (2+f)/2 · 'matched' cobertura igualada al nulo
    scope: 'frac' la perturbacion alcanza a una fraccion f de los sitios, que es
           el modelo variegado de EXP-015a · 'all' alcanza a TODOS los sitios,
           que es el modelo CLONAL de EXP-015a y sirve de referencia
    """
    cov = (2 + f) / 2 if depth_model == "cn" else 1.0
    shift = (1 + f) / (2 + f) - 0.5          # magnitud del desplazamiento
    devs, signed, zs, bafs, depths = [], [], [], [], []
    for _ in range(n_affected * N_SITES):
        dp = max(1, _poisson(rng, DEPTH * cov))
        if direction == "none" or f <= 0:
            local = 0.0
        else:
            # la perturbacion alcanza a una fraccion f de los sitios, igual que
            # en EXP-015a; lo unico que cambia entre las dos celdas es el SIGNO
            sign = rng.choice([-1, 1]) if direction == "mixed" else 1
            # el sorteo se consume siempre, para que las dos ramas de `scope`
            # recorran la misma secuencia del generador y sean comparables
            u = rng.random()
            hit = True if scope == "all" else (u < f)
            local = shift * sign * hit
        alt = _binom(rng, dp, min(max(0.5 + local, 0.01), 0.99))
        baf = alt / dp
        bafs.append(baf)
        devs.append(abs(baf - 0.5))
        signed.append(baf - 0.5)
        zs.append(abs(alt - dp / 2) / math.sqrt(dp / 4))
        depths.append(dp)
    return {
        "signed": abs(statistics.fmean(signed)),
        "absdev": statistics.fmean(devs),
        "disp": statistics.pvariance(bafs),
        "znorm": statistics.fmean(zs),
        "depth": statistics.fmean(depths),
    }


STATS = ("signed", "absdev", "disp", "znorm")


def power_at(null_vals, alt_vals, alpha=ALPHA):
    """Potencia con la FPR fijada: umbral en el percentil (1-alpha) del nulo.

    Misma regla que EXP-015a, de una cola por arriba, para que las cifras sean
    comparables con las publicadas. Una potencia POR DEBAJO de alpha significa
    que el brazo alternativo cayo al lado equivocado del nulo.
    """
    s = sorted(null_vals)
    thr = s[min(len(s) - 1, int((1 - alpha) * len(s)))]
    return sum(1 for v in alt_vals if v > thr) / len(alt_vals)


def arm(seed, f, direction, depth_model, scope="frac"):
    rng = random.Random(seed)
    return [simulate_arm(rng, f, direction, depth_model, scope) for _ in range(N_REP)]


def run():
    out = {"seed": SEED, "depth": DEPTH, "n_rep": N_REP, "alpha": ALPHA,
           "n_sites": N_SITES, "n_affected": N_AFFECTED,
           "experiment": "EXP-015c", "cells": []}

    # el nulo es euploide a la profundidad real: el mismo comparador honesto
    # para las cuatro celdas, que es justo lo que EXP-015a no tuvo
    null = arm(SEED, 0.0, "none", "matched")
    nulls = {s: [r[s] for r in null] for s in STATS}
    out["null"] = {s: round(statistics.fmean(nulls[s]), 6) for s in STATS}
    out["null"]["depth"] = round(statistics.fmean([r["depth"] for r in null]), 3)

    # las cuatro celdas del 2x2 viven dentro del modelo VARIEGADO (scope frac);
    # las dos ultimas son la REFERENCIA clonal (scope all), que no forma parte de
    # la ablacion y esta para que la tabla se pueda situar
    grid = [("fixed", "cn", "frac"), ("fixed", "matched", "frac"),
            ("mixed", "cn", "frac"), ("mixed", "matched", "frac"),
            ("fixed", "cn", "all"), ("fixed", "matched", "all")]
    for direction, depth_model, scope in grid:
        for f in FRACTIONS:
            reps = arm(SEED + 1, f, direction, depth_model, scope)
            cell = {"direction": direction, "depth_model": depth_model, "scope": scope,
                    "fraction": f,
                    "mean_depth": round(statistics.fmean([r["depth"] for r in reps]), 3)}
            for s in STATS:
                vals = [r[s] for r in reps]
                cell[f"mean_{s}"] = round(statistics.fmean(vals), 6)
                cell[f"power_{s}"] = round(power_at(nulls[s], vals), 3)
            out["cells"].append(cell)
            print(f"  {direction:5s} {depth_model:7s} {scope:4s} f={f:<5} "
                  f"dp={cell['mean_depth']:6.2f}  "
                  + "  ".join(f"{s}={cell['mean_'+s]:.5f}/{cell['power_'+s]:.3f}"
                              for s in STATS))
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"\n  -> {OUT}")
    return out


if __name__ == "__main__":
    os.makedirs("work/mosaic", exist_ok=True)
    print("EXP-015c · ablacion 2x2 · direccion de homologo x modelo de profundidad\n")
    run()
