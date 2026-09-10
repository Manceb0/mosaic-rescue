# Parches de herramientas fijadas (GO 2B, remediación adjudicada)

## `scramble_1.0.2_make.vcf.R`

Copia parcheada de `bin/make.vcf.R` de SCRAMble 1.0.2 (imagen
`quay.io/biocontainers/scramble:1.0.2--hec16e2b_0`, digest `sha256:68d1452f…`). SCRAMble es
software de terceros (GeneDx / Torene et al.); este fichero se redistribuye únicamente como parche
de reparación, con su `diff` al lado, bajo los términos de la licencia original de SCRAMble.

Qué cambia, y nada más: una cuarentena de validez de coordenadas **antes** de consultar la base de
referencia, en las dos ramas (MEI y DEL). Una fila cuya coordenada no puede existir en la referencia
no se imputa, no se recorta y no se borra en silencio: se escribe en `<prefix>_rejected_records.txt`
con motivo (`POS_LT_1`, `CONTIG_NOT_IN_REFERENCE`, `POS_GT_CONTIG_LENGTH`), se cuenta en
`<prefix>_rejected_count.txt` (también cuando es cero) y se excluye del VCF. Las filas válidas pasan
intactas. Probado: identidad byte a byte de los registros válidos frente al original, VCF validado
con bcftools 1.21, extremo a extremo con inserción sintética.

Uso en el orquestador: se monta **sólo lectura** sobre `/usr/local/share/scramble/bin/make.vcf.R`;
el digest de la imagen no cambia. Hashes registrados en `src/wgs/remediation_manifest.json`:
original `521b4abb…`, parcheado `c77d2f73…`. La etapa comprueba el hash del fichero antes de montarlo.
