#!/usr/bin/env bash
# GO 2B · las ramas PREREGISTRADAS, en el orden acordado. STOP al terminar.
#
#   0  preflight critico  BAM, BAI, referencia, .fai, compatibilidad de contigs
#                         y procedencia. Si falla: ABORTA. No corre ningun caller.
#   1  mosdepth           cobertura en ventanas · SOLO QC, no es un llamador de CNV
#   2  Manta              SV genoma completo (split reads + pares discordantes)
#   3  DELLY              SV genoma completo, llamador ortogonal
#   4  CNVpytor           RD + BAF: numero de copia, desequilibrio alelico, LOH neutra
#   5  MEI                xTea (PRIMARIO) + SCRAMble (ORTOGONAL), genoma completo
#   6  BUB1B read-backed  metricas por lectura de los dos alelos + replicacion tecnica
#   7  MitoRead           mtDNA:nuclear consciente de NUMT
#   8  DMPK               ExpansionHunter sobre un catalogo derivado de UN SOLO locus
#   9  Tier 1 + resumen   interrogacion de BUB1B +/-1 Mb y manifest
#
# TAXONOMIA DE ESTADOS (cuatro, y no se mezclan)
#   SUCCESS             se ejecuto y sus salidas son validas
#   FAILED              se ejecuto y fallo. NUNCA se degrada a NOT_RUN: que una
#                       herramienta se intentara y fallara es informacion.
#   SKIPPED_DEPENDENCY  no se ejecuto porque fallo un prerequisito suyo
#   NOT_RUN             no se intento, por una razon explicita y escrita
#
# RUNNING no es un quinto estado: es el estado TRANSITORIO mientras la etapa esta
# en vuelo. Se escribe antes de lanzar la herramienta y lo sobrescribe uno de los
# cuatro terminales al acabar. Existe porque la procedencia de una etapa en curso
# tambien tiene que ser legible: sin esto, una etapa corriendo es indistinguible
# de una que nunca se intento. Una etapa que queda en RUNNING indica una corrida
# interrumpida, y sus dependientes la ven como no-SUCCESS, que es lo correcto.
#
# ALCANCE DEL FALLO
#   critico y compartido (BAM, BAI, referencia, contigs, procedencia) -> ABORTA todo
#   local de una rama (Manta, DELLY, CNVpytor, xTea, SCRAMble, MitoRead,
#   ExpansionHunter) -> FAILED en esa rama; siguen SOLO las ramas independientes
#
# OBJETO PRIMARIO: el BAM con duplicados marcados. El pre-markdup NO se usa aqui.
# Los llamadores NO se ejecutan dos veces.
#
# Cada etapa marca .go2b_<n>.done y se salta si ya existe: reanudable.
set -uo pipefail
export MSYS_NO_PATHCONV=1

REPO="${1:?uso: run_callers.sh <ruta POSIX del repositorio>}"
cd "$REPO" || exit 1
py() { "$REPO/.venv/Scripts/python.exe" "$@"; }
cfg() { py -c "import json,sys; print(json.load(open('work/align/run_config.json'))$1)"; }

HOST_REPO="$(cfg "['repo_nospace_host']")"
HOST_VCF_DIR="$(py -c "
import sys, os; sys.path.insert(0,'.')
from src.paths import patient_vcf
print(os.path.dirname(patient_vcf()).replace(chr(92),'/'))")"
VCF_BASE="$(py -c "
import sys, os; sys.path.insert(0,'.')
from src.paths import patient_vcf
print(os.path.basename(patient_vcf()))")"
SM="$(cfg "['sample_sm']")"

W=work/callers; L="$W/logs"; S="$W/status"
mkdir -p "$L" "$S" "$W/sv" "$W/cnv" "$W/mei" "$W/bub1b" "$W/mito" "$W/repeats" "$W/qc"
DK="docker run --rm -v ${HOST_REPO}/work:/work -v ${HOST_VCF_DIR}:/vcf:ro"
REF=/work/ref/runtime.fa
BAM=/work/align/full_depth.markdup.bam
THREADS=20

I_SAM=quay.io/biocontainers/samtools:1.21--h50ea8bc_0
I_BCF=quay.io/biocontainers/bcftools:1.21--h8b25389_0
I_MOS=quay.io/biocontainers/mosdepth:0.3.10--h4e814b3_1
I_MANTA=quay.io/biocontainers/manta:1.6.0--h9ee0642_2
I_DELLY=quay.io/biocontainers/delly:1.3.3--h4d20210_1
# CNVpytor y SCRAMble se ejecutan por DIGEST (el que fija el manifest), no por etiqueta; los gates de las etapas
# 4 y 5a comprueban ademas que la imagen local resuelve a ese digest antes de correr nada.
I_CNV="$(py -c "import json; print(json.load(open('src/wgs/remediation_manifest.json'))['cnvpytor_stage4']['image_by_digest'])")"
I_XTEA_BASE=quay.io/biocontainers/xtea:0.1.9--hdfd78af_0   # solo referencia historica: no puede ejecutar xTea (sin deepforest, sort BusyBox)
# xTea se ejecuta en el entorno A' (A + GNU sort) por ImageID COMPLETO, comprobado en el gate de la etapa 5b;
# la etiqueta no basta. Manifest: src/wgs/remediation_manifest.json. Dockerfiles: src/wgs/containers/.
I_XTEA_ENV_ID="$(py src/wgs/remediation_gates.py image_id)"
I_SCR="$(py -c "import json; print(json.load(open('src/wgs/remediation_manifest.json'))['scramble_stage5a']['image_by_digest'])")"
I_EH=quay.io/biocontainers/expansionhunter:5.0.0--hf366f20_1

