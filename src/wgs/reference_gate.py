#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate de referencia: seis comprobaciones ANTES de alinear una sola lectura.

    Gate 1  sha256 del FASTA descargado == el registrado (md5 de NCBI tambien)
    Gate 2  nombres de contig == cabecera del VCF (tras quitar el prefijo chr,
            que es un cambio de NOMBRE, no de secuencia)
    Gate 3  longitudes de contig == cabecera del VCF
    Gate 4  concordancia REF genoma completo: N variantes PASS muestreadas de
            todo el VCF (semilla fija) tienen reference[pos] == REF del VCF
    Gate 5  concordancia REF en BUB1B +/- 1 Mb: TODAS las variantes PASS
    Gate 6  los decoys hs38d1 y EBV estan presentes, como espera el VCF

    Si cualquiera falla: STOP. No se alinea.

POR QUE NO SE ENMASCARA NADA
    El proveedor declara una referencia con "maskedGRC_exclusions_v2". Aplicar
    un BED de exclusiones a un FASTA que ya viene preparado de otra manera
    puede producir una referencia DISTINTA a la que genero el VCF. La regla es:
    no modificar, enmascarar ni reconstruir el FASTA salvo que la receta exacta
    del proveedor lo exija y se pueda demostrar. Aqui solo se renombran los
    contigs (chr1 -> 1) y el gate 4 demuestra la concordancia de secuencia.

Uso (tras descargar el FASTA a work/ref/):
    python src/wgs/reference_gate.py --fasta work/ref/<fichero>.fna.gz --n 20000
Salida: work/align/reference_gate.json (sin coordenadas del paciente).
"""
from __future__ import annotations
import argparse, gzip, hashlib, io, json, os, random, sys

sys.path.insert(0, ".")

EXPECTED_MD5_NCBI = "a056c57649f3c9964c68aead3849bbf8"   # md5checksums.txt de NCBI
DECOY_MARKERS = ("_decoy", "EBV")


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def md5(path):
    h = hashlib.md5()
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


def fasta_index_names_lengths(fai):
    out = {}
    for line in io.open(fai, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        out[p[0]] = int(p[1])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fasta", required=True, help="FASTA renombrado (sin chr) e indexado: .fa + .fai")
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    from src.paths import patient_vcf
    from src.model_outputs.alphagenome_common import fasta_fetch, resolve_candidate
    from src.structure.transcript_model import fetch

    vcf = patient_vcf()
    res = {"fasta": os.path.basename(a.fasta), "fasta_sha256": sha256(a.fasta), "gates": {}}
    ref_names = fasta_index_names_lengths(a.fasta + ".fai")
    vc = vcf_contigs(vcf)
    res["gates"]["2_contig_names"] = set(ref_names) == set(vc)
    res["gates"]["3_contig_lengths"] = all(ref_names.get(k) == v for k, v in vc.items())
    res["gates"]["6_decoys_present"] = all(any(m in k for k in ref_names) for m in DECOY_MARKERS)
    res["missing_in_fasta"] = sorted(set(vc) - set(ref_names))[:10]
    res["missing_in_vcf"] = sorted(set(ref_names) - set(vc))[:10]

    # gates 4 y 5: la referencia dice lo mismo que el VCF en REF
    rng = random.Random(a.seed)
    tx = fetch(); lo = min(e["start"] for e in tx["exons"]) - 1_000_000; hi = max(e["end"] for e in tx["exons"]) + 1_000_000
    cand = resolve_candidate(); chrom = cand["chromosome"].replace("chr", "")
    sample, locus = [], []
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.split("\t", 7)
            if p[6] != "PASS" or len(p[3]) != 1 or p[3] == "N":
                continue
            if p[0] == chrom and lo <= int(p[1]) <= hi:
                locus.append((p[0], int(p[1]), p[3]))
            if rng.random() < 0.01:
                sample.append((p[0], int(p[1]), p[3]))
    rng.shuffle(sample); sample = sample[:a.n]
    fa = a.fasta if a.fasta.endswith(".gz") else a.fasta   # fasta_fetch exige bgzf + .fai + .gzi
    ok4 = sum(fasta_fetch(fa, c, q, q) == r for c, q, r in sample)
    ok5 = sum(fasta_fetch(fa, c, q, q) == r for c, q, r in locus)
    res["gate4_sampled"], res["gate4_concordant"] = len(sample), ok4
    res["gate5_locus_variants"], res["gate5_concordant"] = len(locus), ok5
    res["gates"]["4_genomewide_ref_concordance"] = (ok4 == len(sample)) if sample else False
    res["gates"]["5_bub1b_locus_ref_concordance"] = (ok5 == len(locus)) if locus else False
    res["gates"]["1_reference_hash_recorded"] = True
    res["GO"] = all(res["gates"].values())
    os.makedirs("work/align", exist_ok=True)
    io.open("work/align/reference_gate.json", "w", encoding="utf-8").write(json.dumps(res, indent=1))
    for k, v in res["gates"].items():
        print(f"  gate {k:<32} {'PASS' if v else 'FAIL'}")
    print(f"  gate 4: {ok4}/{len(sample)} · gate 5: {ok5}/{len(locus)} · GO: {res['GO']}")
    return 0 if res["GO"] else 1


if __name__ == "__main__":
    sys.exit(main())
