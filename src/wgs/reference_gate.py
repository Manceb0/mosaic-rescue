#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate de referencia: seis comprobaciones ANTES de alinear una sola lectura.

    Gate 1  procedencia: work/align/reference_manifest.json existe, el md5 del
            source coincide con el publicado por NCBI, sequence_content_changed
            es false y el sha256 del runtime coincide con el fichero presente
    Gate 2  contigs: TODO contig declarado por el VCF existe en el runtime
            FASTA. Contigs adicionales del FASTA se permiten SOLO si estan
            predeclarados en PREDECLARED_EXTRA_CONTIGS; cualquier otro extra
            es STOP
    Gate 3  longitudes: cada contig del VCF tiene longitud identica en el runtime
    Gate 4  concordancia REF genoma completo: N variantes PASS muestreadas de
            todo el VCF con semilla fija cumplen reference[pos] == REF del VCF,
            en todas
    Gate 5  concordancia REF en BUB1B +/- 1 Mb: TODAS las variantes PASS
    Gate 6  los decoys hs38d1 y EBV estan presentes, como espera el VCF

    Contig del VCF ausente, longitud distinta o REF distinta = STOP.
    Solo con los seis en PASS: ALIGNMENT GO. El alineamiento NO arranca solo:
    se reporta el gate y se espera el GO del mantenedor.

Uso (tras src/wgs/reference_prepare.py):
    python src/wgs/reference_gate.py [--n 20000] [--seed 42]
Salida: work/align/reference_gate.json (sin coordenadas del paciente).
"""
from __future__ import annotations
import argparse, gzip, hashlib, io, json, os, random, sys

sys.path.insert(0, ".")

RUNTIME = "work/ref/runtime.fa"
MANIFEST = "work/align/reference_manifest.json"
EXPECTED_MD5_NCBI = "a056c57649f3c9964c68aead3849bbf8"
DECOY_MARKERS = ("_decoy", "EBV")
PREDECLARED_EXTRA_CONTIGS: set = set()     # ninguno esperado; anadir aqui, a proposito, si el VCF no los enumera


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def vcf_contigs(vcf):
    out = {}
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("##contig="):
                kv = dict(x.split("=", 1) for x in line[len("##contig=<"):].rstrip(">\n").split(","))
                out[kv["ID"]] = int(kv["length"])
            elif line.startswith("#CHROM"):
                break
    return out


class PlainFasta:
    """Acceso aleatorio a un FASTA plano por su .fai (seek), sin dependencias."""

    def __init__(self, path):
        self.path = path; self.idx = {}
        for line in io.open(path + ".fai", encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            self.idx[p[0]] = (int(p[1]), int(p[2]), int(p[3]), int(p[4]))
        self.fh = io.open(path, "rb")

    def base(self, contig, pos1):
        L, off, lb, lw = self.idx[contig]
        z = pos1 - 1
        self.fh.seek(off + (z // lb) * lw + z % lb)
        return self.fh.read(1).decode("ascii").upper()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    from src.paths import patient_vcf
    from src.model_outputs.alphagenome_common import resolve_candidate
    from src.structure.transcript_model import fetch

    res = {"gates": {}, "runtime_fasta": RUNTIME}
    # gate 1: procedencia
    man = json.load(io.open(MANIFEST, encoding="utf-8")) if os.path.exists(MANIFEST) else None
    g1 = bool(man) and man["source_reference_fasta"]["md5"] == EXPECTED_MD5_NCBI \
        and man["sequence_content_changed"] is False \
        and os.path.exists(RUNTIME) and sha256(RUNTIME) == man["runtime_reference_fasta"]["sha256"]
    res["gates"]["1_provenance_source_and_runtime"] = g1
    if not g1:
        res["GO"] = False
        io.open("work/align/reference_gate.json", "w", encoding="utf-8").write(json.dumps(res, indent=1))
        print("  gate 1 FAIL: procedencia de la referencia no verificable"); return 1
    res["source_sha256"] = man["source_reference_fasta"]["sha256"]
    res["runtime_sha256"] = man["runtime_reference_fasta"]["sha256"]

    vcf = patient_vcf(); vc = vcf_contigs(vcf)
    fa = PlainFasta(RUNTIME)
    missing = sorted(set(vc) - set(fa.idx))
    extra = sorted(set(fa.idx) - set(vc))
    res["vcf_contigs_missing_in_runtime"] = missing[:10]
    res["runtime_extra_contigs"] = extra[:10]
    res["gates"]["2_every_vcf_contig_present_extras_predeclared"] = not missing and set(extra) <= PREDECLARED_EXTRA_CONTIGS
    bad_len = [k for k, v in vc.items() if k in fa.idx and fa.idx[k][0] != v]
    res["length_mismatches"] = bad_len[:10]
    res["gates"]["3_identical_lengths"] = not missing and not bad_len
    res["gates"]["6_decoys_present"] = all(any(m in k for k in fa.idx) for m in DECOY_MARKERS)

    rng = random.Random(a.seed)
    tx = fetch(); lo = min(e["start"] for e in tx["exons"]) - 1_000_000; hi = max(e["end"] for e in tx["exons"]) + 1_000_000
    chrom = resolve_candidate()["chromosome"].replace("chr", "")
    sample, locus = [], []
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.split("\t", 7)
            if p[6] != "PASS" or len(p[3]) != 1 or p[3] == "N" or p[0] not in fa.idx:
                continue
            if p[0] == chrom and lo <= int(p[1]) <= hi:
                locus.append((p[0], int(p[1]), p[3]))
            if rng.random() < 0.01:
                sample.append((p[0], int(p[1]), p[3]))
    rng.shuffle(sample); sample = sample[:a.n]
    ok4 = sum(fa.base(c, q) == r for c, q, r in sample)
    ok5 = sum(fa.base(c, q) == r for c, q, r in locus)
    res["gate4_sampled"], res["gate4_concordant"] = len(sample), ok4
    res["gate5_locus_variants"], res["gate5_concordant"] = len(locus), ok5
    res["gates"]["4_genomewide_ref_concordance"] = bool(sample) and ok4 == len(sample)
    res["gates"]["5_bub1b_locus_ref_concordance"] = bool(locus) and ok5 == len(locus)
    res["GO"] = all(res["gates"].values())
    res["next"] = "STOP and report; alignment starts only on the maintainer's explicit GO"
    os.makedirs("work/align", exist_ok=True)
    io.open("work/align/reference_gate.json", "w", encoding="utf-8").write(json.dumps(res, indent=1))
    for k in sorted(res["gates"]):
        print(f"  gate {k:<44} {'PASS' if res['gates'][k] else 'FAIL'}")
    print(f"  gate 4: {ok4}/{len(sample)} · gate 5: {ok5}/{len(locus)} · extras: {len(extra)} · GO: {res['GO']}")
    return 0 if res["GO"] else 1


if __name__ == "__main__":
    sys.exit(main())
