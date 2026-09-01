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
    """Lee un escalar del YAML congelado. Sin dependencias externas y sin
    expresiones regulares: parseo linea a linea, que no se puede malinterpretar."""
    needle = key + ":"
    for line in txt.splitlines():
        stripped = line.strip()
        if not stripped.startswith(needle):
            continue
        v = stripped[len(needle):].split("#", 1)[0].strip()
        if not v:
            continue
        try:
            return float(v)
        except ValueError:
            return v
    return default


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
    allele: str = ""     # ALT tal y como VEP lo representa; clave del cruce con el VCF
    gt: str = ""
    dp: int = 0
    gq: int = 0
    ad: str = ""
    filt: str = ""
    pgt: str = ""      # orientacion dentro del bloque de fase, p.ej. 0|1
    pid: str = ""      # identificador del bloque de fase read-backed

    @property
    def pos(self) -> int:
        return int(self.loc.split(":")[1].split("-")[0])

    @property
    def chrom(self) -> str:
        return self.loc.split(":")[0]

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
    def enters_ranking(self) -> bool:
        """Quien ENTRA al ranking. HIGH y MODERATE, ambos.

        CORRECCION v3. Antes esto se llamaba `is_damaging` y actuaba como filtro
        DURO: una MODERATE sin prediccion de dano desaparecia. Eso eliminaba 53
        de 135 missense raras, seis de ellas SIN NINGUN predictor disponible, en
        silencio.

        Es insostenible despues de haber demostrado en este mismo proyecto que
        SIFT y PolyPhen pueden discrepar fuertemente de un predictor calibrado.
        La prediccion MODULA la evidencia; no decide qué candidato existe.
        """
        return self.impact in ("HIGH", "MODERATE")

    @property
    def predictor_support(self) -> float:
        """Aporte de los predictores a la puntuacion. Nunca elimina.

         +1.0  ambos predictores señalan daño
         +0.5  uno de los dos
          0.0  sin prediccion disponible — NO penaliza la ausencia de dato
         -0.5  ambos lo consideran tolerado
        """
        if self.impact == "HIGH":
            return 1.0
        s_bad = "deleterious" in (self.sift or "")
        p_bad = "damaging" in (self.polyphen or "")
        s_ok = "tolerated" in (self.sift or "")
        p_ok = "benign" in (self.polyphen or "")
        if s_bad and p_bad:
            return 1.0
        if s_bad or p_bad:
            return 0.5
        if s_ok and p_ok:
            return -0.5
        return 0.0        # sin dato: no es evidencia en contra


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


CACHE_DIR = "work/cache"


def _fingerprint(ann_tsv: str, vcf_gz: str) -> str:
    """Huella de las ENTRADAS y del CODIGO que las procesa.

    Incluye el propio fichero fuente: si cambia la logica del cruce, la cache se
    invalida sola. Sin eso, una cache es una forma silenciosa de seguir usando
    un resultado obsoleto — que es peor que no tener cache.
    """
    import os
    parts = []
    for p in (ann_tsv, vcf_gz, __file__,
              os.path.join(os.path.dirname(__file__), "allele_key.py"),
              CONFIG_PATH):
        try:
            st = os.stat(p)
            parts.append(f"{os.path.basename(p)}:{st.st_size}:{int(st.st_mtime)}")
        except OSError:
            parts.append(f"{os.path.basename(p)}:missing")
    return _hl.sha256("|".join(parts).encode()).hexdigest()[:16]


def load(ann_tsv: str, vcf_gz: str, use_cache: bool = True) -> list[Variant]:
    """Cruza la anotacion de VEP con genotipo y calidad del VCF.

    CACHE. El cruce recorre el VCF entero — 5 M lineas, ~17 s — y lo llaman seis
    scripts distintos, algunos varias veces por sesion. El resultado se cachea en
    `work/cache/` con una huella de las entradas Y del codigo; si cualquiera
    cambia, se recalcula. La cache vive en work/, que esta gitignored.
    """
    import os, pickle
    if use_cache:
        fp = _fingerprint(ann_tsv, vcf_gz)
        path = os.path.join(CACHE_DIR, f"load_{fp}.pkl")
        if os.path.exists(path):
            try:
                with io.open(path, "rb") as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, EOFError, AttributeError):
                pass          # cache corrupta o de otra version: se recalcula

    rows = _load_uncached(ann_tsv, vcf_gz)

    if use_cache:
        os.makedirs(CACHE_DIR, exist_ok=True)
        tmp = path + ".tmp"
        with io.open(tmp, "wb") as f:
            pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)   # atomico: nunca deja una cache a medias
    return rows


