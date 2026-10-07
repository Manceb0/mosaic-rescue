#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el CSV de predicciones de Track 1, FUERA del repositorio.

    python src/submission/track1_csv.py

POR QUE ES UN GENERADOR Y NO UN FICHERO VERSIONADO
    El formato oficial exige `chrom`, `pos`, `ref`, `alt` y el identificador del
    probando. Eso son coordenadas y alelos de un menor vivo: exactamente lo que
    `CLAUDE.md` Regla Dura 1 prohibe commitear, aunque sea temporalmente. El CSV
    se escribe en `work/submission/`, que esta en .gitignore, y se sube a mano a
    la plataforma. El repositorio conserva el METODO, no el dato.

    Consecuencia practica: este fichero es el unico sitio donde vive la logica
    de la entrega, y se puede auditar sin ver ni una coordenada.

FORMATO (columnas exactas y en este orden, segun la plataforma)
    proband_id, chrom_1, pos_1, ref_1, alt_1, chrom_2, pos_2, ref_2, alt_2,
    epcr, finding_type, notes

    - hasta 10 filas
    - una fila puede ser una variante suelta o una PAREJA heterocigota compuesta
    - `epcr` en (0, 1], probabilidad estimada de relacion causal
    - `finding_type`: `primary` o `secondary`

QUE SE ENVIA Y POR QUE
    Dos filas. Ni una mas. Se podrian mandar diez, y anadir los competidores ya
    auditados seria cubrirse las espaldas contra nuestro propio analisis: los
    cinco se resolvieron NEGATIVE con evidencia (EXP-020, EXP-021, EXP-022).
    Mandarlos igualmente diria que no nos creemos nuestras propias auditorias.

    fila 1  BUB1B, pareja heterocigota compuesta  ->  primary
    fila 2  LZTR1, variante suelta                ->  secondary

DE DONDE SALE EL `epcr`, QUE NO ES UN NUMERO INVENTADO
    Es una probabilidad subjetiva declarada, no una salida de modelo. La regla
    esta escrita abajo en EPCR_RATIONALE para que se pueda discutir en vez de
    tener que confiar. **Es un punto de decision humana**: el mantenedor puede
    cambiarla, y deberia mirarla antes de enviar.
