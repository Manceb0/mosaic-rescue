#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-015a · simulacion de la cancelacion de BAF y del indice de dispersion.

COMPUERTA, NO EXTRA. El brief deja el indice de dispersion en `L1` hasta
simularlo contra el metodo estandar. Aplicarlo al paciente sin esto seria
presentar un estadistico nuevo sin haber demostrado que aporta algo.

NO USA NINGUN DATO DEL PACIENTE. Es computo puro con la profundidad real (44x)
como unico parametro tomado del caso.

Preregistro completo en docs/DECISIONS.md § EXP-015a, escrito antes de este
fichero. Las cuatro predicciones y la regla de decision estan alli.

Modelo, deliberadamente simple y declarado:
  - N sitios heterocigotos por cromosoma, profundidad Poisson de media 44x
  - Euploide: cada sitio reparte lecturas Binomial(DP, 0.5)
  - Trisomia en fraccion f, CLONAL: se gana SIEMPRE el mismo homologo, asi que
    la proporcion esperada se desplaza a (1+f)/(2+f)
  - Trisomia en fraccion f, VARIEGADO: cada linaje gana un homologo al azar, y
    la mitad de la fraccion desplaza en cada direccion -> cancelacion
  - La COBERTURA sube a (2+f)/2 en ambos escenarios: no se cancela

Lo que el modelo NO incluye, y por eso la potencia sale OPTIMISTA: sesgo de GC,
mapabilidad, sesgo de alelo de referencia. A 44x esos son el factor limitante
real, no el ruido binomial.
"""
from __future__ import annotations
import io, json, math, statistics
import random

SEED = 42                    # semilla fija, declarada en el preregistro
DEPTH = 44                   # profundidad mediana real del caso
N_SITES = 400                # sitios heterocigotos por cromosoma evaluado
N_CHROM = 22                 # autosomas
N_REP = 200                  # repeticiones por celda
FRACTIONS = [0.01, 0.02, 0.05, 0.10, 0.20]
ALPHA = 0.05                 # tasa de falsos positivos fijada


def _poisson(rng, lam):
    """Poisson por el metodo de Knuth. Suficiente para lam=44 y evita numpy."""
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def _binom(rng, n, p):
    return sum(1 for _ in range(n) if rng.random() < p)


def simulate_chromosome(rng, f: float, mode: str):
    """Devuelve (desviacion media de BAF, log-ratio de cobertura) de un cromosoma.

    mode: 'null' euploide · 'clonal' un homologo · 'variegated' homologo aleatorio
    """
    if mode == "null":
        p_shift = 0.0
        cov = 1.0
    elif mode == "clonal":
        # todas las celulas ganan el MISMO homologo: el desplazamiento se suma
        p_shift = (1 + f) / (2 + f) - 0.5
        cov = (2 + f) / 2
    elif mode == "variegated":
        # cada linaje gana uno al azar: la mitad desplaza a un lado y la mitad
        # al otro. El desplazamiento ESPERADO es cero -> cancelacion.
        p_shift = 0.0
        cov = (2 + f) / 2
    else:
        raise ValueError(mode)

    devs = []
    for _ in range(N_SITES):
        dp = max(1, _poisson(rng, DEPTH * cov))
        if mode == "variegated" and f > 0:
            # el signo del desplazamiento se sortea POR SITIO: distintos linajes
            # dominan en distintas regiones. Ese es el mecanismo de cancelacion.
            local = p_shift + ((1 + f) / (2 + f) - 0.5) * rng.choice([-1, 1]) * (rng.random() < f)
        else:
            local = p_shift
        alt = _binom(rng, dp, min(max(0.5 + local, 0.01), 0.99))
        devs.append(abs(alt / dp - 0.5))
    baf_stat = statistics.fmean(devs)
    lrr = math.log2(cov)
    return baf_stat, lrr


def simulate_genome(rng, f: float, mode: str, n_affected: int = 3):
    """Un genoma: `n_affected` cromosomas con el evento, el resto euploides.

    Estadisticos devueltos:
      baf  -> desviacion media de BAF en los cromosomas afectados (metodo estandar)
      disp -> VARIANZA del log-ratio de cobertura ENTRE cromosomas (el propuesto)
    """
    bafs, lrrs = [], []
    for c in range(N_CHROM):
        m = mode if c < n_affected else "null"
        b, l = simulate_chromosome(rng, f if c < n_affected else 0.0, m)
        bafs.append(b)
        lrrs.append(l + rng.gauss(0, 0.02))     # ruido tecnico de cobertura
    return statistics.fmean(bafs[:n_affected]), statistics.pvariance(lrrs)


def power_at(null_vals, alt_vals, alpha=ALPHA):
    """Potencia con la FPR fijada: umbral en el percentil (1-alpha) del nulo."""
    s = sorted(null_vals)
    thr = s[min(len(s) - 1, int((1 - alpha) * len(s)))]
    return sum(1 for v in alt_vals if v > thr) / len(alt_vals)


def run():
    rng = random.Random(SEED)
    null_baf, null_disp = [], []
    for _ in range(N_REP):
        b, d = simulate_genome(rng, 0.0, "null")
        null_baf.append(b)
        null_disp.append(d)

    out = {"seed": SEED, "depth": DEPTH, "n_rep": N_REP, "alpha": ALPHA,
           "n_sites": N_SITES, "results": []}
    for mode in ("clonal", "variegated"):
        for f in FRACTIONS:
            ab, ad = [], []
            for _ in range(N_REP):
                b, d = simulate_genome(rng, f, mode)
                ab.append(b)
                ad.append(d)
            out["results"].append({
                "mode": mode, "fraction": f,
                "power_baf": round(power_at(null_baf, ab), 3),
                "power_dispersion": round(power_at(null_disp, ad), 3),
            })
    return out


if __name__ == "__main__":
    import os
    res = run()
    os.makedirs("work/mosaic", exist_ok=True)
    json.dump(res, io.open("work/mosaic/dispersion_simulation.json", "w", encoding="utf-8"),
              indent=1)
    print(f"  semilla {res['seed']} · {res['n_rep']} repeticiones · profundidad {res['depth']}x"
          f" · FPR fijada {res['alpha']}\n")
    print(f"  {'escenario':<14}{'fraccion':>10}{'potencia BAF':>15}{'potencia DISPERSION':>22}")
    print("  " + "-" * 60)
    for r in res["results"]:
        print(f"  {r['mode']:<14}{r['fraction']*100:>9.0f}%{r['power_baf']:>15.3f}"
              f"{r['power_dispersion']:>22.3f}")
    print("\n  -> work/mosaic/dispersion_simulation.json")
