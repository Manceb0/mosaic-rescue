#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-014a · MitoRead, PILOTO TECNICO sobre L001.

QUE ES ESTO, Y QUE NO ES
    Es una comprobacion de que se puede extraer senal mitocondrial de los FASTQ
    disponibles y de que orden de magnitud tiene. **NO es interpretable como
    biologia del paciente.** Ver el bloque de limitaciones al final.

CORRECCION DE UN ERROR PROPIO
    Se habia declarado esta rama BLOQUEADA porque "el VCF no contiene variantes
    mitocondriales". Eso es irrelevante: mtDNA-CN es un COCIENTE DE COBERTURA y
    no necesita ninguna variante. La rama estaba mal clasificada.

POR QUE k-MEROS Y NO ALINEAMIENTO
    No hay alineador instalable en esta maquina (mappy no compila sin toolchain
    de C) ni referencia nuclear descargada. Para un piloto tecnico, contar
    lecturas que comparten k-meros con el genoma mitocondrial de referencia
    responde la pregunta "se puede medir y en que orden". Para un resultado
    interpretable haria falta alineamiento al genoma COMPLETO con filtro de
    unicidad de mapeo, que es justo lo que separa 014a de 014b.

LIMITACION QUE MAS SESGA, declarada por delante
    Los NUMT — insercciones de ADN mitocondrial en el genoma nuclear — comparten
    secuencia con el mtDNA. Sin alineamiento al genoma completo NO se pueden
    excluir, asi que este recuento esta sesgado **al alza** en una magnitud no
    cuantificada aqui.
"""
from __future__ import annotations
import io, os, gzip, json, urllib.request

MT_URL = ("https://rest.ensembl.org/sequence/region/human/MT:1..16569"
          "?content-type=text/x-fasta")
MT_FASTA = "work/mito/chrM.fa"
K = 31
STRIDE = 8           # se sondea una de cada 8 posiciones de la lectura
MIN_HITS = 2         # dos k-meros distintos: reduce coincidencias por azar
N_READS = 2_000_000  # submuestra; es un COCIENTE, no hace falta el carril entero
MT_LEN = 16569
NUC_LEN = 3_100_000_000


def fetch_mt():
    """Secuencia mitocondrial de REFERENCIA desde Ensembl. Es una descarga de
    secuencia publica: no sale ningun dato del paciente."""
    os.makedirs("work/mito", exist_ok=True)
    if os.path.exists(MT_FASTA) and os.path.getsize(MT_FASTA) > 16000:
        return io.open(MT_FASTA, encoding="utf-8").read()
    req = urllib.request.Request(MT_URL, headers={"User-Agent": "mosaic-rescue/EXP-014a"})
    with urllib.request.urlopen(req, timeout=120) as r:
        txt = r.read().decode()
    io.open(MT_FASTA, "w", encoding="utf-8").write(txt)
    return txt


def revcomp(s):
    return s.translate(str.maketrans("ACGTN", "TGCAN"))[::-1]


def build_kmers(seq):
    """K-meros del mtDNA y de su complementaria inversa. El genoma mitocondrial
    es circular, asi que se cierra el circulo."""
    s = seq.upper()
    circ = s + s[:K - 1]
    ks = {circ[i:i + K] for i in range(len(s))}
    ks |= {revcomp(x) for x in ks}
    return ks


def scan(fastq_gz, kmers, n_reads=N_READS):
    total = mito = 0
    with gzip.open(fastq_gz, "rt", errors="replace") as f:
        for i, line in enumerate(f):
            if i % 4 != 1:
                continue
            total += 1
            seq = line.strip().upper()
            hits = 0
            for p in range(0, len(seq) - K + 1, STRIDE):
                if seq[p:p + K] in kmers:
                    hits += 1
                    if hits >= MIN_HITS:
                        mito += 1
                        break
            if total >= n_reads:
                break
    return total, mito


def main():
    import sys
    sys.path.insert(0, ".")
    from src.paths import get

    fq = get("patient", "fastq_l001_r1", default=None)
    if not fq or not os.path.exists(fq):
        print("  falta la ruta del FASTQ L001 R1 en config/paths.yaml "
              "(clave patient.fastq_l001_r1)")
        return 1

    txt = fetch_mt()
    seq = "".join(l.strip() for l in txt.splitlines() if not l.startswith(">"))
    print(f"  referencia mitocondrial: {len(seq)} pb")
    kmers = build_kmers(seq)
    print(f"  k-meros ({K}-mer, ambas hebras): {len(kmers):,}\n")

    total, mito = scan(fq, kmers)
    frac = mito / total if total else 0
    # mtDNA-CN por celula = 2 x (lecturas_mt/long_mt) / (lecturas_nuc/long_nuc)
    nuc = total - mito
    cn = 2 * (mito / MT_LEN) / (nuc / NUC_LEN) if nuc else 0

    print(f"  lecturas examinadas        : {total:,}")
    print(f"  compatibles con mitocondrial: {mito:,}  ({100*frac:.4f} %)")
    print(f"  estimacion de mtDNA-CN      : {cn:.0f} copias por celula")

    os.makedirs("work/mito", exist_ok=True)
    json.dump({"reads": total, "mito_reads": mito, "fraction": frac,
               "mtdna_cn_estimate": cn, "k": K, "stride": STRIDE,
               "min_hits": MIN_HITS, "lane": "L001",
               "interpretable": False,
               "why_not": "NUMT no excluidos; un solo carril; sin controles; sin hemograma"},
              io.open("work/mito/pilot_l001.json", "w", encoding="utf-8"), indent=1)

    print("\n  === NO INTERPRETABLE COMO BIOLOGIA DEL PACIENTE ===")
    print("  · los NUMT no se pueden excluir sin alinear al genoma completo -> sesgo AL ALZA")
    print("  · un solo carril, no la profundidad completa con la que se llamo el VCF")
    print("  · sin controles procesados con pipeline identico")
    print("  · sin hemograma: plaquetas y formula distorsionan el cociente mtDNA/nuclear")
    print("  Lo unico que demuestra: que la senal es extraible y de que orden es.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
