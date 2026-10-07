"""Cada pregunta abierta, con la siguiente observación que cambia una decisión, y cada brazo con su regla de fracaso.

Por qué existe
    Las soluciones ya estaban en el proyecto, pero repartidas: la tabla de preguntas abiertas del README y de
    Track 1 §7b, Track 1 §7a, las reglas de descarte de Track 2 §5, el Safe Rescue Corridor de Track 2 §6, el
    residual renal y la línea base externa. El jurado tiene que poder verlas juntas en una página.

Qué dice y qué no
    No todas las observaciones resuelven su pregunta: algunas solo la estrechan (un RNA/long-read negativo no
    excluye toda lesión, unas llamadas de HLA-DRB1 que aguantan abren otra auditoría). Por eso el titular habla
    de la siguiente observación que cambia una decisión, no de un experimento decisivo para todo.
    El árbol separa dos carriles: el genotipo del niño y los experimentos que pueden empezar ya en células
    editadas. Los resultados de los brazos solo importan para este niño cuando el genotipo causal está resuelto
    (trans, o cis más un segundo alelo encontrado).

Cómo se dibuja
    Página HTML autocontenida (sin fuentes, scripts ni servicios externos). El JS dibuja las flechas reales del
    árbol y enlaza cada pregunta con su nodo. Playwright (Edge o Chromium) la fotografía a 2x para el PNG.
    El texto evita flechas como carácter, punto y coma y separadores de punto medio.

        python src/figures/fig15_decision_map.py      # HTML siempre; PNG si hay playwright

Guardia
    No es ciencia nueva: cada desenlace y cada regla de descarte tiene que aparecer, literal, en su documento
    de origen. Si alguien cambia el informe y no la figura, o al revés, no se genera nada.
"""
import io
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, ".")

SLUG = "fig15_decision_map"
OUT_DIR = "figures/pub"
FIG_CLASS, ORIGIN = "SYNTHESIS", "DERIVED+EXTERNAL"

SOURCES = {"README": "README.md", "T1": "reports/TRACK1_REPORT.md", "T2": "reports/TRACK2_REPORT.md",
           "RENAL": "docs/RENAL_RESIDUAL.md", "BASE": "docs/EXTERNAL_BASELINE.md"}

# (pregunta, siguiente observación, un desenlace, el otro desenlace, qué hace falta, nodo del árbol,
#  ¿necesita a la familia o al niño?)
TRACK1 = [
    ("Phase of the two alleles is unresolved",
     "Parental genotyping at both sites, or targeted long-read phasing of the child",
     "Trans: the truncating and missense alleles sit on opposite copies, matching the canonical MVA1 configuration. "
     "The missense still needs functional evidence",
     "Cis: this pair cannot be the recessive explanation, and the hidden-allele search becomes the primary question",
     "Parents, or the child's DNA for long reads", "phase", True),
    ("The missense is a VUS",
     "Variant expressed in isogenic cells: BUBR1 abundance and turnover, kinetochore localisation, checkpoint "
     "arrest, segregation errors, with wild-type and known MVA-allele controls",
     "Reduced abundance or checkpoint failure: functional support for pathogenicity",
     "Normal on every readout: the pair is weakened, and a hidden allele or another gene becomes more likely",
     "Engineered cells only", "trans", False),
    ("A hidden second allele is not excluded",
     "RNA-seq and targeted long reads of the child",
     "A splice or intronic lesion is found: a candidate second allele is located",
     "Nothing found: this route weakens without excluding every lesion",
     "Child's RNA and DNA", "cis", True),
    ("Nephrocalcinosis is supported by neither phenotype check",
     "Prenatal history (polyhydramnios or oligohydramnios), electrolytes, renin and aldosterone",
     "A tubulopathy pattern: the mixed-diagnosis branch reopens",
     "No such pattern: the residual stays open and no second diagnosis is claimed",
     "Clinical records", "indep", True),
    ("Exomiser's #1, HLA-DRB1, is an open audit flag",
     "Next audit step: mapping uniqueness, call quality and paralog context at the locus",
     "The calls are mapping artefacts: the flag closes",
     "The calls hold: HLA-DRB1 earns a full audit, like the other competitors",
     "Existing alignment", "indep", False),
    ("Does the method work beyond this child?",
     "An external validation study, to be preregistered: the frozen pipeline run unchanged on previously solved "
     "cases with known causal genes, blinded to the answer",
     "The known genes rank within a top-k threshold set before the run: evidence that the procedure transfers",
     "They do not: the contribution is the audit trail, not the ranking",
     "Public solved cases", "indep", False),
]

