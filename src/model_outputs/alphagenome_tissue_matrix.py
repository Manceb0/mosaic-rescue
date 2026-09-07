#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-024b · Panel tejido x modalidad, congelado ANTES de puntuar.

POR QUE
    AlphaGenome tiene cientos de pistas por modalidad. Ensenar una sola es
    invitar a la sospecha de que se eligio la que quedaba mejor. El panel se
    fija aqui por CRITERIO, se sella con sha256, y luego se muestran todas sus
    celdas: las debiles y las negativas tambien.

CRITERIO DEL PANEL (seis biosamples)
    fenotipo        musculo psoas (atrofia muscular), rinon (nefrocalcinosis)
    celula de MVA   fibroblasto de prepucio: el fibroblasto con mas modalidades
                    disponibles (el de piel, CL:0002620, solo existe en contactos)
    ya congelado    progenitor mieloide CD34+ (la pista DNase de EXP-023)
    sangre          celula mononuclear de sangre periferica
    sin relacion    higado: contexto negativo, para ver como es "nada"

MODALIDADES Y SCORERS
    Los RECOMMENDED_VARIANT_SCORERS oficiales de cada modalidad, con 1 Mb de
    contexto (lo que la documentacion recomienda para scorers de gen). Se
    registra el repr de cada scorer al congelar. Las celdas sin pista en el
    modelo se muestran como "not available", no se rellenan.

REGLA DE LECTURA (por modalidad, dentro del panel)
    "tissue-restricted"  si max |score| >= 3 x mediana |score| del panel
    "broadly consistent" en cualquier otro caso (incluido "sin efecto")
    y, con el null de EXP-024 puntuado con los mismos scorers, el percentil de
    cada celda frente a su distribucion nula.

Uso:
    work/venv-ag/Scripts/python.exe src/model_outputs/alphagenome_tissue_matrix.py freeze
