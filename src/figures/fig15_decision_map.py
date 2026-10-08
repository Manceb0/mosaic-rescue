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
PRINT_PANELS = (("#slideA", "figures/pub/fig15_decision_map_track2_a.png"),
                ("#slideC", "figures/pub/fig15_decision_map_track2_c.png"))

SOURCES = {"README": "README.md", "T1": "reports/TRACK1_REPORT.md", "T2": "reports/TRACK2_REPORT.md",
           "RENAL": "docs/RENAL_RESIDUAL.md", "BASE": "docs/EXTERNAL_BASELINE.md"}

# (pregunta, siguiente observación, un desenlace, el otro desenlace, qué hace falta, nodo del árbol,
#  ¿necesita a la familia o al niño?)
TRACK1 = [
    ("Phase of the two alleles is unresolved",
     "Parental genotyping at both sites, or targeted long-read phasing of the child",
     "Trans: the truncating and missense alleles sit on opposite copies, matching a reported biallelic MVA1 pattern. "
     "The missense still needs functional evidence",
     "Cis: this pair cannot be the recessive explanation, and the hidden-allele search becomes the primary question",
     "Parents, or the child's DNA for long reads", "phase", True),
    ("The missense is a VUS",
     "Variant expressed in isogenic cells: BUBR1 abundance and turnover, kinetochore localisation, checkpoint "
     "arrest, segregation errors, with wild-type and known MVA-allele controls",
     "Disease-relevant defect detected: a reproducible abnormality in a preregistered BUBR1 readout provides "
     "functional support for pathogenicity",
     "No defect across the preregistered readouts: the current pair is weakened, and a hidden allele or another gene "
     "becomes more likely. This does not exclude functions or cellular contexts the assay does not represent",
     "Engineered cells only", "assay", False),
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

# Tipo de flujo de cada fila, con la leyenda del proyecto: b = dato o registro del niño (azul), y = experimento
# en células editadas (amarillo), g = estudio computacional (verde).
ROW_KIND = ["b", "y", "b", "b", "b", "g"]

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
    ("README", "the truncating and missense alleles sit on opposite copies, matching a reported biallelic MVA1 "
               "pattern. The missense still needs functional evidence"),
    ("README", "this pair cannot be the recessive explanation, and the hidden-allele search becomes the primary "
               "question"),
    ("README", "Variant expressed in isogenic cells: BUBR1 abundance and turnover, kinetochore localisation, "
               "checkpoint arrest, segregation errors, with wild-type and known MVA-allele controls"),
    ("README", "Disease-relevant defect detected: a reproducible abnormality in a preregistered BUBR1 readout "
               "provides functional support for pathogenicity"),
    ("README", "No defect across the preregistered readouts: the current pair is weakened, and a hidden allele or "
               "another gene becomes more likely. This does not exclude functions or cellular contexts the assay "
               "does not represent"),
    ("README", "An external validation study, to be preregistered: the frozen pipeline run unchanged on previously "
               "solved cases with known causal genes, blinded to the answer"),
    ("README", "The known genes rank within a top-k threshold set before the run: evidence that the procedure "
               "transfers"),
    ("README", "They do not: the contribution is the audit trail, not the ranking"),
    ("README", "Fewer new segregation errors per completed mitosis at matched proliferation, without extra "
               "clonogenic survival of unstable cells"),
    ("README", "More survival of unstable cells: veto, even if another readout improves"),
    ("README", "it is the first branching observation"),
    ("T1", "the truncating and missense alleles sit on opposite copies, matching a reported biallelic MVA1 pattern"),
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
        "track1": [{"q": q, "obs": o, "a": _split(a), "b": _split(b), "needs": n, "node": nd, "family": fam,
                    "kind": k}
                   for (q, o, a, b, n, nd, fam), k in zip(TRACK1, ROW_KIND)],
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
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1600">
<title>Decision map</title>
<style>
/* Estilo de los diagramas del proyecto, el de las ilustraciones del equipo (docs/assets/mosaic-0*.png): fondo
   casi negro con cuadrícula fina, cajas de cristal gris con borde claro y halo blanco suave, embudos para las
   decisiones, rutas ortogonales de esquinas redondeadas, amarillo discontinuo para lo propuesto y blanco continuo
   para la lógica, pocas palabras y grandes. */
:root{--bg:#0a0c0f;--grid:rgba(255,255,255,.055);--ink:#f3f5f6;--soft:#c5ccd2;--mute:#8e979e;
  --edge:rgba(226,231,235,.80);--yellow:#f6c21c;--green:#34d98a;--blue:#2f8cff}
*{box-sizing:border-box}
html,body{margin:0;background:#050607}
body{font-family:"Segoe UI Variable Display","Segoe UI",system-ui,-apple-system,Arial,sans-serif;color:var(--soft);
  -webkit-font-smoothing:antialiased}
.slide{position:relative;width:1600px;margin:0 auto 24px;padding:44px 48px 64px;background-color:var(--bg);
  background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:56px 56px;overflow:hidden}
.brand{font-size:24px;letter-spacing:7px;font-weight:400;color:#e9edf0}
.bar{width:44px;height:5px;border-radius:3px;background:var(--green);margin:9px 0 14px}
.sub{font-size:31px;font-weight:400;color:var(--ink);letter-spacing:.1px}
.foot{position:absolute;right:48px;bottom:24px;font-size:15px;color:#9aa3aa}
.lane{font-size:16px;letter-spacing:3.5px;text-transform:uppercase;color:#d5dbe0}
.lane::after{content:"";display:block;width:34px;height:4px;border-radius:2px;background:var(--green);margin-top:7px}
/* Vidrio esmerilado: base oscura, luces de color difuminadas detrás (::after), grano fino encima (::before),
   borde blanco brillante con halo exterior suave. */
.g{position:relative;overflow:hidden;border-radius:18px;border:1.8px solid rgba(255,255,255,.88);color:var(--soft);
  background:linear-gradient(180deg,rgba(34,38,43,.82) 0%,rgba(14,16,19,.94) 100%);
  box-shadow:0 0 8px rgba(255,255,255,.09),inset 0 1px 0 rgba(255,255,255,.12)}
.g::after{content:"";position:absolute;inset:-10%;background:var(--l,none);filter:blur(26px);opacity:.85;z-index:0;
  pointer-events:none}
.g::before{content:"";position:absolute;inset:0;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .6 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");background-size:180px 180px;
  opacity:.16;mix-blend-mode:overlay;z-index:1;pointer-events:none}
.g > *{position:relative;z-index:2}
.g.hl{border-color:var(--yellow);box-shadow:0 0 8px rgba(246,194,28,.2)}
/* Paletas de luz, la misma gramática de color que las ilustraciones del equipo */
.Lgb{--l:radial-gradient(32% 55% at 10% 100%,rgba(52,217,138,.55),transparent 70%),
  radial-gradient(30% 55% at 92% 0%,rgba(47,140,255,.55),transparent 70%)}
.Lbo{--l:radial-gradient(26% 60% at 8% 100%,rgba(52,217,138,.45),transparent 70%),
  radial-gradient(26% 55% at 88% 0%,rgba(47,140,255,.55),transparent 70%),
  radial-gradient(24% 55% at 90% 100%,rgba(255,140,60,.45),transparent 70%)}
.Lg{--l:radial-gradient(45% 70% at 70% 110%,rgba(52,217,138,.55),transparent 70%)}
.Lb{--l:radial-gradient(45% 70% at 85% -5%,rgba(47,140,255,.50),transparent 70%)}
.Lo{--l:radial-gradient(45% 70% at 90% 105%,rgba(255,130,60,.48),transparent 70%)}
.Ly{--l:radial-gradient(55% 70% at 50% 115%,rgba(246,194,28,.42),transparent 70%)}
.Lyb{--l:radial-gradient(35% 75% at 18% 115%,rgba(246,194,28,.38),transparent 70%),
  radial-gradient(30% 60% at 94% -5%,rgba(47,140,255,.48),transparent 70%)}
.Lv{--l:radial-gradient(40% 70% at 12% 105%,rgba(180,155,255,.50),transparent 70%),
  radial-gradient(30% 60% at 92% 0%,rgba(47,140,255,.40),transparent 70%)}
.ico{position:absolute!important;right:18px;top:16px}
.two{color:#9aa3aa;font-weight:400}.two b{color:inherit;font-weight:700}
.g.dash{border:1.5px dashed rgba(255,255,255,.45);background:rgba(255,255,255,.012);box-shadow:none}
.g.dash::before,.g.dash::after{display:none}
.g h3{margin:0 0 8px;font-size:25px;font-weight:500;color:var(--ink);letter-spacing:.1px}
.g p{margin:0;font-size:19px;line-height:1.38}
.y{color:var(--yellow)}.gr{color:var(--green)}.w{color:var(--ink)}.bl{color:#5aa8ff}
.g.hlb{border-color:var(--blue);box-shadow:0 0 8px rgba(47,140,255,.2)}
.lbl{color:#aeb6bd}.lbl b{color:#fff;font-weight:700}
.abs{position:absolute}
.lbl{position:absolute;font-size:17px;line-height:1.3;white-space:nowrap;z-index:6}
.lbl b{font-weight:700}
.lbl.wrap{white-space:normal}
.cap{font-size:13.5px;letter-spacing:2.6px;text-transform:uppercase;color:var(--mute);margin-bottom:6px}
svg.wires{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible;z-index:5}
.glyphs{display:flex;gap:22px;align-items:flex-end;margin-top:14px;flex-wrap:wrap}
.glyphs figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:6px}
.glyphs figcaption{font-size:13.5px;color:#aeb6bd;text-align:center;max-width:118px;line-height:1.25}
.glyphs svg,.out svg{flex:none}
.rule{margin-bottom:74px}
.ceiling{position:absolute;right:48px;top:52px;font-size:15px;color:#9aa3aa}
.funnel{position:absolute}
.funnel svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.funnel .t{position:absolute;left:0;right:0;top:20%;text-align:center}
.funnel .k{font-size:15px;letter-spacing:3px;text-transform:uppercase;color:var(--yellow)}
.funnel .n{font-size:24px;color:var(--ink);line-height:1.25;margin-top:4px}
.plate{flex:none}
.legend{position:absolute;left:48px;bottom:18px;display:flex;gap:30px;font-size:15px;color:#c5ccd2;align-items:center;padding:10px 20px;border:1.3px solid rgba(255,255,255,.45);border-radius:14px;background:rgba(255,255,255,.03);box-shadow:0 0 14px rgba(255,255,255,.07)}
.legend span{display:flex;align-items:center;gap:10px}
/* lámina A */
.arm-row{display:flex;align-items:center;gap:16px;margin:12px 0 0}
.arm-row b{display:block;font-size:21px;font-weight:500;color:var(--ink)}
.arm-row i{font-style:normal;font-size:16px;color:var(--soft)}
.indep{display:grid;grid-template-columns:repeat(4,1fr);gap:26px;margin-top:10px}
.indep div{font-size:17px;line-height:1.38}
.indep b{display:block;font-weight:500;color:var(--ink);font-size:18px;margin-bottom:3px}
.indep > div{display:flex;flex-direction:column;padding-left:66px;position:relative}
.indep > div > svg{position:absolute;left:0;top:2px}
/* lámina B */
.heads,.rowsB{display:grid;grid-template-columns:300px 400px 700px;column-gap:52px}
.heads{margin:30px 0 14px}
.heads div{font-size:20px;letter-spacing:4px;color:#e2e7eb;padding-bottom:9px;border-bottom:1.3px solid rgba(226,231,235,.55)}
.rowsB{row-gap:22px}
.rowsB .g{padding:18px 20px}
.q h3{font-size:22px;line-height:1.3}
.need{font-size:16px;margin-top:10px;line-height:1.3}
.need em{font-style:normal;color:var(--mute);letter-spacing:2px;text-transform:uppercase;font-size:13px;display:block;margin-bottom:2px}
.obs p{font-size:18.5px;color:#e0e5e9}
.dec{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:14px!important}
.dec .s{border-radius:13px;border:1.3px solid rgba(255,255,255,.55);background:rgba(8,10,12,.62);padding:13px 15px;box-shadow:inset 0 0 14px rgba(255,255,255,.04)}
.dec .s b{display:block;font-size:18.5px;font-weight:600;color:var(--yellow);margin-bottom:4px}
.k-b .s b{color:#5aa8ff}.k-g .s b{color:var(--green)}
.dec .s span{font-size:17px;line-height:1.38;color:var(--soft)}
/* lámina C */
.prec{margin:26px 0 52px;padding:18px 22px}
.prec p{font-size:19px}
.rowsC{display:grid;grid-template-columns:344px 312px 404px 300px;column-gap:48px;row-gap:24px}
.rowsC .g{padding:18px 20px}
.arm h3{font-size:28px;margin:2px 0 4px}
.arm .role{font-size:17px;color:var(--soft);line-height:1.35}
.arm .tag{font-size:16.5px;color:var(--yellow);margin-top:9px;line-height:1.3}
.arm .need2{font-size:15px;color:var(--yellow);margin-top:12px}
.arm .top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.disc .cap{color:var(--yellow)}
.disc p,.meas p{font-size:18.5px;color:#e0e5e9}
.right{grid-column:4;grid-row:1 / span 3;position:relative}
.right .cnote{font-size:16px;line-height:1.38;color:var(--soft);margin:22px 0 0}
#c-adv{margin-top:330px!important}
#c-veto{margin-top:58px!important}
.out{margin-top:40px;padding:15px 18px!important}
.out p{font-size:17.5px}
.out + .out{margin-top:18px}
.rule{display:flex;align-items:center;gap:28px;margin-top:34px}
.rule .g{padding:14px 24px;border-color:var(--yellow);box-shadow:0 0 14px rgba(246,194,28,.25)}
.rule .g p{font-size:22px;color:var(--ink)}
.rule .note{font-size:17px;color:var(--soft);max-width:760px;line-height:1.38}

/* Caja tintada (caja AlphaGenome de la ilustración 04): el BORDE es un degradado, del color de su evidencia en el
   lado por donde entra el flujo a blanco normal en el resto, y el relleno lleva un tinte solo en ese lado. */
.g.tint{border-color:transparent;
  background:linear-gradient(var(--td,90deg),rgba(var(--tc),.16) 0%,rgba(var(--tc),.04) 30%,rgba(0,0,0,0) 55%) padding-box,
    linear-gradient(180deg,rgba(30,34,39,.86) 0%,rgba(12,14,17,.95) 100%) padding-box,
    linear-gradient(var(--td,90deg),rgb(var(--tc)) 0%,rgba(var(--tc),.85) 20%,rgba(255,255,255,.88) 60%) border-box;
  box-shadow:0 0 8px rgba(var(--tc),.14)}
.t-b{--tc:47,140,255}.t-up{--td:0deg}.t-y{--tc:246,194,28}.t-g{--tc:52,217,138}
.t-by{--tc:47,140,255;--tc2:246,194,28;--e:.15}.t-v{--td:180deg}
.tint .concl{color:rgb(var(--tc));filter:brightness(1.3) saturate(.7)}
</style></head>
<body>

<section class="slide" id="slideA" style="height:1780px">
  <div class="brand">MOSAIC RESCUE</div><div class="bar"></div>
  <div class="sub">The order of decisions</div>
  <div class="ceiling">Proposed decisions, nothing measured yet</div>
  <div class="lane abs" style="left:48px;top:205px">The child's genotype</div>
  <div class="lane abs" style="left:1060px;top:205px">Starts now in engineered cells</div>

  <div class="g hlb tint t-b t-up abs" id="a-phase" style="left:48px;top:262px;width:640px;padding:20px 24px">__ICON_PHASE__
    <h3>1 / Phase of the two BUB1B alleles</h3>
    <p>Parental genotyping or targeted long-read phasing</p><p class="concl" style="margin-top:6px">First branching observation</p></div>
  <div class="g Lo abs" id="a-cis" style="left:48px;top:480px;width:300px;padding:18px 20px">
    <h3>Cis</h3><p>The current pair cannot explain recessive MVA1. Search for a hidden second allele.</p><div style="margin-top:12px;height:58px">__ICON_CIS__</div></div>
  <div class="g Lg abs" id="a-trans" style="left:388px;top:480px;width:300px;padding:18px 20px">
    <h3>Trans</h3><p>The current pair stays plausible. Phase alone does not validate the missense.</p><div style="margin-top:12px;height:58px">__ICON_TRANS__</div></div>
  <div class="g abs" id="a-assay" style="left:388px;top:760px;width:300px;padding:18px 20px">
    <h3>Missense assay</h3><p>Abundance, turnover, kinetochore localisation, checkpoint and segregation at matched expression</p>__ASSAY_GLYPHS__</div>
  <div class="funnel" id="a-g1" data-l="v" style="left:78px;top:1090px;width:580px;height:210px"><div class="t">
    <div class="k" style="color:#5aa8ff">Gate 1</div><div class="n">Patient-specific<br>relevance</div></div></div>
  <div class="abs" style="left:716px;top:1104px;width:300px;font-size:17px;line-height:1.4">
    Requires a supported causal BUB1B genotype. Opposite-copy phase preserves the current pair but does not validate
    the missense. If the pair is cis, a qualifying second BUB1B allele must be found and phased, and the arms
    reassessed for that genotype.</div>

  <div class="g abs" id="a-arms" style="left:1060px;top:262px;width:492px;padding:20px 24px">
    <h3>2 / Three experimental arms</h3>
    <div class="arm-row">__PLATE__<div><b>Azithromycin</b><i>Allele-directed hypothesis</i></div></div>
    <div class="arm-row">__PLATE__<div><b>Arimoclomol</b><i>Falsification sentinel</i></div></div>
    <div class="arm-row">__PLATE__<div><b>Sirolimus</b><i>Adversarial comparator</i></div></div>
    <p class="y" style="margin-top:14px">In parallel with phase. Preclinical, for no patient.</p></div>
  <div class="funnel" id="a-g2" data-l="g" style="left:1066px;top:716px;width:480px;height:210px"><div class="t">
    <div class="k">Gate 2</div><div class="n">Safe Rescue<br>Corridor</div></div></div>
  <div class="abs" style="left:716px;top:736px;width:316px;font-size:17px;line-height:1.4;text-align:right">
    An arm advances only if new segregation errors per completed mitosis fall at matched proliferation and clonogenic
    survival of unstable cells does not rise.</div>

  <div class="g abs" id="a-final" style="left:48px;top:1358px;width:1504px;padding:18px 24px">
    <h3>Patient-specific experimental candidate <span class="w" style="font-size:20px;margin-left:14px;opacity:.85">Only if both gates pass</span></h3>
    <p>Genetics decides whether a result concerns this child. The Safe Rescue Corridor decides whether a preclinical
      result may advance. Neither gate stands in for the other.</p></div>
  <div class="g dash abs" style="left:48px;top:1506px;width:1504px;padding:16px 24px">
    <div class="cap" style="color:#d5dbe0">Independent of phase</div>
    <div class="indep">
      <div>__ICON_DOC__<b>Nephrocalcinosis</b><span>Clinical records</span></div>
      <div>__ICON_READS__<b>HLA-DRB1 flag</b><span>The existing alignment</span></div>
      <div>__ICON_STACK__<b>Generality of the method</b><span>A preregistered study on solved cases</span></div>
      <div>__ICON_CELL__<b>Mosaic fraction</b><span>A direct cell-level measurement. The WGS detector failed its validation (EXP-027) and was not run on the child.</span></div>
    </div></div>
  __LEGEND__
  <div class="foot">Conceptual decision map. No new result, no patient data.</div>
</section>

<section class="slide" id="slideB">
  <div class="brand">MOSAIC RESCUE</div><div class="bar"></div>
  <div class="sub">Track 1: the next observation for each open question</div>
  <div class="ceiling">Proposed measurements, not completed results</div>
  <div class="heads"><div>Open question</div><div>Next observation</div><div>What each outcome decides</div></div>
  <div class="rowsB" id="rowsB"></div>
  <div style="height:70px"></div>
  __LEGEND3__
  <div class="foot">Some observations settle a question, others only narrow it. Text as written in the reports.</div>
</section>

<section class="slide" id="slideC">
  <div class="brand">MOSAIC RESCUE</div><div class="bar"></div>
  <div class="sub">Track 2: three experimental arms and one shared gate</div>
  <div class="ceiling">Proposed preclinical design, no efficacy demonstrated</div>
  <div class="g Lbo prec"><p id="prec"></p></div>
  <div class="rowsC" id="rowsC"><div class="right" id="right">
    <div class="funnel" id="c-g2" data-l="g" style="left:0;top:0;width:300px;height:236px"><div class="t" style="top:16%">
      <div class="k">Gate 2</div><div class="n">Safe Rescue<br>Corridor</div></div></div>
    <div class="g out" id="c-adv"><div class="cap w">An arm advances only if</div><p id="advp"></p>__ADV_GLYPHS__</div>
    <div class="g Ly out hl" id="c-veto"><div style="display:flex;gap:14px;align-items:center">__VETO__<div><div class="cap y">Veto</div><p id="vetop"></p></div></div></div>
    <div class="cnote" id="cnote"></div>
  </div></div>
  <div class="rule"><div class="g Ly"><p>A rise in BUBR1 alone is not a rescue.</p></div>
    <div class="note" id="armsnote"></div></div>
  __LEGEND2__
  <div class="foot">Discard rules as written in the Track 2 report. Preclinical hypotheses, for no patient.</div>
</section>

<script>
const D = __DATA__;
const OBSG = __OBSG__;
const MEASG = __MEASG__;
const $ = (s, r = document) => r.querySelector(s);
const esc = s => s.replace(/[&<>]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"}[c]));
const C = {y: "#f6c21c", b: "#2f8cff", g: "#34d98a"};
const RGB = {y: "246,194,28", b: "47,140,255", g: "52,217,138"};
// Luz dentro de cada caja en el punto exacto por donde entra o sale un flujo, de su color (como el Controlador
// de las referencias: verde donde entra la visión, ámbar donde entra la memoria, azul donde sale la acción).
const PORTS = new Map();
function port(el, slide, x, y, color) {
  if (!el) return;
  const r = box(el, slide);
  if (!PORTS.has(el)) PORTS.set(el, []);
  PORTS.get(el).push({fx: (x - r.x) / r.w * 100, fy: (y - r.y) / r.h * 100, px: x - r.x, py: y - r.y, color});
}
const NS = "http://www.w3.org/2000/svg";

// Lámina B: una fila por pregunta, con el texto de los informes
const rowsB = $("#rowsB");
D.track1.forEach((r, i) => {
  const hl = i === 0 ? " hlb" : "";
  rowsB.insertAdjacentHTML("beforeend",
    `<div class="g q${hl}" data-r="${i}"><h3>${esc(r.q)}</h3><div class="need"><em>Needs</em>` +
    `<span class="${{b: "bl", y: "y", g: "gr"}[r.kind]}">${esc(r.needs)}</span></div></div>` +
    `<div class="g obs${hl}" data-r="${i}"><p>${esc(r.obs)}</p>${OBSG[i]}</div>` +
    `<div class="g dec k-${r.kind}${hl}" data-r="${i}"><div class="s"><b>${esc(r.a.key)}</b><span>${esc(r.a.body)}</span></div>` +
    `<div class="s"><b>${esc(r.b.key)}</b><span>${esc(r.b.body)}</span></div></div>`);
});

// Lámina C: tres brazos y el corredor compartido
$("#prec").innerHTML = `<b class="w" style="font-weight:600">${esc(D.precedent.split(": ")[0])}:</b> ` +
  esc(D.precedent.split(": ").slice(1).join(": "));
const corr = D.track2[3];
$("#cnote").textContent = "Measures " + corr.measure.charAt(0).toLowerCase() + corr.measure.slice(1) + ".";
const cut = corr.discard.indexOf(". More");
$("#advp").textContent = corr.discard.slice(0, cut + 1);
$("#vetop").textContent = corr.discard.slice(cut + 2);
$("#armsnote").textContent = D.armsNote.replace(": a rise in BUBR1 alone is not a rescue.", ".");
const right = $("#right");
D.track2.slice(0, 3).forEach((a, i) => {
  right.insertAdjacentHTML("beforebegin",
    `<div class="g arm" style="grid-row:${i + 1}" data-c="${i}"><div class="top"><div><div class="cap">${esc(a.route)}</div>` +
    `<h3>${esc(a.title)}</h3></div>${D.plate}</div><div class="role">${esc(a.role)}</div>` +
    `<div class="tag">${esc(a.tag)}</div><div class="need2">${esc(a.needs)}</div></div>` +
    `<div class="g meas" style="grid-row:${i + 1}" data-c="${i}"><div class="cap">Must measure</div><p>${esc(a.measure)}</p>${MEASG[i]}</div>` +
    `<div class="g disc" style="grid-row:${i + 1}" data-c="${i}"><div class="cap">${esc(a.dlabel)}</div><p>${esc(a.discard)}</p></div>`);
});

// Rutas ortogonales con esquinas redondeadas
function path(pts, r = 16) {
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 1; i < pts.length - 1; i++) {
    const [px, py] = pts[i - 1], [cx, cy] = pts[i], [nx, ny] = pts[i + 1];
    const d1 = Math.hypot(cx - px, cy - py), d2 = Math.hypot(nx - cx, ny - cy), rr = Math.min(r, d1 / 2, d2 / 2);
    const ax = cx - (cx - px) / d1 * rr, ay = cy - (cy - py) / d1 * rr;
    const bx = cx + (nx - cx) / d2 * rr, by = cy + (ny - cy) / d2 * rr;
    d += ` L${ax},${ay} Q${cx},${cy} ${bx},${by}`;
  }
  const [lx, ly] = pts[pts.length - 1];
  return d + ` L${lx},${ly}`;
}
function svgFor(slide) {
  let s = slide.querySelector("svg.wires");
  if (!s) {
    s = document.createElementNS(NS, "svg"); s.setAttribute("class", "wires"); slide.prepend(s);
    const defs = document.createElementNS(NS, "defs");
    Object.entries(C).forEach(([k, c]) => {
      const m = document.createElementNS(NS, "marker");
      Object.entries({id: `h-${slide.id}-${k}`, viewBox: "0 0 12 12", refX: 10, refY: 6, markerWidth: 12,
        markerHeight: 12, markerUnits: "userSpaceOnUse", orient: "auto"}).forEach(([a, v]) => m.setAttribute(a, v));
      const p = document.createElementNS(NS, "path"); p.setAttribute("d", "M0,0 L12,6 L0,12 z"); p.setAttribute("fill", c);
      m.append(p); defs.append(m);
    });
    s.append(defs);
  }
  return s;
}
function wire(slide, pts, color, dashed, head = true) {
  const s = svgFor(slide), halo = document.createElementNS(NS, "path"), p = document.createElementNS(NS, "path");
  // Halo de neón: un trazo ancho y difuminado debajo del trazo fino, como en las referencias
  halo.setAttribute("d", path(pts)); halo.setAttribute("fill", "none"); halo.setAttribute("stroke", C[color]);
  halo.setAttribute("stroke-width", 6); halo.setAttribute("stroke-linecap", "round"); halo.setAttribute("opacity", .12);
  halo.style.filter = "blur(3px)"; if (dashed) halo.setAttribute("stroke-dasharray", "10 7"); s.append(halo);
  p.setAttribute("d", path(pts)); p.setAttribute("fill", "none"); p.setAttribute("stroke", C[color]);
  p.setAttribute("stroke-width", 2.6); p.setAttribute("stroke-linecap", "round");
  if (dashed) p.setAttribute("stroke-dasharray", "10 7");
  if (head) p.setAttribute("marker-end", `url(#h-${slide.id}-${color})`);
  p.style.filter = `drop-shadow(0 0 3px ${C[color]}88)`;
  s.append(p);
}
// Ninguna línea atraviesa una caja que no sea su origen o su destino, y ninguna etiqueta pisa una caja.
const ISSUES = [];
function crosses(slide, from, to, pts) {
  const boxes = [...slide.querySelectorAll(".g, .funnel, .legend")].filter(e => e !== from && e !== to);
  for (let i = 0; i < pts.length - 1; i++) {
    const [x1, y1] = pts[i], [x2, y2] = pts[i + 1];
    const lx = Math.min(x1, x2), hx = Math.max(x1, x2), ly = Math.min(y1, y2), hy = Math.max(y1, y2);
    for (const e of boxes) {
      const r = box(e, slide), m = 3;
      if (hx > r.x + m && lx < r.r - m && hy > r.y + m && ly < r.bt - m)
        ISSUES.push(`line crosses ${e.id || e.className.split(" ").slice(0, 2).join(".")} in ${slide.id}`);
    }
  }
}
function link(slide, from, to, pts, color, dashed = true, head = true) {
  crosses(slide, from, to, pts);
  if (to && to.classList.contains("funnel")) {
    const g = box(to, slide), [ax, ay] = pts[pts.length - 2], [bx, by] = pts[pts.length - 1];
    if (Math.abs(ax - bx) > .5 || by < ay || Math.abs(by - g.y) > 5 || bx < g.x + 14 || bx > g.r - 14)
      ISSUES.push(`arrow into ${to.id} does not enter its flat top edge vertically`);
  }
  port(from, slide, pts[0][0], pts[0][1], color);
  port(to, slide, pts[pts.length - 1][0], pts[pts.length - 1][1], color);
  wire(slide, pts, color, dashed, head);
}
function box(el, slide) {
  const a = el.getBoundingClientRect(), b = slide.getBoundingClientRect();
  return {x: a.left - b.left, y: a.top - b.top, w: a.width, h: a.height, r: a.right - b.left, bt: a.bottom - b.top,
          cx: a.left - b.left + a.width / 2, cy: a.top - b.top + a.height / 2};
}
function label(slide, x, y, text, color, opts = {}) {
  const d = document.createElement("div");
  d.className = "lbl" + (opts.wrap ? " wrap" : "");
  // Como en las referencias: la etiqueta es neutra, gris con la palabra clave en blanco negrita («visión **actual**»)
  const m = text.match(/^(if a |if |only with |gate )(.*)$/);
  d.innerHTML = m ? `${esc(m[1])}<b>${esc(m[2])}</b>` : esc(text);
  d.style.left = x + "px"; d.style.top = y + "px"; if (opts.w) d.style.width = opts.w + "px";
  if (opts.right) { d.style.left = ""; d.style.right = (slide.clientWidth - x) + "px"; d.style.textAlign = "right"; }
  slide.append(d);
  const r = box(d, slide);
  [...slide.querySelectorAll(".g, .funnel, .legend")].forEach(e => {
    const b = box(e, slide);
    if (r.r > b.x + 2 && r.x < b.r - 2 && r.bt > b.y + 2 && r.y < b.bt - 2)
      ISSUES.push(`label "${text}" overlaps a box in ${slide.id}`);
  });
}
function funnel(el) {
  // Embudo de vidrio: base oscura, grano fino, y una luz en cada puerto con el color del flujo que entra o sale
  const w = el.clientWidth, h = el.clientHeight, s = document.createElementNS(NS, "svg"), id = el.id;
  const lights = (PORTS.get(el) || []).map(q => `<ellipse cx="${Math.min(Math.max(q.px, w * .18), w * .82)}"
    cy="${q.py > h * .6 ? h * .9 : h * .06}" rx="${w * .13}" ry="${h * .2}" fill="${C[q.color]}"
    opacity="${q.py > h * .6 ? .42 : .26}" filter="url(#fb-${id})"/>`).join("");
  const shape = `M14,1 L${w - 14},1 Q${w - 1},1 ${w - 8},13 L${w / 2 + 12},${h - 14} Q${w / 2},${h} ${w / 2 - 12},${h - 14} L8,13 Q1,1 14,1 z`;
  s.setAttribute("viewBox", `0 0 ${w} ${h}`);
  s.innerHTML = `<defs>
      <linearGradient id="fg-${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#262b31" stop-opacity=".88"/>
        <stop offset="1" stop-color="#0e1013" stop-opacity=".96"/></linearGradient>
      <clipPath id="fc-${id}"><path d="${shape}"/></clipPath>
      <filter id="fb-${id}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="26"/></filter>
      <filter id="fn-${id}"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/>
        <feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .5 0"/></filter></defs>
    <path d="${shape}" fill="url(#fg-${id})"/>
    <g clip-path="url(#fc-${id})">
      ${lights}
      <rect width="${w}" height="${h}" filter="url(#fn-${id})" opacity=".12" style="mix-blend-mode:overlay"/></g>
    <path d="${shape}" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="1.8"
      style="filter:drop-shadow(0 0 5px rgba(255,255,255,.18))"/>`;
  el.prepend(s);
}
const PLATEW = 1;

function drawA() {
  const S = $("#slideA"), E = id => $(id), b = id => box($(id), S);
  const ph = b("#a-phase"), ci = b("#a-cis"), tr = b("#a-trans"), as = b("#a-assay"), g1 = b("#a-g1"),
        ar = b("#a-arms"), g2 = b("#a-g2"), fi = b("#a-final");
  // El genotipo del niño viaja en azul: fase, cis, trans, y el segundo alelo
  link(S, E("#a-phase"), E("#a-cis"), [[ci.cx, ph.bt], [ci.cx, ci.y]], "b");
  label(S, ci.cx + 12, (ph.bt + ci.y) / 2 - 11, "if cis", "b");
  link(S, E("#a-phase"), E("#a-trans"), [[tr.cx, ph.bt], [tr.cx, tr.y]], "b");
  label(S, tr.cx + 12, (ph.bt + tr.y) / 2 - 11, "if trans", "b");
  // La variante entra en el ensayo (azul) y sale un resultado experimental (amarillo)
  link(S, E("#a-trans"), E("#a-assay"), [[tr.cx, tr.bt], [tr.cx, as.y]], "b");
  link(S, E("#a-assay"), E("#a-g1"), [[as.cx, as.bt], [as.cx, g1.y]], "y");
  label(S, as.cx + 12, (as.bt + g1.y) / 2 - 11, "if a disease-relevant defect", "y");
  link(S, E("#a-cis"), E("#a-g1"), [[ci.cx, ci.bt], [ci.cx, g1.y]], "b");
  label(S, ci.cx + 14, ci.bt + 40, "only with a qualifying second allele and resolved phase", "b", {wrap: true, w: 168});
  link(S, E("#a-arms"), E("#a-g2"), [[ar.cx, ar.bt], [ar.cx, g2.y]], "y");
  // Cada puerta entrega lo suyo: la relevancia genética (azul) y el resultado preclínico (amarillo)
  link(S, E("#a-g1"), E("#a-final"), [[g1.cx, g1.bt], [g1.cx, fi.y]], "b");
  label(S, g1.cx + 12, (g1.bt + fi.y) / 2 - 11, "gate 1", "b");
  link(S, E("#a-g2"), E("#a-final"), [[g2.cx, g2.bt], [g2.cx, fi.y]], "y");
  label(S, g2.cx + 12, (g2.bt + fi.y) / 2 - 11, "gate 2", "y");
}
function drawB() {
  const S = $("#slideB");
  D.track1.forEach((r, i) => {
    const els = [...S.querySelectorAll(`[data-r="${i}"]`)], [q, o, d] = els.map(e => box(e, S));
    link(S, els[0], els[1], [[q.r + 6, q.cy], [o.x - 4, q.cy]], r.kind);
    link(S, els[1], els[2], [[o.r + 6, o.cy], [d.x - 4, o.cy]], r.kind);
  });
}
function drawC() {
  const S = $("#slideC"), G = $("#c-g2"), g = box(G, S), adv = box($("#c-adv"), S), veto = box($("#c-veto"), S);
  const bus = g.x - 22, ty = g.y - 24, ex = g.x + g.w * .3;
  [0, 1, 2].forEach(i => {
    const els = [...S.querySelectorAll(`[data-c="${i}"]`)], [a, m, d] = els.map(e => box(e, S));
    link(S, els[0], els[1], [[a.r + 6, a.cy], [m.x - 4, a.cy]], "y");
    link(S, els[1], els[2], [[m.r + 6, m.cy], [d.x - 4, m.cy]], "y");
    link(S, els[2], G, [[d.r + 4, d.cy], [bus, d.cy], [bus, ty], [ex, ty], [ex, g.y - 3]], "y", true, i === 0);
  });
  const split = g.bt + 22, rx = adv.r + 24;
  link(S, G, $("#c-adv"), [[g.cx, g.bt], [g.cx, adv.y]], "y");
  label(S, g.cx - 12, (split + adv.y) / 2 - 2, "if it passes", "y", {right: true});
  link(S, null, $("#c-veto"), [[g.cx, split], [rx, split], [rx, veto.cy], [veto.r + 4, veto.cy]], "y");
  label(S, veto.x + 4, veto.y - 38, "if unstable cells survive better", "y");
}
// Luces: en las cajas, solo donde hay un puerto; una caja sin flujos queda con un brillo neutro
function lights() {
  document.querySelectorAll(".g:not(.dash)").forEach(el => {
    const ps = PORTS.get(el) || [];
    // Una caja tintada solo puede tener flujos de su mismo color (si no, el borde contradice sus luces)
    const tk = [...el.classList].find(c => /^t-[byg]$/.test(c));
    if (tk && ps.some(q => q.color !== tk.slice(2))) ISSUES.push(`tinted box ${el.id} has ports of another colour`);
    el.style.setProperty("--l", ps.length ? ps.map(q =>
      `radial-gradient(30% 70% at ${q.fx.toFixed(1)}% ${q.fy.toFixed(1)}%, rgba(${RGB[q.color]},.30), transparent 75%)`).join(",")
      : "radial-gradient(45% 70% at 50% 115%, rgba(255,255,255,.07), transparent 72%)");
  });
  document.querySelectorAll(".funnel").forEach(funnel);
}
function plateSvg(){return '';}
drawA(); drawB(); drawC(); lights();
// La leyenda no puede pisar ninguna caja
document.querySelectorAll(".slide").forEach(S => S.querySelectorAll(".legend").forEach(L => {
  const r = box(L, S);
  S.querySelectorAll(".g, .funnel").forEach(e => { const b = box(e, S);
    if (r.r > b.x + 2 && r.x < b.r - 2 && r.bt > b.y + 2 && r.y < b.bt - 2) ISSUES.push(`legend overlaps a box in ${S.id}`); });
}));
window.__issues = ISSUES;
window.__ready = true;
</script>
</body></html>
"""


# ----------------------------------------------------------------------------- glifos «renderizados»
# Como en las ilustraciones del equipo (docs/assets/mosaic-0*): objetos de vidrio con volumen, degradados, reflejo
# en el borde y halo de su color, grandes y con pie corto. Mismo dibujo para el mismo concepto en todo el proyecto.
# Sin punto y coma dentro de los SVG: el texto de la figura se comprueba contra signos vetados.
_WH = "#eef2f5"
_GLOW = lambda c, r=4: f'style="filter:drop-shadow(0 0 {r}px {c})"'


def _g(w, h, body, defs="", scale=1.0):
    return (f'<svg width="{round(w * scale)}" height="{round(h * scale)}" viewBox="0 0 {w} {h}" style="overflow:visible">'
            f'<defs>{defs}</defs>{body}</svg>')


def _lin(i, a, b, vertical=True):
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    return f'<linearGradient id="{i}" {xy}><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'


def _rad(i, stops, cx=".5", cy=".5", r=".6"):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}">{st}</radialGradient>'


def plate(scale=1.0):
    """Placa de 6 pocillos con volumen: cara superior, costado, pocillos hondos con reflejo en el borde."""
    defs = (_lin("pl-top", "#4a525b", "#191d22") + _lin("pl-side", "#22272d", "#0b0d10")
            + _rad("pl-well", [("0", "#030405"), (".72", "#11151a"), ("1", "#6a737d")], cy=".38", r=".62"))
    wells = "".join(
        f'<ellipse cx="{28 + 38 * c}" cy="{30 + 30 * r}" rx="15" ry="10.5" fill="url(#pl-well)" '
        f'stroke="rgba(255,255,255,.78)" stroke-width="1.2"/>'
        f'<path d="M{16 + 38 * c},{27 + 30 * r} Q{28 + 38 * c},{19 + 30 * r} {40 + 38 * c},{27 + 30 * r}" fill="none" '
        f'stroke="rgba(255,255,255,.55)" stroke-width="1"/>'
        for r in range(2) for c in range(3))
    body = (f'<rect x="3" y="14" width="126" height="76" rx="13" fill="url(#pl-side)" stroke="rgba(255,255,255,.45)" stroke-width="1.1"/>'
            f'<rect x="3" y="6" width="126" height="76" rx="13" fill="url(#pl-top)" stroke="rgba(255,255,255,.9)" '
            f'stroke-width="1.4" {_GLOW("rgba(255,255,255,.35)", 6)}/>'
            f'<path d="M14,10 H110" stroke="rgba(255,255,255,.35)" stroke-width="1.2" stroke-linecap="round"/>' + wells)
    return _g(132, 92, body, defs, scale)


def petri(scale=1.0):
    defs = (_rad("pe-top", [("0", "#2f363e"), (".8", "#14181c"), ("1", "#0c0e11")], cy=".4")
            + _lin("pe-side", "#1a1e23", "#08090b"))
    col = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * .62:.1f}" fill="rgba(220,232,242,.22)" '
                  f'stroke="rgba(255,255,255,.75)" stroke-width=".9"/>'
                  for x, y, rx in ((44, 34, 6), (64, 29, 5), (84, 35, 6.5), (54, 45, 5.5), (75, 46, 5), (98, 42, 4.5), (34, 44, 4.5)))
    body = (f'<path d="M6,40 V48 A60,22 0 0 0 126,48 V40" fill="url(#pe-side)" stroke="rgba(255,255,255,.5)" stroke-width="1.1"/>'
            f'<ellipse cx="66" cy="40" rx="60" ry="22" fill="url(#pe-top)" stroke="rgba(255,255,255,.92)" stroke-width="1.5" '
            f'{_GLOW("rgba(255,255,255,.35)", 6)}/>'
            f'<ellipse cx="66" cy="40" rx="51" ry="17" fill="none" stroke="rgba(255,255,255,.3)" stroke-width="1"/>'
            f'<path d="M20,32 Q40,20 70,19" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="1.3" stroke-linecap="round"/>' + col)
    return _g(132, 74, body, defs, scale)


def protein(ligand=False, scale=1.0):
    defs = (_lin("pr-body", "#7d8893", "#262b31")
            + _rad("pr-lig", [("0", "#fff7cf"), (".45", "#f6c21c"), ("1", "#a77c00")], cx=".35", cy=".35"))
    blob = ("M20,50 C6,50 6,30 20,28 C18,13 37,7 46,17 C51,4 75,6 77,20 C92,16 103,29 95,42 C104,53 89,66 75,59 "
            "C67,69 47,68 43,58 C32,66 17,60 20,50 Z")
    body = (f'<path d="{blob}" fill="url(#pr-body)" stroke="rgba(255,255,255,.8)" stroke-width="1.3" '
            f'{_GLOW("rgba(255,255,255,.18)", 3)}/>'
            '<path d="M22,30 C21,19 33,13 42,19 M50,13 C60,9 72,12 75,21" fill="none" stroke="rgba(255,255,255,.32)" '
            'stroke-width="1.2" stroke-linecap="round"/>')
    w = 104
    if ligand:
        w = 128
        body += ('<path d="M92,22 L106,12" stroke="#f6c21c" stroke-width="2" stroke-linecap="round"/>'
                 f'<circle cx="113" cy="10" r="8.5" fill="url(#pr-lig)" {_GLOW("#f6c21c", 7)}/>')
    return _g(w, 72, body, defs, scale)


def spindle(scale=1.0):
    fib = "".join(f'<path d="M10,36 Q67,{36 + k} 124,36" opacity="{.95 - abs(k) / 70:.2f}"/>'
                  for k in (-30, -22, -14, -7, 0, 7, 14, 22, 30))
    chrom = "".join(f'<path d="M{x - 3},{y - 8} L{x + 3},{y + 8} M{x + 3},{y - 8} L{x - 3},{y + 8}" />'
                    for x, y in ((62, 26), (72, 26), (62, 46), (72, 46)))
    body = (f'<g fill="none" stroke="#34d98a" stroke-width="1.25" {_GLOW("#34d98a", 4)}>{fib}</g>'
            f'<g stroke="#3d9bff" stroke-width="3.4" stroke-linecap="round" {_GLOW("#2f8cff", 5)}>{chrom}</g>'
            + "".join(f'<circle cx="{x}" cy="36" r="10" fill="none" stroke="rgba(255,255,255,.25)" stroke-width="1"/>'
                      f'<circle cx="{x}" cy="36" r="4.6" fill="{_WH}" {_GLOW("#ffffff", 6)}/>' for x in (10, 124)))
    return _g(134, 72, body, "", scale)


def reads_lens(scale=1.0):
    defs = _rad("rl-lens", [("0", "rgba(40,50,62,.55)"), (".8", "rgba(10,12,15,.85)"), ("1", "rgba(120,130,140,.5)")], cx=".4", cy=".35")
    rows = "".join(f'<path d="M{a},{y} H{b}"/>' for a, b, y in
                   ((4, 26, 12), (32, 54, 12), (8, 34, 22), (40, 58, 22), (4, 20, 32), (26, 50, 32), (10, 36, 42), (42, 56, 42), (6, 28, 52)))
    body = (f'<g stroke="#3d9bff" stroke-width="3" stroke-linecap="round" {_GLOW("#2f8cff", 4)}>{rows}</g>'
            f'<path d="M2,60 H60" stroke="rgba(255,255,255,.6)" stroke-width="1.2"/>'
            f'<circle cx="94" cy="28" r="23" fill="url(#rl-lens)" stroke="{_WH}" stroke-width="2" {_GLOW("rgba(255,255,255,.4)", 6)}/>'
            f'<g stroke="#3d9bff" stroke-width="4" stroke-linecap="round" {_GLOW("#2f8cff", 4)}><path d="M78,20 H110 M80,34 H108"/></g>'
            f'<rect x="91.5" y="10" width="5" height="34" rx="2" fill="#f6c21c" {_GLOW("#f6c21c", 5)}/>'
            f'<path d="M77,45 L64,60" stroke="{_WH}" stroke-width="3.5" stroke-linecap="round"/>')
    return _g(122, 66, body, defs, scale)


def pedigree(scale=1.0):
    st = f'fill="rgba(255,255,255,.06)" stroke="{_WH}" stroke-width="1.7" {_GLOW("rgba(255,255,255,.35)", 4)}'
    body = (f'<rect x="10" y="4" width="20" height="20" rx="2.5" {st}/><circle cx="84" cy="14" r="10" {st}/>'
            f'<path d="M30,14 H74 M52,14 V32 M20,32 H84 M20,32 V42 M84,32 V42" fill="none" stroke="{_WH}" stroke-width="1.7"/>'
            f'<rect x="10" y="42" width="20" height="20" rx="2.5" {st}/>'
            f'<circle cx="84" cy="52" r="10" fill="#2f8cff" stroke="{_WH}" stroke-width="1.7" {_GLOW("#2f8cff", 7)}/>')
    return _g(100, 66, body, "", scale)


def longread(scale=1.0):
    defs = _lin("lr-a", "#5aa8ff", "#1f6fd6", vertical=False) + _lin("lr-b", "#1f6fd6", "#5aa8ff", vertical=False)
    body = (f'<path d="M12,10 H128" stroke="{_WH}" stroke-width="1.6"/>'
            f'<path d="M4,10 L14,4 V16 Z M136,10 L126,4 V16 Z" fill="{_WH}"/><path d="M70,4 V16" stroke="{_WH}" stroke-width="1.4"/>'
            f'<rect x="4" y="26" width="52" height="13" rx="2" fill="url(#lr-a)" {_GLOW("#2f8cff", 5)}/>'
            '<rect x="56" y="26" width="26" height="13" fill="#07090b" stroke="rgba(255,255,255,.6)" stroke-width="1"/>'
            f'<rect x="82" y="26" width="54" height="13" rx="2" fill="url(#lr-b)" {_GLOW("#2f8cff", 5)}/>')
    return _g(140, 44, body, defs, scale)


def splice(scale=1.0):
    defs = _lin("sp-ex", "#5aa8ff", "#1f6fd6")
    body = (f'<path d="M4,40 H136" stroke="rgba(255,255,255,.55)" stroke-width="1.4"/>'
            f'<rect x="10" y="31" width="30" height="18" rx="3" fill="url(#sp-ex)" {_GLOW("#2f8cff", 6)}/>'
            f'<rect x="100" y="31" width="30" height="18" rx="3" fill="url(#sp-ex)" {_GLOW("#2f8cff", 6)}/>'
            f'<path d="M40,31 Q70,-4 100,31" fill="none" stroke="{_WH}" stroke-width="1.6" stroke-dasharray="5 4" '
            f'{_GLOW("rgba(255,255,255,.45)", 3)}/>'
            f'<circle cx="70" cy="14" r="3.4" fill="#07090b" stroke="{_WH}" stroke-width="1.4"/>')
    return _g(140, 56, body, defs, scale)


def variant_t(scale=1.0):
    defs = _lin("vt-bar", "#5b636c", "#22272d")
    dots = lambda x0: "".join(f'<circle cx="{x0 + 7 * i}" cy="16" r="2" fill="{_WH}"/>' for i in range(3))
    body = (dots(4) + dots(122)
            + f'<rect x="26" y="11" width="88" height="10" rx="5" fill="url(#vt-bar)" stroke="rgba(255,255,255,.75)" stroke-width="1.1"/>'
            + f'<rect x="66" y="2" width="6" height="28" rx="2" fill="#f6c21c" {_GLOW("#f6c21c", 6)}/>')
    return _g(140, 32, body, defs, scale)


def docs(scale=1.0):
    defs = _lin("dc-p", "#2b3138", "#101317")
    page = lambda x, y: (f'<path d="M{x},{y} H{x + 26} L{x + 36},{y + 10} V{y + 46} H{x} Z" fill="url(#dc-p)" '
                         f'stroke="{_WH}" stroke-width="1.5"/><path d="M{x + 26},{y} V{y + 10} H{x + 36}" fill="none" stroke="{_WH}" stroke-width="1.3"/>'
                         f'<path d="M{x + 7},{y + 20} H{x + 29} M{x + 7},{y + 28} H{x + 29} M{x + 7},{y + 36} H{x + 21}" stroke="rgba(255,255,255,.7)" stroke-width="1.3"/>')
    return _g(62, 66, page(18, 2) + page(10, 9) + page(2, 16), defs, scale)


def doc(scale=1.0):
    defs = _lin("dc1-p", "#2b3138", "#101317")
    body = (f'<path d="M4,2 H34 L46,14 V62 H4 Z" fill="url(#dc1-p)" stroke="{_WH}" stroke-width="1.6" {_GLOW("rgba(255,255,255,.3)", 5)}/>'
            f'<path d="M34,2 V14 H46" fill="none" stroke="{_WH}" stroke-width="1.4"/>'
            '<path d="M12,26 H38 M12,35 H38 M12,44 H30" stroke="rgba(255,255,255,.75)" stroke-width="1.5"/>'
            f'<circle cx="38" cy="54" r="6" fill="#2f8cff" {_GLOW("#2f8cff", 5)}/>')
    return _g(50, 66, body, defs, scale)


def veto(scale=1.0):
    body = (f'<circle cx="32" cy="32" r="25" fill="rgba(246,194,28,.06)" stroke="#f6c21c" stroke-width="6" {_GLOW("#f6c21c", 8)}/>'
            '<path d="M14,14 L50,50" stroke="#f6c21c" stroke-width="6" stroke-linecap="round"/>')
    return _g(64, 64, body, "", scale)


def homolog(m1, m2, w=170, cls="ico"):
    """Dos homólogos h1/h2 como tubos de vidrio con segmentos, marca amarilla (truncante) y rombo azul (missense)."""
    defs = _lin("hm-tube", "#5a626b", "#1a1e23")

    def bar(y, marks, name):
        out = (f'<text x="0" y="{y + 5}" font-size="13" fill="#c5ccd2" font-family="Segoe UI">{name}</text>'
               f'<rect x="24" y="{y - 6}" width="{w - 28}" height="12" rx="6" fill="url(#hm-tube)" '
               f'stroke="rgba(255,255,255,.8)" stroke-width="1.1"/>'
               + "".join(f'<path d="M{24 + (w - 28) * f:.0f},{y - 6} V{y + 6}" stroke="rgba(255,255,255,.35)" stroke-width="1"/>'
                         for f in (.18, .82)))
        for kind, x in marks:
            if kind == "t":
                out += f'<rect x="{x - 2.5}" y="{y - 11}" width="5" height="22" rx="2" fill="#f6c21c" {_GLOW("#f6c21c", 5)}/>'
            else:
                out += (f'<rect x="{x - 7}" y="{y - 7}" width="14" height="14" transform="rotate(45 {x} {y})" '
                        f'fill="#3d9bff" {_GLOW("#2f8cff", 6)}/>')
        return out
    return (f'<svg class="{cls}" width="{w}" height="62" viewBox="0 0 {w} 62" style="overflow:visible"><defs>{defs}</defs>'
            f'{bar(16, m1, "h1")}{bar(46, m2, "h2")}</svg>')


ICON_PHASE = homolog([("t", 70)], [("d", 128)], 170)
ICON_CIS = homolog([("t", 66), ("d", 116)], [], 152)
ICON_TRANS = homolog([("t", 66)], [("d", 116)], 152)
ICON_SPINDLE = spindle()
ICON_DOC = doc(.62)
ICON_READS = reads_lens(.42)
ICON_STACK = docs(.62)
ICON_CELL = ('<svg width="40" height="40" viewBox="0 0 40 40"><ellipse cx="20" cy="20" rx="17" ry="15" fill="rgba(255,255,255,.05)" '
             f'stroke="{_WH}" stroke-width="1.5"/><g stroke="#3d9bff" stroke-width="3" stroke-linecap="round" {_GLOW("#2f8cff", 4)}>'
             '<path d="M12,14 L15,20 M20,11 L20,18 M26,15 L23,21 M14,26 L19,27 M24,27 L28,24"/></g></svg>')

G_PEDIGREE, G_LONGREAD, G_SPLICE = pedigree(), longread(), splice()
G_PROTEIN, G_PROTEIN_PLAIN, G_SPINDLE, G_PETRI = protein(True), protein(), spindle(), petri()
G_VETO, G_READS_LENS, G_VARIANT_T, G_DOC, G_STACK = veto(), reads_lens(), variant_t(), doc(), docs()


def glyphs(*items):
    """Fila de glifos con su pie corto debajo, como en las ilustraciones del equipo."""
    return '<div class="glyphs">' + "".join(f'<figure>{svg}<figcaption>{cap}</figcaption></figure>' for svg, cap in items) + "</div>"


OBS_GLYPHS = [
    glyphs((pedigree(), "Parents"), (longread(), "Targeted long read")),
    glyphs((protein(), "BUBR1"), (spindle(), "Spindle checkpoint")),
    glyphs((splice(), "Splice junction (RNA)"), (longread(), "Targeted long read")),
    glyphs((doc(), "Clinical records"),),
    glyphs((reads_lens(), "Existing alignment"),),
    glyphs((docs(), "Solved cases"),),
]
MEAS_GLYPHS = [
    glyphs((variant_t(.82), "PTC transcript"), (protein(scale=.82), "Full-length product")),
    glyphs((protein(True, .78), "Engagement, then BUBR1"), (spindle(.78), "Function")),
    glyphs((spindle(.78), "Segregation errors"), (petri(.78), "Clonogenic survival")),
]
ASSAY_GLYPHS = glyphs((protein(scale=.85), "BUBR1"), (spindle(.85), "Checkpoint, segregation"))
ADV_GLYPHS = glyphs((spindle(.8), "Errors per completed mitosis"), (petri(.8), "Clonogenic survival"))

PLATE = plate(.62).replace("<svg ", '<svg class="plate" ', 1)
PLATE_SMALL = plate(.5).replace("<svg ", '<svg class="plate" ', 1)


def legend(items, static=False):
    out = []
    for color, dashed, text in items:
        dash = ' stroke-dasharray="10 7"' if dashed else ""
        out.append(f'<span><svg width="58" height="12"><line x1="2" y1="6" x2="56" y2="6" stroke="{color}" '
                   f'stroke-width="2.6"{dash}/></svg>{text}</span>')
    style = ' style="position:static;margin-top:0"' if static else ""
    return f'<div class="legend"{style}>' + "".join(out) + "</div>"


def render_html():
    n = check_sources()
    d = data(n)
    d["plate"] = PLATE
    html = (TEMPLATE.replace("__DATA__", json.dumps(d, ensure_ascii=False))
            .replace("__OBSG__", json.dumps(OBS_GLYPHS)).replace("__MEASG__", json.dumps(MEAS_GLYPHS))
            .replace("__ASSAY_GLYPHS__", ASSAY_GLYPHS)
            .replace("__ADV_GLYPHS__", ADV_GLYPHS)
            .replace("__VETO__", G_VETO)
            .replace("__PLATE__", PLATE_SMALL).replace("__ICON_PHASE__", ICON_PHASE).replace("__ICON_CIS__", ICON_CIS)
            .replace("__ICON_TRANS__", ICON_TRANS).replace("__ICON_SPINDLE__", ICON_SPINDLE)
            .replace("__ICON_DOC__", ICON_DOC).replace("__ICON_READS__", ICON_READS)
            .replace("__ICON_STACK__", ICON_STACK).replace("__ICON_CELL__", ICON_CELL)
            .replace("__LEGEND__", legend((("#2f8cff", True, "The child's genotype, proposed observation"),
                                           ("#f6c21c", True, "Experiment in engineered cells, proposed"))))
            .replace("__LEGEND3__", legend((("#2f8cff", True, "Observation on the child's data or records"),
                                            ("#f6c21c", True, "Experiment in engineered cells"),
                                            ("#34d98a", True, "Computational study on public data")), static=True))
            .replace("__LEGEND2__", legend((("#f6c21c", True, "Experiment in engineered cells, proposed"),))))
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, SLUG + ".html")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    return path, n


def render(width=1600):
    """HTML siempre. Con Playwright: PNG completo (tres láminas), miniatura y las láminas A y C para el PDF."""
    path, n = render_html()
    out = {"html": path, "figure_class": FIG_CLASS, "evidence_origin": ORIGIN, "guards": n}
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("AVISO fig15: sin playwright en este Python; HTML escrito, PNG no.")
        return out
    url = pathlib.Path(path).resolve().as_uri()
    png = os.path.join(OUT_DIR, SLUG + ".png")
    thumb = os.path.join(OUT_DIR, "thumb", SLUG + ".png")
    os.makedirs(os.path.dirname(thumb), exist_ok=True)
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            b = p.chromium.launch(headless=True)
        for target, scale, panels in ((png, 2, True), (thumb, 0.4, False)):
            ctx = b.new_context(viewport={"width": width, "height": 1000}, device_scale_factor=scale)
            pg = ctx.new_page()
            pg.goto(url)
            pg.wait_for_function("window.__ready === true")
            if panels:
                # Ningún texto visible puede llevar los signos vetados por estilo
                issues = pg.evaluate("window.__issues")
                if issues:
                    raise SystemExit("fig15: elementos tapados o cruzados:\n  " + "\n  ".join(issues))
                txt = pg.evaluate("document.body.innerText")
                bad = [m for m in FORBIDDEN_MARKS if m in txt]
                if bad:
                    raise SystemExit(f"fig15: texto visible con signos vetados: {bad}")
                for sel, t in PRINT_PANELS:
                    pg.locator(sel).screenshot(path=t)
            pg.screenshot(path=target, full_page=True)
            ctx.close()
        b.close()
    out.update({"png": png, "thumb": thumb, "print": [t for _, t in PRINT_PANELS]})
    return out


def load_and_build():
    return render(), {}


if __name__ == "__main__":
    print(render())
