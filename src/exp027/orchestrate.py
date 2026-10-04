"""Orquestador de EXP-027: herramientas reales en Docker -> evaluate -> informe de Phase 1.

Cadena por hijo: subconjunto C_target -> AC/AN/MAF solo en C_target -> entrada conjunta
(C_target ∪ {objetivo}) anotada -> sin sitios enmascarados (Amendment 8: globales + copy-changing
del hijo) -> phase_common por chunks solapados -> ligate (L_isec > 0) ->
phase_rare -> SER con switch -P (verdad mendeliana) -> AD con bcftools mpileup -> WindowSites ->
evaluate.run_benchmark -> informe.

Falla fuerte si: una imagen no está en local o su digest no coincide (no se descarga nada), falta
una salida, ligate no muestra solape real, un comando viola una regla congelada (--pedigree en la
inferencia, --reference externo, sin mapa) o una salida no tiene el formato esperado.

Uso (solo datos sintéticos de juguete en esta etapa):
    python -m src.exp027.orchestrate toy --out work/exp027/toy_orchestrator
"""
from __future__ import annotations

import argparse
import gzip
import json
import subprocess
from pathlib import Path

import numpy as np

from . import evaluate, masks as masks_mod, selection, tools, toy_data, truth
from .serialize import window_id
from .windows import Intervals

SAMTOOLS_IMAGE = "quay.io/biocontainers/samtools@sha256:783c6646029a306ec5e4162009dc1a20d8f6c528f7c380e5b4affbf12d9112e5"
BUFFER_BP = 250_000
ANALYTIC_MAF = 0.01
SCAFFOLD_MAF = 0.001
GQ_MIN = 30


class OrchestrationError(RuntimeError):
    pass


# --- Docker ------------------------------------------------------------------------------------
def docker_available() -> bool:
    r = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], capture_output=True, text=True)
    return r.returncode == 0 and bool(r.stdout.strip())


