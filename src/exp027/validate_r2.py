"""EXP-027 · validación de A′ (EXEC-DEF-PH1-001) antes del freeze r2.

Usa el intento abortado bajo exp027-phase1-execution-freeze (work/exp027/phase1) como referencia:
  - ventanas que fallaban en phase_rare (scaffold.bcf sin result.json): con A′ deben completar;
  - ventanas que habían completado: el resultado nuevo (scaffold como salida faseada) debe ser idéntico
    al viejo (phase_rare) en filas de WindowSites, recuentos de SER y auditoría; y, ejecutando también
    phase_rare sobre la misma entrada, los GT de todos los sitios del scaffold (MAF ≥ 0,1 %) deben ser
    idénticos bit a bit en las 2.504 muestras.
No calcula T, p, APR ni A1: solo igualdad técnica. Escribe work/exp027/validation_r2/VALIDATION.json.

Uso:  python -m src.exp027.validate_r2 --plan work/exp027/plan_execution
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import phase1, tools
from .orchestrate import _d

N_FAILING = 5
N_COMPLETED = 4
OLD = "work/exp027/phase1"
OUT = "work/exp027/validation_r2"


def _window_from_dir(name: str):
    chrom, rng = name.split("_", 1)
    s, e = rng.split("-")
    return chrom, int(s), int(e)


def pick(root: Path):
    """Elección determinista: orden alfabético de hijo/ventana, como mucho una ventana por hijo primero."""
    # Fallidas: la lista explícita del intento abortado (ABORTED_FAILED_WINDOWS.json), solo los fallos
    # confirmados de phase_rare, no los trabajos que la parada pudo interrumpir.
    aborted = json.loads((root / OLD / "ABORTED_FAILED_WINDOWS.json").read_text(encoding="utf-8"))
    failing = sorted((j["child"], j["window_dir"]) for j in aborted["jobs"]
                     if not j["possibly_interrupted_by_stop"])
    done = []
    for kid_dir in sorted(p for p in (root / OLD).iterdir() if p.is_dir()):
        for d in sorted(p for p in kid_dir.iterdir() if p.is_dir() and not p.name.startswith("cal_")):
            if (d / "result.json").exists():
                done.append((kid_dir.name, d.name))

    def spread(items, n):
        """Hijos y ventanas distintos siempre que se pueda (más cobertura que n veces la misma ventana)."""
        out, kids, wins = [], set(), set()
        for kid, w in items:
            if kid not in kids and w not in wins:
                out.append((kid, w))
                kids.add(kid)
                wins.add(w)
            if len(out) == n:
                return out
        for kid, w in items:
            if len(out) == n:
                break
            if (kid, w) not in out and w not in wins:
                out.append((kid, w))
                wins.add(w)
        return (out + [x for x in items if x not in out])[:n]

    return spread(failing, N_FAILING), spread(done, N_COMPLETED)


def scaffold_gt_invariance(rn, wd: str) -> dict:
    """GT de todas las muestras en los registros del scaffold (clave CHROM POS REF ALT), antes y después
    de phase_rare. Se casa por registro, no por posición: phase_rare añade variantes raras que pueden
    compartir posición con un sitio del scaffold (eso se informa aparte, no es una diferencia de GT).

    El primer intento de esta validación casaba por posición y dio un falso «distinto»
    (VALIDATION_attempt1_flawed_gt_check.json): comparaba ficheros con registros distintos.
    """
    q = "'%CHROM\\t%POS\\t%REF\\t%ALT[\\t%GT]\\n'"
    script = (f"cd /data/{wd} && bcftools query -l scaffold.bcf > _s.txt && "
              f"bcftools query -f '%CHROM\\t%POS\\n' scaffold.bcf > _sites.tsv && "
              f"bcftools query -S _s.txt -f {q} scaffold.bcf | sort -u > _q_a.txt && "
              f"bcftools query -S _s.txt -R _sites.tsv -f {q} phased_rare.bcf | sort -u > _q_b_all.txt && "
              "awk -F'\\t' 'NR==FNR{k[$1 FS $2 FS $3 FS $4]=1; next} ($1 FS $2 FS $3 FS $4) in k' "
              "_q_a.txt _q_b_all.txt | sort -u > _q_b.txt && "
              "echo $(md5sum < _q_a.txt) $(wc -l < _q_a.txt) $(md5sum < _q_b.txt) $(wc -l < _q_b.txt) $(wc -l < _q_b_all.txt)")
    p = rn.run(tools.BCFTOOLS_IMAGE, ["sh", "-c", script])
    f = p.stdout.split()                      # md5a - na md5b - nb nall
    md5a, na, md5b, nb, nall = f[0], int(f[2]), f[3], int(f[5]), int(f[6])
    return {"scaffold_records": na, "phased_rare_same_records": nb,
            "extra_rare_records_sharing_positions": nall - nb, "identical": md5a == md5b and na == nb}


def check_completed(ds, kid: str, wdir: str) -> dict:
    trio = next(t for t in ds.trios if t[0] == kid)
    window = _window_from_dir(wdir)
    old = json.loads((ds.mount / OLD / kid / wdir / "result.json").read_text(encoding="utf-8"))
    new = phase1.window_job(ds, trio, window, keep_intermediates=True)
    wd = phase1.job_dir(ds, "win", kid, window)
    rn = phase1.LoggedRunner(ds.mount, wd)
    contig = window[0]
    _, rs, re_ = phase1.phasing_region(window, phase1.BUFFER_BP, ds.lengths)
    region = tools.region_str(contig, rs, re_)
    rn.run(tools.SHAPEIT5_IMAGE, tools.phase_rare_cmd(_d(f"{wd}/joint_masked.bcf"), region,
                                                      _d(f"{wd}/scaffold.bcf"), region,
                                                      _d(ds.gmap(contig)), _d(f"{wd}/phased_rare.bcf")))
    rare_ok = (ds.mount / wd / "phased_rare.bcf").exists()
    gt = {}
    if rare_ok:
        rn.index(f"{wd}/phased_rare.bcf")
        gt = scaffold_gt_invariance(rn, wd)
    same = {k: old[k] == new[k] for k in ("rows", "ser_analytic", "ser_scaffold", "audit")}
    phase1._cleanup(rn, wd)
    for p in (ds.mount / wd).glob("_q_*.txt"):            # volcados de GT (~100 MB): solo para el md5
        p.unlink()
    return {"child": kid, "window": old["window"], "result_identical": same,
            "n_rows": len(new["rows"]), "phase_rare_completed": rare_ok, "scaffold_gt_invariance": gt,
            "pass": all(same.values()) and (not rare_ok or gt.get("identical", False))}


def check_failing(ds, kid: str, wdir: str) -> dict:
    trio = next(t for t in ds.trios if t[0] == kid)
    window = _window_from_dir(wdir)
    try:
        r = phase1.window_job(ds, trio, window)
        return {"child": kid, "window": r["window"], "completed": True, "n_rows": len(r["rows"]),
                "ser_analytic": r["ser_analytic"], "pass": True}
    except Exception as exc:                       # noqa: BLE001 — se reporta, no se oculta
        return {"child": kid, "window": wdir, "completed": False, "error": f"{type(exc).__name__}: {exc}",
                "pass": False}


def main(argv=None) -> int:
    import yaml
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, default=Path("work/exp027/plan_execution"))
    ap.add_argument("--workers", type=int, default=9)
    a = ap.parse_args(argv)
    root = Path(yaml.safe_load(Path("config/paths.yaml").read_text(encoding="utf-8"))["compute"]["docker_repo_root"])
    ds = phase1.Dataset.from_plan(a.plan, "work/exp027/data", root, out=OUT)
    failing, done = pick(root)
    print(f"ventanas antes fallidas: {failing}\nventanas antes completadas: {done}", flush=True)
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        f1 = [ex.submit(check_failing, ds, k, w) for k, w in failing]
        f2 = [ex.submit(check_completed, ds, k, w) for k, w in done]
        res_f = [f.result() for f in f1]
        res_c = [f.result() for f in f2]
    verdict = all(r["pass"] for r in res_f + res_c) and len(res_f) == N_FAILING and len(res_c) == N_COMPLETED
    code = {f"src/exp027/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob("*.py"))}
    report = {"verdict": "PASS" if verdict else "FAIL", "previously_failing": res_f,
              "previously_completed": res_c, "reference_attempt": OLD,
              "note": ("Igualdad de rows/audit implica entrada puntuable idéntica byte a byte; la "
                       "puntuación es determinista, así que no se calculan T ni p aquí."),
              "code_sha256": code}
    out = root / OUT / "VALIDATION.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2), flush=True)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
