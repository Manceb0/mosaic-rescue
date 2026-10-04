"""EXP-027 · Amendment 8: máscaras de sitio en lugar de exclusión de ventana (sin red ni datos reales)."""
import gzip

import numpy as np

from src.exp027 import evaluate, gates, masks, plan, rho, serialize as S, spikein, stats, windows

LENGTHS = {f"chr{i}": 50_000_000 for i in range(1, 23)}
BUB = windows.BUB1B_WINDOW


def _lists(gaps=()):
    tiles = windows.lattice_tiles(LENGTHS)
    tex = windows.Intervals(gaps)
    order = windows.global_order(tiles, tex)
    lat = windows.evaluation_lattice(order)
    return order, windows.evaluation_windows(lat, tex), windows.calibration_tiles(order)


def _sites(chrom, start, n, step=1_000):
    return [(start + i * step, "A") for i in range(n)]


def _window_sites(keep, no_truth, positions, audit, depth=30):
    """WindowSites con los sitios retenidos; paternal = −1 para los que salen de la verdad."""
    kept = [p for p, _ in positions if p in keep]
    n = len(kept)
    rng = np.random.default_rng(0)
    n_alt = rng.integers(10, 21, n)
    pat = np.array([-1 if p in no_truth else 0 for p in kept])
    return evaluate.WindowSites(depth - n_alt, n_alt, np.zeros(n, int), pat, np.ones(n, bool), audit)


def test_one_bp_segdup_masks_site_not_window():
    order, ev, cal = _lists()
    w = ev[1]
    m = masks.SiteMasks(segdup=[(w[0], w[1] + 5_000, w[1] + 5_000)])
    cands = _sites(w[0], w[1], 60)
    keep, no_truth, audit = masks.window_audit(w[0], cands, m, w)
    assert w in ev and len(ev) == 50                       # la segdup no entra en la lista de ventanas
    assert audit["n_mask_segdup"] == 1 and len(keep) == 59 and not no_truth


def test_bub1b_with_0_61_percent_segdup_stays_and_hmin_decides():
    _, ev, _ = _lists()
    assert ev[0] == BUB
    c, s, _ = BUB
    seg = [(c, s + 100_000 + k * 20_000, s + 100_000 + k * 20_000 + 1_525) for k in range(8)]
    m = masks.SiteMasks(segdup=seg)
    assert abs(masks.covered_fraction(seg, BUB) - 0.0061) < 0.0002
    inside = [(a + 10, "A") for _, a, _ in seg[:5]]              # 5 hets dentro de la segdup
    for n_out, evaluable in ((55, True), (47, False)):
        cands = inside + _sites(c, s + 500_000, n_out)
        keep, no_truth, audit = masks.window_audit(c, cands, m, BUB)
        ws = _window_sites(keep, no_truth, cands, audit)
        ie = evaluate.intact_eval(ws, "K", windows.wid(BUB), b=50)
        assert audit["n_mask_segdup"] == 5 and ws.full_audit()["n_after_intact"] == n_out
        assert ie["evaluable"] is evaluable                        # Hmin = 50 tras la máscara


def test_small_child_del_masks_sites_not_window():
    _, ev, _ = _lists()
    w = ev[2]
    m = masks.SiteMasks(child_cc=[(w[0], w[1] + 10_000, w[1] + 10_300)])
    cands = _sites(w[0], w[1] + 10_000, 70, step=100)            # 4 caen en el DEL
    keep, no_truth, audit = masks.window_audit(w[0], cands, m, w)
    assert audit["n_mask_child_copychange"] == 4 and len(keep) == 66 and w in ev
    assert m.child_cc[0] in [tuple(x) for x in m.phasing_intervals()]


def test_parental_sv_only_affects_truth_power_and_ser():
    _, ev, _ = _lists()
    w = ev[3]
    par = [(w[0], w[1] + 1, w[1] + 30_000)]
    m = masks.SiteMasks(parent_cc=par)
    cands = _sites(w[0], w[1] + 1, 80)                           # 30 caen en el SV parental
    keep, no_truth, audit = masks.window_audit(w[0], cands, m, w)
    assert len(keep) == 80 and len(no_truth) == 30               # APR y ρ los conservan
    assert audit["n_mask_parent_copychange_truth"] == 30
    assert par[0] not in m.phasing_intervals() and par[0] in m.truth_intervals()
    ws = _window_sites(keep, no_truth, cands, audit)
    fa = ws.full_audit()
    assert fa["n_after_intact"] == 80 and fa["n_after_truth"] == 50
    assert evaluate.intact_eval(ws, "K", windows.wid(w), b=50)["evaluable"]


