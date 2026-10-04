"""EXP-027 · ejecutor probado solo con sintéticos de juguete (sin 1000G, sin datos del paciente).

Cada bloque comprueba una regla congelada de docs/DECISIONS.md § EXP-027.
"""
import hashlib

import numpy as np
import pytest

from src.exp027 import evaluate, gates, rho, selection, serialize, spikein, stats, tools, truth, windows


# --- serialización (decisiones confirmadas) --------------------------------------------------
def _h(s):
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def test_serialization_is_literal():
    assert serialize.child_order_key("NA12878") == _h("42:NA12878")
    assert serialize.tile_order_key("chr15", 1) == _h("42:chr15:1")
    assert serialize.window_id("chr1", 1, 2000000) == "chr1:1-2000000"
    assert [serialize.delta_fmt(d) for d in serialize.DELTA_GRID] == ["0.00", "0.02", "0.05", "0.10", "0.15", "0.20"]
    wid = serialize.window_id(*windows.BUB1B_WINDOW)
    assert serialize.draw_seed("HG00096", wid, 0.10, 7) == int(_h(f"42:draw:HG00096:{wid}:0.10:7")[:16], 16)
    assert serialize.perm_seed_obs("HG00096", wid) == int(_h(f"42:perm:OBS:HG00096:{wid}")[:16], 16)
    assert serialize.perm_seed_spike("HG00096", wid, 0.00, 0) == int(_h(f"42:perm:SPIKE:HG00096:{wid}:0.00:0")[:16], 16)
    assert serialize.perm_seed_obs("HG00096", wid) != serialize.perm_seed_spike("HG00096", wid, 0.00, 0)
    with pytest.raises(ValueError):
        serialize.tile_order_key("15", 1)          # chr debe ser "chrN"
    with pytest.raises(ValueError):
        serialize.delta_fmt(0.07)                  # fuera de la rejilla


def test_sign_is_exactly_half_and_half():
    for r in (2, 100):
        signs = [serialize.rep_sign(k) for k in range(r)]
        assert signs.count(1) == signs.count(-1) == r // 2
        assert all(s == (1 if k % 2 == 0 else -1) for k, s in enumerate(signs))


# --- selección y cohorte -------------------------------------------------------------------------
def _trios(n_per=6):
    out = []
    for sp in selection.SUPERPOPULATIONS:
        for i in range(n_per):
            out.append({"child": f"{sp}c{i}", "father": f"{sp}f{i}", "mother": f"{sp}m{i}",
                        "superpop": sp, "complete": True, "parents_sequenced": True})
    return out


def test_offspring_selection_by_hash_and_short_stratum():
    trios = _trios()
    trios = [t for t in trios if not (t["superpop"] == "SAS" and t["child"] != "SASc0")]
    trios.append({"child": "X", "father": "a", "mother": "b", "superpop": "AFR",
                  "complete": False, "parents_sequenced": True})
    chosen, short = selection.select_offspring(trios)
    assert short == ["SAS"] and len(chosen["SAS"]) == 1
    for sp in ("AFR", "AMR", "EAS", "EUR"):
        ids = [t["child"] for t in chosen[sp]]
        assert len(ids) == 4 and "X" not in ids
        assert ids == sorted(ids, key=serialize.child_order_key)


def test_conditioning_cohort_excludes_target_and_first_degree():
    ped = [("kid", "dad", "mom"), ("sib", "dad", "mom"), ("other", "o1", "o2")]
    phase3 = ["kid", "dad", "mom", "sib", "other", "o1", "unrelated"]
    c = selection.conditioning_cohort(phase3, "kid", ped)
    assert set(c) == {"other", "o1", "unrelated"}
    assert selection.conditioning_cohort(phase3, None, ped) == phase3     # paciente: completa


# --- ventanas ------------------------------------------------------------------------------------
LENGTHS = {f"chr{i}": 50_000_000 for i in range(1, 23)}