"""
from __future__ import annotations
import csv, gzip, io, os, sys

sys.path.insert(0, ".")
from src.prioritization.genome_wide import load                        # noqa: E402
from src.paths import patient_vcf                                      # noqa: E402

# ---------------------------------------------------------------------------
# EL IDENTIFICADOR DE LA PLATAFORMA, QUE NO ES EL NOMBRE DE MUESTRA DEL VCF.
#
# Este generador leia el nombre de muestra de la cabecera del VCF y lo escribia
# en la columna `proband_id`. Es lo natural para una herramienta general y aqui
# esta MAL: el nombre de muestra viene de los ficheros genomicos oficiales,
# mientras la plataforma keyea su ground truth por OTRO identificador y rechaza
# cualquier otro valor. El mensaje del evaluador es explicito:
#
#     Unknown proband_id '{...}'. Only PROBAND01 is accepted in this challenge.
#
# Verificado el 2026-09-04 en el codigo publicado del Space
# SageBio/rare-disease-real-kid-mva-hackathon-2026: `groundtruth.py` keyea el
# ground truth por "PROBAND01" y `tabs/submit_track1.py` emite ese error.
#
# Nombre de muestra e identificador de submission son OBJETOS DISTINTOS.
# Confundirlos cuesta uno de los seis intentos, y el fallo no habria dado un
# error de formato sino cero puntos silenciosos, que es peor.
SUBMISSION_PROBAND_ID = "PROBAND01"

OUT_DIR = "work/submission"
OUT = os.path.join(OUT_DIR, "track1_predictions.csv")
ANN = "work/gw/highmod_ann.tsv"

COLUMNS = ["proband_id", "chrom_1", "pos_1", "ref_1", "alt_1",
           "chrom_2", "pos_2", "ref_2", "alt_2",
           "epcr", "finding_type", "notes"]

EPCR_RATIONALE = {
    "BUB1B": (0.75, """A favor (lineas de analisis distintas sobre el MISMO VCF, no replicas biologicas):
      - #1 en 14 de los 15 analisis de priorizacion; en el A0 CONGELADO queda #4,
        y los tres que lo superaban se resolvieron como polimorfismos comunes con
        rsID (EXP-021). En la sensibilidad A0-FREQFIX vuelve al #1.
      - metodo EXTERNO sobre el mismo VCF (Exomiser; no es evidencia biologica independiente) lo situa #2 de 398 GENES
        DISTINTOS, modelo autosomico recesivo, en las dos corridas. Las 470 filas
        de la salida son pares gen x modelo de herencia, no genes: contar 470
        inflaba el denominador un 18 % y contaba BUB1B dos veces.
      - mecanismo y herencia compatibles con MVA1 (OMIM 257300).
      - los cuatro competidores restantes auditados y NEGATIVE (EXP-020, EXP-022).
      - el alelo truncante alcanza Likely Pathogenic en curacion de investigacion.
    En contra, y por esto no sube mas:
      - LA FASE NO ESTA RESUELTA. Sin genotipos parentales, PM3 esta bloqueado y
        la configuracion bialelica es CANDIDATA, no demostrada.
      - la missense sigue siendo VUS: no hay ensayo funcional de abundancia.
      - la busqueda estructural con lecturas cortas (GO 2B) no emitio CNV
        (CNVpytor) ni MEI (xTea, SCRAMble) sobre el cuerpo del gen, pero una
        insercion compleja intronica NO queda excluida (EXP-012, EXP-012b)."""),
    "LZTR1": (0.05, """Candidato secundario/incidental DE INVESTIGACION, no causa
      propuesta del fenotipo MVA y NO un hallazgo clinico devolvible.
      - es una parada prematura en el transcrito MANE, heterocigota, de alta
        calidad, rara y clasificada patogenica/probablemente patogenica en ClinVar:
        no es un artefacto.
      - pero la forma sindromica de LZTR1 es RECESIVA y exige dos alelos; solo hay
        uno. Y lo que si produce un LoF heterocigoto, schwannomatosis de inicio
        adulto, no genera aneuploidia variegada ni explica el rabdomiosarcoma.
      - epcr bajo justamente porque se declara la probabilidad de relacion CAUSAL
        con el fenotipo consultado, que se estima pequena. Se envia porque es real
        y porque el formato tiene una casilla para eso (EXP-022)."""),
}

NOTES = {
    "BUB1B": ("Compound-heterozygous candidate in BUB1B (MVA1, OMIM 257300): truncating "
              "allele + missense. Phase UNRESOLVED, no parental samples, so PM3 is blocked "
              "and biallelic configuration is candidate, not demonstrated. Panel-free "
              "genome-wide search; frozen preregistered ranking A0 places it #4 and the "
              "A0-FREQFIX sensitivity #1, both reported. External baseline Exomiser ranks "
              "it #2 of 398 distinct genes, AR model. Short-read SV search: no CNV or MEI call "
              "overlaps the gene body; a complex intronic insertion is not excluded."),
    "LZTR1": ("Research secondary/incidental candidate, NOT proposed as the cause of the "
              "reported phenotype and NOT a returnable clinical finding. Heterozygous "
              "nonsense on the MANE transcript, ClinVar pathogenic/likely pathogenic. "
              "LZTR1 syndromic disease is recessive and only one allele is present; "
              "heterozygous LoF associates with adult-onset schwannomatosis, which does "
              "not produce variegated aneuploidy. Requires independent clinical "
              "confirmation and appropriate return-of-results handling. No clinical "
              "recommendation is made."),
}


def vcf_sample_name() -> str:
    """El nombre de MUESTRA de la cabecera del VCF.

    NO es lo que va en la columna `proband_id` del CSV: ese campo lo define la
    plataforma y solo acepta SUBMISSION_PROBAND_ID. Esta funcion se conserva
    porque el nombre de muestra sirve de comprobacion cruzada al operador -- si
    algun dia no coincide con el fichero que se cree estar usando, es que se
    esta generando la submission desde otro VCF.
    """
    with gzip.open(patient_vcf(), "rt", errors="replace") as f:
        for line in f:
            if line.startswith("#CHROM"):
                p = line.rstrip("\n").split("\t")
                return p[9] if len(p) > 9 else "PROBAND"
            if not line.startswith("#"):
                break
    return "PROBAND"


def ref_alt(keys):
    """REF y ALT crudos del VCF para las posiciones dadas.

    El objeto Variant lleva los campos de VEP (`Location`, `Allele`), y `Allele`
    es la forma normalizada de VEP, que para indels NO coincide con el par
    REF/ALT del VCF. La plataforma pide el par del VCF, asi que se lee de ahi.
    """
    want = set(keys)
    found = {}
    with gzip.open(patient_vcf(), "rt", errors="replace") as f:
        for line in f:
            if line[0] == "#":
                continue
            p = line.split("	", 5)
            k = (p[0], int(p[1]))
            if k in want:
                found[k] = (p[3], p[4].split(",")[0])
                if len(found) == len(want):
                    break
    missing = want - set(found)
    assert not missing, f"posiciones no encontradas en el VCF: {len(missing)}"
    return found


def pick(rows, gene: str):
    v = [x for x in rows if x.gene == gene and x.enters_ranking]
    # orden estable: el truncante primero, luego la missense
    rank = {"HIGH": 0, "MODERATE": 1, "LOW": 2, "MODIFIER": 3}
    return sorted(v, key=lambda x: (rank.get(x.impact, 9), x.chrom, x.pos))


def chrom(c: str) -> str:
    return c if str(c).startswith("chr") else "chr" + str(c)


def main() -> int:
    rows = load(ANN, patient_vcf())
    pid = SUBMISSION_PROBAND_ID
    bub, lz = pick(rows, "BUB1B"), pick(rows, "LZTR1")

    assert len(bub) == 2, f"se esperaban 2 alelos de BUB1B, hay {len(bub)}"
    assert len(lz) == 1, f"se esperaba 1 alelo de LZTR1, hay {len(lz)}"

    RA = ref_alt([(x.chrom, x.pos) for x in bub + lz])

    out = []
    a, b = bub
    ra_a, ra_b = RA[(a.chrom, a.pos)], RA[(b.chrom, b.pos)]
    out.append({
        "proband_id": pid,
        "chrom_1": chrom(a.chrom), "pos_1": a.pos, "ref_1": ra_a[0], "alt_1": ra_a[1],
        "chrom_2": chrom(b.chrom), "pos_2": b.pos, "ref_2": ra_b[0], "alt_2": ra_b[1],
        "epcr": EPCR_RATIONALE["BUB1B"][0], "finding_type": "primary",
        "notes": NOTES["BUB1B"],
    })
    c = lz[0]
    ra_c = RA[(c.chrom, c.pos)]
    out.append({
        "proband_id": pid,
        "chrom_1": chrom(c.chrom), "pos_1": c.pos, "ref_1": ra_c[0], "alt_1": ra_c[1],
        "chrom_2": "", "pos_2": "", "ref_2": "", "alt_2": "",
        "epcr": EPCR_RATIONALE["LZTR1"][0], "finding_type": "secondary",
        "notes": NOTES["LZTR1"],
    })

    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out)

    # Salida SANEADA a proposito: ni una coordenada, ni un alelo, ni el
    # identificador del probando. Esta consola acaba en transcripciones y logs.
    print(f"escrito {OUT}  ({len(out)} filas, {len(COLUMNS)} columnas)")
    print()
    print(f"  {'gen':<10}{'tipo':<12}{'epcr':>6}  {'cigosidad':<10}consecuencias")
    print("  " + "-" * 72)
    print(f"  {'BUB1B':<10}{'primary':<12}{EPCR_RATIONALE['BUB1B'][0]:>6}  "
          f"{a.gt + ' + ' + b.gt:<10}{a.consequence} + {b.consequence}")
    print(f"  {'LZTR1':<10}{'secondary':<12}{EPCR_RATIONALE['LZTR1'][0]:>6}  "
          f"{c.gt:<10}{c.consequence}")
    print()
    print(f"  proband_id enviado : {SUBMISSION_PROBAND_ID}   <- lo exige la plataforma")
    print(f"  nombre de muestra  : {vcf_sample_name()}   <- del VCF, NO se envia")
    print()
    print("  El CSV lleva coordenadas y alelos reales y por eso vive en work/,")
    print("  que esta en .gitignore. NO se commitea. Se sube a mano.")
    print()
    print("  REVISION HUMANA PENDIENTE: el `epcr` es una probabilidad subjetiva")
    print("  declarada, no una salida de modelo. Su justificacion esta en")
    print("  EPCR_RATIONALE, dentro de este fichero. Miralo antes de enviar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
