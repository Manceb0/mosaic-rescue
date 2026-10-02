"""Dataset de juguete para probar el orquestador de EXP-027 de extremo a extremo con Docker.

100 % sintético (semilla 42), sin datos del paciente ni de 1000G. Reutiliza los genotipos de
c3_synth.simulate y añade lo que el flujo real necesita: referencia FASTA, mapa genético explícito,
VCF no faseado con GQ y FILTER, pedigrí, lista de la cohorte (no emparentados + padres, como los
2.504 de fase 3) y, para cada hijo, un BAM con lecturas simuladas desde sus haplotipos verdaderos.
"""
from __future__ import annotations

import gzip
from pathlib import Path

import numpy as np

from .c3_synth import simulate

CONTIG = "chr20"
REF_LEN = 3_100_000
READ_LEN = 100
DEPTH = 40
SEED = 42


def _reference(rng, positions) -> bytearray:
    seq = bytearray(rng.choice(np.frombuffer(b"ACGT", dtype=np.uint8), REF_LEN).tobytes())
    for p in positions:
        seq[p - 1] = ord("A")                         # REF = A en todos los sitios variantes
    return seq


def _write_fasta(path: Path, seq: bytearray) -> None:
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(f">{CONTIG}\n")
        for i in range(0, len(seq), 60):
            f.write(seq[i:i + 60].decode() + "\n")


def _write_map(path: Path) -> None:
    """Mapa explícito a 1 cM/Mb (pos chr cM): la ejecución no usa el valor por defecto implícito."""
    with gzip.open(path, "wt", encoding="ascii", newline="\n") as f:
        f.write("pos\tchr\tcM\n")
        for pos in range(1, REF_LEN + 1, 10_000):
            f.write(f"{pos}\t{CONTIG[3:]}\t{pos / 1e6:.6f}\n")


def _write_vcf(path: Path, samples, pos, G) -> None:
    n = len(samples)
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(f"##fileformat=VCFv4.2\n##contig=<ID={CONTIG},length={REF_LEN}>\n")
        f.write('##FILTER=<ID=PASS,Description="All filters passed">\n')
        f.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
        f.write('##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype quality">\n')
        f.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(samples) + "\n")
        for j, p in enumerate(pos):
            col = G[:, j]
            if col.sum() in (0, 2 * n):
                continue
            gts = [f"{min(col[2*s], col[2*s+1])}/{max(col[2*s], col[2*s+1])}:99" for s in range(n)]
            f.write(f"{CONTIG}\t{p}\tv{j}\tA\tG\t.\tPASS\t.\tGT:GQ\t" + "\t".join(gts) + "\n")


def _write_sam(path: Path, ref: bytearray, pos, hap1, hap2, rng, imbalance: float) -> None:
    """Lecturas de 100 pb desde los haplotipos verdaderos del hijo (hap1 = paterno).

    Cada lectura sale de un haplotipo (paterno con probabilidad 0.5 + imbalance) y lleva el alelo de
    ese haplotipo en todos los sitios variantes que cubre.
    """
    pos = np.asarray(pos)
    alt1, alt2 = np.asarray(hap1, bool), np.asarray(hap2, bool)
    het = np.where(alt1 != alt2)[0]
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(f"@HD\tVN:1.6\tSO:unsorted\n@SQ\tSN:{CONTIG}\tLN:{REF_LEN}\n")
        rid = 0
        for i in het:
            for _ in range(DEPTH):
                start = int(pos[i]) - int(rng.integers(0, READ_LEN))
                start = min(max(start, 1), REF_LEN - READ_LEN + 1)
                end = start + READ_LEN - 1
                paternal = rng.random() < 0.5 + imbalance
                alts = alt1 if paternal else alt2
                seq = bytearray(ref[start - 1:end])
                lo, hi = np.searchsorted(pos, start), np.searchsorted(pos, end, side="right")
                for k in range(lo, hi):
                    seq[int(pos[k]) - start] = ord("G") if alts[k] else ord("A")
                f.write(f"r{rid}\t0\t{CONTIG}\t{start}\t60\t{READ_LEN}M\t*\t0\t0\t{seq.decode()}\t{'I' * READ_LEN}\n")
                rid += 1


def build(out: Path, imbalance: float = 0.0) -> dict:
    """Escribe el dataset en out y devuelve sus rutas y metadatos (sin BAM indexado: lo hace el
    orquestador con samtools en Docker)."""
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    samples, ped, pos, G = simulate()
    ref = _reference(rng, pos)
    _write_fasta(out / "ref.fa", ref)
    _write_map(out / "toy.gmap.gz")
    _write_vcf(out / "joint.vcf", samples, pos, G)
    with open(out / "pedigree.ped", "w", encoding="ascii", newline="\n") as f:
        for kid, fa, mo in ped:
            f.write(f"{kid}\t{fa}\t{mo}\n")
    cohort = [s for s in samples if not s.startswith("C")]          # no emparentados + padres
    with open(out / "phase3_like.txt", "w", encoding="ascii", newline="\n") as f:
        f.write("".join(f"{s}\n" for s in cohort))
    idx = {s: i for i, s in enumerate(samples)}
    children = []
    for kid, _, _ in ped:
        s = idx[kid]
        _write_sam(out / f"{kid}.sam", ref, pos, G[2 * s], G[2 * s + 1], rng, imbalance)
        children.append(kid)
    return {"dir": out, "contig": CONTIG, "ref_len": REF_LEN, "children": children,
            "pedigree": [tuple(p) for p in ped], "cohort": cohort}