def test_lattice_and_overlap_conventions():
    tiles = windows.lattice_tiles(LENGTHS)
    assert tiles[0] == ("chr1", 1, 2_000_000) and len(tiles) == 22 * 25
    iv = windows.Intervals.from_bed_lines(["chr1\t1999999\t2000000\n"])    # BED: base 1 = 2000000
    assert iv.hits("chr1", 1, 2_000_000) and not iv.hits("chr1", 2_000_001, 4_000_000)


def test_global_list_and_common_calibration_amendment8():
    """Amendment 8: solo gaps/centrómeros quitan tiles; ventanas y calibración comunes a todos."""
    tiles = windows.lattice_tiles(LENGTHS)
    gaps = windows.Intervals([("chr2", 1, 10)])
    order = windows.global_order(tiles, gaps)
    assert all(not (t[0] == "chr15" and windows.overlaps(t[1], t[2], 39_191_079, 41_191_078)) for t in order)
    assert ("chr2", 1, 2_000_000) not in order
    lat = windows.evaluation_lattice(order)
    ev = windows.evaluation_windows(lat, gaps)
    assert ev[0] == windows.BUB1B_WINDOW and len(ev) == 50
    cal = windows.calibration_tiles(order)
    assert cal == order[49:69] and not set(cal) & set(lat)
    gap_on_bub1b = windows.Intervals([("chr15", 40_000_000, 40_000_000)])
    assert windows.BUB1B_WINDOW not in windows.evaluation_windows(lat, gap_on_bub1b)


# --- verdad mendeliana ---------------------------------------------------------------------------
@pytest.mark.parametrize("child,father,mother,expected", [
    ((0, 1), (0, 0), (1, 1), 0),
    ((0, 1), (1, 1), (0, 1), 1),
    ((0, 1), (0, 1), (0, 0), 1),
    ((0, 1), (0, 1), (0, 1), None),     # ambos heterocigotos: ambiguo
    ((0, 1), (0, 0), (0, 0), None),     # inconsistencia / de novo
    ((0, 0), (0, 0), (1, 1), None),     # el hijo no es het
])
def test_paternal_allele(child, father, mother, expected):
    assert truth.paternal_allele(child, father, mother) == expected


# --- estadístico y A1 ------------------------------------------------------------------------------
def test_t_statistic_formula():
    d, n = np.array([0.1, 0.2, -0.05]), np.array([20, 40, 25])
    assert stats.t_statistic(d, n) == pytest.approx(d.sum() / np.sqrt((0.25 / n).sum()))


def test_effect_is_abs_mean_not_mean_abs():
    d = np.array([0.2, -0.2, 0.2, -0.2])
    assert stats.a1_effect(d) == 0.0 and np.mean(np.abs(d)) == pytest.approx(0.2)


def test_phase_randomized_p_extremes():
    strong = np.full(100, 0.1)
    assert stats.phase_randomized_p(strong, seed=1, b=500) == pytest.approx(1 / 501)
    rng = np.random.default_rng(3)
    ps = [stats.phase_randomized_p(rng.choice([-0.05, 0.05], 80), seed=s, b=200) for s in range(300)]
    assert 0.01 < np.mean(np.array(ps) < 0.05) < 0.11       # calibración aproximada bajo H0


def test_a1_class_precedence():
    assert stats.a1_class(0.20, 0.30, 100, False) == stats.NO_EVIDENCE
    assert stats.a1_class(0.01, 0.05, 100, False) == stats.SUGGESTIVE
    assert stats.a1_class(0.01, 0.10, 100, False) == stats.CONSISTENT
    assert stats.a1_class(0.01, 0.30, 100, True) == stats.NOT_EVALUABLE   # CNV en la ventana
    assert stats.a1_class(0.01, 0.30, 49, False) == stats.NOT_EVALUABLE   # < Hmin


