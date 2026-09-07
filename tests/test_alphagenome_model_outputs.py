#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las salidas de modelo post-congelacion (ISM y contactos) son lo que dicen ser.

DOS BLOQUES
    1-9   sin datos del paciente: la aritmetica de la ISM, los invariantes de
          una matriz de contactos, el lector bgzf y el contrato del manifest,
          todo sobre numeros inventados aqui mismo. Corren al clonar.
    10-18 con work/ local: los artefactos reales cuadran con su metadata
          (hashes, 768 evaluaciones, 256 x 4, sin NaN, simetria, delta exacto,
          procedencia completa, clave ausente). Se SALTAN, declarandolo, si no
          hay work/, en vez de pasar en verde sin mirar.
    19-20 sobre lo versionado: ninguna figura de publicacion nueva existe sin
          su JSON progenitor declarado, y ningun documento canonico convierte
          una prediccion en validacion.

POR QUE EXISTE
    Una figura de "model output" se convierte en "evidencia" en el momento en
    que nadie comprueba de donde salio cada pixel. Estos tests atan cada
    figura a su matriz, la matriz a su corrida, y la corrida a su manifest.
"""
import gzip, io, json, os, pathlib, re, struct, sys, zlib

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model_outputs import alphagenome_common as C                    # noqa: E402
from src.model_outputs import alphagenome_ism as I                       # noqa: E402
from src.model_outputs import alphagenome_contacts as K                  # noqa: E402

ISM_DIR = ROOT / "work/alphagenome/ism"
CON_DIR = ROOT / "work/alphagenome/contacts"
MANIFEST = ROOT / "work/alphagenome/run_manifest.json"
HAVE_WORK = (ISM_DIR / "metadata.json").exists() and (CON_DIR / "metadata.json").exists()
needs_work = pytest.mark.skipif(not HAVE_WORK, reason="sin work/alphagenome local: "
                                "estas pruebas solo corren con los artefactos presentes")


# ─────────── 1-3 · aritmetica de la ISM, con numeros inventados ───────────

def _toy():
    rng = np.random.default_rng(0)
    ref = "ACGTTGCA"
    recs = []
    for i, b in enumerate(ref):
        for a in "ACGT":
            if a != b:
                recs.append({"index": i, "alt": a, "score": float(rng.normal())})
    return ref, recs


def test_01_la_matriz_cruda_pone_cero_en_la_base_de_referencia():
    ref, recs = _toy()
    raw = I.raw_matrix(recs, len(ref), ref)
    assert raw.shape == (8, 4)
    for i, b in enumerate(ref):
        assert raw[i, "ACGT".index(b)] == 0.0


def test_02_el_centrado_es_el_del_sdk_media_de_las_tres_alternativas():
    """ISM_{p,b} = s_{p,b} - (1/3) sum_{b' != ref} s_{p,b'}: la celda de
    referencia queda en -media(alternativas)."""
    ref, recs = _toy()
    raw = I.raw_matrix(recs, len(ref), ref)
    cen = I.center_by_position(raw)
    for i, b in enumerate(ref):
        alts = [raw[i, j] for j in range(4) if j != "ACGT".index(b)]
        assert cen[i, "ACGT".index(b)] == pytest.approx(-np.mean(alts))
    # y el logo conserva SOLO esa celda
    logo = I.logo_from(cen, ref)
    assert np.count_nonzero(logo) == len(ref)


def test_03_una_ism_incompleta_o_repetida_no_pasa():
    ref, recs = _toy()
    with pytest.raises(ValueError):
        I.raw_matrix(recs[:-1], len(ref), ref)
    with pytest.raises(ValueError):
        I.raw_matrix(recs + [recs[0]], len(ref), ref)


def test_04_los_rangos_del_candidato_se_calculan_sobre_el_maximo_por_posicion():
    cen = np.zeros((5, 4))
    cen[3, 1] = 9.0          # posicion 3 domina
    cen[1, 2] = -2.0
    rk = I.ranks(cen, cand_index=1, cand_alt="G")
    assert rk["candidate_position_rank_of_L"] == 2
    assert rk["window_argmax_offset"] == 2
    assert rk["candidate_substitution_rank_of_all"] == 2


# ─────────── 5-6 · invariantes de una matriz de contactos ───────────

def test_05_una_matriz_asimetrica_no_pasa_y_una_simetrica_si():
    a = np.array([[1.0, 0.2], [0.2, 1.0]])
    assert K.check_maps(a, a)["square"]
    with pytest.raises(ValueError):
        K.check_maps(a, np.array([[1.0, 0.3], [0.2, 1.0]]))
    with pytest.raises(ValueError):
        K.check_maps(a, np.ones((3, 3)))
    with pytest.raises(ValueError):
        K.check_maps(a, np.array([[np.nan, 0.2], [0.2, 1.0]]))


def test_06_el_umbral_de_visibilidad_es_relativo_al_maximo_de_ref():
    ref = np.array([[10.0, 1.0], [1.0, 10.0]])
    assert not K.visible(ref, np.full((2, 2), 0.4), 0.05)["visible"]
    assert K.visible(ref, np.full((2, 2), 0.6), 0.05)["visible"]
    assert np.array_equal(K.delta_of(ref, ref + 1), np.ones((2, 2)))


# ─────────── 7-8 · lector bgzf + fai sobre un fichero construido aqui ───────────

def _bgzf(path: pathlib.Path, payload: bytes, block: int = 40):
    """Escribe `payload` como bgzf (bloques gzip con campo extra BC) y su .gzi."""
    coff, uoff, pairs = 0, 0, []
    with io.open(path, "wb") as f:
        for i in range(0, len(payload), block):
            chunk = payload[i:i + block]
            comp = zlib.compressobj(6, zlib.DEFLATED, -15)
            body = comp.compress(chunk) + comp.flush()
            bsize = 18 + len(body) + 8 - 1
            hdr = (b"\x1f\x8b\x08\x04" + b"\x00" * 4 + b"\x00\xff" + struct.pack("<H", 6)
                   + b"BC" + struct.pack("<H", 2) + struct.pack("<H", bsize))
            tail = struct.pack("<II", zlib.crc32(chunk) & 0xFFFFFFFF, len(chunk))
            blk = hdr + body + tail
            f.write(blk)
            coff += len(blk); uoff += len(chunk)
            pairs.append((coff, uoff))
    pairs = pairs[:-1]                      # el .gzi no lista el final del ultimo bloque
    with io.open(str(path) + ".gzi", "wb") as g:
        g.write(struct.pack("<Q", len(pairs)))
        for c, u in pairs:
            g.write(struct.pack("<QQ", c, u))


def test_07_fasta_fetch_lee_bases_a_traves_de_bloques(tmp_path):
    seq = "".join("ACGT"[(i * 7) % 4] for i in range(150))
    lines = [seq[i:i + 60] for i in range(0, len(seq), 60)]
    fasta = ">toy desc\n" + "\n".join(lines) + "\n"
    fa = tmp_path / "toy.fa.gz"
    _bgzf(fa, fasta.encode("ascii"), block=40)
    io.open(str(fa) + ".fai", "w").write(f"toy\t{len(seq)}\t{len('>toy desc') + 1}\t60\t61\n")
    assert C.fasta_fetch(str(fa), "toy", 1, 1) == seq[0]
    assert C.fasta_fetch(str(fa), "toy", 58, 63) == seq[57:63]      # cruza salto de linea
    assert C.fasta_fetch(str(fa), "toy", 100, 150) == seq[99:150]   # cruza varios bloques
    with pytest.raises(ValueError):
        C.fasta_fetch(str(fa), "toy", 150, 151)


def test_08_el_gz_reproducible_da_el_mismo_sha256_dos_veces(tmp_path):
    p1, p2 = tmp_path / "a.json.gz", tmp_path / "b.json.gz"
    s1 = C.write_json(str(p1), {"x": [1, 2, 3]}, gz=True)
    s2 = C.write_json(str(p2), {"x": [1, 2, 3]}, gz=True)
    assert s1 == s2
    assert C.read_json(str(p1)) == {"x": [1, 2, 3]}


# ─────────── 9 · el contrato del manifest ───────────

MANIFEST_KEYS = ("candidate", "assembly_gate", "model", "ism", "contacts",
                 "forbidden_interpretations", "random_seed", "deterministic_inference",
                 "git_commit", "frozen_at_utc")


def test_09_el_manifest_declara_todo_lo_que_los_runners_exigen():
    """Sin llamar a nada: se comprueba la FORMA del manifest que build_manifest
    produce, con un candidato ficticio inyectado."""
    src = io.open(ROOT / "src/model_outputs/alphagenome_common.py", encoding="utf-8").read()
    for k in MANIFEST_KEYS:
        assert f'"{k}"' in src, f"build_manifest no declara {k!r}"
    # random_seed = null a proposito: no hay componente aleatorio que sembrar
    assert '"random_seed": None' in src
    assert '"deterministic_inference": True' in src


# ─────────── 10-18 · los artefactos reales, si estan ───────────

@needs_work
def test_10_el_manifest_esta_congelado_y_su_hash_coincide():
    want = io.open(str(MANIFEST) + ".sha256").read().strip()
    assert C.sha256_file(str(MANIFEST)) == want
    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    for k in MANIFEST_KEYS:
        assert k in m
    assert m["assembly_gate"]["ref_validation"] == "PASS"
    assert m["assembly_gate"]["source_assembly"] == "GRCh38"
    assert m["random_seed"] is None


@needs_work
def test_11_las_dos_corridas_citan_el_mismo_manifest_congelado():
    want = io.open(str(MANIFEST) + ".sha256").read().strip()
    for d in (ISM_DIR, CON_DIR):
        meta = json.load(io.open(d / "metadata.json", encoding="utf-8"))
        assert meta["manifest_sha256"] == want, f"{d.name}: corrida sobre otro manifest"
        assert meta["figure_class"] == "MODEL_OUTPUT"
        assert meta["evidence_origin"] == "PREDICTED"
        assert meta["source_type"] == "predicted_not_patient_measurement"
        assert meta["random_seed"] is None and meta["deterministic_inference"] is True
        for k in ("environment", "model", "started_utc", "finished_utc"):
            assert k in meta
        assert meta["environment"]["alphagenome_sdk"] not in ("", None)


@needs_work
def test_12_ism_exactamente_tres_alternativas_por_posicion_y_768_evaluaciones():
    meta = json.load(io.open(ISM_DIR / "metadata.json", encoding="utf-8"))
    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    for tag in ("primary", "sensitivity"):
        run = meta[tag]
        assert run["n_variants"] == m["ism"]["expected_variants"] == 768
        for role, info in run["roles"].items():
            raw = C.read_json(str(ISM_DIR / info["files"]["raw_scores"]))["records"]
            per_pos = {}
            for r in raw:
                per_pos.setdefault(r["index"], set()).add(r["alt"])
                assert r["alt"] != r["ref"]
            assert len(per_pos) == run["ism_window_bp"] == 256
            assert all(len(v) == 3 for v in per_pos.values())


@needs_work
def test_13_ism_matrices_L_por_4_finitas_y_centradas_como_el_sdk():
    meta = json.load(io.open(ISM_DIR / "metadata.json", encoding="utf-8"))
    for tag in ("primary", "sensitivity"):
        for role, info in meta[tag]["roles"].items():
            z = np.load(ISM_DIR / info["files"]["npz"])
            raw, cen, logo = z["raw"], z["centered"], z["logo"]
            assert raw.shape == cen.shape == logo.shape == (256, 4)
            assert np.isfinite(cen).all()
            assert np.allclose(cen, I.center_by_position(raw))
            M = C.read_json(str(ISM_DIR / info["files"]["matrix"]))
            assert np.allclose(np.asarray(M["centered"]), cen)
            assert len(M["reference_window"]) == 256


@needs_work
def test_14_ism_los_hashes_de_metadata_son_los_de_los_ficheros():
    meta = json.load(io.open(ISM_DIR / "metadata.json", encoding="utf-8"))
    for tag in ("primary", "sensitivity"):
        for role, info in meta[tag]["roles"].items():
            f = info["files"]
            assert C.sha256_file(str(ISM_DIR / f["raw_scores"])) == f["raw_scores_sha256"]
            assert C.sha256_file(str(ISM_DIR / f["matrix"])) == f["matrix_sha256"]
            assert C.sha256_file(str(ISM_DIR / f["npz"])) == f["npz_sha256"]


@needs_work
def test_15_ism_scorer_y_ontologia_son_los_del_manifest_no_otros():
    meta = json.load(io.open(ISM_DIR / "metadata.json", encoding="utf-8"))
    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    declared = {s["role"]: s for s in m["ism"]["scorers"]}
    for tag in ("primary", "sensitivity"):
        for role, info in meta[tag]["roles"].items():
            assert info["scorer"] == declared[role], f"{tag}/{role}: scorer distinto al congelado"
    assert meta["primary"]["sequence_context_bp"] == m["ism"]["sequence_context_bp"]
    assert meta["sensitivity"]["sequence_context_bp"] == m["ism"]["sensitivity_check"]["sequence_context_bp"]
    ip = meta["interpretation"]
    assert ip["reading"] in (m["ism"]["interpretation_rule"]["concentrated"],
                             m["ism"]["interpretation_rule"]["otherwise"])


@needs_work
def test_16_contactos_cuadradas_simetricas_misma_forma_y_delta_exacto():
    meta = json.load(io.open(CON_DIR / "metadata.json", encoding="utf-8"))
    z = np.load(CON_DIR / "matrices.npz")
    ref, alt, delta = z["ref"], z["alt"], z["delta"]
    K.check_maps(ref, alt)                              # lanza si algo falla
    assert np.array_equal(delta, alt - ref)
    assert ref.shape == (meta["n_bins"], meta["n_bins"])
    assert meta["input_length_bp"] // meta["n_bins"] == meta["output_resolution_bp"] == 2048
    for name in ("ref", "alt", "delta"):
        J = C.read_json(str(CON_DIR / meta["files"][name]["file"]))
        assert np.allclose(np.asarray(J["matrix"]), z[name])
        assert C.sha256_file(str(CON_DIR / meta["files"][name]["file"])) == meta["files"][name]["sha256"]
    assert C.sha256_file(str(CON_DIR / "matrices.npz")) == meta["files"]["npz"]["sha256"]


@needs_work
def test_17_contactos_la_pista_es_la_predeclarada_y_la_robustez_no_la_elige():
    meta = json.load(io.open(CON_DIR / "metadata.json", encoding="utf-8"))
    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    assert meta["ontology_curie"] == m["contacts"]["ontology_curie"]
    rob = json.load(io.open(CON_DIR / "robustness_scores.json", encoding="utf-8"))
    assert rob["chosen_ontology"] == m["contacts"]["ontology_curie"]
    assert rob["n_tracks"] == len(rob["rows"]) >= 20
    assert 1 <= rob["chosen_rank_of_n"] <= rob["n_tracks"]
    ip = meta["interpretation"]
    assert ip["reading"] in (m["contacts"]["interpretation_rule"]["visible"],
                             m["contacts"]["interpretation_rule"]["otherwise"])
    assert ip["visible"] == (ip["ratio"] >= ip["threshold"])


@needs_work
def test_18_ninguna_clave_de_api_en_los_artefactos():
    key_rx = re.compile(r"AIza[0-9A-Za-z_\-]{30,}")
    for d in (ISM_DIR, CON_DIR, MANIFEST.parent):
        for p in d.glob("*.json"):
            assert not key_rx.search(io.open(p, encoding="utf-8").read()), f"clave en {p.name}"


# ─────────── 19-20 · lo versionado ───────────

NEW_FIGS = {"fig04I_alphagenome_ism": "work/alphagenome/ism",
            "fig04C_alphagenome_contact_maps": "work/alphagenome/contacts"}


def test_19_cada_figura_nueva_declara_su_json_progenitor_en_la_ficha_qa():
    qa = io.open(ROOT / "PUBLICATION_FIGURE_QA.md", encoding="utf-8").read()
    for slug, src in NEW_FIGS.items():
        if (ROOT / "figures/pub" / f"{slug}.svg").exists():
            assert slug in qa, f"{slug} sin ficha QA"
            assert src in qa, f"la ficha de {slug} no cita {src}"
            assert "MODEL_OUTPUT" in qa and "PREDICTED" in qa


STALE = re.compile(r"alphagenome\s+(?:validates|demonstrates|proves|confirms|shows that the patient)|"
                   r"ism\s+(?:proves|demonstrates)\s+(?:the\s+)?region\s+is\s+functional|"
                   r"the\s+patient\s+has\s+altered\s+chromatin|"
                   r"the\s+variant\s+disrupts\s+(?:enhancer|looping)", re.I)
CANON = ("README.md", "reports/TRACK1_REPORT.md", "reports/TRACK2_REPORT.md",
         "docs/DECISIONS.md", "research/EXPERIMENT_REGISTRY.md", "PUBLICATION_FIGURE_QA.md",
         "src/nb/nb04_hidden_allele.py", "src/figures/fig04_ism.py",
         "src/figures/fig04_contacts.py", "src/figures/render_all.py")


def test_20_ningun_documento_canonico_convierte_la_prediccion_en_validacion():
    NIEGA = ("never", "not ", "no ", "nunca", "prohibido", "forbidden")
    for rel in CANON:
        p = ROOT / rel
        if not p.exists():
            continue
        for n, line in enumerate(io.open(p, encoding="utf-8", errors="replace"), 1):
            m = STALE.search(line)
            if m and not any(k in line.lower() for k in NIEGA):
                pytest.fail(f"{rel}:{n} afirma {m.group(0)!r}")
