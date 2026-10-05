"""EXP-027 · GO-B: descarga de los slices regionales brutos (VCF y CRAM) con su SHA256.

Se guardan los bytes tal como los sirve el servidor, por rango HTTP:
  - VCF de genotipos: los bloques BGZF de la cabecera de cada cromosoma y, por región de fase
    (ventana ± 250 kb), los bloques BGZF que tabix leería según el .tbi;
  - CRAM de cada hijo: la definición de fichero + contenedor de cabecera, los contenedores que el
    .crai asigna a sus 70 ventanas (sin buffer: AD solo dentro) y el contenedor EOF.
Cada pieza lleva URL, rango, tamaño y SHA256 en el manifest. Validación: ningún mensaje de error del
servidor inyectado; cada bloque BGZF se descomprime con su CRC32; el CRAM ensamblado pasa
`samtools quickcheck` e `index` (CRC32 por contenedor en CRAM 3). El BCF reducido GT:GQ/FILTER se
deriva en un paso posterior, sin descartar nunca los brutos antes de terminar Phase 1.

Uso:
    python -m src.exp027.slices fetch  --plan work/exp027/plan_a8 --data work/exp027/data
    python -m src.exp027.slices verify --data work/exp027/data      # recalcula todos los SHA256
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import struct
import subprocess
import sys
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import materialize as M
from . import plan as P

BGZF_EOF = bytes.fromhex("1f8b08040000000000ff0600424302001b0003000000000000000000")
CRAM_EOF_TAIL = 38
HEADER_PROBE = 4 << 20
WORKERS = 4
DERIVE_WORKERS = 6
_LOCK = threading.Lock()


class SliceError(RuntimeError):
    pass


def curl_range(url: str, start: int, end_incl: int) -> bytes:
    """Bytes [start, end_incl] por HTTPS con TLS verificado. Falla si el tamaño no cuadra o si el
    servidor inyectó un mensaje de error en el cuerpo (incidente del 2026-10-04)."""
    p = subprocess.run(["curl", "-fsSL", "--proto", "=https", "--retry", "8", "--retry-delay", "15",
                        "-r", f"{start}-{end_incl}", url], capture_output=True)
    if p.returncode:
        raise SliceError(f"curl {p.returncode} en {url} [{start}-{end_incl}]: {p.stderr.decode(errors='replace')[-300:]}")
    data = p.stdout
    if len(data) != end_incl - start + 1:
        raise SliceError(f"{url}: recibidos {len(data)} bytes, pedidos {end_incl - start + 1}")
    if M.INJECTED_ERROR in data:
        raise SliceError(f"{url}: mensaje de error del servidor dentro del cuerpo")
    return data


SUBRANGE = 256 << 20
SUBRANGE_TRIES = 5
PIECE_TRIES = 4


def curl_range_to_file(url: str, start: int, end_incl: int, dest: Path) -> None:
    """Como curl_range, pero en disco y por tramos de 256 MB, cada uno validado (tamaño exacto, sin
    mensaje de error del servidor) y reintentado por separado.

    El servidor de EBI inserta a veces un XML de error (ConnectionClosedException) en mitad del cuerpo
    y sigue enviando hasta completar el tamaño (2026-10-04: referencia, chr14; GO-B, chr2 7,1 GB):
    curl sale 0 y el tamaño cuadra. Tramos cortos acotan lo que hay que repetir.
    """
    tmp = dest.with_name(dest.name + ".seg")
    with open(dest, "wb") as out:
        a = start
        while a <= end_incl:
            b = min(a + SUBRANGE - 1, end_incl)
            for attempt in range(1, SUBRANGE_TRIES + 1):
                p = subprocess.run(["curl", "-fsSL", "--proto", "=https", "--retry", "8", "--retry-delay", "15",
                                    "-r", f"{a}-{b}", "-o", str(tmp), url], capture_output=True)
                ok = p.returncode == 0 and tmp.exists() and tmp.stat().st_size == b - a + 1
                if ok:
                    data = tmp.read_bytes()
                    ok = M.INJECTED_ERROR not in data
                if ok:
                    out.write(data)
                    break
                if attempt == SUBRANGE_TRIES:
                    raise SliceError(f"{url} [{a}-{b}]: {SUBRANGE_TRIES} intentos fallidos "
                                     f"(curl {p.returncode}, error inyectado o tamaño)")
                time.sleep(20 * attempt)
            a = b + 1
    tmp.unlink(missing_ok=True)
    if dest.stat().st_size != end_incl - start + 1:
        raise SliceError(f"{url}: recibidos {dest.stat().st_size} bytes, pedidos {end_incl - start + 1}")


def scan_bgzf_file(path: Path, stop_at: int, stop_inclusive: bool, base: int) -> tuple[int, str]:
    """Valida bloque a bloque (CRC32/ISIZE, sin error inyectado) hasta el bloque que empieza en
    stop_at (offset absoluto; incluido si stop_inclusive). Devuelve (bytes que se conservan, sha256)."""
    h = hashlib.sha256()
    keep = 0
    with open(path, "rb") as f:
        while True:
            head = f.read(18)
            if len(head) < 18:
                break
            if head[:4] != b"\x1f\x8b\x08\x04":
                raise SliceError(f"{path.name}: cabecera BGZF inválida en {keep}")
            xlen = struct.unpack_from("<H", head, 10)[0]
            extra = head[12:18] + f.read(xlen - 6) if xlen > 6 else head[12:12 + xlen]
            bsize = None
            x = 0
            while x < xlen:
                if extra[x] == 66 and extra[x + 1] == 67:
                    bsize = struct.unpack_from("<H", extra, x + 4)[0] + 1
                x += 4 + struct.unpack_from("<H", extra, x + 2)[0]
            if bsize is None:
                raise SliceError(f"{path.name}: bloque sin campo BC")
            consumed = 12 + xlen
            rest = f.read(bsize - consumed)
            if len(rest) < bsize - consumed:
                break                                           # bloque incompleto: fuera del rango
            block = head[:12] + extra[:xlen] + rest
            abs_off = base + keep
            if abs_off > stop_at or (abs_off == stop_at and not stop_inclusive):
                break
            if M.INJECTED_ERROR in block:
                raise SliceError(f"{path.name}: mensaje de error del servidor dentro del cuerpo")
            inflate_block(block)
            h.update(block)
            keep += bsize
    return keep, h.hexdigest()


def bgzf_blocks(buf: bytes):
    """Recorre bloques BGZF completos: [(offset, tamaño)]. Se detiene en el primero incompleto."""
    out, o = [], 0
    while o + 18 <= len(buf):
        if buf[o:o + 4] != b"\x1f\x8b\x08\x04":
            raise SliceError(f"cabecera BGZF inválida en el byte {o}")
        xlen = struct.unpack_from("<H", buf, o + 10)[0]
        bsize = None
        x = o + 12
        while x < o + 12 + xlen:
            si1, si2, slen = buf[x], buf[x + 1], struct.unpack_from("<H", buf, x + 2)[0]
            if si1 == 66 and si2 == 67:
                bsize = struct.unpack_from("<H", buf, x + 4)[0] + 1
            x += 4 + slen
        if bsize is None:
            raise SliceError("bloque BGZF sin campo BC")
        if o + bsize > len(buf):
            break
        out.append((o, bsize))
        o += bsize
    return out


def inflate_block(block: bytes) -> bytes:
    """Descomprime un bloque BGZF y verifica su CRC32 e ISIZE."""
    xlen = struct.unpack_from("<H", block, 10)[0]
    data = zlib.decompress(block[12 + xlen:-8], -15)
    crc, isize = struct.unpack_from("<II", block, len(block) - 8)
    if zlib.crc32(data) & 0xFFFFFFFF != crc or len(data) != isize:
        raise SliceError("CRC32 o ISIZE de bloque BGZF no coincide")
    return data


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _record(manifest: dict, path: Path, key: str, rec: dict) -> None:
    with _LOCK:
        manifest[key] = rec
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8", newline="\n")


def _done(manifest: dict, key: str, data: Path) -> bool:
    """Pieza ya descargada: existe con el tamaño registrado (el SHA256 completo se verifica en
    `verify`, no en cada reanudación)."""
    rec = manifest.get(key)
    return bool(rec) and (data / rec["path"]).exists() and (data / rec["path"]).stat().st_size == rec["bytes"]


def verify_all(data: Path, plan_dir: Path | None = None) -> int:
    """Revalidación desde cero de GO-B (que figure en el manifest no basta).

    Por pieza: existe, tamaño registrado, SHA256 recalculado y estructura: los ficheros BGZF (cabeceras
    y regiones VCF) se descomprimen bloque a bloque con CRC32/ISIZE y sin cola incompleta; el CRAM
    empieza por «CRAM» y acaba en el contenedor EOF. Con plan_dir, además, comprueba que están todas
    las piezas que el plan exige (regiones de fase de las 70 ventanas y los 20 CRAM).
    """
    man = json.loads((data / "goB/MANIFEST_goB.json").read_text(encoding="utf-8"))
    bad = []
    for key, rec in sorted(man.items()):
        path = data / rec["path"]
        if not path.exists() or path.stat().st_size != rec["bytes"]:
            bad.append(f"{key}:tamaño")
            continue
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(1 << 22), b""):
                h.update(block)
        if h.hexdigest() != rec["sha256"]:
            bad.append(f"{key}:sha256")
            continue
        try:
            if key.startswith("gt_"):
                n = sum(1 for _ in iter_inflated(path))
                if n == 0:
                    raise SliceError("sin bloques")
            elif key.startswith("cram:"):
                with open(path, "rb") as f:
                    head = f.read(4)
                    f.seek(-CRAM_EOF_TAIL, 2)
                    tail = f.read(8)
                if head != b"CRAM" or tail != bytes.fromhex("0f000000ffffffff"):
                    raise SliceError("firma CRAM o EOF incorrecta")
        except (SliceError, zlib.error) as e:
            bad.append(f"{key}:estructura({e})")
    missing = []
    if plan_dir is not None:
        plan = json.loads((plan_dir / "plan_windows.json").read_text(encoding="utf-8"))
        wins = _windows(plan["evaluation"] + plan["calibration"])
        regions = sorted({P.phasing_region(w, P.BUFFER_BP, plan["lengths"]) for w in wins})
        need = [f"gt_region:{c}:{s}-{e}" for c, s, e in regions] + \
               [f"gt_header:{c}" for c in sorted({r[0] for r in regions})] + \
               [f"cram:{s['child']}" for s in plan["selection"]]
        missing = [k for k in need if k not in man]
    print(f"{len(man) - len(bad)}/{len(man)} piezas válidas (tamaño, SHA256, CRC/estructura)"
          + (f"; MAL: {bad}" if bad else "") + (f"; FALTAN: {missing}" if missing else ""))
    return 1 if bad or missing else 0


def verify_derived(data: Path, docker_root: Path) -> int:
    """Cada BCF derivado: SHA256 registrado, índice presente y legible con registros (bcftools index -n);
    cada CRAM ensamblado: quickcheck (vuelve a ejecutarse) e índice con el SHA256 registrado."""
    from . import tools
    from .orchestrate import SAMTOOLS_IMAGE
    der = json.loads((data / "goB/MANIFEST_goB_derived.json").read_text(encoding="utf-8"))
    bad = []
    for key, rec in sorted(der.items()):
        path = docker_root / rec["path"]
        if not path.exists() or sha256(path.read_bytes()) != rec["sha256"]:
            bad.append(f"{key}:sha256")
            continue
        if key.startswith("gt_region:"):
            p = subprocess.run(["docker", "run", "--rm", "-v", f"{docker_root}:/data", tools.BCFTOOLS_IMAGE,
                                "bcftools", "index", "-n", f"/data/{rec['path']}"], capture_output=True, text=True)
            if p.returncode != 0 or not p.stdout.strip().isdigit() or int(p.stdout) == 0:
                bad.append(f"{key}:indice")
        elif key.startswith("cram_index:"):
            cram = rec["path"][:-len(".crai")]
            p = subprocess.run(["docker", "run", "--rm", "-v", f"{docker_root}:/data", SAMTOOLS_IMAGE,
                                "samtools", "quickcheck", "-v", f"/data/{cram}"], capture_output=True, text=True)
            if p.returncode != 0:
                bad.append(f"{key}:quickcheck")
    n_gt = sum(k.startswith("gt_region:") for k in der)
    n_cr = sum(k.startswith("cram_index:") for k in der)
    print(f"derivados: {n_gt} BCF y {n_cr} CRAM indexados; {len(der) - len(bad)}/{len(der)} válidos"
          + (f"; MAL: {bad}" if bad else ""))
    return 1 if bad else 0


# ---------------------------------------------------------------- VCF
def gt_url(chrom: str) -> str:
    return M.GT_DIR + M.GT_NAME.format(chrom=chrom)


def fetch_gt_header(chrom: str, out: Path) -> dict:
    """Bloques BGZF desde el byte 0 hasta el que contiene el final de la línea #CHROM."""
    url = gt_url(chrom)
    probe = HEADER_PROBE
    while True:
        buf = curl_range(url, 0, probe - 1)
        text, end = b"", None
        for o, n in bgzf_blocks(buf):
            text += inflate_block(buf[o:o + n])
            i = text.find(b"\n#CHROM")
            if i >= 0 and text.find(b"\n", i + 1) >= 0:
                end = o + n
                break
        if end is not None:
            raw = buf[:end]
            out.write_bytes(raw)
            return {"url": url, "range": [0, end - 1], "bytes": end, "sha256": sha256(raw)}
        probe *= 2
        if probe > 256 << 20:
            raise SliceError(f"cabecera de {chrom} > 256 MB")