stamp() { date -u +%FT%TZ; }
log()   { echo "[$(stamp)] $*" | tee -a "$L/callers.log"; }
done_() { [ -f "$W/.go2b_$1.done" ]; }
mark()  { echo "$(stamp)" > "$W/.go2b_$1.done"; }
CTRL_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo 'no disponible')"
# set_status <etapa> <RUNNING|SUCCESS|FAILED|SKIPPED_DEPENDENCY|NOT_RUN> [motivo]
# La cuarta columna es el commit bajo el que corre esta etapa, de modo que la
# procedencia queda visible tambien MIENTRAS corre, no solo al terminar.
set_status() {
  # Un estado terminal anterior NUNCA se pierde: antes de sobrescribir, se anexa a <etapa>.history
  # con la marca de tiempo. Asi el FAILED de una corrida previa sigue siendo legible tras el rerun.
  if [ -f "$S/$1.status" ] && [ "$(cut -f2 "$S/$1.status")" != "RUNNING" ]; then
    printf '%s\t%s\n' "$(stamp)" "$(cat "$S/$1.status")" >> "$S/$1.history"
  fi
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "${3:-}" "$CTRL_COMMIT" > "$S/$1.status"
  log "  etapa $1 → $2${3:+ · $3}"
}
# begin <etapa>: marca RUNNING antes de lanzar la herramienta
begin() { set_status "$1" RUNNING "en curso bajo $CTRL_COMMIT"; }
# sub_status <etapa> <parte> <estado>: un estado agregado no puede borrar la
# evidencia valida de una parte que si funciono (p. ej. CNVpytor RD=SUCCESS con
# BAF=FAILED sigue siendo FAILED en agregado, pero la parte RD se conserva).
sub_status() { printf '%s\t%s\n' "$2" "$3" >> "$S/$1.sub"; }
# reset_sub <etapa>: los subestados de una corrida anterior se archivan en <etapa>.sub.history antes de
# empezar de nuevo; un rerun no borra la evidencia de que RD fallo o de que una familia no llego al terminal.
reset_sub() {
  if [ -s "$S/$1.sub" ]; then
    { printf '# %s · subestados previos de la etapa %s\n' "$(stamp)" "$1"; cat "$S/$1.sub"; } >> "$S/$1.sub.history"
  fi
  : > "$S/$1.sub"
}
# archive_attempt <etapa> <ruta>...: las salidas de un intento anterior se mueven a work/callers/attempts/<etapa>_<utc>/
# antes de volver a correr. Ni se borran (evidencia) ni se dejan donde una herramienta que ANEXA (el parche de SCRAMble
# suma _rejected_count y anexa _rejected_records) o que reabre un fichero (sample.pytor) las mezclaria con el intento nuevo.
archive_attempt() {
  local st="$1" dst moved=0 p; shift
  dst="$W/attempts/${st}_$(stamp | tr -d ':')"
  for p in "$@"; do
    if [ -e "$p" ]; then mkdir -p "$dst"; mv "$p" "$dst/"; moved=$((moved+1)); fi
  done
  if [ "$moved" -gt 0 ]; then log "  etapa $st: $moved salida(s) de un intento anterior archivadas en $dst"; fi
  return 0
}
# is_nonneg_int <texto>: entero decimal >= 0, sin signo, sin espacios, no vacio
is_nonneg_int() { case "$1" in ''|*[!0-9]*) return 1;; *) return 0;; esac; }
status_of() { [ -f "$S/$1.status" ] && cut -f2 "$S/$1.status" || echo "NOT_REACHED"; }

