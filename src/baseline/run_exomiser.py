#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-006b · baseline externo independiente con Exomiser.

INDEPENDENCIA — lo que este script NO le pasa a Exomiser
    Ni nuestras 142 candidatas, ni la shortlist de BUB1B, ni nuestras
    puntuaciones, ni nuestros paneles, ni ningun gen candidato. Solo:
      · el VCF original completo        (ruta desde config/paths.yaml)
      · GRCh38
      · sexo masculino
      · los 7 terminos HPO del documento clinico
      · la base de conocimiento propia de Exomiser

    Si se le pasara cualquier otra cosa dejaria de ser una comprobacion
    independiente y no valdria como convergencia.

LOS TERMINOS SALEN DE LA FUENTE CONGELADA
    Se leen de `config/phenotype_v2.yaml`, no se reescriben aqui. Tener dos
    copias de la lista es la forma habitual de que se desincronicen.

INDEPENDENCIA PARCIAL, DECLARADA
    El preset de exoma de Exomiser usa REVEL y MVP como fuentes de
    patogenicidad. REVEL tambien intervino en nuestra decision de PP3, asi que
    en ese eje concreto los dos analisis comparten una entrada. Lo que SI es
    independiente: el motor de priorizacion, el emparejamiento fenotipico
    (hiPhive), la base de conocimiento y toda la logica de ranking.

DOS CORRIDAS, Y SOLO DOS (preregistradas en docs/DECISIONS.md)
    BASELINE-PRIMARY : los 7 terminos del probando
    BASELINE-FH      : los 7 + historia familiar, como sensibilidad