def fetch_gt_region(chrom: str, start: int, end: int, header_end: int, refs, out: Path,
                    file_size: int) -> dict:
    """Bloques BGZF de la región según el .tbi, cortados en límites de bloque (en disco)."""
    v = P.tbi_region_voffsets(refs, chrom, start, end)
    if v is None:
        raise SliceError(f"el .tbi no tiene datos para {chrom}:{start}-{end}")
    lo_c, hi_c, hi_u = v[0] >> 16, v[1] >> 16, v[1] & 0xFFFF
    lo_c = max(lo_c, header_end)
    url = gt_url(chrom)
    tmp = out.with_suffix(".part")
    curl_range_to_file(url, lo_c, min(hi_c + P.BGZF_MAX_BLOCK, file_size) - 1, tmp)
    keep, digest = scan_bgzf_file(tmp, hi_c, hi_u != 0, lo_c)
    if keep == 0:
        raise SliceError(f"{chrom}:{start}-{end}: ningún bloque completo")
    with open(tmp, "r+b") as f:
        f.truncate(keep)                    # solo bloques completos hasta el último de la región
    tmp.replace(out)
    return {"url": url, "range": [lo_c, lo_c + keep - 1], "bytes": keep, "sha256": digest,
            "region": f"{chrom}:{start}-{end}"}


