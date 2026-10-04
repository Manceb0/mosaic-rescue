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


def _fake_docker(info_ok: bool, inspect_rc: int, inspect_out: str = ""):
    def run(args, **kwargs):
        if args[1] == "info":
            return _Proc(0, "29.0.0") if info_ok else _Proc(1)
        return _Proc(inspect_rc, inspect_out)
    return run


def test_check_image_distinguishes_daemon_missing_and_digest(monkeypatch):
    ref = tools.BCFTOOLS_IMAGE
    monkeypatch.setattr(subprocess, "run", _fake_docker(False, 0))
    with pytest.raises(orchestrate.OrchestrationError, match="daemon de Docker"):
        orchestrate.check_image(ref)                               # Docker apagado: no es "falta imagen"
    monkeypatch.setattr(subprocess, "run", _fake_docker(True, 1))
    with pytest.raises(orchestrate.OrchestrationError, match="no disponible"):
        orchestrate.check_image(ref)
    monkeypatch.setattr(subprocess, "run", _fake_docker(True, 0, '["quay.io/biocontainers/bcftools@sha256:otro"]'))
    with pytest.raises(orchestrate.OrchestrationError, match="digest"):
        orchestrate.check_image(ref)
    monkeypatch.setattr(subprocess, "run", _fake_docker(True, 0, f'["{ref}"]'))
    orchestrate.check_image(ref)                                   # coincide: no lanza


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
    # Amendment 8: máscaras de sitio en todos los caminos, sin quitar la ventana
    au = rep["toy"]["audit"]
    assert all(a["n_mask_segdup"] > 0 and a["n_mask_blacklist"] > 0 for a in au.values())
    assert au["C0"]["n_mask_child_copychange"] > 0 and au["C1"]["n_mask_child_copychange"] == 0
    assert au["C1"]["n_mask_parent_copychange_truth"] > 0 and au["C0"]["n_mask_parent_copychange_truth"] == 0
    for c, a in au.items():
        assert a["n_after_intact"] <= a["n_before"] - a["n_mask_segdup"] - a["n_mask_blacklist"] - a["n_mask_child_copychange"]
        assert a["n_after_truth"] <= a["n_after_intact"]
        assert 0 < a["masked_bp_fraction_intact"] < 0.2               # descriptiva, no puerta
