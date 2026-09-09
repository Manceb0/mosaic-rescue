#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QC e integridad del alineamiento: parseo de salidas de samtools/bcftools/VerifyBamID2
y escritura de work/align/alignment_manifest.json y qc_summary.json.

Subcomandos (los usa run_alignment.sh):
    regions   imprime las regiones de profundidad: BUB1B +/-50 kb, +/-1 Mb
    sites     escribe work/align/integrity/sites.tsv: 20 000 sitios PASS (semilla 42)
              con el genotipo del VCF para la concordancia
    summary   calcula todo y escribe manifest + resumen; imprime el resumen sin
              coordenadas ni identificadores

Claim maximo de integridad: "The reconstructed alignment is technically
concordant with the supplied variant dataset." Sexo: "genomic sex concordance
consistent with the declared XY configuration". Nada de identidad.
"""
from __future__ import annotations
import glob, gzip, hashlib, io, json, os, random, re, statistics, sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

W = "work/align"
BAM = os.path.join(W, "full_depth.markdup.bam")
PAR_X = [(10001, 2781479), (155701383, 156030895)]      # GRCh38 PAR1/PAR2 en X


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _tx():
    from src.structure.transcript_model import fetch
    tx = fetch(); ex = [(e["start"], e["end"]) for e in tx["exons"]]
    return min(a for a, _ in ex), max(b for _, b in ex)


def regions():
    from src.model_outputs.alphagenome_common import resolve_candidate
    chrom = resolve_candidate()["chromosome"].replace("chr", "")
    lo, hi = _tx()
    print(f"BUB1B_pm50kb\t{chrom}:{max(1, lo - 50000)}-{hi + 50000}")
    print(f"BUB1B_pm1Mb\t{chrom}:{max(1, lo - 1000000)}-{hi + 1000000}")


def depth():
    """Resume `samtools depth` de stdin: bases, media y mediana.

    En Python y no en awk: el awk del contenedor es mawk y no tiene asort(),
    de modo que la primera version escribia un fichero vacio SIN fallar.
    """
    name = sys.argv[2] if len(sys.argv) > 2 else "region"
    vals = []
    for line in sys.stdin:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            vals.append(int(p[2]))
    if not vals:
        print(f"{name}\t0\t0\t0"); return
    vals.sort()
    n = len(vals)
    print(f"{name}\t{n}\t{sum(vals) / n:.2f}\t{vals[n // 2]}")


def sites(n=20000, seed=42):
    from src.paths import patient_vcf
    rng = random.Random(seed); rows = []
    with gzip.open(patient_vcf(), "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.split("\t", 10)
            if p[6] != "PASS" or len(p[3]) != 1 or "," in p[4] or len(p[4]) != 1:
                continue
            if rng.random() < 0.01:
                rows.append((p[0], int(p[1]), p[3], p[4], p[9].split(":")[0]))
    rng.shuffle(rows); rows = sorted(rows[:n])
    os.makedirs(os.path.join(W, "integrity"), exist_ok=True)
    with io.open(os.path.join(W, "integrity", "sites.tsv"), "w", newline="\n") as f:
        for c, q, _r, _a, _g in rows:
            f.write(f"{c}\t{q}\n")
    with io.open(os.path.join(W, "integrity", "sites_truth.tsv"), "w", newline="\n") as f:
        for c, q, r, a, g in rows:
            f.write(f"{c}\t{q}\t{r}\t{a}\t{g}\n")
    print(len(rows))


def _flagstat(path):
    out = {}
    for line in io.open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"(\d+) \+ (\d+) (.+?)(?: \((\S+) : \S+\))?$", line.strip())
        if m:
            key = m.group(3).split(" (")[0]
            out[key] = {"n": int(m.group(1)), "pct": m.group(4)}
    return out


def _stats(path):
    out = {}
    for line in io.open(path, encoding="utf-8", errors="replace"):
        if line.startswith("SN\t"):
            k, v = line.split("\t")[1].rstrip(":"), line.split("\t")[2].strip()
            out[k] = v
    return out


def _concordance():
    truth = {}
    for line in io.open(os.path.join(W, "integrity", "sites_truth.tsv")):
        c, q, r, a, g = line.rstrip("\n").split("\t")
        truth[(c, int(q))] = (r, a, g.replace("|", "/"))
    calls = {}
    p = os.path.join(W, "integrity", "bam_calls.vcf.gz")
    if not os.path.exists(p):
        return {"status": "bam_calls.vcf.gz missing"}
    with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            x = line.split("\t", 10)
            calls[(x[0], int(x[1]))] = (x[3], x[4], x[9].split(":")[0].replace("|", "/"))
    n = agree = compared = 0
    for k, (r, a, g) in truth.items():
        n += 1
        if k not in calls:
            continue
        cr, ca, cg = calls[k]
        if cr != r:
            continue
        compared += 1
        # genotipo del BAM en terminos del ALT del VCF
        alts = ca.split(",")
        idx = {"0": "0"}
        for i, al in enumerate(alts, 1):
            idx[str(i)] = "1" if al == a else "x"
        cg2 = "/".join(sorted(idx.get(s, "x") for s in cg.split("/")))
        if cg2 == "/".join(sorted(g.split("/"))):
            agree += 1
    return {"sites_sampled": n, "sites_compared": compared, "genotype_concordant": agree,
            "concordance": (agree / compared) if compared else None}


def _verifybamid2():
    p = os.path.join(W, "integrity", "vb", "vb2.selfSM")
    if not os.path.exists(p):
        return {"status": "not available"}
    rows = [l.rstrip("\n").split("\t") for l in io.open(p, encoding="utf-8")]
    hdr = rows[0]; val = rows[1]
    d = dict(zip(hdr, val))
    return {"FREEMIX_alpha": d.get("FREEMIX") or d.get("Alpha"), "raw": d}


def _x_nonpar_het():
    from src.paths import patient_vcf
    het = hom = 0
    with gzip.open(patient_vcf(), "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.split("\t", 10)
            if p[0] != "X" or p[6] != "PASS":
                continue
            q = int(p[1])
            if any(a <= q <= b for a, b in PAR_X):
                continue
            g = p[9].split(":")[0].replace("|", "/")
            if g in ("0/1", "1/0"):
                het += 1
            elif g == "1/1":
                hom += 1
    return {"het": het, "hom": hom, "het_fraction": het / (het + hom) if het + hom else None}


def summary():
    cfg = json.load(io.open(os.path.join(W, "run_config.json")))
    cov = {}
    for line in io.open(os.path.join(W, "qc", "coverage_by_contig.tsv"), encoding="utf-8"):
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        cov[p[0]] = {"length": int(p[2]) - int(p[1]) + 1, "meandepth": float(p[6]), "coverage_pct": float(p[5])}
    autos = [str(i) for i in range(1, 23)]
    auto_depths = [cov[c]["meandepth"] for c in autos if c in cov]
    auto_med = statistics.median(auto_depths) if auto_depths else None
    auto_w = sum(cov[c]["meandepth"] * cov[c]["length"] for c in autos if c in cov) / max(sum(cov[c]["length"] for c in autos if c in cov), 1)
    x_ratio = cov["X"]["meandepth"] / auto_w if "X" in cov and auto_w else None
    y_ratio = cov["Y"]["meandepth"] / auto_w if "Y" in cov and auto_w else None
    reg = {}
    for line in io.open(os.path.join(W, "qc", "region_depth.tsv"), encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 4:
            reg[p[0]] = {"bases": int(p[1]), "mean_depth": float(p[2]), "median_depth": int(p[3])}
    fs = _flagstat(os.path.join(W, "qc", "flagstat.txt"))
    st = _stats(os.path.join(W, "qc", "stats.txt"))
    per_rg = {os.path.basename(p)[12:-4]: _flagstat(p) for p in sorted(glob.glob(os.path.join(W, "qc", "flagstat_rg_*.txt")))}
    rgs = [l.strip() for l in io.open(os.path.join(W, "qc", "read_groups.txt"))]
    pre = {}
    for line in io.open(os.path.join(W, "fastq_preflight.tsv")):
        lane, mate, n, rc = line.rstrip("\n").split("\t")
        pre.setdefault(lane, {})[mate] = int(n)
    xhet = _x_nonpar_het()
    conc = _concordance(); vb = _verifybamid2()
    bam_size = os.path.getsize(BAM); bam_sha = sha256(BAM)
    total = fs.get("in total", {}).get("n"); mapped = fs.get("mapped", {})
    dup = fs.get("duplicates", {}).get("n") or fs.get("primary duplicates", {}).get("n")
    sex_ok = (x_ratio is not None and x_ratio < 0.75) and (y_ratio is not None and y_ratio > 0.25) \
        and (xhet["het_fraction"] is not None and xhet["het_fraction"] < 0.15)
    q = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "bam": {"file": os.path.basename(BAM), "size_gb": round(bam_size / 1024 ** 3, 1), "sha256": bam_sha},
        "fastq_preflight": pre, "read_groups_n": len(rgs), "read_groups_expected": 4,
        "reads_total": total, "mapped": mapped, "properly_paired": fs.get("properly paired", {}),
        "duplicates": dup, "duplicate_fraction": (dup / total) if dup and total else None,
        "duplicate_fraction_note": ("pipeline QC only. Global marking across four lanes whose library "
                                    "provenance is unavailable: may overmark if the lanes come from "
                                    "independent library preparations. Not a biological property."),
        "insert_size_mean": st.get("insert size average"), "insert_size_sd": st.get("insert size standard deviation"),
        "error_rate": st.get("error rate"), "average_quality": st.get("average quality"),
        "autosomal_median_of_contig_mean_depth_q20": auto_med, "autosomal_weighted_mean_depth_q20": round(auto_w, 2),
        "autosomal_depth_min_max": [min(auto_depths), max(auto_depths)] if auto_depths else None,
        "X_over_autosome": round(x_ratio, 3) if x_ratio else None, "Y_over_autosome": round(y_ratio, 3) if y_ratio else None,
        "chrX_nonPAR_heterozygosity_from_vcf": xhet,
        "sex_concordance": ("genomic sex concordance consistent with the declared XY configuration" if sex_ok
                            else "NOT consistent with XY: adjudicate before proceeding"),
        "bub1b_depth": reg, "per_read_group_flagstat": {k: {"total": v.get("in total", {}).get("n"),
                                                          "mapped_pct": v.get("mapped", {}).get("pct")} for k, v in per_rg.items()},
        "bam_vcf_genotype_concordance": conc, "verifybamid2": vb,
        "claim_ceiling": "The reconstructed alignment is technically concordant with the supplied variant dataset. Not identity proof.",
    }
    io.open(os.path.join(W, "qc_summary.json"), "w", encoding="utf-8").write(json.dumps(q, indent=1))
    containers = json.load(io.open(os.path.join(W, "containers.json")))
    refman = json.load(io.open(os.path.join(W, "reference_manifest.json")))
    gate = json.load(io.open(os.path.join(W, "reference_gate.json")))
    pre = os.path.join(W, "merged.bam")
    man = {"run": "GO 2A alignment", "finished_utc": q["generated_utc"],
           "library_preparation_identity": "unavailable",
           "duplicate_marking_scope": "global across all four lanes",
           "duplicate_marking_assumption": ("lanes treated jointly for duplicate marking because library "
                                            "provenance is unavailable; this may overmark if lanes derive "
                                            "from independent library preparations"),
           "duplicate_fraction_interpretation": ("pipeline QC, not a biological property of the sample"),
           "downstream_object_rule": ("The globally duplicate-marked BAM is the primary downstream "
                                      "alignment object. The pre-markdup BAM is retained for technical "
                                      "adjudication only when a critical finding is plausibly sensitive "
                                      "to duplicate handling. Callers are NOT run twice."),
           "bam_pre_markdup": ({"file": "merged.bam", "size_gb": round(os.path.getsize(pre) / 1024 ** 3, 1),
                                "sha256": sha256(pre), "retained": "until GO 2B completes"}
                               if os.path.exists(pre) else {"status": "absent"}),
           "discarded_prior_run": ("technical pre-commit trial (L001 and 50 min of L002, 2026-09-07); "
                                   "excluded from all final analyses; no intermediate BAM retained"),
           "reference": {"source_sha256": refman["source_reference_fasta"]["sha256"],
                         "runtime_sha256": refman["runtime_reference_fasta"]["sha256"], "gates_GO": gate["GO"]},
           "containers": {k: {"tag": v["tag"], "amd64_digest": v["amd64_digest"], "tool_reported_version": v.get("tool_reported_version")}
                          for k, v in containers["images"].items() if k in ("bwa", "samtools", "bcftools", "verifybamid2")},
           "parameters": {"bwa": cfg["bwa_params"], "sort": cfg["sort_params"], "markdup": cfg["markdup"], "read_group_policy": cfg["lb_note"]},
           "fastq_sha256_file": "work/align/fastq_sha256.txt",
           "bam": q["bam"], "qc_summary": "work/align/qc_summary.json",
           "next": "STOP. Callers (Manta, DELLY, CNVpytor, mosdepth, MEI, MitoRead, DMPK) wait for GO 2B."}
    io.open(os.path.join(W, "alignment_manifest.json"), "w", encoding="utf-8").write(json.dumps(man, indent=1))
    print(f"  BAM {q['bam']['size_gb']} GB · lecturas {total} · mapeadas {mapped.get('pct')} · pares propios "
          f"{q['properly_paired'].get('pct')} · duplicados {q['duplicate_fraction']}")
    print(f"  profundidad autosomica ponderada (q20) {q['autosomal_weighted_mean_depth_q20']} · X/auto "
          f"{q['X_over_autosome']} · Y/auto {q['Y_over_autosome']} · X no-PAR het {xhet['het_fraction']}")
    print(f"  BUB1B: {reg}")
    print(f"  read groups {len(rgs)}/4 · concordancia BAM<->VCF {conc.get('concordance')} en {conc.get('sites_compared')} sitios · "
          f"VerifyBamID2 {vb.get('FREEMIX_alpha')}")
    print(f"  sexo: {q['sex_concordance']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    {"regions": regions, "sites": sites, "depth": depth, "summary": summary}[cmd]()
