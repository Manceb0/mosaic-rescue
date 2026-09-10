# Entornos derivados para xTea 0.1.9 (GO 2B, remediación adjudicada)

La imagen fijada `quay.io/biocontainers/xtea:0.1.9--hdfd78af_0` no puede ejecutar xTea: importa
`deepforest` incondicionalmente y no lo trae, y su `sort` es BusyBox, sin el tipo de orden `V` que
`x_gvcf.py` necesita. Dos imágenes derivadas, construidas desde el digest original, con el código de
xTea y el modelo DF21 byte a byte iguales:

| Candidato | Cambio | ImageID |
|---|---|---|
| A | `scikit-learn 1.0.1` (= `_sklearn_version` embebido en el modelo DF21), `deep-forest 0.1.6`, `joblib 1.1.0`, `threadpoolctl 3.1.0` | `sha256:8e10fb98…` |
| A' | único cambio que afecta al runtime científico: GNU `sort` 8.30 de Debian buster `coreutils 8.30-3` en `/usr/local/bin`, cero bibliotecas extranjeras; además ficheros de evidencia (`SHA256SUMS`, `pip freeze`) | `sha256:42da6df7…` |

`xtea_candA/Dockerfile` y `xtea_candA_prime/Dockerfile` reconstruyen ambas. Las ruedas de Python
se descargan y hashean durante la construcción. El `.deb` de coreutils y el binario `sort`
extraído (hashes en `gnu_sort/SHA256SUMS`) son artefactos que viven en `work/resources/` y en la
evidencia del STOP; el Dockerfile de A' los copia desde `gnu_sort/` del contexto de construcción.

El orquestador **no confía en la etiqueta**: antes de ejecutar la etapa 5b comprueba que el ImageID
completo de A' coincide con `src/wgs/remediation_manifest.json` y ejecuta el contenedor por ese ID.