# --- spike-in y ρ ----------------------------------------------------------------------------------
def test_spikein_keeps_depth_and_is_deterministic():
    n = np.full(4000, 40)
    k1 = spikein.paternal_counts(n, 0.10, 0, 0.0, "c", "chr1:1-2000000")
    k2 = spikein.paternal_counts(n, 0.10, 0, 0.0, "c", "chr1:1-2000000")
    assert np.array_equal(k1, k2) and (k1 <= n).all() and (k1 >= 0).all()
    assert k1.mean() / 40 == pytest.approx(0.60, abs=0.01)                 # rep par: +δ
    km = spikein.paternal_counts(n, 0.10, 1, 0.0, "c", "chr1:1-2000000")
    assert km.mean() / 40 == pytest.approx(0.40, abs=0.01)                 # rep impar: −δ
    h1 = spikein.oriented_h1_counts(np.array([40, 40]), np.array([30, 30]), np.array([1, 1]), np.array([1, 0]))
    assert list(h1) == [30, 10]


def test_rho_estimator_recovers_truth():
    rng = np.random.default_rng(5)
    true_rho, n = 0.03, rng.integers(25, 60, 20_000)
    a = 0.5 * (1 - true_rho) / true_rho
    k = rng.binomial(n, rng.beta(a, a, n.size))
    assert rho.rho_hat(k / n, n) == pytest.approx(true_rho, abs=0.006)
    assert rho.rho_hat(np.full(10, 0.5), np.full(10, 30)) == 0.0             # recorte a 0


def test_rho_fallback_hierarchy():
    rng = np.random.default_rng(6)
    big = (rng.uniform(0.3, 0.7, 300), np.full(300, 25))                     # bin [20,30)
    small = (rng.uniform(0.3, 0.7, 50), np.full(50, 25))
    table, src = rho.rho_table({"A": big, "B": small})
    assert src[("A", (20, 30))] == "child_bin" and src[("B", (20, 30))] == "global_bin"
    assert src[("A", (60, None))] == "global_all"


# --- puertas ---------------------------------------------------------------------------------------
def test_apr_calibration_sentinel_thresholds():
    crit = lambda n: next(k for k in range(n + 1) if gates.binomial_upper_tail(k, n, gates.APR_P0) < gates.APR_ALPHA)
    assert [crit(n) for n in (60, 900, 1000)] == [7, 57, 63]
    assert gates.binomial_upper_tail(6, 60) == pytest.approx(0.0787, abs=1e-4)      # 6/60 no es exceso


def test_sentinel_critical_counts():
    assert [gates.sentinel_critical_count(n) for n in range(15, 21)] == [3, 3, 4, 4, 4, 4]
    assert gates.binomial_upper_tail(3, 17) == pytest.approx(0.050253, abs=1e-6)
    assert not gates.sentinel_veto(3, 17) and gates.sentinel_veto(4, 17)


# --- comandos ----------------------------------------------------------------------------------------
def test_tool_commands_enforce_frozen_rules():
    pc = tools.phase_common_cmd("/data/in.bcf", "chr1:1-2", "/data/map", "/data/out.bcf")
    assert pc[pc.index("--filter-maf") + 1] == "0.001" and pc[pc.index("--seed") + 1] == "42"
    with pytest.raises(ValueError):
        tools.phase_common_cmd("i", "r", "", "o")                          # sin mapa: prohibido
    with pytest.raises(ValueError):
        tools.assert_frozen(pc + ["--pedigree", "x"])
    with pytest.raises(ValueError):
        tools.assert_frozen(pc + ["--reference", "x"])
    mp = tools.mpileup_cmd("ref.fa", "sites.tsv", "a.cram", "o.bcf")
    assert "--ff" in mp and mp[mp.index("--ff") + 1] == "UNMAP,SECONDARY,QCFAIL,DUP,SUPPLEMENTARY"
    with pytest.raises(ValueError):
        tools.assert_frozen(mp + ["-x"])
    assert "--log" not in tools.phase_rare_cmd("i", "r", "s", "r", "/data/map", "o")
    tags = tools.cohort_tags_cmd("c.bcf", "t.bcf")
    assert tags[:2] == ["bcftools", "+fill-tags"] and tags[-1] == "AC,AN,MAF"
    ann = tools.annotate_cohort_tags_cmd("joint.bcf", "t.bcf", "o.bcf")
    assert ann[ann.index("-c") + 1] == "INFO/AC,INFO/AN,INFO/MAF"
    assert "INFO/MAF>=0.01" in tools.analytic_subset_cmd("i", "o")


