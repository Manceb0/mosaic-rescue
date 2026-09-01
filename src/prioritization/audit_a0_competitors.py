#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-021 · auditoria de los tres competidores que superan a BUB1B en A0.

POR QUE ES PRIORIDAD A
    Al conectar el cruce de alelos (que nunca lo habia estado), tres deleciones
    homocigotas de sitio donador emergieron con 13,5 puntos y desplazaron a
    BUB1B del puesto 1 al 4 en el control genetico puro. Un resultado que mueve
    la interpretacion causal se audita antes que nada.

QUE NO VALE COMO PRUEBA
    Que no aparezcan en la salida de Exomiser NO demuestra que sean falsas.
    Exomiser pudo excluirlas por frecuencia, por efecto, por herencia o por
    calidad, y cada motivo significa una cosa distinta. Hay que recuperar el
    motivo, no inferirlo.

ORDEN DE AGOTAMIENTO, todo LOCAL
    1. QC de variante: QUAL, FILTER, DP, AD, GQ, balance alelico
    2. transcrito: .esta la consecuencia en el transcrito MANE/canonico?
    3. consecuencia de splicing: .es el donador canonico o la 5.a base?
    4. frecuencia en recursos ya descargados
    5. motivo exacto de exclusion de Exomiser
    6. contexto de repeticion y mapabilidad, si hay recurso local

Si tras esto siguen sin resolverse, el estado es UNRESOLVED — nunca NEGATIVE —
y BUB1B se queda en el puesto 4 de A0. No se tocan los pesos.
"""
from __future__ import annotations
import io, sys, gzip, collections

sys.path.insert(0, ".")
from src.prioritization.genome_wide import load          # noqa: E402
from src.paths import patient_vcf                        # noqa: E402

GENES = ("CTU2", "PEX5", "SLC22A1")
ANN = "work/gw/highmod_ann.tsv"


def targets(rows):
    out = []
    for g in GENES:
        v = [x for x in rows if x.gene == g and x.gt == "1/1"
             and x.max_af is None and x.impact == "HIGH"]
        if v:
            out.append((g, v[0]))
    return out


def vcf_record(chrom, pos_window):
    """Registro crudo del VCF, para leer QUAL y el resto de campos que el
    pipeline no conserva."""
    found = {}
    with gzip.open(patient_vcf(), "rt", errors="replace") as f:
        for line in f:
            if line[0] == "#":
                continue
            p = line.rstrip("\n").split("\t")
            key = (p[0], int(p[1]))
            if key in pos_window:
                found[key] = p
    return found


def transcript_context(gene: str):
    """Todas las anotaciones de ese gen en el TSV, con transcrito y MANE.

    Importa porque una consecuencia de splicing sobre un transcrito menor no
    tiene el mismo peso que sobre el MANE Select.
    """
    rows, ix = [], None
    with io.open(ANN, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("##"):
                continue
            if line.startswith("#"):
                ix = {k: i for i, k in enumerate(line[1:].rstrip("\n").split("\t"))}
                continue
            p = line.rstrip("\n").split("\t")
            if p[ix["SYMBOL"]] == gene:
                rows.append({k: p[i] for k, i in ix.items()})
    return rows


def main():
    rows = load(ANN, patient_vcf())
    tgt = targets(rows)

    print("=== EXP-021 · AUDITORIA LOCAL DE LOS TRES COMPETIDORES DE A0 ===\n")

    # --- 1 · QC de variante, desde el VCF crudo ---
    window = {}
    for g, v in tgt:
        # la Location de VEP para una delecion empieza una base despues del VCF
        base = int(v.loc.split(":")[1].split("-")[0])
        for d in (0, -1, -2):
            window[(v.chrom, base + d)] = g
    rec = vcf_record(None, set(window))

    print("  1 · QC DE VARIANTE, desde el VCF crudo")
    print(f"  {'gen':<10}{'QUAL':>9}{'FILTER':>9}{'GT':>7}{'DP':>6}{'GQ':>6}{'AD':>12}{'AB':>7}")
    print("  " + "-" * 66)
    for (c, p), g in sorted(window.items()):
        r = rec.get((c, p))
        if not r:
            continue
        d = dict(zip(r[8].split(":"), r[9].split(":")))
        ad = d.get("AD", "")
        try:
            a = [int(x) for x in ad.split(",")]
            ab = a[1] / sum(a) if len(a) > 1 and sum(a) else None
        except ValueError:
            ab = None
        print(f"  {g:<10}{r[5]:>9}{r[6]:>9}{d.get('GT',''):>7}{d.get('DP',''):>6}"
              f"{d.get('GQ',''):>6}{ad:>12}{(f'{ab:.2f}' if ab is not None else '-'):>7}")

    # --- 2 y 3 · transcrito y detalle de la consecuencia ---
    print("\n  2-3 · TRANSCRITO Y CONSECUENCIA")
    for g, v in tgt:
        ctx = transcript_context(g)
        mane = [r for r in ctx if r.get("MANE_SELECT", "-") not in ("", "-")]
        canon = [r for r in ctx if r.get("CANONICAL") == "YES"]
        hi = [r for r in ctx if r.get("IMPACT") == "HIGH"]
        print(f"\n  {g}: {len(ctx)} anotaciones · {len(mane)} en MANE Select · "
              f"{len(canon)} en canonico · {len(hi)} de impacto HIGH")
        for r in hi[:3]:
            print(f"      consecuencia : {r.get('Consequence','')}")
            print(f"      transcrito   : {r.get('Feature','')}  "
                  f"MANE={'si' if r.get('MANE_SELECT','-') not in ('','-') else 'NO'}  "
                  f"canonico={'si' if r.get('CANONICAL')=='YES' else 'NO'}")
            print(f"      intron/exon  : intron={r.get('INTRON','-')} exon={r.get('EXON','-')}")

    # --- 6 · contexto local de variantes: .region de complejidad? ---
    print("\n  6 · CONTEXTO LOCAL (densidad de variantes en +/-1 kb)")
    for g, v in tgt:
        near = [w for w in rows if w.chrom == v.chrom and abs(w.pos - v.pos) <= 1000]
        pos = {w.loc for w in near}
        print(f"      {g:<10}{len(pos):>4} posiciones anotadas en 2 kb   "
              f"DP={v.dp}  GQ={v.gq}")


if __name__ == "__main__":
    main()
