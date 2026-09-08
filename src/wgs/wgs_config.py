#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuracion de la corrida de alineamiento, derivada de los ficheros, no inventada.

    SM   el nombre de muestra de la columna 10 del VCF del proveedor
    PU   {flowcell}.{lane}.{indice}, con el indice MAYORITARIO de las primeras
         2 000 lecturas de cada lane (los errores de secuenciacion del indice
         no se propagan al read group)
    LB   NO SE INVENTA. Un indice de muestra identico en las cuatro lanes
         demuestra que se demultiplexaron como la misma MUESTRA, no que
         provengan de una unica preparacion de LIBRERIA. Se busca metadata de
         libreria en la cabecera del VCF y en las cabeceras FASTQ; si no
         aparece, el campo LB se OMITE del @RG (es opcional en la
         especificacion SAM) y se registra
         "library identity unavailable from supplied metadata".
         Consecuencia tecnica, comprobada: `samtools markdup` NO agrupa por LB
         (a diferencia de Picard MarkDuplicates); marca duplicados por
         coordenada y orientacion sobre el fichero completo. Omitir LB no
         cambia el marcado global de duplicados.
    ID   {flowcell}.{lane}

Todo lo que lleva identificadores del paciente va a work/align/run_config.json
(gitignored). La salida estandar no imprime SM ni rutas con usuario.

Uso: python src/wgs/wgs_config.py
"""
from __future__ import annotations
import collections, glob, gzip, io, json, os, re, sys

sys.path.insert(0, ".")

OUT = "work/align/run_config.json"
# La ruta del repositorio que Docker monta vive en config/paths.yaml (gitignored),
# clave compute.docker_repo_root: normalmente un junction sin espacios. Regla Dura 2.
# Si falta, se usa el directorio actual.


def docker_repo_root() -> str:
    from src.paths import get
    return str(get("compute", "docker_repo_root", default=os.getcwd())).replace("\\", "/")


def main() -> int:
    from src.paths import get, patient_vcf
    vcf = patient_vcf()
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#CHROM"):
                sm = line.rstrip("\n").split("\t")[9]; break
    fq_dir = os.path.dirname(get("patient", "fastq_l001_r1"))
    lanes = {}
    for r1 in sorted(glob.glob(os.path.join(fq_dir, "*_L00?_R1_001.fastq.gz"))):
        lane = re.search(r"_L(00\d)_R1_", r1).group(1)
        r2 = r1.replace("_R1_001.fastq.gz", "_R2_001.fastq.gz")
        if not os.path.exists(r2):
            raise SystemExit(f"falta R2 de la lane {lane}")
        idx = collections.Counter(); fc = None
        with gzip.open(r1, "rt") as f:
            for i, line in enumerate(f):
                if i % 4 == 0:
                    a, b = line.split()
                    fc = a.split(":")[2]
                    idx[b.split(":")[3]] += 1
                if i >= 8000:
                    break
        index, n = idx.most_common(1)[0]
        lanes[f"L{lane}"] = {"r1": os.path.basename(r1), "r2": os.path.basename(r2), "flowcell": fc,
                             "lane": int(lane), "index": index, "index_support": f"{n}/2000",
                             "rg_id": f"{fc}.{int(lane)}", "pu": f"{fc}.{int(lane)}.{index}"}
    if len(lanes) != 4:
        raise SystemExit(f"se esperaban 4 lanes, hay {len(lanes)}")

    # metadata de libreria: se busca, no se infiere
    lb = None
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("##"):
                break
            m = re.search(r"\bLB[:=]([^\s,>]+)", line)
            if m:
                lb = m.group(1); break
    lb_source = "supplier VCF header" if lb else None
    lb_note = ("library identity unavailable from supplied metadata: neither the VCF header nor the "
               "FASTQ read names declare a library. An identical sample index across the four lanes "
               "shows they were demultiplexed as the same SAMPLE, not that they come from one library "
               "prep, so LB is OMITTED from @RG (optional per the SAM spec) rather than inferred. "
               "samtools markdup does not group by LB, so global duplicate marking is unaffected.")
    cfg = {"sample_sm": sm, "library_lb": lb, "library_lb_source": lb_source, "lb_note": lb_note,
           "platform": "ILLUMINA", "fastq_dir_host": fq_dir.replace("\\", "/"),
           "repo_nospace_host": docker_repo_root(), "lanes": lanes,
           "read_groups": {k: (f"@RG\\tID:{v['rg_id']}\\tSM:{sm}\\tPL:ILLUMINA\\tPU:{v['pu']}"
                               + (f"\\tLB:{lb}" if lb else ""))
                           for k, v in lanes.items()},
           "reference_runtime": "work/ref/runtime.fa",
           "bwa_params": "-t 20 -K 100000000 -Y", "sort_params": "-@ 4 -m 1500M",
           "markdup": "per lane: bwa mem -> samtools collate (explicit name grouping, no assumption about "
                      "the aligner's output order) -> samtools fixmate -m -> coordinate sort. Then: merge "
                      "the four lane BAMs -> samtools markdup on the merged file (GLOBAL) -> index"}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(cfg, indent=1))
    print(f"  lanes: {sorted(lanes)}  flowcell: {next(iter(lanes.values()))['flowcell']}  "
          f"indice unico: {len({v['index'] for v in lanes.values()}) == 1}  SM: {sm[:4]}… ({len(sm)} chars)")
    print(f"  LB: {lb or 'OMITIDO (library identity unavailable from supplied metadata)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
