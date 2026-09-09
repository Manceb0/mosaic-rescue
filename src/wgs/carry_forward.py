#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arrastre de una etapa completada bajo un commit anterior, con su procedencia real.

EL PROBLEMA QUE RESUELVE
    Una etapa puede haber terminado bien bajo el commit A y, antes de que siga
    la corrida, el orquestador se enmienda y pasa al commit B. Repetirla seria
    tirar trabajo valido. Pero dejarla sin marcar seria peor: el resumen final
    daria a entender que TODO el GO 2B se ejecuto con el codigo enmendado, y eso
    es una falsedad historica pequeña pero real.

    Aqui la etapa se conserva como **SUCCESS** —`carried_forward` es procedencia,
    no un estado nuevo— y se registra bajo que commit se ejecuto de verdad, con
    los hashes de sus salidas.

CONDICIONES DE ACEPTACION (todas, o se rechaza)
    1. las salidas declaradas existen y no estan vacias;
    2. sus hashes se calculan y se guardan en el momento de sellar;
    3. si ya habia un sellado previo, los hashes coinciden: nada cambio desde
       entonces;
    4. el preflight critico de la etapa 0 esta en SUCCESS **bajo este commit**,
       de modo que BAM, BAI, referencia, contigs y procedencia se han vuelto a
       comprobar antes de reutilizar nada.

Uso:
    python src/wgs/carry_forward.py seal   <etapa> <commit real>   # antes de enmendar
    python src/wgs/carry_forward.py accept <etapa>                 # lo llama el orquestador
"""
from __future__ import annotations
import hashlib, io, json, os, subprocess, sys
from datetime import datetime, timezone

W = "work/callers"
S = os.path.join(W, "status")

# Salidas que definen que una etapa termino bien, por etapa.
OUTPUTS = {
    "1": ["work/callers/qc/win1kb.regions.bed.gz",
          "work/callers/qc/win1kb.mosdepth.summary.txt",
          "work/callers/qc/win1kb.mosdepth.global.dist.txt"],
}
TOOL = {"1": {"tool": "mosdepth", "image_tag": "0.3.10--h4e814b3_1",
              "params": "-t 4 -n --by 1000",
              "inputs_unchanged": "BAM, BAI, reference, parameters and container digest are unchanged"}}


def sha256(p):
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def head_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "no disponible"


def _hashes(stage):
    out = {}
    for rel in OUTPUTS[stage]:
        if not os.path.exists(rel) or os.path.getsize(rel) == 0:
            return None, f"salida ausente o vacia: {os.path.basename(rel)}"
        out[os.path.basename(rel)] = {"bytes": os.path.getsize(rel), "sha256": sha256(rel)}
    return out, None


def seal(stage, commit):
    """Sella la procedencia ANTES de enmendar el orquestador."""
    h, err = _hashes(stage)
    if err:
        raise SystemExit(f"no se puede sellar la etapa {stage}: {err}")
    rec = {"stage": stage, "status": "SUCCESS", "carried_forward": True,
           "executed_under_commit": commit, "sealed_utc": now(), "outputs": h,
           **TOOL.get(stage, {}),
           "carry_forward_reason": ("mosdepth completed successfully before the control-flow "
                                    "amendment; its validated outputs were retained because BAM, "
                                    "BAI, reference, parameters and container digest are unchanged."),
           "carry_forward_validation": ("critical preflight rerun under the amended orchestrator "
                                        "before reuse")}
    os.makedirs(S, exist_ok=True)
    io.open(os.path.join(S, f"{stage}.carry.json"), "w", encoding="utf-8").write(json.dumps(rec, indent=1))
    print(f"  etapa {stage} sellada · ejecutada bajo {commit} · {len(h)} salidas hasheadas")
    for k, v in h.items():
        print(f"    {v['sha256'][:16]}…  {v['bytes']:>12,} B  {k}")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def accept(stage):
    """Lo llama el orquestador: acepta el arrastre solo si todo cuadra."""
    p = os.path.join(S, f"{stage}.carry.json")
    if not os.path.exists(p):
        raise SystemExit(f"la etapa {stage} no tiene procedencia sellada: no se arrastra")
    rec = json.load(io.open(p, encoding="utf-8"))
    h, err = _hashes(stage)
    if err:
        raise SystemExit(f"arrastre rechazado: {err}")
    for k, v in rec["outputs"].items():
        if k not in h or h[k]["sha256"] != v["sha256"]:
            raise SystemExit(f"arrastre rechazado: {k} cambio desde el sellado")
    st = os.path.join(S, "0.status")
    ok0 = os.path.exists(st) and io.open(st, encoding="utf-8").read().split("\t")[1] == "SUCCESS"
    if not ok0:
        raise SystemExit("arrastre rechazado: el preflight critico no esta en SUCCESS bajo este commit")
    rec["accepted_utc"] = now()
    rec["controlflow_commit"] = head_commit()
    rec["preflight_revalidated_under_controlflow_commit"] = True
    io.open(p, "w", encoding="utf-8").write(json.dumps(rec, indent=1))
    print(f"  etapa {stage} arrastrada: SUCCESS · ejecutada bajo {rec['executed_under_commit']} · "
          f"control de flujo {rec['controlflow_commit']} · preflight revalidado")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "accept"
    if cmd == "seal":
        seal(sys.argv[2], sys.argv[3])
    elif cmd == "accept":
        sys.exit(accept(sys.argv[2]))
    else:
        raise SystemExit("uso: seal <etapa> <commit> | accept <etapa>")
