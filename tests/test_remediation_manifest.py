# -*- coding: utf-8 -*-
"""El manifest de remediacion del GO 2B es lo que los gates comprueban en ejecucion antes de tocar al
paciente. Estas pruebas no necesitan Docker ni datos: fijan su forma y los identificadores que el
mantenedor adjudico, para que un cambio accidental no pase en silencio."""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "src", "wgs", "remediation_manifest.json")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _load():
    return json.load(io.open(MAN, encoding="utf-8"))


def test_manifest_loads_and_has_three_stages():
    m = _load()
    assert set(m) >= {"cnvpytor_stage4", "xtea_stage5b", "scramble_stage5a"}


def test_cnvpytor_seven_resources_with_sha256():
    c = _load()["cnvpytor_stage4"]
    assert len(c["resources_sha256"]) == 7
    assert all(SHA256.match(v) for v in c["resources_sha256"].values())
    assert c["mount_mode"] == "ro" and c["upstream_commit"] == "3adc56fc6433ab8d76db1f151720cc4a4e487f20"
    assert c["image_by_digest"].startswith("quay.io/biocontainers/cnvpytor@sha256:")


def test_xtea_exact_image_id_and_required_library_files():
    x = _load()["xtea_stage5b"]
    assert x["required_image_id"] == "sha256:42da6df7f1eca858fadacf1ab623af45c74ba278600a6252906c4f843ac145c5"
    assert x["required_image_id"] == x["env_candidate_A_prime"]["image_id"]
    assert x["env_candidate_A_prime"]["parent_image_id"] == x["env_candidate_A"]["image_id"]
    assert len(x["library"]["required_files_for_y7_sha256"]) == 12
    assert len(x["library"]["consensus_bwa_index_sha256"]) == 15
    assert x["final_vcf_rule"]["expected_vcf_by_family"] == {"L1": "full_depth.markdup_LINE1.vcf", "Alu": "full_depth.markdup_ALU.vcf", "SVA": "full_depth.markdup_SVA.vcf"}
    assert x["env_candidate_A_prime"]["gnu_sort"]["foreign_runtime_libraries_added"] == 0
    assert "-x null" in x["generator_flags"] and "--xtea /usr/local/lib/" in x["generator_flags"]
    assert x["visual_steps"]["--igv --bamsnap"]["required_for_stage_success"] is False


def test_scramble_patch_hash_matches_versioned_file():
    import hashlib
    s = _load()["scramble_stage5a"]
    p = os.path.join(ROOT, s["patch_file_rel"])
    assert os.path.exists(p)
    assert hashlib.sha256(io.open(p, "rb").read()).hexdigest() == s["patched_sha256"]
    assert s["mount_mode"] == "ro"
    assert s["image_by_digest"].startswith("quay.io/biocontainers/scramble@sha256:")
