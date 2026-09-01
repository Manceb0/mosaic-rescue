#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-021b · `A0-FREQFIX`, analisis de SENSIBILIDAD.

QUE ES Y QUE NO ES
    NO sustituye a `A0`. `A0` esta congelado por el preregistro de EXP-006 y se
    reporta tal y como salio, con BUB1B en el puesto 4.

    Esto responde una pregunta distinta y acotada: .cuanto de ese resultado lo
    explica un DEFECTO DE ANOTACION conocido?

EL DEFECTO
    VEP dejo `MAX_AF` vacio en 33 alelos, casi todos indels, porque la
    representacion del indel no casa con la de la base de frecuencias. La regla
    congelada trata "sin frecuencia" como "raro", asi que esos 33 entran como si
    fueran variantes nuevas.

LA REGLA QUE HACE HONESTO ESTO
    El arreglo se aplica a LOS 33, no a los que estorban. Elegir solo las tres
    que desplazaron a BUB1B seria exactamente el sesgo que el preregistro
    prohibe.

Todo local: la frecuencia se recupera de la base que Exomiser ya tiene
descargada. Ninguna coordenada del paciente sale de la maquina.
"""
from __future__ import annotations
import io, os, sys, json, gzip, glob, shutil, subprocess

sys.path.insert(0, ".")
from src.prioritization.genome_wide import load, rank      # noqa: E402
from src.paths import patient_vcf                          # noqa: E402

RUN = "work/exomiser/runs/FREQFIX"
HOME = "work/exomiser/exomiser-cli-14.1.0"
ANN = "work/gw/highmod_ann.tsv"


def missing_freq(rows):
    """Alelos unicos con genotipo cruzado y sin MAX_AF."""
    seen, out = set(), []
    for v in rows:
        if v.impact not in ("HIGH", "MODERATE") or not v.gt:
            continue
        k = (v.loc, v.allele)
        if k in seen:
            continue
        seen.add(k)
        if v.max_af is None:
            out.append(v)
    return out


def write_mini_vcf(variants, dest):
    """VCF con solo esos sitios. Va a work/, gitignored."""
    want = set()
    for v in variants:
        base = int(v.loc.split(":")[1].split("-")[0])
        for d in (0, -1, -2):
            want.add((v.chrom, base + d))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    n = 0
    with gzip.open(patient_vcf(), "rt", errors="replace") as f, \
            io.open(dest, "w", encoding="utf-8", newline="\n") as out:
        for line in f:
            if line[0] == "#":
                out.write(line)
                continue
            p = line.split("\t", 3)
            if (p[0], int(p[1])) in want:
                out.write(line)
                n += 1
    return n


def run_exomiser(mini_vcf):
    src = "work/exomiser/runs/MINI"
    os.makedirs(RUN, exist_ok=True)
    uri = "file:///" + os.path.abspath(mini_vcf).replace(os.sep, "/").lstrip("/")
    s = io.open(f"{src}/sample.yml", encoding="utf-8").read()
    s = "\n".join(("  - uri: " + uri) if l.strip().startswith("- uri:") else l
                  for l in s.splitlines())
    io.open(f"{RUN}/sample.yml", "w", encoding="utf-8").write(s)
    o = io.open(f"{src}/output.yml", encoding="utf-8").read().replace("MINI", "FREQFIX")
    io.open(f"{RUN}/output.yml", "w", encoding="utf-8").write(o)
    shutil.copy(f"{src}/analysis.yml", f"{RUN}/analysis.yml")
    shutil.copy(f"{src}/application.properties", f"{RUN}/application.properties")
    r = subprocess.run(
        ["java", "-Xmx4g", "-jar", "exomiser-cli-14.1.0.jar",
         "--sample", f"../runs/FREQFIX/sample.yml",
         "--analysis", f"../runs/FREQFIX/analysis.yml",
         "--output", f"../runs/FREQFIX/output.yml",
         "--spring.config.location=../runs/FREQFIX/application.properties"],
        cwd=os.path.abspath(HOME), capture_output=True, text=True)
    return r.returncode


def recovered_frequencies():
    """(chrom, pos) -> frecuencia maxima, desde el JSON de Exomiser."""
    f = glob.glob(f"{RUN}/*.json")
    if not f:
        return {}
    out = {}
    for g in json.load(io.open(f[0], encoding="utf-8")):
        for ve in g.get("variantEvaluations", []):
            fr = ve.get("frequencyData", {}).get("frequencies", [])
            if not fr:
                continue
            mx = max(x["frequency"] for x in fr)
            out[(str(ve.get("contigName")), int(ve.get("start")))] = mx / 100.0
    return out


def main():
    rows = load(ANN, patient_vcf())
    miss = missing_freq(rows)
    print(f"  alelos sin MAX_AF a reparar: {len(miss)}")

    n = write_mini_vcf(miss, f"{RUN}/missing.vcf")
    print(f"  VCF minimo: {n} registros")
    rc = run_exomiser(f"{RUN}/missing.vcf")
    print(f"  Exomiser rc={rc}")

    freq = recovered_frequencies()
    print(f"  frecuencias recuperadas: {len(freq)} sitios\n")

    # --- se aplica a TODOS los que se pudo recuperar, no a una seleccion ---
    patched = 0
    for v in rows:
        if v.max_af is not None:
            continue
        base = int(v.loc.split(":")[1].split("-")[0])
        for d in (0, -1, -2):
            if (v.chrom, base + d) in freq:
                v.max_af = freq[(v.chrom, base + d)]
                patched += 1
                break
    print(f"  filas con frecuencia inyectada: {patched}")

    def a0(calls):
        out = []
        for c in calls:
            s = c.score
            has = any("pathogenic" in (x.clinsig or "").lower()
                      and "conflicting" not in (x.clinsig or "").lower() for x in c.variants)
            if has:
                s -= 5.0
            out.append((s, c.gene, c.model))
        return sorted(out, key=lambda t: (-t[0], t[1]))

    res = a0(rank(rows, male=True))
    print(f"\n  === A0-FREQFIX · SENSIBILIDAD (NO sustituye a A0) ===\n")
    for i, (s, g, m) in enumerate(res[:8], 1):
        mark = "  <<<" if g == "BUB1B" else ""
        print(f"    {i:>2}  {g:<12}{s:6.2f}  {m[:44]}{mark}")
    r = next((i for i, (_, g, _) in enumerate(res, 1) if g == "BUB1B"), None)
    print(f"\n  BUB1B en A0 congelado : puesto 4")
    print(f"  BUB1B en A0-FREQFIX   : puesto {r}")
    print(f"\n  Los DOS numeros se reportan. A0 sigue siendo el resultado preregistrado.")


if __name__ == "__main__":
    main()