# Brazos de Track 2. `discard` es la regla del informe y `tag` repite una frase literal del informe.
TRACK2 = [
    {"route": "Allele-directed: the truncating allele", "title": "Azithromycin",
     "role": "candidate hypothesis: readthrough of the premature stop codon",
     "tag": "Computationally weakened by EXP-029, not eliminated",
     "measure": "Available PTC transcript, readthrough above noise and function of the full-length product, at "
                "attainable exposure",
     "dlabel": "Discarded if",
     "discard": "PTC transcript abundance is too low to permit detectable rescue at attainable exposure, if "
                "readthrough does not exceed noise at attainable exposure, or if the inserted amino acid does not "
                "restore BUBR1 function",
     "needs": "Engineered cells only"},
    {"route": "Abundance and proteostasis: the missense", "title": "Arimoclomol",
     "role": "candidate hypothesis and falsification sentinel, with a ca-HSF1 positive control and an HSP70 "
             "overexpression comparator",
     "tag": "Verified counterexample",
     "measure": "HSP induction at attainable exposure first, then BUBR1 abundance, then function at matched levels",
     "dlabel": "Discarded if",
     "discard": "it does not raise HSP at attainable exposure, or if it raises HSP without raising BUBR1. "
                "Chaperone biology as a whole is not discarded: the HSP90 route stays open",
     "needs": "Engineered cells only"},
    {"route": "Tolerance of aneuploidy without correcting BUBR1", "title": "Sirolimus",
     "role": "adversarial comparator, not a therapeutic nominee", "tag": "Boundary marker",
     "measure": "CIN, micronuclei, segregation errors and clonogenic survival, read together",
     "dlabel": "Discarded as a therapeutic candidate",
     "discard": "the moment it increases CIN, micronuclei, segregation errors or clonogenic survival. As a "
                "comparator its failure is the result",
     "needs": "Engineered cells only"},
    {"route": "Every arm that survives its own rule", "title": "Safe Rescue Corridor",
     "role": "the shared rule each arm is judged by", "tag": "Shared rule, not an invention of this project",
     "measure": "New segregation errors per completed mitosis at matched proliferation, and clonogenic survival of "
                "unstable cells, in an isogenic aneuploid/euploid pair",
     "dlabel": "An arm advances only if",
     "discard": "new segregation errors per completed mitosis fall at matched proliferation and clonogenic "
                "survival of unstable cells does not rise. More survival of unstable cells is a veto, even if "
                "another readout improves",
     "needs": "Engineered cells only"},
]

PRECEDENT = ("Why a rescue route exists at all: re-expressing BUBR1 restored the checkpoint in MVA patient cells. "
             "That rescue was genetic and the alleles were not this child's (Suijkerbuijk et al. 2010, "
             "PMID 20516114). Our bounded literature search found no pharmacologic rescue tested in BUB1B patient "
             "cells.")
ARMS_NOTE = ("Each discard rule above is specific to its route. An arm that survives it must still pass the Safe "
             "Rescue Corridor: a rise in BUBR1 alone is not a rescue.")

