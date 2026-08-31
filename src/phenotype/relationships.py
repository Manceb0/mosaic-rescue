#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tipo de relacion enfermedad-gen y compatibilidad de herencia.

MOTIVO. El modo B daba a SERPINA1 soporte fenotipico desde ORPHA:586, fibrosis
quistica. Esa NO es una relacion causal primaria: es de modificador. HPO publica
el tipo en genes_to_disease.txt, y estaba siendo ignorado:

    SERPINA1 -> ORPHA:586  UNKNOWN     <- modificador, contaminaba el ranking
    LZTR1    -> ORPHA:648  UNKNOWN     <- Noonan, misma contaminacion
    BUB1B    -> OMIM:257300 MENDELIAN  <- causal, se conserva

Y un buen emparejamiento de HPO no basta si el genotipo del paciente no encaja
con la herencia del modelo. Caso concreto: el candidato de LZTR1 es un LoF
heterocigoto, y las formas dominantes de Noonan por LZTR1 van por ganancia de
funcion mientras que el LoF es el mecanismo recesivo.
"""
import io, collections

INH = {"HP:0000006": "AD", "HP:0000007": "AR", "HP:0001417": "XL",
       "HP:0001419": "XLR", "HP:0001423": "XLD", "HP:0001427": "mitocondrial"}


def causal_pairs(path="work/hpo/genes_to_disease.txt", keep=("MENDELIAN",)):
    """Solo relaciones causales establecidas. Modificadores y susceptibilidad fuera.

    Un par puede declarar VARIOS tipos (hay uno MENDELIAN+POLYGENIC). Se acepta
    si ALGUNO de sus tipos es causal, en vez de exigir coincidencia exacta.
    """
    ok, dropped = set(), collections.Counter()
    with io.open(path, encoding="utf-8", errors="replace") as f:
        h = f.readline().rstrip("\n").split("\t")
        ix = {k: i for i, k in enumerate(h)}
        for line in f:
            p = line.rstrip("\n").split("\t")
            t = p[ix["association_type"]]
            if t in keep:
                ok.add((p[ix["gene_symbol"]], p[ix["disease_id"]]))
            else:
                dropped[t] += 1
    return ok, dropped


def disease_inheritance(path="work/hpo/phenotype.hpoa"):
    """Modo de herencia por enfermedad, de los terminos con aspecto 'I'."""
    out = collections.defaultdict(set)
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) > 3 and p[3] in INH:
                out[p[0]].add(INH[p[3]])
            elif len(p) > 2 and p[2] in INH:
                out[p[0]].add(INH[p[2]])
    return dict(out)


# Estados explicitos. "compatible" a secas convertia dos variantes candidatas
# en un caso recesivo resuelto, que es justo lo que no tenemos.
COMPATIBLE_CONFIRMED = "COMPATIBLE_CONFIRMED"   # fase demostrada y ambos alelos sostenidos
CANDIDATE_COMPATIBLE = "CANDIDATE_COMPATIBLE"   # encaja, pero causalidad bialelica NO establecida
INCOMPATIBLE         = "INCOMPATIBLE"
UNRESOLVED           = "UNRESOLVED"             # el modelo no declara herencia


def genotype_compatible(patient_model: str, inheritance: set):
    """Encaja el genotipo del paciente con la herencia del modelo?

    Devuelve (estado, motivo). Ningun estado afirma causalidad: el mas alto que
    se puede alcanzar sin fase demostrada es CANDIDATE_COMPATIBLE.
    """
    if not inheritance:
        return UNRESOLVED, "el modelo no declara herencia"
    m = patient_model.lower()
    two_alleles = ("homocigoto" in m) or ("compuesto" in m)
    hemi = "hemicigoto" in m
    single_het = ("heterocigoto" in m) and not two_alleles

    if two_alleles and "AR" in inheritance:
        # CANDIDATE, no CONFIRMED: sin fase no sabemos si estan en trans, y el
        # segundo alelo puede seguir siendo VUS. Dos variantes candidatas NO son
        # un caso recesivo resuelto.
        return CANDIDATE_COMPATIBLE, "dos alelos candidatos vs modelo recesivo · causalidad bialelica NO establecida"
    if hemi and ({"XLR", "XL"} & inheritance):
        return CANDIDATE_COMPATIBLE, "hemicigoto en varon vs recesivo ligado a X · un alelo basta, patogenicidad no establecida"
    if single_het and ({"AD", "XLD"} & inheritance):
        return CANDIDATE_COMPATIBLE, "un alelo vs modelo dominante · patogenicidad no establecida"
    if single_het and inheritance == {"AR"}:
        return INCOMPATIBLE, "UN alelo frente a modelo SOLO recesivo: falta el segundo"
    if two_alleles and inheritance == {"AD"}:
        return UNRESOLVED, "dos alelos frente a modelo solo dominante: posible, no esperado"
    return UNRESOLVED, f"herencia {'/'.join(sorted(inheritance))} sin regla clara"