# --- etapas que quedaron en RUNNING de una corrida anterior -----------------
# Una etapa en RUNNING significa que la corrida anterior se interrumpio antes
# de que esa etapa escribiera su estado terminal. Dos reglas, y ninguna crea un
# estado terminal nuevo:
#   no cuenta como SUCCESS: `status_of` devuelve RUNNING, y toda dependencia
#     compara contra SUCCESS, asi que la ve como no-SUCCESS;
#   no se auto-salta: el hecho se REGISTRA primero en status/interrupted.tsv y
#     solo despues decide el flujo normal si la etapa se repite.
# Sin este registro la interrupcion se repetiria en silencio y el resumen final
# no distinguiria una etapa rehecha tras un corte de una que corrio una sola vez.
INTERRUPTED_FOUND=0
for f in "$S"/*.status; do
  [ -f "$f" ] || continue
  [ "$(cut -f2 "$f")" = "RUNNING" ] || continue
  INTERRUPTED_FOUND=1
  st="$(cut -f1 "$f")"; pc="$(cut -f4 "$f")"
  printf '%s	%s	%s	%s\n' \
    "$(stamp)" "$st" "${pc:-sin registro de commit}" \
    "la corrida anterior quedo interrumpida: la etapa nunca escribio estado terminal" \
    >> "$S/interrupted.tsv"
  log "AVISO · la etapa $st quedo en RUNNING bajo ${pc:-sin registro de commit}: la corrida anterior se interrumpio. No cuenta como SUCCESS y queda registrada en status/interrupted.tsv"
  if done_ "$st"; then
    log "  contradiccion: tenia marcador .done con estado RUNNING. Se retira el marcador, porque una etapa que nunca escribio estado terminal no puede saltarse"
    rm -f "$W/.go2b_$st.done"
  fi
done


log "GO 2B inicio · objeto primario: BAM con duplicados marcados"
# El commit que se registra como procedencia solo es verdad si el arbol de trabajo esta limpio.
# Sin esto, una corrida con cambios sin commitear nombraria un commit cuyo contenido no es el que corrio.
# Decide el CODIGO DE SALIDA del gate (cierra en fallo: git status o git rev-parse con rc!=0 tambien abortan), no un grep.
if ! py src/wgs/remediation_gates.py worktree >> "$L/callers.log" 2>&1; then
  log "ABORT: arbol de trabajo sucio; relanzar unicamente desde codigo versionado"
  echo "EXIT_CODE=5" > "$W/go2b.exit"; exit 5
fi

# =================================================== 0 · preflight critico ===
# Un fallo aqui es COMPARTIDO: aborta la corrida entera. Ningun caller puede
# producir un resultado interpretable sobre una base rota.
#
# El preflight se REPITE siempre que cambie el commit del control de flujo. Su
# funcion es revalidar la base compartida (BAM, BAI, referencia, contigs,
# procedencia) BAJO el codigo que va a invocar a los llamadores, y cuesta solo
# leer la cabecera del BAM. Saltarlo en una reanudacion y seguir afirmando
# "preflight revalidado bajo este commit" seria escribir algo que no ocurrio.
PRE_COMMIT="$( [ -f "$S/0.status" ] && cut -f4 "$S/0.status" || echo '' )"
if done_ 0 && [ "$PRE_COMMIT" != "$CTRL_COMMIT" ]; then
  log "0 · el preflight se repite: sellado bajo '${PRE_COMMIT:-sin registro de commit}', control de flujo $CTRL_COMMIT"
  rm -f "$W/.go2b_0.done"
fi
# ... y tambien cuando la corrida se reanuda tras una interrupcion: es justo cuando mas falta hace revalidar la base.
if done_ 0 && [ "$INTERRUPTED_FOUND" = "1" ]; then
  log "0 · el preflight se repite: se detecto una etapa interrumpida en RUNNING"
  rm -f "$W/.go2b_0.done"
fi
if ! done_ 0; then
  log "0 · preflight critico (compartido): BAM, BAI, referencia, contigs, procedencia"
  begin 0
  crit_fail=""
  for f in work/align/full_depth.markdup.bam work/align/full_depth.markdup.bam.bai \
           work/ref/runtime.fa work/ref/runtime.fa.fai work/align/reference_gate.json \
           work/align/alignment_manifest.json work/align/run_config.json; do
    [ -s "$f" ] || crit_fail="$crit_fail $f"
  done
  [ -z "$crit_fail" ] || { set_status 0 FAILED "faltan artefactos criticos:$crit_fail"; \
    log "ABORT: preflight critico fallido"; echo "EXIT_CODE=3" > "$W/go2b.exit"; exit 3; }
  # el gate de referencia del GO 2A tiene que estar en GO
  py -c "
import json,io,sys
g=json.load(io.open('work/align/reference_gate.json'))
sys.exit(0 if g.get('GO') else 1)" || { set_status 0 FAILED "el gate de referencia del GO 2A no esta en GO"; \
    log "ABORT"; echo "EXIT_CODE=3" > "$W/go2b.exit"; exit 3; }
  # los contigs del BAM tienen que coincidir con los del .fai de la referencia
  $DK $I_SAM sh -c "samtools view -H $BAM | grep '^@SQ' | sed -E 's/.*SN:([^\t]+)\tLN:([0-9]+).*/\1\t\2/' | sort" \
    > "$W/qc/bam_contigs.tsv" 2>> "$L/preflight.log"
  sort -k1,1 work/ref/runtime.fa.fai | cut -f1,2 | sort > "$W/qc/ref_contigs.tsv"
  if ! diff -q <(sort "$W/qc/bam_contigs.tsv") <(sort "$W/qc/ref_contigs.tsv") >/dev/null; then
    set_status 0 FAILED "los contigs del BAM no coinciden con los de la referencia"
    log "ABORT: incompatibilidad de contigs"; echo "EXIT_CODE=3" > "$W/go2b.exit"; exit 3
  fi
  set_status 0 SUCCESS "$(wc -l < "$W/qc/bam_contigs.tsv") contigs coincidentes"
  mark 0
