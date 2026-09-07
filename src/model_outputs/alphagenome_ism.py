#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""In silico mutagenesis (ISM) de AlphaGenome alrededor del candidato congelado.

GOBERNANZA
    - Solo corre con un manifest congelado y sin modificar (sha256 comprobado).
    - Los 768 SNV que se puntuan son PERTURBACIONES SINTETICAS de la secuencia
      de referencia: lo unico derivado del paciente que sale de la maquina es
      el locus (la misma coordenada que ya se transmitio en EXP-009).
    - Ninguna coordenada se imprime. Los artefactos con coordenadas viven en
      work/, gitignored. Lo que se versiona lleva OFFSETS al candidato.
    - No hay componente aleatorio: random_seed = null.

QUE PRODUCE (work/alphagenome/ism/)
    primary_raw_scores.json.gz     un registro por variante y scorer: offset,
                                   ref, alt, escalar crudo, y la pista/ontologia
    primary_matrix.json.gz         matriz 256 x 4 centrada por posicion (la
                                   transformacion oficial de ism_matrix) y la
                                   version 'logo' (solo base de referencia)
    primary_matrices.npz           lo mismo, binario, para carga rapida
    sensitivity_*                  idem con 100 kb de contexto
    metadata.json                  procedencia, hashes, entorno, rangos e
                                   interpretacion segun la regla predeclarada

