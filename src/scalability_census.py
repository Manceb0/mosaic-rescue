#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cuanto de src/ depende de ESTE caso, y cuanto no.

    python src/scalability_census.py

POR QUE EXISTE
    La escalabilidad pesa 15 % en la evaluacion oficial, y la respuesta habitual
    a esa pregunta es una afirmacion sin numero: "el metodo es general". Aqui se
    mide. Un modulo cuenta como especifico del caso si menciona el gen, la
    enfermedad, un rasgo del probando o uno de los compuestos evaluados.

QUE MIDE Y QUE NO
    Mide DEPENDENCIA TEXTUAL, que es un limite superior de la dependencia real:
    muchos de los modulos marcados como especificos solo nombran el caso en
    titulos de figura y cadenas de texto, no en la logica. Por eso el numero de
    modulos genericos es un SUELO, no un techo.

    No mide, y no puede: si el metodo funcionaria de verdad en otro paciente.
    Eso exige un segundo paciente, y este proyecto solo tiene uno. Declarado en
    docs/SCALABILITY.md como el limite principal.
"""
from __future__ import annotations
import io, os, re, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# El vocabulario de "esto es de este caso". Deliberadamente amplio: si duda,
# cuenta como especifico, para que el numero de genericos no se infle.
CASE = re.compile(
    r"BUB1B|BUBR1|\bMVA\b|nefrocalcin|nephrocalc|arimoclomol|sirolimus|"
    r"azithro|azitromicina|HSF1|257300|rabdomiosarcoma|rhabdomyosarcoma",
    re.IGNORECASE)


def census(pkg: str = "src"):
    rows = []
    base = os.path.join(ROOT, pkg)
    for dp, _dn, fn in os.walk(base):
        if "__pycache__" in dp:
            continue
        for f in sorted(fn):
            if not f.endswith(".py") or f == "__init__.py":
                continue
            # El censo se excluye a si mismo: su regex CONTIENE por fuerza todo
            # el vocabulario del caso, asi que contarse seria un artefacto de
            # autorreferencia, no una dependencia.
            if f == os.path.basename(__file__):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
            t = io.open(p, encoding="utf-8", errors="replace").read()
            rows.append((rel, len(t.splitlines()), len(CASE.findall(t))))
    return rows


def main() -> int:
    rows = census()
    gen = [r for r in rows if r[2] == 0]
    spec = [r for r in rows if r[2] > 0]
    lg, ls = sum(r[1] for r in gen), sum(r[1] for r in spec)

    print("MOSAIC RESCUE, censo de escalabilidad de src/")
    print()
    print(f"  {'':<38}{'modulos':>9}{'lineas':>9}")
    print("  " + "-" * 56)
    print(f"  {'sin ninguna mencion al caso':<38}{len(gen):>9}{lg:>9}")
    print(f"  {'con menciones al caso':<38}{len(spec):>9}{ls:>9}")
    print("  " + "-" * 56)
    print(f"  {'total':<38}{len(rows):>9}{lg + ls:>9}")
    print()
    print(f"  {100.0 * lg / max(lg + ls, 1):.0f} % de las lineas de src/ no sabe que "
          "este paciente existe.")
    print()
    print("  TRANSFERIBLES TAL CUAL")
    for p, l, _ in sorted(gen):
        print(f"    {p:<48}{l:>5} lineas")
    print()
    print("  ATADOS AL CASO (mas menciones = mas atado)")
    for p, l, n in sorted(spec, key=lambda r: (-r[2], r[0])):
        print(f"    {p:<48}{l:>5} lineas{n:>5} menciones")
    print()
    print("  Lo que este censo NO demuestra: que el metodo funcione en otro")
    print("  paciente. Eso exige un segundo paciente. Ver docs/SCALABILITY.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
