#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometria REAL del bolsillo alrededor del residuo candidato.

POR QUE ESTE MODULO
    La figura estructural del proyecto era un SVG dibujado a mano. Un revisor no
    puede comprobar de donde salen las distancias. Aqui todo se calcula sobre las
    coordenadas del modelo de AlphaFold (AF-O60566-F1.pdb): vecinos por distancia
    entre atomos pesados, puentes de hidrogeno por criterio geometrico, y pLDDT
    leido de la columna de factor B.

LO QUE ES Y LO QUE NO ES
    Es la geometria de un MODELO PREDICHO, no de una estructura experimental.
    Por eso el pLDDT viaja siempre con la figura: sin el, un modelo de AlphaFold
    se lee como si fuera una cristalografia, y no lo es.

    El criterio de puente de hidrogeno es puramente geometrico (donante/aceptor
    N u O a <= 3.5 A). No hay hidrogenos en el modelo, asi que NO se comprueba
    el angulo: son puentes de hidrogeno CANDIDATOS, y se declaran como tales.

SANEADO
    El numero del residuo candidato NO esta aqui. Se lee de config/paths.yaml,
    que esta en .gitignore.
"""
from __future__ import annotations
import collections, io, math

PDB = "work/struct/AF-O60566-F1.pdb"
HB_MAX = 3.5          # A, distancia donante-aceptor
CONTACT = 5.0         # A, entre atomos pesados
BACKBONE = {"N", "CA", "C", "O"}

AA3 = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
       "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
       "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
       "TYR": "Y", "VAL": "V"}


def read_pdb(path: str = PDB):
    """{resnum: {'aa','plddt','atoms':{name:(x,y,z)}}} del primer modelo."""
    res = {}
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("ATOM"):
            continue
        name = line[12:16].strip()
        if line[76:78].strip() == "H":
            continue
        num = int(line[22:26])
        r = res.setdefault(num, {"aa": AA3.get(line[17:20].strip(), "X"),
                                 "plddt": float(line[60:66]), "atoms": {}})
        r["atoms"][name] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
    return res


def _d(a, b):
    return math.dist(a, b)


def neighbours(res: dict, target: int, cutoff: float = CONTACT, side_chain_only=True):
    """Vecinos por distancia MINIMA entre atomos pesados. Devuelve lista
    ordenada de (resnum, aa, dmin, par de atomos)."""
    t = res[target]
    tat = {k: v for k, v in t["atoms"].items()
           if not (side_chain_only and k in BACKBONE)} or t["atoms"]
    out = []
    for n, r in res.items():
        if abs(n - target) < 1 or n == target:
            continue
        best = None
        for an, a in tat.items():
            for bn, b in r["atoms"].items():
                d = _d(a, b)
                if best is None or d < best[0]:
                    best = (d, an, bn)
        if best and best[0] <= cutoff:
            out.append({"resnum": n, "aa": r["aa"], "dmin": round(best[0], 2),
                        "atoms": (best[1], best[2]), "plddt": r["plddt"],
                        "contiguo": abs(n - target) <= 4})
    return sorted(out, key=lambda x: x["dmin"])


def hbonds(res: dict, target: int, cutoff: float = HB_MAX):
    """Puentes de hidrogeno CANDIDATOS: pares N/O a <= cutoff. Sin angulo:
    el modelo no trae hidrogenos, asi que la geometria esta incompleta."""
    t = res[target]
    out = []
    for an, a in t["atoms"].items():
        if an[0] not in "NO":
            continue
        for n, r in res.items():
            if n == target:
                continue
            for bn, b in r["atoms"].items():
                if bn[0] not in "NO":
                    continue
                d = _d(a, b)
                if d <= cutoff:
                    out.append({"from": an, "to_res": n, "to_aa": r["aa"], "to_atom": bn,
                                "dist": round(d, 2),
                                "sc_sc": an not in BACKBONE and bn not in BACKBONE})
    return sorted(out, key=lambda x: x["dist"])


def plddt_track(res: dict, lo: int, hi: int):
    xs = [n for n in range(lo, hi + 1) if n in res]
    return xs, [res[n]["plddt"] for n in xs]


def summary(target: int, pocket=()):
    res = read_pdb()
    nb = neighbours(res, target)
    hb = hbonds(res, target)
    return {"res": res, "target": target, "aa": res[target]["aa"],
            "plddt": res[target]["plddt"], "neighbours": nb, "hbonds": hb,
            "pocket_present": [p for p in pocket if p in res]}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.paths import get
    t = int(get("candidate", "residue"))
    s = summary(t, get("candidate", "pocket", default=()))
    print(f"  modelo: {PDB}  ·  {len(s['res'])} residuos")
    print(f"  pLDDT del residuo candidato: {s['plddt']:.1f}")
    print(f"  vecinos a <= {CONTACT} A (atomos pesados, cadena lateral): {len(s['neighbours'])}")
    for n in s["neighbours"][:12]:
        print(f"    {n['aa']}{n['resnum']:<6}{n['dmin']:>5.2f} A   "
              f"{n['atoms'][0]}-{n['atoms'][1]:<5} pLDDT {n['plddt']:.0f}"
              f"{'   (contiguo en secuencia)' if n['contiguo'] else ''}")
    print(f"  puentes de H candidatos a <= {HB_MAX} A: {len(s['hbonds'])}")
    for h in s["hbonds"][:8]:
        print(f"    {h['from']:<4} -> {h['to_aa']}{h['to_res']:<6}{h['to_atom']:<5}"
              f"{h['dist']:>5.2f} A  {'cadena lateral' if h['sc_sc'] else 'esqueleto'}")