# ---------------------------------------------------------------- CRAM
def container_ranges(crai, seq_ids: dict, windows, cram_size: int):
    """Rangos de bytes contiguos (inicio, fin incl.) de los contenedores que solapan las ventanas."""
    rows, offsets = crai
    nxt = {o: (offsets[i + 1] if i + 1 < len(offsets) else cram_size - CRAM_EOF_TAIL)
           for i, o in enumerate(offsets)}
    hit = set()
    for chrom, s, e in windows:
        sid = seq_ids[chrom]
        hit |= {r[3] for r in rows if r[0] == sid and r[1] <= e and r[1] + r[2] - 1 >= s}
    ranges = []
    for o in sorted(hit):
        if ranges and ranges[-1][1] + 1 == o:
            ranges[-1][1] = nxt[o] - 1
        else:
            ranges.append([o, nxt[o] - 1])
    return [tuple(r) for r in ranges]


def fetch_cram(child: str, url: str, cram_size: int, crai, seq_ids, windows, out: Path) -> dict:
    """Cabecera + contenedores de las ventanas + EOF, concatenados en orden de fichero."""
    head_end = crai[1][0]
    pieces = [("header", 0, head_end - 1)]
    pieces += [("containers", a, b) for a, b in container_ranges(crai, seq_ids, windows, cram_size)]
    pieces.append(("eof", cram_size - CRAM_EOF_TAIL, cram_size - 1))
    recs, h = [], hashlib.sha256()
    tmp = out.with_suffix(".part")
    with open(tmp, "wb") as f:
        for kind, a, b in pieces:
            data = curl_range(url, a, b)
            if kind == "eof" and data[:8] != bytes.fromhex("0f000000ffffffff"):
                raise SliceError(f"{child}: el contenedor EOF no tiene la firma esperada")
            f.write(data)
            h.update(data)
            recs.append({"kind": kind, "range": [a, b], "bytes": len(data), "sha256": sha256(data)})
    tmp.replace(out)
    return {"url": url, "pieces": recs, "bytes": sum(r["bytes"] for r in recs), "sha256": h.hexdigest()}