# Fragmentos que deben aparecer LITERALES (sin marcas de Markdown) en su documento de origen.
GUARDS = [
    ("README", "the truncating and missense alleles sit on opposite copies, matching the canonical MVA1 configuration. "
               "The missense still needs functional evidence"),
    ("README", "this pair cannot be the recessive explanation, and the hidden-allele search becomes the primary "
               "question"),
    ("README", "Variant expressed in isogenic cells: BUBR1 abundance and turnover, kinetochore localisation, "
               "checkpoint arrest, segregation errors, with wild-type and known MVA-allele controls"),
    ("README", "Reduced abundance or checkpoint failure: functional support for pathogenicity"),
    ("README", "Normal on every readout: the pair is weakened, and a hidden allele or another gene becomes more "
               "likely"),
    ("README", "An external validation study, to be preregistered: the frozen pipeline run unchanged on previously "
               "solved cases with known causal genes, blinded to the answer"),
    ("README", "The known genes rank within a top-k threshold set before the run: evidence that the procedure "
               "transfers"),
    ("README", "They do not: the contribution is the audit trail, not the ranking"),
    ("README", "Fewer new segregation errors per completed mitosis at matched proliferation, without extra "
               "clonogenic survival of unstable cells"),
    ("README", "More survival of unstable cells: veto, even if another readout improves"),
    ("README", "it is the first branching observation"),
    ("T1", "the truncating and missense alleles sit on opposite copies, matching the canonical MVA1 configuration"),
    ("T1", "RNA-seq and targeted long reads remain routes for a hidden allele"),
    ("RENAL", "¿hubo polihidramnios u oligohidramnios?"),
    ("RENAL", "electrolitos/renina/aldosterona"),
    ("BASE", "Nada de lo hecho aquí comprueba la unicidad de mapeo, la calidad de las llamadas ni el contexto de "
             "pseudogén"),
    ("T2", "Discarded if PTC transcript abundance is too low to permit detectable rescue at attainable exposure, "
           "if readthrough does not exceed noise at attainable exposure, or if the inserted amino acid does not "
           "restore BUBR1 function"),
    ("T2", "Discarded if it does not raise HSP at attainable exposure, or if it raises HSP without raising BUBR1"),
    ("T2", "the HSP90 route stays open"),
    ("T2", "Discarded as a therapeutic candidate the moment it increases CIN, micronuclei, segregation errors or "
           "clonogenic survival"),
    ("T2", "As an adversarial comparator it is not discarded: there, its failure is the result"),
    ("T2", "chromosome instability falls and clonogenic survival does not rise"),
    ("T2", "Computationally weakened by EXP-029, not eliminated"),
    ("T2", "re-expression of BUBR1 doubled their response to nocodazole"),
    ("T2", "Our bounded literature search found no pharmacologic rescue tested in BUB1B patient cells"),
    ("T2", "Verified counterexample"),
    ("T2", "not as a candidate, but as the boundary marker"),
    ("T2", "The corridor is a shared rule, not an invention of this project"),
]

# El texto de la figura no lleva flechas como carácter, punto y coma ni punto medio como separador.
FORBIDDEN_MARKS = ("→", ";", "·")


def _plain(path):
    s = io.open(path, encoding="utf-8").read()
    s = re.sub(r"(?m)^\s*>\s?", "", s)  # marcadores de cita de Markdown
    s = re.sub(r"[*`]", "", s)
    return re.sub(r"\s+", " ", s)


def check_sources():
    texts = {k: _plain(p) for k, p in SOURCES.items()}
    missing = [(k, frag) for k, frag in GUARDS if re.sub(r"\s+", " ", frag) not in texts[k]]
    if missing:
        raise SystemExit("fig15: estos fragmentos ya no están literales en su fuente; revisar la figura o el "
                         "documento antes de generarla:\n" + "\n".join(f"  [{k}] {f[:90]}" for k, f in missing))
    return len(GUARDS)


def _split(outcome):
    """'Trans: the truncating…' se parte en etiqueta y cuerpo; el texto no cambia."""
    k, _, body = outcome.partition(": ")
    return {"key": k, "body": body}


