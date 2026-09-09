#!/usr/bin/env bash
# GO 2A · alineamiento de profundidad completa, hasta QC e integridad. STOP despues.
#
# Etapas (cada una deja un marcador .done y se salta si ya existe; reanudable):
#   0  preflight de los 8 FASTQ: integridad gzip (descompresion completa), conteo de
#      lecturas, R1 == R2, cuatro lanes
#   1  bwa index del runtime FASTA
#   2  por lane: bwa mem (read group fiel) | samtools collate (agrupacion por
#      nombre EXPLICITA: no se asume nada sobre el orden de salida del alineador)
#      | samtools fixmate -m | samtools sort (coordenada)
#   3  merge de las 4 lanes -> markdup GLOBAL -> index. SE CONSERVAN LOS DOS
#      BAM, el merged pre-markdup y el markdup final, ambos hasheados: sin
#      metadata de libreria, el marcado global es una DECISION declarada y hay
#      que poder volver al objeto anterior a esa decision. El pre-markdup no se
#      borra hasta que GO 2A y GO 2B hayan terminado.
#   4  QC: quickcheck, flagstat global y por read group, stats, coverage por contig,
#      profundidad en BUB1B +/-50 kb y +/-1 Mb, X/Y frente a autosomas
#   5  integridad: genotipos BAM<->VCF en 20 000 sitios PASS (bcftools) y VerifyBamID2
#   6  manifest + resumen (src/wgs/alignment_qc.py). STOP: no arranca ningun caller.
#
# Parametros: los congelados en el preregistro. Nada se ajusta despues de mirar.
# Rutas: Docker monta el junction sin espacios; la salida no imprime SM ni usuario.
set -uo pipefail
export MSYS_NO_PATHCONV=1

# La ruta del repositorio llega como argumento (el lanzador vive fuera del repo):
# ninguna ruta local con nombre de usuario se escribe en este fichero versionado.
REPO="${1:?uso: run_alignment.sh <ruta POSIX del repositorio>}"
cd "$REPO" || exit 1
CFG="work/align/run_config.json"
py() { "$REPO/.venv/Scripts/python.exe" "$@"; }
jq_() { py -c "import json,sys; c=json.load(open('$CFG')); print(eval(sys.argv[1]))" "$1"; }

HOST_REPO="$(jq_ "c['repo_nospace_host']")"
HOST_FQ="$(jq_ "c['fastq_dir_host']")"
SM="$(jq_ "c['sample_sm']")"
W="work/align"; L="$W/logs"; T="$W/tmp"; mkdir -p "$L" "$T" "$W/lanes" "$W/qc" "$W/integrity"
IMG_BWA="quay.io/biocontainers/bwa:0.7.18--he4a0461_0"
IMG_SAM="quay.io/biocontainers/samtools:1.21--h50ea8bc_0"
IMG_BCF="quay.io/biocontainers/bcftools:1.21--h8b25389_0"
IMG_VB="quay.io/biocontainers/verifybamid2:2.0.3--hc004090_0"
DK="docker run --rm -v ${HOST_REPO}/work:/work -v ${HOST_FQ}:/data:ro"
REF="/work/ref/runtime.fa"
BAM="$W/full_depth.markdup.bam"

stamp() { date -u +%FT%TZ; }
log() { echo "[$(stamp)] $*" | tee -a "$L/pipeline.log"; }
done_() { [ -f "$W/.stage$1.done" ]; }
mark() { echo "$(stamp)" > "$W/.stage$1.done"; }

# ---------------------------------------------------------------- 0 preflight
if ! done_ 0; then
  log "stage 0 · preflight FASTQ"
  : > "$W/fastq_preflight.tsv"
  ok=1
  for lane in L001 L002 L003 L004; do
    r1="$(jq_ "c['lanes']['$lane']['r1']")"; r2="$(jq_ "c['lanes']['$lane']['r2']")"
    n1=$(gzip -dc "$HOST_FQ/$r1" | wc -l); rc1=$?
    n2=$(gzip -dc "$HOST_FQ/$r2" | wc -l); rc2=$?
    reads1=$((n1/4)); reads2=$((n2/4))
    echo -e "$lane\tR1\t$reads1\tgzip_rc=$rc1" >> "$W/fastq_preflight.tsv"
    echo -e "$lane\tR2\t$reads2\tgzip_rc=$rc2" >> "$W/fastq_preflight.tsv"
    if [ "$rc1" -ne 0 ] || [ "$rc2" -ne 0 ] || [ "$reads1" -ne "$reads2" ] || [ $((n1%4)) -ne 0 ]; then ok=0; fi
    log "  $lane: R1 $reads1 lecturas, R2 $reads2 lecturas, gzip rc $rc1/$rc2"
  done
  [ "$ok" -eq 1 ] || { log "STOP: preflight fallido"; exit 2; }
  mark 0
