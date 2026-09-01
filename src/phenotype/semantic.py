#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-006 modo B · similitud semantica HPO a nivel de MODELO DE ENFERMEDAD.

CORRECCION v3, y es la que mas importa. La v2 proponia unir todos los terminos
HPO de todas las enfermedades de un gen en un unico conjunto. Eso resuelve el
problema de "muchos modelos = muchos intentos" introduciendo uno peor: fabrica
una enfermedad Frankenstein que ningun modelo real tiene.

    Enfermedad A -> tumor + talla baja
    Enfermedad B -> nefrocalcinosis
    Enfermedad C -> atrofia muscular
    union        -> parece explicar un paciente multisistemico entero,
                    aunque ninguna enfermedad conocida de ese gen lo explique.

Con un fenotipo multisistemico como el de este caso, ese sesgo seria fatal.

v3: la comparacion primaria es POR ENFERMEDAD. Se conserva la relacion concreta
enfermedad -> gen -> herencia, y se reporta QUE modelo da el soporte fenotipico.
El resumen por gen usa el mejor modelo compatible, exponiendo siempre cuantos se
evaluaron. No se inventa ninguna penalizacion post-hoc por numero de modelos: se
reporta como posible sesgo de constatacion y se deja que el baseline externo
haga de comprobacion ortogonal.
"""
from __future__ import annotations
import io, math, collections
from dataclasses import dataclass


# ───────────────────────── ontologia ─────────────────────────

def load_ontology(obo_path: str):
    """Devuelve (padres, nombres). Solo relaciones `is_a` de terminos vigentes."""
    parents, names = collections.defaultdict(set), {}
    cur = None
    for line in io.open(obo_path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if line == "[Term]":
            cur = {"id": None, "parents": set(), "name": None, "obs": False}
        elif cur is not None:
            if line.startswith("id: HP:"):
                cur["id"] = line[4:]
            elif line.startswith("name: "):
                cur["name"] = line[6:]
            elif line.startswith("is_a: HP:"):
                cur["parents"].add(line[6:].split(" ")[0])
            elif line.startswith("is_obsolete: true"):
                cur["obs"] = True
            elif line == "" and cur.get("id"):
                if not cur["obs"]:
                    parents[cur["id"]] = cur["parents"]
                    names[cur["id"]] = cur["name"]
                cur = None
    return dict(parents), names


def ancestors(term: str, parents: dict, cache: dict) -> set:
    """Cierre transitivo `is_a`, incluyendo el propio termino."""
    if term in cache:
        return cache[term]
    out = {term}
    for p in parents.get(term, ()):
        out |= ancestors(p, parents, cache)
    cache[term] = out
    return out


# ─────────────────── modelos de enfermedad ───────────────────

@dataclass
class DiseaseModel:
    disease_id: str
    gene: str
    terms: frozenset          # propagados por ancestros
    n_raw: int                # terminos anotados antes de propagar


def load_disease_models(g2p_path: str, parents: dict):
    """(gene, disease_id) -> conjunto de terminos propagado.

    Se conserva la pareja enfermedad-gen. NO se unen enfermedades.
    """
    raw = collections.defaultdict(set)
    with io.open(g2p_path, encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
        ix = {k: i for i, k in enumerate(header)}
        for line in f:
            p = line.rstrip("\n").split("\t")
            try:
                raw[(p[ix["gene_symbol"]], p[ix["disease_id"]])].add(p[ix["hpo_id"]])
            except (IndexError, KeyError):
                continue
    cache = {}
    models = []
    for (gene, dis), terms in raw.items():
        prop = set()
        for t in terms:
            prop |= ancestors(t, parents, cache)
        models.append(DiseaseModel(dis, gene, frozenset(prop), len(terms)))
    return models


def information_content(models, parents) -> dict:
    """IC(t) = -log( genes anotados con t o descendiente / genes totales ).

    Corpus: el propio corpus gen-fenotipo. Como los conjuntos ya vienen
    propagados, contar apariciones equivale a contar t-o-descendiente.
    """
    genes_per_term = collections.defaultdict(set)
    all_genes = set()
    for m in models:
        all_genes.add(m.gene)
        for t in m.terms:
            genes_per_term[t].add(m.gene)
    n = len(all_genes) or 1
    return {t: -math.log(len(g) / n) for t, g in genes_per_term.items()}


# ───────────────────────── similitud ─────────────────────────

def resnik_bma(patient_terms, model_terms, ic: dict, parents: dict, cache: dict) -> float:
    """Best Match Average ASIMETRICA, direccion paciente -> modelo.

    Para cada termino del paciente se toma el IC del ancestro comun mas
    informativo con algun termino del modelo, y se promedia sobre los terminos
    del paciente.

    Asimetrica a proposito: la direccion inversa penalizaria a un modelo por
    rasgos que el paciente no tiene, y en este caso "no tiene" significa
    DESCONOCIDO, porque el documento clinico no declara ser exhaustivo.
    """
    if not patient_terms or not model_terms:
        return 0.0
    total = 0.0
    for pt in patient_terms:
        pa = ancestors(pt, parents, cache)
        best = 0.0
        for mt in model_terms:
            common = pa & ancestors(mt, parents, cache)
            if common:
                v = max(ic.get(c, 0.0) for c in common)
                if v > best:
                    best = v
        total += best
    return total / len(patient_terms)


def _pheno_cache_key(patient_terms, models):
    """Huella del conjunto de terminos Y del corpus de modelos.

    Si cambian los terminos o el corpus, la cache se invalida sola. Se usa el
    numero de modelos y un hash de sus identificadores: recorrer los conjuntos
    de terminos propagados seria mas caro que el propio calculo.
    """
    import hashlib
    h = hashlib.sha256()
    h.update(",".join(sorted(patient_terms)).encode())
    h.update(f"|{len(models)}|".encode())
    h.update(",".join(sorted(m.disease_id for m in models[:2000])).encode())
    return h.hexdigest()[:16]


def score_genes(patient_terms, models, ic, parents, use_cache=True):
    """Envoltorio con cache en disco. El calculo real esta en `_score_genes`.

    MOTIVO. Resnik+BMA sobre ~7 000 modelos y 8 conjuntos de terminos distintos
    domina el coste del modo B. El resultado es determinista dadas las entradas
    congeladas, asi que recalcularlo en cada sesion es puro gasto.
    """
    import io as _io, os, pickle
    if not use_cache:
        return _score_genes(patient_terms, models, ic, parents)
    d = "work/cache"
    path = os.path.join(d, f"pheno_{_pheno_cache_key(patient_terms, models)}.pkl")
    if os.path.exists(path):
        try:
            with _io.open(path, "rb") as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError):
            pass
    out = _score_genes(patient_terms, models, ic, parents)
    os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with _io.open(tmp, "wb") as f:
        pickle.dump(out, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmp, path)
    return out


def _score_genes(patient_terms, models, ic, parents):
    """Puntuacion por gen = MEJOR modelo de enfermedad, con trazabilidad.

    Devuelve, por gen: la puntuacion, que enfermedad la produce, y cuantos
    modelos se evaluaron — para que el sesgo por numero de modelos sea visible.
    """
    cache = {}
    by_gene = collections.defaultdict(list)
    for m in models:
        by_gene[m.gene].append(m)
    out = {}
    for gene, ms in by_gene.items():
        best_s, best_m = 0.0, None
        for m in ms:
            s = resnik_bma(patient_terms, m.terms, ic, parents, cache)
            if s > best_s:
                best_s, best_m = s, m
        out[gene] = {
            "score": best_s,
            "disease": best_m.disease_id if best_m else None,
            "n_models_tested": len(ms),        # sesgo de constatacion, visible
            "n_terms_best_model": best_m.n_raw if best_m else 0,
        }
    return out
