"""Datos sintéticos de la auditoría mecánica C3 de SHAPEIT5 (EXP-027).

Sin datos del paciente y sin 1000G. Genera 85 muestras no emparentadas y 5 trios
(hijo = haplotipo paterno + materno recombinados, de modo que la fase verdadera es
conocida), SNP comunes con LD por mosaico de haplotipos fundadores, más sitios raros
(MAC 2-4) y singletons. Semilla fija 42 (config/paths.example.yaml, compute.seed).

Uso:
    python -m src.exp027.c3_synth --out <directorio>

Escribe truth.vcf (fase verdadera), unphased.vcf (los mismos genotipos sin fase)
y trios.ped (hijo, padre, madre).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

SEED = 42
N_COMMON, N_FOUNDERS, SWITCH_P = 1500, 8, 0.01
N_UNRELATED, N_TRIOS = 85, 5
N_RARE, N_SINGLETON = 60, 40
REGION = (10_000, 3_000_000)
CONTIG, CONTIG_LEN = "20", 64_444_167


def simulate(seed: int = SEED):
    rng = np.random.default_rng(seed)
    pos_c = np.sort(rng.choice(np.arange(*REGION), N_COMMON, replace=False))
    p = np.clip(rng.beta(0.5, 0.5, N_COMMON), 0.05, 0.95)
    founders = (rng.random((N_FOUNDERS, N_COMMON)) < p).astype(np.int8)

    def new_hap():
        h = np.empty(N_COMMON, np.int8)
        f = rng.integers(N_FOUNDERS)
        for j in range(N_COMMON):
            if rng.random() < SWITCH_P:
                f = rng.integers(N_FOUNDERS)
            h[j] = founders[f, j]
        h[rng.random(N_COMMON) < 0.001] ^= 1
        return h

    def child_hap(h1, h2):
        out = np.empty_like(h1)
        src = rng.integers(2)
        for j in range(N_COMMON):
            if rng.random() < SWITCH_P:
                src ^= 1
            out[j] = h1[j] if src == 0 else h2[j]
        return out

    samples, haps, ped = [], [], []
    for i in range(N_UNRELATED):
        samples.append(f"U{i:03d}")
        haps.append((new_hap(), new_hap()))
    for t in range(N_TRIOS):
        fa, mo = (new_hap(), new_hap()), (new_hap(), new_hap())
        ch = (child_hap(*fa), child_hap(*mo))  # hap1 = paterno, hap2 = materno
        for name, hp in ((f"F{t}", fa), (f"M{t}", mo), (f"C{t}", ch)):
            samples.append(name)
            haps.append(hp)
        ped.append((f"C{t}", f"F{t}", f"M{t}"))

    n = len(samples)
    H = np.zeros((2 * n, N_COMMON), np.int8)
    for s, (a, b) in enumerate(haps):
        H[2 * s], H[2 * s + 1] = a, b

    free = np.setdiff1d(np.arange(*REGION), pos_c)
    extra_pos = np.sort(rng.choice(free, N_RARE + N_SINGLETON, replace=False))
    macs = np.array([rng.integers(2, 5) for _ in range(N_RARE)] + [1] * N_SINGLETON)
    rng.shuffle(macs)
    E = np.zeros((2 * n, len(extra_pos)), np.int8)
    for k, m in enumerate(macs):
        E[rng.choice(2 * n, m, replace=False), k] = 1

    pos_all = np.concatenate([pos_c, extra_pos])
    G = np.concatenate([H, E], axis=1)
    order = np.argsort(pos_all)
    return samples, ped, pos_all[order], G[:, order]


def write_vcf(path: Path, samples, pos_all, G, phased: bool) -> None:
    n = len(samples)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"##fileformat=VCFv4.2\n##contig=<ID={CONTIG},length={CONTIG_LEN}>\n")
        f.write('##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count">\n')
        f.write('##INFO=<ID=AN,Number=1,Type=Integer,Description="Allele number">\n')
        f.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
        f.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(samples) + "\n")
        for j, ps in enumerate(pos_all):
            col = G[:, j]
            ac = int(col.sum())
            if ac == 0 or ac == 2 * n:
                continue
            gts = []
            for s in range(n):
                a, b = int(col[2 * s]), int(col[2 * s + 1])
                gts.append(f"{a}|{b}" if phased else f"{min(a, b)}/{max(a, b)}")
            f.write(f"{CONTIG}\t{ps}\tsnp{j}\tA\tG\t.\tPASS\tAC={ac};AN={2 * n}\tGT\t" + "\t".join(gts) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path, help="directorio de salida")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    samples, ped, pos_all, G = simulate()
    write_vcf(args.out / "truth.vcf", samples, pos_all, G, phased=True)
    write_vcf(args.out / "unphased.vcf", samples, pos_all, G, phased=False)
    with open(args.out / "trios.ped", "w", encoding="utf-8", newline="\n") as f:
        for kid, fa, mo in ped:
            f.write(f"{kid}\t{fa}\t{mo}\n")
    print(f"samples {len(samples)} | trios {len(ped)} | sites {G.shape[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