fi
[ "$(status_of 0)" = "SUCCESS" ] || { log "ABORT: el preflight critico no esta en SUCCESS"; \
  echo "EXIT_CODE=3" > "$W/go2b.exit"; exit 3; }

# ------------------------------------------------------ 1 · mosdepth (QC) ---
# Evaluacion del ARRASTRE antes de decidir si se repite. Dos ejes separados:
#   execution_status         lo que paso al ejecutar. Historico, no se reescribe.
#   carry_forward_validation si esas salidas se pueden reutilizar AHORA.
# Una validacion fallida NO convierte la ejecucion original en FAILED: solo
# obliga a repetir la etapa. Unicamente una nueva ejecucion fallida da FAILED.
if done_ 1 && [ ! -f "$S/1.status" ]; then
  py src/wgs/carry_forward.py accept 1 2>&1 | tee -a "$L/carry_forward.log"
  case "${PIPESTATUS[0]}" in
    0) set_status 1 SUCCESS "carried_forward · ver status/1.carry.json" ;;
    2) log "  arrastre no validado: se repite mosdepth (el SUCCESS historico no se reescribe)"
       rm -f "$W/.go2b_1.done" ;;
    3) log "ABORT: el preflight critico no esta en SUCCESS"
       echo "EXIT_CODE=3" > "$W/go2b.exit"; exit 3 ;;
    # Cualquier otro codigo es un fallo de la propia comprobacion, no del
    # preflight. Se dice tal cual en vez de culpar a la etapa equivocada.
    *) log "ABORT: la comprobacion de arrastre fallo (codigo ${PIPESTATUS[0]}); ver logs/carry_forward.log"
       echo "EXIT_CODE=4" > "$W/go2b.exit"; exit 4 ;;
  esac
fi
if ! done_ 1; then
  log "1 · mosdepth · cobertura en ventanas de 1 kb (QC, no es CNV calling)"
  begin 1
  if $DK $I_MOS mosdepth -t 4 -n --by 1000 /work/callers/qc/win1kb "$BAM" > "$L/mosdepth.log" 2>&1 \
     && [ -s "$W/qc/win1kb.regions.bed.gz" ]; then
    set_status 1 SUCCESS "ejecutada bajo este commit"; mark 1
  else
    set_status 1 FAILED "mosdepth: nueva ejecucion fallida"
  fi
fi

# ---------------------------------------------------------- 2 · Manta (SV) ---
if ! done_ 2; then
  log "2 · Manta · SV genoma completo"
  begin 2
  rm -rf "$W/sv/manta"
  if $DK $I_MANTA configManta.py --bam "$BAM" --referenceFasta "$REF" \
        --runDir /work/callers/sv/manta > "$L/manta_config.log" 2>&1 \
     && $DK $I_MANTA /work/callers/sv/manta/runWorkflow.py -m local -j $THREADS -g 40 \
          > "$L/manta_run.log" 2>&1 \
     && [ -s "$W/sv/manta/results/variants/diploidSV.vcf.gz" ]; then
    set_status 2 SUCCESS; mark 2
  else
    set_status 2 FAILED "Manta (ver logs/manta_*.log)"
  fi
fi

# ---------------------------------------------------------- 3 · DELLY (SV) ---
if ! done_ 3; then
  log "3 · DELLY · SV genoma completo, llamador ortogonal"
  begin 3
  if $DK -e OMP_NUM_THREADS=$THREADS $I_DELLY \
        delly call -g "$REF" -o /work/callers/sv/delly.bcf "$BAM" > "$L/delly.log" 2>&1 \
     && $DK $I_BCF sh -c "bcftools view /work/callers/sv/delly.bcf -Oz -o /work/callers/sv/delly.vcf.gz && bcftools index -t /work/callers/sv/delly.vcf.gz" >> "$L/delly.log" 2>&1 \
     && [ -s "$W/sv/delly.vcf.gz" ]; then
    set_status 3 SUCCESS; mark 3
  else
    set_status 3 FAILED "DELLY (ver logs/delly.log)"
  fi
fi

