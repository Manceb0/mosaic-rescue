#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-024 · Calibracion del score de AlphaGenome del candidato congelado frente a
nulls preregistrados y controles de sensibilidad. Plan estadistico sellado ANTES
de puntuar nada. Revisado tras la primera revision del mantenedor (2026-09-07).

LO QUE RESPONDE
    EXP-023 respondio "¿el candidato cae donde el modelo es localmente
    sensible?". Esto responde: "¿el score del candidato es inusualmente extremo
    frente a SNV comparables puntuadas con el mismo sistema?". Calibra el
    MODELO. No calibra patogenicidad.

CONJUNTOS, cada uno con su manifest y su sha256, sellados antes de la primera llamada
    NULL-LOCAL        transiciones sinteticas del MISMO entorno del locus: a
                      <= 5 000 pb del candidato, intronicas, a >= 1 000 pb de
                      cualquier borde de exon (la misma clase "intronica
                      profunda" del candidato), fuera de la ventana ISM y de los
                      controles. Seleccionadas solo con rasgos independientes
                      del modelo. Se documenta que dimensiones NO quedaron
                      emparejadas; no se llama "fully matched".
    NULL-TRANSCRIPT   las 300 transiciones intronicas profundas de todo el
                      transcrito (la referencia amplia). Mismo muestreo y misma
                      semilla que el primer sellado, asi que son las mismas 300.
    CTRL-POS          las 4 posiciones canonicas de splicing de cada intron,
                      mutadas a su transicion. Control de POTENCIA de la lectura
                      de splicing, y SOLO de esa lectura.

    El candidato no esta en ningun conjunto (se comprueba). El unico paso
    aleatorio es el muestreo: semilla 42, registrada.

SENSIBILIDAD, POR LECTURA
    splice     calibrada por CTRL-POS
    dnase      UNCALIBRATED FOR SENSITIVITY: no existe un conjunto positivo
               externo defendible sin curacion nueva; un no-significativo solo
               puede leerse como "not unusually extreme under the preregistered
               null", nunca como evidencia contra un efecto funcional
    contact    UNCALIBRATED FOR SENSITIVITY, idem

FAMILIAS
    CONFIRMATORY FAMILY = {splice-primary, dnase-secondary, contact-global}:
        exactamente tres hipotesis; Benjamini-Hochberg SOLO entre ellas.
    Panel tejido x modalidad: PRE-SPECIFIED EXPLORATORY / DESCRIPTIVE. Sus
        percentiles son descriptivos. Ninguna celda se convierte en
        "significant" con el q de la familia de tres.

ESTADISTICA
    percentil  = 100 * #{|S_null| <  |S_cand|} / N
    p_emp      = (1 + #{|S_null| >= |S_cand|}) / (N + 1)
    z robusto  = (S_cand - mediana) / (1,4826 * MAD)
    MAD degenerado (MAD == 0 o MAD < 1e-6 * max|S_null|): z = "undefined
        (degenerate null spread)"; se reporta la fraccion de nulls iguales a 0
        y quedan percentil y p_emp como unicos resumenes.
    Cada estadistico se calcula frente a NULL-LOCAL y frente a NULL-TRANSCRIPT;
    la familia confirmatoria usa NULL-LOCAL (el emparejamiento mas estrecho) y
    NULL-TRANSCRIPT se reporta al lado.

LECTURAS OBLIGATORIAS
    q >= 0,05   "not unusually extreme relative to the preregistered null"
    q <  0,05   "unusually extreme relative to the preregistered null": se
                registra como CONTRADICCION CONCRETA para adjudicacion; no
                cambia por si sola clasificacion, ranking ni rama
    potencia(splice) < 0,5   la lectura de splicing no es sensible en este gen
                y el resultado del candidato en esa lectura se declara no
                informativo. NO se propaga a dnase ni contact.
    prohibido:  negative, benign, non-functional, no regulatory effect

CONTRATO DE PUNTUACION IDENTICO (invariante)
    candidato == null == controles en: longitud de contexto, scorer,
    ontologia, tratamiento de hebra, mascara central, agregacion escalar,
    normalizacion REF/ALT y manejo de salidas ausentes. Una variante que no
    pueda cumplir el contrato exacto (error de la API tras 3 reintentos, NaN,
    pista ausente) se EXCLUYE bajo esta regla escrita y se registra el motivo;
    si las exclusiones superan el 5 % de un conjunto, la corrida se marca
    INCOMPLETE y no se interpreta.

    Ninguna figura cambia de estatus por parecer visualmente llamativa.

Uso:
    python src/model_outputs/alphagenome_calibration.py freeze   # sin modelo
    work/venv-ag/Scripts/python.exe src/model_outputs/alphagenome_calibration.py run
"""
from __future__ import annotations
import io, json, os, random, sys, time

import numpy as np

sys.path.insert(0, ".")
from src.model_outputs import alphagenome_common as C                  # noqa: E402

DIR = os.path.join(C.WORK, "calibration")
INDEX = os.path.join(DIR, "prereg_index.json")
SETS = {"NULL-LOCAL": "null_local_manifest.json",
        "NULL-TRANSCRIPT": "null_transcript_manifest.json",
        "CTRL-POS": "ctrl_pos_manifest.json"}

N_LOCAL, N_TRANSCRIPT = 100, 300
LOCAL_RADIUS = 5000           # pb: "mismo entorno del locus"
MIN_EXON_DIST = 1000          # pb a cualquier borde de exon: clase "intronica profunda"
SEED = 42
TRANSITION = {"A": "G", "G": "A", "C": "T", "T": "C"}
FAMILY = ("splice", "dnase", "contact")
MAD_REL_EPS = 1e-6
MAX_EXCLUDED_FRAC = 0.05


# ------------------------------------------------------- geometria -------
def _exons():
    from src.structure.transcript_model import fetch
    tx = fetch()
    ex = sorted((int(e["start"]), int(e["end"])) for e in tx["exons"])
    return tx, ex


def exon_distance(p: int, ex) -> int:
    return min(min(abs(p - a), abs(p - b)) for a, b in ex)


def in_exon(p: int, ex) -> bool:
    return any(a <= p <= b for a, b in ex)


def deep_intronic_positions(ex, cand_pos: int, ism_half: int, lo: int, hi: int):
    return [p for p in range(lo, hi + 1)
            if not in_exon(p, ex) and exon_distance(p, ex) >= MIN_EXON_DIST
            and abs(p - cand_pos) > ism_half]


def canonical_sites(ex, strand: int):
    out = []
    for (a1, b1), (a2, b2) in zip(ex[:-1], ex[1:]):
        out += [(b1 + 1, "donor+1" if strand > 0 else "acceptor-1"),
                (b1 + 2, "donor+2" if strand > 0 else "acceptor-2"),
                (a2 - 2, "acceptor-2" if strand > 0 else "donor+2"),
                (a2 - 1, "acceptor-1" if strand > 0 else "donor+1")]
    return out


def candidate_features(cand, ex, tx, plain) -> dict:
    p = cand["position_1based"]
    gene_lo, gene_hi = ex[0][0], ex[-1][1]
    strand = int(tx.get("strand", 1))
    tss = gene_lo if strand > 0 else gene_hi
    flank = C.fasta_fetch(C.FASTA, plain, p - 50, p + 50)
    gc = sum(ch in "GC" for ch in flank) / len(flank)
    intron_idx = next((i for i, ((a1, b1), (a2, b2)) in enumerate(zip(ex[:-1], ex[1:]), 1)
                       if b1 < p < a2), None)
    return {"class": f"{cand['ref']}>{cand['alt']} transition", "intronic": not in_exon(p, ex),
            "intron_index_of_n": [intron_idx, len(ex) - 1],
            "distance_to_nearest_exon_bp": exon_distance(p, ex),
            "distance_to_tss_bp": abs(p - tss), "gc_101bp": round(gc, 3)}


# ------------------------------------------------------- freeze ----------
def _variants(positions, plain, cand_pos, role=None):
    out = []
    for p in positions:
        ref = C.fasta_fetch(C.FASTA, plain, p, p)
        if ref not in TRANSITION:
            raise SystemExit(f"base ambigua en el FASTA en el offset {p - cand_pos:+d}")
        v = {"position_1based": p, "ref": ref, "alt": TRANSITION[ref], "offset_bp": p - cand_pos}
        if role is not None:
            v["role"] = role if isinstance(role, str) else role[positions.index(p)]
        out.append(v)
    return out


def freeze() -> dict:
    for f in list(SETS.values()) + [os.path.basename(INDEX)]:
        if os.path.exists(os.path.join(DIR, f)):
            raise SystemExit(f"{f} ya existe: un conjunto congelado no se reescribe")
    man = C.load_manifest()
    cand = man["candidate"]; plain = cand["chromosome"].replace("chr", "")
    tx, ex = _exons(); strand = int(tx.get("strand", 1))
    ism_half = man["ism"]["ism_window_bp"] // 2
    cp = cand["position_1based"]
    feats = candidate_features(cand, ex, tx, plain)

    ctrl_sites = canonical_sites(ex, strand)
    ctrl_pos = {p for p, _ in ctrl_sites}

    # NULL-LOCAL: mismo entorno, misma clase intronica profunda
    local_pool = [p for p in deep_intronic_positions(ex, cp, ism_half, cp - LOCAL_RADIUS, cp + LOCAL_RADIUS)
                  if p not in ctrl_pos]
    if len(local_pool) < N_LOCAL:
        raise SystemExit(f"NULL-LOCAL: solo {len(local_pool)} posiciones elegibles")
    rng = random.Random(SEED)
    local = _variants(sorted(rng.sample(local_pool, N_LOCAL)), plain, cp)
    # NULL-TRANSCRIPT: todo el transcrito, misma semilla que el primer sellado
    gene_lo, gene_hi = ex[0][0], ex[-1][1]
    tr_pool = [p for p in deep_intronic_positions(ex, cp, ism_half, gene_lo, gene_hi)]
    rng = random.Random(SEED)
    transcript = _variants(sorted(rng.sample(tr_pool, N_TRANSCRIPT)), plain, cp)
    ctrl = []
    for p, role in ctrl_sites:
        ref = C.fasta_fetch(C.FASTA, plain, p, p)
        ctrl.append({"position_1based": p, "ref": ref, "alt": TRANSITION[ref], "role": role,
                     "offset_bp": p - cp})
    for s in (local, transcript, ctrl):
        if any(v["position_1based"] == cp for v in s):
            raise SystemExit("el candidato aparece en un conjunto: fuga")
    if set(v["position_1based"] for v in local) & ctrl_pos:
        raise SystemExit("NULL-LOCAL solapa con CTRL-POS")

    def dist_summary(vs):
        d = sorted(exon_distance(v["position_1based"], ex) for v in vs)
        off = [v["offset_bp"] for v in vs]
        return {"exon_distance_min_median_max_bp": [d[0], d[len(d) // 2], d[-1]],
                "offset_min_max_bp": [min(off), max(off)],
                "n_upstream": sum(o < 0 for o in off), "n_downstream": sum(o > 0 for o in off)}

    common = {"frozen_at_utc": C.now_utc(), "git_commit": C.git_commit(),
              "exp023_manifest_sha256": io.open(C.MANIFEST + ".sha256").read().strip(),
              "chromosome": cand["chromosome"], "transcript": {"id": tx["transcript"],
              "release": tx["release"], "strand": strand, "n_exons": len(ex)},
              "candidate_features_model_independent": feats, "random_seed": SEED}
    manifests = {
        "NULL-LOCAL": {**common, "set": "NULL-LOCAL",
                       "definition": f"synthetic transitions within {LOCAL_RADIUS} bp of the candidate, "
                                     f"intronic, >= {MIN_EXON_DIST} bp from any exon boundary (the candidate's "
                                     "deep-intronic class), outside the ISM window and CTRL-POS; features "
                                     "independent of the model",
                       "n": N_LOCAL, "eligible_positions": len(local_pool),
                       "matched_dimensions": ["substitution class (transition)", "intronic", "deep-intronic "
                                              "(>= 1 kb from exon boundary)", "same locus environment "
                                              f"(<= {LOCAL_RADIUS} bp)"],
                       "unmatched_dimensions": ["exact distance to exon boundary (pool spans a range)",
                                                "strand side (see n_upstream/n_downstream)",
                                                "local GC (reported, not matched)"],
                       "fully_matched": False, "summary": dist_summary(local), "variants": local},
        "NULL-TRANSCRIPT": {**common, "set": "NULL-TRANSCRIPT",
                            "definition": "deep-intronic synthetic transitions of the whole transcript, "
                                          f">= {MIN_EXON_DIST} bp from any exon boundary, outside the ISM window",
                            "n": N_TRANSCRIPT, "eligible_positions": len(tr_pool),
                            "note": "same rule family and seed as the first sealing of 2026-09-07 (then "
                                    "named NULL-A, superseded before any scoring); the pool is now computed "
                                    "uniformly as exon_distance >= 1000, so the sample is NOT byte-identical "
                                    "to NULL-A. Both manifests are kept",
                            "summary": dist_summary(transcript), "variants": transcript},
        "CTRL-POS": {**common, "set": "CTRL-POS",
                     "definition": "the four canonical splice-site positions of every intron (donor +1/+2, "
                                   "acceptor -2/-1), transition", "n": len(ctrl),
                     "validates": "sensitivity of the SPLICE readout only", "variants": ctrl},
    }
    shas = {}
    for name, obj in manifests.items():
        p = os.path.join(DIR, SETS[name])
        shas[name] = C.write_json(p, obj)
        io.open(p + ".sha256", "w").write(shas[name] + "\n")
    index = {
        "experiment": "EXP-024", "status": "PREREGISTERED, NOT EXECUTED", **common,
        "sets": {k: {"file": SETS[k], "sha256": shas[k], "n": manifests[k]["n"]} for k in SETS},
        "scoring_contract": {
            "16kb": {"context_bp": man["ism"]["sequence_context_bp"], "scorers": man["ism"]["scorers"],
                     "note": "identical to EXP-023 ISM: the candidate scalar is the same object"},
            "1Mb": {"context_bp": man["contacts"]["sequence_context_bp"],
                    "contact": {"scorer": "ContactMapScorer", "tracks": "all 28",
                                "predeclared_track": man["contacts"]["ontology_curie"]},
                    "panel": "work/alphagenome/tissue_matrix/panel_manifest.json"},
            "invariant": "candidate == null == controls for context length, scorer, ontology, strand "
                         "handling, centre mask, scalar aggregation, REF/ALT normalisation and "
                         "missing-output handling",
            "exclusion_rule": "API error after 3 retries, NaN, or missing track -> excluded and logged; "
                              f"> {int(100 * MAX_EXCLUDED_FRAC)} % excluded in any set -> run INCOMPLETE, "
                              "not interpreted",
        },
        "sensitivity_calibration": {"splice": "CTRL-POS", "dnase": "UNCALIBRATED FOR SENSITIVITY",
                                    "contact": "UNCALIBRATED FOR SENSITIVITY"},
        "confirmatory_family": ["splice-primary", "dnase-secondary", "contact-global"],
        "exploratory_prespecified": ["tissue x modality panel: descriptive; no cell becomes significant"],
        "statistics": {"percentile": "100 * #{|S_null| < |S_cand|} / N",
                       "p_emp": "(1 + #{|S_null| >= |S_cand|}) / (N + 1)",
                       "robust_z": "(S_cand - median) / (1.4826 * MAD)",
                       "mad_degenerate": f"MAD == 0 or MAD < {MAD_REL_EPS} * max|S_null| -> z undefined "
                                         "(degenerate null spread); report share of nulls equal to 0",
                       "multiplicity": "Benjamini-Hochberg over the confirmatory family only",
                       "primary_null": "NULL-LOCAL; NULL-TRANSCRIPT reported alongside",
                       "power_check": "fraction of CTRL-POS with p_emp < 0.05 under the splice readout; "
                                      "applies to the splice readout only"},
        "reading_rules": {
            "q>=0.05": "not unusually extreme relative to the preregistered null",
            "q<0.05": "unusually extreme relative to the preregistered null: logged as a concrete "
                      "contradiction for adjudication; changes no classification, ranking or branch",
            "power<0.5": "splice readout insufficiently sensitive in this gene: the candidate's splice "
                         "result is declared uninformative (not propagated to dnase or contact)",
            "forbidden_words": ["negative", "benign", "non-functional", "no regulatory effect"],
            "ceiling": "EXP-024 calibrates the model output. It does not calibrate pathogenicity, does "
                       "not reclassify the VUS, does not demonstrate absence of a second allele, does "
                       "not show the locus lacks function, and does not turn predicted contacts into "
                       "patient chromatin",
            "figures": "no plot changes status because it looks visually striking",
        },
        "figure_hierarchy": {"fig04Q_alphagenome_calibration": "MAIN diagnostic AlphaGenome calibration",
                             "fig04C_alphagenome_contact_maps + panel E": "secondary/main mechanistic model output",
                             "fig04T_alphagenome_tissue_matrix": "SUPPLEMENTARY, pre-specified exploratory context",
                             "fig04L_alphagenome_ism_logo": "SUPPLEMENTARY only; ISM-derived local sensitivity "
                                                            "logo, never motif discovery"},
    }
    sha_idx = C.write_json(INDEX, index)
    io.open(INDEX + ".sha256", "w").write(sha_idx + "\n")
    return index, shas, sha_idx


def load_sets() -> dict:
    idx = C.read_json(INDEX)
    if C.sha256_file(INDEX) != io.open(INDEX + ".sha256").read().strip():
        raise SystemExit("el indice del preregistro cambio")
    out = {}
    for name, info in idx["sets"].items():
        p = os.path.join(DIR, info["file"])
        if C.sha256_file(p) != info["sha256"]:
            raise SystemExit(f"{name} cambio despues de sellarse")
        out[name] = C.read_json(p)
    return idx, out


# ------------------------------------------------------- estadistica -----
def calibrate(s_cand: float, s_null) -> dict:
    s_null = np.asarray(s_null, dtype=float)
    a, c, n = np.abs(s_null), abs(float(s_cand)), len(s_null)
    med = float(np.median(s_null)); mad = float(np.median(np.abs(s_null - med)))
    degenerate = (mad == 0.0) or (mad < MAD_REL_EPS * float(np.abs(s_null).max()))
    return {"n": int(n), "percentile": float(100.0 * (a < c).sum() / n),
            "p_emp": float((1 + (a >= c).sum()) / (n + 1)),
            "robust_z": None if degenerate else float((s_cand - med) / (1.4826 * mad)),
            "robust_z_note": "undefined (degenerate null spread)" if degenerate else "ok",
            "null_median": med, "null_mad": mad, "share_null_exactly_zero": float((s_null == 0).mean())}


def bh(pvals) -> list:
    p = np.asarray(pvals, dtype=float); m = len(p)
    order = np.argsort(p); ranked = p[order] * m / (np.arange(m) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m); out[order] = np.minimum(q, 1.0)
    return out.tolist()


# --------------------------------------------------------------- the run ---
def run() -> int:
    """Se ejecuta UNA vez, bajo los manifests sellados, y SOLO cuando el mantenedor lo autorice."""
    from alphagenome.data import genome
    from alphagenome.models import dna_client, variant_scorers
    from src.model_outputs.alphagenome_ism import make_scorers, scalar_from
    from src.model_outputs import alphagenome_tissue_matrix as TM

    man = C.load_manifest(); idx, sets = load_sets(); panel = TM.load_panel()
    cand = man["candidate"]; chrom = cand["chromosome"]
    todo = [("candidate", "candidate", cand["position_1based"], cand["ref"], cand["alt"])]
    for name, s in sets.items():
        todo += [(name, v.get("role", name), v["position_1based"], v["ref"], v["alt"]) for v in s["variants"]]
    model = dna_client.create(C.api_key(), model_version=man["model"]["model_version_requested"])
    ism_scorers = make_scorers(man["ism"]["scorers"]); contact = variant_scorers.ContactMapScorer()
    panel_scorers = TM.make_scorers(panel)
    print(f"  -> {len(todo)} variantes; solo el locus del candidato es dato del paciente")
    rows, excluded, t0 = [], [], time.time()
    for i, (kind, role, pos, ref, alt) in enumerate(todo):
        v = genome.Variant(chromosome=chrom, position=pos, reference_bases=ref, alternate_bases=alt)
        row = None
        for attempt in range(3):
            try:
                r16 = model.score_variant(interval=v.reference_interval.resize(man["ism"]["sequence_context_bp"]),
                                          variant=v, variant_scorers=ism_scorers)
                r1m = model.score_variant(interval=v.reference_interval.resize(man["contacts"]["sequence_context_bp"]),
                                          variant=v, variant_scorers=[contact] + panel_scorers)
                X = np.asarray(r1m[0].X, dtype=float).ravel()
                cur = r1m[0].var["ontology_curie"].astype(str).to_numpy()
                row = {"kind": kind, "role": role, "offset_bp": pos - cand["position_1based"], "ref": ref,
                       "alt": alt, "splice": scalar_from(r16[0], man["ism"]["scorers"][0])[0],
                       "dnase": scalar_from(r16[1], man["ism"]["scorers"][1])[0],
                       "contact": float(X[np.flatnonzero(cur == man["contacts"]["ontology_curie"])[0]]),
                       "contact_all": dict(zip(cur.tolist(), X.tolist())),
                       "panel": TM.extract(r1m[1:], panel)}
                if not all(np.isfinite(row[k]) for k in FAMILY):
                    raise ValueError("NaN en un escalar")
                break
            except Exception as e:                         # noqa: BLE001
                err = f"{type(e).__name__}: {e}"[:160]
                time.sleep(5 * (attempt + 1))
        if row is None:
            excluded.append({"kind": kind, "offset_bp": pos - cand["position_1based"], "reason": err})
        else:
            rows.append(row)
        if (i + 1) % 25 == 0:
            print(f"    {i + 1}/{len(todo)}  {time.time() - t0:.0f} s  excluidas {len(excluded)}", flush=True)
    os.makedirs(DIR, exist_ok=True)
    sha_raw = C.write_json(os.path.join(DIR, "raw_scores.json.gz"), {"rows": rows, "excluded": excluded}, gz=True)
    io.open(os.path.join(DIR, "raw_scores.tsv"), "w", encoding="utf-8", newline="\n").write(
        "kind\trole\toffset_bp\tref\talt\tsplice\tdnase\tcontact\n" + "".join(
            f"{r['kind']}\t{r['role']}\t{r['offset_bp']}\t{r['ref']}\t{r['alt']}\t{r['splice']!r}\t"
            f"{r['dnase']!r}\t{r['contact']!r}\n" for r in rows))

    incomplete = {}
    for name, s in sets.items():
        got = sum(r["kind"] == name for r in rows)
        incomplete[name] = (s["n"] - got) / s["n"] > MAX_EXCLUDED_FRAC
    if rows[0]["kind"] != "candidate":
        incomplete["candidate"] = True
    c = rows[0]
    by = {name: [r for r in rows if r["kind"] == name] for name in sets}
    stats = {}
    for k in FAMILY:
        stats[k] = {"NULL-LOCAL": calibrate(c[k], [r[k] for r in by["NULL-LOCAL"]]),
                    "NULL-TRANSCRIPT": calibrate(c[k], [r[k] for r in by["NULL-TRANSCRIPT"]])}
    q = bh([stats[k]["NULL-LOCAL"]["p_emp"] for k in FAMILY])
    for k, qq in zip(FAMILY, q):
        stats[k]["q_bh_confirmatory"] = qq
    null_local_splice = [r["splice"] for r in by["NULL-LOCAL"]]
    power = float(np.mean([calibrate(r["splice"], null_local_splice)["p_emp"] < 0.05 for r in by["CTRL-POS"]]))
    reading = {}
    for k in FAMILY:
        reading[k] = ("unusually extreme relative to the preregistered null (logged as a concrete "
                      "contradiction for adjudication)" if stats[k]["q_bh_confirmatory"] < 0.05
                      else "not unusually extreme relative to the preregistered null")
        if k != "splice":
            reading[k] += " [UNCALIBRATED FOR SENSITIVITY]"
    if power < 0.5:
        reading["splice"] += " [POWER CHECK FAILED: splice readout insufficiently sensitive in this gene; " \
                             "the candidate's splice result is uninformative]"
    meta = {"run": "calibration", "status": "INCOMPLETE" if any(incomplete.values()) else "COMPLETE",
            "figure_class": "MODEL_OUTPUT", "evidence_origin": "PREDICTED+DERIVED",
            "source_type": "predicted_not_patient_measurement", "finished_utc": C.now_utc(),
            "environment": C.environment(), "manifest_sha256": io.open(C.MANIFEST + ".sha256").read().strip(),
            "prereg_index_sha256": io.open(INDEX + ".sha256").read().strip(),
            "sets_sha256": {k: v["sha256"] for k, v in idx["sets"].items()},
            "panel_manifest_sha256": TM.panel_sha(), "n_scored": len(rows), "n_excluded": len(excluded),
            "incomplete": incomplete, "files": {"raw_scores": "raw_scores.json.gz", "raw_scores_sha256": sha_raw},
            "candidate_scores": {k: c[k] for k in FAMILY}, "calibration": stats,
            "power_check_splice": power, "reading": reading, "random_seed": idx["random_seed"]}
    C.write_json(os.path.join(DIR, "metadata.json"), meta)
    for k in FAMILY:
        s = stats[k]["NULL-LOCAL"]
        print(f"  {k:<8} pct {s['percentile']:5.1f}  p {s['p_emp']:.4f}  q {stats[k]['q_bh_confirmatory']:.4f}  -> {reading[k][:70]}")
    print(f"  potencia splice (CTRL-POS): {power:.2f}   estado: {meta['status']}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "freeze"
    if cmd == "freeze":
        idx, shas, sha_idx = freeze()
        for k, v in idx["sets"].items():
            print(f"  {k:<16} n={v['n']:<4} sha256 {v['sha256']}")
        print(f"  indice           sha256 {sha_idx}")
        f = idx["candidate_features_model_independent"]
        print(f"  candidato: {f['class']}, intron {f['intron_index_of_n'][0]} de {f['intron_index_of_n'][1]}, "
              f"a {f['distance_to_nearest_exon_bp']} pb del exon mas cercano, GC(101 pb) {f['gc_101bp']}")
    elif cmd == "run":
        sys.exit(run())
    else:
        raise SystemExit("uso: freeze | run")