def check_image(ref: str) -> None:
    """La imagen debe estar en local y con el digest congelado. Nunca se descarga aquí.

    Distingue tres fallos: el daemon de Docker no responde, la imagen no está en local y el digest
    no coincide. Un daemon apagado no debe leerse como «falta la imagen» (no hay que descargar nada).
    """
    if not docker_available():
        raise OrchestrationError("el daemon de Docker no responde: arranca Docker Desktop y repite "
                                 "(no se descarga ninguna imagen)")
    name, digest = ref.split("@")
    r = subprocess.run(["docker", "image", "inspect", "--format", "{{json .RepoDigests}}", ref],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise OrchestrationError(f"imagen no disponible en local (no se descarga): {ref}")
    if f"{name}@{digest}" not in json.loads(r.stdout.strip() or "[]"):
        raise OrchestrationError(f"el digest de la imagen no coincide con el congelado: {ref}")


class Runner:
    def __init__(self, mount: Path):
        self.mount = mount.resolve()

    def run(self, image: str, cmd: list[str]) -> subprocess.CompletedProcess:
        full = tools.docker_cmd(image, str(self.mount), cmd)       # aplica assert_frozen
        return subprocess.run(full, capture_output=True, text=True)

    def bcf(self, *args: str) -> subprocess.CompletedProcess:
        return self.run(tools.BCFTOOLS_IMAGE, ["bcftools", *args])

    def out(self, rel: str) -> Path:
        return tools.require_output(self.mount / rel)

    def index(self, rel: str) -> None:
        r = self.bcf("index", "-f", f"/data/{rel}")
        if r.returncode != 0:
            raise OrchestrationError(f"bcftools index falló en {rel}: {r.stderr[-400:]}")

    def query(self, rel: str, fmt: str, samples: str | None = None) -> list[str]:
        args = ["query", "-f", fmt]
        if samples:
            args += ["-s", samples]
        r = self.bcf(*args, f"/data/{rel}")
        if r.returncode != 0:
            raise OrchestrationError(f"bcftools query falló en {rel}: {r.stderr[-400:]}")
        return [l for l in r.stdout.splitlines() if l]


def _d(rel: str) -> str:
    return f"/data/{rel}"


def write_lines(path: Path, lines) -> None:
    """Texto para las herramientas, siempre con LF. En Windows, write_text pondría CRLF y la
    herramienta leería nombres terminados en retorno de carro (ligate no encontraba los chunks)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write("".join(f"{line}\n" for line in lines))


def require_samples(rn: "Runner", rel: str, expected) -> None:
    """La salida debe contener exactamente las muestras esperadas."""
    got = rn.bcf("query", "-l", _d(rel)).stdout.split()
    if sorted(got) != sorted(expected):
        raise OrchestrationError(f"{rel}: {len(got)} muestras, se esperaban {len(expected)}")


# --- pasos ---------------------------------------------------------------------------------------
def prepare_toy_bams(rn: Runner, children) -> None:
    for kid in children:
        r = rn.run(SAMTOOLS_IMAGE, ["sh", "-c", f"samtools sort -o /data/{kid}.bam /data/{kid}.sam "
                                                f"&& samtools index /data/{kid}.bam"])
        rn.out(f"{kid}.bam")
    r = rn.run(SAMTOOLS_IMAGE, ["samtools", "faidx", "/data/ref.fa"])
    rn.out("ref.fa.fai")


def cohort_inputs(rn: Runner, all_bcf: str, cohort, child: str, wd: str) -> str:
    """AC/AN/MAF calculados solo en C_target y copiados a la entrada conjunta (Amendment 7)."""
    write_lines(rn.mount / f"{wd}/cohort.txt", cohort)
    write_lines(rn.mount / f"{wd}/joint.txt", cohort + [child])
    steps = [
        tools.cohort_subset_cmd(_d(all_bcf), _d(f"{wd}/cohort.txt"), _d(f"{wd}/cohort.bcf")),
        tools.cohort_tags_cmd(_d(f"{wd}/cohort.bcf"), _d(f"{wd}/cohort_tags.bcf")),
        tools.cohort_subset_cmd(_d(all_bcf), _d(f"{wd}/joint.txt"), _d(f"{wd}/joint.bcf")),
    ]
    outs = ["cohort.bcf", "cohort_tags.bcf", "joint.bcf"]
    expected = [cohort, cohort, cohort + [child]]
    for cmd, o, exp in zip(steps, outs, expected):
        rn.run(tools.BCFTOOLS_IMAGE, cmd)
        rn.out(f"{wd}/{o}")
        rn.index(f"{wd}/{o}")
        require_samples(rn, f"{wd}/{o}", exp)
    rn.run(tools.BCFTOOLS_IMAGE, tools.annotate_cohort_tags_cmd(_d(f"{wd}/joint.bcf"),
                                                                _d(f"{wd}/cohort_tags.bcf"),
                                                                _d(f"{wd}/joint_ann.bcf")))
    rn.out(f"{wd}/joint_ann.bcf")
    rn.index(f"{wd}/joint_ann.bcf")
    return f"{wd}/joint_ann.bcf"


def phase(rn: Runner, joint: str, chunks, region: str, gmap: str, wd: str) -> str:
    """phase_common por chunks solapados -> ligate con solape real -> phase_rare sobre el scaffold."""
    lst = []
    for i, (c, s, e) in enumerate(chunks):
        out = f"{wd}/common_{i}.bcf"
        rn.run(tools.SHAPEIT5_IMAGE, tools.phase_common_cmd(_d(joint), tools.region_str(c, s, e), _d(gmap), _d(out)))
        rn.out(out)
        rn.index(out)
        lst.append(_d(out))
    write_lines(rn.mount / f"{wd}/chunks.txt", lst)
    r = rn.run(tools.SHAPEIT5_IMAGE, tools.ligate_cmd(_d(f"{wd}/chunks.txt"), _d(f"{wd}/scaffold.bcf")))
    tools.require_ligate_overlap(r.stdout + r.stderr, len(chunks))
    rn.out(f"{wd}/scaffold.bcf")
    rn.index(f"{wd}/scaffold.bcf")
    rn.run(tools.SHAPEIT5_IMAGE, tools.phase_rare_cmd(_d(joint), region, _d(f"{wd}/scaffold.bcf"),
                                                      region, _d(gmap), _d(f"{wd}/phased.bcf")))
    rn.out(f"{wd}/phased.bcf")
    rn.index(f"{wd}/phased.bcf")
    return f"{wd}/phased.bcf"


def exclude_masked(rn: Runner, src: str, bed_items, contig: str, dst: str, expected=None) -> str:
    """Retira los sitios cuyo span toca los intervalos (Amendment 8). Sin intervalos, no hace nada."""
    lines = masks_mod.bed_lines(bed_items, contig)
    if not lines:
        return src
    bed = dst.rsplit(".", 1)[0] + ".mask.bed"
    write_lines(rn.mount / bed, lines)
    rn.run(tools.BCFTOOLS_IMAGE, tools.exclude_regions_cmd(_d(src), _d(bed), _d(dst)))
    rn.out(dst)
    rn.index(dst)
    if expected is not None:
        require_samples(rn, dst, expected)
    return dst


def require_unmasked(rn: Runner, rel: str, contig: str, items, what: str) -> int:
    """Fallo fuerte si algún sitio cuyo span toca la máscara sobrevivió en la salida."""
    iv = Intervals(items)
    rows = rn.query(rel, "%POS\t%REF\n")
    for line in rows:
        pos, ref = line.split("\t")
        s, e = masks_mod.marker_span(int(pos), ref)
        if iv.hits(contig, s, e):
            raise OrchestrationError(f"{what}: el sitio enmascarado {contig}:{pos} sigue en {rel}")
    return len(rows)


def ser_for_child(rn: Runner, phased: str, all_bcf: str, trio, region: str, wd: str, maf: float, tag: str,
                  truth_items=(), contig: str = "") -> float:
    """SER del hijo con verdad mendeliana (switch -P), en marcadores con MAF de C_target ≥ maf.

    Amendment 8 r8: sobre el conjunto sin máscaras globales ni copy-changing de hijo y padres
    (truth_items), tanto en la estimación como en la validación.
    """
    kid, fa, mo = trio
    write_lines(rn.mount / f"{wd}/trio.txt", [kid, fa, mo])
    write_lines(rn.mount / f"{wd}/trio.ped", [f"{kid}\t{fa}\t{mo}"])
    ann = f"{wd}/phased_ann.bcf"
    if not (rn.mount / ann).exists():
        rn.run(tools.BCFTOOLS_IMAGE, tools.annotate_cohort_tags_cmd(_d(phased), _d(f"{wd}/cohort_tags.bcf"), _d(ann)))
        rn.out(ann)
        rn.index(ann)
        rn.bcf("view", "-S", _d(f"{wd}/trio.txt"), "-Ob", "-o", _d(f"{wd}/trio_all.bcf"), _d(all_bcf))
        rn.out(f"{wd}/trio_all.bcf")
        rn.index(f"{wd}/trio_all.bcf")
        require_samples(rn, f"{wd}/trio_all.bcf", [kid, fa, mo])
        validation = exclude_masked(rn, f"{wd}/trio_all.bcf", truth_items, contig, f"{wd}/trio.bcf", [kid, fa, mo])
        if validation != f"{wd}/trio.bcf":
            rn.bcf("view", "-Ob", "-o", _d(f"{wd}/trio.bcf"), _d(validation))
            rn.out(f"{wd}/trio.bcf")
            rn.index(f"{wd}/trio.bcf")
    est_all = f"{wd}/est_{tag}_all.bcf"
    rn.bcf("view", "-i", f"INFO/MAF>={maf}", "-Ob", "-o", _d(est_all), _d(ann))
    rn.out(est_all)
    rn.index(est_all)
    est = exclude_masked(rn, est_all, truth_items, contig, f"{wd}/est_{tag}.bcf")
    if truth_items:
        require_unmasked(rn, est, contig, truth_items, "SER")
    rn.run(tools.SHAPEIT5_IMAGE, tools.switch_cmd(_d(f"{wd}/trio.bcf"), _d(est), _d(f"{wd}/trio.ped"),
                                                  region, _d(f"{wd}/ser_{tag}")))
    path = rn.out(f"{wd}/ser_{tag}.sample.switch.txt.gz")
    with gzip.open(path, "rt") as f:
        ser = tools.parse_switch_sample(f.read().splitlines())
    if kid not in ser:
        raise OrchestrationError(f"switch no reportó SER para {kid}")
    return ser[kid]


def ad_counts(rn: Runner, bam: str, ref: str, sites, contig: str, wd: str) -> dict[int, tuple[int, int]]:
    """Recuentos REF/ALT por posición con el extractor único congelado."""
    sites = sorted(set(sites))                     # mpileup -R respeta el orden dado: debe ir ordenado
    write_lines(rn.mount / f"{wd}/sites.tsv", [f"{contig}\t{p}" for p in sites])
    rn.run(tools.BCFTOOLS_IMAGE, tools.mpileup_cmd(_d(ref), _d(f"{wd}/sites.tsv"), _d(bam), _d(f"{wd}/ad.bcf")))
    rn.out(f"{wd}/ad.bcf")
    rn.index(f"{wd}/ad.bcf")
    out = {}
    for line in rn.query(f"{wd}/ad.bcf", "%POS\t%REF\t%ALT[\t%AD]\n"):
        pos, ref_a, alts, ad = line.split("\t")
        counts = [int(x) for x in ad.split(",")]
        if len(counts) < 2:
            raise OrchestrationError(f"AD con formato inesperado en {pos}: {ad}")
        alt_list = alts.split(",")
        k = alt_list.index("G") + 1 if "G" in alt_list else None
        out[int(pos)] = (counts[0], counts[k] if k is not None else 0)
    return out


def _gt(s: str):
    s = s.replace("|", "/")
    if "." in s:
        return None
    a, b = s.split("/")
    return (int(a), int(b))


def child_inputs(rn: Runner, ds: dict, trio, window, calibration_regions, superpop: str,
                 gmap: str, all_bcf: str, site_masks: masks_mod.SiteMasks | None = None) -> dict:
    kid, fa, mo = trio
    wd = f"run/{kid}"
    m = site_masks or masks_mod.SiteMasks()
    cohort = selection.conditioning_cohort(ds["cohort"], kid, ds["pedigree"])
    if kid in cohort or fa in cohort or mo in cohort:
        raise OrchestrationError("leave-target-and-family-out violado")
    contig, ws, we = window
    joint = cohort_inputs(rn, all_bcf, cohort, kid, wd)
    # Amendment 8 r3: el input específico del objetivo pierde los sitios globales y copy-changing
    # del hijo; sin padding nuevo.
    joint = exclude_masked(rn, joint, m.phasing_intervals(), contig, f"{wd}/joint_masked.bcf", cohort + [kid])

    rs, re_ = max(1, ws - BUFFER_BP), min(ds["ref_len"], we + BUFFER_BP)
    mid = (rs + re_) // 2
    chunks = [(contig, rs, mid + BUFFER_BP), (contig, mid - BUFFER_BP + 1, re_)]
    region = tools.region_str(contig, rs, re_)
    phased = phase(rn, joint, chunks, region, gmap, wd)
    if m.phasing_intervals():
        require_unmasked(rn, phased, contig, m.phasing_intervals(), "fase")

    truth_items = m.truth_intervals()
    ser = ser_for_child(rn, phased, all_bcf, trio, region, wd, ANALYTIC_MAF, "analytic", truth_items, contig)
    ser_scaffold = ser_for_child(rn, phased, all_bcf, trio, region, wd, SCAFFOLD_MAF, "scaffold", truth_items, contig)

    maf = {int(p): float(m_) for p, m_ in (l.split("\t") for l in rn.query(f"{wd}/cohort_tags.bcf", "%POS\t%INFO/MAF\n"))}
    info = {}
    # Cada columna va etiquetada con su muestra: bcftools query -s no garantiza el orden pedido.
    for l in rn.query(all_bcf, "%POS\t%REF\t%FILTER[\t%SAMPLE=%GT=%GQ]\n", samples=f"{kid},{fa},{mo}"):
        f = l.split("\t")
        by = {}
        for cell in f[3:]:
            name, gt, gq = cell.split("=")
            by[name] = (_gt(gt), int(gq) if gq not in (".", "") else -1)
        if set(by) != {kid, fa, mo}:
            raise OrchestrationError(f"muestras inesperadas en la consulta del trio: {sorted(by)}")
        info[int(f[0])] = {"ref": f[1], "filter": f[2], "kid": by[kid][0], "gq": by[kid][1],
                           "fa": by[fa][0], "mo": by[mo][0]}
    phased_gt = {}
    for l in rn.query(phased, "%POS[\t%GT]\n", samples=kid):
        p, g = l.split("\t")
        phased_gt[int(p)] = g

    def analytic(p):
        i = info.get(p)
        return (i is not None and maf.get(p, 0.0) >= ANALYTIC_MAF and i["filter"] == "PASS"
                and i["gq"] >= GQ_MIN and i["kid"] == (0, 1))

    # Amendment 8: los hets analíticos de la ventana se clasifican por máscara antes de medir.
    candidates = [(p, info[p]["ref"]) for p in sorted(info) if ws <= p <= we and analytic(p)]
    keep, no_truth, audit = masks_mod.window_audit(contig, candidates, m, window)
    audit["n_not_in_phased_output"] = sum(p not in phased_gt for p in keep)     # se reporta, como antes
    win_sites = sorted(p for p in keep if p in phased_gt)
    cal_sites = sorted(p for p in info if analytic(p) and any(s <= p <= e for _, s, e in calibration_regions)
                       and not masks_mod.intact_excluded(m.flags(contig, p, info[p]["ref"])))
    ad = ad_counts(rn, f"{kid}.bam", "ref.fa", win_sites + cal_sites, contig, wd)

    rows = []
    for p in win_sites:
        g = phased_gt[p]
        if "|" not in g:
            raise OrchestrationError(f"het sin fasear en la salida para {kid}:{p} ({g})")
        if p not in ad:
            continue
        pat = None if p in no_truth else truth.paternal_allele(info[p]["kid"], info[p]["fa"], info[p]["mo"])
        rows.append((ad[p][0], ad[p][1], int(g.split("|")[0]), -1 if pat is None else pat))
    arr = np.array(rows, dtype=np.int64).reshape(-1, 4)
    sites = evaluate.WindowSites(arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], np.ones(len(arr), bool), audit)
    cn = np.array([sum(ad[p]) for p in cal_sites if p in ad and sum(ad[p]) > 0], float)
    cb = np.array([ad[p][1] / sum(ad[p]) for p in cal_sites if p in ad and sum(ad[p]) > 0], float)
    return {"superpop": superpop, "ser": ser, "ser_scaffold": ser_scaffold, "calibration": (cb, cn),
            "windows": {window_id(*window): (sites, True)}}


def run_toy(out: Path, b: int = 200, deltas=(0.00, 0.10)) -> dict:
    for img in (tools.SHAPEIT5_IMAGE, tools.BCFTOOLS_IMAGE, SAMTOOLS_IMAGE):
        check_image(img)
    ds = toy_data.build(out)
    rn = Runner(out)
    prepare_toy_bams(rn, ds["children"])
    rn.bcf("view", "-Ob", "-o", "/data/all.bcf", "/data/joint.vcf")
    rn.out("all.bcf")
    rn.index("all.bcf")
    gmap = "toy.gmap.gz"
    rn.out(gmap)
    contig = ds["contig"]
    window = (contig, 500_001, 2_500_000)                        # ventana "locus" del juguete
    calib = [(contig, 1, 250_000), (contig, 2_750_001, ds["ref_len"])]
    kids = {}
    for i, trio in enumerate(ds["pedigree"]):
        sp = selection.SUPERPOPULATIONS[i % len(selection.SUPERPOPULATIONS)]
        kids[trio[0]] = child_inputs(rn, ds, trio, window, calib, sp, gmap, "all.bcf",
                                     toy_data.site_masks(trio[0]))
    result = evaluate.run_benchmark(kids, b=b, deltas_grid=deltas)
    report = result["report"]
    wid = window_id(*window)
    report["toy"] = {"children": len(kids), "window": wid,
                     "hets_per_child": {c: int(k["windows"][wid][0].n_ref.size) for c, k in kids.items()},
                     "audit": {c: r["windows"][wid]["audit"] for c, r in result["results"]["children"].items()}}
    (out / "report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Orquestador de EXP-027 (solo juguete en esta etapa)")
    sub = ap.add_subparsers(dest="mode", required=True)
    t = sub.add_parser("toy")
    t.add_argument("--out", type=Path, required=True)
    t.add_argument("--b", type=int, default=200)
    args = ap.parse_args(argv)
    rep = run_toy(args.out, b=args.b)
    print(json.dumps({k: rep[k] for k in ("phase1_global", "a1_applicable", "apr_k", "apr_n",
                                          "apr_p_binom_one_sided", "sensitivity_inferred",
                                          "retention", "ser", "ser_scaffold_descriptive",
                                          "fail_reasons", "toy")}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
