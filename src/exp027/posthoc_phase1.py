"""EXP-027 · POST-HOC DIAGNOSTIC — NOT USED FOR ADJUDICATION.

Lee los result.json congelados del run r2 (work/exp027/phase1_r2) y hace dos cosas, sin volver a
fasear ni a descargar nada:

1. Reproduce la evaluación completa (evaluate.run_benchmark con las mismas semillas, B = 10 000 y la
   rejilla de δ congelada) y exige que coincida con phase1_report.json en cada métrica adjudicada.
   Si no coincide, falla: el informe sellado no sería reproducible.
2. Construye el mapa de los 1000 pares hijo × ventana de evaluación (995 evaluables): p y T con datos
   intactos (mismas semillas OBS), efecto, n de hets, profundidad, fracción enmascarada, fracción del
   alelo de referencia y si el par fue positivo. Más resúmenes por hijo, superpoblación, cromosoma y
   terciles. Todo es descriptivo: no cambia el FAIL ni se usa para adjudicar nada.

Las curvas de sensibilidad por δ (fase inferida y mendeliana) salen de la reproducción del punto 1.
Salidas en work/exp027/posthoc/ (no versionadas: contienen coordenadas de ventanas).

Uso:  python -m src.exp027.posthoc_phase1
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from . import evaluate, phase1, stats
from .serialize import DELTA_GRID, delta_fmt, perm_seed_obs

LABEL = "POST-HOC DIAGNOSTIC — NOT USED FOR ADJUDICATION"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(run: Path):
    win, cal = [], []
    for rj in sorted(run.rglob("result.json")):
        r = json.loads(rj.read_text(encoding="utf-8"))
        (win if "rows" in r else cal).append(r)
    return win, cal


def reproduce(run: Path, plan: dict, win, cal) -> tuple[dict, dict]:
    sp = {s["child"]: s["superpop"] for s in plan["selection"]}
    ds = phase1.Dataset(mount=None, out="", trios=[(s["child"], s["father"], s["mother"]) for s in plan["selection"]],
                        superpop=sp, phase3=[], pedigree=[], lengths={}, evaluation=[], calibration=[],
                        reference="", region_bcf=None, alignment=None, gmap=None, site_masks=None)
    children = phase1.assemble(ds, win, cal)
    out = evaluate.run_benchmark(children, b=stats.B_PERMUTATIONS, deltas_grid=DELTA_GRID)
    return out, children


def compare(report: dict, rep: dict) -> dict:
    keys = ["phase1_global", "a1_applicable", "apr_k", "apr_n", "apr", "sensitivity_inferred",
            "sensitivity_mendelian", "retention", "ser", "ser_scaffold_descriptive", "fail_reasons"]
    diff = {k: (report[k], rep[k]) for k in keys if report[k] != rep[k]}
    for sp, v in report["strata"].items():
        if v != rep["strata"][sp]:
            diff[f"strata.{sp}"] = (v, rep["strata"][sp])
    for k, v in report["locus_bub1b"].items():
        if v != rep["locus_bub1b"][k]:
            diff[f"locus_bub1b.{k}"] = (v, rep["locus_bub1b"][k])
    return diff


def sensitivity_curves(results: dict) -> dict:
    """Media por hijo de la fracción detectada en sus ventanas, y media entre hijos (Amendment 6)."""
    curves = {"inferred": {}, "mendelian": {}}
    for key, field in (("inferred", "detect_inferred"), ("mendelian", "detect_mendel")):
        for d in DELTA_GRID:
            dk = delta_fmt(d)
            per_child = []
            for k in results["children"].values():
                vals = [np.mean(w[field][dk]) for w in k["windows"].values() if w["power_evaluable"]]
                if vals:
                    per_child.append(float(np.mean(vals)))
            curves[key][dk] = float(np.mean(per_child))
    return curves


def apr_map(win, plan: dict) -> list[dict]:
    sp = {s["child"]: s["superpop"] for s in plan["selection"]}
    rows = []
    for r in sorted(win, key=lambda x: (x["child"], x["window"])):
        arr = np.array(r["rows"], dtype=np.int64).reshape(-1, 4)
        ws = evaluate.WindowSites(arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], np.ones(len(arr), bool), r["audit"])
        ie = evaluate.intact_eval(ws, r["child"], r["window"])
        m = ws.mask()
        n = ws.depth()[m]
        ref_frac = float(np.mean(arr[:, 0][m] / n)) if n.size else None
        # Alelo en H1 = 0 significa que H1 lleva REF: fracción de hets con REF en H1 (descriptivo).
        h1_ref = float(np.mean(arr[:, 2][m] == 0)) if n.size else None
        a = r["audit"]
        rows.append({
            "child": r["child"], "superpop": sp[r["child"]], "window": r["window"],
            "chrom": r["window"].split(":")[0], "is_bub1b": r["is_bub1b"],
            "evaluable": ie["evaluable"], "n_hets": ie["n_hets"],
            "p": ie.get("p"), "T": ie.get("T"), "effect": ie.get("effect"),
            "positive": bool(ie.get("positive", False)),
            "mean_depth": float(n.mean()) if n.size else None, "ref_fraction": ref_frac, "h1_ref_fraction": h1_ref,
            "masked_bp_fraction_intact": a.get("masked_bp_fraction_intact"),
            "n_mask_segdup": a.get("n_mask_segdup"), "n_not_in_phased_output": a.get("n_not_in_phased_output"),
            "n_without_ad": a.get("n_without_ad"), "ser_switches": r["ser_analytic"][0],
            "ser_checked": r["ser_analytic"][1],
        })
    return rows


def summaries(rows: list[dict]) -> dict:
    ev = [r for r in rows if r["evaluable"]]

    def group(key):
        g = {}
        for r in ev:
            g.setdefault(r[key], []).append(r["positive"])
        return {k: {"n": len(v), "positive": int(sum(v)), "apr": round(sum(v) / len(v), 4)} for k, v in sorted(g.items())}

    def terciles(field):
        vals = sorted(r[field] for r in ev if r[field] is not None)
        cuts = [vals[len(vals) // 3], vals[2 * len(vals) // 3]]
        out = {}
        for name, lo, hi in (("bajo", -1e18, cuts[0]), ("medio", cuts[0], cuts[1]), ("alto", cuts[1], 1e18)):
            sel = [r["positive"] for r in ev if r[field] is not None and lo <= r[field] < hi]
            out[name] = {"rango": [None if lo == -1e18 else round(lo, 4), None if hi == 1e18 else round(hi, 4)],
                         "n": len(sel), "apr": round(sum(sel) / len(sel), 4) if sel else None}
        return out

    pos = [r for r in ev if r["positive"]]
    return {
        "label": LABEL,
        "pairs_total": len(rows), "pairs_evaluable": len(ev), "positives": len(pos),
        "apr": round(len(pos) / len(ev), 4),
        "by_superpop": group("superpop"), "by_child": group("child"), "by_chrom": group("chrom"),
        "terciles": {f: terciles(f) for f in ("n_hets", "mean_depth", "masked_bp_fraction_intact",
                                               "ref_fraction", "h1_ref_fraction")},
        "effect_positive_median": float(np.median([r["effect"] for r in pos])) if pos else None,
        "effect_negative_median": float(np.median([r["effect"] for r in ev if not r["positive"]])),
        "T_sign_among_positives": {"T>0": sum(r["T"] > 0 for r in pos), "T<0": sum(r["T"] < 0 for r in pos)},
    }


def main(argv=None) -> int:
    import yaml
    root = Path(yaml.safe_load(Path("config/paths.yaml").read_text(encoding="utf-8"))["compute"]["docker_repo_root"])
    run = root / "work/exp027/phase1_r2"
    plan = json.loads((root / "work/exp027/plan_execution/plan_windows.json").read_text(encoding="utf-8"))
    report = json.loads((run / "phase1_report.json").read_text(encoding="utf-8"))
    out = root / "work/exp027/posthoc"
    out.mkdir(parents=True, exist_ok=True)
    win, cal = load(run)
    print(f"{LABEL}\nresult.json: {len(win)} ventanas, {len(cal)} tiles de calibración", flush=True)

    rows = apr_map(win, plan)
    s = summaries(rows)
    with open(out / "apr_map.csv", "w", encoding="utf-8", newline="") as f:
        f.write(f"# {LABEL}\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"mapa APR: {s['positives']}/{s['pairs_evaluable']} = {s['apr']} (informe: {report['apr_k']}/{report['apr_n']})", flush=True)

    rep_full, _ = reproduce(run, plan, win, cal)
    rep = rep_full["report"]
    diff = compare(report, rep)
    curves = sensitivity_curves(rep_full["results"])
    result = {
        "label": LABEL,
        "inputs": {"phase1_report.json": _sha(run / "phase1_report.json"),
                   "RUN_MANIFEST.json": _sha(run / "RUN_MANIFEST.json"),
                   "plan_windows.json": _sha(root / "work/exp027/plan_execution/plan_windows.json"),
                   "n_result_json": len(win) + len(cal)},
        "reproduction": {"identical_to_sealed_report": not diff, "differences": diff},
        "apr_map_consistent": s["positives"] == report["apr_k"] and s["pairs_evaluable"] == report["apr_n"],
        "sensitivity_by_delta": curves,
        "summary": s,
        "code_sha256": _sha(Path(__file__)),
    }
    (out / "phase1_posthoc.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"identical_to_sealed_report": not diff, "differences": diff,
                      "apr_map_consistent": result["apr_map_consistent"], "sensitivity_by_delta": curves},
                     indent=1, default=str), flush=True)
    return 0 if (not diff and result["apr_map_consistent"]) else 1


if __name__ == "__main__":
    sys.exit(main())