def test_ligate_overlap_and_outputs(tmp_path):
    tools.require_ligate_overlap("Buf 0 [20:1-2] [L_isec=221 / L_tot=221]", 2)
    with pytest.raises(RuntimeError):
        tools.require_ligate_overlap("Ligating chunks\n * #samples = 100", 2)  # sin solape
    with pytest.raises(RuntimeError):
        tools.require_output(tmp_path / "missing.bcf")
    assert tools.parse_switch_sample(["C0 3 317 0.95"]) == {"C0": pytest.approx(0.0095)}


# --- extremo a extremo con sintéticos ------------------------------------------------------------------
def _window(rng, n_hets, scramble, resolvable_frac=1.0):
    n = rng.integers(30, 50, n_hets)
    pat = rng.integers(0, 2, n_hets)
    k = rng.binomial(n, 0.5)                                     # datos intactos: sin desequilibrio
    n_alt = np.where(pat == 1, k, n - k)
    h1 = pat.copy() if not scramble else rng.integers(0, 2, n_hets)
    truth_pat = np.where(rng.random(n_hets) < resolvable_frac, pat, -1)
    return evaluate.WindowSites(n - n_alt, n_alt, h1, truth_pat, np.ones(n_hets, bool))


def _children(scramble):
    rng = np.random.default_rng(11)
    kids = {}
    for sp in selection.SUPERPOPULATIONS:
        for i in range(4):
            c = f"{sp}{i}"
            wins = {serialize.window_id(*windows.BUB1B_WINDOW): (_window(rng, 120, scramble), True),
                    "chr1:1-2000000": (_window(rng, 120, scramble), False),
                    "chr2:1-2000000": (_window(rng, 120, scramble), False)}
            calib = (rng.uniform(0.35, 0.65, 400), rng.integers(30, 50, 400))
            kids[c] = {"superpop": sp, "ser": 0.005, "calibration": calib, "windows": wins}
    return kids


def test_end_to_end_perfect_phase_retains_power():
    out = evaluate.run_benchmark(_children(scramble=False), b=200, deltas_grid=(0.00, 0.10))
    r = out["report"]
    assert r["retention"] == pytest.approx(1.0) and r["sensitivity_inferred"] >= 0.80
    L = r["locus_bub1b"]
    assert L["evaluable_children"] == 20 and L["evaluable_strata"] == 5
    assert L["evaluable_by_superpop"] == {sp: 4 for sp in selection.SUPERPOPULATIONS}
    assert r["apr_n"] == 60 and r["apr_p_binom_one_sided"] >= gates.APR_ALPHA
    assert r["phase1_global"] == "PASS" and r["a1_applicable"] is True


def test_end_to_end_scrambled_phase_fails_retention():
    out = evaluate.run_benchmark(_children(scramble=True), b=200, deltas_grid=(0.00, 0.10))
    r = out["report"]
    assert r["retention"] < 0.90 and r["phase1_global"] == "FAIL"
    assert "global:retention" in r["fail_reasons"] and r["a1_applicable"] is False


def test_power_uses_only_mendelian_resolvable_hets():
    rng = np.random.default_rng(2)
    s = _window(rng, 120, scramble=False, resolvable_frac=0.5)
    pe = evaluate.power_eval(s, "c", "chr1:1-2000000", False, lambda n: 0.0, (0.10,), b=50)
    ie = evaluate.intact_eval(s, "c", "chr1:1-2000000", b=50)
    assert ie["n_hets"] == 120 and pe["n_hets"] == int((s.paternal >= 0).sum())
