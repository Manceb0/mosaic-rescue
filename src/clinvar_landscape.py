#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cruza las variantes de ClinVar en BUB1B con su posicion proteica y evalua
PS1, PM5 y la base empirica de PM1 para un residuo candidato.

PS1: mismo cambio aminoacidico, distinto cambio nucleotidico, ya P/LP.
PM5: distinto cambio aminoacidico en el mismo residuo, P/LP.
PM1: exige enriquecimiento real de P/LP y escasez de B/LB en la region.

Salida agregada mas un fichero para la figura. No imprime el genotipo del
paciente: solo la posicion del residuo candidato, que es dato de la curacion.

Uso: python src/clinvar_landscape.py RESIDUO AA_REF AA_ALT
"""
import io, sys, collections, json

RES = int(sys.argv[1]) if len(sys.argv) > 1 else None
AAREF = sys.argv[2] if len(sys.argv) > 2 else None
AAALT = sys.argv[3] if len(sys.argv) > 3 else None

# --- CLNSIG desde el VCF de ClinVar ---
clnsig, clnrev = {}, {}
for line in io.open("work/clinvar/bub1b_clinvar.vcf", encoding="utf-8", errors="replace"):
    if line.startswith("#"):
        continue
    p = line.rstrip("\n").split("\t")
    info = dict(kv.split("=", 1) for kv in p[7].split(";") if "=" in kv)
    clnsig[p[2]] = info.get("CLNSIG", "").replace("_", " ")
    clnrev[p[2]] = info.get("CLNREVSTAT", "").replace("_", " ")

def bucket(sig):
    s = sig.lower()
    if "conflicting" in s:                      return "CONFLICTIVA"
    if "pathogenic" in s and "likely" in s:     return "P/LP"
    if s.startswith("pathogenic"):              return "P/LP"
    if "likely pathogenic" in s:                return "P/LP"
    if "benign" in s:                           return "B/LB"
    if "uncertain" in s:                        return "VUS"
    return "otra"

rows = []
with io.open("work/clinvar/clinvar_ann.tsv", encoding="utf-8", errors="replace") as f:
    ix = None
    for line in f:
        if line.startswith("##"):
            continue
        if line.startswith("#"):
            h = line[1:].rstrip("\n").split("\t"); ix = {k: i for i, k in enumerate(h)}; continue
        p = line.rstrip("\n").split("\t")
        vid = p[ix["Uploaded_variation"]]
        pp = p[ix["Protein_position"]]
        aa = p[ix["Amino_acids"]]
        con = p[ix["Consequence"]]
        sig = clnsig.get(vid, "")
        rows.append(dict(vid=vid, pp=pp, aa=aa, con=con, sig=sig,
                         cls=bucket(sig), rev=clnrev.get(vid, "")))

# --- panorama global ---
cnt = collections.Counter(r["cls"] for r in rows)
print("=" * 66)
print("BUBR1 — panorama de ClinVar en la region del gen")
print("=" * 66)
print(f"  variantes anotadas : {len(rows):,}")
for k, v in cnt.most_common():
    print(f"    {k:<14} {v:>6,}  ({100*v/len(rows):.1f} %)")

coding = [r for r in rows if r["pp"] not in ("-", "") and r["aa"] not in ("-", "")]
print(f"\n  con posicion proteica : {len(coding):,}")

# --- PS1 / PM5 sobre el residuo candidato ---
if RES:
    print(f"\n{'='*66}\nRESIDUO {RES} — evaluacion de PS1 y PM5\n{'='*66}")
    same = []
    for r in coding:
        try:
            pos = int(str(r["pp"]).split("-")[0].split("/")[0])
        except ValueError:
            continue
        if pos == RES:
            same.append(r)
    if not same:
        print(f"  ClinVar NO tiene ninguna variante anotada en el residuo {RES}")
        print("  -> PS1: no aplica.   PM5: no aplica.")
    else:
        print(f"  {len(same)} variante(s) de ClinVar en este residuo:")
        for r in same:
            print(f"    {r['aa']:<10} {r['cls']:<12} {r['sig'][:44]}")
        ps1 = [r for r in same if r["cls"] == "P/LP" and r["aa"].replace("/", "") == f"{AAREF}{AAALT}"]
        pm5 = [r for r in same if r["cls"] == "P/LP" and r["aa"].replace("/", "") != f"{AAREF}{AAALT}"]
        print(f"\n  PS1 (mismo cambio aa, ya P/LP) : {'SI — ' + str(len(ps1)) if ps1 else 'no'}")
        print(f"  PM5 (otro cambio aa, P/LP)     : {'SI — ' + str(len(pm5)) if pm5 else 'no'}")

# --- base empirica de PM1: distribucion por ventanas ---
print(f"\n{'='*66}\nPM1 — distribucion por ventanas de 100 residuos\n{'='*66}")
win = collections.defaultdict(lambda: collections.Counter())
for r in coding:
    try:
        pos = int(str(r["pp"]).split("-")[0].split("/")[0])
    except ValueError:
        continue
    win[pos // 100 * 100][r["cls"]] += 1
print(f"  {'residuos':<14}{'P/LP':>6}{'B/LB':>7}{'VUS':>7}{'confl.':>8}   ratio P/LP:B/LB")
for w in sorted(win):
    c = win[w]
    p_, b_, v_, x_ = c["P/LP"], c["B/LB"], c["VUS"], c["CONFLICTIVA"]
    ratio = f"{p_/b_:.2f}" if b_ else ("inf" if p_ else "-")
    marca = "  <<<" if RES and w == RES // 100 * 100 else ""
    print(f"  {w:>4}-{w+99:<9}{p_:>6}{b_:>7}{v_:>7}{x_:>8}   {ratio:>8}{marca}")

# --- datos para la figura ---
# El fichero que consumen fig02, make_fig2b, make_landscape_figure y el
# notebook 02 es landscape_missense.json, y hasta esta correccion NO lo escribia
# ningun fichero versionado del repositorio: existia solo en work/. El que si se
# generaba, landscape.json, no lo leia nadie y se anunciaba como "datos de la
# figura". Ahora se emiten los dos y cada uno dice lo que es.
#
# `totals` cuenta TODAS las clases que aparecen en `variants`, no un subconjunto.
# La version anterior declaraba solo P/LP, B/LB y VUS: sumaba 1 462 mientras el
# rotulo de la figura decia 1 497, porque CONFLICTIVA y "otra" desaparecian sin
# dejar rastro. Un reparto que no cubre su propio denominador es la clase de
# descuadre que un revisor usa para dudar del resto de las cifras.
def _pos_of(r):
    try:
        return int(str(r["pp"]).split("-")[0].split("/")[0])
    except ValueError:
        return None


def _dump(rows_subset, path, etiqueta):
    variants = [{"pos": _pos_of(r), "cls": r["cls"]}
                for r in rows_subset if _pos_of(r) is not None]
    totals = collections.Counter(v["cls"] for v in variants)
    assert sum(totals.values()) == len(variants), "el reparto no cubre el denominador"
    io.open(path, "w", encoding="utf-8").write(json.dumps(
        {"variants": variants, "totals": dict(totals), "candidate": RES},
        ensure_ascii=False))
    reparto = "  ".join(f"{k} {v:,}" for k, v in totals.most_common())
    print(f"  {etiqueta:<24} -> {path} ({len(variants):,} registros: {reparto})")


missense = [r for r in coding if "missense_variant" in r["con"]]
print(f"\n{'='*66}\nDATOS PARA LAS FIGURAS\n{'='*66}")
_dump(missense, "work/clinvar/landscape_missense.json", "solo missense")
_dump(coding, "work/clinvar/landscape.json", "todo lo codificante")