def data(n_guards):
    d = {
        "track1": [{"q": q, "obs": o, "a": _split(a), "b": _split(b), "needs": n, "node": nd, "family": fam}
                   for q, o, a, b, n, nd, fam in TRACK1],
        "track2": TRACK2,
        "precedent": PRECEDENT,
        "armsNote": ARMS_NOTE,
        "guards": n_guards,
        "stamp": "Figure class: synthesis    Evidence origin: derived, external",
        "sources": "README open-question table, Track 1 §7a and §7b, Track 2 §1, §5 and §6, "
                   "docs/RENAL_RESIDUAL.md and docs/EXTERNAL_BASELINE.md",
    }
    text = json.dumps(d, ensure_ascii=False)
    bad = [m for m in FORBIDDEN_MARKS if m in text]
    if bad:
        raise SystemExit(f"fig15: el texto de la figura lleva signos vetados por estilo: {bad}")
    return d


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Decision map</title>
<style>
:root{
  --page:#F3F5F4; --card:#FFFFFF; --ink:#16212B; --muted:#5A6670; --faint:#8A949B; --line:#DCE1E3;
  --blue:#0B6FA4; --blue-tint:#E8F1F7; --green:#047857; --green-tint:#E6F3EE;
  --verm:#B8470C; --verm-tint:#FBEDE5; --gold:#9A6400; --gold-tint:#F8F0DE; --violet:#5B4B8A; --violet-tint:#EFECF6;
  --shadow:0 1px 2px rgba(22,33,43,.06),0 4px 14px rgba(22,33,43,.05);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --page:#11171C; --card:#18212A; --ink:#E6ECEF; --muted:#A3AEB5; --faint:#76838B; --line:#2B3640;
  --blue:#5AB0E0; --blue-tint:#15283A; --green:#4CC59A; --green-tint:#13302A; --verm:#F08A50; --verm-tint:#3A2016;
  --gold:#E2B04A; --gold-tint:#33291A; --violet:#B3A4E6; --violet-tint:#272238; --shadow:none}}
:root[data-theme="dark"]{
  --page:#11171C; --card:#18212A; --ink:#E6ECEF; --muted:#A3AEB5; --faint:#76838B; --line:#2B3640;
  --blue:#5AB0E0; --blue-tint:#15283A; --green:#4CC59A; --green-tint:#13302A; --verm:#F08A50; --verm-tint:#3A2016;
  --gold:#E2B04A; --gold-tint:#33291A; --violet:#B3A4E6; --violet-tint:#272238; --shadow:none}
*{box-sizing:border-box}
html,body{margin:0;background:var(--page);color:var(--ink)}
body{font:14px/1.45 "Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  font-variant-numeric:tabular-nums}
.sheet{width:min(1600px,100%);margin:0 auto;padding:40px 48px 28px;position:relative}
.stamp{position:absolute;top:14px;right:22px;font-size:11px;color:var(--faint);white-space:pre}
.eyebrow{font-size:11.5px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;color:var(--muted)}
h1{font:700 32px/1.15 "Segoe UI Variable Display","Segoe UI",system-ui,sans-serif;letter-spacing:-.5px;
  margin:8px 0 10px;text-wrap:balance;max-width:1300px}
.deck{font-size:15.5px;line-height:1.55;color:var(--muted);max-width:1180px;margin:0}
.controls{display:flex;gap:10px;align-items:center;margin-top:18px}
.controls button{font:600 12.5px/1 inherit;color:var(--ink);background:var(--card);border:1px solid var(--line);
  border-radius:999px;padding:9px 14px;cursor:pointer}
.controls button[aria-pressed="true"]{background:var(--ink);color:var(--card);border-color:var(--ink)}
.controls button:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.controls span{font-size:12.5px;color:var(--muted)}
body.export .controls{display:none}
.grid{display:grid;grid-template-columns:610px minmax(0,1fr);grid-template-areas:"a b" "c c";
  column-gap:32px;row-gap:30px;margin-top:26px;align-items:start}
.sec-a{grid-area:a}.sec-b{grid-area:b}.sec-c{grid-area:c}
.panel-h{display:flex;align-items:baseline;gap:10px;margin:0 0 12px;flex-wrap:wrap}
.panel-h b{font-size:12px;font-weight:800;color:var(--card);background:var(--ink);border-radius:5px;
  padding:3px 7px;letter-spacing:.5px}
.panel-h h2{font-size:17px;font-weight:700;margin:0;letter-spacing:-.1px}
.panel-h small{font-size:12.5px;color:var(--muted)}

/* A: orden de decisiones, en dos carriles */
.flow{position:relative;background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:16px 18px 18px;box-shadow:var(--shadow)}
.flow svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible}
.nodes{display:grid;grid-template-columns:1fr 1fr 1.08fr;column-gap:14px;position:relative}
.lane{font-size:10.5px;font-weight:800;letter-spacing:1.2px;text-transform:uppercase;color:var(--faint);
  padding:0 2px 8px}
.lane.g{grid-column:1/3}.lane.x{grid-column:3}
.node{position:relative;border-radius:11px;padding:11px 12px 11px;background:var(--card);
  border:1.5px solid var(--line);transition:box-shadow .15s,transform .15s;z-index:1}
.node .k{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;
  font-size:11.5px;font-weight:800;color:var(--card);background:var(--ink);margin-right:7px;vertical-align:-1px}
.node h3{font-size:13.8px;margin:0 0 4px;font-weight:700;line-height:1.3}
.node p{margin:0;font-size:12.2px;color:var(--muted);line-height:1.42}
.n-phase{grid-column:1/3;grid-row:2;align-self:start;border-color:var(--blue);background:var(--blue-tint)}
.n-arms{grid-column:3;grid-row:2;border-color:var(--gold);background:var(--gold-tint)}
.n-cis{grid-column:1;grid-row:3;align-self:start;margin-top:54px;border-color:var(--verm);background:var(--verm-tint)}
.n-trans{grid-column:2;grid-row:3;align-self:start;margin-top:54px;border-color:var(--green);background:var(--green-tint)}
.n-corr{grid-column:3;grid-row:3;margin-top:54px;border:2px solid var(--ink)}
.n-gate{grid-column:1/3;grid-row:4;margin-top:56px;border-color:var(--violet);background:var(--violet-tint)}
.n-indep{grid-column:1/4;grid-row:5;margin-top:18px;border-style:dashed;background:transparent}
.n-indep ul{margin:6px 0 0;padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:5px 18px}
.n-indep li{font-size:12.2px;color:var(--muted);padding-left:14px;position:relative}
.n-indep li::before{content:"";position:absolute;left:2px;top:7px;width:5px;height:5px;border-radius:50%;
  background:var(--faint)}
.pill{position:absolute;transform:translate(-50%,-50%);font-size:11px;font-weight:700;padding:3px 9px;
  border-radius:999px;background:var(--card);border:1px solid currentColor;white-space:nowrap;z-index:2}
.node.lit,.row.lit,.arm.lit{box-shadow:0 0 0 3px rgba(11,111,164,.28)}
.node.lit{transform:translateY(-1px)}

/* B: Track 1 */
.t1{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);overflow:hidden}
.t1 .head,.t1 .row{display:grid;grid-template-columns:178px minmax(0,1fr) minmax(0,1.05fr) minmax(0,1.05fr);
  gap:12px;padding:11px 14px}
.t1 .head{font-size:10.5px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--blue);
  border-bottom:2px solid var(--blue);padding-top:12px;padding-bottom:9px}
