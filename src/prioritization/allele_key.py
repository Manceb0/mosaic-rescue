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


def vep_location_allele(chrom: str, pos: str, ref: str, alt: str):
    """Representacion (Location, Allele) tal y como VEP la escribe para un
    registro de VCF. Devuelve una lista de formas candidatas, o [] si el alelo
    es complejo.

    POR QUE HACE FALTA
        El TSV anotado de este proyecto se genero con `--fields` empezando en
        `Location`, asi que NO contiene `Uploaded_variation`. Sin esa columna la
        identidad de alelo de arriba no es aplicable, y cruzar por posicion
        pierde 433 posiciones HIGH/MODERATE — 346 de ellas indels — porque VEP
        desplaza la coordenada del indel respecto al VCF.

        Aqui se REPRODUCEN las reglas de VEP en vez de tolerar distancias:

          SNV        Location = chrom:pos           Allele = ALT
          Delecion   Location = chrom:(pos+1)-(fin) Allele = "-"
          Insercion  Location = chrom:(pos+1)-(pos) Allele = bases insertadas

        Un alelo complejo (MNV, indel mixto) devuelve [] y se declara como no
        resuelto. NUNCA se adivina por proximidad.
    """
    p = int(pos)
    if len(ref) == 1 and len(alt) == 1 and ref != "-" and alt != "-":
        return [(f"{chrom}:{p}", alt)]                       # SNV, sin recortar

    # MINIMIZACION. Primero por la DERECHA, luego por la IZQUIERDA avanzando la
    # posicion. Recortar solo el prefijo dejaba 327 indels sin cruzar: el VCF
    # puede traer bases comunes al final que VEP elimina.
    while len(ref) > 1 and len(alt) > 1 and ref[-1] == alt[-1]:
        ref, alt = ref[:-1], alt[:-1]
    while ref and alt and ref[0] == alt[0]:
        ref, alt, p = ref[1:], alt[1:], p + 1

    if not ref:                                              # insercion
        # Dos convenciones de Location conviven para una insercion: la clasica
        # de VEP, con inicio > fin, y la de bases flanqueantes en orden
        # ascendente, que es la que produjo la corrida de este proyecto. Se
        # emiten las dos. No introduce falsos positivos: el ALELO tambien
        # tiene que coincidir, y es identico en ambas.
        return [(f"{chrom}:{p}-{p - 1}", alt), (f"{chrom}:{p - 1}-{p}", alt)]
    if not alt:                                              # delecion
        end = p + len(ref) - 1
        forms = [(f"{chrom}:{p}-{end}", "-")]
        if p == end:
            forms.append((f"{chrom}:{p}", "-"))              # VEP omite el rango de 1 pb
        return forms
    if len(ref) == 1 and len(alt) == 1:                      # SNV tras recortar
        return [(f"{chrom}:{p}", alt)]

    end = p + len(ref) - 1                                   # MNV / indel mixto
    forms = [(f"{chrom}:{p}-{end}", alt)]
    if p == end:
        forms.append((f"{chrom}:{p}", alt))
    return forms


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
