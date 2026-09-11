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


def test_cnvpytor_memory_remediation_is_operational_not_scientific():
    c = _load()["cnvpytor_stage4"]["memory_remediation"]
    assert c["id"] == "EXEC-OOM-001" and c["scope"] == "operational environment only"
    assert c["wsl_memory_target"] == "48GB" and c["effective_floor_gib"] == 47
    assert c["host_config_committed"] is False and c["wsl_shutdown_required"] is True
    assert "NOT a CNVpytor published requirement" in c["target_semantics"]
    assert "not a biological/tool requirement" in c["floor_semantics"]
    assert c["observed_failure"]["container_exit_code"] == 137
    assert "CNVpytor command" in c["unchanged"] and "-rd parallelism (8 cores, tool default)" in c["unchanged"]


def _gates_module(monkeypatch, tmp_path):
    """Carga src/wgs/remediation_gates.py aislado: el manifest se lee desde ROOT y los gate.json van a un directorio temporal,
    nunca al status/ vivo de una corrida."""
    import importlib.util
    monkeypatch.chdir(ROOT)
    spec = importlib.util.spec_from_file_location("remediation_gates_under_test", os.path.join(ROOT, "src", "wgs", "remediation_gates.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.S = str(tmp_path / "status")
    return mod


def _memory_env(mod, monkeypatch, tmp_path, memtotal_bytes):
    """Todo en PASS salvo el MemTotal: .wslconfig con 48GB, cero contenedores, imagen presente por digest. Ningun docker real."""
    wsl = tmp_path / ".wslconfig"
    wsl.write_text("[wsl2]\nmemory=48GB\n", encoding="utf-8")
    monkeypatch.setattr(mod.os.path, "expanduser", lambda path: str(wsl))

    def fake_run(cmd, timeout=600):
        if cmd[:2] == ["docker", "info"]:
            return 0, f"{memtotal_bytes}\n", ""
        if cmd[:2] == ["docker", "ps"]:
            return 0, "", ""
        if cmd[0] == "powershell":
            return 0, "64606720\n", ""
        raise AssertionError(f"comando inesperado en el test: {cmd}")

    monkeypatch.setattr(mod, "run", fake_run)
    monkeypatch.setattr(mod, "image_present_by_digest", lambda ref: (True, "sha256:test-image-id"))


def test_stage4_memory_gate_decides_on_exact_bytes_at_the_floor(monkeypatch, tmp_path):
    mod = _gates_module(monkeypatch, tmp_path)
    floor = int(47 * (2 ** 30))
    assert floor == 50465865728
    # suelo - 1: 46,999999999... GiB redondea a 47.0 pero NO puede pasar
    _memory_env(mod, monkeypatch, tmp_path, floor - 1)
    assert mod.stage4_memory() == 1
    rec = json.load(io.open(tmp_path / "status" / "4.memory.gate.json", encoding="utf-8"))
    assert rec["result"] == "FAIL"
    assert rec["docker_memtotal_bytes"] == floor - 1 and rec["effective_floor_bytes"] == floor
    assert rec["docker_memtotal_gib"] == 47.0
    assert any("por debajo del suelo" in f for f in rec["failures"]) and len(rec["failures"]) == 1
    # suelo exacto: PASS
    _memory_env(mod, monkeypatch, tmp_path, floor)
    assert mod.stage4_memory() == 0
    rec = json.load(io.open(tmp_path / "status" / "4.memory.gate.json", encoding="utf-8"))
    assert rec["result"] == "PASS" and rec["failures"] == []
    assert rec["docker_memtotal_bytes"] == floor and rec["configured_wsl_target"] == "48GB"
    assert rec["other_running_containers"] == 0 and rec["image_present"] is True
