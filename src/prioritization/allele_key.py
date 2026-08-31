#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identidad exacta de alelo entre VEP y el VCF.

MOTIVO. La v1 cruzaba por (chrom, pos) exacto y perdia 466 posiciones, 228 de
alto impacto incluidos 157 frameshifts, porque VEP normaliza indels a la
izquierda. La v2 lo "arreglo" con tolerancia +-1, y eso es peor de lo que
parece: dos indels vecinos pueden emparejarse mal. La proximidad NO es una
clave de union aceptable.

v3: identidad exacta. `Uploaded_variation` de VEP conserva la representacion de
ENTRADA, asi que hay dos formas y las dos son exactas:

  - ID del VCF = "."  -> Uploaded_variation es `chrom_pos_ref/alt` ORIGINAL
  - ID del VCF = rsID -> Uploaded_variation es ese mismo rsID

Ninguna de las dos usa distancias.
"""
from __future__ import annotations
import re

# chrom_pos_ref/alt , con chrom que puede llevar puntos (contigs decoy)
_COORD = re.compile(r"^(?P<c>[\w.]+)_(?P<p>\d+)_(?P<r>[ACGTN*-]+)/(?P<a>[ACGTN*-]+)$")


def parse_uploaded(uploaded: str):
    """Devuelve ('coord', (chrom,pos,ref,alt)) o ('id', valor) o ('unparsed', valor).

    Nunca devuelve una posicion aproximada. Si no se puede identificar el alelo,
    se dice explicitamente en vez de adivinar.
    """
    m = _COORD.match(uploaded)
    if m:
        return "coord", (m.group("c"), int(m.group("p")), m.group("r"), m.group("a"))
    if uploaded and uploaded != "-":
        return "id", uploaded
    return "unparsed", uploaded


def vcf_keys(chrom: str, pos: str, vid: str, ref: str, alt_field: str):
    """Claves con las que un registro del VCF puede ser referenciado por VEP.

    Un sitio multialelico genera una clave por alelo alternativo: asi una
    variante no se pierde ni se duplica.
    """
    keys = set()
    for a in alt_field.split(","):
        keys.add(("coord", (chrom, int(pos), ref, a)))
    if vid and vid != ".":
        for one in vid.split(";"):
            keys.add(("id", one))
    return keys


def build_index(vcf_lines):
    """Indice clave -> registro del VCF. Sin tolerancias."""
    idx = {}
    for parts in vcf_lines:
        for k in vcf_keys(parts[0], parts[1], parts[2], parts[3], parts[4]):
            idx[k] = parts
    return idx


def join_report(wanted: set, resolved: set) -> dict:
    """Informe de recuperacion. Un join que no es uno a uno se declara."""
    missing = wanted - resolved
    return {
        "wanted": len(wanted),
        "resolved": len(resolved & wanted),
        "missing": len(missing),
        "one_to_one": len(missing) == 0,
        "missing_examples": sorted(missing)[:8],
    }