def test_copy_neutral_never_masks_and_copy_changing_rules():
    gt = ["GT"]
    assert not masks.sample_copy_changing("INS", gt, "0/1")
    assert not masks.sample_copy_changing("INS:ME:ALU", gt, "1/1")
    assert not masks.sample_copy_changing("INV", ["GT", "CN"], "0/1:1")
    assert not masks.sample_copy_changing("BND", gt, "0/1")
    assert masks.sample_copy_changing("DEL", gt, "0/1")
    assert masks.sample_copy_changing("DUP:TANDEM", gt, "0/1")
    assert not masks.sample_copy_changing("DEL", gt, "0/0")
    assert masks.sample_copy_changing("CNV", ["GT", "CN"], ".:3")
    assert not masks.sample_copy_changing("CNV", ["GT", "CN"], ".:2")
    assert masks.sample_copy_changing("CPX", ["GT", "RD_CN"], "0/1:1")
    assert not masks.sample_copy_changing("CPX", ["GT", "RD_CN"], "0/1:2")
    assert not masks.sample_copy_changing("CPX", ["GT", "RD_CN"], "0/0:1")


def test_trio_copy_changing_reads_callset(tmp_path):
    vcf = tmp_path / "sv.vcf.gz"
    head = "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tK\tF\tM\tX\n"
    rows = [
        "chr1\t1000\ta\tN\t<INS>\t.\tPASS\tSVTYPE=INS;END=1001\tGT\t0/1\t0/0\t0/0\t0/0\n",
        "chr1\t2000\tb\tN\t<INV>\t.\tPASS\tSVTYPE=INV;END=9000\tGT\t0/1\t0/0\t0/0\t0/0\n",
        "chr1\t3000\tc\tN\t<DEL>\t.\tPASS\tSVTYPE=DEL;END=3300\tGT\t0/1\t0/0\t0/0\t0/0\n",
        "chr1\t5000\td\tN\t<DUP>\t.\tPASS\tSVTYPE=DUP;END=6000\tGT\t0/0\t0/1\t0/0\t0/0\n",
        "chrX\t5000\te\tN\t<DEL>\t.\tPASS\tSVTYPE=DEL;END=6000\tGT\t0/1\t0/0\t0/0\t0/0\n",
    ]
    vcf.write_bytes(gzip.compress(("##fileformat=VCFv4.2\n" + head + "".join(rows)).encode()))
    out, st = plan.trio_copy_changing(vcf, [{"child": "K", "father": "F", "mother": "M"}])
    assert out["K"]["child_cc"] == [("chr1", 3000, 3300)]        # INS/INV no; chrX no
    assert out["K"]["parent_cc"] == [("chr1", 5000, 6000)]


def test_calibration_tiles_are_global_and_common():
    order, ev, cal = _lists()
    assert cal == order[49:69] and not set(cal) & set(ev)
    # ninguna máscara de hijo entra en la selección: misma lista para cualquier hijo
    assert windows.calibration_tiles(order) == cal


def test_patient_cnv_still_makes_a1_not_evaluable():
    c, s, e = BUB
    cnv = [(c, e, e + 50_000)]                                  # 1 pb de solape
    assert masks.patient_window_blocked(cnv, BUB)
    assert stats.a1_class(p=0.001, effect=0.30, n_hets=500, cnv_overlap=True) == stats.NOT_EVALUABLE
    assert not masks.patient_window_blocked([(c, e + 1, e + 9)], BUB)


def test_seeds_and_gates_unchanged():
    """Valores de referencia calculados con el código del tag exp027-prebenchmark-freeze."""
    w = "chr1:1-2000000"
    assert S.child_order_key("HG00096").startswith("1a2169f4c23ac4c1")
    assert S.tile_order_key("chr1", 1).startswith("51b4eaf704ecef31")
    assert S.perm_seed_obs("HG00096", w) == 18027233654295802832
    assert S.perm_seed_spike("HG00096", w, 0.10, 3) == 1521670837342729669
    assert S.draw_seed("HG00096", w, 0.10, 3) == 2855948293961004295
    d = np.linspace(-0.2, 0.25, 60)
    assert stats.phase_randomized_p(d, S.perm_seed_obs("HG00096", w), 1000) == 0.16183816183816183
    k = spikein.paternal_counts(np.full(60, 30), 0.10, 3, np.full(60, 0.01), "HG00096", w)
    assert int(k.sum()) == 735 and k[:5].tolist() == [5, 9, 10, 15, 12]
    assert (stats.B_PERMUTATIONS, stats.ALPHA, stats.DELTA_STAR, stats.H_MIN) == (10_000, 0.05, 0.10, 50)
    assert (gates.APR_P0, gates.APR_ALPHA, gates.SENS_MIN, gates.RETENTION_MIN, gates.SER_MAX,
            gates.STRATUM_SER_MAX, gates.LOCUS_CHILDREN_MIN, gates.LOCUS_STRATA_MIN) == \
        (0.05, 0.05, 0.80, 0.90, 0.02, 0.04, 15, 4)
    assert [gates.sentinel_critical_count(n) for n in (15, 16, 17, 20)] == [3, 3, 4, 4]
    assert rho.MIN_HETS == 200 and S.DELTA_GRID == (0.00, 0.02, 0.05, 0.10, 0.15, 0.20)
