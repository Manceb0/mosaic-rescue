#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lectura FAIL-CLOSED de los artefactos congelados que alimentan las figuras.

Por que existe
    Escribir el sha256 en la ficha QA no protege nada: la ficha la escribe una persona y el
    dibujo lo hace el codigo. Si el JSON de origen cambia, la figura sale distinta y la ficha
    sigue diciendo el hash viejo. Aqui el hash se comprueba ANTES de dibujar, contra
    work/callers/final/MANIFEST.json, y si no coincide el renderer no dibuja: levanta y para.

Contrato
    load_frozen(nombre) -> (objeto, sha256)   para .json
    frozen_path(nombre) -> (ruta, sha256)     para cualquier otro fichero
    Cualquier discrepancia, ausencia del fichero o ausencia de su entrada en el MANIFEST
    termina en FrozenArtifactError. No hay modo permisivo, ni variable de entorno que lo apague.
"""
from __future__ import annotations
import hashlib, io, json, os

FINAL_DIR = os.path.join("work", "callers", "final")
MANIFEST = "MANIFEST.json"


class FrozenArtifactError(RuntimeError):
    """El artefacto congelado no es el que la figura declara usar. La figura no se dibuja."""


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _expected(final_dir: str, name: str) -> str:
    man_path = os.path.join(final_dir, MANIFEST)
    if not os.path.exists(man_path):
        raise FrozenArtifactError(f"no hay manifest de artefactos congelados en {man_path}")
    man = json.load(io.open(man_path, encoding="utf-8"))
    for entry in man.get("files", []):
        if entry.get("file") == name:
            exp = entry.get("sha256")
            if not exp:
                raise FrozenArtifactError(f"{name}: el manifest no registra sha256")
            return exp
    raise FrozenArtifactError(f"{name}: sin entrada en {man_path}; un artefacto no declarado no se dibuja")


def frozen_path(name: str, final_dir: str | None = None) -> tuple[str, str]:
    """Devuelve (ruta, sha256) tras comprobar el hash contra el manifest. Aborta si no coincide."""
    final_dir = final_dir or FINAL_DIR
    path = os.path.join(final_dir, name)
    if not os.path.exists(path):
        raise FrozenArtifactError(f"{name}: no existe en {final_dir}")
    exp = _expected(final_dir, name)
    got = sha256(path)
    if got != exp:
        raise FrozenArtifactError(
            f"{name}: sha256 {got} != {exp} declarado en el manifest. "
            "El artefacto congelado cambio; la figura NO se dibuja hasta readjudicarlo.")
    return path, got


def load_frozen(name: str, final_dir: str | None = None):
    """Carga un JSON congelado tras verificar su hash. Devuelve (objeto, sha256)."""
    path, got = frozen_path(name, final_dir)
    return json.load(io.open(path, encoding="utf-8")), got