def _load_uncached(ann_tsv: str, vcf_gz: str) -> list[Variant]:
    """El cruce real. Separado para que la cache no oculte la logica."""
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
                canonical=p[ix["CANONICAL"]] == "YES", mane=p[ix["MANE_SELECT"]],
                allele=p[ix["Allele"]] if "Allele" in ix else ""))

    # --- cruce por (Location, Allele), NO por posicion ---
    # Cruzar solo por posicion perdia 433 posiciones HIGH/MODERATE, 346 de ellas
    # indels, porque VEP desplaza la coordenada del indel respecto al VCF. Aqui
    # se reproduce la representacion exacta de VEP para cada registro del VCF.
    # Sin tolerancias: un alelo complejo se queda sin cruzar y se declara.
    from src.prioritization.allele_key import vep_location_allele

    want = {(r.loc, r.allele) for r in rows}
    want_loc = {r.loc for r in rows}
    geno = {}
    with gzip.open(vcf_gz, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line[0] == "#":
                continue
            p = line.rstrip("\n").split("\t")
            for a in p[4].split(","):
                for key in vep_location_allele(p[0], p[1], p[3], a):
                    if key in want:
                        d = dict(zip(p[8].split(":"), p[9].split(":")))
                        geno[key] = (d.get("GT", "").replace("|", "/"),
                                     int(d["DP"]) if d.get("DP", "").isdigit() else 0,
                                     int(d["GQ"]) if d.get("GQ", "").isdigit() else 0,
                                     d.get("AD", ""), p[6],
                                     d.get("PGT", ""), d.get("PID", ""))
    for r in rows:
        g = geno.get((r.loc, r.allele))
        if g:
            r.gt, r.dp, r.gq, r.ad, r.filt, r.pgt, r.pid = g
    return rows


def haplotypic_events(variants: list) -> tuple[list, dict]:
    """Colapsa variantes probadas en CIS en un solo evento haplotipico.

    MOTIVO. Varias variantes distintas y cercanas NO son automaticamente varios
    alelos de enfermedad. Caso real de este proyecto:

      33 nearby phased variants collapse into a single local haplotypic event;
      low allele balance suggests local mapping/representation complexity, but
      the cause is not established.

    Lo MEDIDO es que comparten bloque `PID` con la misma orientacion `PGT`, es
    decir que estan en cis. Llamarlo "haplotipo divergente que mapea mal" seria
    interpretacion: el balance de 0,13-0,30 lo hace sospechar, pero la causa no
    esta establecida. Para el conteo de modelos recesivos basta con lo medido.

    Reglas, en orden:
      - Mismo `PID` y mismo `PGT`  -> mismo haplotipo. UN evento.
      - Mismo `PID` y `PGT` opuesto -> haplotipos distintos. Apoya trans LOCAL.
      - Sin `PID`                   -> fase desconocida. Evento independiente,
                                       pero NUNCA cuenta como trans demostrado.
    """
    groups, singles, trans_evidence = {}, [], False
    for v in variants:
        if v.pid and v.pgt:
            groups.setdefault((v.chrom, v.pid, v.pgt), []).append(v)
        else:
            singles.append(v)

    # dos orientaciones distintas en el mismo bloque = trans demostrado localmente
    blocks = {}
    for (c, pid, pgt), vs in groups.items():
        blocks.setdefault((c, pid), set()).add(pgt)
    for k, orients in blocks.items():
        if len(orients) > 1:
            trans_evidence = True

    events = [vs for vs in groups.values()] + [[v] for v in singles]
    info = {
        "n_variants": len(variants),
        "n_events": len(events),
        "collapsed": len(variants) - len(events),
        "local_trans_proven": trans_evidence,
    }
    return events, info


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
        if r.is_rare and r.passes_quality and r.enters_ranking:
            by_gene[r.gene].append(r)

    calls = []
    for g, vs in by_gene.items():
        # colapsar cis probado ANTES de contar alelos
        events, hap = haplotypic_events(vs)
        hom = [v for v in vs if v.gt == "1/1"]
        high = [v for v in vs if v.impact == "HIGH"]
        # un evento heterocigoto = un candidato a alelo, no cada variante suelta
        het_events = [e for e in events if any(v.gt == "0/1" for v in e)]

        hemi = [v for v in hom if is_hemizygous(v.loc, male)]
        true_hom = [v for v in hom if v not in hemi]

        # CORRECCION v3. Antes se penalizaba la hemicigosis con base 5.0 por
        # "tener un solo alelo". Eso confunde dos cosas distintas:
        #   - cuantos alelos hay      -> uno, porque el varon tiene una sola X
        #   - si el modelo esta COMPLETO -> SI, para recesivo ligado a X
        # Un alelo hemicigoto en un varon es un modelo causal COMPLETO para
        # enfermedad recesiva ligada a X. No es media evidencia. Importa
        # directamente para MAGED2, que ya estaba anotado en el panel renal.
        if true_hom:
            model, base = "homocigoto recesivo · modelo completo", 10.0
        elif hemi:
            model, base = "hemicigoto ligado a X · modelo recesivo COMPLETO en varon", 10.0
        elif len(het_events) >= 2:
            if hap["local_trans_proven"]:
                model, base = "recesivo compuesto · trans LOCAL demostrado por reads", 9.0
            else:
                model, base = "recesivo compuesto CANDIDATO · fase no resuelta", 8.0
        elif len(het_events) == 1 and hap["collapsed"]:
            model, base = f"un haplotipo ({hap['n_variants']} variantes en cis)", 2.0
        elif high:
            model, base = "LoF heterocigoto · dominante/de novo no distinguible", 4.0
        else:
            model, base = "heterocigoto unico", 1.0

        score = (base
                 + 2.0 * len(high)
                 + 0.5 * len(vs)
                 + sum(v.predictor_support for v in vs))   # modula, no elimina
        # bonificacion solo por evidencia clinica externa, nunca por identidad del gen
        if any("pathogenic" in (v.clinsig or "").lower() and "conflicting" not in (v.clinsig or "").lower()
               for v in vs):
            score += 5.0
        calls.append(GeneCall(g, model, len(hom), len(het_events), len(high), score, vs))

    return sorted(calls, key=lambda c: (-c.score, c.gene))
