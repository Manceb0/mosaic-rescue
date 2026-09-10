# Candidato A · entorno compatible para el modelo DF21 de xTea 0.1.9.
# Politica: MINIMO CAMBIO dictado por el modelo, no por "la version mas nueva".
#   - Base: la imagen historica fijada por digest. xTea 0.1.9 y su codigo quedan byte a byte iguales.
#   - scikit-learn 1.0.1: la version que el propio modelo declara (_sklearn_version en param.pkl).
#   - deep-forest 0.1.6: la primera version sin el pin numpy<1.20 (0.1.5 obligaria a degradar numpy 1.21.6);
#     exige scikit-learn>=1.0 y numpy>=1.14.6, scipy>=1.1.0, joblib>=0.11, ya satisfechos salvo joblib.
#   - joblib y threadpoolctl: dependencias nuevas minimas de scikit-learn>=1.0 y deep-forest; pinadas.
#   - numpy 1.21.6, scipy 1.7.3, pandas 1.3.5, pysam 0.19.1: NO se tocan (--no-deps + --no-index).
# Evidencia que deja dentro de la imagen: pip freeze antes/despues, hashes sha256 de las ruedas instaladas.
FROM quay.io/biocontainers/xtea@sha256:0855c844a4e6298aacbbdef1d538507c33ab1683215b22b2b20aa0077af9bd42

RUN pip freeze > /opt/pip_freeze_base.txt && mkdir -p /opt/wheels
RUN pip download --no-deps --dest /opt/wheels --only-binary=:all: "scikit-learn==1.0.1" "deep-forest==0.1.6" "joblib==1.1.0" "threadpoolctl==3.1.0"
RUN cd /opt/wheels && sha256sum * > SHA256SUMS && cat SHA256SUMS
RUN pip install --no-deps --no-index --find-links /opt/wheels "scikit-learn==1.0.1" "deep-forest==0.1.6" "joblib==1.1.0" "threadpoolctl==3.1.0"
RUN pip freeze > /opt/pip_freeze_candA.txt && python -c "import sklearn, deepforest, joblib, threadpoolctl, numpy, scipy, pandas, pkg_resources as pr; print('sklearn', sklearn.__version__, 'deep-forest', pr.get_distribution('deep-forest').version, 'joblib', joblib.__version__, 'threadpoolctl', threadpoolctl.__version__, 'numpy', numpy.__version__, 'scipy', scipy.__version__, 'pandas', pandas.__version__)"
LABEL org.mosaic_rescue.base_digest="sha256:0855c844a4e6298aacbbdef1d538507c33ab1683215b22b2b20aa0077af9bd42" \
      org.mosaic_rescue.candidate="A" \
      org.mosaic_rescue.policy="minimum change dictated by DF21 model: sklearn 1.0.1 (model _sklearn_version), deep-forest 0.1.6 (first without numpy<1.20 pin)"
