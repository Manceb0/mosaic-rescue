"""EXP-027 · plan exacto previo a GO-B (Amendment 8): ventanas comunes, máscaras de sitio por hijo
y presupuesto de rangos.

Lee solo recursos materializados en GO-A (metadatos, pistas, callset SV, índices .tbi/.crai, mapa,
referencia). No toca cuerpos de VCF/CRAM de genotipos ni calcula nada de Phase 1 (BAF, SER, A1).

Comprobaciones de compatibilidad (fallo fuerte):
  - la selección re-derivada de los metadatos coincide con la del inventario;
  - el mapa SHAPEIT4 b38 tiene formato "pos chr cM", posiciones crecientes y cM no decreciente;
  - MD5 de chr1..chr22 de la referencia == M5 del .dict == M5 de la cabecera de cada CRAM;
  - los contigs del .tbi de genotipos y del callset SV se llaman chrN.

Uso:  python -m src.exp027.plan --data work/exp027/data --out work/exp027/plan
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
import subprocess
import sys
import tarfile
from pathlib import Path

from . import materialize as M
from .selection import conditioning_cohort, select_offspring
from .serialize import window_id
from .masks import SiteMasks, bed_lines, covered_fraction, sample_copy_changing
from .windows import (AUTOSOMES, BUB1B_WINDOW, Intervals, calibration_tiles, evaluation_lattice,
                      evaluation_windows, global_order, lattice_tiles, phasing_region)

BUFFER_BP = 250_000
BGZF_MAX_BLOCK = 65_536


class PlanError(RuntimeError):
    pass


# ---------------------------------------------------------------- metadatos y selección
def read_ped_population(path: Path):
    rows = [l.split() for l in path.read_text(encoding="ascii").splitlines()[1:] if l.strip()]
    return {r[1]: {"father": r[2], "mother": r[3], "superpop": r[6]} for r in rows}


def index_samples(path: Path) -> dict[str, dict]:
    out = {}
    lines = [l for l in path.read_text(encoding="ascii").splitlines() if l and not l.startswith("##")]
    head = lines[0].lstrip("#").split("\t")
    for l in lines[1:]:
        f = dict(zip(head, l.split("\t")))
        out[f["SAMPLE_NAME"]] = {"cram": f["ENA_FILE_PATH"], "md5": f["MD5SUM"]}
    return out


def rebuild_selection(data: Path):
    ped = read_ped_population(data / "meta/ped_population.txt")
    i2504 = index_samples(data / "meta/index_2504.sequence.index")
    i698 = index_samples(data / "meta/index_698.sequence.index")
    sequenced = set(i2504) | set(i698)
    trios = [{"child": s, "father": r["father"], "mother": r["mother"], "superpop": r["superpop"],
              "complete": r["father"] != "0" and r["mother"] != "0",
              "parents_sequenced": r["father"] in sequenced and r["mother"] in sequenced and s in sequenced}
             for s, r in ped.items()]
    chosen, short = select_offspring(trios)
    pedigree = [(s, r["father"], r["mother"]) for s, r in ped.items()]
    phase3 = sorted(i2504)
    n_eligible = sum(t["complete"] and t["parents_sequenced"] for t in trios)
    sel = []
    for sp in chosen:
        for t in chosen[sp]:
            cram = {**i2504, **i698}[t["child"]]
            sel.append({**{k: t[k] for k in ("child", "father", "mother", "superpop")},
                        "C_target_n": len(conditioning_cohort(phase3, t["child"], pedigree)),
                        "cram_https": cram["cram"].replace("ftp://", "https://", 1), "cram_md5": cram["md5"]})
    return sel, short, n_eligible


# ---------------------------------------------------------------- exclusiones
def ucsc_bed(path: Path, cols=(1, 2, 3)):
    """Tablas UCSC (bin chrom chromStart chromEnd …): base 0 semiabierta -> base 1 inclusiva."""
    items = []
    with gzip.open(path, "rt", encoding="ascii") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            items.append((p[cols[0]], int(p[cols[1]]) + 1, int(p[cols[2]])))
    return items


def bed_gz(path: Path):
    with gzip.open(path, "rt", encoding="ascii") as f:
        return [(p[0], int(p[1]) + 1, int(p[2])) for p in (l.split("\t") for l in f if l.strip())]


def trio_copy_changing(sv_vcf: Path, trios: list[dict]):
    """SV copy-changing de cada trío (Amendment 8 r4-r5), separados en hijo y padres.

    Intervalo [POS, END] (INFO/END; si falta, POS + len(REF) - 1). Se consideran todos los registros
    autosómicos del callset, sin filtrar por FILTER (máscara conservadora).
    """
    members = {t["child"]: (t["child"], t["father"], t["mother"]) for t in trios}
    out = {c: {"child_cc": [], "parent_cc": []} for c in members}
    stats = {"records": 0, "by_svtype": {}}
    with gzip.open(sv_vcf, "rt", encoding="ascii", errors="replace") as f:
        for line in f:
            if line.startswith("##"):
                continue
            if line.startswith("#"):
                head = line.rstrip("\n").split("\t")
                col = {s: i for i, s in enumerate(head)}
                missing = [s for m in members.values() for s in m if s not in col]
                if missing:
                    raise PlanError(f"muestras ausentes en el callset SV: {missing}")
                continue
            p = line.rstrip("\n").split("\t")
            if p[0] not in AUTOSOMES:
                continue
            info = dict(kv.split("=", 1) if "=" in kv else (kv, True) for kv in p[7].split(";"))
            pos = int(p[1])
            end = max(int(info["END"]) if "END" in info else pos + len(p[3]) - 1, pos)
            svtype = str(info.get("SVTYPE", "NA"))
            fmt = p[8].split(":")
            stats["records"] += 1
            stats["by_svtype"][svtype] = stats["by_svtype"].get(svtype, 0) + 1
            iv = (p[0], pos, end)
            for kid, (c, fa, mo) in members.items():
                if sample_copy_changing(svtype, fmt, p[col[c]]):
                    out[kid]["child_cc"].append(iv)
                if sample_copy_changing(svtype, fmt, p[col[fa]]) or sample_copy_changing(svtype, fmt, p[col[mo]]):
                    out[kid]["parent_cc"].append(iv)
    return out, stats


def _carries(sample_field: str) -> bool:
    gt = sample_field.split(":", 1)[0].replace("|", "/")
    return any(a not in ("0", ".") for a in gt.split("/"))


# ---------------------------------------------------------------- .tbi y .crai
def _reg2bins(beg: int, end: int):
    """Bins del esquema UCSC/tabix que solapan [beg, end) (base 0)."""
    end -= 1
    bins = [0]
    for shift, off in ((26, 1), (23, 9), (20, 73), (17, 585), (14, 4681)):
        bins += range(off + (beg >> shift), off + (end >> shift) + 1)
    return bins


def read_tbi(path: Path):
    raw = gzip.decompress(path.read_bytes())
    if raw[:4] != b"TBI\x01":
        raise PlanError(f"{path.name} no es un índice tabix")
    n_ref, fmt, cs, cb, ce, meta, skip, l_nm = struct.unpack_from("<8i", raw, 4)
    names = raw[36:36 + l_nm].split(b"\x00")[:n_ref]
    off = 36 + l_nm
    refs = {}
    for name in names:
        (n_bin,) = struct.unpack_from("<i", raw, off); off += 4
        bins = {}
        for _ in range(n_bin):
            b, n_chunk = struct.unpack_from("<Ii", raw, off); off += 8
            bins[b] = [struct.unpack_from("<QQ", raw, off + 16 * k) for k in range(n_chunk)]
            off += 16 * n_chunk
        (n_intv,) = struct.unpack_from("<i", raw, off); off += 4
        ioff = list(struct.unpack_from(f"<{n_intv}Q", raw, off)); off += 8 * n_intv
        refs[name.decode()] = (bins, ioff)
    return refs


def tbi_region_bytes(refs, chrom: str, start1: int, end1: int) -> int:
    """Bytes comprimidos que tabix pedirá para [start1, end1] (base 1): de la primera a la última
    chunk que solapa, más un bloque BGZF de cola. Cota superior razonable, no exacta."""
    bins, ioff = refs[chrom]
    beg0 = start1 - 1
    min_off = ioff[min(beg0 >> 14, len(ioff) - 1)] if ioff else 0
    lo, hi = None, None
    for b in _reg2bins(beg0, end1):
        for cb, ce in bins.get(b, ()):
            if ce <= min_off:
                continue
            lo = cb if lo is None else min(lo, cb)
            hi = ce if hi is None else max(hi, ce)
    if lo is None:
        return 0
    return (hi >> 16) - (lo >> 16) + BGZF_MAX_BLOCK


def read_crai(path: Path):
    rows = []
    with gzip.open(path, "rt", encoding="ascii") as f:
        for line in f:
            s, a, span, c_off, sl_off, sl_size = (int(x) for x in line.split("\t"))
            rows.append((s, a, span, c_off))
    offsets = sorted({r[3] for r in rows})
    return rows, offsets


def crai_region_bytes(crai, seq_id: int, start1: int, end1: int, cram_size: int) -> int:
    rows, offsets = crai
    nxt = {o: (offsets[i + 1] if i + 1 < len(offsets) else cram_size) for i, o in enumerate(offsets)}
    hit = {r[3] for r in rows if r[0] == seq_id and r[1] <= end1 and r[1] + r[2] - 1 >= start1}
    return sum(nxt[o] - o for o in hit)


# ---------------------------------------------------------------- compatibilidad
def reference_md5(fa: Path, wanted=AUTOSOMES) -> dict[str, str]:
    """MD5 de cada secuencia en mayúsculas sin saltos de línea (convención M5 de SAM/CRAM)."""
    out, name, h = {}, None, None
    with open(fa, "rb") as f:
        for line in f:
            if line.startswith(b">"):
                if name in wanted:
                    out[name] = h.hexdigest()
                name = line[1:].split()[0].decode()
                h = hashlib.md5() if name in wanted else None
            elif h is not None:
                h.update(line.rstrip(b"\r\n").upper())
    if name in wanted:
        out[name] = h.hexdigest()
    return out


def dict_md5(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="ascii").splitlines():
        if line.startswith("@SQ"):
            f = dict(x.split(":", 1) for x in line.split("\t")[1:])
            out[f["SN"]] = f.get("M5")
    return out


def cram_header_sq(url: str, first_container_offset: int) -> list[dict]:
    """Descarga solo los bytes previos al primer contenedor de datos (definición de fichero +
    contenedor de cabecera SAM) y devuelve las @SQ. Ningún registro de lectura."""
    p = subprocess.run(["curl", "-fsSL", "--proto", "=https", "--retry", "5", "-r",
                        f"0-{first_container_offset - 1}", url], capture_output=True)
    if p.returncode:
        raise PlanError(f"no se pudo leer la cabecera de {url}: {p.stderr.decode(errors='replace')}")
    buf = p.stdout
    if buf[:4] != b"CRAM":
        raise PlanError(f"{url}: no es CRAM")
    text = _cram_sam_header(buf)
    sq = []
    for line in text.splitlines():
        if line.startswith("@SQ"):
            sq.append(dict(x.split(":", 1) for x in line.split("\t")[1:]))
    return sq, len(buf)


def _itf8(b, o):
    x = b[o]
    if x < 0x80:
        return x, o + 1
    if x < 0xC0:
        return ((x & 0x3F) << 8) | b[o + 1], o + 2
    if x < 0xE0:
        return ((x & 0x1F) << 16) | (b[o + 1] << 8) | b[o + 2], o + 3
    if x < 0xF0:
        return ((x & 0x0F) << 24) | (b[o + 1] << 16) | (b[o + 2] << 8) | b[o + 3], o + 4
    return ((x & 0x0F) << 28) | (b[o + 1] << 20) | (b[o + 2] << 12) | (b[o + 3] << 4) | (b[o + 4] & 0x0F), o + 5


def _ltf8(b, o):
    x, n = b[o], 0
    while n < 8 and x & (0x80 >> n):
        n += 1
    val = x & (0xFF >> (n + 1)) if n < 8 else 0
    for k in range(n):
        val = (val << 8) | b[o + 1 + k]
    return val, o + 1 + n


def _cram_sam_header(buf: bytes) -> str:
    major = buf[4]
    o = 26
    (length,) = struct.unpack_from("<i", buf, o); o += 4
    for _ in range(4):
        _, o = _itf8(buf, o)                     # ref id, start, span, n_records
    _, o = (_ltf8(buf, o) if major >= 3 else _itf8(buf, o))
    _, o = (_ltf8(buf, o) if major >= 3 else _itf8(buf, o))
    _, o = _itf8(buf, o)                         # n_blocks
    n_land, o = _itf8(buf, o)
    for _ in range(n_land):
        _, o = _itf8(buf, o)
    if major >= 3:
        o += 4                                   # crc32
    method, ctype = buf[o], buf[o + 1]; o += 2
    _, o = _itf8(buf, o)
    csize, o = _itf8(buf, o)
    rsize, o = _itf8(buf, o)
    data = buf[o:o + csize]
    if method == 1:
        data = gzip.decompress(data)
    elif method != 0:
        raise PlanError(f"método de compresión de cabecera CRAM no soportado: {method}")
    (l_text,) = struct.unpack_from("<i", data, 0)
    return data[4:4 + l_text].decode("ascii", errors="replace")


def check_map(tar_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    found = {}
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf.getmembers():
            name = Path(m.name).name
            for c in AUTOSOMES:
                if name == f"{c}.b38.gmap.gz":
                    data = tf.extractfile(m).read()
                    (out_dir / name).write_bytes(data)
                    found[c] = data
    if set(found) != set(AUTOSOMES):
        raise PlanError(f"faltan mapas: {sorted(set(AUTOSOMES) - set(found))}")
    rep = {}
    for c, data in found.items():
        lines = gzip.decompress(data).decode("ascii").splitlines()
        if lines[0].split() != ["pos", "chr", "cM"]:
            raise PlanError(f"mapa {c}: cabecera {lines[0]!r}, se esperaba 'pos chr cM'")
        rows = [l.split() for l in lines[1:] if l.strip()]
        pos = [int(r[0]) for r in rows]
        cm = [float(r[2]) for r in rows]
        if any(b <= a for a, b in zip(pos, pos[1:])) or any(b < a for a, b in zip(cm, cm[1:])):
            raise PlanError(f"mapa {c}: posiciones no crecientes o cM decreciente")
        if {r[1] for r in rows} != {c[3:]}:
            raise PlanError(f"mapa {c}: columna chr inesperada {sorted({r[1] for r in rows})[:3]}")
        rep[c] = {"n": len(rows), "first": pos[0], "last": pos[-1], "cM_last": cm[-1],
                  "sha256": hashlib.sha256(data).hexdigest()}
    return rep


# ---------------------------------------------------------------- plan
def build_plan(data: Path, inventory_selection: Path) -> dict:
    """Ventanas exactas (Amendment 8): 50 de evaluación y 20 de calibración comunes a los 20 hijos,
    más las máscaras de sitio de cada hijo y su fracción enmascarada (solo descriptiva)."""
    manifest = json.loads((data / "MANIFEST.json").read_text(encoding="utf-8"))
    sel, short, n_elig = rebuild_selection(data)
    inv = json.loads(inventory_selection.read_text(encoding="utf-8"))["selection"]
    if [s["child"] for s in sel] != [s["child"] for s in inv] or             [s["C_target_n"] for s in sel] != [s["C_target_n"] for s in inv]:
        raise PlanError("la selección re-derivada no coincide con la del inventario")
    fai = {}
    for line in (data / f"ref/{M.REF_NAME}.fa.fai").read_text(encoding="ascii").splitlines():
        f = line.split("\t")
        fai[f[0]] = int(f[1])
    lengths = {c: fai[c] for c in AUTOSOMES}
    seq_ids = {name: i for i, name in enumerate(fai)}

    gaps = ucsc_bed(data / "tracks/ucsc_gap.txt.gz") + ucsc_bed(data / "tracks/ucsc_centromeres.txt.gz")
    segdups = ucsc_bed(data / "tracks/ucsc_genomicSuperDups.txt.gz")
    blacklist = bed_gz(data / "tracks/hg38-blacklist.v2.bed.gz")
    tile_excl = Intervals(gaps)
    tiles = lattice_tiles(lengths)
    order = global_order(tiles, tile_excl)
    lattice49 = evaluation_lattice(order)
    evaluation = evaluation_windows(lattice49, tile_excl)
    calibration = calibration_tiles(order)

    sv, sv_stats = trio_copy_changing(data / f"sv/{M.SV_NAME}", sel)
    masks_bed = {"gaps": bed_lines(gaps), "segdup": bed_lines(segdups), "blacklist": bed_lines(blacklist)}
    masks_bed.update({f"{c}.{k}": bed_lines(v[k]) for c, v in sv.items() for k in ("child_cc", "parent_cc")})
    children = []
    for s in sel:
        m = SiteMasks(gaps=gaps, segdup=segdups, blacklist=blacklist,
                      child_cc=sv[s["child"]]["child_cc"], parent_cc=sv[s["child"]]["parent_cc"])
        frac = {window_id(*w): {"intact": round(covered_fraction(m.phasing_intervals(), w), 6),
                                "truth": round(covered_fraction(m.truth_intervals(), w), 6)}
                for w in evaluation + calibration}
        children.append({"child": s["child"], "superpop": s["superpop"],
                         "n_child_copychange": len(m.child_cc), "n_parent_copychange": len(m.parent_cc),
                         "masked_bp_fraction_descriptive": frac})
    return {"amendment": 8, "selection": sel, "short_strata": short, "n_eligible_trios": n_elig,
            "lengths": lengths, "seq_ids": seq_ids, "n_tiles": len(tiles),
            "n_tiles_hit_by_gaps": sum(tile_excl.hits(*t) for t in tiles),
            "n_global_eligible": len(order),
            "evaluation": [window_id(*w) for w in evaluation],
            "calibration": [window_id(*w) for w in calibration],
            "bub1b_in_evaluation": evaluation[:1] == [BUB1B_WINDOW],
            "sv_stats": sv_stats, "children": children, "manifest_keys": sorted(manifest),
            "_masks_bed": masks_bed}


def compatibility(plan: dict, data: Path) -> dict:
    """Mapa, referencia vs .dict vs cabeceras CRAM, nombres de contig de .tbi. Falla fuerte."""
    rep = {"map": check_map(data / "maps/genetic_maps.b38.tar.gz", data / "maps/b38")}
    ref = reference_md5(data / f"ref/{M.REF_NAME}.fa")
    dct = dict_md5(data / f"ref/{M.REF_NAME}.dict")
    bad = [c for c in AUTOSOMES if ref.get(c) != dct.get(c)]
    if bad:
        raise PlanError(f"MD5 de referencia != .dict en {bad}")
    rep["reference_md5"] = ref
    crams = {}
    for s in plan["selection"]:
        crai = read_crai(data / f"crai/{s['child']}.final.cram.crai")
        sq, nbytes = cram_header_sq(s["cram_https"], crai[1][0])
        m5 = {q["SN"]: q.get("M5") for q in sq}
        names = [q["SN"] for q in sq]
        mism = [c for c in AUTOSOMES if m5.get(c) != ref[c]]
        if mism:
            raise PlanError(f"{s['child']}: M5 de la cabecera CRAM != referencia en {mism}")
        if names[:len(AUTOSOMES)] != list(AUTOSOMES) or \
                any(plan["seq_ids"].get(n) != i for i, n in enumerate(names)):
            raise PlanError(f"{s['child']}: orden de @SQ distinto del .fai")
        crams[s["child"]] = {"header_bytes": nbytes, "n_sq": len(sq)}
    rep["cram_headers"] = crams
    for c in AUTOSOMES:
        tbi = read_tbi(data / f"gt_index/{M.GT_NAME.format(chrom=c)}.tbi")
        if c not in tbi:
            raise PlanError(f"el .tbi de {c} no contiene el contig {c}: {sorted(tbi)[:3]}")
    return rep


def budget(plan: dict, data: Path, inventory_selection: Path) -> dict:
    """Bytes que pedirán los accesos remotos, a partir de .tbi y .crai.

    Genotipos: unión de regiones de fase (ventana ± 250 kb) de todos los hijos, una vez.
    CRAM: por hijo, sus ventanas de evaluación y calibración (sin buffer: AD solo dentro).
    """
    lengths = plan["lengths"]
    regions = set(plan["evaluation"]) | set(plan["calibration"])
    phase_regions = []
    for w in sorted(regions):
        c, rng = w.split(":")
        s, e = (int(x) for x in rng.split("-"))
        phase_regions.append(phasing_region((c, s, e), BUFFER_BP, lengths))
    tbis = {}
    gt_bytes, per_region = 0, []
    for c, s, e in phase_regions:
        if c not in tbis:
            tbis[c] = read_tbi(data / f"gt_index/{M.GT_NAME.format(chrom=c)}.tbi")
        b = tbi_region_bytes(tbis[c], c, s, e)
        gt_bytes += b
        per_region.append({"region": window_id(c, s, e), "bytes": b})
    cram_size = {i["child"]: i["cram_bytes"] for i in
                 json.loads(inventory_selection.read_text(encoding="utf-8"))["selection"]}
    cram_rows = []
    windows_all = plan["evaluation"] + plan["calibration"]
    for s in plan["selection"]:
        crai = read_crai(data / f"crai/{s['child']}.final.cram.crai")
        size = cram_size[s["child"]]
        b = 0
        for w in windows_all:
            c, rng = w.split(":")
            st, en = (int(x) for x in rng.split("-"))
            b += crai_region_bytes(crai, plan["seq_ids"][c], st, en, size)
        cram_rows.append({"child": s["child"], "windows": len(windows_all),
                          "bytes": b, "header_bytes": crai[1][0]})
    return {"n_union_windows": len(regions), "phase_regions_bp": sum(e - s + 1 for _, s, e in phase_regions),
            "gt_bytes": gt_bytes, "gt_regions": per_region, "cram": cram_rows,
            "cram_bytes": sum(r["bytes"] + r["header_bytes"] for r in cram_rows),
            "total_bytes": gt_bytes + sum(r["bytes"] + r["header_bytes"] for r in cram_rows)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="work/exp027/data")
    ap.add_argument("--selection", default="work/exp027/inventory/selection.json")
    ap.add_argument("--out", default="work/exp027/plan")
    ap.add_argument("--windows-only", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data = Path(a.data)
    plan = build_plan(data, Path(a.selection))
    beds = plan.pop("_masks_bed")
    (out / "masks").mkdir(exist_ok=True)
    for name, lines in beds.items():
        (out / "masks" / f"{name}.bed").write_text("".join(f"{l}\n" for l in lines), encoding="ascii",
                                                    newline="\n")
    (out / "plan_windows.json").write_text(json.dumps(plan, indent=2), encoding="utf-8", newline="\n")
    if a.windows_only:
        _print(plan)
        return 0
    compat = compatibility(plan, data)
    (out / "compatibility.json").write_text(json.dumps(compat, indent=2), encoding="utf-8", newline="\n")
    bud = budget(plan, data, Path(a.selection))
    (out / "budget.json").write_text(json.dumps(bud, indent=2), encoding="utf-8", newline="\n")
    _print(plan)
    print(f"ventanas únicas {bud['n_union_windows']}; fase {bud['phase_regions_bp']/1e6:.0f} Mb; "
          f"GT {bud['gt_bytes']/1e9:.1f} GB; CRAM {bud['cram_bytes']/1e9:.1f} GB; "
          f"TOTAL {bud['total_bytes']/1e9:.1f} GB")
    return 0


def _print(plan):
    print(json.dumps({k: plan[k] for k in ("n_tiles", "n_tiles_hit_by_gaps", "n_global_eligible",
                                           "bub1b_in_evaluation", "sv_stats")}, indent=1))
    print(f"evaluación {len(plan['evaluation'])} ventanas; calibración {len(plan['calibration'])} tiles (comunes)")
    for c in plan["children"]:
        fr = c["masked_bp_fraction_descriptive"][plan["evaluation"][0]]
        print(c["child"], c["superpop"], "SV copy-changing hijo", c["n_child_copychange"],
              "padres", c["n_parent_copychange"], "| frac. enmascarada ventana #1", fr)


if __name__ == "__main__":
    sys.exit(main())
