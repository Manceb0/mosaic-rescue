#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-006 · ejecuta los QUINCE analisis congelados en config/phenotype_v2.yaml
con la correccion v3: comparacion a nivel de MODELO DE ENFERMEDAD.

Nada se ajusta despues de ver los resultados.
"""
import sys, io, pickle, collections
sys.path.insert(0, ".")
sys.setrecursionlimit(50000)
from src.phenotype.semantic import score_genes
from src.prioritization.genome_wide import load, rank

# --- los 8 terminos, tomados del documento clinico (config/phenotype_v2.yaml) ---
PROBAND = {
    "HP:0002859": ("Rhabdomyosarcoma", "tumor"),
    "HP:0000121": ("Nephrocalcinosis", "renal"),
    "HP:0004322": ("Short stature", "growth"),
    "HP:0001508": ("Failure to thrive", "growth"),
    "HP:0003202": ("Skeletal muscle atrophy", "muscle"),
    "HP:0001622": ("Premature birth", "perinatal"),
    "HP:0001518": ("Small for gestational age", "perinatal"),
}
FAMILY = {"HP:0200067": ("Recurrent spontaneous abortion", "family")}

ANALYSES = [
    ("A0_GENETICS",               None,                                    False, 0.0),
    ("A1_GENETICS_CLINVAR",       None,                                    True,  0.0),
    ("B0_FULL_PROBAND",           set(PROBAND),                            True,  0.0),
    ("B1_MINUS_RHABDOMYOSARCOMA", set(PROBAND) - {"HP:0002859"},           True,  0.0),
    ("B2_MINUS_RENAL",            set(PROBAND) - {"HP:0000121"},           True,  0.0),
    ("B3_MINUS_GROWTH_PERINATAL", set(PROBAND) - {"HP:0004322", "HP:0001508",
                                                  "HP:0001622", "HP:0001518"}, True, 0.0),
    ("B4_GENETICS_ONLY_CONTROL",  None,                                    True,  0.0),
    ("FH_ON",                     set(PROBAND),                            True,  0.3),
] + [(f"LOO_{t.replace(':', '_')}", set(PROBAND) - {t}, True, 0.0) for t in PROBAND]

PREP = pickle.load(io.open("work/hpo/prepared.pkl", "rb"))
parents, ic = PREP["parents"], PREP["ic"]

# --- v4: SOLO relaciones causales establecidas ---
from src.phenotype.relationships import causal_pairs, disease_inheritance, genotype_compatible
CAUSAL, DROPPED = causal_pairs()
INHERIT = disease_inheritance()
_all = PREP["models"]
models = [m for m in _all if (m.gene, m.disease_id) in CAUSAL]

# Tabla de contingencia SOBRE EL UNIVERSO QUE USA EL MODO B, con asercion.
# Antes se imprimian los conteos de genes_to_disease.txt como si fueran la resta
# de estos modelos: dos tablas distintas presentadas como una sola operacion.
import collections as _c
_types = _c.Counter()
for m in _all:
    _types["MENDELIAN" if (m.gene, m.disease_id) in CAUSAL else "no causal"] += 1
assert sum(_types.values()) == len(_all), "los tipos no suman el total"
print(f"  modelos con anotacion HPO : {len(_all):,}")
for k, v in _types.most_common():
    print(f"    {k:<22} {v:>7,}")
print(f"  -> se conservan {len(models):,} causales; se eliminan {len(_all)-len(models):,}")

rows = load("work/gw/highmod_ann.tsv",
            "C:/Users/USUARIO/Downloads/[REDACTED]_[REDACTED].vcf.gz")

# --- puntuacion genetica, con y sin ClinVar ---
def genetics(with_clinvar: bool):
    calls = rank(rows, male=True)
    out = {}
    for c in calls:
        s = c.score
        if not with_clinvar:
            has = any("pathogenic" in (v.clinsig or "").lower()
                      and "conflicting" not in (v.clinsig or "").lower() for v in c.variants)
            if has:
                s -= 5.0
        out[c.gene] = (s, c.model)
    return out

GEN_CV = genetics(True)
GEN_NO = genetics(False)

# cache de fenotipo: una vez por conjunto de terminos
pheno_cache = {}
def pheno(terms):
    key = frozenset(terms)
    if key not in pheno_cache:
        pheno_cache[key] = score_genes(list(terms), models, ic, parents)
    return pheno_cache[key]

FAM = pheno(set(FAMILY))

results = {}
for name, terms, clinvar, fhw in ANALYSES:
    base = GEN_CV if clinvar else GEN_NO
    ph = pheno(terms) if terms else {}
    scored = []
    for g, (gs, model) in base.items():
        p = ph.get(g, {})
        f = FAM.get(g, {})
        dis = p.get("disease")
        compat, why = genotype_compatible(model, INHERIT.get(dis, set())) if dis else (None, "sin modelo")
        # un modelo INCOMPATIBLE no aporta soporte fenotipico
        ph_score = 0.0 if compat == "INCOMPATIBLE" else p.get("score", 0.0)
        total = gs + 1.0 * ph_score + fhw * f.get("score", 0.0)
        scored.append((g, total, model, dis, p.get("n_models_tested", 0),
                       round(ph_score, 3), compat, why))
    scored.sort(key=lambda x: (-x[1], x[0]))
    results[name] = scored
    print(f"  {name:<28} listo   top: {', '.join(s[0] for s in scored[:3])}")

pickle.dump(results, io.open("work/gw/mode_b_results_v4.pkl", "wb"))
print(f"\n  {len(ANALYSES)} analisis -> work/gw/mode_b_results_v4.pkl")