fi

# ---------------------------------------------------------------- 1 bwa index
if ! done_ 1; then
  log "stage 1 · bwa index"
  $DK $IMG_BWA bwa index "$REF" > "$L/bwa_index.log" 2>&1 || { log "STOP: bwa index fallo"; exit 2; }
  mark 1
fi

# ---------------------------------------------------------------- 2 per-lane alignment
for lane in L001 L002 L003 L004; do
  if ! done_ "2_$lane"; then
    log "stage 2 · $lane · bwa mem | collate | fixmate -m | sort"
    r1="$(jq_ "c['lanes']['$lane']['r1']")"; r2="$(jq_ "c['lanes']['$lane']['r2']")"
    rg="$(jq_ "c['read_groups']['$lane']")"
    # samtools collate -O agrupa por nombre en el flujo, sin escribir un BAM
    # intermedio y sin depender de que el alineador entregue los pares juntos.
    $DK $IMG_BWA bwa mem -t 20 -K 100000000 -Y -R "$rg" "$REF" "/data/$r1" "/data/$r2" 2> "$L/bwa_$lane.log" \
      | $DK -i $IMG_SAM sh -c "samtools collate -@ 3 -O -u -T /work/align/tmp/collate_$lane - | samtools fixmate -m -@ 2 -u - - | samtools sort -@ 4 -m 1500M -T /work/align/tmp/sort_$lane -o /work/align/lanes/$lane.bam -" 2> "$L/sort_$lane.log"
    rc=$?
    $DK $IMG_SAM samtools quickcheck "/work/align/lanes/$lane.bam" || rc=1
    [ "$rc" -eq 0 ] || { log "STOP: alineamiento de $lane fallo (rc $rc)"; exit 2; }
    rm -f "$T"/sort_${lane}*
    mark "2_$lane"
  fi
done

# ---------------------------------------------------------------- 3 merge + global markdup + index
if ! done_ 3; then
  log "stage 3 · merge 4 lanes -> markdup global -> index"
  $DK $IMG_SAM samtools merge -@ 8 -o /work/align/merged.bam /work/align/lanes/L001.bam /work/align/lanes/L002.bam /work/align/lanes/L003.bam /work/align/lanes/L004.bam > "$L/merge.log" 2>&1 || { log "STOP: merge fallo"; exit 2; }
  $DK $IMG_SAM samtools markdup -@ 8 -s -f /work/align/qc/markdup_stats.txt /work/align/merged.bam /work/align/full_depth.markdup.bam > "$L/markdup.log" 2>&1 || { log "STOP: markdup fallo"; exit 2; }
  $DK $IMG_SAM samtools index -@ 8 /work/align/full_depth.markdup.bam || { log "STOP: index fallo"; exit 2; }
  $DK $IMG_SAM samtools quickcheck /work/align/full_depth.markdup.bam || { log "STOP: quickcheck fallo"; exit 2; }
  # los DOS objetos se conservan y se hashean: merged pre-markdup y markdup final.
  # El pre-markdup NO se borra aqui; su borrado es parte de la limpieza posterior a GO 2B.
  $DK $IMG_SAM samtools index -@ 8 /work/align/merged.bam || log "aviso: no se pudo indexar el pre-markdup"
  for f in merged.bam full_depth.markdup.bam; do
    sha256sum "$W/$f" | awk -v n="$f" '{print $1"  "n}' >> "$W/bam_sha256.txt"
  done
  log "  BAM conservados: merged.bam (pre-markdup) y full_depth.markdup.bam, ambos hasheados"
  mark 3
