#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga de Exomiser y sus datos para el BASELINE EXTERNO (EXP-006b).

Reanudable con Range: si se corta a los 15 GB, continua en vez de empezar de
cero. Todo va a work/ (gitignored).

Este script NO ejecuta nada del baseline ni le pasa un solo dato nuestro. Solo
trae la herramienta y su propia base de conocimiento.
"""
from __future__ import annotations
import io, os, sys, time, urllib.request

BASE_DATA = "https://data.monarchinitiative.org/exomiser/data/"
DEST = "work/exomiser"

ARTIFACTS = [
    ("exomiser-cli-14.1.0-distribution.zip",
     "https://github.com/exomiser/Exomiser/releases/download/14.1.0/"
     "exomiser-cli-14.1.0-distribution.zip"),
    ("2402_phenotype.zip", BASE_DATA + "2402_phenotype.zip"),
    ("2402_hg38.zip",      BASE_DATA + "2402_hg38.zip"),
]


def download(name: str, url: str) -> None:
    os.makedirs(DEST, exist_ok=True)
    path = os.path.join(DEST, name)
    have = os.path.getsize(path) if os.path.exists(path) else 0

    head = urllib.request.Request(url, method="HEAD",
                                  headers={"User-Agent": "mosaic-rescue/baseline"})
    with urllib.request.urlopen(head, timeout=60) as r:
        total = int(r.headers.get("Content-Length", 0))

    if have and have >= total:
        print(f"  {name}: ya completo ({have/2**30:.1f} GB)", flush=True)
        return

    hdr = {"User-Agent": "mosaic-rescue/baseline"}
    if have:
        hdr["Range"] = f"bytes={have}-"
        print(f"  {name}: reanudando en {have/2**30:.1f} / {total/2**30:.1f} GB", flush=True)
    else:
        print(f"  {name}: descargando {total/2**30:.1f} GB", flush=True)

    req = urllib.request.Request(url, headers=hdr)
    t0, last = time.time(), have
    with urllib.request.urlopen(req, timeout=120) as r, io.open(path, "ab") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            have += len(chunk)
            if have - last > (1 << 29):          # informe cada 512 MB
                el = time.time() - t0
                print(f"    {name}: {have/2**30:.1f}/{total/2**30:.1f} GB "
                      f"({100*have/total:.0f} %) · {(have-(last))/2**20/max(el,1):.1f} MB/s",
                      flush=True)
                last = have
    print(f"  {name}: LISTO {have/2**30:.1f} GB en {(time.time()-t0)/60:.0f} min", flush=True)


if __name__ == "__main__":
    for name, url in ARTIFACTS:
        try:
            download(name, url)
        except Exception as e:                   # una caida no debe abortar el resto
            print(f"  {name}: FALLO {e.__class__.__name__}: {e}", flush=True)
            sys.exit(1)
    print("  todos los artefactos descargados", flush=True)
