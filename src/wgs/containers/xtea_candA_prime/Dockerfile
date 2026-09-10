# Candidato A' = candidato A + GNU coreutils `sort`. Unico cambio que afecta al runtime cientifico: GNU sort;
# los demas ficheros anadidos (SHA256SUMS, pip freeze) son evidencia, no runtime.
#
# Por que: la imagen fijada de xTea trae BusyBox 1.32.1 como coreutils; x_gvcf.py ejecuta
#     sort -k1,1V -k2,2n -o <salida> <entrada>
# y BusyBox no conoce el tipo de orden "V" (rc=2, sin fichero); CMD_RUNNER ignora el codigo de retorno
# y --gVCF muere. Reproducido en L1, Alu y SVA del candidato A.
#
# Politica (lider, 2026-09-10):
#   - padre: el ImageID EXACTO del candidato A;
#   - solo el ejecutable GNU sort; CERO bibliotecas de runtime extranjeras;
#   - si `ldd` muestra un solo "not found", la construccion SE DETIENE;
#   - origen fijado: Debian buster coreutils 8.30-3, .deb sha256 ae6e5cd6… (coincide con el indice Packages
#     de buster), extraido sin red en debian@sha256:bb3dc79f…; el binario `sort` copiado tiene sha256 5c9c5373…
#   - el .deb y el binario se conservan en env/gnu_sort/ con SHA256SUMS para reconstruir exactamente lo mismo.
FROM mosaic-rescue/xtea-env-canda:0.1.9-sk1.0.1-df0.1.6

COPY gnu_sort/sort /usr/local/bin/sort
COPY gnu_sort/SHA256SUMS /opt/gnu_sort_SHA256SUMS

# Gate de construccion: hash exacto del binario, resolucion completa con las bibliotecas PROPIAS de la base,
# precedencia en PATH, version y soporte del tipo de orden V. Cualquier fallo aborta la construccion.
RUN set -e; chmod 0755 /usr/local/bin/sort; \
    got=$(sha256sum /usr/local/bin/sort | cut -d" " -f1); exp=$(grep " \*\?sort$" /opt/gnu_sort_SHA256SUMS | cut -d" " -f1); \
    echo "sort sha256 $got (esperado $exp)"; [ "$got" = "$exp" ] || { echo "GATE: sha256 del binario no coincide"; exit 1; }; \
    ldd /usr/local/bin/sort; nf=$(ldd /usr/local/bin/sort | grep -c "not found" || true); echo "ldd not found = $nf"; [ "$nf" = "0" ] || { echo "GATE: dependencias sin resolver"; exit 1; }; \
    which=$(command -v sort); echo "command -v sort = $which"; [ "$which" = "/usr/local/bin/sort" ] || { echo "GATE: sort no precede en PATH"; exit 1; }; \
    sort --version | head -1; \
    printf "21\t30149986\t1\t2\n21\t100\t1\t2\n" > /tmp/raw.txt; sort -k1,1V -k2,2n -o /tmp/raw.sorted /tmp/raw.txt; cat /tmp/raw.sorted; rm -f /tmp/raw.txt /tmp/raw.sorted; \
    pip freeze > /opt/pip_freeze_candA_prime.txt; diff /opt/pip_freeze_candA.txt /opt/pip_freeze_candA_prime.txt && echo "python deps identicas a A"

LABEL org.mosaic_rescue.candidate="A_prime" \
      org.mosaic_rescue.parent_image_id="sha256:8e10fb9811380ac067678e566ad05b9431b3fd63cd8a293a431fd461da009c8c" \
      org.mosaic_rescue.change_over_A="only change affecting the scientific runtime: GNU coreutils sort 8.30 (Debian buster coreutils 8.30-3, deb sha256 ae6e5cd6e9aaf74d66edded3931a7a6c916625b8b890379189c75574f6856bf4) at /usr/local/bin/sort; evidence files added: /opt/gnu_sort_SHA256SUMS, /opt/pip_freeze_candA_prime.txt" \
      org.mosaic_rescue.foreign_runtime_libraries_added="0"