"""
from __future__ import annotations
import io, os, sys

import numpy as np

sys.path.insert(0, ".")
from src.model_outputs import alphagenome_common as C                  # noqa: E402

DIR = os.path.join(C.WORK, "tissue_matrix")
PANEL_MANIFEST = os.path.join(DIR, "panel_manifest.json")

STATUS = "PRE-SPECIFIED EXPLORATORY / DESCRIPTIVE"
DISCLAIMER = ("External model contexts. No patient transcriptome, epigenome, chromatin profile or "
              "cell-specific functional assay is available; no cell is a measurement from the patient.")
BIOSAMPLES = [
    ("UBERON:0008450", "psoas muscle", "phenotype-motivated context (skeletal muscle atrophy); not an affected patient tissue"),
    ("UBERON:0002113", "kidney", "phenotype-motivated context (nephrocalcinosis); not an affected patient tissue"),
    ("CL:1001608", "foreskin fibroblast", "literature-motivated MVA functional context (the fibroblast with most modalities; skin fibroblast exists only in contact maps)"),
    ("CL:0001059", "common myeloid progenitor, CD34-positive", "proliferative hematopoietic context; the DNase track already frozen in EXP-023"),
    ("CL:2000001", "peripheral blood mononuclear cell", "tissue of WGS origin, if applicable"),
    ("UBERON:0002107", "liver", "predeclared unrelated comparator"),
]
MODALITIES = ["RNA_SEQ", "SPLICE_SITE_USAGE", "SPLICE_JUNCTIONS", "DNASE", "ATAC", "CHIP_HISTONE"]
HISTONE_MARKS = ["H3K27ac", "H3K4me3"]      # activa / promotor; fijados aqui


def make_scorers(panel: dict):
    from alphagenome.models import variant_scorers
    return [variant_scorers.RECOMMENDED_VARIANT_SCORERS[m] for m in panel["modalities"]]


def freeze() -> dict:
    if os.path.exists(PANEL_MANIFEST):
        raise SystemExit(f"{PANEL_MANIFEST} ya existe: un panel congelado no se reescribe")
    from alphagenome.models import variant_scorers, dna_client
    man = C.load_manifest()
    model = dna_client.create(C.api_key())
    md = model.output_metadata(organism=dna_client.Organism.HOMO_SAPIENS)   # solo metadatos
    avail = {}
    for m in MODALITIES:
        df = getattr(md, m.lower())
        cur = set(df["ontology_curie"].astype(str)) if df is not None and "ontology_curie" in df.columns else set()
        avail[m] = {c: (c in cur) for c, _n, _r in BIOSAMPLES}
    out = {"experiment": "EXP-024b tissue x modality", "status": STATUS, "disclaimer": DISCLAIMER,
           "inference": "descriptive only; percentiles per cell are descriptive; no cell becomes a "
                        "significant result and none is chosen after seeing scores",
           "frozen_at_utc": C.now_utc(), "git_commit": C.git_commit(),
           "exp023_manifest_sha256": io.open(C.MANIFEST + ".sha256").read().strip(),
           "context_bp": man["contacts"]["sequence_context_bp"],
           "biosamples": [{"ontology_curie": c, "name": n, "reason": r} for c, n, r in BIOSAMPLES],
           "modalities": MODALITIES, "histone_marks": HISTONE_MARKS,
           "scorers": {m: repr(variant_scorers.RECOMMENDED_VARIANT_SCORERS[m]) for m in MODALITIES},
           "availability": avail,
           "cell_rule": "signed score of the biosample's track(s); several tracks -> the one with "
                        "the largest |score|; absent -> 'not available' (never imputed)",
           "reading_rule": {"tissue_restricted": "max |score| >= 3 x median |score| within the modality",
                            "otherwise": "broadly consistent (weak or no predicted effect)",
                            "percentile": "each cell against the EXP-024 null scored with the same scorer"},
           "forbidden": ["choosing a biosample after seeing scores", "hiding weak or negative cells",
                         "calling any cell a measurement in the patient"]}
    sha = C.write_json(PANEL_MANIFEST, out)
    io.open(PANEL_MANIFEST + ".sha256", "w").write(sha + "\n")
    return out, sha


def load_panel() -> dict:
    want = io.open(PANEL_MANIFEST + ".sha256").read().strip()
    if C.sha256_file(PANEL_MANIFEST) != want:
        raise SystemExit("el panel cambio despues de congelarse")
    return C.read_json(PANEL_MANIFEST)


def panel_sha() -> str:
    return io.open(PANEL_MANIFEST + ".sha256").read().strip()


def extract(adatas, panel: dict) -> dict:
    """(modalidad -> biosample -> score) desde las AnnData de score_variant."""
    out = {}
    for m, ad in zip(panel["modalities"], adatas):
        X = np.asarray(ad.X, dtype=float)
        if X.ndim == 2 and X.shape[0] > 1:          # scorers de gen: una fila por gen
            X = X[[i for i, g in enumerate(ad.obs.get("gene_name", [])) if g == "BUB1B"] or [0]]
        X = X.ravel()
        var = ad.var
        cell = {}
        for b in panel["biosamples"]:
            mask = (var["ontology_curie"].astype(str) == b["ontology_curie"]).to_numpy() \
                if "ontology_curie" in var.columns else np.zeros(len(var), bool)
            if m == "CHIP_HISTONE" and "name" in var.columns:
                mask &= var["name"].astype(str).str.contains("|".join(panel["histone_marks"])).to_numpy()
            if mask.sum() == 0:
                cell[b["ontology_curie"]] = None
            else:
                xs = X[np.flatnonzero(mask)]
                cell[b["ontology_curie"]] = float(xs[np.argmax(np.abs(xs))])
        out[m] = cell
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "freeze"
    if cmd == "freeze":
        out, sha = freeze()
        print(f"  panel congelado: {PANEL_MANIFEST}  sha256 {sha[:16]}...")
        for m in MODALITIES:
            av = out["availability"][m]
            print(f"    {m:<18} " + "  ".join(f"{c}:{'si' if ok else 'NO'}" for c, ok in av.items()))
    else:
        raise SystemExit("uso: freeze")
