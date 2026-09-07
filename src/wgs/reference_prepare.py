#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dos objetos de referencia, con procedencia separada.

    source_reference_fasta   el FASTA de NCBI tal cual se descargo, byte a byte,
                             con su sha256 y md5 (el md5 se compara con el que
                             publica NCBI).
    runtime_reference_fasta  una COPIA con los identificadores de contig
                             renombrados (chr1 -> 1, chrM -> M, chrEBV -> EBV,
                             chrUn_KN707606v1_decoy -> Un_KN707606v1_decoy) para
                             que coincidan con el VCF del proveedor. Tiene su
                             propio sha256 y md5, su .fai construido aqui, y un
                             manifest con el mapa de cabeceras y dos banderas:

                                 sequence_content_changed = false
                                 header_names_changed     = true

    The NCBI source FASTA is preserved byte-for-byte. A separate runtime FASTA
    changes contig identifiers only; nucleotide sequence is unchanged.

    "Sin cambio de secuencia" no se afirma: se COMPRUEBA con un sha256 por
    contig de la secuencia (sin cabecera, sin saltos de linea) en ambos
    ficheros; el gate 4 lo vuelve a comprobar contra el VCF.

Uso (tras descargar el .fna.gz de NCBI a work/ref/):
    python src/wgs/reference_prepare.py --source work/ref/<fichero>.fna.gz
Salida: work/ref/runtime.fa (+ .fai) y work/align/reference_manifest.json
"""
from __future__ import annotations
import argparse, gzip, hashlib, io, json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

EXPECTED_MD5_NCBI = "a056c57649f3c9964c68aead3849bbf8"
RUNTIME = "work/ref/runtime.fa"
MANIFEST = "work/align/reference_manifest.json"


def hashes(path):
    h1, h2 = hashlib.sha256(), hashlib.md5()
    with io.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h1.update(b); h2.update(b)
    return h1.hexdigest(), h2.hexdigest()


def rename(header_id: str) -> str:
    return header_id[3:] if header_id.startswith("chr") else header_id


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    a = ap.parse_args()
    src_sha, src_md5 = hashes(a.source)
    if src_md5 != EXPECTED_MD5_NCBI:
        raise SystemExit(f"STOP: md5 del FASTA descargado {src_md5} != publicado por NCBI {EXPECTED_MD5_NCBI}")

    os.makedirs(os.path.dirname(RUNTIME), exist_ok=True)
    mapping, fai, per_contig = {}, [], {}
    cur, cur_hash, seq_len, line_bases, line_width, offset = None, None, 0, None, None, 0
    op = gzip.open if a.source.endswith(".gz") else io.open

    def close_contig():
        if cur is not None:
            per_contig[cur] = {"length": seq_len, "seq_sha256": cur_hash.hexdigest()}
            fai.append((cur, seq_len, seq_off, line_bases or 0, line_width or 0))

    with op(a.source, "rb") as fin, io.open(RUNTIME, "wb") as fout:
        for raw in fin:
            if raw.startswith(b">"):
                close_contig()
                old_id = raw[1:].split()[0].decode("ascii")
                cur = rename(old_id); mapping[old_id] = cur
                cur_hash, seq_len, line_bases, line_width = hashlib.sha256(), 0, None, None
                hdr = b">" + cur.encode("ascii") + b"\n"
                fout.write(hdr); offset += len(hdr); seq_off = offset
            else:
                s = raw.rstrip(b"\r\n")
                if line_bases is None and s:
                    line_bases, line_width = len(s), len(s) + 1
                cur_hash.update(s.upper()); seq_len += len(s)
                fout.write(s + b"\n"); offset += len(s) + 1
        close_contig()
    with io.open(RUNTIME + ".fai", "w", encoding="utf-8", newline="\n") as f:
        for name, L, off, lb, lw in fai:
            f.write(f"{name}\t{L}\t{off}\t{lb}\t{lw}\n")
    rt_sha, rt_md5 = hashes(RUNTIME)

    # la secuencia no cambio: mismo sha256 por contig leyendo el runtime de nuevo
    check = {}
    with io.open(RUNTIME, "rb") as f:
        name, h = None, None
        for raw in f:
            if raw.startswith(b">"):
                if name is not None:
                    check[name] = h.hexdigest()
                name, h = raw[1:].strip().decode("ascii"), hashlib.sha256()
            else:
                h.update(raw.rstrip(b"\n").upper())
        if name is not None:
            check[name] = h.hexdigest()
    seq_unchanged = all(check[k] == v["seq_sha256"] for k, v in per_contig.items())

    man = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "source_reference_fasta": {"file": os.path.basename(a.source), "sha256": src_sha, "md5": src_md5,
                                      "md5_matches_ncbi": src_md5 == EXPECTED_MD5_NCBI, "preserved": "byte-for-byte"},
           "runtime_reference_fasta": {"file": RUNTIME, "sha256": rt_sha, "md5": rt_md5,
                                       "fai": RUNTIME + ".fai", "fai_built_by": "src/wgs/reference_prepare.py"},
           "sequence_content_changed": False if seq_unchanged else "CHECK FAILED",
           "header_names_changed": True,
           "header_rule": "leading 'chr' removed from the contig identifier; description dropped",
           "header_mapping": mapping, "n_contigs": len(mapping),
           "per_contig_sequence_sha256": per_contig,
           "statement": "The NCBI source FASTA is preserved byte-for-byte. A separate runtime FASTA "
                        "changes contig identifiers only; nucleotide sequence is unchanged."}
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    io.open(MANIFEST, "w", encoding="utf-8").write(json.dumps(man, indent=1))
    print(f"  source  sha256 {src_sha[:16]}…  md5 {src_md5}  (NCBI: {'OK' if man['source_reference_fasta']['md5_matches_ncbi'] else 'MISMATCH'})")
    print(f"  runtime sha256 {rt_sha[:16]}…  md5 {rt_md5}  contigs {len(mapping)}  "
          f"sequence_content_changed={man['sequence_content_changed']}")
    return 0 if seq_unchanged else 1


if __name__ == "__main__":
    sys.exit(main())
