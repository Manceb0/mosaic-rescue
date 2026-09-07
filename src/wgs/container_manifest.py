#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manifest de contenedores del alineamiento: tag + digest inmutable + version reportada.

POR QUE
    Un tag puede cambiar de contenido en el registro. El identificador
    reproducible es el DIGEST del manifest (sha256 inmutable). Aqui se
    registran, para cada herramienta: registro/repositorio, tag, digest del
    indice multi-arquitectura, digest de la imagen linux/amd64 y, cuando la
    imagen ya se ha descargado, la version que la propia herramienta reporta.

    `resolve` no descarga capas: `docker manifest inspect` solo lee metadatos.
    `versions` si necesita las imagenes locales (se ejecuta tras el GO de
    descarga) y rellena tool_reported_version.

Uso:
    python src/wgs/container_manifest.py resolve     # sin descargas
    python src/wgs/container_manifest.py versions    # tras `docker pull`
Salida: work/align/containers.json
"""
from __future__ import annotations
import io, json, os, subprocess, sys

OUT = "work/align/containers.json"

IMAGES = [
    ("bwa",       "quay.io/biocontainers/bwa",       "0.7.18--he4a0461_0",   ["bwa"]),
    ("samtools",  "quay.io/biocontainers/samtools",  "1.21--h50ea8bc_0",     ["samtools", "--version"]),
    ("manta",     "quay.io/biocontainers/manta",     "1.6.0--h9ee0642_2",    ["configManta.py", "--version"]),
    ("delly",     "quay.io/biocontainers/delly",     "1.3.3--h4d20210_1",    ["delly", "--version"]),
    ("cnvpytor",  "quay.io/biocontainers/cnvpytor",  "1.3.2--pyhdfd78af_0",  ["cnvpytor", "-version"]),
    ("mosdepth",  "quay.io/biocontainers/mosdepth",  "0.3.10--h4e814b3_1",   ["mosdepth", "--version"]),
    ("bedtools",  "quay.io/biocontainers/bedtools",  "2.31.1--hf5e1c6e_2",   ["bedtools", "--version"]),
    # v5: alcance cientifico WGS
    ("bcftools",  "quay.io/biocontainers/bcftools",  "1.21--h8b25389_0",     ["bcftools", "--version"]),
    ("verifybamid2", "quay.io/biocontainers/verifybamid2", "2.0.3--hc004090_0", ["verifybamid2", "--help"]),
    ("expansionhunter", "quay.io/biocontainers/expansionhunter", "5.0.0--hf366f20_1", ["ExpansionHunter", "--version"]),
    ("xtea",      "quay.io/biocontainers/xtea",      "0.1.9--hdfd78af_0",    ["xtea", "--help"]),
    ("scramble",  "quay.io/biocontainers/scramble",  "1.0.2--hec16e2b_0",    ["cluster_identifier", "--help"]),
]


def _run(cmd, timeout=120):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def resolve() -> dict:
    from datetime import datetime, timezone
    out = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "note": "digests read from the registry manifest; no layers downloaded", "images": {}}
    for name, repo, tag, _cmd in IMAGES:
        ref = f"{repo}:{tag}"
        code, txt = _run(["docker", "manifest", "inspect", "-v", ref])
        entry = {"registry_repository": repo, "tag": tag, "index_digest": None,
                 "amd64_digest": None, "tool_reported_version": "to be recorded after pull"}
        if code == 0:
            try:
                d = json.loads(txt)
                items = d if isinstance(d, list) else [d]
                for it in items:
                    plat = it.get("Descriptor", {}).get("platform", {})
                    dig = it.get("Descriptor", {}).get("digest")
                    if plat.get("architecture") == "amd64" and plat.get("os") == "linux":
                        entry["amd64_digest"] = dig
                    if entry["amd64_digest"] is None and dig:
                        entry["amd64_digest"] = dig
                code2, txt2 = _run(["docker", "manifest", "inspect", ref])
                if code2 == 0:
                    import hashlib
                    # digest del indice = sha256 del manifest canonico devuelto
                    entry["index_digest"] = "sha256:" + hashlib.sha256(txt2.encode("utf-8")).hexdigest()
                    entry["index_digest_note"] = ("computed from the manifest bytes returned by "
                                                  "`docker manifest inspect`; the amd64 digest is the "
                                                  "descriptor digest reported by the registry")
            except Exception as e:                          # noqa: BLE001
                entry["error"] = f"{type(e).__name__}: {e}"[:120]
        else:
            entry["error"] = txt.strip()[:160]
        out["images"][name] = entry
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return out


def versions() -> dict:
    d = json.load(io.open(OUT, encoding="utf-8"))
    for name, repo, tag, cmd in IMAGES:
        code, txt = _run(["docker", "run", "--rm", f"{repo}@{d['images'][name]['amd64_digest']}"] + cmd, timeout=300)
        line = next((l.strip() for l in txt.splitlines() if l.strip()), "")
        d["images"][name]["tool_reported_version"] = line[:120]
        code2, txt2 = _run(["docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}",
                            f"{repo}:{tag}"])
        if code2 == 0:
            d["images"][name]["pulled_repo_digest"] = txt2.strip()
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(d, indent=1))
    return d


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "resolve"
    d = resolve() if cmd == "resolve" else versions()
    for k, v in d["images"].items():
        print(f"  {k:<9} {v['tag']:<22} amd64 {str(v.get('amd64_digest'))[:26]}…  "
              f"{v.get('tool_reported_version', '')[:40]}{'  ERROR ' + v['error'] if v.get('error') else ''}")
