#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gates de remediacion del GO 2B: comprobaciones que las etapas 4, 5b y 5a ejecutan ANTES de
tocar al paciente, contra src/wgs/remediation_manifest.json. Todos cierran en FALLO: cualquier
comando que no termine con codigo 0, cualquier salida que no confirme lo esperado, cualquier hash
distinto -> codigo 1 y la etapa queda FAILED con motivo escrito; no corre nada.

Cada gate escribe work/callers/status/<etapa>.gate.json con lo observado, para la procedencia.

    remediation_gates.py worktree                 git status --porcelain vacio; rc=0 de git status y git rev-parse; HEAD valido
    remediation_gates.py stage4_memory            EXEC-OOM-001: objetivo local de memoria en .wslconfig, MemTotal efectivo de Docker
                                                  >= suelo, sin otros contenedores, imagen por digest (antes de stage4)
    remediation_gates.py stage4                   imagen de CNVpytor presente por DIGEST; siete recursos por sha256
    remediation_gates.py cnvpytor_startup <f> <rc>  la salida de `cnvpytor -rg_info` confirma hg38 con GC y mascara (positivo), rc=0
    remediation_gates.py stage5b                  ImageID COMPLETO de A'; 12 ficheros de biblioteca + 15 indices bwa por sha256; GENCODE
    remediation_gates.py stage5a                  imagen de SCRAMble por DIGEST; sha256 del make.vcf.R ORIGINAL observado dentro de la
                                                  imagen sin parche; sha256 del parche versionado
    remediation_gates.py image_id                 imprime el ImageID exigido de A'
    remediation_gates.py xtea_vcf_name <fam>      imprime el nombre del gVCF final que x_TEA_main escribe para esa familia
