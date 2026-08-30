#!/usr/bin/env bash
# Descarga el cache de VEP para GRCh38 con la MISMA version que la imagen,
# usando el instalador que trae dentro. Asi no hay desajuste entre binario y
# cache, que es el fallo mas comun al montar VEP a mano.
#
# El cache vive en work/vep_cache (ignorado por Git). Ocupa del orden de 20-25 GB
# y solo se descarga una vez.
#
# Uso:  bash src/setup_vep_cache.sh [tag_de_imagen]
set -euo pipefail

IMG="${1:-ensemblorg/ensembl-vep:latest}"
WORK="$(pwd)/work"
CACHE="$WORK/vep_cache"
mkdir -p "$CACHE"

echo "==> descargando imagen: $IMG"
docker pull "$IMG"

echo
echo "==> version de VEP dentro de la imagen"
VEP_VER="$(MSYS_NO_PATHCONV=1 docker run --rm "$IMG" vep 2>&1 | grep -iE 'ensembl-vep|versions' -A3 | head -8 || true)"
echo "$VEP_VER"

echo
echo "==> instalando cache de GRCh38 (20-25 GB — esto tarda)"
echo "    destino: $CACHE"
# -a cf : solo cache + FASTA. No instala APIs ni plugins en esta pasada.
# -y    : ensamblado. --NO_UPDATE evita que intente actualizarse solo.
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "${CACHE}:/cache" \
  "$IMG" \
  INSTALL.pl \
    --AUTO cf \
    --SPECIES homo_sapiens \
    --ASSEMBLY GRCh38 \
    --CACHEDIR /cache \
    --NO_UPDATE \
    --NO_BIOPERL

echo
echo "==> contenido del cache"
du -sh "$CACHE" 2>/dev/null || true
ls -1 "$CACHE/homo_sapiens" 2>/dev/null || echo "    (revisar: no se creo homo_sapiens/)"

cat > "$WORK/vep_cache_provenance.txt" <<EOF
CACHE DE VEP
============
fecha (UTC)   : $(date -u +%Y-%m-%dT%H:%M:%SZ)
imagen        : ${IMG}
digest        : $(docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null || echo 'no disponible')
ensamblado    : GRCh38
especie       : homo_sapiens
instalado con : INSTALL.pl --AUTO cf (cache + FASTA)
destino       : work/vep_cache
version cache : $(ls -1 "$CACHE/homo_sapiens" 2>/dev/null | tr '\n' ' ')
EOF
echo
echo "==> procedencia escrita en work/vep_cache_provenance.txt"
