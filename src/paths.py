#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Acceso unico a las rutas de datos del paciente.

REGLA DURA 2 (CLAUDE.md): el codigo NO contiene rutas absolutas. Todas viven en
`config/paths.yaml`, que esta en `.gitignore`. Este modulo es la unica puerta.

Motivo, concreto: una ruta hardcodeada filtra a la vez el nombre de usuario del
sistema y el identificador de muestra real. Ambos son reidentificantes y ambos
quedan en el historial de git para siempre.
"""
from __future__ import annotations
import io, os, functools

CONFIG = "config/paths.yaml"


@functools.lru_cache(maxsize=1)
def _load() -> dict:
    if not os.path.exists(CONFIG):
        raise FileNotFoundError(
            f"Falta {CONFIG}. Copia config/paths.example.yaml y rellena las rutas "
            "reales. Ese fichero esta en .gitignore y no se commitea nunca.")
    import yaml
    return yaml.safe_load(io.open(CONFIG, encoding="utf-8")) or {}


def get(*keys, default=None):
    """get('patient', 'vcf') -> ruta. Lanza si falta y no hay default."""
    node = _load()
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            if default is not None:
                return default
            raise KeyError(f"{CONFIG}: falta la clave {'.'.join(keys)}")
        node = node[k]
    return node


def patient_vcf() -> str:
    return get("patient", "vcf")
