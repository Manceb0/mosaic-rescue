"""EXP-027 · ejecutor real de Phase 1: 20 hijos × 50 ventanas + 20 tiles de calibración.

Trabajos independientes y reanudables, cada uno con su directorio y su result.json:
  - ventana (hijo × ventana de evaluación): C_target -> AC/AN/MAF en C_target -> entrada conjunta sin
    sitios enmascarados (globales + copy-changing del hijo) -> phase_common por 2 chunks con buffer ->
    ligate (L_isec > 0) -> el scaffold es la salida faseada (sin phase_rare: EXEC-DEF-PH1-001) -> SER
    analítico y de scaffold por recuentos, sin máscaras de verdad -> hets analíticos clasificados por
    masks.window_audit -> AD con el extractor congelado (bcftools mpileup) sobre el slice CRAM,
    casando el ALT del VCF;
  - calibración (hijo × tile): hets analíticos intactos (sin máscaras globales ni copy-changing del
    hijo) con su AD, sin fase (ρ usa b_i − 0.5).
Al terminar, evaluate.run_benchmark con B = 10 000 y la rejilla de δ congelada produce el informe.

El mismo código corre sobre el juguete (Dataset.toy) y sobre 1000G (Dataset.from_plan). Fallo fuerte
heredado del orquestador: imagen ausente o digest distinto, salida ausente, ligate sin solape, regla
congelada violada, muestras inesperadas, sitio enmascarado superviviente.

Nada falla en silencio (EXEC-DEF-PH1-001): cada trabajo escribe job.log con cada comando, su código
de salida y su stderr; el ejecutor escribe progress.log (sin búfer) y status.json en cada trabajo; la
primera excepción cancela lo pendiente, mata los contenedores del run, escribe FAILED_JOB.json y
termina con error.

Uso:
    python -m src.exp027.phase1 toy  --out work/exp027/phase1_toy
    python -m src.exp027.phase1 real --plan work/exp027/plan_execution --workers 16   # solo en el tag de ejecución
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import evaluate, masks as masks_mod, selection, tools, toy_data, truth
from .orchestrate import (ANALYTIC_MAF, BUFFER_BP, GQ_MIN, SAMTOOLS_IMAGE, SCAFFOLD_MAF,
                          OrchestrationError, Runner, _d, _gt, check_image, cohort_inputs,
                          exclude_masked, phase, require_samples, require_unmasked, ser_for_child,
                          write_lines)
from .serialize import DELTA_GRID, window_id
from .windows import BUB1B_WINDOW, phasing_region

# Etiqueta Docker única de los contenedores de ESTE proceso: la parada solo mata contenedores con ella,
# nunca un barrido genérico.
RUN_LABEL = f"exp027-r2-{uuid.uuid4().hex[:12]}"


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _write_atomic(path: Path, text: str) -> None:
    """Escribe en un temporal del mismo directorio y lo renombra (os.replace es atómico)."""
    import os
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex[:8]}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


class LoggedRunner(Runner):
    """Runner que deja rastro: cada comando Docker, su código de salida, su duración y la cola de su
    stderr van a job.log del trabajo (append + flush). Los contenedores llevan la etiqueta del run para
    poder matarlos en bloque si algo falla."""

    def __init__(self, mount: Path, job_dir: str):
        super().__init__(mount)
        self.log_path = self.mount / job_dir / "job.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def run(self, image: str, cmd: list[str]) -> subprocess.CompletedProcess:
        full = tools.docker_cmd(image, str(self.mount), cmd)          # aplica assert_frozen
        full = full[:2] + ["--label", f"exp027_run={RUN_LABEL}"] + full[2:]
        t0 = time.time()
        p = subprocess.run(full, capture_output=True, text=True)
        entry = {"utc": _now(), "seconds": round(time.time() - t0, 1), "returncode": p.returncode,
                 "cmd": cmd, "stderr_tail": (p.stderr or "")[-2000:]}
        with open(self.log_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
        return p


@dataclass
class Dataset:
    mount: Path                                   # se monta en /data
    out: str                                      # relativo a mount
    trios: list                                   # [(hijo, padre, madre)]
    superpop: dict
    phase3: list
    pedigree: list
    lengths: dict
    evaluation: list                              # [(chrom, start, end)]
    calibration: list
    reference: str
    region_bcf: callable
    alignment: callable
    gmap: callable
    site_masks: callable
    bub1b: tuple = BUB1B_WINDOW
    meta: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ constructores
    @classmethod
    def toy(cls, out: Path) -> "Dataset":
        ds = toy_data.build(out)
        rn = Runner(out)
        from .orchestrate import prepare_toy_bams
        prepare_toy_bams(rn, ds["children"])
        rn.bcf("view", "-Ob", "-o", "/data/all.bcf", "/data/joint.vcf")
        rn.out("all.bcf")
        rn.index("all.bcf")
        contig = ds["contig"]
        sp = {t[0]: selection.SUPERPOPULATIONS[i % 5] for i, t in enumerate(ds["pedigree"])}
        window = (contig, 500_001, 2_500_000)
        return cls(mount=out, out="phase1", trios=list(ds["pedigree"]), superpop=sp, phase3=ds["cohort"],
                   pedigree=ds["pedigree"], lengths={contig: ds["ref_len"]}, evaluation=[window],
                   calibration=[(contig, 1, 250_000), (contig, 2_750_001, ds["ref_len"])],
                   reference="ref.fa", region_bcf=lambda w: "all.bcf", alignment=lambda k: f"{k}.bam",
                   gmap=lambda c: "toy.gmap.gz", site_masks=toy_data.site_masks, bub1b=window)

    @classmethod
    def from_plan(cls, plan_dir: Path, data_rel: str, mount: Path,
                  out: str = "work/exp027/phase1_r2") -> "Dataset":
        from . import plan as P
        plan = json.loads((plan_dir / "plan_windows.json").read_text(encoding="utf-8"))
        data = mount / data_rel
        ped = P.read_ped_population(data / "meta/ped_population.txt")
        pedigree = [(s, r["father"], r["mother"]) for s, r in ped.items()]
        phase3 = sorted(P.index_samples(data / "meta/index_2504.sequence.index"))
        win = lambda ids: [(c, int(r.split("-")[0]), int(r.split("-")[1])) for c, r in (w.split(":") for w in ids)]
        lengths = plan["lengths"]
        mdir = plan_dir / "masks"

        def bed(name):
            p = mdir / f"{name}.bed"
            if not p.exists():
                raise OrchestrationError(f"falta la máscara {p}")
            return [(c, int(s) + 1, int(e)) for c, s, e in
                    (l.split("\t") for l in p.read_text(encoding="ascii").splitlines() if l.strip())]

        glob = {k: bed(k) for k in ("gaps", "segdup", "blacklist")}
        masks_cache = {}

        def site_masks(kid):
            if kid not in masks_cache:
                masks_cache[kid] = masks_mod.SiteMasks(gaps=glob["gaps"], segdup=glob["segdup"],
                                                       blacklist=glob["blacklist"],
                                                       child_cc=bed(f"{kid}.child_cc"),
                                                       parent_cc=bed(f"{kid}.parent_cc"))
            return masks_cache[kid]

        def region_bcf(w):
            c, s, e = phasing_region(w, BUFFER_BP, lengths)
            return f"{data_rel}/goB/gt_reduced/{c}_{s}_{e}.gtgq.bcf"

        return cls(mount=mount, out=out, trios=[(s["child"], s["father"], s["mother"])
                                                                 for s in plan["selection"]],
                   superpop={s["child"]: s["superpop"] for s in plan["selection"]}, phase3=phase3,
                   pedigree=pedigree, lengths=lengths, evaluation=win(plan["evaluation"]),
                   calibration=win(plan["calibration"]),
                   reference=f"{data_rel}/ref/GRCh38_full_analysis_set_plus_decoy_hla.fa",
                   region_bcf=region_bcf, alignment=lambda k: f"{data_rel}/goB/cram_raw/{k}.slices.cram",
                   gmap=lambda c: f"{data_rel}/maps/b38/{c}.b38.gmap.gz", site_masks=site_masks,
                   meta={"plan": str(plan_dir)})


# ---------------------------------------------------------------------- piezas
def trio_info(rn: Runner, bcf: str, trio, window) -> dict:
    """POS -> REF, ALT, FILTER, GT/GQ del hijo y GT de los padres, dentro de la ventana."""
    kid, fa, mo = trio
    c, s, e = window
    args = ["query", "-r", f"{c}:{s}-{e}", "-s", f"{kid},{fa},{mo}",
            "-f", "%POS\t%REF\t%ALT\t%FILTER[\t%SAMPLE=%GT=%GQ]\n", _d(bcf)]
    r = rn.bcf(*args)
    if r.returncode != 0:
        raise OrchestrationError(f"bcftools query falló en {bcf}: {r.stderr[-400:]}")
    info = {}
    for line in r.stdout.splitlines():
        f = line.split("\t")
        by = {}
        for cell in f[4:]:
            name, gt, gq = cell.split("=")
            by[name] = (_gt(gt), int(gq) if gq not in (".", "") else -1)
        if set(by) != {kid, fa, mo}:
            raise OrchestrationError(f"muestras inesperadas en la consulta del trío: {sorted(by)}")
        pos = int(f[0])
        if pos in info:                                  # varios registros en la misma posición
            info[pos]["dup"] = True
            continue
        info[pos] = {"ref": f[1], "alt": f[2], "filter": f[3], "kid": by[kid][0], "gq": by[kid][1],
                     "fa": by[fa][0], "mo": by[mo][0], "dup": False}
    return info


def cohort_maf(rn: Runner, tags_bcf: str, window) -> dict:
    c, s, e = window
    r = rn.bcf("query", "-r", f"{c}:{s}-{e}", "-f", "%POS\t%REF\t%ALT\t%INFO/MAF\n", _d(tags_bcf))
    if r.returncode != 0:
        raise OrchestrationError(f"bcftools query falló en {tags_bcf}: {r.stderr[-400:]}")
    out = {}
    for line in r.stdout.splitlines():
        pos, ref, alt, maf = line.split("\t")
        # Registros multialélicos (MAF con comas): no son marcadores analíticos (SHAPEIT5 no los fasea).
        out[(int(pos), ref, alt)] = float(maf) if maf not in (".", "") and "," not in maf else 0.0
    return out


def analytic(info: dict, maf: dict, p: int) -> bool:
    """Marcador analítico congelado: MAF de C_target ≥ 1 %, PASS, GQ ≥ 30, het 0/1 en el hijo."""
    i = info.get(p)
    return (i is not None and not i["dup"] and maf.get((p, i["ref"], i["alt"]), 0.0) >= ANALYTIC_MAF
            and i["filter"] == "PASS" and i["gq"] >= GQ_MIN and i["kid"] == (0, 1))


def ad_by_allele(rn: Runner, aln: str, ref: str, contig: str, sites: dict, wd: str) -> dict:
    """AD de REF y del ALT del VCF por posición con el extractor congelado (bcftools mpileup).

    sites: {pos: (ref, alt)}. Si mpileup no emite un registro con ese REF, la posición no tiene AD;
    si no ve el ALT, su recuento es 0.
    """
    if not sites:
        return {}
    pos_sorted = sorted(sites)
    write_lines(rn.mount / f"{wd}/sites.tsv", [f"{contig}\t{p}" for p in pos_sorted])
    rn.run(tools.BCFTOOLS_IMAGE, tools.mpileup_cmd(_d(ref), _d(f"{wd}/sites.tsv"), _d(aln), _d(f"{wd}/ad.bcf")))
    rn.out(f"{wd}/ad.bcf")
    rn.index(f"{wd}/ad.bcf")
    out = {}
    for line in rn.query(f"{wd}/ad.bcf", "%POS\t%REF\t%ALT[\t%AD]\n"):
        pos, ref_a, alts, ad = line.split("\t")
        pos = int(pos)
        if pos not in sites or ref_a != sites[pos][0]:
            continue
        counts = [int(x) for x in ad.split(",")]
        alt_list = alts.split(",")
        want = sites[pos][1]
        k = alt_list.index(want) + 1 if want in alt_list else None
        out[pos] = (counts[0], counts[k] if k is not None and k < len(counts) else 0)
    return out


def _cleanup(rn: Runner, wd: str) -> None:
    """Borra los intermedios grandes del trabajo (BCF de cohorte, entrada conjunta, chunks y fase).
    Son derivados reproducibles desde los slices brutos, que no se tocan."""
    d = rn.mount / wd
    for p in d.glob("*.bcf*"):
        p.unlink()


def _switch_counts(rn: Runner, wd: str, tag: str, kid: str):
    with gzip.open(rn.mount / f"{wd}/ser_{tag}.sample.switch.txt.gz", "rt") as f:
        c = tools.parse_switch_counts(f.read().splitlines())
    if kid not in c:
        raise OrchestrationError(f"switch sin recuentos para {kid}")
    return list(c[kid])


def job_dir(ds: Dataset, kind: str, kid: str, window) -> str:
    wid = window_id(*window).replace(":", "_")
    return f"{ds.out}/{kid}/{wid}" if kind == "win" else f"{ds.out}/{kid}/cal_{wid}"


def window_job(ds: Dataset, trio, window, keep_intermediates: bool = False) -> dict:
    kid, fa, mo = trio
    wid = window_id(*window)
    wd = job_dir(ds, "win", kid, window)
    res_path = ds.mount / wd / "result.json"
    if res_path.exists():
        return json.loads(res_path.read_text(encoding="utf-8"))
    rn = LoggedRunner(ds.mount, wd)
    m = ds.site_masks(kid)
    cohort = selection.conditioning_cohort(ds.phase3, kid, ds.pedigree)
    if kid in cohort or fa in cohort or mo in cohort:
        raise OrchestrationError("leave-target-and-family-out violado")
    contig, ws, we = window
    bcf = ds.region_bcf(window)
    joint = cohort_inputs(rn, bcf, cohort, kid, wd)
    joint = exclude_masked(rn, joint, m.phasing_intervals(), contig, f"{wd}/joint_masked.bcf", cohort + [kid])
    _, rs, re_ = phasing_region(window, BUFFER_BP, ds.lengths)
    mid = (rs + re_) // 2
    chunks = [(contig, rs, mid + BUFFER_BP), (contig, mid - BUFFER_BP + 1, re_)]
    region = tools.region_str(contig, rs, re_)
    # A′ (EXEC-DEF-PH1-001): sin phase_rare; el scaffold común (MAF ≥ 0,1 %) es la salida faseada.
    phased = phase(rn, joint, chunks, region, ds.gmap(contig), wd, rare=False)
    if m.phasing_intervals():
        require_unmasked(rn, phased, contig, m.phasing_intervals(), "fase")
    truth_items = m.truth_intervals()
    ser_for_child(rn, phased, bcf, trio, region, wd, ANALYTIC_MAF, "analytic", truth_items, contig)
    ser_for_child(rn, phased, bcf, trio, region, wd, SCAFFOLD_MAF, "scaffold", truth_items, contig)
    ser_a, ser_s = _switch_counts(rn, wd, "analytic", kid), _switch_counts(rn, wd, "scaffold", kid)

    maf = cohort_maf(rn, f"{wd}/cohort_tags.bcf", window)
    info = trio_info(rn, bcf, trio, window)
    phased_gt = {}
    for line in rn.query(phased, "%POS\t%REF\t%ALT[\t%GT]\n", samples=kid):
        p, ref, alt, g = line.split("\t")
        if ws <= int(p) <= we:
            phased_gt[(int(p), ref, alt)] = g
    candidates = [(p, info[p]["ref"]) for p in sorted(info) if analytic(info, maf, p)]
    keep, no_truth, audit = masks_mod.window_audit(contig, candidates, m, window)
    key = lambda p: (p, info[p]["ref"], info[p]["alt"])
    audit["n_not_in_phased_output"] = sum(key(p) not in phased_gt for p in keep)
    win_sites = sorted(p for p in keep if key(p) in phased_gt)
    ad = ad_by_allele(rn, ds.alignment(kid), ds.reference, contig,
                      {p: (info[p]["ref"], info[p]["alt"]) for p in win_sites}, wd)
    audit["n_without_ad"] = sum(p not in ad for p in win_sites)
    rows = []
    for p in win_sites:
        g = phased_gt[key(p)]
        if "|" not in g:
            raise OrchestrationError(f"het sin fasear en la salida para {kid}:{p} ({g})")
        if p not in ad:
            continue
        pat = None if p in no_truth else truth.paternal_allele(info[p]["kid"], info[p]["fa"], info[p]["mo"])
        rows.append([ad[p][0], ad[p][1], int(g.split("|")[0]), -1 if pat is None else pat])
    res = {"child": kid, "window": wid, "is_bub1b": tuple(window) == tuple(ds.bub1b), "rows": rows,
           "audit": audit, "ser_analytic": ser_a, "ser_scaffold": ser_s}
    if not keep_intermediates:
        _cleanup(rn, wd)
    res_path.write_text(json.dumps(res), encoding="utf-8", newline="\n")
    return res


def calibration_job(ds: Dataset, trio, tile) -> dict:
    kid = trio[0]
    wid = window_id(*tile)
    wd = job_dir(ds, "cal", kid, tile)
    res_path = ds.mount / wd / "result.json"
    if res_path.exists():
        return json.loads(res_path.read_text(encoding="utf-8"))
    rn = LoggedRunner(ds.mount, wd)
    m = ds.site_masks(kid)
    cohort = selection.conditioning_cohort(ds.phase3, kid, ds.pedigree)
    bcf = ds.region_bcf(tile)
    write_lines(rn.mount / f"{wd}/cohort.txt", cohort)
    rn.run(tools.BCFTOOLS_IMAGE, tools.cohort_subset_cmd(_d(bcf), _d(f"{wd}/cohort.txt"), _d(f"{wd}/cohort.bcf")))
    rn.out(f"{wd}/cohort.bcf")
    rn.index(f"{wd}/cohort.bcf")
    require_samples(rn, f"{wd}/cohort.bcf", cohort)
    rn.run(tools.BCFTOOLS_IMAGE, tools.cohort_tags_cmd(_d(f"{wd}/cohort.bcf"), _d(f"{wd}/cohort_tags.bcf")))
    rn.out(f"{wd}/cohort_tags.bcf")
    rn.index(f"{wd}/cohort_tags.bcf")
    contig = tile[0]
    maf = cohort_maf(rn, f"{wd}/cohort_tags.bcf", tile)
    info = trio_info(rn, bcf, trio, tile)
    sites = {p: (info[p]["ref"], info[p]["alt"]) for p in sorted(info)
             if analytic(info, maf, p) and not masks_mod.intact_excluded(m.flags(contig, p, info[p]["ref"]))}
    ad = ad_by_allele(rn, ds.alignment(kid), ds.reference, contig, sites, wd)
    b, n = [], []
    for p in sorted(ad):
        tot = sum(ad[p])
        if tot > 0:
            n.append(tot)
            b.append(ad[p][1] / tot)
    res = {"child": kid, "tile": wid, "b": b, "n": n, "n_sites": len(sites), "n_with_ad": len(ad)}
    _cleanup(rn, wd)
    res_path.write_text(json.dumps(res), encoding="utf-8", newline="\n")
    return res


# ---------------------------------------------------------------------- manifest de ejecución
EXECUTION_TAG = "exp027-phase1-execution-freeze-r2"
SUPERSEDED = {
    "supersedes_execution_tag": "exp027-phase1-execution-freeze",
    "previous_attempt_status": "ABORTED_TECHNICAL",
    "previous_attempt_dir": "work/exp027/phase1",
    "rare_phasing_in_phase1": False,
    "reason": ("EXEC-DEF-PH1-001: SHAPEIT5_phase_rare (5.1.1) aborta de forma determinista "
               "(Assertion !isnan(...prob) en phaseLiAndStephens) con genotipos ausentes en variantes "
               "raras; ningún endpoint adjudicable de Phase 1 usa variantes raras y A2 es UNSCORABLE. "
               "Phase 1 termina la fase tras phase_common + ligate y usa el scaffold."),
    "scaffold_invariance_test": "src/exp027/validate_r2.py (work/exp027/validation_r2/VALIDATION.json)",
}


def _git(*args) -> str:
    import subprocess
    p = subprocess.run(["git", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise OrchestrationError(f"git {' '.join(args)} falló: {p.stderr.strip()}")
    return p.stdout.strip()


def _sha_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def run_manifest(ds: Dataset, plan_dir: Path, data: Path, workers: int, b: int) -> dict:
    """Qué código y qué bytes producen el resultado. Barrera: HEAD debe ser el commit del tag de
    ejecución y src/, config/ y tests/ no pueden tener cambios sin commitear."""
    import datetime as dt
    import os
    import platform
    import subprocess
    head = _git("rev-parse", "HEAD")
    tagged = _git("rev-parse", f"{EXECUTION_TAG}^{{commit}}")
    if head != tagged:
        raise OrchestrationError(f"HEAD {head[:12]} no es el tag {EXECUTION_TAG} ({tagged[:12]})")
    dirty = _git("status", "--porcelain", "--", "src", "config", "tests")
    if dirty:
        raise OrchestrationError(f"cambios sin commitear en src/config/tests:\n{dirty}")
    goB = json.loads((data / "goB/MANIFEST_goB.json").read_text(encoding="utf-8"))
    der = json.loads((data / "goB/MANIFEST_goB_derived.json").read_text(encoding="utf-8"))
    mat = json.loads((data / "MANIFEST.json").read_text(encoding="utf-8"))
    images = {}
    for ref in (tools.SHAPEIT5_IMAGE, tools.BCFTOOLS_IMAGE, SAMTOOLS_IMAGE):
        r = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", ref], capture_output=True, text=True)
        images[ref] = r.stdout.strip()
    return {
        "experiment": "EXP-027 Phase 1",
        "commit": head, "tag": EXECUTION_TAG, "tag_commit": tagged, **SUPERSEDED,
        "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "workers": workers, "B": b, "deltas": list(DELTA_GRID),
        "children": [t[0] for t in ds.trios], "n_evaluation": len(ds.evaluation),
        "n_calibration": len(ds.calibration),
        "plan": {"plan_windows.json": _sha_file(plan_dir / "plan_windows.json"),
                 **{f"masks/{p.name}": _sha_file(p) for p in sorted((plan_dir / "masks").glob("*.bed"))}},
        "config": {p: _sha_file(Path(p)) for p in ("config/exp027_benchmark.yaml", "config/exp027_tool_manifest.json")},
        "goB_raw_sha256": {k: v["sha256"] for k, v in sorted(goB.items())},
        "goB_derived_sha256": {k: v["sha256"] for k, v in sorted(der.items())},
        "goA_sha256": {k: v["sha256"] for k, v in sorted(mat.items())},
        "images": images,
        "host": {"platform": platform.platform(), "cpus": os.cpu_count(), "python": platform.python_version()},
    }


# ---------------------------------------------------------------------- ensamblado
def assemble(ds: Dataset, win_results, cal_results) -> dict:
    children = {}
    for kid, _, _ in ds.trios:
        wins = [r for r in win_results if r["child"] == kid]
        cals = [r for r in cal_results if r["child"] == kid]
        ea = sum(r["ser_analytic"][0] for r in wins)
        na = sum(r["ser_analytic"][1] for r in wins)
        es = sum(r["ser_scaffold"][0] for r in wins)
        ns = sum(r["ser_scaffold"][1] for r in wins)
        windows = {}
        for r in wins:
            arr = np.array(r["rows"], dtype=np.int64).reshape(-1, 4)
            windows[r["window"]] = (evaluate.WindowSites(arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3],
                                                         np.ones(len(arr), bool), r["audit"]), r["is_bub1b"])
        children[kid] = {"superpop": ds.superpop[kid],
                         "ser": ea / na if na else None, "ser_scaffold": es / ns if ns else None,
                         "ser_counts": {"analytic": [ea, na], "scaffold": [es, ns]},
                         "calibration": (np.array([x for r in cals for x in r["b"]], float),
                                         np.array([x for r in cals for x in r["n"]], float)),
                         "windows": windows}
    return children


class JobFailed(OrchestrationError):
    pass


def kill_run_containers() -> int:
    """Mata los contenedores Docker etiquetados con la etiqueta de este proceso."""
    ids = subprocess.run(["docker", "ps", "-q", "--filter", f"label=exp027_run={RUN_LABEL}"],
                         capture_output=True, text=True).stdout.split()
    if ids:
        subprocess.run(["docker", "kill", *ids], capture_output=True, text=True)
    return len(ids)


def _job_log_tail(path: Path, n: int = 8) -> list:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()[-n:] if l.strip()]


def run(ds: Dataset, workers: int, b: int, deltas=DELTA_GRID, log=None) -> dict:
    """Ejecuta todos los trabajos. Nada falla en silencio: progress.log y status.json en cada trabajo,
    y la primera excepción detiene el run (FAILED_JOB.json + contenedores muertos + JobFailed)."""
    for img in (tools.SHAPEIT5_IMAGE, tools.BCFTOOLS_IMAGE, SAMTOOLS_IMAGE):
        check_image(img)
    out_dir = ds.mount / ds.out
    out_dir.mkdir(parents=True, exist_ok=True)
    progress = open(out_dir / "progress.log", "a", encoding="utf-8", newline="\n")

    def say(msg: str) -> None:
        line = f"{_now()} {msg}"
        progress.write(line + "\n")
        progress.flush()
        if log is not None:
            log(line)

    t0 = time.time()
    jobs = [("win", t, w) for t in ds.trios for w in ds.evaluation] + \
           [("cal", t, w) for t in ds.trios for w in ds.calibration]
    lock = threading.Lock()
    first_failure = threading.Lock()                     # solo se registra el primer fallo de este run
    running: dict = {}
    counts = {"done": 0, "total": len(jobs)}

    def status(state: str, extra: dict | None = None) -> None:
        with lock:
            snap = {"state": state, "updated_utc": _now(), "run_label": RUN_LABEL, **counts,
                    "elapsed_s": round(time.time() - t0), "running": sorted(running.values()), **(extra or {})}
        _write_atomic(out_dir / "status.json", json.dumps(snap, indent=1))

    def tracked(kind, trio, w):
        tag = f"{kind} {trio[0]} {window_id(*w)}"
        with lock:
            running[tag] = f"{tag} desde {_now()}"
        try:
            return (window_job if kind == "win" else calibration_job)(ds, trio, w)
        finally:
            with lock:
                running.pop(tag, None)

    say(f"inicio: {len(jobs)} trabajos, {workers} workers, etiqueta {RUN_LABEL}")
    status("RUNNING")
    win_results, cal_results = [], []
    ex = ThreadPoolExecutor(max_workers=workers)
    futs = {ex.submit(tracked, k, t, w): (k, t, w) for k, t, w in jobs}
    try:
        for fut in as_completed(futs):
            k, trio, w = futs[fut]
            try:
                r = fut.result()
            except Exception as exc:                           # primera excepción: se para todo
                if not first_failure.acquire(blocking=False):
                    raise
                ex.shutdown(wait=False, cancel_futures=True)
                with lock:
                    running_at_failure = sorted(running.values())
                killed = kill_run_containers()
                wd = job_dir(ds, k, trio[0], w)
                failed = {"utc": _now(), "kind": k, "child": trio[0], "window": window_id(*w), "job_dir": wd,
                          "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc(),
                          "last_commands": _job_log_tail(ds.mount / wd / "job.log"),
                          "running_at_failure": running_at_failure, "run_label": RUN_LABEL,
                          "containers_killed": killed, "done_before_failure": counts["done"]}
                if (out_dir / "FAILED_JOB.json").exists():      # nunca se sobrescribe un fallo previo
                    raise JobFailed("ya existe FAILED_JOB.json en el directorio del run") from exc
                _write_atomic(out_dir / "FAILED_JOB.json", json.dumps(failed, indent=2))
                say(f"FALLO {k} {trio[0]} {window_id(*w)}: {type(exc).__name__}: {exc} -> FAILED_JOB.json")
                status("FAILED", {"failed_job": f"{k} {trio[0]} {window_id(*w)}"})
                raise JobFailed(f"trabajo fallido {k} {trio[0]} {window_id(*w)}: {exc}") from exc
            (win_results if k == "win" else cal_results).append(r)
            with lock:
                counts["done"] += 1
            say(f"[{counts['done']}/{len(jobs)}] {k} {trio[0]} {window_id(*w)} · {time.time() - t0:.0f}s")
            status("RUNNING")
    finally:
        ex.shutdown(wait=False, cancel_futures=True)
    say("trabajos completos; evaluación (permutaciones y spike-in)")
    status("EVALUATING")
    children = assemble(ds, win_results, cal_results)
    result = evaluate.run_benchmark(children, b=b, deltas_grid=deltas)
    report = result["report"]
    report["ser_counts"] = {k: v["ser_counts"] for k, v in children.items()}
    report["audit"] = {k: {wid: w["audit"] for wid, w in r["windows"].items()}
                       for k, r in result["results"]["children"].items()}
    report["run"] = {"children": len(ds.trios), "evaluation_windows": len(ds.evaluation),
                     "calibration_tiles": len(ds.calibration), "B": b, "deltas": list(deltas),
                     "seconds": round(time.time() - t0)}
    out = ds.mount / ds.out / "phase1_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8", newline="\n")
    say(f"FIN: phase1_report.json escrito ({report.get('phase1_global')})")
    status("DONE")
    progress.close()
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ejecutor real de Phase 1 de EXP-027")
    sub = ap.add_subparsers(dest="mode", required=True)
    t = sub.add_parser("toy")
    t.add_argument("--out", type=Path, required=True)
    t.add_argument("--b", type=int, default=200)
    t.add_argument("--workers", type=int, default=4)
    r = sub.add_parser("real")
    r.add_argument("--plan", type=Path, default=Path("work/exp027/plan_execution"))  # máscaras con regla A
    r.add_argument("--workers", type=int, default=16)   # operacional: solo cambia el tiempo de reloj
    a = ap.parse_args(argv)
    if a.mode == "toy":
        if a.out.exists():
            shutil.rmtree(a.out)
        ds = Dataset.toy(a.out)
        rep = run(ds, a.workers, a.b, deltas=(0.00, 0.10), log=lambda m: print(m, flush=True))
    else:
        import yaml
        root = Path(yaml.safe_load(Path("config/paths.yaml").read_text(encoding="utf-8"))["compute"]["docker_repo_root"])
        ds = Dataset.from_plan(a.plan, "work/exp027/data", root)
        b = evaluate.stats.B_PERMUTATIONS
        man = run_manifest(ds, a.plan, root / "work/exp027/data", a.workers, b)
        mpath = root / ds.out / "RUN_MANIFEST.json"
        mpath.parent.mkdir(parents=True, exist_ok=True)
        if mpath.exists():                       # reanudación: solo con el mismo código y los mismos bytes
            prev = json.loads(mpath.read_text(encoding="utf-8"))
            same = all(prev[k] == man[k] for k in ("commit", "plan", "config", "goB_raw_sha256",
                                                    "goB_derived_sha256", "images"))
            if not same:
                raise OrchestrationError("RUN_MANIFEST existente con otro código o entradas: no se reanuda")
            man["resumed_utc"], man["started_utc"] = man["started_utc"], prev["started_utc"]
        mpath.write_text(json.dumps(man, indent=2), encoding="utf-8", newline="\n")
        try:
            rep = run(ds, a.workers, b, log=lambda m: print(m, flush=True))
        except JobFailed:
            raise                                   # FAILED_JOB.json ya escrito
        except BaseException as exc:                # cualquier otro fallo también deja rastro
            kill_run_containers()
            _write_atomic(root / ds.out / "FAILED_RUN.json", json.dumps(
                {"utc": _now(), "run_label": RUN_LABEL, "error": f"{type(exc).__name__}: {exc}",
                 "traceback": traceback.format_exc()}, indent=2))
            raise
    print(json.dumps({k: rep.get(k) for k in ("phase1_global", "a1_applicable", "apr_k", "apr_n",
                                              "apr_p_binom_one_sided", "sensitivity_inferred",
                                              "retention", "ser", "fail_reasons", "run")},
                     indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
