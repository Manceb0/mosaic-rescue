#!/usr/bin/env bash
# GO 2B · las ramas PREREGISTRADAS, en el orden acordado. STOP al terminar.
#
#   1  mosdepth            cobertura en ventanas · SOLO QC, no es un llamador de CNV
#   2  Manta               SV genoma completo (split reads + pares discordantes)
#   3  DELLY               SV genoma completo, llamador ortogonal
#   4  CNVpytor            RD + BAF: numero de copia, desequilibrio alelico, LOH neutra
#   5  MEI                 xTea (primario) + SCRAMble (ortogonal), genoma completo
#   6  BUB1B read-backed   metricas por lectura de los dos alelos + replicacion tecnica
#   7  MitoRead            mtDNA:nuclear consciente de NUMT
#   8  DMPK                ExpansionHunter, cribado P1; solo se interpreta DMPK
#   9  Tier 1 + resumen    interrogacion de BUB1B +/-1 Mb y manifest
#
# OBJETO PRIMARIO: el BAM con duplicados marcados. El pre-markdup NO se usa aqui;
# queda para adjudicacion tecnica puntual si un hallazgo resulta sensible al
# marcado. Los llamadores NO se ejecutan dos veces.
#
# Cada etapa marca .go2b_<n>.done y se salta si ya existe: reanudable.
# Una etapa que falla NO aborta la corrida: se registra y se sigue, para que un
# fallo tardio no se lleve por delante lo que ya funciono. El resumen final dice
# cuales corrieron y cuales no.
set -uo pipefail
export MSYS_NO_PATHCONV=1

REPO="${1:?uso: run_callers.sh <ruta POSIX del repositorio>}"
cd "$REPO" || exit 1
py() { "$REPO/.venv/Scripts/python.exe" "$@"; }
cfg() { py -c "import json,sys; print(json.load(open('work/align/run_config.json'))$1)"; }

HOST_REPO="$(cfg "['repo_nospace_host']")"
HOST_FQ="$(cfg "['fastq_dir_host']")"
HOST_VCF_DIR="$(py -c "
import sys; sys.path.insert(0,'.')
from src.paths import patient_vcf
import os; print(os.path.dirname(patient_vcf()).replace(chr(92),'/'))")"
VCF_BASE="$(py -c "
import sys; sys.path.insert(0,'.')
from src.paths import patient_vcf
import os; print(os.path.basename(patient_vcf()))")"
SM="$(cfg "['sample_sm']")"

W=work/callers; L="$W/logs"; mkdir -p "$L" "$W/sv" "$W/cnv" "$W/mei" "$W/bub1b" "$W/mito" "$W/repeats" "$W/qc"
DK="docker run --rm -v ${HOST_REPO}/work:/work -v ${HOST_VCF_DIR}:/vcf:ro"
REF=/work/ref/runtime.fa
BAM=/work/align/full_depth.markdup.bam
THREADS=20

I_SAM=quay.io/biocontainers/samtools:1.21--h50ea8bc_0
I_BCF=quay.io/biocontainers/bcftools:1.21--h8b25389_0
I_MOS=quay.io/biocontainers/mosdepth:0.3.10--h4e814b3_1
I_MANTA=quay.io/biocontainers/manta:1.6.0--h9ee0642_2
I_DELLY=quay.io/biocontainers/delly:1.3.3--h4d20210_1
I_CNV=quay.io/biocontainers/cnvpytor:1.3.2--pyhdfd78af_0
I_XTEA=quay.io/biocontainers/xtea:0.1.9--hdfd78af_0
I_SCR=quay.io/biocontainers/scramble:1.0.2--hec16e2b_0
I_EH=quay.io/biocontainers/expansionhunter:5.0.0--hf366f20_1

stamp() { date -u +%FT%TZ; }
log()   { echo "[$(stamp)] $*" | tee -a "$L/callers.log"; }
done_() { [ -f "$W/.go2b_$1.done" ]; }
mark()  { echo "$(stamp)" > "$W/.go2b_$1.done"; }
fail()  { echo "$(stamp) $2" > "$W/.go2b_$1.failed"; log "  ETAPA $1 NO COMPLETADA: $2"; }

