#!/usr/bin/env bash
# EXP-027 · Auditoría mecánica C3 de SHAPEIT5 sobre datos 100 % sintéticos.
# Sin datos del paciente y sin 1000G. Reproduce los hechos registrados en
# docs/DECISIONS.md (Amendments 3 y 4 de EXP-027).
#
# Uso:   bash src/exp027/c3_audit.sh <directorio_de_salida>
# Requiere: docker y el entorno Python del repositorio (numpy).
# Imágenes fijadas por digest (config/exp027_tool_manifest.json).
set -euo pipefail

OUT="${1:?uso: c3_audit.sh <directorio_de_salida>}"
mkdir -p "$OUT"
S5="quay.io/biocontainers/shapeit5@sha256:cf3c988c2da4beda759f03300f767495944e25984a7dfa042f806c3113c6e450"
BCF="quay.io/biocontainers/bcftools@sha256:969314d56b9131683917cc5801734891a9af130daf7a0fb902b7707060b06027"
export MSYS_NO_PATHCONV=1                       # Git Bash en Windows: no reescribir /data
MNT="$(cygpath -w "$OUT" 2>/dev/null || echo "$OUT")"
s5()  { docker run --rm -v "$MNT:/data" "$S5"  "$@"; }
bcf() { docker run --rm -v "$MNT:/data" "$BCF" "$@"; }
need() { [ -s "$OUT/$1" ] || { echo "FALTA $1: la herramienta no escribió salida" >&2; exit 1; }; }

# 0. Procedencia de la herramienta: banner literal y sha256 de los binarios
s5 SHAPEIT5_phase_common --help | grep -E "Version" | tee "$OUT/shapeit5_banner.txt"
docker run --rm "$S5" sh -c 'cd /usr/local/bin && sha256sum SHAPEIT5_phase_common SHAPEIT5_phase_rare SHAPEIT5_ligate SHAPEIT5_switch' \
  | tee "$OUT/shapeit5_binaries.sha256"

# 1. Datos sintéticos (semilla 42) -> BCF indexado
python -m src.exp027.c3_synth --out "$OUT"
for f in truth unphased; do bcf sh -c "bcftools view -Ob -o /data/$f.bcf /data/$f.vcf && bcftools index -f /data/$f.bcf"; done

# 2. phase_common sin --pedigree (como en el benchmark): solo GT, sin PS ni PP
s5 SHAPEIT5_phase_common --input /data/unphased.bcf --region 20 --filter-maf 0.05 --seed 42 --output /data/common.bcf --log /data/common.log
need common.bcf; bcf bcftools index -f /data/common.bcf
bcf bcftools view -h /data/common.bcf | grep '^##FORMAT' > "$OUT/common.format.txt"

# 3. phase_rare sobre el scaffold, por defecto y con --score-singletons (experimental).
#    phase_rare NO acepta --log y devuelve exit 0 ante argumentos inválidos: se valida la salida.
for mode in default score; do
  extra=""; [ "$mode" = score ] && extra="--score-singletons"
  s5 SHAPEIT5_phase_rare --input /data/unphased.bcf --input-region 20:1-3000000 \
     --scaffold /data/common.bcf --scaffold-region 20:1-3000000 --seed 42 $extra --output /data/rare_$mode.bcf
  need "rare_$mode.bcf"; bcf bcftools index -f "/data/rare_$mode.bcf"
done
bcf bcftools view -h /data/rare_default.bcf | grep '^##FORMAT' > "$OUT/rare.format.txt"
bcf bcftools query -i 'GT="het" && INFO/AC==1' -f '[%PP\n]' /data/rare_default.bcf | sort | uniq -c > "$OUT/singleton_pp_default.txt"

# 4. switch: SER contra verdad completa y contra verdad mendeliana (-P con genotipos no faseados)
s5 SHAPEIT5_switch --validation /data/truth.bcf    --estimation /data/rare_default.bcf --frequency /data/truth.bcf --region 20 --output /data/ser
s5 SHAPEIT5_switch --validation /data/unphased.bcf --estimation /data/common.bcf --pedigree /data/trios.ped --region 20 --output /data/serP

# 5. --pedigree en la inferencia cambia el método (prohibido en el benchmark)
s5 SHAPEIT5_phase_common --input /data/unphased.bcf --region 20 --filter-maf 0.05 --seed 42 --pedigree /data/trios.ped --output /data/common_ped.bcf
need common_ped.bcf; bcf bcftools index -f /data/common_ped.bcf
s5 SHAPEIT5_switch --validation /data/truth.bcf --estimation /data/common_ped.bcf --region 20 --output /data/serPed
s5 SHAPEIT5_switch --validation /data/truth.bcf --estimation /data/common.bcf     --region 20 --output /data/serNoPed

# 6. ligate con y sin solape: sin solape no da error y concatena sin alinear la fase
for r in "chA 20:1-1800000" "chB 20:1200000-3000000" "nA 20:1-1500000" "nB 20:1500001-3000000"; do
  set -- $r
  s5 SHAPEIT5_phase_common --input /data/unphased.bcf --region "$2" --filter-maf 0.05 --seed 42 --output "/data/$1.bcf"
  need "$1.bcf"; bcf bcftools index -f "/data/$1.bcf"
done
printf "/data/chA.bcf\n/data/chB.bcf\n" > "$OUT/list_overlap.txt"
printf "/data/nA.bcf\n/data/nB.bcf\n"   > "$OUT/list_nooverlap.txt"
for t in overlap nooverlap; do
  s5 SHAPEIT5_ligate --input "/data/list_$t.txt" --output "/data/lig_$t.bcf" | tee "$OUT/ligate_$t.log"
  need "lig_$t.bcf"; bcf bcftools index -f "/data/lig_$t.bcf"
  s5 SHAPEIT5_switch --validation /data/truth.bcf --estimation "/data/lig_$t.bcf" --region 20 --output "/data/serLig_$t"
done

echo "C3 completada en $OUT"