# ------------------------------------------------- 4 · CNVpytor (RD + BAF) ---
if ! done_ 4; then
  log "4 · CNVpytor · profundidad de lectura y frecuencia del alelo B"
  begin 4
  R=/work/callers/cnv/sample.pytor
  reset_sub 4
  archive_attempt 4 "$W/cnv/sample.pytor" "$W/cnv/calls_rd.tsv" "$W/cnv/calls_combined.tsv"
  # La imagen fijada no trae los recursos de GC y mascara (y devuelve codigo 0 cuando faltan). Se montan
  # SOLO LECTURA los siete ficheros congelados al commit upstream 3adc56f, tras comprobar su sha256
  # contra el manifest. Si el gate falla, la etapa queda FAILED con motivo y no corre nada.
  CNV_RES="$(py -c "import json; print(json.load(open('src/wgs/remediation_manifest.json'))['cnvpytor_stage4']['resource_dir_rel'])")"
  DK_CNV="$DK -v ${HOST_REPO}/${CNV_RES}:/usr/local/lib/python3.12/site-packages/cnvpytor/data:ro"
  # Gate POSITIVO de arranque (no basta con que falte el mensaje de error): -rg_info tiene que devolver rc=0 y su salida
  # tiene que listar '* hg38' con 'GC file specified: Yes' y 'Mask file specified: Yes', la salida conocida del scratch.
  cnvpytor_startup_ok() {
    local rg_log="$L/cnvpytor_rg_info.log" rg_rc
    if $DK_CNV $I_CNV cnvpytor -rg_info > "$rg_log" 2>&1; then rg_rc=0; else rg_rc=$?; fi
    cat "$rg_log" >> "$L/cnvpytor.log"
    py src/wgs/remediation_gates.py cnvpytor_startup "$rg_log" "$rg_rc" >> "$L/cnvpytor.log" 2>&1
  }
  # EXEC-OOM-001: en el rerun bajo ffb3c09, -rd murio por OOM (exit 137) con la VM de Docker en 30 GiB tras leer los 2 580 contigs.
  # Gate de memoria PREVIO, operacional: objetivo local 48GB en ~/.wslconfig, MemTotal efectivo de Docker >= 47 GiB, sin otros
  # contenedores, imagen por digest. Es una remediacion de esta maquina, no un requisito publicado de CNVpytor. Si vuelve a haber
  # OOM: FAILED, sin bajar -j, sin mas memoria, sin rescatar el RD de intentos previos; se preserva todo y se readjudica.
  if ! py src/wgs/remediation_gates.py stage4_memory >> "$L/cnvpytor.log" 2>&1; then
    sub_status 4 RD NOT_RUN; sub_status 4 BAF NOT_RUN
    set_status 4 FAILED "gate de memoria no superado (ver status/4.memory.gate.json)"
  elif ! py src/wgs/remediation_gates.py stage4 >> "$L/cnvpytor.log" 2>&1; then
    sub_status 4 RD NOT_RUN; sub_status 4 BAF NOT_RUN
    set_status 4 FAILED "gate de recursos congelados no superado (ver status/4.gate.json)"
  elif ! cnvpytor_startup_ok; then
    sub_status 4 RD NOT_RUN; sub_status 4 BAF NOT_RUN
    set_status 4 FAILED "arranque de CNVpytor no confirmado: -rg_info tiene que devolver rc=0 y listar hg38 con GC y mascara (ver status/4.startup.gate.json, logs/cnvpytor_rg_info.log)"
  elif $DK_CNV $I_CNV cnvpytor -root $R -rd "$BAM" >> "$L/cnvpytor.log" 2>&1 \
     && $DK_CNV $I_CNV cnvpytor -root $R -his 1000 10000 100000 >> "$L/cnvpytor.log" 2>&1 \
     && $DK_CNV $I_CNV cnvpytor -root $R -partition 1000 10000 100000 >> "$L/cnvpytor.log" 2>&1 \
     && $DK_CNV $I_CNV sh -c "cnvpytor -root $R -call 1000 10000 100000 > /work/callers/cnv/calls_rd.tsv" >> "$L/cnvpytor.log" 2>&1 \
     && [ -s "$W/cnv/calls_rd.tsv" ]; then
    sub_status 4 RD SUCCESS
    # La mitad BAF puede fallar sin invalidar la mitad RD. El estado AGREGADO
    # sera FAILED, pero el subestado conserva la evidencia valida de RD.
    if $DK_CNV $I_CNV cnvpytor -root $R -snp "/vcf/$VCF_BASE" -sample "$SM" >> "$L/cnvpytor.log" 2>&1 \
       && $DK_CNV $I_CNV cnvpytor -root $R -mask_snps >> "$L/cnvpytor.log" 2>&1 \
       && $DK_CNV $I_CNV cnvpytor -root $R -baf 10000 100000 >> "$L/cnvpytor.log" 2>&1 \
       && $DK_CNV $I_CNV sh -c "cnvpytor -root $R -call combined 100000 > /work/callers/cnv/calls_combined.tsv" >> "$L/cnvpytor.log" 2>&1 \
       && [ -s "$W/cnv/calls_combined.tsv" ]; then
      sub_status 4 BAF SUCCESS
      set_status 4 SUCCESS "RD y BAF"
    else
      sub_status 4 BAF FAILED
      set_status 4 FAILED "agregado FAILED; RD produjo llamadas validas y se conserva (ver subestados)"
    fi
    mark 4
  else
    sub_status 4 RD FAILED
    sub_status 4 BAF SKIPPED_DEPENDENCY
    set_status 4 FAILED "CNVpytor, mitad RD (ver logs/cnvpytor.log)"
  fi
fi