fi

# ---------------------------------------------------------------- 4 QC
if ! done_ 4; then
  log "stage 4 · QC"
  Q="/work/align/qc"; B="/work/align/full_depth.markdup.bam"
  $DK $IMG_SAM sh -c "samtools flagstat -@ 8 $B > $Q/flagstat.txt"
  $DK $IMG_SAM sh -c "samtools view -H $B | grep '^@RG' > $Q/read_groups.txt"
  for rg in $(grep -o 'ID:[^[:space:]]*' "$W/qc/read_groups.txt" | cut -d: -f2); do
    $DK $IMG_SAM sh -c "samtools flagstat -@ 4 -r $rg $B > $Q/flagstat_rg_$rg.txt" 2>/dev/null \
      || $DK $IMG_SAM sh -c "samtools view -@ 4 -b -r $rg $B | samtools flagstat -@ 4 - > $Q/flagstat_rg_$rg.txt"
  done
  $DK $IMG_SAM sh -c "samtools stats -@ 8 $B > $Q/stats.txt"
  $DK $IMG_SAM sh -c "samtools idxstats $B > $Q/idxstats.txt"
  $DK $IMG_SAM sh -c "samtools coverage -q 20 -Q 20 $B > $Q/coverage_by_contig.tsv"
  py src/wgs/alignment_qc.py regions > "$W/qc/regions.tsv"
  # La mediana se calcula en Python, no en awk: el awk del contenedor (mawk) no
  # tiene asort(), que es una extension de GNU awk. La primera version uso
  # asort() y la etapa produjo un fichero VACIO sin fallar; el fallo silencioso
  # solo se vio porque el resumen mostro el campo de profundidad de BUB1B vacio.
  : > "$W/qc/region_depth.tsv"
  while IFS=$'\t' read -r name region; do
    $DK $IMG_SAM sh -c "samtools depth -a -q 20 -Q 20 -r $region $B" \
      | py src/wgs/alignment_qc.py depth "$name" >> "$W/qc/region_depth.tsv"
  done < "$W/qc/regions.tsv"
  [ -s "$W/qc/region_depth.tsv" ] || { log "STOP: la profundidad por region salio vacia"; exit 2; }
  mark 4
fi

# ---------------------------------------------------------------- 5 integridad
if ! done_ 5; then
  log "stage 5 · integridad BAM<->VCF y contaminacion"
  py src/wgs/alignment_qc.py sites > /dev/null                      # work/align/integrity/sites.tsv (20 000 PASS, semilla 42)
  $DK $IMG_BCF sh -c "bcftools mpileup -f $REF -R /work/align/integrity/sites.tsv -a AD,DP -q 20 -Q 20 /work/align/full_depth.markdup.bam 2>/dev/null | bcftools call -m -Oz -o /work/align/integrity/bam_calls.vcf.gz" || log "aviso: bcftools mpileup/call devolvio error"
  # VerifyBamID2: recurso b38 con nombres sin 'chr' (solo el .bed lleva nombres)
  $DK $IMG_VB sh -c "R=/usr/local/share/verifybamid2-2.0.3-0/resource/1000g.phase3.100k.b38.vcf.gz.dat; mkdir -p /work/align/integrity/vb; for e in UD V mu; do cp \$R.\$e /work/align/integrity/vb/res.dat.\$e; done; sed 's/^chr//' \$R.bed > /work/align/integrity/vb/res.dat.bed; cd /work/align/integrity/vb && verifybamid2 --SVDPrefix res.dat --Reference $REF --BamFile /work/align/full_depth.markdup.bam --NumThread 8 --Output vb2 > vb2.log 2>&1; tail -5 vb2.log" > "$L/verifybamid2.log" 2>&1 || log "aviso: VerifyBamID2 devolvio error (ver log)"
  mark 5
fi

# ---------------------------------------------------------------- 6 manifest + resumen
if ! done_ 6; then
  log "stage 6 · manifest y resumen de QC"
  py src/wgs/alignment_qc.py summary | tee -a "$L/pipeline.log"
  mark 6
fi
log "GO 2A COMPLETO · STOP: no se lanza ningun caller"
echo "EXIT_CODE=0" > "$W/go2a.done"
