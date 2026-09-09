#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GO 2B · adjudicacion por lecturas, MitoRead y resumen de los llamadores.

Subcomandos (los usa run_callers.sh):
    regions   escribe la region de trabajo de BUB1B (Tier 1) y los dos alelos
    bub1b     metricas por lectura de los dos alelos desde el SAM del locus
    mito      cociente mtDNA:nuclear consciente de NUMT
    summary   recuento de llamadas por herramienta, extraccion de Tier 1 y manifest

NADA DE ESTO INTERPRETA. Cuenta, mide y tabula. La adjudicacion cientifica es
del mantenedor, despues del STOP.

TECHOS ESCRITOS AQUI, no en el informe:
    SV/CNV negativo -> "No supported structural or copy-number second allele was
        detected by the specified short-read WGS workflow; classes poorly
        accessible to short reads remain unresolved." Nunca "excluido".
    bcftools        -> "TECHNICAL REPLICATION FROM THE SAME READS", nunca
        evidencia independiente.
    MitoRead        -> "cell-composition-unadjusted WGS-derived blood
        mtDNA:nuclear ratio". Nunca disfuncion mitocondrial.
    ExpansionHunter -> cribado; solo se interpreta DMPK, y como segundo
        diagnostico posible, no como causa del MVA.
"""
from __future__ import annotations
import csv, glob, gzip, hashlib, io, json, os, re, statistics, sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

W = "work/callers"
BAM = "work/align/full_depth.markdup.bam"
TIER1_FLANK = 1_000_000
DMPK_LOCI = ("DMPK",)          # el unico locus de expansiones que se interpreta


def sha256(p):
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _alleles():
    """Los dos alelos prioritarios, desde el CSV de entrega (objeto canonico)."""
    rows = list(csv.DictReader(io.open("work/submission/track1_predictions.csv", encoding="utf-8")))
    r = [x for x in rows if x["finding_type"] == "primary"][0]
    return [{"chrom": r["chrom_1"].replace("chr", ""), "pos": int(r["pos_1"]), "ref": r["ref_1"], "alt": r["alt_1"]},
            {"chrom": r["chrom_2"].replace("chr", ""), "pos": int(r["pos_2"]), "ref": r["ref_2"], "alt": r["alt_2"]}]


def _tier1():
    from src.structure.transcript_model import fetch
    tx = fetch()
    lo = min(e["start"] for e in tx["exons"]) - TIER1_FLANK
    hi = max(e["end"] for e in tx["exons"]) + TIER1_FLANK
    a = _alleles()[0]["chrom"]
    return a, max(1, lo), hi


def regions():
    c, lo, hi = _tier1()
    print(f"TIER1\t{c}:{lo}-{hi}")


def dmpk_catalog():
    """Catalogo DERIVADO con un solo locus, DMPK.

    El catalogo oficial de ExpansionHunter para GRCh38 trae 31 loci. Ejecutarlo
    entero generaria resultados de 30 loci que el preregistro prohibe
    interpretar, y un resultado que existe se acaba mirando. Aqui se extrae la
    entrada de DMPK del catalogo oficial y se escribe un catalogo de un
    elemento: los demas loci no se llaman, no se generan y no se revisan ni
    incidentalmente. La procedencia del catalogo oficial queda registrada.
    """
    src = os.path.join(W, "repeats", "catalog_official_grch38.json")
    if not os.path.exists(src):
        raise SystemExit("falta la copia del catalogo oficial: el orquestador debe extraerla del contenedor")
    official = json.load(io.open(src, encoding="utf-8"))
    picked = [x for x in official if x.get("LocusId") in DMPK_LOCI]
    if len(picked) != len(DMPK_LOCI):
        raise SystemExit(f"esperados {len(DMPK_LOCI)} loci, encontrados {len(picked)}")
    out = os.path.join(W, "repeats", "catalog_dmpk_only.json")
    io.open(out, "w", encoding="utf-8", newline="\n").write(json.dumps(picked, indent=1))
    io.open(os.path.join(W, "repeats", "catalog_provenance.json"), "w", encoding="utf-8").write(
        json.dumps({"derived_from": "ExpansionHunter 5.0.0 official grch38 variant_catalog.json",
                    "official_loci": len(official), "official_sha256": sha256(src),
                    "interpreted_loci": list(DMPK_LOCI), "derived_sha256": sha256(out),
                    "reason": "P1 phenotype-driven screen; other loci are not called, not generated "
                              "and not reviewed even incidentally"}, indent=1))
    print(f"  catalogo derivado: {len(picked)} locus de {len(official)} oficiales")


# ------------------------------------------------- 6 · lecturas de BUB1B ----
def bub1b():
    """Metricas por lectura de cada alelo, leidas del SAM del locus.

    Sin pysam: el SAM se parsea a mano. Se cuentan lecturas primarias no
    duplicadas que cubren la posicion, y se clasifica cada una por la base que
    presenta en ella, resolviendo el CIGAR.
    """
    sam = os.path.join(W, "bub1b", "locus.sam")
    out = {"alleles": [], "note": "primary, non-duplicate reads covering the position"}
    als = _alleles()
    recs = []
    for line in io.open(sam, encoding="utf-8", errors="replace"):
        if line.startswith("@"):
            continue
        p = line.rstrip("\n").split("\t")
        flag = int(p[1])
        if flag & 0x900:                      # secundaria o suplementaria
            continue
        recs.append((flag, p[2], int(p[3]), int(p[4]), p[5], p[9], p[10]))
    for a in als:
        cov = {"A": 0, "C": 0, "G": 0, "T": 0}
        mapq, bq, fwd, rev, clip, dup = [], [], 0, 0, 0, 0
        for flag, rname, pos, q, cigar, seq, qual in recs:
            if rname.replace("chr", "") != a["chrom"]:
                continue
            # recorre el CIGAR hasta la posicion pedida
            ref_i, read_i, base, bqual = pos, 0, None, None
            for n, op in re.findall(r"(\d+)([MIDNSHP=X])", cigar):
                n = int(n)
                if op in "SH":
                    if op == "S":
                        read_i += n
                    clip_here = True
                    continue
                if op in "M=X":
                    if ref_i <= a["pos"] < ref_i + n:
                        off = a["pos"] - ref_i
                        base = seq[read_i + off]
                        bqual = ord(qual[read_i + off]) - 33
                        break
                    ref_i += n; read_i += n
                elif op == "I":
                    read_i += n
                elif op in "DN":
                    if ref_i <= a["pos"] < ref_i + n:
                        base = "-"; break
                    ref_i += n
            if base is None:
                continue
            if flag & 0x400:
                dup += 1
                continue                      # los duplicados no cuentan para el balance
            if base in cov:
                cov[base] += 1
            mapq.append(q)
            if bqual is not None:
                bq.append(bqual)
            if flag & 0x10:
                rev += 1
            else:
                fwd += 1
            if "S" in cigar or "H" in cigar:
                clip += 1
        ref_n, alt_n = cov.get(a["ref"], 0), cov.get(a["alt"], 0)
        tot = sum(cov.values())
        out["alleles"].append({
            "ref": a["ref"], "alt": a["alt"],
            "DP_primary_nondup": tot, "AD_ref": ref_n, "AD_alt": alt_n,
            "allele_balance_alt": (alt_n / tot) if tot else None,
            "other_bases": tot - ref_n - alt_n,
            "MAPQ_median": statistics.median(mapq) if mapq else None,
            "MAPQ_min": min(mapq) if mapq else None,
            "base_quality_median": statistics.median(bq) if bq else None,
            "forward": fwd, "reverse": rev,
            "strand_balance_fwd": (fwd / (fwd + rev)) if (fwd + rev) else None,
            "soft_or_hard_clipped_reads": clip,
            "duplicates_at_site": dup,
        })
    out["ceiling"] = ("read-level QC of the two prioritized alleles on the reconstructed alignment. "
                      "Recovery here is not independent evidence of pathogenicity.")
    io.open(os.path.join(W, "bub1b", "read_metrics.json"), "w", encoding="utf-8").write(
        json.dumps(out, indent=1))
    for i, x in enumerate(out["alleles"], 1):
        print(f"  alelo {i}: DP {x['DP_primary_nondup']} · AD {x['AD_ref']},{x['AD_alt']} · "
              f"balance {x['allele_balance_alt']} · MAPQ mediana {x['MAPQ_median']} · "
              f"hebras {x['forward']}/{x['reverse']} · recortadas {x['soft_or_hard_clipped_reads']}")


# --------------------------------------------------------- 7 · MitoRead ----
def mito():
    def depths(p):
        v = [int(l.split("\t")[2]) for l in io.open(p, encoding="utf-8") if l.strip()]
        return v
    d0 = depths(os.path.join(W, "mito", "chrM_q0.txt"))
    d30 = depths(os.path.join(W, "mito", "chrM_q30.txt"))
    cov = {}
    for line in io.open("work/align/qc/coverage_by_contig.tsv", encoding="utf-8"):
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) > 6:
            cov[p[0]] = {"len": int(p[2]) - int(p[1]) + 1, "mean": float(p[6])}
    autos = [str(i) for i in range(1, 23)]
    aw = sum(cov[c]["mean"] * cov[c]["len"] for c in autos if c in cov) / \
         sum(cov[c]["len"] for c in autos if c in cov)
    per_chr = {c: round(cov[c]["mean"], 2) for c in autos if c in cov}
    m0 = statistics.median(d0) if d0 else 0
    m30 = statistics.median(d30) if d30 else 0
    out = {
        "chrM_median_depth_MAPQ0": m0, "chrM_median_depth_MAPQ30": m30,
        "chrM_mean_depth_MAPQ0": round(statistics.mean(d0), 1) if d0 else 0,
        "chrM_mean_depth_MAPQ30": round(statistics.mean(d30), 1) if d30 else 0,
        "numt_aware_note": ("MAPQ>=30 filtering reduces, identifies and filters likely "
                            "nuclear-mitochondrial (NUMT) mappings; it does not guarantee their "
                            "complete removal"),
        "mapq30_retained_fraction": round(m30 / m0, 4) if m0 else None,
        "autosomal_weighted_mean_depth": round(aw, 2),
        "per_autosome_mean_depth": per_chr,
        "ratio_mtDNA_to_nuclear_MAPQ30": round(m30 / aw, 1) if aw else None,
        "ratio_mtDNA_to_nuclear_MAPQ0": round(m0 / aw, 1) if aw else None,
        "sensitivity_to_denominator": {
            "min_autosome": round(m30 / min(per_chr.values()), 1) if per_chr else None,
            "max_autosome": round(m30 / max(per_chr.values()), 1) if per_chr else None},
        "ceiling": ("Without CBC/platelet/cell-composition data, the result is a "
                    "cell-composition-unadjusted WGS-derived blood mtDNA:nuclear ratio. "
                    "It is an orthogonal WGS readout, not evidence of mitochondrial dysfunction."),
    }
    io.open(os.path.join(W, "mito", "mitoread.json"), "w", encoding="utf-8").write(json.dumps(out, indent=1))
    print(f"  chrM mediana MAPQ0 {m0} · MAPQ>=30 {m30} · retenido {out['mapq30_retained_fraction']}")
    print(f"  cociente mtDNA:nuclear (MAPQ>=30) {out['ratio_mtDNA_to_nuclear_MAPQ30']} · "
          f"sensibilidad al denominador {out['sensitivity_to_denominator']}")


# ------------------------------------------------------- 9 · resumen -------
def _count_vcf(path, tier1=None):
    """(total, en Tier 1) de un VCF/BCF comprimido, sin dependencias."""
    if not os.path.exists(path):
        return None, None
    n = t = 0
    op = gzip.open if path.endswith(".gz") else io.open
    try:
        with op(path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                n += 1
                if tier1:
                    p = line.split("\t", 3)
                    if p[0].replace("chr", "") == tier1[0] and tier1[1] <= int(p[1]) <= tier1[2]:
                        t += 1
    except Exception:
        return None, None
    return n, t


def summary():
    for d in ("", "sv", "cnv", "mei", "bub1b", "mito", "repeats", "qc", "logs"):
        os.makedirs(os.path.join(W, d), exist_ok=True)
    c, lo, hi = _tier1()
    tier1 = (c, lo, hi)
    # Taxonomia de estados: SUCCESS / FAILED / SKIPPED_DEPENDENCY / NOT_RUN.
    # FAILED nunca se degrada a NOT_RUN: que una herramienta se intentara y
    # fallara es informacion, y borrarla falsea el reporte.
    NAMES = {"0": "preflight critico", "1": "mosdepth (QC)", "2": "Manta (SV)",
             "3": "DELLY (SV ortogonal)", "4": "CNVpytor (RD + BAF)",
             "5b": "xTea (MEI primario)", "5a": "SCRAMble (MEI ortogonal)",
             "6": "BUB1B por lecturas", "7": "MitoRead", "8": "DMPK (solo un locus)"}
    stages = {}
    for k, label in NAMES.items():
        p = os.path.join(W, "status", f"{k}.status")
        if os.path.exists(p):
            parts = io.open(p, encoding="utf-8").read().rstrip("\n").split("\t")
            stages[k] = {"name": label, "status": parts[1] if len(parts) > 1 else "UNKNOWN",
                         "detail": parts[2] if len(parts) > 2 and parts[2] else None}
        else:
            stages[k] = {"name": label, "status": "NOT_RUN",
                         "detail": "no se alcanzo esta etapa en esta corrida"}
        # subestados: un agregado FAILED no puede borrar la parte que si funciono
        sub = os.path.join(W, "status", f"{k}.sub")
        if os.path.exists(sub):
            stages[k]["sub_status"] = dict(
                l.rstrip("\n").split("\t")[:2] for l in io.open(sub, encoding="utf-8") if "\t" in l)
        # procedencia de arrastre: `carried_forward` es procedencia, no un estado
        carry = os.path.join(W, "status", f"{k}.carry.json")
        if os.path.exists(carry):
            c = json.load(io.open(carry, encoding="utf-8"))
            # execution_status es historico y no lo reescribe una validacion fallida
            stages[k]["execution_status"] = c.get("execution_status")
            stages[k]["executed_under_commit"] = c.get("executed_under_commit")
            stages[k]["carry_forward_validation"] = c.get("carry_forward_validation")
            stages[k]["carried_forward"] = c.get("carried_forward")
            stages[k]["output_sha256"] = {n: v["sha256"] for n, v in c.get("outputs", {}).items()}
            stages[k]["carry_forward_reason"] = c.get("carry_forward_reason")
            stages[k]["carry_forward_validation_note"] = c.get("carry_forward_validation")
    tally = {}
    for v in stages.values():
        tally[v["status"]] = tally.get(v["status"], 0) + 1

    manta = os.path.join(W, "sv/manta/results/variants/diploidSV.vcf.gz")
    delly = os.path.join(W, "sv/delly.vcf.gz")
    m_n, m_t = _count_vcf(manta, tier1)
    d_n, d_t = _count_vcf(delly, tier1)

    def _rows(p):
        return sum(1 for l in io.open(p, encoding="utf-8", errors="replace") if l.strip()) \
            if os.path.exists(p) else None
    cnv_rd = _rows(os.path.join(W, "cnv/calls_rd.tsv"))
    cnv_cb = _rows(os.path.join(W, "cnv/calls_combined.tsv"))
    scr = sorted(glob.glob(os.path.join(W, "mei", "scramble*MEIs.txt")))
    scr_n = _rows(scr[0]) if scr else None

    eh = os.path.join(W, "repeats", "eh.json")
    dmpk = {}
    if os.path.exists(eh):
        try:
            j = json.load(io.open(eh, encoding="utf-8"))
            for name, v in (j.get("LocusResults") or {}).items():
                if any(g.lower() in name.lower() for g in DMPK_LOCI):
                    dmpk[name] = v
        except Exception as e:                      # noqa: BLE001
            dmpk = {"error": f"{type(e).__name__}"}

    import subprocess
    try:
        ctrl = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                   # noqa: BLE001
        ctrl = "no disponible"
    out = {
        "run": "GO 2B", "finished_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "controlflow_commit": ctrl,
        "provenance_note": ("stages marked carried_forward ran under an earlier commit, named in "
                            "executed_under_commit; every other stage ran under controlflow_commit"),
        "provenance_axes": {
            "execution_status": "what actually happened when the stage ran. Historical: a failed "
                                "reuse validation never rewrites it",
            "carry_forward_validation": "PASS or FAIL — whether those outputs may be reused now",
            "carried_forward": "true only when validation passed and the stage was not re-run",
            "rule": "preflight FAILED -> abort. preflight PASS + hashes match -> reuse. preflight "
                    "PASS + outputs invalid -> validation FAIL, history untouched, stage re-run. "
                    "Only a new failed execution yields FAILED"},
        "primary_object": {"file": os.path.basename(BAM),
                           "sha256": sha256(BAM) if os.path.exists(BAM) else None,
                           "rule": "the globally duplicate-marked BAM is the primary downstream "
                                   "alignment object; the pre-markdup BAM was NOT used here"},
        "stages": stages, "status_tally": tally,
        "status_taxonomy": {"SUCCESS": "ran and produced valid outputs",
                            "FAILED": "ran and failed; never downgraded to NOT_RUN",
                            "SKIPPED_DEPENDENCY": "not run because a prerequisite failed",
                            "NOT_RUN": "not attempted, with an explicit stated reason"},
        "failure_scope": {"critical_shared": "BAM / BAI / reference / contig compatibility / "
                                             "provenance → aborts GO 2B entirely",
                          "local": "a single caller → FAILED for that branch only; independent "
                                   "branches continue"},
        "tier1_region_bp": hi - lo + 1,
        "structural_variants": {
            "manta_total": m_n, "manta_in_tier1": m_t,
            "delly_total": d_n, "delly_in_tier1": d_t,
            "concordance_note": "caller concordance increases technical support but is not required "
                                "for candidate retention",
            "ceiling": "No supported structural or copy-number second allele was detected by the "
                       "specified short-read WGS workflow; classes poorly accessible to short reads "
                       "remain unresolved. NEVER 'structural second allele excluded'."},
        "copy_number": {"cnvpytor_rd_calls": cnv_rd, "cnvpytor_combined_rd_baf_calls": cnv_cb,
                        "note": "CNVpytor is read-depth + BAF; mosdepth is coverage QC only and is "
                                "not a CNV caller"},
        "mobile_elements": {"xtea_role": "PRIMARY", "xtea_status": stages["5b"]["status"],
                            "scramble_role": "ORTHOGONAL", "scramble_status": stages["5a"]["status"],
                            "scramble_calls": scr_n,
                            "role_note": "roles are fixed by the preregistration and do not depend on "
                                         "which tool ran first or which one succeeded",
                            "ceiling": "a combined negative does not exclude all complex insertions; "
                                       "some are resolvable only by targeted analysis or long reads"},
        "bub1b_read_backed": ("work/callers/bub1b/read_metrics.json" if os.path.exists(
            os.path.join(W, "bub1b/read_metrics.json")) else None),
        "technical_replication": {"tool": "bcftools mpileup/call on the same BAM",
                                  "label": "TECHNICAL REPLICATION FROM THE SAME READS",
                                  "not": "independent evidence"},
        "mitoread": ("work/callers/mito/mitoread.json" if os.path.exists(
            os.path.join(W, "mito/mitoread.json")) else None),
        "repeat_expansions": {"catalog": "DERIVED single-locus catalog extracted from the official "
                                         "ExpansionHunter grch38 catalog; other loci are not called, "
                                         "not generated and not reviewed even incidentally",
                              "interpreted_loci": list(DMPK_LOCI),
                              "dmpk_result": dmpk or None,
                              "ceiling": "P1 residual / second-diagnosis screen, not an MVA-causal "
                                         "hypothesis; any positive requires visual inspection"},
        "not_done_on_purpose": ["no interpretation", "Track 1 untouched", "variant classification "
                                "untouched", "Track 2 untouched", "EXP-024 not scored",
                                "callers not run twice"],
    }
    io.open(os.path.join(W, "go2b_summary.json"), "w", encoding="utf-8").write(json.dumps(out, indent=1))
    print(f"  control de flujo: {ctrl}")
    for k, v in stages.items():
        extra = ""
        if v.get("executed_under_commit"):
            extra += (f"  · ejecucion {v.get('execution_status')} bajo {v['executed_under_commit']}"
                      f", reutilizacion {v.get('carry_forward_validation')}"
                      f", carried_forward={v.get('carried_forward')}")
        if v.get("sub_status"):
            extra += "  · " + ", ".join(f"{a}={b}" for a, b in v["sub_status"].items())
        print(f"  {k:<3} {v['name']:<26} {v['status']}{'  · ' + v['detail'] if v['detail'] else ''}{extra}")
    print("  recuento: " + " · ".join(f"{k} {n}" for k, n in sorted(tally.items())))
    print(f"  SV: Manta {m_n} total / {m_t} en Tier 1 · DELLY {d_n} / {d_t}")
    print(f"  CNV: CNVpytor {cnv_rd} llamadas RD, {cnv_cb} combinadas RD+BAF")
    print(f"  MEI: xTea (primario) {stages['5b']['status']} · SCRAMble (ortogonal) "
          f"{stages['5a']['status']}, {scr_n} llamadas")
    print(f"  DMPK: {'presente en el catalogo' if dmpk else 'sin resultado'}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    {"regions": regions, "dmpk_catalog": dmpk_catalog, "bub1b": bub1b,
     "mito": mito, "summary": summary}[cmd]()