# ------------------------------------------------------------- 5 · MEI -------
# Papeles fijados en el preregistro, independientes del orden de ejecucion:
#   xTea     = PRIMARIO
#   SCRAMble = ORTOGONAL
if ! done_ 5b; then
  log "5b · xTea (PRIMARIO) · inserciones de elementos moviles · entorno A' por ImageID"
  begin 5b
  reset_sub 5b
  # Lo adjudicado tras el scratch: (1) gate del ImageID COMPLETO de A', de los 12 ficheros de biblioteca
  # que exige -y 7 y de GENCODE v33; (2) -x null y --xtea, que el generador exige; (3) bam_list.txt con
  # <sample_id>\t<ruta>; (4) EJECUCION EFECTIVA de run_xTEA_pipeline.sh por familia, con su rc capturado; (5) terminal
  # cientifico = genotipado completado + --gVCF completado en el fichero de nombre FIJO que x_TEA_main escribe
  # (<bam sin extension>_<LINE1|ALU|SVA>.vcf), unico .vcf de la familia, que bcftools parsea; (6) rc!=0 solo se admite
  # si lo explica EXCLUSIVAMENTE el paso visual --igv --bamsnap (opcion inexistente en 0.1.9: error de optparse, tras el
  # paso gVCF, cero Tracebacks) y queda como subestado SKIPPED_UNSUPPORTED_IN_XTEA_0.1.9; cualquier otro error o rc =
  # familia FAILED aunque existan ficheros. Biblioteca y GENCODE se montan SOLO LECTURA en rutas que no tapan nada
  # del sistema (nunca /lib).
  XLIB="$(py -c "import json; m=json.load(open('src/wgs/remediation_manifest.json'))['xtea_stage5b']; print(m['library']['dir_rel'])")"
  XGEN="$(py -c "import json; m=json.load(open('src/wgs/remediation_manifest.json'))['xtea_stage5b']; print(m['gencode']['dir_rel'])")"
  DK_XTEA="$DK -v ${HOST_REPO}/${XLIB}:/res/xtea_lib:ro -v ${HOST_REPO}/${XGEN}:/res/gencode:ro"
  XW=/work/callers/mei/xtea
  if ! py src/wgs/remediation_gates.py stage5b >> "$L/xtea_gate.log" 2>&1; then
    for fam in L1 Alu SVA; do sub_status 5b "$fam" NOT_RUN; done
    set_status 5b FAILED "gate de A'/biblioteca/GENCODE no superado (ver status/5b.gate.json)"
  else
    archive_attempt 5b "$W/mei/xtea"; mkdir -p "$W/mei/xtea"
    printf '%s\n' "$SM" > "$W/mei/xtea/sample_id.txt"
    printf '%s\t%s\n' "$SM" "$BAM" > "$W/mei/xtea/bam_list.txt"
    if $DK_XTEA "$I_XTEA_ENV_ID" sh -c "cd $XW && xtea -x null -i sample_id.txt -b bam_list.txt -p $XW/ -o submit.sh -l /res/xtea_lib/ -r $REF -g /res/gencode/gencode.v33.annotation.gff3 --xtea /usr/local/lib/ -f 5907 -y 7 -n $THREADS -m 32 -q 1 -t 0-23" > "$L/xtea_prep.log" 2>&1 \
       && [ -f "$W/mei/xtea/$SM/L1/run_xTEA_pipeline.sh" ] && [ -f "$W/mei/xtea/$SM/Alu/run_xTEA_pipeline.sh" ] && [ -f "$W/mei/xtea/$SM/SVA/run_xTEA_pipeline.sh" ]; then
      XOK=1
      for fam in L1 Alu SVA; do
        FD="$W/mei/xtea/$SM/$fam"
        XLOG="$L/xtea_exec_$fam.log"
        # bash -x deja en el log la traza de cada paso del script generado (como en el scratch): sirve para situar el
        # error de --bamsnap DESPUES del paso --gVCF. El rc se captura; no se descarta.
        if $DK_XTEA "$I_XTEA_ENV_ID" bash -x "$XW/$SM/$fam/run_xTEA_pipeline.sh" > "$XLOG" 2>&1; then XRC=0; else XRC=$?; fi
        GNTP="$FD/candidate_disc_filtered_cns.txt.high_confident.post_filtering_with_gene_gntp.txt"
        VCF_NAME="$(py src/wgs/remediation_gates.py xtea_vcf_name "$fam")"; VCF="$FD/$VCF_NAME"
        NVCF="$(find "$FD" -maxdepth 1 -name '*.vcf' 2>/dev/null | wc -l | tr -d ' ')"
        TRACEBACKS="$(grep -c '^Traceback (most recent call last)' "$XLOG" || true)"
        ERRS="$(grep -c 'x_TEA_main.py: error:' "$XLOG" || true)"
        BAMSNAP="$(grep -c 'error: no such option: --bamsnap' "$XLOG" || true)"
        GV_LINE="$(grep -n -- '--gVCF' "$XLOG" | head -1 | cut -d: -f1)"; GV_LINE="${GV_LINE:-0}"
        BS_LINE="$(grep -n 'error: no such option: --bamsnap' "$XLOG" | head -1 | cut -d: -f1)"; BS_LINE="${BS_LINE:-0}"
        RC_OK=0
        if [ "$XRC" -eq 0 ]; then RC_OK=1
        elif [ "$BAMSNAP" -gt 0 ] && [ "$ERRS" -eq "$BAMSNAP" ] && [ "$TRACEBACKS" -eq 0 ] && [ "$GV_LINE" -gt 0 ] && [ "$BS_LINE" -gt "$GV_LINE" ]; then RC_OK=1
        fi
        if [ "$RC_OK" = "1" ] && [ -f "$GNTP" ] && [ "$NVCF" = "1" ] && [ -s "$VCF" ] \
           && $DK $I_BCF sh -c "bcftools view $XW/$SM/$fam/$VCF_NAME > /dev/null" >> "$XLOG" 2>&1; then
          sub_status 5b "$fam" SUCCESS
        else
          sub_status 5b "$fam" FAILED; XOK=0
        fi
        log "  5b/$fam: rc=$XRC tracebacks=$TRACEBACKS errores_optparse=$ERRS de_ellos_bamsnap=$BAMSNAP gntp=$([ -f "$GNTP" ] && echo si || echo no) vcfs=$NVCF esperado=$VCF_NAME"
        if [ "$BAMSNAP" -gt 0 ]; then sub_status 5b "${fam}_igv_bamsnap" SKIPPED_UNSUPPORTED_IN_XTEA_0.1.9; fi
      done
      if [ "$XOK" = "1" ]; then
        set_status 5b SUCCESS "L1, Alu y SVA: genotipado + gVCF validos"; mark 5b
      else
        set_status 5b FAILED "xTea: alguna familia no alcanzo el terminal cientifico (ver subestados y logs/xtea_exec_*.log)"
      fi
    else
      for fam in L1 Alu SVA; do sub_status 5b "$fam" SKIPPED_DEPENDENCY; done
      set_status 5b FAILED "xTea: el generador fallo (ver logs/xtea_prep.log)"
    fi
  fi
