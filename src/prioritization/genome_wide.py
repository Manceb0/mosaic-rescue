#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-006 · ranking genome-wide sin panel.

Funciones importables. Ningun nombre de gen aparece en este modulo: esa es la
garantia de que el ranking no esta dirigido.

Criterios preregistrados en docs/DECISIONS.md antes de ejecutar.
"""
from __future__ import annotations
import io, gzip, collections
from dataclasses import dataclass, field

# --- la formula vive en config/ranking_v1.yaml, CONGELADO antes de mirar ---
import re as _re, hashlib as _hl, pathlib as _pl

CONFIG_PATH = "config/ranking_v1.yaml"


def config_fingerprint(path: str = CONFIG_PATH) -> str:
    """Hash del fichero de formula. Si cambia, el resultado no es comparable."""
    return _hl.sha256(_pl.Path(path).read_bytes()).hexdigest()[:16]


def _grab(txt, key, default):
    m = _re.search(rf"^\s*{key}:\s*([^
#]+)", txt, _re.M)
    if not m:
        return default
    v = m.group(1).strip()
    try:
        return float(v)
    except ValueError:
        return v


_CFG = _pl.Path(CONFIG_PATH).read_text(encoding="utf-8") if _pl.Path(CONFIG_PATH).exists() else ""
RARE_MAX_AF = _grab(_CFG, "max", 1e-3)
MIN_DP = int(_grab(_CFG, "min_dp", 10))
MIN_GQ = int(_grab(_CFG, "min_gq", 20))
AB_HET_LO, AB_HET_HI = 0.20, 0.80

# PAR1/PAR2 en GRCh38: ahi un varon SI es diploide
PAR_X = [(10001, 2781479), (155701383, 156030895)]


def is_hemizygous(loc: str, male: bool) -> bool:
    """Un 1/1 en X fuera de PAR de un varon es HEMICIGOTO, no homocigoto.
    Confundirlos convierte un solo alelo en un falso recesivo resuelto."""
    if not male:
        return False
    c, rest = loc.split(":")[0], loc.split(":")[1]
    if c == "Y":
        return True
    if c != "X":
        return False
    pos = int(rest.split("-")[0])
    return not any(lo <= pos <= hi for lo, hi in PAR_X)


@dataclass
class Variant:
    loc: str
    gene: str
    consequence: str
    impact: str
    max_af: float | None
    sift: str
    polyphen: str
    clinsig: str
    hgvsp: str
    canonical: bool
    mane: str
    gt: str = ""
    dp: int = 0
    gq: int = 0
    ad: str = ""
    filt: str = ""

    @property
    def allele_balance(self) -> float | None:
        try:
            r, a = (int(x) for x in self.ad.split(",")[:2])
            return a / (r + a) if (r + a) else None
        except (ValueError, ZeroDivisionError):
            return None

    @property
    def is_rare(self) -> bool:
        return self.max_af is None or self.max_af < RARE_MAX_AF

    @property
    def passes_quality(self) -> bool:
        if self.filt != "PASS" or self.dp < MIN_DP or self.gq < MIN_GQ:
            return False
        if self.gt == "0/1":
            ab = self.allele_balance
            return ab is not None and AB_HET_LO <= ab <= AB_HET_HI
        return True

    @property
    def is_damaging(self) -> bool:
        """HIGH siempre; MODERATE solo si al menos un predictor lo marca."""
        if self.impact == "HIGH":
            return True
        return "deleterious" in self.sift or "damaging" in self.polyphen


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load(ann_tsv: str, vcf_gz: str) -> list[Variant]:
    """Cruza la anotacion de VEP con genotipo y calidad del VCF."""
    rows, ix = [], None
    with io.open(ann_tsv, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("##"):
                continue
            if line.startswith("#"):
                h = line[1:].rstrip("\n").split("\t")
                ix = {k: i for i, k in enumerate(h)}
                continue
            p = line.rstrip("\n").split("\t")
            g = p[ix["SYMBOL"]]
            if not g or g == "-":
                continue
            rows.append(Variant(
                loc=p[ix["Location"]], gene=g,
                consequence=p[ix["Consequence"]], impact=p[ix["IMPACT"]],
                max_af=_f(p[ix["MAX_AF"]]),
                sift=p[ix["SIFT"]], polyphen=p[ix["PolyPhen"]],
                clinsig=p[ix["CLIN_SIG"]], hgvsp=p[ix["HGVSp"]],
                canonical=p[ix["CANONICAL"]] == "YES", mane=p[ix["MANE_SELECT"]]))

    want = {r.loc.split(":")[0] + ":" + r.loc.split(":")[1].split("-")[0] for r in rows}
    geno = {}
    with gzip.open(vcf_gz, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line[0] == "#":
                continue
            p = line.rstrip("\n").split("\t")
            k = f"{p[0]}:{p[1]}"
            if k not in want:
                continue
            d = dict(zip(p[8].split(":"), p[9].split(":")))
            geno[k] = (d.get("GT", "").replace("|", "/"),
                       int(d["DP"]) if d.get("DP", "").isdigit() else 0,
                       int(d["GQ"]) if d.get("GQ", "").isdigit() else 0,
                       d.get("AD", ""), p[6])
    for r in rows:
        k = r.loc.split(":")[0] + ":" + r.loc.split(":")[1].split("-")[0]
        if k in geno:
            r.gt, r.dp, r.gq, r.ad, r.filt = geno[k]
    return rows


@dataclass
class GeneCall:
    gene: str
    model: str
    n_hom: int = 0
    n_het: int = 0
    n_high: int = 0
    score: float = 0.0
    variants: list = field(default_factory=list)


def rank(rows: list[Variant], male: bool = True) -> list[GeneCall]:
    """Agrega por gen y puntua por modelo de herencia.

    Puntuacion preregistrada. No depende de ninguna lista de genes.
    """
    by_gene = collections.defaultdict(list)
    for r in rows:
        if r.is_rare and r.passes_quality and r.is_damaging:
            by_gene[r.gene].append(r)

    calls = []
    for g, vs in by_gene.items():
        hom = [v for v in vs if v.gt == "1/1"]
        het = [v for v in vs if v.gt == "0/1"]
        high = [v for v in vs if v.impact == "HIGH"]

        hemi = [v for v in hom if is_hemizygous(v.loc, male)]
        true_hom = [v for v in hom if v not in hemi]

        if hemi and not true_hom:
            # un solo alelo: NO es un recesivo resuelto
            model, base = "hemicigoto ligado a X · un solo alelo", 5.0
        elif true_hom:
            model, base = "homocigoto recesivo", 10.0
        elif len(het) >= 2:
            model, base = "recesivo compuesto CANDIDATO · fase no resuelta", 8.0
        elif high:
            model, base = "LoF heterocigoto · dominante/de novo no distinguible", 4.0
        else:
            model, base = "heterocigoto unico", 1.0

        score = base + 2.0 * len(high) + 0.5 * len(vs)
        # bonificacion solo por evidencia clinica externa, nunca por identidad del gen
        if any("pathogenic" in (v.clinsig or "").lower() and "conflicting" not in (v.clinsig or "").lower()
               for v in vs):
            score += 5.0
        calls.append(GeneCall(g, model, len(hom), len(het), len(high), score, vs))

    return sorted(calls, key=lambda c: (-c.score, c.gene))
