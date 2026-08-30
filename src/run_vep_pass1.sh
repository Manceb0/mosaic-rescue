#!/usr/bin/env bash
# Pasada 1 de VEP — capa minima de consecuencia, suficiente para asignar
# variante -> gen -> mecanismo y construir los tres carriles.
#
# GOBERNANZA (CLAUDE.md, Reglas Duras 1 y 2):
#   - --offline --cache : NINGUNA variante del paciente sale de la maquina.
#     Prohibido --database, que consulta los servidores de Ensembl.
#   - El VCF original NO se modifica. Todo derivado va a work/, ignorado por Git.
#   - Se emite un fichero de procedencia junto a cada salida.
#
# NO usar --everything en esta pasada. La anotacion profunda (gnomAD, ClinVar,
# CADD, SpliceAI) es pasada 2 y va solo sobre la shortlist.
#
# Uso:  bash src/run_vep_pass1.sh /ruta/al.vcf.gz
set -euo pipefail

IN="${1:?falta la ruta del VCF de entrada}"
# La imagen se fija tras el setup, para que binario y cache no se desajusten.
# Sobrescribible: VEP_IMG=... bash src/run_vep_pass1.sh entrada.vcf.gz
IMG="${VEP_IMG:-ensemblorg/ensembl-vep:latest}"
WORK="$(pwd)/work"
CACHE="$WORK/vep_cache"
OUT="$WORK/pass1"
mkdir -p "$CACHE" "$OUT"

IN_DIR="$(cd "$(dirname "$IN")" && pwd)"
IN_BASE="$(basename "$IN")"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_BASE="pass1_${STAMP}"

echo "==> hash del VCF de entrada (puede tardar en 301 MB)"
IN_HASH="$(sha256sum "$IN" | cut -d' ' -f1)"

# Campos minimos. Cada uno responde a una pregunta concreta del funnel;
# no se anade nada "por si acaso".
FIELDS="Uploaded_variation,Location,Allele,Gene,SYMBOL,Feature,Feature_type,\
Consequence,IMPACT,BIOTYPE,CANONICAL,MANE_SELECT,EXON,INTRON,HGVSc,HGVSp,\
Protein_position,Amino_acids,Codons,VARIANT_CLASS,DISTANCE,STRAND,FLAGS"

echo "==> VEP pasada 1 (offline, cache local)"
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "${IN_DIR}:/in:ro" \
  -v "${CACHE}:/cache" \
  -v "${OUT}:/out" \
  "$IMG" \
  vep \
    --input_file "/in/${IN_BASE}" \
    --output_file "/out/${OUT_BASE}.tsv" \
    --stats_file  "/out/${OUT_BASE}.html" \
    --dir_cache /cache \
    --species homo_sapiens \
    --assembly GRCh38 \
    --offline \
    --cache \
    --tab \
    --fields "$FIELDS" \
    --symbol --canonical --mane --biotype --hgvs --numbers \
    --variant_class \
    --pick_allele_gene \
    --keep_csq \
    --no_escape \
    --fork 8 \
    --buffer_size 20000 \
    --warning_file "/out/${OUT_BASE}.warnings.txt"

echo "==> hash de la salida"
OUT_HASH="$(sha256sum "${OUT}/${OUT_BASE}.tsv" | cut -d' ' -f1)"
VEP_VER="$(MSYS_NO_PATHCONV=1 docker run --rm "$IMG" vep --help 2>/dev/null | grep -m1 -i 'ensembl-vep' || echo 'no capturada')"
CACHE_VER="$(ls "$CACHE/homo_sapiens" 2>/dev/null | head -1 || echo 'no encontrada')"

cat > "${OUT}/${OUT_BASE}.provenance.txt" <<EOF
PROCEDENCIA — VEP pasada 1
==========================
fecha (UTC)        : ${STAMP}
imagen docker      : ${IMG}
version de VEP     : ${VEP_VER}
version del cache  : ${CACHE_VER}
ensamblado         : GRCh38
modo               : --offline --cache  (sin acceso a red; --database NO usado)

entrada            : ${IN_BASE}
sha256 entrada     : ${IN_HASH}

salida             : ${OUT_BASE}.tsv
sha256 salida      : ${OUT_HASH}

campos             : ${FIELDS}
seleccion          : --pick_allele_gene (una consecuencia por alelo y gen)

NOTA: --everything NO se uso. Anotacion profunda (gnomAD, ClinVar, CADD,
SpliceAI, AlphaGenome) es pasada 2 y va solo sobre la shortlist.
EOF

echo
echo "==> listo"
echo "    salida      : ${OUT}/${OUT_BASE}.tsv"
echo "    procedencia : ${OUT}/${OUT_BASE}.provenance.txt"