fi
if ! done_ 5a; then
  log "5a · SCRAMble (ORTOGONAL) · inserciones por lecturas recortadas · escritor de VCF parcheado"
  begin 5a
  archive_attempt 5a "$W/mei/clusters.txt" "$W"/mei/scramble*
  # El escritor de VCF de SCRAMble 1.0.2 aborta si una insercion cae en POS=0 (viola VCF 1-based). El parche
  # versionado en src/wgs/patches/ pone en cuarentena las coordenadas invalidas con motivo, sin imputar ni
  # borrar en silencio, y se monta SOLO LECTURA sobre el fichero de la imagen: el digest no cambia. El gate
  # comprueba, por digest, que la imagen local es la fijada, que el make.vcf.R ORIGINAL dentro de ella tiene el sha256
  # esperado (observado ahora, no solo anotado) y que el parche versionado tiene el suyo, antes de montarlo; tras correr,
  # el sha256 del fichero montado que SCRAMble vio queda en el log y se exige igual al del parche. Exito = scramble.vcf
  # no vacio que bcftools parsea + scramble_MEIs.txt presente + scramble_rejected_count.txt con un entero >= 0
  # (scramble_rejected_records.txt solo si hubo rechazos). Las salidas de un intento anterior se archivan antes: el
  # parche ANEXA y SUMA, no sobrescribe.
  SPATCH="$(py -c "import json; print(json.load(open('src/wgs/remediation_manifest.json'))['scramble_stage5a']['patch_file_rel'])")"
  DK_SCR="$DK -v ${HOST_REPO}/${SPATCH}:/usr/local/share/scramble/bin/make.vcf.R:ro"
  SPATCH_SHA="$(py -c "import json; print(json.load(open('src/wgs/remediation_manifest.json'))['scramble_stage5a']['patched_sha256'])")"
  if ! py src/wgs/remediation_gates.py stage5a >> "$L/scramble_gate.log" 2>&1; then
    set_status 5a FAILED "gate de imagen/original/parche no superado (ver status/5a.gate.json)"
  elif $DK $I_SCR sh -c "cluster_identifier $BAM > /work/callers/mei/clusters.txt" > "$L/scramble_cluster.log" 2>&1 \
     && [ -s "$W/mei/clusters.txt" ] \
     && $DK_SCR $I_SCR sh -c "sha256sum /usr/local/share/scramble/bin/make.vcf.R && Rscript /usr/local/share/scramble/bin/SCRAMble.R --out-name /work/callers/mei/scramble --cluster-file /work/callers/mei/clusters.txt --install-dir /usr/local/share/scramble/bin --mei-refs /usr/local/share/scramble/resources/MEI_consensus_seqs.fa --ref $REF --eval-meis" > "$L/scramble_eval.log" 2>&1 \
     && grep -q "^${SPATCH_SHA}  /usr/local/share/scramble/bin/make.vcf.R" "$L/scramble_eval.log" \
     && [ -s "$W/mei/scramble.vcf" ] && [ -f "$W/mei/scramble_MEIs.txt" ] \
     && REJ="$(tr -d '[:space:]' < "$W/mei/scramble_rejected_count.txt" 2>/dev/null)" && is_nonneg_int "$REJ" \
     && $DK $I_BCF sh -c "bcftools view /work/callers/mei/scramble.vcf > /dev/null" >> "$L/scramble_eval.log" 2>&1; then
    set_status 5a SUCCESS "VCF valido; scramble_MEIs.txt presente; rechazos por coordenada: $REJ"; mark 5a
  else
    set_status 5a FAILED "SCRAMble (ver logs/scramble_*.log)"
  fi