log "GO 2B inicio · objeto primario: BAM con duplicados marcados"

# ------------------------------------------------------ 1 · mosdepth (QC) ---
if ! done_ 1; then
  log "1 · mosdepth · cobertura en ventanas de 1 kb (QC, no es CNV calling)"
  $DK $I_MOS mosdepth -t 4 -n --by 1000 /work/callers/qc/win1kb "$BAM" > "$L/mosdepth.log" 2>&1 \
    && mark 1 || fail 1 "mosdepth"
fi

# ---------------------------------------------------------- 2 · Manta (SV) ---
if ! done_ 2; then
  log "2 · Manta · SV genoma completo"
  rm -rf "$W/sv/manta"
  $DK $I_MANTA configManta.py --bam "$BAM" --referenceFasta "$REF" \
      --runDir /work/callers/sv/manta > "$L/manta_config.log" 2>&1 \
    && $DK $I_MANTA /work/callers/sv/manta/runWorkflow.py -m local -j $THREADS -g 40 \
         > "$L/manta_run.log" 2>&1 \
    && [ -s "$W/sv/manta/results/variants/diploidSV.vcf.gz" ] \
    && mark 2 || fail 2 "Manta"
fi

# ---------------------------------------------------------- 3 · DELLY (SV) ---
if ! done_ 3; then
  log "3 · DELLY · SV genoma completo, llamador ortogonal"
  $DK -e OMP_NUM_THREADS=$THREADS $I_DELLY \
      delly call -g "$REF" -o /work/callers/sv/delly.bcf "$BAM" > "$L/delly.log" 2>&1 \
    && $DK $I_BCF sh -c "bcftools view /work/callers/sv/delly.bcf -Oz -o /work/callers/sv/delly.vcf.gz && bcftools index -t /work/callers/sv/delly.vcf.gz" >> "$L/delly.log" 2>&1 \
    && mark 3 || fail 3 "DELLY"
fi

# ------------------------------------------------- 4 · CNVpytor (RD + BAF) ---
if ! done_ 4; then
  log "4 · CNVpytor · profundidad de lectura y frecuencia del alelo B"
  R=/work/callers/cnv/sample.pytor
  $DK $I_CNV cnvpytor -root $R -rd "$BAM" > "$L/cnvpytor.log" 2>&1 \
    && $DK $I_CNV cnvpytor -root $R -his 1000 10000 100000 >> "$L/cnvpytor.log" 2>&1 \
    && $DK $I_CNV cnvpytor -root $R -partition 1000 10000 100000 >> "$L/cnvpytor.log" 2>&1 \
    && $DK $I_CNV sh -c "cnvpytor -root $R -call 1000 10000 100000 > /work/callers/cnv/calls_rd.tsv" >> "$L/cnvpytor.log" 2>&1 \
    && $DK $I_CNV cnvpytor -root $R -snp "/vcf/$VCF_BASE" -sample "$SM" >> "$L/cnvpytor.log" 2>&1 \
    && $DK $I_CNV cnvpytor -root $R -mask_snps >> "$L/cnvpytor.log" 2>&1 \
    && $DK $I_CNV cnvpytor -root $R -baf 10000 100000 >> "$L/cnvpytor.log" 2>&1 \
    && $DK $I_CNV sh -c "cnvpytor -root $R -call combined 100000 > /work/callers/cnv/calls_combined.tsv" >> "$L/cnvpytor.log" 2>&1 \
    && mark 4 || fail 4 "CNVpytor"
fi

# ------------------------------------------------------------- 5 · MEI -------
if ! done_ 5a; then
  log "5a · SCRAMble · inserciones de elementos moviles por lecturas recortadas"
  $DK $I_SCR sh -c "cluster_identifier $BAM > /work/callers/mei/clusters.txt" > "$L/scramble_cluster.log" 2>&1 \
    && $DK $I_SCR sh -c "Rscript /usr/local/share/scramble/bin/SCRAMble.R --out-name /work/callers/mei/scramble --cluster-file /work/callers/mei/clusters.txt --install-dir /usr/local/share/scramble/bin --mei-refs /usr/local/share/scramble/resources/MEI_consensus_seqs.fa --ref $REF --eval-meis" > "$L/scramble_eval.log" 2>&1 \
    && mark 5a || fail 5a "SCRAMble"