# ---------------------------------------------------------------- órdenes
def _windows(ids):
    out = []
    for w in ids:
        c, rng = w.split(":")
        s, e = (int(x) for x in rng.split("-"))
        out.append((c, s, e))
    return out


def fetch_all(plan_dir: Path, data: Path, workers: int = WORKERS) -> int:
    plan = json.loads((plan_dir / "plan_windows.json").read_text(encoding="utf-8"))
    sizes = {i["child"]: i["cram_bytes"] for i in json.loads(
        Path("work/exp027/inventory/selection.json").read_text(encoding="utf-8"))["selection"]}
    root = data / "goB"
    (root / "gt_raw").mkdir(parents=True, exist_ok=True)
    (root / "cram_raw").mkdir(parents=True, exist_ok=True)
    man_path = root / "MANIFEST_goB.json"
    manifest = json.loads(man_path.read_text(encoding="utf-8")) if man_path.exists() else {}
    wins = _windows(plan["evaluation"] + plan["calibration"])
    regions = sorted({P.phasing_region(w, P.BUFFER_BP, plan["lengths"]) for w in wins})
    chroms = sorted({r[0] for r in regions}, key=lambda c: int(c[3:]))
    stamp = lambda: dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    headers = {}
    for c in chroms:
        key = f"gt_header:{c}"
        path = root / "gt_raw" / f"{c}.header.bgzf"
        if not _done(manifest, key, data):
            rec = fetch_gt_header(c, path)
            _record(manifest, man_path, key, {**rec, "path": str(path.relative_to(data)).replace("\\", "/"),
                                              "fetched_utc": stamp()})
        headers[c] = manifest[key]["range"][1] + 1
        print(f"cabecera {c}: {manifest[key]['bytes']:,} bytes", flush=True)

    tbis = {c: P.read_tbi(data / f"gt_index/{M.GT_NAME.format(chrom=c)}.tbi") for c in chroms}
    per_chrom = json.loads(Path("work/exp027/inventory/resources.json").read_text(encoding="utf-8"))["genotypes"]["per_chrom"]
    gt_sizes = {f"chr{k}": v["vcf"] for k, v in per_chrom.items()}
    crais = {s["child"]: P.read_crai(data / f"crai/{s['child']}.final.cram.crai") for s in plan["selection"]}

    def gt_job(r):
        c, s, e = r
        key = f"gt_region:{c}:{s}-{e}"
        path = root / "gt_raw" / f"{c}_{s}_{e}.bgzf"
        if _done(manifest, key, data):
            return key, manifest[key]["bytes"], True
        rec = fetch_gt_region(c, s, e, headers[c], tbis[c], path, gt_sizes[c])
        _record(manifest, man_path, key, {**rec, "path": str(path.relative_to(data)).replace("\\", "/"),
                                          "fetched_utc": stamp()})
        return key, rec["bytes"], False

    def cram_job(s):
        key = f"cram:{s['child']}"
        path = root / "cram_raw" / f"{s['child']}.slices.cram"
        if _done(manifest, key, data):
            return key, manifest[key]["bytes"], True
        rec = fetch_cram(s["child"], s["cram_https"], sizes[s["child"]], crais[s["child"]],
                         plan["seq_ids"], wins, path)
        _record(manifest, man_path, key, {**rec, "path": str(path.relative_to(data)).replace("\\", "/"),
                                          "fetched_utc": stamp()})
        return key, rec["bytes"], False

    def retried(fn, arg, label):
        """Una pieza que no valida se repite entera; una pieza mala no detiene las demás."""
        for attempt in range(1, PIECE_TRIES + 1):
            try:
                return fn(arg)
            except SliceError as e:
                print(f"REINTENTO {label} ({attempt}/{PIECE_TRIES}): {e}", flush=True)
                if attempt == PIECE_TRIES:
                    raise
                time.sleep(60 * attempt)

    total, failed = 0, []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(retried, gt_job, r, f"{r[0]}:{r[1]}-{r[2]}"): f"gt_region:{r[0]}:{r[1]}-{r[2]}"
                for r in regions}
        futs.update({ex.submit(retried, cram_job, s, s["child"]): f"cram:{s['child']}" for s in plan["selection"]})
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                key, nbytes, cached = fut.result()
            except SliceError as e:
                failed.append(futs[fut])
                print(f"[{i}/{len(futs)}] FALLO {futs[fut]}: {e}", flush=True)
                continue
            total += nbytes
            print(f"[{i}/{len(futs)}] {key} {nbytes / 1e9:.2f} GB{' (ya estaba)' if cached else ''} "
                  f"· acumulado {total / 1e9:.1f} GB", flush=True)
    if failed:
        print(f"GO-B INCOMPLETO: {len(failed)} piezas fallidas: {failed}", flush=True)
        return 1
    print(f"OK GO-B: {len(regions)} regiones VCF + {len(plan['selection'])} CRAM; {total / 1e9:.1f} GB", flush=True)
    return 0


