#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapas de contacto de cromatina predichos por AlphaGenome: REF, ALT y ALT-REF.

GOBERNANZA
    - Solo corre con un manifest congelado y sin modificar.
    - Biosample, contexto y regla de lectura vienen del manifest, no de mirar
      cual queda mejor. Los 28 biosamples se puntuan con el scorer oficial y
      se guardan como DISTRIBUCION: sirven para decir donde cae el elegido,
      nunca para sustituirlo.
    - Lo que sale de la maquina es la variante ya transmitida en EXP-009.

QUE PRODUCE (work/alphagenome/contacts/)
    ref.json.gz / alt.json.gz / delta.json.gz     matrices completas, auditables
    matrices.npz                                  lo mismo, binario
    robustness_scores.json                        ContactMapScorer, 28 pistas
    metadata.json                                 procedencia, hashes, checks,
                                                  interpretacion predeclarada

Uso: work/venv-ag/Scripts/python.exe src/model_outputs/alphagenome_contacts.py
"""
from __future__ import annotations
import io, os, sys, time

import numpy as np

sys.path.insert(0, ".")
from src.model_outputs import alphagenome_common as C                  # noqa: E402


# ------------------------------------------------------------ pure numpy ---
def check_maps(ref: np.ndarray, alt: np.ndarray, atol: float = 1e-5) -> dict:
    """Los invariantes que una matriz de contactos tiene que cumplir."""
    if ref.ndim != 2 or ref.shape[0] != ref.shape[1]:
        raise ValueError(f"REF no es cuadrada: {ref.shape}")
    if ref.shape != alt.shape:
        raise ValueError(f"REF {ref.shape} y ALT {alt.shape} difieren")
    if not (np.isfinite(ref).all() and np.isfinite(alt).all()):
        raise ValueError("NaN/Inf en las matrices")
    sym_ref = float(np.abs(ref - ref.T).max())
    sym_alt = float(np.abs(alt - alt.T).max())
    if sym_ref > atol or sym_alt > atol:
        raise ValueError(f"asimetria: REF {sym_ref:.2e}, ALT {sym_alt:.2e}")
    return {"square": True, "same_shape": True, "finite": True,
            "max_asymmetry_ref": sym_ref, "max_asymmetry_alt": sym_alt, "atol": atol}


def delta_of(ref: np.ndarray, alt: np.ndarray) -> np.ndarray:
    return alt.astype(np.float64) - ref.astype(np.float64)


def visible(ref: np.ndarray, delta: np.ndarray, frac: float = 0.05) -> dict:
    m_ref = float(np.abs(ref).max())
    m_d = float(np.abs(delta).max())
    return {"max_abs_ref": m_ref, "max_abs_delta": m_d,
            "ratio": (m_d / m_ref) if m_ref > 0 else float("inf"),
            "threshold": frac, "visible": bool(m_ref > 0 and m_d / m_ref >= frac)}


# ------------------------------------------------------------- the run ---
def main() -> int:
    from alphagenome.data import genome
    from alphagenome.models import dna_client, variant_scorers

    manifest = C.load_manifest()
    cand = manifest["candidate"]
    if C.assembly_gate(cand)["ref_validation"] != "PASS":
        return 2
    mc = manifest["contacts"]
    curie = mc["ontology_curie"]

    variant = genome.Variant(chromosome=cand["chromosome"], position=cand["position_1based"],
                             reference_bases=cand["ref"], alternate_bases=cand["alt"])
    interval = variant.reference_interval.resize(mc["sequence_context_bp"])
    print("  -> llamando a la API de AlphaGenome (la variante ya transmitida en EXP-009)")
    model = dna_client.create(C.api_key(), model_version=manifest["model"]["model_version_requested"])
    os.makedirs(C.CONTACT_DIR, exist_ok=True)
    started = C.now_utc()

    t0 = time.time()
    out = model.predict_variant(interval=interval, variant=variant,
                                requested_outputs=[dna_client.OutputType.CONTACT_MAPS],
                                ontology_terms=[curie])
    secs = time.time() - t0
    ref_td, alt_td = out.reference.contact_maps, out.alternate.contact_maps
    md = ref_td.metadata
    mask = (md["ontology_curie"].astype(str) == curie).to_numpy()
    if mask.sum() != 1:
        raise SystemExit(f"esperaba 1 pista de contactos para {curie}, hay {int(mask.sum())}")
    k = int(np.flatnonzero(mask)[0])
    ref = np.asarray(ref_td.values[..., k], dtype=np.float64)
    alt = np.asarray(alt_td.values[..., k], dtype=np.float64)
    checks = check_maps(ref, alt)
    delta = delta_of(ref, alt)
    n = ref.shape[0]
    res_bp = interval.width // n
    if res_bp != mc["resolution_bp"]:
        raise SystemExit(f"resolucion {res_bp} pb, el manifest declara {mc['resolution_bp']}")
    cand_bin = ((cand["position_1based"] - 1) - interval.start) // res_bp

    # robustez: el scorer oficial sobre TODAS las pistas de contactos
    t1 = time.time()
    sc = model.score_variant(interval=interval, variant=variant,
                             variant_scorers=[variant_scorers.ContactMapScorer()])[0]
    secs_sc = time.time() - t1
    X = np.asarray(sc.X, dtype=np.float64).ravel()
    rows = []
    for i in range(len(X)):
        r = sc.var.iloc[i]
        rows.append({"name": str(r.get("name", i)), "ontology_curie": str(r.get("ontology_curie", "")),
                     "biosample_name": str(r.get("biosample_name", "")),
                     "biosample_type": str(r.get("biosample_type", "")), "score": float(X[i])})
    chosen = [r for r in rows if r["ontology_curie"] == curie]
    scores = np.array([r["score"] for r in rows])
    chosen_rank = int((scores > chosen[0]["score"]).sum()) + 1 if chosen else None

    files = {}
    for name, arr in (("ref", ref), ("alt", alt), ("delta", delta)):
        p = os.path.join(C.CONTACT_DIR, f"{name}.json.gz")
        files[name] = {"file": os.path.basename(p),
                       "sha256": C.write_json(p, {"resolution_bp": res_bp, "n_bins": n,
                                                  "candidate_bin": int(cand_bin),
                                                  "matrix": arr.tolist()}, gz=True)}
    npz = os.path.join(C.CONTACT_DIR, "matrices.npz")
    np.savez_compressed(npz, ref=ref, alt=alt, delta=delta,
                        offsets_bp=(np.arange(n) - cand_bin) * res_bp)
    files["npz"] = {"file": "matrices.npz", "sha256": C.sha256_file(npz)}
    C.write_json(os.path.join(C.CONTACT_DIR, "robustness_scores.json"),
                 {"scorer": "ContactMapScorer", "n_tracks": len(rows), "rows": rows,
                  "chosen_ontology": curie, "chosen_rank_of_n": chosen_rank})

    vis = visible(ref, delta, 0.05)
    meta = {"run": "contacts", "started_utc": started, "finished_utc": C.now_utc(),
            "manifest_sha256": io.open(C.MANIFEST + ".sha256").read().strip(),
            "environment": C.environment(),
            "model": {"name": "AlphaGenome", "sdk": C.environment()["alphagenome_sdk"],
                      "model_version_requested": manifest["model"]["model_version_requested"],
                      "model_version_served": "not exposed by the API"},
            "figure_class": "MODEL_OUTPUT", "evidence_origin": "PREDICTED",
            "source_type": "predicted_not_patient_measurement",
            "random_seed": None, "deterministic_inference": True,
            "output": "CONTACT_MAPS", "input_length_bp": int(interval.width),
            "output_resolution_bp": int(res_bp), "n_bins": int(n),
            "candidate_bin": int(cand_bin),
            "ontology_curie": curie, "biosample_name": str(md.iloc[k].get("biosample_name", "")),
            "track_name": str(md.iloc[k].get("name", "")),
            "seconds_predict": round(secs, 1), "seconds_score": round(secs_sc, 1),
            "checks": checks, "delta_integrity": bool(np.array_equal(delta, alt - ref)),
            "files": files,
            "robustness": {"n_tracks": len(rows), "chosen_rank_of_n": chosen_rank,
                           "chosen_score": chosen[0]["score"] if chosen else None,
                           "score_min": float(scores.min()), "score_median": float(np.median(scores)),
                           "score_max": float(scores.max())},
            "interpretation": {"rule": mc["interpretation_rule"], **vis,
                               "reading": (mc["interpretation_rule"]["visible"] if vis["visible"]
                                           else mc["interpretation_rule"]["otherwise"])}}
    C.write_json(os.path.join(C.CONTACT_DIR, "metadata.json"), meta)
    print(f"  pista     : {meta['biosample_name']} ({curie}) · {n}x{n} bins de {res_bp} pb")
    print(f"  checks    : simetria REF {checks['max_asymmetry_ref']:.1e}, ALT "
          f"{checks['max_asymmetry_alt']:.1e}; delta == ALT-REF: {meta['delta_integrity']}")
    print(f"  max |REF| {vis['max_abs_ref']:.4g} · max |delta| {vis['max_abs_delta']:.4g} · "
          f"ratio {vis['ratio']:.4f} -> visible: {vis['visible']}")
    print(f"  robustez  : ContactMapScorer en {len(rows)} pistas; la elegida ocupa el puesto "
          f"{chosen_rank} (score {meta['robustness']['chosen_score']:.4g}; mediana "
          f"{meta['robustness']['score_median']:.4g}, max {meta['robustness']['score_max']:.4g})")
    print(f"  -> {C.CONTACT_DIR}/metadata.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
