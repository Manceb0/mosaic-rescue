#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida el CSV de Track 1 ANTES de gastar uno de los seis envios.

    python src/submission/validate_track1.py [ruta.csv]

Comprueba, contra las instrucciones publicadas de la plataforma (28 ago 2026):

    - columnas exactas y en orden; como mucho 10 filas
    - `proband_id` == PROBAND01 (el unico que acepta el evaluador)
    - cromosomas con prefijo `chr`, posiciones enteras positivas, alelos ACGT
    - pareja heterocigota compuesta completa o vacia (las cuatro columnas `_2`)
    - `epcr` en (0, 1]; `finding_type` en {primary, secondary}; ninguna fila duplicada
    - el REF de cada variante coincide con GRCh38 (FASTA local de la cache de VEP)
    - el ranking por `epcr` es estricto entre filas `primary` (sin empates ambiguos)
    - el nombre de fichero lleva equipo y enfoque, como piden las instrucciones

La salida esta SANEADA: nunca imprime una coordenada, un alelo ni un identificador
de muestra. Solo dice que comprobacion pasa y cual falla.
"""
from __future__ import annotations
import csv, os, re, sys

sys.path.insert(0, ".")

COLUMNS = ["proband_id", "chrom_1", "pos_1", "ref_1", "alt_1", "chrom_2", "pos_2", "ref_2", "alt_2",
           "epcr", "finding_type", "notes"]
FASTA = "work/vep_cache/homo_sapiens/116_GRCh38/Homo_sapiens.GRCh38.dna.toplevel.fa.gz"


def main(path: str) -> int:
    errs, warns = [], []
    with open(path, encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh)
        header = next(rd)
        rows = [r for r in rd if any(x.strip() for x in r)]
    if header != COLUMNS:
        errs.append("las columnas no coinciden con la plantilla oficial (nombre u orden)")
    if not 1 <= len(rows) <= 10:
        errs.append(f"{len(rows)} filas: la plataforma acepta de 1 a 10")
    D = [dict(zip(COLUMNS, r)) for r in rows]
    fetch = None
    if os.path.exists(FASTA):
        from src.model_outputs.alphagenome_common import fasta_fetch
        fetch = lambda c, p, n: fasta_fetch(FASTA, c.removeprefix("chr"), p, p + n - 1).upper()
    else:
        warns.append("FASTA GRCh38 local no disponible: REF no verificado contra la referencia")
    seen = set()
    for i, r in enumerate(D, 1):
        if len(rows[i - 1]) != len(COLUMNS):
            errs.append(f"fila {i}: numero de campos incorrecto"); continue
        if r["proband_id"] != "PROBAND01":
            errs.append(f"fila {i}: proband_id no es PROBAND01")
        sides = [("1", True), ("2", False)]
        for s, required in sides:
            vals = [r[f"chrom_{s}"], r[f"pos_{s}"], r[f"ref_{s}"], r[f"alt_{s}"]]
            if not any(vals) and not required:
                continue
            if not all(vals):
                errs.append(f"fila {i}: variante {s} incompleta"); continue
            if not re.fullmatch(r"chr([1-9]|1[0-9]|2[0-2]|X|Y|M)", r[f"chrom_{s}"]):
                errs.append(f"fila {i}: chrom_{s} sin formato chrN")
            if not re.fullmatch(r"[1-9][0-9]*", r[f"pos_{s}"]):
                errs.append(f"fila {i}: pos_{s} no es un entero positivo")
            for a in ("ref", "alt"):
                if not re.fullmatch(r"[ACGT]+", r[f"{a}_{s}"]):
                    errs.append(f"fila {i}: {a}_{s} no es una secuencia ACGT")
            if fetch and re.fullmatch(r"[1-9][0-9]*", r[f"pos_{s}"]):
                ok = fetch(r[f"chrom_{s}"], int(r[f"pos_{s}"]), len(r[f"ref_{s}"])) == r[f"ref_{s}"]
                (None if ok else errs.append(f"fila {i}: ref_{s} NO coincide con GRCh38"))
                print(f"  fila {i} variante {s}: REF vs GRCh38 {'OK' if ok else 'FALLA'}")
        try:
            e = float(r["epcr"])
            if not 0 < e <= 1:
                errs.append(f"fila {i}: epcr fuera de (0, 1]")
        except ValueError:
            errs.append(f"fila {i}: epcr no es numerico")
        if r["finding_type"] not in ("primary", "secondary"):
            errs.append(f"fila {i}: finding_type debe ser primary o secondary")
        key = tuple(r[c] for c in COLUMNS[1:9])
        if key in seen:
            errs.append(f"fila {i}: duplicada")
        seen.add(key)
        if len(r["notes"]) > 800:
            warns.append(f"fila {i}: notes largas ({len(r['notes'])} caracteres)")
    prim = sorted(float(r["epcr"]) for r in D if r["finding_type"] == "primary")
    if len(prim) != len(set(prim)):
        warns.append("empates de epcr entre filas primary: el orden entre ellas queda ambiguo")
    if not any(r["finding_type"] == "primary" for r in D):
        errs.append("ninguna fila primary")
    base = os.path.basename(path)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*_[A-Za-z0-9._-]+\.csv", base) or base.startswith("track1_predictions"):
        warns.append("el nombre de fichero deberia ser <equipo>_<enfoque>.csv (instrucciones oficiales)")
    print(f"\n{len(rows)} filas · {sum(r['finding_type'] == 'primary' for r in D)} primary · "
          f"{sum(bool(r['chrom_2']) for r in D)} pareja(s) heterocigota(s) compuesta(s)")
    for w in warns:
        print("  AVISO ", w)
    for e in errs:
        print("  ERROR ", e)
    print("\nVALIDO para subir" if not errs else "\nNO SUBIR: corregir los errores")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "work/submission/track1_predictions.csv"))