fi

# ------------------------------------------- 6 · BUB1B basado en lecturas ----
if ! done_ 6; then
  log "6 · adjudicacion por lecturas de los dos alelos + replicacion tecnica"
  begin 6
  py src/wgs/callers_summary.py regions > "$W/bub1b/targets.tsv" 2>> "$L/bub1b.log"
  tr -d '\r' < "$W/bub1b/targets.tsv" > "$W/bub1b/t.tmp" && mv "$W/bub1b/t.tmp" "$W/bub1b/targets.tsv"
  R1="$(head -1 "$W/bub1b/targets.tsv" | cut -f2)"
  if $DK $I_SAM sh -c "samtools view -h $BAM $R1 -o /work/callers/bub1b/locus.sam" >> "$L/bub1b.log" 2>&1 \
     && $DK $I_BCF sh -c "bcftools mpileup -f $REF -r $R1 -a AD,DP,SP -q 0 -Q 0 -d 500 $BAM 2>/dev/null | bcftools call -m -Oz -o /work/callers/bub1b/replication.vcf.gz && bcftools index -t /work/callers/bub1b/replication.vcf.gz" >> "$L/bub1b.log" 2>&1 \
     && py src/wgs/callers_summary.py bub1b >> "$L/bub1b.log" 2>&1; then
    set_status 6 SUCCESS; mark 6
  else
    set_status 6 FAILED "adjudicacion BUB1B (ver logs/bub1b.log)"
  fi
fi

# ---------------------------------------------------------- 7 · MitoRead ----
if ! done_ 7; then
  log "7 · MitoRead · mtDNA:nuclear consciente de NUMT"
  begin 7
  if $DK $I_SAM sh -c "samtools depth -a -r M $BAM > /work/callers/mito/chrM_q0.txt" > "$L/mito.log" 2>&1 \
     && $DK $I_SAM sh -c "samtools depth -a -Q 30 -r M $BAM > /work/callers/mito/chrM_q30.txt" >> "$L/mito.log" 2>&1 \
     && py src/wgs/callers_summary.py mito >> "$L/mito.log" 2>&1; then
    set_status 7 SUCCESS; mark 7
  else
    set_status 7 FAILED "MitoRead (ver logs/mito.log)"
  fi
fi

# ------------------------------------------------- 8 · DMPK (cribado P1) ----
# Catalogo DERIVADO de un solo locus: no se generan ni se miran otros loci,
# ni siquiera de forma incidental.
if ! done_ 8; then
  log "8 · ExpansionHunter · catalogo derivado con DMPK unicamente"
  begin 8
  # copia del catalogo oficial fuera del contenedor, para poder hashearla y derivar
  $DK $I_EH sh -c "cat /usr/local/share/ExpansionHunter/variant_catalog/grch38/variant_catalog.json" \
    > "$W/repeats/catalog_official_grch38.json" 2>> "$L/dmpk_catalog.log"
  if py src/wgs/callers_summary.py dmpk_catalog > "$L/dmpk_catalog.log" 2>&1 \
     && [ -s "$W/repeats/catalog_dmpk_only.json" ] \
     && $DK $I_EH ExpansionHunter --reads "$BAM" --reference "$REF" \
          --variant-catalog /work/callers/repeats/catalog_dmpk_only.json \
          --output-prefix /work/callers/repeats/eh --threads 8 > "$L/expansionhunter.log" 2>&1 \
     && [ -s "$W/repeats/eh.json" ]; then
    set_status 8 SUCCESS "solo DMPK"; mark 8
  else
    set_status 8 FAILED "ExpansionHunter (ver logs/expansionhunter.log)"
  fi
fi

# --------------------------------------------- 9 · Tier 1 y resumen final ----
log "9 · interrogacion de BUB1B +/-1 Mb y resumen"
# La etapa 9 escribe su propio estado terminal: su exito ya no se infiere del log.
begin 9
summary_ok() {
  py src/wgs/callers_summary.py summary >> "$L/callers.log" 2>&1 \
  && py -c "import json,io; json.load(io.open('work/callers/go2b_summary.json', encoding='utf-8'))"
}
# Dos pasadas (PROV-GAP-9): la primera prueba que el resumen se escribe y es JSON valido; fijado 9=SUCCESS, la segunda
# lo reescribe para que se lea a si mismo en su estado terminal y no como RUNNING. Si la segunda falla, 9 pasa a FAILED:
# lo que quede en disco no describe un estado terminal coherente.
if summary_ok; then
  set_status 9 SUCCESS "resumen escrito y JSON valido"
  if ! summary_ok; then set_status 9 FAILED "la reescritura final del resumen (con 9=SUCCESS) fallo (ver logs/callers.log)"; fi
else
  set_status 9 FAILED "resumen no escrito o JSON invalido"
fi
log "GO 2B COMPLETO · STOP: no se interpreta nada, no se toca Track 1 ni Track 2"
echo "EXIT_CODE=0" > "$W/go2b.exit"