"""
from __future__ import annotations
import hashlib, io, json, os, re, subprocess, sys
from datetime import datetime, timezone

MAN = json.load(io.open("src/wgs/remediation_manifest.json", encoding="utf-8"))
S = "work/callers/status"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def sha256(p: str) -> str:
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def finish(stage: str, rec: dict, ok: bool) -> int:
    rec["result"] = "PASS" if ok else "FAIL"
    rec["checked_utc"] = now()
    os.makedirs(S, exist_ok=True)
    io.open(os.path.join(S, f"{stage}.gate.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(rec, indent=1, ensure_ascii=False))
    print(f"  gate {stage}: {rec['result']}" + ("" if ok else " · " + "; ".join(rec.get("failures", []))))
    return 0 if ok else 1


def run(cmd: list[str], timeout: int = 600):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors="replace")
    return r.returncode, r.stdout, r.stderr


# ----------------------------------------------------------------------------- worktree ----
def worktree() -> int:
    fails = []
    rc1, out1, err1 = run(["git", "status", "--porcelain"])
    rc2, out2, err2 = run(["git", "rev-parse", "HEAD"])
    head = out2.strip()
    if rc1 != 0:
        fails.append(f"git status fallo (rc={rc1}): {err1.strip()[:120]}")
    if rc2 != 0 or not HEX40.match(head):
        fails.append(f"git rev-parse HEAD fallo o no devolvio un SHA valido (rc={rc2}, '{head[:50]}')")
    dirty = [l for l in out1.splitlines() if l.strip()]
    if dirty:
        fails.append(f"arbol de trabajo sucio: {len(dirty)} entrada(s)")
    rec = {"gate": "worktree", "head": head if HEX40.match(head) else None, "git_status_rc": rc1, "git_rev_parse_rc": rc2,
           "worktree_clean": (rc1 == 0 and not dirty), "dirty_entries": dirty[:20], "failures": fails}
    return finish("worktree", rec, not fails)


# ----------------------------------------------------------------------------- imagenes -----
def image_present_by_digest(ref: str) -> tuple[bool, str | None]:
    """La referencia repo@sha256:digest tiene que resolverse localmente a una imagen cuyo RepoDigests la contenga."""
    rc, out, _ = run(["docker", "image", "inspect", "--format", "{{.Id}}|{{json .RepoDigests}}", ref])
    if rc != 0 or "|" not in out:
        return False, None
    iid, digests = out.strip().split("|", 1)
    return (ref.split("@", 1)[1] in digests), iid


# ----------------------------------------------------------------------------- stage 4 ------
def stage4() -> int:
    m = MAN["cnvpytor_stage4"]
    fails = []
    ref = m["image_by_digest"]
    present, iid = image_present_by_digest(ref)
    if not present:
        fails.append(f"imagen no presente por digest: {ref}")
    d = m["resource_dir_rel"]
    seen = {}
    for name, exp in m["resources_sha256"].items():
        p = os.path.join(d, name)
        if not os.path.exists(p):
            fails.append(f"ausente: {name}"); continue
        got = sha256(p); seen[name] = got
        if got != exp:
            fails.append(f"sha256 distinto: {name}")
    rec = {"gate": "stage4_frozen_resources", "image_by_digest": ref, "image_present": present, "image_id": iid,
           "resource_dir": d, "upstream_commit": m["upstream_commit"],
           "mount": f"{d} -> {m['mount_target']} ({m['mount_mode']})", "resources_checked": len(seen),
           "resources_expected": len(m["resources_sha256"]), "sha256_observed": seen, "failures": fails}
    return finish("4", rec, not fails and len(seen) == len(m["resources_sha256"]))


def cnvpytor_startup(path: str, rc_text: str) -> int:
    """Gate POSITIVO sobre la salida de `cnvpytor -rg_info`: rc=0, sin el error de recursos, y el bloque
    de hg38 con 'GC file specified: Yes' y 'Mask file specified: Yes' (la salida conocida del scratch)."""
    fails = []
    try:
        rc = int(rc_text)
    except ValueError:
        rc = -1
    out = io.open(path, encoding="utf-8", errors="replace").read() if os.path.exists(path) else ""
    if rc != 0:
        fails.append(f"cnvpytor -rg_info termino con rc={rc}")
    if "resource files are missing" in out:
        fails.append("CNVpytor sigue sin ver sus recursos")
    block, gc, mask = False, False, False
    for line in out.splitlines():
        if line.startswith("* "):
            block = line.strip() == "* hg38"
        elif block:
            if "GC file specified: Yes" in line: gc = True
            if "Mask file specified: Yes" in line: mask = True
    if not (gc and mask):
        fails.append("la salida no confirma hg38 con GC y mascara disponibles")
    rec = {"gate": "stage4_cnvpytor_startup", "rg_info_rc": rc, "hg38_gc_yes": gc, "hg38_mask_yes": mask,
           "resource_error_seen": "resource files are missing" in out, "failures": fails}
    return finish("4.startup", rec, not fails)


def stage4_memory() -> int:
    """EXEC-OOM-001: `cnvpytor -rd` murio por OOM (exit 137) con la VM de Docker en 30,17 GiB. Este gate comprueba la
    remediacion OPERACIONAL del host antes de la etapa 4: (1) el objetivo local de memoria configurado en ~/.wslconfig
    ([wsl2] memory=<target>), (2) el MemTotal efectivo que Docker declara, comparado en BYTES exactos contra un suelo tolerante a
    contabilidad (el GiB redondeado solo se muestra), (3) que no haya otros contenedores en marcha, (4) que la imagen de CNVpytor resuelva al digest fijado.
    El objetivo es una REMEDIACION OPERACIONAL LOCAL derivada de EXEC-OOM-001 y de la capacidad del host; no es un
    requisito publicado de CNVpytor, ni un minimo empirico de RAM, ni un parametro cientifico."""
    m = MAN["cnvpytor_stage4"]["memory_remediation"]
    fails = []
    wsl_path = os.path.expanduser(m["host_config_file"])
    configured, section, relevant_line = None, None, None
    if os.path.exists(wsl_path):
        for line in io.open(wsl_path, encoding="utf-8", errors="replace"):
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                section = s.lower()
            elif section == "[wsl2]" and s.lower().startswith("memory") and "=" in s:
                configured = s.split("=", 1)[1].strip(); relevant_line = s
    if configured is None:
        fails.append(f"{wsl_path}: sin 'memory=' en [wsl2] (WSL2 usa su configuracion por defecto)")
    elif configured.upper().replace(" ", "") != m["wsl_memory_target"].upper():
        fails.append(f"memory configurada '{configured}' distinta del objetivo '{m['wsl_memory_target']}'")
    # La desigualdad se decide en BYTES exactos; el valor en GiB redondeado es solo para mostrar.
    floor_bytes = int(m["effective_floor_gib"] * (2 ** 30))
    rc, out, err = run(["docker", "info", "--format", "{{.MemTotal}}"])
    mem_bytes = int(out.strip()) if (rc == 0 and out.strip().isdigit()) else None
    mem_gib = round(mem_bytes / 2 ** 30, 2) if mem_bytes is not None else None
    if mem_bytes is None:
        fails.append(f"docker info no devolvio MemTotal (rc={rc}): {err.strip()[:100]}")
    elif mem_bytes < floor_bytes:
        fails.append(f"MemTotal efectivo de Docker {mem_bytes} bytes ({mem_gib} GiB) por debajo del suelo "
                     f"{floor_bytes} bytes ({m['effective_floor_gib']} GiB)")
    rc, out, _ = run(["docker", "ps", "-q"])
    running = [l for l in out.split() if l]
    if rc != 0 or running:
        fails.append(f"otros contenedores en marcha: {len(running)}")
    ref = MAN["cnvpytor_stage4"]["image_by_digest"]
    present, iid = image_present_by_digest(ref)
    if not present:
        fails.append(f"imagen no presente por digest: {ref}")
    host_gib = None
    try:
        rc, out, _ = run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize"], timeout=60)
        host_gib = round(int(out.strip()) / 2 ** 20, 2) if rc == 0 and out.strip().isdigit() else None
    except Exception:
        pass
    rec = {"gate": "stage4_memory_remediation", "id": m["id"], "scope": m["scope"],
           "wsl_config_file": wsl_path, "wsl_config_present": os.path.exists(wsl_path), "wsl_relevant_line_observed": relevant_line,
           "configured_wsl_target": configured, "required_wsl_target": m["wsl_memory_target"],
           "docker_memtotal_bytes": mem_bytes, "docker_memtotal_gib": mem_gib, "effective_floor_gib": m["effective_floor_gib"],
           "effective_floor_bytes": floor_bytes, "comparison": "docker_memtotal_bytes >= effective_floor_bytes (exact bytes; GiB shown rounded)",
           "host_total_gib": host_gib, "other_running_containers": len(running), "image_by_digest": ref, "image_present": present, "image_id": iid,
           "target_semantics": m["target_semantics"], "floor_semantics": m["floor_semantics"],
           "unchanged": m["unchanged"], "gates_run_next": ["4.gate.json (recursos 7/7 por sha256, imagen por digest)", "4.startup.gate.json (-rg_info positivo)"],
           "failures": fails}
    return finish("4.memory", rec, not fails)


# ----------------------------------------------------------------------------- stage 5b -----
def stage5b() -> int:
    m = MAN["xtea_stage5b"]
    fails = []
    tag = m["env_candidate_A_prime"]["tag"]
    rc, out, _ = run(["docker", "image", "inspect", "--format", "{{.Id}}", tag])
    got_id = out.strip() if rc == 0 else None
    exp_id = m["required_image_id"]
    if got_id != exp_id:
        fails.append(f"ImageID de A' no coincide: etiqueta {tag} -> {got_id} ; exigido {exp_id}")
    lib = m["library"]["dir_rel"]
    lib_seen = {}
    for rel, exp in {**m["library"]["required_files_for_y7_sha256"], **m["library"]["consensus_bwa_index_sha256"]}.items():
        p = os.path.join(lib, rel)
        if not os.path.exists(p):
            fails.append(f"biblioteca: ausente {rel}"); continue
        got = sha256(p); lib_seen[rel] = got
        if got != exp:
            fails.append(f"biblioteca: sha256 distinto {rel}")
    g = m["gencode"]
    gp = os.path.join(g["dir_rel"], g["file"])
    g_got = sha256(gp) if os.path.exists(gp) else None
    if g_got != g["decompressed_sha256"]:
        fails.append("GENCODE: ausente o sha256 distinto")
    rec = {"gate": "stage5b_exact_image_and_resources", "image_tag": tag, "image_id_observed": got_id, "image_id_required": exp_id,
           "image_id_match": got_id == exp_id, "parent_image_id": m["env_candidate_A_prime"]["parent_image_id"],
           "gnu_sort": m["env_candidate_A_prime"]["gnu_sort"], "library_dir": lib, "library_upstream_commit": m["library"]["upstream_commit"],
           "library_files_checked": len(lib_seen), "library_files_expected": len(m["library"]["required_files_for_y7_sha256"]) + len(m["library"]["consensus_bwa_index_sha256"]),
           "gencode_sha256_observed": g_got, "failures": fails}
    return finish("5b", rec, not fails)


def xtea_vcf_name(fam: str) -> str:
    """x_TEA_main.py --gVCF escribe <prefix><sample_id>_<rep_type>.vcf, donde sample_id es el nombre del BAM sin su
    ultima extension. Aqui se reproduce esa regla para exigir EXACTAMENTE ese fichero por familia."""
    m = MAN["xtea_stage5b"]
    bam_base = m["final_vcf_rule"]["bam_basename_without_extension"]
    rep = m["final_vcf_rule"]["rep_type_by_family"][fam]
    return f"{bam_base}_{rep}.vcf"


# ----------------------------------------------------------------------------- stage 5a -----
def stage5a() -> int:
    m = MAN["scramble_stage5a"]
    fails = []
    ref = m["image_by_digest"]
    present, iid = image_present_by_digest(ref)
    if not present:
        fails.append(f"imagen no presente por digest: {ref}")
    # el ORIGINAL dentro de la imagen sin parche, observado ahora, no solo escrito en el manifest
    orig_got = None
    if present:
        rc, out, err = run(["docker", "run", "--rm", ref, "sha256sum", m["patch_target"]], timeout=300)
        orig_got = out.split()[0] if (rc == 0 and out.strip()) else None
        if orig_got != m["original_sha256"]:
            fails.append(f"make.vcf.R original en la imagen: sha256 {orig_got} distinto del exigido {m['original_sha256']}")
    p = m["patch_file_rel"]
    got = sha256(p) if os.path.exists(p) else None
    if got != m["patched_sha256"]:
        fails.append(f"parche versionado: sha256 {got} distinto del exigido {m['patched_sha256']}")
    rec = {"gate": "stage5a_image_original_and_patch", "image_by_digest": ref, "image_present": present, "image_id": iid,
           "original_sha256_observed_in_image": orig_got, "original_sha256_required": m["original_sha256"],
           "patch_file": p, "patch_sha256_observed": got, "patch_sha256_required": m["patched_sha256"],
           "patch_target": m["patch_target"], "mount_mode": m["mount_mode"], "failures": fails}
    return finish("5a", rec, not fails)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "image_id":
        print(MAN["xtea_stage5b"]["required_image_id"]); sys.exit(0)
    if cmd == "xtea_vcf_name":
        print(xtea_vcf_name(sys.argv[2])); sys.exit(0)
    if cmd == "cnvpytor_startup":
        sys.exit(cnvpytor_startup(sys.argv[2], sys.argv[3]))
    fn = {"worktree": worktree, "stage4_memory": stage4_memory, "stage4": stage4, "stage5b": stage5b, "stage5a": stage5a}.get(cmd)
    if fn is None:
        raise SystemExit("uso: remediation_gates.py worktree|stage4_memory|stage4|cnvpytor_startup <f> <rc>|stage5b|stage5a|image_id|xtea_vcf_name <fam>")
    sys.exit(fn())
