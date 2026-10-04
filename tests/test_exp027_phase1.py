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
