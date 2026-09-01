#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-011b · asignacion de clados para la robustez filogenetica.

POR QUE HACE FALTA
    Los 120 ortologos alineados NO son 120 observaciones independientes. Ensembl
    muestrea densamente mamiferos y primates; un 119/120 agregado puede estar
    sostenido por un solo linaje sobremuestreado. La pregunta correcta no es
    "cuantos", sino "sobrevive fuera de mamiferos".

POR QUE NO SE USA `taxonomy_level` DE LA PROPIA HOMOLOGIA
    Ese campo es el NODO DE DIVERGENCIA con el humano, no el clado de la especie.
    Aves, reptiles, anfibios y peces con aleta radiada caen todos en
    "Gnathostomata" (62 de 153). Inservible para lo que se pregunta.

QUE SE HACE EN SU LUGAR
    Se pide a Ensembl la clasificacion taxonomica real de cada `taxon_id` y se
    asigna el clado buscando en el linaje, de mas especifico a mas general. El
    orden de las reglas importa: un primate tambien es Mammalia.

NO se construye un arbol filogenetico ni se pondera por distancia. El objetivo
es unicamente comprobar si el resultado sobrevive fuera de los linajes
densamente muestreados.
"""
from __future__ import annotations
import io, os, json, time, urllib.request, urllib.error

URL = "https://rest.ensembl.org/taxonomy/classification/{tid}?content-type=application/json"

# De MAS especifico a MAS general. La primera regla que casa, gana.
RULES = [
    ("primates",            ("Primates",)),
    ("otros mamiferos",     ("Mammalia",)),
    ("aves",                ("Aves",)),
    ("reptiles",            ("Lepidosauria", "Testudines", "Crocodylia", "Archosauria")),
    ("anfibios",            ("Amphibia",)),
    ("peces con aleta radiada", ("Actinopterygii", "Actinopteri")),
    ("peces cartilaginosos", ("Chondrichthyes",)),
    ("vertebrados basales", ("Cyclostomata", "Hyperoartia", "Myxini", "Coelacanthimorpha",
                             "Dipnoi", "Sarcopterygii")),
]

ORDER = ["primates", "otros mamiferos", "aves", "reptiles", "anfibios",
         "peces con aleta radiada", "peces cartilaginosos", "vertebrados basales",
         "sin clasificar"]


def fetch_lineages(taxon_ids, cache_path: str, pause: float = 0.08) -> dict:
    """taxon_id -> lista de nombres del linaje. Cacheado: reejecutar no vuelve a
    pedir nada, para que el analisis no dependa del servicio ni cambie solo."""
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(io.open(cache_path, encoding="utf-8"))
    missing = [str(t) for t in taxon_ids if str(t) not in cache]
    for j, tid in enumerate(missing):
        try:
            req = urllib.request.Request(URL.format(tid=tid),
                                         headers={"User-Agent": "mosaic-rescue/EXP-011b"})
            with urllib.request.urlopen(req, timeout=60) as r:
                cache[tid] = [n.get("name") for n in json.load(r)]
        except (urllib.error.URLError, ValueError, TimeoutError) as e:
            cache[tid] = []                       # se marca vacio, no se inventa
            print(f"    aviso: taxon {tid} sin clasificacion ({e.__class__.__name__})")
        time.sleep(pause)
    if missing:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        json.dump(cache, io.open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
    return cache


def clade_of(lineage) -> str:
    names = set(lineage or ())
    for clade, keys in RULES:
        if names & set(keys):
            return clade
    return "sin clasificar"
