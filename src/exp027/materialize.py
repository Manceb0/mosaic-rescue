"""EXP-027 · materialización de recursos auxiliares e índices (GO-A).

Descarga por HTTPS con verificación TLS (curl, nunca -k), comprueba el MD5 publicado donde existe y
calcula el SHA256 local de todo. Registra URL, tamaño y cabeceras en un manifest. No descarga cuerpos
de CRAM/VCF: solo índices (.tbi, .crai), metadatos, pistas de exclusión, mapa, callset SV y referencia.

Uso:  python -m src.exp027.materialize fetch --data work/exp027/data
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HC = "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/"
GT_DIR = HC + "working/20201028_3202_raw_GT_with_annot/"
GT_NAME = "20201028_CCDG_14151_B01_GRM_WGS_2020-08-05_{chrom}.recalibrated_variants.vcf.gz"
SV_DIR = HC + "working/20210124.SV_Illumina_Integration/"
SV_NAME = "1KGP_3202.gatksv_svtools_novelins.freeze_V3.wAF.vcf.gz"
SV_MD5_MANIFEST = "1KGP_3202.Illumina_ensemble_callset.freeze_V3.manifest.md5"
REF_DIR = "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/"
REF_NAME = "GRCh38_full_analysis_set_plus_decoy_hla"
UCSC = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/"
AUTOSOMES = tuple(f"chr{i}" for i in range(1, 23))


def static_resources() -> list[dict]:
    """Recursos fijos del GO-A: (clave, url, ruta relativa, md5 publicado si lo hay)."""
    r = [
        ("ped_population", HC + "20130606_g1k_3202_samples_ped_population.txt", "meta/ped_population.txt"),
        ("index_2504", HC + "1000G_2504_high_coverage.sequence.index", "meta/index_2504.sequence.index"),
        ("index_698", HC + "1000G_698_related_high_coverage.sequence.index", "meta/index_698.sequence.index"),
        ("pedigree_info", HC + "working/1kGP.3202_samples.pedigree_info.txt", "meta/pedigree_info.txt"),
        ("genetic_maps_b38", "https://github.com/odelaneau/shapeit4/raw/master/maps/genetic_maps.b38.tar.gz",
         "maps/genetic_maps.b38.tar.gz"),
        ("ucsc_gap", UCSC + "gap.txt.gz", "tracks/ucsc_gap.txt.gz"),
        ("ucsc_centromeres", UCSC + "centromeres.txt.gz", "tracks/ucsc_centromeres.txt.gz"),
        ("ucsc_segdups", UCSC + "genomicSuperDups.txt.gz", "tracks/ucsc_genomicSuperDups.txt.gz"),
        ("encode_blacklist_v2",
         "https://raw.githubusercontent.com/Boyle-Lab/Blacklist/master/lists/hg38-blacklist.v2.bed.gz",
         "tracks/hg38-blacklist.v2.bed.gz"),
        ("sv_md5_manifest", SV_DIR + SV_MD5_MANIFEST, "sv/" + SV_MD5_MANIFEST),
        ("sv_readme", SV_DIR + "1KGP_3202.Illumina_ensemble_callset.freeze_V3.README.md", "sv/freeze_V3.README.md"),
        ("sv_callset", SV_DIR + SV_NAME, "sv/" + SV_NAME),
        ("sv_callset_tbi", SV_DIR + SV_NAME + ".tbi", "sv/" + SV_NAME + ".tbi"),
        ("reference_readme", REF_DIR + "README.20150309." + REF_NAME, "ref/README." + REF_NAME),
        ("reference_fai", REF_DIR + REF_NAME + ".fa.fai", f"ref/{REF_NAME}.fa.fai"),
        ("reference_dict", REF_DIR + REF_NAME + ".dict", f"ref/{REF_NAME}.dict"),
        ("reference_fa", REF_DIR + REF_NAME + ".fa", f"ref/{REF_NAME}.fa"),
    ]
    r += [(f"gt_tbi_{c}", GT_DIR + GT_NAME.format(chrom=c) + ".tbi", f"gt_index/{GT_NAME.format(chrom=c)}.tbi")
          for c in AUTOSOMES]
    return [{"key": k, "url": u, "path": p} for k, u, p in r]


def crai_resources(selection: list[dict]) -> list[dict]:
    """Un .crai por hijo seleccionado, con la URL HTTPS de su CRAM."""
    out = []
    for s in selection:
        url = s["cram_http"].replace("http://", "https://", 1) + ".crai"
        out.append({"key": f"crai_{s['child']}", "url": url, "path": f"crai/{s['child']}.final.cram.crai"})
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _headers(raw: str) -> dict:
    """Cabeceras de la última respuesta (tras redirecciones)."""
    blocks = [b for b in raw.replace("\r", "").split("\n\n") if b.strip()]
    out = {}
    for line in blocks[-1].split("\n")[1:] if blocks else []:
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def fetch(res: dict, data: Path) -> dict:
    """curl HTTPS con TLS verificado; reanuda si hay parcial. Falla fuerte si curl falla o el
    tamaño no coincide con Content-Length."""
    dest = data / res["path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    hdr = dest.with_name(dest.name + ".headers")
    cmd = ["curl", "-fsSL", "--proto", "=https", "--proto-redir", "=https", "--retry", "5",
           "--retry-delay", "10", "-C", "-", "-D", str(hdr), "-o", str(dest), res["url"]]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode not in (0,):
        raise RuntimeError(f"curl falló ({p.returncode}) en {res['key']}: {p.stderr.strip()}")
    headers = _headers(hdr.read_text(encoding="latin-1")) if hdr.exists() else {}
    size = dest.stat().st_size
    rec = {**res, "bytes": size, "content_length": headers.get("content-length"),
           "content_range": headers.get("content-range"), "last_modified": headers.get("last-modified"),
           "etag": headers.get("etag"), "sha256": sha256_file(dest),
           "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    if headers.get("content-length") and not headers.get("content-range") and int(headers["content-length"]) != size:
        raise RuntimeError(f"{res['key']}: tamaño {size} != Content-Length {headers['content-length']}")
    return rec


def published_md5(data: Path, selection: list[dict]) -> dict[str, str]:
    """MD5 publicados: manifest del callset SV y sequence.index de los CRAM (para sus .crai no hay)."""
    out = {}
    man = data / "sv" / SV_MD5_MANIFEST
    for line in man.read_text(encoding="ascii").splitlines():
        f = line.split("\t")
        if len(f) == 3:
            out["sv/" + f[0]] = f[2]
    return out


INJECTED_ERROR = b"<Error><Code>"


def integrity(rec: dict, data: Path) -> str:
    """Comprobación independiente del MD5 publicado (que casi nunca existe).

    El 2026-10-04 el servidor de EBI insertó un XML de error a mitad de la referencia; curl salió 0
    y el tamaño coincidía. Por eso: (1) ningún fichero puede contener ese XML; (2) todo .gz/.tbi/
    .crai/.tar.gz se descomprime entero (CRC32 de gzip/BGZF); (3) la referencia se valida contig a
    contig contra las M5 del .dict (ver check_reference_md5).
    """
    path = data / rec["path"]
    tail = b""
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            if INJECTED_ERROR in tail + block:
                raise RuntimeError(f"{rec['key']}: contiene un mensaje de error del servidor inyectado")
            tail = block[-len(INJECTED_ERROR):]
    if path.name.endswith((".gz", ".tbi", ".crai")):
        import gzip
        with gzip.open(path, "rb") as g:
            while g.read(1 << 22):
                pass
        return "gzip_crc_ok"
    return "no_injected_error"


def check_reference_md5(data: Path) -> int:
    """MD5 de cada contig del FASTA == M5 del .dict, para todos los contigs."""
    from .plan import dict_md5, reference_md5
    dct = dict_md5(data / f"ref/{REF_NAME}.dict")
    ref = reference_md5(data / f"ref/{REF_NAME}.fa", wanted=tuple(dct))
    bad = [c for c in dct if ref.get(c) != dct[c]]
    if bad:
        raise RuntimeError(f"referencia corrupta o distinta: M5 != .dict en {bad[:10]}")
    return len(dct)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["fetch"])
    ap.add_argument("--data", default="work/exp027/data")
    ap.add_argument("--selection", default="work/exp027/inventory/selection.json")
    a = ap.parse_args(argv)
    data = Path(a.data)
    selection = json.loads(Path(a.selection).read_text(encoding="utf-8"))["selection"]
    manifest_path = data / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    curl_v = subprocess.run(["curl", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    for res in static_resources() + crai_resources(selection):
        if res["key"] in manifest and (data / res["path"]).exists() \
                and manifest[res["key"]]["sha256"] == sha256_file(data / res["path"]):
            continue
        rec = fetch(res, data)
        rec["tool"] = curl_v
        manifest[res["key"]] = rec
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
        print(f"{res['key']:28s} {rec['bytes']:>14,d}  {rec['sha256'][:16]}", flush=True)
    md5 = published_md5(data, selection)
    bad = []
    for key, rec in manifest.items():
        if rec["path"] in md5:
            got = md5_file(data / rec["path"])
            rec["md5_published"], rec["md5_ok"] = md5[rec["path"]], got == md5[rec["path"]]
            if not rec["md5_ok"]:
                bad.append(key)
    for key, rec in manifest.items():
        rec["integrity"] = integrity(rec, data)
    n_contigs = check_reference_md5(data)
    manifest["reference_fa"]["integrity"] = f"m5_vs_dict_ok_{n_contigs}_contigs"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    if bad:
        print("MD5 NO COINCIDE:", bad)
        return 1
    print(f"OK: {len(manifest)} recursos; MD5 publicado verificado en "
          f"{sum('md5_ok' in r for r in manifest.values())}; integridad en todos; "
          f"referencia M5 == .dict en {n_contigs} contigs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
