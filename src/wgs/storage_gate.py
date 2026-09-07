#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate de almacenamiento del alineamiento de profundidad completa (EXP-012 / EXP-014a-v2).

POR QUE
    Descubrir a las catorce horas que el disco se lleno no es un contratiempo:
    es una corrida perdida y un BAM a medias que alguien puede confundir con
    uno entero. Las cifras de aqui se CALCULAN desde los FASTQ reales y desde
    reglas declaradas; no se escriben a mano.

REGLAS DE ESTIMACION (declaradas, conservadoras)
    FASTQ comprimidos              F  (medido)
    referencia + indice bwa        ~ 3,2 GB FASTA + 5,5 GB indice + 1 GB extras
    BAM ordenado (pre-markdup)     ~ 1,4 x F   (BAM ~ FASTQ.gz en tamano; margen 40 %)
    temporales de samtools sort    ~ 1,0 x F   (chunks comprimidos, se borran al terminar)
    BAM markdup final + indice     ~ 1,4 x F
    Manta + DELLY + CNVpytor + mosdepth + logs   ~ 40 GB
    PICO = referencia + BAM pre-markdup + temporales + BAM final + callers
    RETENIDO tras limpieza = referencia + BAM final + callers
    MARGEN exigido: libre >= 1,5 x PICO

Uso: python src/wgs/storage_gate.py   (sin datos del paciente en la salida)
"""
from __future__ import annotations
import io, json, os, shutil, sys

sys.path.insert(0, ".")

GB = 1024 ** 3


def main() -> int:
    from src.paths import get
    fq_dir = os.path.dirname(get("patient", "fastq_l001_r1"))
    fastqs = sorted(f for f in os.listdir(fq_dir) if f.endswith(".fastq.gz"))
    F = sum(os.path.getsize(os.path.join(fq_dir, f)) for f in fastqs)
    ref = 3.2 * GB + 5.5 * GB + 1.0 * GB
    bam_pre, tmp, bam_final, callers = 1.4 * F, 1.0 * F, 1.4 * F, 40 * GB
    peak = ref + bam_pre + tmp + bam_final + callers
    kept = ref + bam_final + callers
    work_dir = os.path.abspath("work/align")
    free = shutil.disk_usage(os.path.splitdrive(work_dir)[0] + os.sep).free
    ok = free >= 1.5 * peak
    out = {
        "n_fastq": len(fastqs), "fastq_gb": round(F / GB, 1),
        "reference_plus_index_gb": round(ref / GB, 1),
        "bam_pre_markdup_gb": round(bam_pre / GB, 1), "sort_temp_gb": round(tmp / GB, 1),
        "bam_final_plus_index_gb": round(bam_final / GB, 1), "callers_and_logs_gb": round(callers / GB, 1),
        "peak_gb": round(peak / GB, 1), "retained_after_cleanup_gb": round(kept / GB, 1),
        "free_now_gb": round(free / GB, 1), "required_free_gb_1p5x_peak": round(1.5 * peak / GB, 1),
        "temp_dir": os.path.join(work_dir, "tmp"), "work_dir": work_dir,
        "cleanup": ["borrar temporales de sort al terminar el sort", "borrar el BAM pre-markdup tras "
                    "verificar el BAM final e indice (samtools quickcheck + flagstat)",
                    "convertir a CRAM y borrar el BAM solo despues de que Manta, DELLY, CNVpytor, "
                    "mosdepth y MitoRead hayan terminado y sus salidas esten hasheadas"],
        "GO": ok,
    }
    os.makedirs(work_dir, exist_ok=True)
    io.open(os.path.join(work_dir, "storage_gate.json"), "w", encoding="utf-8").write(
        json.dumps(out, indent=1, ensure_ascii=False))
    for k, v in out.items():
        if k not in ("cleanup", "temp_dir", "work_dir"):
            print(f"  {k:<32} {v}")
    print(f"  temp_dir: work/align/tmp (mismo SSD)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
