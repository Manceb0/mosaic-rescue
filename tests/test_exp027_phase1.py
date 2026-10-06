"""EXP-027 · ejecutor real de Phase 1: piezas puras y prueba de juguete con Docker (opcional)."""
import os

import numpy as np
import pytest

from src.exp027 import phase1, tools


def _info(**kw):
    base = {"ref": "A", "alt": "G", "filter": "PASS", "kid": (0, 1), "gq": 99, "fa": (0, 0), "mo": (1, 1), "dup": False}
    base.update(kw)
    return base


def test_analytic_marker_rule():
    maf = {(10, "A", "G"): 0.05, (20, "A", "G"): 0.005, (30, "A", "G"): 0.05, (40, "A", "G"): 0.05,
           (50, "A", "G"): 0.05, (60, "A", "G"): 0.05}
    info = {10: _info(), 20: _info(), 30: _info(filter="LowQual"), 40: _info(gq=20),
            50: _info(kid=(1, 1)), 60: _info(dup=True)}
    assert [p for p in sorted(info) if phase1.analytic(info, maf, p)] == [10]


def test_switch_counts_parse():
    assert tools.parse_switch_counts(["C0 9 228 3.95", "x"]) == {"C0": (9, 228)}


def test_assemble_pools_ser_by_counts_and_calibration():
    ds = phase1.Dataset(mount=None, out="o", trios=[("K", "F", "M")], superpop={"K": "AFR"}, phase3=[],
                        pedigree=[], lengths={}, evaluation=[], calibration=[], reference="r",
                        region_bcf=None, alignment=None, gmap=None, site_masks=None)
    wins = [{"child": "K", "window": "chr1:1-2", "is_bub1b": True, "rows": [[10, 12, 0, 1]],
             "audit": {"n_before": 1}, "ser_analytic": [1, 100], "ser_scaffold": [3, 300]},
            {"child": "K", "window": "chr1:3-4", "is_bub1b": False, "rows": [],
             "audit": {"n_before": 0}, "ser_analytic": [3, 100], "ser_scaffold": [0, 100]}]
    cals = [{"child": "K", "b": [0.5, 0.4], "n": [30, 40]}, {"child": "K", "b": [0.6], "n": [25]}]
    ch = phase1.assemble(ds, wins, cals)["K"]
    assert ch["ser"] == 4 / 200 and ch["ser_scaffold"] == 3 / 400            # recuentos, no media de tasas
    assert np.allclose(ch["calibration"][1], [30, 40, 25])
    sites, is_b = ch["windows"]["chr1:1-2"]
    assert is_b and sites.n_alt.tolist() == [12] and sites.full_audit()["n_after_intact"] == 1
    assert ch["windows"]["chr1:3-4"][0].n_ref.size == 0


@pytest.mark.skipif(os.environ.get("EXP027_DOCKER") != "1", reason="requiere Docker e imágenes fijadas (EXP027_DOCKER=1)")
def test_phase1_runner_on_toy_with_docker(tmp_path):
    ds = phase1.Dataset.toy(tmp_path / "toy")
    rep = phase1.run(ds, workers=4, b=100, deltas=(0.00, 0.10), log=lambda *_: None)
    assert rep["run"]["children"] == 5 and rep["apr_n"] == 5
    assert set(rep["ser_counts"]) == {"C0", "C1", "C2", "C3", "C4"}
    au = {c: next(iter(w.values())) for c, w in rep["audit"].items()}
    assert au["C0"]["n_mask_child_copychange"] > 0 and au["C1"]["n_mask_parent_copychange_truth"] > 0
    assert all(a["n_after_truth"] <= a["n_after_intact"] for a in au.values())
    assert "bub1b:evaluable" in rep["fail_reasons"]                  # 5 hijos < 15
    assert not list((tmp_path / "toy" / "phase1").rglob("*.bcf"))   # intermedios grandes borrados


def test_run_manifest_refuses_when_head_is_not_execution_tag(monkeypatch, tmp_path):
    calls = {"rev-parse HEAD": "a" * 40, f"rev-parse {phase1.EXECUTION_TAG}^{{commit}}": "b" * 40}
    monkeypatch.setattr(phase1, "_git", lambda *a: calls[" ".join(a)])
    with pytest.raises(phase1.OrchestrationError, match="no es el tag"):
        phase1.run_manifest(None, tmp_path, tmp_path, 16, 10_000)


def test_run_manifest_refuses_dirty_tree(monkeypatch, tmp_path):
    calls = {"rev-parse HEAD": "a" * 40, f"rev-parse {phase1.EXECUTION_TAG}^{{commit}}": "a" * 40,
             "status --porcelain -- src config tests": " M src/exp027/stats.py"}
    monkeypatch.setattr(phase1, "_git", lambda *a: calls[" ".join(a)])
    with pytest.raises(phase1.OrchestrationError, match="sin commitear"):
        phase1.run_manifest(None, tmp_path, tmp_path, 16, 10_000)