.t1 .row{border-top:1px solid var(--line);transition:background .15s}
.t1 .row:first-of-type{border-top:0}
.q{font-weight:700;font-size:13.2px;line-height:1.35}
.needs{display:inline-block;margin-top:7px;font-size:10.8px;font-weight:700;letter-spacing:.2px;padding:3px 8px;
  border-radius:6px;background:var(--page);color:var(--muted);border:1px solid var(--line)}
.needs.now{color:var(--green);border-color:var(--green);background:var(--green-tint)}
.obs{font-size:12.6px;color:var(--ink)}
.out{border-radius:9px;padding:8px 10px;font-size:12.4px;line-height:1.42}
.out b{display:block;font-size:11.8px;margin-bottom:2px}
.out.a{background:var(--blue-tint)} .out.a b{color:var(--blue)}
.out.b{background:var(--verm-tint)} .out.b b{color:var(--verm)}
.dim{opacity:.32}

/* C: Track 2 */
.precedent{margin:0 0 12px;padding:11px 14px;border-radius:10px;background:var(--card);border:1px solid var(--line);
  font-size:13px;color:var(--muted)}
.precedent strong{color:var(--ink)}
.arms{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
.arm{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px 13px;
  box-shadow:var(--shadow);display:flex;flex-direction:column;gap:8px}
.arm .route{font-size:11px;font-weight:800;letter-spacing:1.1px;text-transform:uppercase;color:var(--gold)}
.arm h3{margin:0;font-size:18px;letter-spacing:-.2px}
.arm h3 span{display:block;margin-top:3px;font-size:13px;line-height:1.4;font-weight:500;color:var(--muted);letter-spacing:0}
.tag{align-self:flex-start;font-size:11.5px;font-weight:700;padding:3px 9px;border-radius:999px;
  background:var(--gold-tint);color:var(--gold)}
.lab{font-size:10.5px;font-weight:800;letter-spacing:1.1px;text-transform:uppercase;color:var(--faint);margin-bottom:2px}
.measure{font-size:13px}
.discard{background:var(--verm-tint);border-radius:9px;padding:9px 11px;font-size:12.8px;line-height:1.42}
.discard .lab{color:var(--verm)}
.arm .needs{align-self:flex-start;margin-top:auto}
.arm.corr{border:2px solid var(--ink)}
.arm.corr .route{color:var(--ink)}
.arm.corr .tag{background:var(--page);color:var(--ink);border:1px solid var(--line)}
.arm.corr .discard{background:var(--green-tint)} .arm.corr .discard .lab{color:var(--green)}
.armsnote{margin:12px 0 0;font-size:12.8px;color:var(--muted)}
.armsnote strong{color:var(--ink)}

footer{display:flex;justify-content:space-between;gap:24px;margin-top:22px;padding-top:12px;
  border-top:1px solid var(--line);font-size:11.5px;color:var(--faint)}
@media (max-width:1100px){.grid{grid-template-columns:1fr;grid-template-areas:"a" "b" "c"}.t1 .head{display:none}
  .t1 .row{grid-template-columns:1fr}.arms{grid-template-columns:1fr}.sheet{padding:28px 16px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head>
<body>
<div class="sheet">
  <div class="stamp" id="stamp"></div>
  <div class="eyebrow">MOSAIC RESCUE decision map</div>
  <h1>Every open question has a decision-changing next observation, and every Track 2 arm a written condition for failure</h1>
  <p class="deck">Track 1 questions need new observations, not more computation on this genome. Some observations would
    settle a question and others would only narrow it. Track 2 arms are preclinical hypotheses, for no patient, and each
    discard rule is the one written in the report before any experiment.</p>
  <div class="controls">
    <button id="now" aria-pressed="false">Show what can start without the family</button>
    <span>Hover a question to see where it sits in the order of decisions.</span>
  </div>

  <div class="grid">
    <section class="sec-a">
      <div class="panel-h"><b>A</b><h2>The order of decisions</h2></div>
      <div class="flow" id="flow">
        <svg id="wires" aria-hidden="true"></svg>
        <div class="nodes">
          <div class="lane g">The child's genotype</div><div class="lane x">Experiments that can start now</div>
          <div class="node n-phase" data-node="phase"><h3><span class="k">1</span>Phase of the two BUB1B alleles</h3>
            <p>Parental genotyping or targeted long-read phasing. The first branching observation.</p></div>
          <div class="node n-arms" data-node="arms"><h3><span class="k">2</span>Three experimental arms, preclinical</h3>
            <p>Two candidate hypotheses and one adversarial comparator, in engineered cells, in parallel with phase.</p></div>
          <div class="node n-cis" data-node="cis"><h3>Cis</h3>
            <p>The current pair cannot explain recessive MVA1. Search for a hidden second allele.</p></div>
          <div class="node n-trans" data-node="trans"><h3>Trans</h3>
            <p>The current pair stays relevant. Test the missense at matched expression.</p></div>
          <div class="node n-corr" data-node="corr"><h3><span class="k">3</span>Safe Rescue Corridor</h3>
            <p>An arm advances only if new segregation errors per completed mitosis fall at matched proliferation and
              clonogenic survival of unstable cells does not rise.</p></div>
          <div class="node n-gate" data-node="gate"><h3>Patient relevance</h3>
            <p>Arm results matter for this child only once the causal genotype is resolved: trans, or cis plus a second
              allele found.</p></div>
          <div class="node n-indep" data-node="indep"><h3>Independent of phase</h3>
            <ul><li>Nephrocalcinosis: clinical records</li>
              <li>HLA-DRB1 flag: the existing alignment</li>
              <li>Generality of the method: a preregistered study on solved cases</li>
              <li>Mosaic fraction: a direct cell-level measurement. The WGS detector failed its validation (EXP-027)
                and was not run on the child.</li></ul></div>
        </div>
      </div>
    </section>

    <section class="sec-b">
      <div class="panel-h"><b>B</b><h2>Track 1: the next observation for each open question</h2></div>
      <div class="t1" id="t1">
        <div class="head"><div>Open question</div><div>Next observation that changes a decision</div>
          <div>If it comes out one way</div><div>If it comes out the other</div></div>
      </div>
    </section>

    <section class="sec-c">
      <div class="panel-h"><b>C</b><h2>Track 2: experimental arms</h2>
        <small>preclinical, with discard rules as written in the Track 2 report</small></div>
      <p class="precedent" id="precedent"></p>
      <div class="arms" id="arms"></div>
      <p class="armsnote" id="armsnote"></p>
    </section>
  </div>

  <footer><div id="sources"></div><div>Generated by src/figures/fig15_decision_map.py. No new result, no patient
    data or coordinates.</div></footer>
</div>

<script>
const D = __DATA__;
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls;
  if (html !== undefined) e.innerHTML = html; return e; };
const esc = s => s.replace(/[&<>]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
const lead = (s, cut) => { const i = s.indexOf(cut); return "<strong>" + esc(s.slice(0, i + cut.length)) +
  "</strong>" + esc(s.slice(i + cut.length)); };

if (new URLSearchParams(location.search).has("export")) document.body.classList.add("export");
$("#stamp").textContent = D.stamp;
$("#sources").textContent = `Sources, checked verbatim before generating (${D.guards} fragments): ${D.sources}.`;
$("#precedent").innerHTML = lead(D.precedent, ":");
$("#armsnote").innerHTML = lead(D.armsNote, ".");

const t1 = $("#t1");
D.track1.forEach(r => {
  const row = el("div", "row" + (r.family ? " dim-able" : ""));
  row.dataset.node = r.node;
  row.append(
    el("div", "", `<div class="q">${esc(r.q)}</div><span class="needs${r.family ? "" : " now"}">${esc(r.needs)}</span>`),
    el("div", "obs", esc(r.obs)),
    el("div", "out a", `<b>${esc(r.a.key)}</b>${esc(r.a.body)}`),
    el("div", "out b", `<b>${esc(r.b.key)}</b>${esc(r.b.body)}`));
  t1.append(row);
});

const arms = $("#arms");
D.track2.forEach((a, i) => {
  const c = el("article", "arm" + (i === 3 ? " corr" : ""));
  c.dataset.node = i === 3 ? "corr" : "arms";
  c.innerHTML = `<div class="route">${esc(a.route)}</div>
    <h3>${esc(a.title)} <span>${esc(a.role)}</span></h3>
    <span class="tag">${esc(a.tag)}</span>
    <div><div class="lab">What the experiment must measure</div><div class="measure">${esc(a.measure)}</div></div>
    <div class="discard"><div class="lab">${esc(a.dlabel)}</div>${esc(a.discard)}</div>
    <span class="needs now">${esc(a.needs)}</span>`;
  arms.append(c);
});

// Flechas reales entre nodos, recalculadas con el layout.
const NS = "http://www.w3.org/2000/svg";
function wire() {
  const svg = $("#wires"), box = $("#flow").getBoundingClientRect();
  svg.innerHTML = ""; document.querySelectorAll(".pill").forEach(p => p.remove());
  const css = getComputedStyle(document.documentElement);
  const col = n => css.getPropertyValue(n).trim();
  const defs = document.createElementNS(NS, "defs");
  ["blue", "green", "verm", "ink", "violet"].forEach(id => {
    const m = document.createElementNS(NS, "marker");
    Object.entries({id: "h-" + id, viewBox: "0 0 10 10", refX: 8.5, refY: 5, markerWidth: 7, markerHeight: 7,
      orient: "auto-start-reverse"}).forEach(([k, v]) => m.setAttribute(k, v));
    const p = document.createElementNS(NS, "path"); p.setAttribute("d", "M0,0 L10,5 L0,10 z");
    p.setAttribute("fill", col("--" + id)); m.append(p); defs.append(m);
  });
  svg.append(defs);
  const r = s => { const b = $(s).getBoundingClientRect();
    return {x: b.left - box.left, y: b.top - box.top, w: b.width, h: b.height}; };
  const pill = (x, y, text, color) => { const t = el("span", "pill", text); t.style.left = x + "px";
    t.style.top = y + "px"; t.style.color = col("--" + color); $("#flow").append(t); };
  const link = (x1, y1, x2, y2, color, opts = {}) => {
    const p = document.createElementNS(NS, "path"), my = (y1 + y2) / 2;
    const d = opts.horizontal ? `M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2 - 2},${y2}`
                              : `M${x1},${y1} C${x1},${my} ${x2},${my} ${x2},${y2 - 2}`;
    p.setAttribute("d", d); p.setAttribute("fill", "none"); p.setAttribute("stroke", col("--" + color));
    p.setAttribute("stroke-width", 2); p.setAttribute("marker-end", `url(#h-${color})`);
    if (opts.dashed) p.setAttribute("stroke-dasharray", "5 4");
    svg.append(p);
    if (opts.label) pill((x1 + x2) / 2 + (opts.lx || 0), my + (opts.ly || 0), opts.label, color);
  };
  const ph = r(".n-phase"), ci = r(".n-cis"), tr = r(".n-trans"), ar = r(".n-arms"), co = r(".n-corr"),
        ga = r(".n-gate");
  link(ph.x + ph.w * .25, ph.y + ph.h, ci.x + ci.w / 2, ci.y, "verm", {label: "if cis"});
  link(ph.x + ph.w * .75, ph.y + ph.h, tr.x + tr.w / 2, tr.y, "green", {label: "if trans"});
  link(ar.x + ar.w / 2, ar.y + ar.h, co.x + co.w / 2, co.y, "ink");
  link(tr.x + tr.w / 2, tr.y + tr.h, ga.x + ga.w * .72, ga.y, "green");
  link(ci.x + ci.w / 2, ci.y + ci.h, ga.x + ga.w * .28, ga.y, "verm",
       {dashed: true, label: "only with a second allele", ly: -2});
  link(ga.x + ga.w, ga.y + ga.h / 2, co.x + co.w / 2, co.y + co.h, "violet",
       {label: "decides relevance to this child", lx: 18, ly: 14});
}

// Enlaces: pasar por una pregunta ilumina su nodo, y al revés.
function light(node, on) {
  document.querySelectorAll(`[data-node="${node}"]`).forEach(e => e.classList.toggle("lit", on));
}
document.querySelectorAll("[data-node]").forEach(e => {
  e.addEventListener("mouseenter", () => light(e.dataset.node, true));
  e.addEventListener("mouseleave", () => light(e.dataset.node, false));
});
$("#now").addEventListener("click", ev => {
  const on = ev.currentTarget.getAttribute("aria-pressed") !== "true";
  ev.currentTarget.setAttribute("aria-pressed", on);
  document.querySelectorAll(".dim-able").forEach(e => e.classList.toggle("dim", on));
});

wire();
addEventListener("resize", wire);
document.fonts && document.fonts.ready.then(() => { wire(); window.__ready = true; });
setTimeout(() => { window.__ready = true; }, 400);
</script>
</body></html>
"""


def render_html():
    n = check_sources()
    html = TEMPLATE.replace("__DATA__", json.dumps(data(n), ensure_ascii=False))
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, SLUG + ".html")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    return path, n


def render(width=1600):
    """HTML siempre; PNG 2x y miniatura si hay Playwright (Edge o Chromium)."""
    path, n = render_html()
    out = {"html": path, "figure_class": FIG_CLASS, "evidence_origin": ORIGIN, "guards": n}
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("AVISO fig15: sin playwright en este Python; HTML escrito, PNG no. "
              "Ejecuta: python src/figures/fig15_decision_map.py con un Python que lo tenga.")
        return out
    url = pathlib.Path(path).resolve().as_uri() + "?export=1"
    png = os.path.join(OUT_DIR, SLUG + ".png")
    thumb = os.path.join(OUT_DIR, "thumb", SLUG + ".png")
    os.makedirs(os.path.dirname(thumb), exist_ok=True)
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            b = p.chromium.launch(headless=True)
        for target, scale in ((png, 2), (thumb, 0.4)):
            ctx = b.new_context(viewport={"width": width, "height": 1000}, device_scale_factor=scale,
                                color_scheme="light")
            pg = ctx.new_page()
            pg.goto(url)
            pg.wait_for_function("window.__ready === true")
            pg.screenshot(path=target, full_page=True)
            ctx.close()
        b.close()
    out.update({"png": png, "thumb": thumb})
    return out


def load_and_build():
    return render(), {}


if __name__ == "__main__":
    print(render())
