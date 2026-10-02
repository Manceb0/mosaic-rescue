"""EXP-027 · orquestador: fallos fuertes (sin Docker) y extremo a extremo con Docker (opcional).

La prueba de integración solo corre con EXP027_DOCKER=1, porque necesita las imágenes fijadas por
digest en local y tarda unos minutos. Usa exclusivamente el dataset sintético de juguete.
"""
import os
import subprocess

import pytest

from src.exp027 import orchestrate, tools


def test_write_lines_is_lf(tmp_path):
    p = tmp_path / "x.txt"
    orchestrate.write_lines(p, ["a", "b"])
    assert p.read_bytes() == b"a\nb\n"


class _Proc:
    def __init__(self, rc, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def test_check_image_fails_when_missing_or_digest_differs(monkeypatch):
    ref = tools.BCFTOOLS_IMAGE
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _Proc(1))
    with pytest.raises(orchestrate.OrchestrationError, match="no disponible"):
        orchestrate.check_image(ref)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _Proc(0, '["quay.io/biocontainers/bcftools@sha256:otro"]'))
    with pytest.raises(orchestrate.OrchestrationError, match="digest"):
        orchestrate.check_image(ref)
    name = ref.split("@")[0]
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _Proc(0, f'["{ref}"]'))
    orchestrate.check_image(ref)                                   # coincide: no lanza
    assert name in ref


def test_docker_cmd_refuses_frozen_violations():
    pc = tools.phase_common_cmd("/data/i.bcf", "chr1:1-2", "/data/m.gz", "/data/o.bcf")
    with pytest.raises(ValueError):
        tools.docker_cmd(tools.SHAPEIT5_IMAGE, "/m", pc + ["--pedigree", "/data/p.ped"])
    with pytest.raises(ValueError):
        tools.phase_common_cmd("/data/i.bcf", "chr1:1-2", "", "/data/o.bcf")    # sin mapa


def test_require_samples_detects_mismatch(monkeypatch):
    rn = orchestrate.Runner.__new__(orchestrate.Runner)
    rn.bcf = lambda *a: _Proc(0, "A\nB\n")
    orchestrate.require_samples(rn, "x.bcf", ["B", "A"])
    with pytest.raises(orchestrate.OrchestrationError):
        orchestrate.require_samples(rn, "x.bcf", ["A", "B", "C"])


@pytest.mark.skipif(os.environ.get("EXP027_DOCKER") != "1", reason="requiere Docker e imágenes fijadas (EXP027_DOCKER=1)")
def test_toy_end_to_end_with_docker(tmp_path):
    rep = orchestrate.run_toy(tmp_path / "toy", b=100)
    assert rep["toy"]["children"] == 5 and rep["apr_n"] == 5
    assert all(n >= 50 for n in rep["toy"]["hets_per_child"].values())
    assert rep["ser"] is not None and rep["retention"] is not None
    assert "bub1b:evaluable" in rep["fail_reasons"]            # 5 hijos < 15: el juguete no puede pasar
    assert rep["a1_applicable"] is False
