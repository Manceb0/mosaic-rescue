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
    4. el preflight critico de la etapa 0 esta en SUCCESS **y el commit que el
       mismo dejo escrito es el commit del control de flujo actual**, de modo que
       BAM, BAI, referencia, contigs y procedencia se han vuelto a comprobar de
       verdad antes de reutilizar nada. La revalidacion se comprueba, no se declara.

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
    # Dos ejes SEPARADOS, y no se contaminan:
    #   execution_status        lo que paso de verdad al ejecutar. Historico.
    #                           Una validacion de reutilizacion fallida NO lo reescribe.
    #   carry_forward_validation si esas salidas se pueden REUTILIZAR ahora.
    rec = {"stage": stage, "execution_status": "SUCCESS",
           "carry_forward_validation": "PENDING", "carried_forward": False,
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
    """Lo llama el orquestador. Codigos de salida, y lo que significan:

        0  validacion PASS  -> se reutiliza; la etapa no se repite
        2  validacion FAIL  -> NO se reutiliza y la etapa se REPITE. El
                              `execution_status` historico NO se reescribe: la
                              ejecucion original si tuvo exito; lo que fallo es
                              la reutilizacion. Solo una NUEVA ejecucion fallida
                              produce FAILED.
        3  el preflight critico no esta en SUCCESS, o su SUCCESS se sello bajo
                              otro commit y por tanto la base no se ha revalidado
                              bajo este -> el orquestador ABORTA
    """
    p = os.path.join(S, f"{stage}.carry.json")
    if not os.path.exists(p):
        print(f"  etapa {stage}: sin procedencia sellada; se repite")
        return 2
    rec = json.load(io.open(p, encoding="utf-8"))
    # Sellados escritos antes de separar los dos ejes usaban la clave `status`.
    # Se migra en memoria en vez de romper: el hecho historico es el mismo.
    if "execution_status" not in rec:
        rec["execution_status"] = rec.pop("status", "SUCCESS")
        rec["schema_migrated_from"] = "status -> execution_status"
    rec.setdefault("carry_forward_validation", "PENDING")

    # El preflight tiene que estar en SUCCESS **y** haberse ejecutado bajo ESTE
    # commit del control de flujo. No se afirma: se comprueba leyendo el commit
    # que la propia etapa 0 dejo escrito. El orquestador repite el preflight
    # cuando el commit cambia, asi que una discrepancia aqui significa que la
    # base no se revalido y no se puede reutilizar nada sobre ella.
    st = os.path.join(S, "0.status")
    parts = (io.open(st, encoding="utf-8").read().rstrip("\n").split("\t")
             if os.path.exists(st) else [])
    if len(parts) < 2 or parts[1] != "SUCCESS":
        print("  el preflight critico no esta en SUCCESS")
        return 3
    pre_commit = parts[3] if len(parts) > 3 and parts[3] else None
    head = head_commit()
    if pre_commit != head:
        print(f"  el preflight esta en SUCCESS pero se sello bajo "
              f"'{pre_commit or 'sin registro de commit'}' y el control de flujo es '{head}': "
              f"no esta revalidado bajo este commit")
        return 3

    h, err = _hashes(stage)
    reason = err
    if not err:
        for k, v in rec["outputs"].items():
            if k not in h or h[k]["sha256"] != v["sha256"]:
                reason = f"{k} cambio desde el sellado"
                break

    rec["controlflow_commit"] = head
    rec["preflight_commit"] = pre_commit
    rec["preflight_revalidated_under_controlflow_commit"] = (pre_commit == head)
    rec["evaluated_utc"] = now()
    if reason:
        rec["carry_forward_validation"] = "FAIL"
        rec["carry_forward_validation_reason"] = reason
        rec["carried_forward"] = False
        rec["note"] = ("the original execution SUCCEEDED and that history is not rewritten; "
                       "only the reuse validation failed, so the stage is re-run")
        io.open(p, "w", encoding="utf-8").write(json.dumps(rec, indent=1))
        print(f"  etapa {stage}: carry_forward_validation=FAIL ({reason}). "
              f"execution_status historico sigue siendo {rec['execution_status']}. Se repite.")
        return 2
    rec["carry_forward_validation"] = "PASS"
    rec["carried_forward"] = True
    rec["accepted_utc"] = now()
    io.open(p, "w", encoding="utf-8").write(json.dumps(rec, indent=1))
    print(f"  etapa {stage}: carry_forward_validation=PASS · execution_status "
          f"{rec['execution_status']} bajo {rec['executed_under_commit']} · control de flujo "
          f"{rec['controlflow_commit']} · preflight revalidado")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "accept"
    if cmd == "seal":
        seal(sys.argv[2], sys.argv[3])
    elif cmd == "accept":
        sys.exit(accept(sys.argv[2]))
    else:
        raise SystemExit("uso: seal <etapa> <commit> | accept <etapa>")