def test_run_fails_fast_and_leaves_a_trace(monkeypatch, tmp_path):
    """La primera excepción detiene el run: FAILED_JOB.json, status FAILED, línea FALLO en progress.log
    y los trabajos pendientes no se ejecutan (EXEC-DEF-PH1-001: nada falla en silencio)."""
    import json as _json
    import threading as _th
    ran = []
    gate = _th.Event()

    def fake_window_job(ds, trio, window, keep_intermediates=False):
        ran.append(window)
        if window[1] == 2:
            raise phase1.OrchestrationError("salida ausente o vacía: phased.bcf")
        gate.wait(0.05)
        return {"child": trio[0], "window": "w", "is_bub1b": False, "rows": [], "audit": {},
                "ser_analytic": [0, 1], "ser_scaffold": [0, 1]}

    monkeypatch.setattr(phase1, "window_job", fake_window_job)
    monkeypatch.setattr(phase1, "check_image", lambda ref: None)
    monkeypatch.setattr(phase1, "kill_run_containers", lambda: 0)
    wins = [("chr1", i, i + 1) for i in range(1, 60)]
    ds = phase1.Dataset(mount=tmp_path, out="run", trios=[("K", "F", "M")], superpop={"K": "AFR"}, phase3=[],
                        pedigree=[], lengths={}, evaluation=wins, calibration=[], reference="r",
                        region_bcf=None, alignment=None, gmap=None, site_masks=None)
    with pytest.raises(phase1.JobFailed):
        phase1.run(ds, workers=1, b=10)
    out = tmp_path / "run"
    failed = _json.loads((out / "FAILED_JOB.json").read_text(encoding="utf-8"))
    assert failed["child"] == "K" and "phased.bcf" in failed["error"] and failed["traceback"]
    assert _json.loads((out / "status.json").read_text(encoding="utf-8"))["state"] == "FAILED"
    assert "FALLO" in (out / "progress.log").read_text(encoding="utf-8")
    assert len(ran) < len(wins)                                       # lo pendiente se cancela


def test_logged_runner_records_every_command(monkeypatch, tmp_path):
    import json as _json

    class P:
        returncode, stdout, stderr = 3, "", "Assertion failed"

    monkeypatch.setattr(phase1.subprocess, "run", lambda *a, **k: P())
    rn = phase1.LoggedRunner(tmp_path, "job")
    rn.run(phase1.tools.BCFTOOLS_IMAGE, ["bcftools", "index", "/data/x.bcf"])
    entry = _json.loads((tmp_path / "job" / "job.log").read_text(encoding="utf-8").splitlines()[0])
    assert entry["returncode"] == 3 and "Assertion" in entry["stderr_tail"] and entry["cmd"][0] == "bcftools"


def test_kill_only_touches_this_runs_labelled_containers(monkeypatch):
    calls = []

    class P:
        def __init__(self, out=""):
            self.stdout, self.returncode = out, 0

    def fake_run(args, **kw):
        calls.append(args)
        return P("abc123\n") if args[1] == "ps" else P()

    monkeypatch.setattr(phase1.subprocess, "run", fake_run)
    assert phase1.kill_run_containers() == 1
    assert calls[0] == ["docker", "ps", "-q", "--filter", f"label=exp027_run={phase1.RUN_LABEL}"]
    assert calls[1] == ["docker", "kill", "abc123"]                   # solo los ids filtrados
    assert phase1.RUN_LABEL.startswith("exp027-r2-")


def test_write_atomic_replaces_whole_file(tmp_path):
    p = tmp_path / "status.json"
    phase1._write_atomic(p, '{"a": 1}')
    phase1._write_atomic(p, '{"a": 2}')
    assert p.read_text(encoding="utf-8") == '{"a": 2}' and not list(tmp_path.glob(".*.tmp"))


def test_existing_failed_job_is_never_overwritten(monkeypatch, tmp_path):
    def boom(ds, trio, window, keep_intermediates=False):
        raise phase1.OrchestrationError("x")

    monkeypatch.setattr(phase1, "window_job", boom)
    monkeypatch.setattr(phase1, "check_image", lambda ref: None)
    monkeypatch.setattr(phase1, "kill_run_containers", lambda: 0)
    (tmp_path / "run").mkdir()
    (tmp_path / "run" / "FAILED_JOB.json").write_text('{"previo": true}', encoding="utf-8")
    ds = phase1.Dataset(mount=tmp_path, out="run", trios=[("K", "F", "M")], superpop={"K": "AFR"}, phase3=[],
                        pedigree=[], lengths={}, evaluation=[("chr1", 1, 2)], calibration=[], reference="r",
                        region_bcf=None, alignment=None, gmap=None, site_masks=None)
    with pytest.raises(phase1.JobFailed, match="ya existe"):
        phase1.run(ds, workers=1, b=10)
    assert (tmp_path / "run" / "FAILED_JOB.json").read_text(encoding="utf-8") == '{"previo": true}'
