#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-006b · comparacion entre el baseline externo y nuestro ranking.

QUE ES ESTA COMPARACION
    Convergencia METODOLOGICA: dos motores sin codigo comun sobre el MISMO
    VCF. Un artefacto compartido los engana a los dos (ocurrio: SERPINA1).
    Nunca se presenta como dos observaciones biologicas.

Se ejecuta DESPUES de Exomiser. La comparacion no puede influir en el baseline:
Exomiser ya termino y no ha visto nada nuestro.

Lecturas, todas fijadas en docs/DECISIONS.md antes de ejecutar:
  1. rango de BUB1B en BASELINE-PRIMARY   -> top 10 / 11-50 / fuera / ausente
  2. solapamiento del top-20 con B0_FULL_PROBAND
  3. genes del top-10 del baseline que nosotros no habiamos mirado

SANEADO: imprime simbolos de gen y rangos. No imprime coordenadas, genotipos ni
identidad de variantes. Los simbolos de gen no son reidentificantes por si solos.
"""
from __future__ import annotations
import io, os, sys, csv, pickle

sys.path.insert(0, ".")
RUNS = "work/exomiser/runs"
GENE = "BUB1B"


def read_exomiser(run: str):
    """[(rango, gen, score, MOI)] por GEN UNICO, desde el TSV de genes.

    Exomiser emite UNA FILA POR GEN Y MODO DE HERENCIA: en esta corrida son 470
    filas para 398 genes. Contar filas como si fueran genes infla el denominador
    y hace aparecer genes repetidos en el top-10 y en el solapamiento. Se
    conserva la mejor fila de cada gen y se reporta el modo que la produce, que
    es informacion util: dice bajo que modelo de herencia lo prioriza.
    """
    d = os.path.join(RUNS, run)
    cand = [f for f in os.listdir(d) if f.endswith(".genes.tsv")] if os.path.isdir(d) else []
    if not cand:
        raise FileNotFoundError(f"sin .genes.tsv en {d} — .corrio Exomiser?")
    path = os.path.join(d, cand[0])
    with io.open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    hdr = [h.lstrip("#").strip().upper() for h in rows[0]]
    ix = {h: i for i, h in enumerate(hdr)}
    gi, ri = ix["GENE_SYMBOL"], ix.get("RANK")
    si = next((i for i, h in enumerate(hdr) if "COMBINED_SCORE" in h), None)
    mi = ix.get("MOI")

    best = {}
    for r in rows[1:]:
        if len(r) <= gi:
            continue
        g = r[gi]
        rank = int(r[ri]) if ri is not None else len(best) + 1
        if g not in best or rank < best[g][0]:
            best[g] = (rank, g,
                       float(r[si]) if si is not None and len(r) > si else None,
                       r[mi] if mi is not None and len(r) > mi else "")
    ordered = sorted(best.values(), key=lambda t: t[0])
    # se reindexa: el RANK del fichero cuenta filas, no genes
    return [(i, g, s, m) for i, (_, g, s, m) in enumerate(ordered, 1)], path, len(rows) - 1


def read_ours(analysis="B0_FULL_PROBAND"):
    res = pickle.load(io.open("work/gw/mode_b_results_v4.pkl", "rb"))
    return [(i, row[0], row[1]) for i, row in enumerate(res[analysis], 1)]


def rank_of(rows, gene):
    for t in rows:
        if t[1] == gene:
            return t[0], t[2], (t[3] if len(t) > 3 else "")
    return None, None, ""


def verdict(rank):
    if rank is None:
        return "AUSENTE de la salida — comprobar si lo filtro por frecuencia, herencia o efecto"
    if rank <= 10:
        return ("CONVERGENCIA METODOLOGICA (top 10) — metodo independiente "
                "sobre el MISMO VCF del paciente; no es evidencia biologica independiente")
    if rank <= 50:
        return f"CONVERGENCIA PARCIAL (puesto {rank}) — no se presenta como confirmacion"
    return f"DISCREPANCIA SERIA (puesto {rank}) — investigar antes de defender nada nuestro"


def main():
    ours = read_ours()
    ext_primary = None
    print("=== EXP-006b · BASELINE EXTERNO vs NUESTRO RANKING ===\n")

    for run in ("BASELINE-PRIMARY", "BASELINE-FH"):
        try:
            ext, path, nrows = read_exomiser(run)
        except FileNotFoundError as e:
            print(f"  {run}: {e}\n")
            continue
        r, s, moi = rank_of(ext, GENE)
        print(f"  --- {run} · {len(ext):,} genes unicos ({nrows} filas gen x herencia) ---")
        print(f"  fuente: {os.path.basename(path)}")
        print(f"  {GENE}: puesto {r if r else '—'} de {len(ext)}"
              + (f" · score {s:.4f} · mejor modelo {moi}" if s is not None else ""))
        print(f"  VEREDICTO: {verdict(r)}\n")
        print("  top 10 del baseline, por gen unico:")
        for rank, g, sc, m in ext[:10]:
            mark = "  <<<" if g == GENE else ""
            print(f"    {rank:>3}  {g:<14}{m:<5}{sc if sc is None else f'{sc:.4f}'}{mark}")
        if run == "BASELINE-PRIMARY":
            ext_primary = ext
        print()

    if ext_primary is None:
        print("  sin BASELINE-PRIMARY: no hay comparacion que hacer")
        return 1

    # --- solapamiento del top-20 ---
    a = [t[1] for t in ext_primary[:20]]
    b = [g for _, g, _ in ours[:20]]
    shared = [g for g in a if g in b]
    print(f"  --- solapamiento top-20 ---")
    print(f"  {len(shared)} de 20 genes en comun: {', '.join(shared) if shared else '(ninguno)'}")

    only_ext = [g for g in a[:10] if g not in [x for _, x, _ in ours[:50]]]
    print(f"\n  --- genes del top-10 externo fuera de NUESTRO top-50 ---")
    if only_ext:
        print("  " + ", ".join(only_ext))
        print("  -> entran en el camino critico como hipotesis competidoras")
    else:
        print("  ninguno")

    our_rank = next((i for i, g, _ in ours if g == GENE), None)
    print(f"\n  nuestro ranking (B0_FULL_PROBAND): {GENE} puesto {our_rank}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
