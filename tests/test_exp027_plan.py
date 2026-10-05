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


def _bgzf_block(payload: bytes) -> bytes:
    import zlib
    comp = zlib.compressobj(6, zlib.DEFLATED, -15)
    cdata = comp.compress(payload) + comp.flush()
    bsize = 12 + 6 + len(cdata) + 8
    head = bytes([31, 139, 8, 4, 0, 0, 0, 0, 0, 255]) + struct.pack("<H", 6) + b"BC" + struct.pack("<HH", 2, bsize - 1)
    return head + cdata + struct.pack("<II", zlib.crc32(payload) & 0xFFFFFFFF, len(payload))


def test_scan_bgzf_file_cuts_at_region_end_and_checks_crc(tmp_path):
    from src.exp027 import slices
    blocks = [_bgzf_block(f"linea {i}\n".encode() * 50) for i in range(4)]
    base = 1000
    offs = [base + sum(len(b) for b in blocks[:i]) for i in range(4)]
    p = tmp_path / "r.bgzf"
    p.write_bytes(b"".join(blocks) + blocks[0][:10])               # cola incompleta
    keep, _ = slices.scan_bgzf_file(p, offs[2], True, base)
    assert keep == sum(len(b) for b in blocks[:3])
    keep, _ = slices.scan_bgzf_file(p, offs[2], False, base)
    assert keep == sum(len(b) for b in blocks[:2])
    bad = bytearray(b"".join(blocks))
    bad[len(blocks[0]) - 5] ^= 0xFF                                 # rompe el CRC del bloque 0
    p.write_bytes(bytes(bad))
    with pytest.raises(Exception):
        slices.scan_bgzf_file(p, offs[3], True, base)


def test_container_ranges_merges_adjacent_and_excludes_eof():
    from src.exp027 import slices
    rows = [(0, 1, 1000, 100), (0, 1001, 1000, 200), (0, 5001, 1000, 400), (1, 1, 1000, 600)]
    crai = (rows, [100, 200, 400, 600])
    r = slices.container_ranges(crai, {"chr1": 0, "chr2": 1}, [("chr1", 1, 2000), ("chr2", 1, 10)], 738)
    assert r == [(100, 399), (600, 699)]                              # 738 - 38 de EOF


def test_index_samples_strips_trailing_spaces(tmp_path):
    p = tmp_path / "x.sequence.index"
    p.write_text("##c\n#ENA_FILE_PATH\tMD5SUM\tSAMPLE_NAME\n"
                 "ftp://a/HG1.cram\tm1\tHG1 \nftp://a/HG2.cram\tm2\tHG2\n", encoding="ascii")
    assert set(plan.index_samples(p)) == {"HG1", "HG2"}


def test_curl_range_to_file_retries_injected_error_by_subrange(monkeypatch, tmp_path):
    """Un tramo con el XML de error inyectado se repite; el fichero final sale limpio."""
    from src.exp027 import slices

    class P:
        def __init__(self, rc):
            self.returncode, self.stderr = rc, b""

    body = bytes(range(256)) * 40                       # 10 240 bytes
    calls = {"n": 0}

    def fake_run(cmd, capture_output=True):
        a, b = (int(x) for x in cmd[cmd.index("-r") + 1].split("-"))
        out = __import__("pathlib").Path(cmd[cmd.index("-o") + 1])
        calls["n"] += 1
        chunk = body[a:b + 1]
        if calls["n"] == 2:                             # segundo tramo, primer intento: error inyectado
            chunk = b"<Error><Code>X</Code></Error>" + chunk[29:]
        out.write_bytes(chunk)
        return P(0)

    monkeypatch.setattr(slices, "SUBRANGE", 4096)
    monkeypatch.setattr(slices.time, "sleep", lambda s: None)
    monkeypatch.setattr(slices.subprocess, "run", fake_run)
    dest = tmp_path / "x.part"
    slices.curl_range_to_file("https://h/f", 0, len(body) - 1, dest)
    assert dest.read_bytes() == body and calls["n"] == 4   # 3 tramos + 1 reintento
