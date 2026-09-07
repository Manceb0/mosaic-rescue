#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base comun de las salidas de modelo AlphaGenome post-congelacion.

QUE HACE
    1. Resuelve el candidato CANONICO desde la cache congelada de AlphaGenome
       (work/alphagenome/arrays_*.json y chr*_*.json). Ninguna coordenada se
       escribe en codigo ni se recibe por linea de comandos (Regla Dura 2).
    2. Gate de ensamblado: build declarado en config/paths.yaml, longitud de
       contigs en la cabecera del VCF, y la base REF leida del FASTA GRCh38
       LOCAL de la cache de VEP (bgzf + .fai + .gzi, sin red).
    3. Escribe el manifest PRE-RUN, con sha256, ANTES de la primera llamada.
       Los parametros del manifest quedan congelados; los runners rechazan
       ejecutarse si el manifest cambio desde que se congelo.

QUE NO HACE
    No llama a la API. No elige scorer, ontologia ni ventana despues de ver un
    resultado: todo eso se declara aqui y se registra con hash.

Uso (desde la raiz del repositorio):
    python src/model_outputs/alphagenome_common.py validate
    python src/model_outputs/alphagenome_common.py freeze
"""
from __future__ import annotations
import bisect, glob, gzip, hashlib, io, json, os, struct, subprocess, sys, zlib
from datetime import datetime, timezone

sys.path.insert(0, ".")

WORK = "work/alphagenome"
MANIFEST = os.path.join(WORK, "run_manifest.json")
ISM_DIR = os.path.join(WORK, "ism")
CONTACT_DIR = os.path.join(WORK, "contacts")

# El FASTA que instalo INSTALL.pl --AUTO cf junto a la cache de VEP. Es la misma
# referencia contra la que se anoto el VCF (pasada 1), asi que validar REF aqui
# ata AlphaGenome a la misma cadena de procedencia que A0.
FASTA = "work/vep_cache/homo_sapiens/116_GRCh38/Homo_sapiens.GRCh38.dna.toplevel.fa.gz"

# Longitudes de contig que identifican GRCh38 sin ambiguedad (GRCh37 tiene
# 249 250 621 para el cromosoma 1).
GRCH38_LEN = {"1": 248956422, "15": 101991189}

MODEL_ASSEMBLY = "hg38 (GRCh38.p13)"   # lo que AlphaGenome usa para humano


# ------------------------------------------------------------- utilidades ---
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_json(obj) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "no disponible"


def api_key() -> str:
    """Clave desde .env, nunca desde codigo, CLI ni notebook."""
    for line in io.open(".env", encoding="utf-8"):
        if line.startswith("ALPHAGENOME_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("falta ALPHAGENOME_API_KEY en .env")


def write_json(path: str, obj, gz: bool = False) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if gz:
        # mtime=0 y sin nombre de fichero en la cabecera: el .gz es reproducible
        # byte a byte, asi que su sha256 significa algo.
        with io.open(path, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as f:
                f.write(data)
    else:
        io.open(path, "wb").write(data)
    return sha256_file(path)


def read_json(path: str):
    op = gzip.open if path.endswith(".gz") else io.open
    with op(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


# ------------------------------------------------------ lector bgzf + fai ---
def gzi_index(path: str):
    """Indice bgzf: lista de (offset comprimido, offset descomprimido) por bloque."""
    raw = io.open(path, "rb").read()
    n = struct.unpack("<Q", raw[:8])[0]
    pairs = [(0, 0)]
    for i in range(n):
        c, u = struct.unpack("<QQ", raw[8 + 16 * i: 24 + 16 * i])
        pairs.append((c, u))
    return pairs


def fai_index(path: str):
    out = {}
    for line in io.open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 5:
            out[p[0]] = dict(length=int(p[1]), offset=int(p[2]),
                             linebases=int(p[3]), linewidth=int(p[4]))
    return out


def bgzf_block(fh, coffset: int) -> bytes:
    fh.seek(coffset)
    head = fh.read(18)
    if len(head) < 18 or head[:2] != b"\x1f\x8b":
        raise ValueError("bloque bgzf invalido")
    bsize = struct.unpack("<H", head[16:18])[0] + 1
    fh.seek(coffset)
    block = fh.read(bsize)
    return zlib.decompress(block[18:-8], -15)


def fasta_fetch(fa_gz: str, contig: str, start1: int, end1: int) -> str:
    """Secuencia [start1, end1] 1-based inclusiva desde un FASTA bgzf indexado.

    Sin red, sin pysam, sin descomprimir el fichero entero: localiza el bloque
    con el .gzi y descomprime solo lo necesario.
    """
    fai = fai_index(fa_gz + ".fai")
    if contig not in fai:
        raise KeyError(f"contig {contig!r} no esta en el .fai")
    e = fai[contig]
    if not (1 <= start1 <= end1 <= e["length"]):
        raise ValueError("rango fuera del contig")

    def uoff(pos1):
        z = pos1 - 1
        return e["offset"] + (z // e["linebases"]) * e["linewidth"] + z % e["linebases"]

    u0, u1 = uoff(start1), uoff(end1)
    blocks = gzi_index(fa_gz + ".gzi")
    uoffs = [u for _c, u in blocks]
    i = bisect.bisect_right(uoffs, u0) - 1
    out = bytearray()
    with io.open(fa_gz, "rb") as fh:
        while True:
            c, u = blocks[i]
            data = bgzf_block(fh, c)
            lo = max(u0 - u, 0)
            hi = min(u1 - u + 1, len(data))
            out += data[lo:hi]
            if u + len(data) > u1:
                break
            i += 1
            if i >= len(blocks):
                raise ValueError("fin del fichero antes de completar el rango")
    return out.decode("ascii").replace("\n", "").replace("\r", "").upper()


# ---------------------------------------------------- candidato canonico ---
def resolve_candidate() -> dict:
    """El candidato es el que ya esta en la cache congelada. No se acepta otro."""
    arrays = sorted(glob.glob(os.path.join(WORK, "arrays_*.json")))
    summ = sorted(glob.glob(os.path.join(WORK, "chr*_*_*_*.json")))
    if len(arrays) != 1 or len(summ) != 1:
        raise SystemExit(f"se esperaba exactamente un candidato congelado en {WORK}: "
                         f"arrays={len(arrays)} resumen={len(summ)}")
    ar = read_json(arrays[0])
    sm = read_json(summ[0])
    chrom, pos = str(ar["chrom"]), int(ar["pos"])
    # "chrN:POSref>alt" en el resumen congelado
    v = sm["variant"]
    ref, alt = v.split(">")[0][-1], v.split(">")[1]
    if not v.startswith(f"{chrom}:{pos}"):
        raise SystemExit("las dos caches congeladas no describen la misma variante")
    return dict(candidate_id="frozen_nb04_alphagenome_candidate",
                chromosome=chrom, position_1based=pos, ref=ref, alt=alt,
                source_arrays=os.path.basename(arrays[0]),
                source_arrays_sha256=sha256_file(arrays[0]),
                source_summary=os.path.basename(summ[0]),
                source_summary_sha256=sha256_file(summ[0]))


# ------------------------------------------------------ gate de ensamblado ---
def assembly_gate(cand: dict) -> dict:
    """Todo lo que tiene que ser verdad ANTES de mandar nada al modelo."""
    from src.paths import get, patient_vcf

    build = str(get("reference", "build"))
    if build != "GRCh38":
        raise SystemExit(f"STOP: config/paths.yaml declara build {build!r}, no GRCh38")

    vcf = patient_vcf()
    contigs = {}
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("##contig="):
                body = line[len("##contig=<"):].rstrip(">\n")
                kv = dict(x.split("=", 1) for x in body.split(","))
                contigs[kv["ID"]] = int(kv["length"])
            elif line.startswith("#CHROM"):
                break
    plain = cand["chromosome"].replace("chr", "")
    for c, L in GRCH38_LEN.items():
        if contigs.get(c) != L:
            raise SystemExit(f"STOP: el contig {c} del VCF mide {contigs.get(c)}, "
                             f"GRCh38 exige {L}")

    if not os.path.exists(FASTA):
        raise SystemExit(f"STOP: falta el FASTA de referencia {FASTA}")
    ref_local = fasta_fetch(FASTA, plain, cand["position_1based"], cand["position_1based"])
    if ref_local != cand["ref"]:
        raise SystemExit(f"STOP: REF del candidato {cand['ref']!r} != GRCh38 {ref_local!r}")

    # identidad: la variante existe en el VCF del paciente con ese REF/ALT
    found = False
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.split("\t", 5)
            if p[0] == plain and int(p[1]) == cand["position_1based"]:
                found = (p[3] == cand["ref"] and cand["alt"] in p[4].split(","))
                break
            if p[0] == plain and int(p[1]) > cand["position_1based"]:
                break
    if not found:
        raise SystemExit("STOP: el candidato no aparece en el VCF con ese REF/ALT")

    return dict(source_assembly="GRCh38", model_assembly=MODEL_ASSEMBLY,
                assembly_evidence=f"config/paths.yaml reference.build + contig lengths "
                                  f"{GRCH38_LEN}", vcf_sha256=sha256_file(vcf),
                fasta=FASTA, fasta_provenance="work/vep_cache_provenance.txt",
                ref_validation="PASS", ref_from_fasta=ref_local,
                variant_in_vcf="PASS", liftover="not_needed",
                chromosome_naming=dict(vcf=plain, model=cand["chromosome"], fasta=plain))


# ----------------------------------------------------------- manifest ---
def build_manifest() -> dict:
    """Los parametros congelados. Cambiarlos DESPUES de ver un resultado es lo
    que este fichero existe para impedir."""
    cand = resolve_candidate()
    gate = assembly_gate(cand)
    from src.structure.transcript_model import fetch
    tx = fetch()   # cache local work/struct/transcript.json; sin datos del paciente
    return {
        "run_id": "alphagenome_postfreeze_ism_contacts",
        "purpose": ("post-freeze model-output characterization of the frozen notebook-04 "
                    "AlphaGenome candidate. NOT new evidence, NOT validation."),
        "frozen_at_utc": now_utc(),
        "git_commit": git_commit(),
        "candidate": cand,
        "assembly_gate": gate,
        "transcript_context": {"transcript": tx["transcript"], "release": tx["release"],
                               "source": "work/struct/transcript.json (Ensembl REST, gene symbol only)"},
        "model": {"name": "AlphaGenome", "access": "API", "organism": "HOMO_SAPIENS",
                  "model_version_requested": None,
                  "model_version_note": "None = server default; the SDK exposes folds "
                                        "ALL_FOLDS/FOLD_0..3 but the served build is not "
                                        "returned by the API"},
        "ism": {
            "sequence_context_bp": 16384,
            "ism_window_bp": 256,
            "expected_variants": 256 * 3,
            "sensitivity_check": {"sequence_context_bp": 131072,
                                  "rule": "same window, same scorers, same ontology; "
                                          "reported, never used to replace the primary"},
            "scorers": [
                {"role": "PRIMARY", "output": "SPLICE_SITES", "scorer": "CenterMaskScorer",
                 "width": 2001, "aggregation": "DIFF_MEAN",
                 "ontology_curie": None,
                 "scalar_rule": "of the 4 splice-site tracks (donor/acceptor x strand), "
                                "keep the signed score of the track with the largest |score|",
                 "reason": "splicing is the modality that decided the frozen hypothesis "
                           "(fig04 main); CenterMask is the documented ISM path; 2001 bp "
                           "is the smallest supported width covering the splice neighbourhood"},
                {"role": "SECONDARY", "output": "DNASE", "scorer": "CenterMaskScorer",
                 "width": 501, "aggregation": "DIFF_MEAN",
                 "ontology_curie": "CL:0001059",
                 "scalar_rule": "single predeclared track",
                 "reason": "accessibility is the supplementary modality of the frozen "
                           "block (fig04S); the track is the DNase track already frozen "
                           "in work/alphagenome/arrays_*.json by the base>=0.01 rule"},
            ],
            "interpretation_rule": {
                "concentrated": "candidate position ranks in the top 5 % (<=13 of 256) "
                                "by max |centered score| under the PRIMARY scorer",
                "otherwise": "no compelling local ISM sensitivity under the pre-specified "
                             "readout",
                "context_sensitive": "Pearson r between the 16 kb and 100 kb matrices < 0.8",
            },
        },
        "contacts": {
            "sequence_context_bp": 1048576,
            "output": "CONTACT_MAPS", "resolution_bp": 2048,
            "ontology_curie": "CL:0002620", "biosample_name": "skin fibroblast",
            "biosample_reason": "primary (non-immortalised) fibroblast: the cell type in "
                                "which PCS/MVA patient functional studies are performed; "
                                "not a cancer line, not embryonic, not lymphoid. Chosen "
                                "from the 28 available tracks BEFORE any prediction",
            "robustness": "ContactMapScorer (official) on all 28 contact tracks, reported "
                          "as a distribution; never used to pick the displayed track",
            "interpretation_rule": {
                "visible": "max |ALT-REF| >= 5 % of max REF contact value in the map",
                "otherwise": "no compelling predicted contact effect",
            },
        },
        "forbidden_interpretations": [
            "pathogenic", "functional validation", "regulatory mechanism proven",
            "patient-specific chromatin state", "alters Track 1 ranking",
            "alters ACMG classification", "reopens Track 2",
        ],
        "random_seed": None,
        "deterministic_inference": True,
    }


def freeze() -> dict:
    if os.path.exists(MANIFEST):
        raise SystemExit(f"{MANIFEST} ya existe. Un manifest congelado no se reescribe; "
                         "borralo A PROPOSITO si quieres repetir el preregistro")
    m = build_manifest()
    sha = write_json(MANIFEST, m)
    io.open(MANIFEST + ".sha256", "w").write(sha + "\n")
    return m


def load_manifest() -> dict:
    """El manifest, comprobando que nadie lo toco desde que se congelo."""
    if not os.path.exists(MANIFEST):
        raise SystemExit("no hay manifest congelado: ejecuta primero `alphagenome_common.py freeze`")
    want = io.open(MANIFEST + ".sha256").read().strip()
    got = sha256_file(MANIFEST)
    if want != got:
        raise SystemExit("el manifest cambio despues de congelarse; se rechaza la corrida")
    return read_json(MANIFEST)


def environment() -> dict:
    import platform
    import numpy
    out = {"python": platform.python_version(), "numpy": numpy.__version__,
           "platform": platform.platform(), "git_commit": git_commit()}
    try:
        import alphagenome
        out["alphagenome_sdk"] = getattr(alphagenome, "__version__", "unknown")
    except Exception:
        out["alphagenome_sdk"] = "not importable in this interpreter"
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        c = resolve_candidate()
        g = assembly_gate(c)
        print(f"  candidato   : {c['candidate_id']} (REF/ALT {c['ref']}>{c['alt']}, "
              f"coordenada no impresa)")
        print(f"  ensamblado  : {g['source_assembly']} -> modelo {g['model_assembly']}")
        print(f"  REF en FASTA: {g['ref_validation']}   variante en VCF: {g['variant_in_vcf']}")
    elif cmd == "freeze":
        m = freeze()
        print(f"  manifest congelado: {MANIFEST}")
        print(f"  sha256            : {io.open(MANIFEST + '.sha256').read().strip()}")
        print(f"  git               : {m['git_commit'][:12]}")
        print(f"  ISM               : {m['ism']['ism_window_bp']} bp x 3 en "
              f"{m['ism']['sequence_context_bp']:,} bp; scorers "
              f"{[s['output'] for s in m['ism']['scorers']]}")
        print(f"  contactos         : {m['contacts']['biosample_name']} "
              f"({m['contacts']['ontology_curie']}), {m['contacts']['sequence_context_bp']:,} bp")
    else:
        raise SystemExit("uso: validate | freeze")