# ---------------------------------------------------------------- derivación GT:GQ/FILTER
def iter_inflated(path: Path):
    """Descomprime bloque a bloque un fichero de bloques BGZF completos (verifica CRC32)."""
    with open(path, "rb") as f:
        buf = b""
        while True:
            chunk = f.read(1 << 24)
            if not chunk and not buf:
                return
            buf += chunk
            blocks = bgzf_blocks(buf)
            if not blocks:
                if not chunk:
                    raise SliceError(f"{path.name}: cola BGZF incompleta")
                continue
            for o, n in blocks:
                yield inflate_block(buf[o:o + n])
            last = blocks[-1][0] + blocks[-1][1]
            buf = buf[last:]
            if not chunk and buf:
                raise SliceError(f"{path.name}: cola BGZF incompleta")


def header_text(path: Path) -> bytes:
    """Solo las líneas de cabecera (#) de los bloques de cabecera del cromosoma."""
    text = b"".join(iter_inflated(path))
    lines = text.split(b"\n")
    out = [l for l in lines if l.startswith(b"#")]
    if not out or not out[-1].startswith(b"#CHROM"):
        raise SliceError(f"{path.name}: cabecera sin línea #CHROM completa")
    return b"\n".join(out) + b"\n"


def region_records(path: Path, skip: int):
    """Registros completos de la región: salta los `skip` primeros bytes descomprimidos (cola de un
    registro anterior, offset virtual del .tbi) y descarta el registro final cortado."""
    pending = b""
    first = True
    for data in iter_inflated(path):
        if first:
            data, first = data[skip:], False
        pending += data
        cut = pending.rfind(b"\n")
        if cut >= 0:
            yield pending[:cut + 1]
            pending = pending[cut + 1:]


