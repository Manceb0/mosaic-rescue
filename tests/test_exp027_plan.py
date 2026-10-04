"""EXP-027 · materialización y plan: integridad de descargas e índices (sin red ni datos reales)."""
import gzip
import struct

import pytest

from src.exp027 import materialize, plan


def test_integrity_detects_injected_server_error(tmp_path):
    good = tmp_path / "ok.fa"
    good.write_bytes(b">chr1\nACGT\n")
    assert materialize.integrity({"key": "ok", "path": "ok.fa"}, tmp_path) == "no_injected_error"
    bad = tmp_path / "bad.fa"
    bad.write_bytes(b">chr1\nACGT<Error><Code>ConnectionClosedException</Code></Error>ACGT\n")
    with pytest.raises(RuntimeError, match="inyectado"):
        materialize.integrity({"key": "bad", "path": "bad.fa"}, tmp_path)


def test_integrity_detects_truncated_gzip(tmp_path):
    p = tmp_path / "x.gz"
    p.write_bytes(gzip.compress(b"a\tb\n" * 1000)[:-6])
    with pytest.raises(Exception):
        materialize.integrity({"key": "x", "path": "x.gz"}, tmp_path)


def test_reference_md5_is_uppercase_without_newlines(tmp_path):
    fa = tmp_path / "r.fa"
    fa.write_bytes(b">chr1 desc\nacgt\nNN\n>chr2\nAC\n")
    import hashlib
    got = plan.reference_md5(fa, wanted=("chr1", "chr2"))
    assert got == {"chr1": hashlib.md5(b"ACGTNN").hexdigest(), "chr2": hashlib.md5(b"AC").hexdigest()}


def test_carries_reads_gt_only():
    assert plan._carries("0/1:30") and plan._carries("1|0") and plan._carries("1/1")
    assert not plan._carries("0/0:99") and not plan._carries("./.") and not plan._carries(".")


def test_crai_region_bytes_counts_each_container_once(tmp_path):
    rows = ["0\t1\t1000\t100\t10\t50", "0\t1001\t1000\t100\t60\t50",   # mismo contenedor
            "0\t2001\t1000\t500\t10\t50", "1\t1\t1000\t900\t10\t50"]
    p = tmp_path / "x.crai"
    p.write_bytes(gzip.compress(("\n".join(rows) + "\n").encode()))
    crai = plan.read_crai(p)
    assert plan.crai_region_bytes(crai, 0, 1, 1500, 1200) == 400          # 100..500
    assert plan.crai_region_bytes(crai, 0, 1, 2500, 1200) == 800          # + 500..900
    assert plan.crai_region_bytes(crai, 1, 1, 10, 1200) == 300            # 900..fin


def _tbi(name: str, bins: dict, ioff: list) -> bytes:
    nm = name.encode() + b"\x00"
    out = b"TBI\x01" + struct.pack("<8i", 1, 2, 1, 2, 0, ord("#"), 0, len(nm)) + nm
    out += struct.pack("<i", len(bins))
    for b, chunks in bins.items():
        out += struct.pack("<Ii", b, len(chunks))
        for cb, ce in chunks:
            out += struct.pack("<QQ", cb, ce)
    out += struct.pack("<i", len(ioff)) + struct.pack(f"<{len(ioff)}Q", *ioff)
    return gzip.compress(out)


def test_tbi_region_bytes_spans_overlapping_chunks(tmp_path):
    leaf = 4681                                     # bin de 16 kb que contiene la posición 1
    p = tmp_path / "x.tbi"
    p.write_bytes(_tbi("chr1", {leaf: [(1000 << 16, 5000 << 16)], leaf + 1: [(5000 << 16, 9000 << 16)]},
                       [1000 << 16, 5000 << 16]))
    refs = plan.read_tbi(p)
    assert plan.tbi_region_bytes(refs, "chr1", 1, 100) == 4000 + plan.BGZF_MAX_BLOCK
    assert plan.tbi_region_bytes(refs, "chr1", 1, 20_000) == 8000 + plan.BGZF_MAX_BLOCK