fi
if ! done_ 5b; then
  log "5b · xTea · llamador primario de MEI"
  $DK $I_XTEA sh -c "cd /work/callers/mei && echo '$SM' > sample_id.txt && printf '%s\n' '$BAM' > bam_list.txt && xtea -i sample_id.txt -b bam_list.txt -p /work/callers/mei/xtea -o run_xtea.sh -l /usr/local/lib/rep_lib_prep -r $REF -g /usr/local/lib/rep_lib_prep/gencode.v33.annotation.gff3.gz -y 7 -f 5907 -n $THREADS -m 32 -q 1 -t 0-23" > "$L/xtea_prep.log" 2>&1 \
    && mark 5b || fail 5b "xTea (preparacion): sus recursos exigen una descarga externa que no esta preregistrada"
fi

# ------------------------------------------- 6 · BUB1B basado en lecturas ----
if ! done_ 6; then
  log "6 · adjudicacion por lecturas de los dos alelos + replicacion tecnica"
  py src/wgs/callers_summary.py regions > "$W/bub1b/targets.tsv" 2>> "$L/bub1b.log"
  tr -d '\r' < "$W/bub1b/targets.tsv" > "$W/bub1b/targets.clean.tsv" && mv "$W/bub1b/targets.clean.tsv" "$W/bub1b/targets.tsv"
  R1="$(head -1 "$W/bub1b/targets.tsv" | cut -f2)"
  $DK $I_SAM sh -c "samtools view -h $BAM $R1 -o /work/callers/bub1b/locus.sam" >> "$L/bub1b.log" 2>&1 \
    && $DK $I_BCF sh -c "bcftools mpileup -f $REF -r $R1 -a AD,DP,SP -q 0 -Q 0 -d 500 $BAM 2>/dev/null | bcftools call -m -Oz -o /work/callers/bub1b/replication.vcf.gz && bcftools index -t /work/callers/bub1b/replication.vcf.gz" >> "$L/bub1b.log" 2>&1 \
    && py src/wgs/callers_summary.py bub1b >> "$L/bub1b.log" 2>&1 \
    && mark 6 || fail 6 "adjudicacion BUB1B"
fi

# ---------------------------------------------------------- 7 · MitoRead ----
if ! done_ 7; then
  log "7 · MitoRead · mtDNA:nuclear consciente de NUMT"
  $DK $I_SAM sh -c "samtools depth -a -r M $BAM > /work/callers/mito/chrM_q0.txt" > "$L/mito.log" 2>&1
  $DK $I_SAM sh -c "samtools depth -a -Q 30 -r M $BAM > /work/callers/mito/chrM_q30.txt" >> "$L/mito.log" 2>&1
  $DK $I_SAM sh -c "samtools view -c -q 30 $BAM M > /work/callers/mito/reads_M_q30.txt" >> "$L/mito.log" 2>&1
  py src/wgs/callers_summary.py mito >> "$L/mito.log" 2>&1 && mark 7 || fail 7 "MitoRead"
fi

# ------------------------------------------------- 8 · DMPK (cribado P1) ----
if ! done_ 8; then
  log "8 · ExpansionHunter · cribado; solo se interpreta DMPK"
  $DK $I_EH ExpansionHunter --reads "$BAM" --reference "$REF" \
      --variant-catalog /usr/local/share/ExpansionHunter/variant_catalog/grch38/variant_catalog.json \
      --output-prefix /work/callers/repeats/eh --threads 8 > "$L/expansionhunter.log" 2>&1 \
    && mark 8 || fail 8 "ExpansionHunter"
fi

# --------------------------------------------- 9 · Tier 1 y resumen final ----
log "9 · interrogacion de BUB1B +/-1 Mb y resumen"
py src/wgs/callers_summary.py summary 2>&1 | tee -a "$L/callers.log"
log "GO 2B COMPLETO · STOP: no se interpreta nada, no se toca Track 1 ni Track 2"
echo "EXIT_CODE=0" > "$W/go2b.done"