def derive_region(data: Path, plan: dict, chrom: str, start: int, end: int, samples_rel: str,
                  docker_root: Path, refs, header_end: int) -> dict:
    """Bruto -> BCF reducido (GT, GQ, FILTER; sin INFO) de las muestras necesarias, solo la región."""
    from . import tools
    v = P.tbi_region_voffsets(refs, chrom, start, end)
    if (v[0] >> 16) < header_end:
        raise SliceError(f"{chrom}:{start}-{end}: la región empieza dentro de la cabecera")
    raw = data / f"goB/gt_raw/{chrom}_{start}_{end}.bgzf"
    out_rel = f"work/exp027/data/goB/gt_reduced/{chrom}_{start}_{end}.gtgq.bcf"
    (docker_root / out_rel).parent.mkdir(parents=True, exist_ok=True)
    region = f"{chrom}:{start}-{end}"
    script = (f"bcftools view -t {region} -S /data/{samples_rel} -Ou - | "
              f"bcftools annotate -x INFO,^FORMAT/GT,FORMAT/GQ -Ob -o /data/{out_rel} && "
              f"bcftools index -f /data/{out_rel}")
    cmd = ["docker", "run", "--rm", "-i", "-v", f"{docker_root}:/data", tools.BCFTOOLS_IMAGE, "sh", "-c", script]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        proc.stdin.write(header_text(data / f"goB/gt_raw/{chrom}.header.bgzf"))
        for chunk in region_records(raw, v[0] & 0xFFFF):
            proc.stdin.write(chunk)
        proc.stdin.close()
    except BrokenPipeError:
        pass                                   # el error real viene en stderr
    err = proc.stderr.read().decode(errors="replace")
    if proc.wait() != 0:
        raise SliceError(f"derivación de {region} falló: {err[-800:]}")
    out = docker_root / out_rel
    h = hashlib.sha256()
    with open(out, "rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
    return {"path": out_rel, "bytes": out.stat().st_size, "sha256": h.hexdigest(),
            "raw_sha256": None, "region": region}


def derive_all(plan_dir: Path, data: Path, partial: bool = False) -> int:
    import yaml
    plan = json.loads((plan_dir / "plan_windows.json").read_text(encoding="utf-8"))
    docker_root = Path(yaml.safe_load(Path("config/paths.yaml").read_text(encoding="utf-8"))["compute"]["docker_repo_root"])
    man = json.loads((data / "goB/MANIFEST_goB.json").read_text(encoding="utf-8"))
    i2504 = P.index_samples(data / "meta/index_2504.sequence.index")
    need = set(i2504) | {s[k] for s in plan["selection"] for k in ("child", "father", "mother")}
    samples_rel = "work/exp027/data/goB/samples_needed.txt"
    (docker_root / samples_rel).parent.mkdir(parents=True, exist_ok=True)
    with open(docker_root / samples_rel, "w", encoding="ascii", newline="\n") as f:
        f.write("".join(f"{s}\n" for s in sorted(need)))
    der_path = data / "goB/MANIFEST_goB_derived.json"
    derived = json.loads(der_path.read_text(encoding="utf-8")) if der_path.exists() else {}
    wins = _windows(plan["evaluation"] + plan["calibration"])
    regions = sorted({P.phasing_region(w, P.BUFFER_BP, plan["lengths"]) for w in wins})
    keys = [f"gt_region:{c}:{s}-{e}" for c, s, e in regions]
    missing = [k for k in keys if k not in man] + \
              [f"cram:{s['child']}" for s in plan["selection"] if f"cram:{s['child']}" not in man]
    if missing and not partial:
        raise SliceError(f"faltan piezas de GO-B: {missing[:5]} ({len(missing)})")
    if partial:                                  # solo piezas ya terminadas (la descarga sigue)
        keys = [k for k in keys if k in man]
    refs = {c: P.read_tbi(data / f"gt_index/{M.GT_NAME.format(chrom=c)}.tbi") for c in {r[0] for r in regions}}

    def job(key):
        if key in derived and (docker_root / derived[key]["path"]).exists():
            return key, derived[key], True
        c, rng = key.split(":", 1)[1].split(":")
        s, e = (int(x) for x in rng.split("-"))
        rec = derive_region(data, plan, c, s, e, samples_rel, docker_root, refs[c],
                            man[f"gt_header:{c}"]["range"][1] + 1)
        rec["raw_sha256"] = man[key]["sha256"]
        rec["n_samples"] = len(need)
        return key, rec, False

    with ThreadPoolExecutor(max_workers=DERIVE_WORKERS) as ex:
        for i, fut in enumerate(as_completed([ex.submit(job, k) for k in keys]), 1):
            key, rec, cached = fut.result()
            _record(derived, der_path, key, rec)
            print(f"[{i}/{len(keys)}] {rec['region']} -> {rec['bytes'] / 1e6:.0f} MB"
                  f"{' (ya estaba)' if cached else ''}", flush=True)
    for s in plan["selection"]:
        key = f"cram_index:{s['child']}"
        if key in derived or f"cram:{s['child']}" not in man:
            continue
        _record(derived, der_path, key, prepare_cram(docker_root, man[f"cram:{s['child']}"]["path"]))
        print(f"CRAM {s['child']}: quickcheck e índice OK", flush=True)
    n_gt = sum(k.startswith("gt_region:") for k in derived)
    n_cram = sum(k.startswith("cram_index:") for k in derived)
    print(f"derivados en total: {n_gt} regiones VCF y {n_cram} CRAM indexados "
          f"(el plan exige {len(regions)} y {len(plan['selection'])})", flush=True)
    return 0


def prepare_cram(docker_root: Path, cram_rel_to_data: str) -> dict:
    """samtools quickcheck + index del CRAM ensamblado (los contenedores llevan CRC32 en CRAM 3)."""
    from .orchestrate import SAMTOOLS_IMAGE
    rel = f"work/exp027/data/{cram_rel_to_data}"
    cmd = ["docker", "run", "--rm", "-v", f"{docker_root}:/data", SAMTOOLS_IMAGE, "sh", "-c",
           f"samtools quickcheck -v /data/{rel} && samtools index /data/{rel}"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SliceError(f"CRAM inválido {rel}: {p.stdout[-300:]} {p.stderr[-300:]}")
    idx = docker_root / f"{rel}.crai"
    return {"path": f"{rel}.crai", "bytes": idx.stat().st_size, "sha256": sha256(idx.read_bytes())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["fetch", "verify", "derive", "verify-derived"])
    ap.add_argument("--plan", default="work/exp027/plan_a8")
    ap.add_argument("--data", default="work/exp027/data")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--partial", action="store_true", help="derive: solo las piezas ya descargadas")
    a = ap.parse_args(argv)
    if a.step == "verify":
        return verify_all(Path(a.data), Path(a.plan))
    if a.step == "verify-derived":
        import yaml
        root = Path(yaml.safe_load(Path("config/paths.yaml").read_text(encoding="utf-8"))["compute"]["docker_repo_root"])
        return verify_derived(Path(a.data), root)
    if a.step == "derive":
        return derive_all(Path(a.plan), Path(a.data), a.partial)
    return fetch_all(Path(a.plan), Path(a.data), a.workers)


if __name__ == "__main__":
    sys.exit(main())