"""
from __future__ import annotations
import io, os, sys, subprocess, shutil

sys.path.insert(0, ".")
from src.paths import patient_vcf                                   # noqa: E402

HOME = "work/exomiser/exomiser-cli-14.1.0"
JAR = os.path.join(HOME, "exomiser-cli-14.1.0.jar")
# Barras NORMALES a proposito: en un fichero .properties de Java la barra
# invertida es un caracter de escape, asi que "C:\Users\..." se deserializa como
# "UsersUSUARIO..." y Jannovar no encuentra los datos.
DATA = os.path.abspath("work/exomiser/data").replace("\\", "/")
RUNS = "work/exomiser/runs"
XMX = "4g"          # la RAM es el recurso escaso. 4 GB bastan: la corrida real uso
                    # picos muy por debajo de 8 GB y el sistema tiene 16 GB en total.


def phenotype_terms():
    """(proband, family_history) desde la fuente congelada.

    NO se usa un parser YAML completo: `config/phenotype_v2.yaml` no es YAML
    valido — el bloque `analyses:` cierra con `total: 15` a la misma indentacion
    que los elementos de la lista, que es un error de sintaxis. El fichero esta
    CONGELADO, asi que no se corrige aqui; se lee el bloque que hace falta.
    El defecto queda anotado en docs/DECISIONS.md.
    """
    import re
    txt = io.open("config/phenotype_v2.yaml", encoding="utf-8").read()

    def block(name, end):
        # las claves llevan comentario en la misma linea, asi que no vale exigir fin de linea
        m = re.search(rf"^  {name}:.*?$(.*?)^  {end}:", txt, re.S | re.M)
        if not m:
            raise ValueError(f"no se encuentra el bloque '{name}' en phenotype_v2.yaml")
        return re.findall(r'-\s+id:\s*"(HP:\d+)"\s*\n\s*label:\s*"([^"]+)"', m.group(1))

    proband = block("proband", "family_history")
    family = block("family_history", "excluded_terms")
    if len(proband) != 7 or len(family) != 1:
        raise ValueError(f"esperados 7+1 terminos, leidos {len(proband)}+{len(family)}")
    return proband, family


def vcf_sample_name(vcf: str) -> str:
    """Nombre de muestra de la cabecera del VCF.

    Exomiser exige que el `subject.id` del phenopacket coincida con el nombre de
    muestra del VCF. Ese nombre ES el identificador real de la muestra, asi que
    NO se escribe en el codigo: se lee del fichero en tiempo de ejecucion. El
    sample.yml generado vive en work/ y nunca se commitea.
    """
    import gzip
    op = gzip.open if vcf.endswith(".gz") else io.open
    with op(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#CHROM"):
                cols = line.rstrip("\n").split("\t")
                if len(cols) < 10:
                    raise ValueError("el VCF no tiene columnas de muestra")
                return cols[9]
    raise ValueError("no se encontro la linea #CHROM en el VCF")


def write_sample(path: str, terms, vcf: str) -> None:
    # `htsFiles.uri` se parsea como URI, no como ruta: con "C:/Users/..." Java
    # toma "C" por esquema y falla con FileSystemNotFoundException.
    sample_id = vcf_sample_name(vcf)
    vcf = "file:///" + os.path.abspath(vcf).replace("\\", "/").lstrip("/")
    feats = "".join(f"  - type:\n      id: {i}\n      label: {l}\n" for i, l in terms)
    io.open(path, "w", encoding="utf-8").write(
        "# Generado por src/baseline/run_exomiser.py — NO editar a mano.\n"
        "# Los terminos vienen de config/phenotype_v2.yaml (congelado).\n"
        "---\n"
        f"id: {sample_id}\n"
        "subject:\n"
        f"  id: {sample_id}\n"
        "  sex: MALE\n"
        "phenotypicFeatures:\n" + feats +
        "htsFiles:\n"
        f"  - uri: {vcf}\n"
        "    htsFormat: VCF\n"
        "    genomeAssembly: hg38\n"
        "metaData:\n"
        "  createdBy: mosaic-rescue/EXP-006b\n"
        "  phenopacketSchemaVersion: 1.0\n")


def write_output_options(path: str, outdir: str, name: str) -> None:
    io.open(path, "w", encoding="utf-8").write(
        "---\n"
        "outputContributingVariantsOnly: false\n"
        "numGenes: 0                      # TODOS los genes: recortar arriba sesgaria la comparacion\n"
        f"outputDirectory: {outdir}\n"
        f"outputFileName: {name}\n"
        "outputFormats: [ TSV_GENE, TSV_VARIANT, JSON ]\n")


def write_properties(path: str) -> None:
    io.open(path, "w", encoding="utf-8").write(
        f"exomiser.data-directory={DATA}\n"
        "exomiser.hg38.data-version=2402\n"
        "exomiser.phenotype.data-version=2402\n"
        "logging.level.org.monarchinitiative.exomiser=INFO\n")


def run(name: str, terms) -> int:
    outdir = os.path.abspath(os.path.join(RUNS, name))
    os.makedirs(outdir, exist_ok=True)
    sample = os.path.join(outdir, "sample.yml")
    outopt = os.path.join(outdir, "output.yml")
    props = os.path.join(outdir, "application.properties")
    analysis = os.path.join(outdir, "analysis.yml")

    write_sample(sample, terms, patient_vcf())
    write_output_options(outopt, outdir, name)
    write_properties(props)
    # el preset de exoma corresponde al alcance que declaramos en EXP-006:
    # pasada codificante/de splicing, no genome-wide regulatorio
    shutil.copy(os.path.join(HOME, "examples/preset-exome-analysis.yml"), analysis)

    cmd = ["java", f"-Xmx{XMX}", "-jar", os.path.abspath(JAR),
           "--sample", sample, "--analysis", analysis, "--output", outopt,
           f"--spring.config.location={os.path.abspath(props)}"]
    print(f"\n  === {name} · {len(terms)} terminos HPO ===", flush=True)
    print("  " + " ".join(cmd[:6]) + " ...", flush=True)
    return subprocess.run(cmd, cwd=os.path.abspath(HOME)).returncode


if __name__ == "__main__":
    proband, family = phenotype_terms()
    print(f"  terminos del probando : {len(proband)}")
    print(f"  historia familiar     : {len(family)}")
    rc = run("BASELINE-PRIMARY", proband)
    if rc == 0:
        rc = run("BASELINE-FH", proband + family)
    sys.exit(rc)
