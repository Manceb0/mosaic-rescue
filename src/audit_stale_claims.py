#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AUDIT 2 · escaner de afirmaciones OBSOLETAS en ficheros versionados.

POR QUE
    Cada resultado nuevo que falsa o estrecha uno anterior deja atras frases en
    otros documentos. Encontrarlas a ojo no escala y no es repetible.

QUE DISTINGUE — y es la parte importante
    Un documento HISTORICO (bitacora, registro de experimentos) DEBE conservar
    la afirmacion vieja con su correccion al lado: ese es el rastro de auditoria.
    Un documento CANONICO (lo que un jurado lee como verdad actual) NO puede
    llevarla, porque ahi parece incoherencia y no rigor.

    Por eso cada hallazgo se clasifica segun DONDE aparece.

NO decide por si solo. Produce la lista para revisarla una a una.
"""
from __future__ import annotations
import io, re, sys, subprocess

# Documentos que un lector externo toma como estado ACTUAL del proyecto.
CANONICAL = (
    "README.md", "CLAUDE.md",
    "docs/01_MASTER_BRIEF.md", "docs/02_ANALYSIS_PLAN.md",
    "docs/04_ARQUITECTURA_MAESTRA.md", "docs/05_CONTRATO_VISUAL.md",
    "research/SCIENTIFIC_CRITICAL_PATH.md", "research/EXPERIMENT_REGISTRY.md",
    "research/CANONICAL_CLAIMS.md",
)
# Las figuras son lo PRIMERO que lee un jurado: cuentan como canonicas.
CANONICAL_PREFIX = ("figures/",)
# Documentos cuyo VALOR es conservar lo que se creyo y que lo falso.
HISTORICAL = ("docs/DECISIONS.md", "docs/EVIDENCE.md", "research/agent_findings/")

# (patron, por que esta obsoleto o prohibido, formulacion vigente)
STALE = [
    (r"#\s*1 en (los|todos los) (15|quince)|#1 in all",
     "A0 corregido: BUB1B es #4 en el A0 congelado",
     "#1 en 14 de 15; en A0 congelado #4, y #1 en la sensibilidad A0-FREQFIX"),
    (r"~?4[23](?:[.,]\d)?\s*x efectiv|profundidad efectiva.{0,12}4[23]",
     "profundidad efectiva de un solo carril, no del dataset con el que se llamo el VCF",
     "L001 ~13x en disco; el VCF viene de los cuatro carriles"),
    (r"(?<!\?)\bdesestabiliza(nte|)\b(?!.{0,120}(no demostrad|hipotesis|hipótesis|predic|inferencia|modelar|primera version|primera versión))(?!.{0,40}\?)",
     "el analisis geometrico corrigio a la baja: esterico y carga enterrada debilitados",
     "estructuralmente preocupante; desestabilizacion NO demostrada"),
    (r"jaula (de )?cuatro aromatic|cuatro anillos aromaticos conservad",
     "conservacion ortologa: de los cuatro aromaticos, uno no esta conservado ni en clase",
     "bolsillo hidrofobico conservado; la jaula de cuatro aromaticos no lo esta"),
    (r"heterocigosis compuesta (confirmad|demostrad|establecid)|compound heterozygous (confirmed|established)",
     "la fase no esta resuelta y PM3 sigue bloqueado",
     "candidato a heterocigosis compuesta, fase NO resuelta"),
    (r"(?<!afirmar configuracion )(?<!afirmar configuración )\ben trans\b(?!.{0,60}(no resuelt|no establecid|NO establecid|candidat|sin resolver|que la fase|, y el))|\bin trans\b(?!.{0,60}unresolved)",
     "trans no demostrado sin genotipos parentales ni lectura larga",
     "fase no resuelta"),
    (r"CNV grande descartad|large CNV excluded|se descarta la CNV",
     "la profundidad del VCF no esta normalizada para llamar numero de copia",
     "sin evidencia de delecion heterocigota grande desde profundidad y heterocigosidad"),
    (r"mtDNA-CN del paciente|mtDNA-CN medid|copias por celula del paciente",
     "el piloto es prototipo con k-meros, NUMT no excluidos",
     "naive mtDNA-equivalent estimate bajo los supuestos del piloto"),
    (r"dispersion.{0,30}(superior|mas potente|supera).{0,20}MoChA|mas potente que el metodo estandar",
     "el comparador usado no reproduce el faseo de largo alcance de MoChA",
     "el indice sobrevive a la cancelacion; superioridad NO demostrada"),
    (r'(?<!no ")(?<!llama )convergencia mecanistica|MECHANISTIC CONVERGENCE',
     "con n=1 bulk son dos observaciones compatibles, no una regresion",
     "consistency check"),
    (r"\*\*Arimoclomol\.\*\*\s*La nominaci|nominacion.{0,20}arimoclomol|arimoclomol.{0,20}nominad",
     "no hay nominacion de farmaco; la compuerta exige cinco condiciones y ninguna candidata las reune",
     "clase mecanistica candidata; sin nominacion"),
    (r"muy buena hipotesis farmacologica|buena hipotesis de farmaco|strong drug hypothesis",
     "el puente 7 esta UNRESOLVED con contraevidencia en otro sistema",
     "hipotesis mecanistica con el puente farmacologico sin resolver"),
    (r"mantiene la hipotesis viva.{0,60}dependiente de estres|stress-dependent action keeps",
     "la via dependiente de estres esta al 50-60 % en celulas aneuploides: es a la vez razon y pasivo",
     "tension mecanistica: la deficiencia de HSF1 hace la via relevante Y la farmacologia incierta"),
    (r"subir HSP.{0,40}(luego|por tanto|therefore).{0,40}coinduct",
     "sustitucion prohibida: puente 6 no es puente 7",
     "el aumento genetico rescata; la coinduccion farmacologica no esta demostrada"),
]


def files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    keep = (".md", ".ipynb", ".svg", ".html", ".py", ".yaml", ".txt")
    return [f for f in out.splitlines()
            if f.endswith(keep) and not f.startswith(("work/", "results/"))]


def classify(path):
    if path.startswith(HISTORICAL):
        return "HISTORICO"
    if path in CANONICAL or path.startswith(CANONICAL_PREFIX):
        return "CANONICO"
    return "OTRO"


def norm(s):
    """Sin acentos, para que el patron case escriba como escriba el documento."""
    for a, b in zip("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN"):
        s = s.replace(a, b)
    return s


def main():
    rows = []
    for f in files():
        try:
            txt = io.open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for pat, why, current in STALE:
            for m in re.finditer(pat, norm(txt), re.I):
                line = norm(txt).count("\n", 0, m.start()) + 1
                frag = txt.splitlines()[line - 1][:110] if line <= len(txt.splitlines()) else ""
                rows.append((classify(f), f, line, m.group(0)[:40], why, current, frag))

    order = {"CANONICO": 0, "OTRO": 1, "HISTORICO": 2}
    rows.sort(key=lambda r: (order[r[0]], r[1], r[2]))

    print(f"  ficheros revisados: {len(files())}\n")
    cur = None
    for cls, f, line, hit, why, current, frag in rows:
        if cls != cur:
            cur = cls
            head = {"CANONICO": "REQUIEREN CORRECCION — un lector externo los toma como verdad actual",
                    "OTRO": "REVISAR — codigo, figuras y docs secundarios",
                    "HISTORICO": "CORRECTOS ASI — el rastro de auditoria DEBE conservarlos"}[cls]
            print(f"\n=== {cls} · {head} ===\n")
        print(f"  {f}:{line}")
        print(f"    coincide   : {hit!r}")
        print(f"    obsoleto   : {why}")
        print(f"    vigente    : {current}")
        print(f"    contexto   : {frag.strip()[:100]}")
        print()

    n_can = sum(1 for r in rows if r[0] == "CANONICO")
    print(f"\n  TOTAL {len(rows)} coincidencias · {n_can} en documentos CANONICOS")
    return 1 if n_can else 0


if __name__ == "__main__":
    sys.exit(main())