Uso: work/venv-ag/Scripts/python.exe src/model_outputs/alphagenome_ism.py
"""
from __future__ import annotations
import io, os, sys, time

import numpy as np

sys.path.insert(0, ".")
from src.model_outputs import alphagenome_common as C                  # noqa: E402

VOCAB = "ACGT"


# ------------------------------------------------------------ pure numpy ---
def center_by_position(raw: np.ndarray) -> np.ndarray:
    """La transformacion oficial de `alphagenome.interpretation.ism.ism_matrix`.

    `raw` es L x 4 con el escalar de cada sustitucion y 0 en la base de
    referencia (una variante REF->REF no existe). El SDK resta a las cuatro
    celdas de cada posicion la media de las TRES alternativas:

        ISM_{p,b} = s_{p,b} - (1/3) * sum_{b' != ref} s_{p,b'}

    La celda de referencia queda en -media(alternativas), que es exactamente lo
    que dibuja el logo oficial. Reimplementada aqui, fuera del SDK, para que
    los tests la comprueben contra lo que el SDK devolvio.
    """
    raw = np.asarray(raw, dtype=np.float64)
    return raw - raw.sum(axis=1, keepdims=True) / 3.0


def logo_from(centered: np.ndarray, ref_seq: str) -> np.ndarray:
    """Version 'solo referencia': cada fila conserva solo la base de REF."""
    out = np.zeros_like(centered)
    for i, b in enumerate(ref_seq):
        out[i, VOCAB.index(b)] = centered[i, VOCAB.index(b)]
    return out


def raw_matrix(records: list, L: int, ref_seq: str) -> np.ndarray:
    """L x 4 con el escalar de cada (posicion, alt) y 0 en la base de REF."""
    m = np.zeros((L, 4), dtype=np.float64)
    seen = np.zeros((L, 4), dtype=bool)
    for r in records:
        i, j = r["index"], VOCAB.index(r["alt"])
        if seen[i, j]:
            raise ValueError("sustitucion repetida")
        m[i, j] = r["score"]; seen[i, j] = True
    for i, b in enumerate(ref_seq):
        seen[i, VOCAB.index(b)] = True
    if not seen.all():
        raise ValueError("faltan sustituciones: la ISM no esta completa")
    return m


def ranks(centered: np.ndarray, cand_index: int, cand_alt: str) -> dict:
    per_pos = np.abs(centered).max(axis=1)
    order = np.argsort(-per_pos, kind="stable")
    pos_rank = int(np.where(order == cand_index)[0][0]) + 1
    flat = np.abs(centered).ravel()
    cand_flat = cand_index * 4 + VOCAB.index(cand_alt)
    sub_rank = int((flat > flat[cand_flat]).sum()) + 1
    return {"candidate_position_rank_of_L": pos_rank,
            "candidate_substitution_rank_of_all": sub_rank,
            "candidate_abs_centered": float(np.abs(centered[cand_index, VOCAB.index(cand_alt)])),
            "window_max_abs_centered": float(per_pos.max()),
            "window_argmax_offset": int(order[0] - cand_index)}


# ------------------------------------------------------------- the run ---
def make_scorers(spec_list):
    from alphagenome.models import dna_client, variant_scorers
    out = []
    for s in spec_list:
        if s["scorer"] != "CenterMaskScorer":
            raise SystemExit(f"scorer no soportado por este runner: {s['scorer']}")
        out.append(variant_scorers.CenterMaskScorer(
            requested_output=getattr(dna_client.OutputType, s["output"]),
            width=s["width"],
            aggregation_type=getattr(variant_scorers.AggregationType, s["aggregation"])))
    return out


def scalar_from(adata, spec) -> tuple[float, str]:
    """Aplica la scalar_rule predeclarada. Devuelve (escalar, pista usada)."""
    X = np.asarray(adata.X, dtype=np.float64).ravel()
    var = adata.var
    if spec["ontology_curie"]:
        mask = (var["ontology_curie"].astype(str) == spec["ontology_curie"]).to_numpy()
        if mask.sum() != 1:
            raise SystemExit(f"{spec['output']}: esperaba 1 pista {spec['ontology_curie']}, "
                             f"hay {int(mask.sum())}")
        k = int(np.flatnonzero(mask)[0])
    else:
        # sin ontologia: la pista con mayor |score| (regla del manifest)
        k = int(np.argmax(np.abs(X)))
    name = str(var.iloc[k].get("name", k))
    return float(X[k]), name


def run_context(model, manifest, ctx_bp: int, tag: str, cand, ref_window: str) -> dict:
    from alphagenome.data import genome
    from alphagenome.interpretation import ism as ism_lib

    m_ism = manifest["ism"]
    variant = genome.Variant(chromosome=cand["chromosome"], position=cand["position_1based"],
                             reference_bases=cand["ref"], alternate_bases=cand["alt"])
    seq_interval = variant.reference_interval.resize(ctx_bp)
    ism_interval = variant.reference_interval.resize(m_ism["ism_window_bp"])
    L = ism_interval.width
    cand_index = (cand["position_1based"] - 1) - ism_interval.start
    scorers = make_scorers(m_ism["scorers"])

    t0 = time.time()
    results = model.score_ism_variants(interval=seq_interval, ism_interval=ism_interval,
                                       variant_scorers=scorers, progress_bar=False)
    secs = time.time() - t0
    if len(results) != m_ism["expected_variants"]:
        raise SystemExit(f"{tag}: {len(results)} variantes, esperadas {m_ism['expected_variants']}")

    records = {s["role"]: [] for s in m_ism["scorers"]}
    variants = []
    for per_variant in results:
        v = per_variant[0].uns["variant"]
        idx = (v.position - 1) - ism_interval.start
        if not (0 <= idx < L):
            raise SystemExit("variante ISM fuera de la ventana")
        # el modelo trabaja sobre SU genoma: la base de referencia que asume
        # tiene que coincidir con nuestro GRCh38 local, posicion a posicion
        if v.reference_bases != ref_window[idx]:
            raise SystemExit(f"{tag}: REF del modelo != FASTA local en el offset "
                             f"{idx - cand_index}")
        variants.append(v)
        for spec, adata in zip(m_ism["scorers"], per_variant):
            sc, track = scalar_from(adata, spec)
            records[spec["role"]].append({"index": int(idx), "offset": int(idx - cand_index),
                                          "ref": v.reference_bases, "alt": v.alternate_bases,
                                          "score": sc, "track": track})

    out = {"tag": tag, "sequence_context_bp": ctx_bp, "ism_window_bp": L,
           "n_variants": len(results), "seconds": round(secs, 1),
           "candidate_index_in_window": int(cand_index), "roles": {}}
    for spec in m_ism["scorers"]:
        role = spec["role"]
        recs = records[role]
        raw = raw_matrix(recs, L, ref_window)
        centered = center_by_position(raw)
        # la transformacion oficial del SDK, sobre los mismos escalares, tiene
        # que dar lo mismo que la reimplementacion de arriba
        official = ism_lib.ism_matrix([r["score"] for r in recs], variants=variants,
                                      interval=ism_interval, multiply_by_sequence=False,
                                      require_fully_filled=True)
        # el SDK trabaja en float32; la tolerancia es la de ese tipo
        if not np.allclose(official, centered, rtol=1e-5, atol=1e-6):
            raise SystemExit(f"{tag}/{role}: la matriz del SDK no coincide con la centrada")
        logo = logo_from(centered, ref_window)
        if not np.isfinite(centered).all():
            raise SystemExit(f"{tag}/{role}: NaN/Inf en la matriz")
        rk = ranks(centered, cand_index, cand["alt"])
        base = os.path.join(C.ISM_DIR, f"{tag}_{role.lower()}")
        sha_raw = C.write_json(base + "_raw_scores.json.gz",
                               {"scorer": spec, "records": recs}, gz=True)
        sha_mat = C.write_json(base + "_matrix.json.gz",
                               {"vocabulary": VOCAB, "offsets": [i - cand_index for i in range(L)],
                                "reference_window": ref_window,
                                "centered": centered.tolist(), "logo_ref_only": logo.tolist(),
                                "candidate_index": int(cand_index)}, gz=True)
        np.savez_compressed(base + "_matrices.npz", raw=raw, centered=centered, logo=logo,
                            offsets=np.arange(L) - cand_index)
        out["roles"][role] = {"scorer": spec, "files": {
            "raw_scores": os.path.basename(base + "_raw_scores.json.gz"), "raw_scores_sha256": sha_raw,
            "matrix": os.path.basename(base + "_matrix.json.gz"), "matrix_sha256": sha_mat,
            "npz": os.path.basename(base + "_matrices.npz"),
            "npz_sha256": C.sha256_file(base + "_matrices.npz")},
            "ranks": rk, "tracks_used": sorted({r["track"] for r in recs})}
    return out


def interpret(primary: dict, sensitivity: dict | None, manifest: dict) -> dict:
    rule = manifest["ism"]["interpretation_rule"]
    L = manifest["ism"]["ism_window_bp"]
    rk = primary["roles"]["PRIMARY"]["ranks"]
    concentrated = rk["candidate_position_rank_of_L"] <= max(1, int(round(0.05 * L)))
    out = {"primary_scorer": "PRIMARY",
           "concentrated_local_sensitivity_at_candidate": bool(concentrated),
           "reading": (rule["concentrated"] if concentrated else rule["otherwise"]),
           "candidate_position_rank": rk["candidate_position_rank_of_L"],
           "candidate_substitution_rank": rk["candidate_substitution_rank_of_all"]}
    if sensitivity is not None:
        r = {}
        for role in primary["roles"]:
            a = np.load(os.path.join(C.ISM_DIR, primary["roles"][role]["files"]["npz"]))["centered"]
            b = np.load(os.path.join(C.ISM_DIR, sensitivity["roles"][role]["files"]["npz"]))["centered"]
            r[role] = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
        out["context_pearson_r"] = r
        out["context_sensitive"] = bool(r["PRIMARY"] < 0.8)
    return out


def main() -> int:
    from alphagenome.models import dna_client
    manifest = C.load_manifest()
    cand = manifest["candidate"]
    if C.assembly_gate(cand)["ref_validation"] != "PASS":      # se repite: es barato
        return 2
    plain = cand["chromosome"].replace("chr", "")
    from alphagenome.data import genome
    v = genome.Variant(chromosome=cand["chromosome"], position=cand["position_1based"],
                       reference_bases=cand["ref"], alternate_bases=cand["alt"])
    w = v.reference_interval.resize(manifest["ism"]["ism_window_bp"])
    ref_window = C.fasta_fetch(C.FASTA, plain, w.start + 1, w.end)      # 1-based inclusivo
    if len(ref_window) != w.width or ref_window[(cand["position_1based"] - 1) - w.start] != cand["ref"]:
        raise SystemExit("la ventana de referencia local no cuadra con el candidato")

    print("  -> llamando a la API de AlphaGenome (el locus del candidato sale de la maquina; "
          "las 768 variantes son sinteticas)")
    model = dna_client.create(C.api_key(), model_version=manifest["model"]["model_version_requested"])
    os.makedirs(C.ISM_DIR, exist_ok=True)
    started = C.now_utc()
    primary = run_context(model, manifest, manifest["ism"]["sequence_context_bp"], "primary",
                          cand, ref_window)
    print(f"  primary   : {primary['n_variants']} variantes en {primary['seconds']} s")
    sens_bp = manifest["ism"]["sensitivity_check"]["sequence_context_bp"]
    sensitivity = run_context(model, manifest, sens_bp, "sensitivity", cand, ref_window)
    print(f"  sensitivity: {sensitivity['n_variants']} variantes en {sensitivity['seconds']} s")

    meta = {"run": "ism", "started_utc": started, "finished_utc": C.now_utc(),
            "manifest_sha256": io.open(C.MANIFEST + ".sha256").read().strip(),
            "environment": C.environment(),
            "model": {"name": "AlphaGenome", "sdk": C.environment()["alphagenome_sdk"],
                      "model_version_requested": manifest["model"]["model_version_requested"],
                      "model_version_served": "not exposed by the API"},
            "figure_class": "MODEL_OUTPUT", "evidence_origin": "PREDICTED",
            "source_type": "predicted_not_patient_measurement",
            "random_seed": None, "deterministic_inference": True,
            "primary": primary, "sensitivity": sensitivity}
    meta["interpretation"] = interpret(primary, sensitivity, manifest)
    C.write_json(os.path.join(C.ISM_DIR, "metadata.json"), meta)
    rk = primary["roles"]["PRIMARY"]["ranks"]
    print(f"  PRIMARY  : candidato en el puesto {rk['candidate_position_rank_of_L']} de "
          f"{manifest['ism']['ism_window_bp']} posiciones; |efecto| {rk['candidate_abs_centered']:.3e} "
          f"frente al maximo de la ventana {rk['window_max_abs_centered']:.3e} "
          f"(offset {rk['window_argmax_offset']:+d})")
    ip = meta["interpretation"]
    print(f"  lectura  : {ip['reading']}")
    print(f"  contexto : r(16 kb, 100 kb) = {ip['context_pearson_r']}")
    print(f"  -> {C.ISM_DIR}/metadata.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
