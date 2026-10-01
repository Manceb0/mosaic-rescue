"""EXP-027 · El generador sintético de C3 es determinista y tiene la forma declarada."""
import hashlib

from src.exp027 import c3_synth


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_generator_is_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    assert c3_synth.main(["--out", str(a)]) == 0
    assert c3_synth.main(["--out", str(b)]) == 0
    for name in ("truth.vcf", "unphased.vcf", "trios.ped"):
        assert _sha(a / name) == _sha(b / name)


def test_shape_matches_declaration(tmp_path):
    c3_synth.main(["--out", str(tmp_path)])
    header = [l for l in (tmp_path / "truth.vcf").read_text().splitlines() if l.startswith("#CHROM")][0]
    assert len(header.split("\t")) - 9 == c3_synth.N_UNRELATED + 3 * c3_synth.N_TRIOS
    ped = (tmp_path / "trios.ped").read_text().splitlines()
    assert len(ped) == c3_synth.N_TRIOS
    unphased = [l for l in (tmp_path / "unphased.vcf").read_text().splitlines() if not l.startswith("#")]
    assert all("|" not in l.split("\t", 9)[9] for l in unphased)
