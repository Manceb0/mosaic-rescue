#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 8 — el baseline externo, y por que el puesto 2 pesa mas que el 1.

Dos paneles:
  A. los dos rankings, uno frente a otro. Motores sin codigo comun.
  B. QUE EVIDENCIA sostiene a cada gen del top-10 externo. Es el panel que
     importa: un ranking sin esto solo dice quien gano, no si el ganador es
     creible.

SANEADO: simbolos de gen, conteos y clases de variante. Sin coordenadas, sin
genotipos, sin identidad de variantes.
"""
import io, csv, sys, pickle, collections

sys.path.insert(0, ".")
RUN = "work/exomiser/runs/BASELINE-PRIMARY"
GENE = "BUB1B"
W, H = 1440, 1040


def load_genes():
    rows = list(csv.reader(io.open(f"{RUN}/BASELINE-PRIMARY.genes.tsv", encoding="utf-8"),
                           delimiter="\t"))
    ix = {h.lstrip("#"): i for i, h in enumerate(rows[0])}
    best = {}
    for r in rows[1:]:
        g, rk = r[ix["GENE_SYMBOL"]], int(r[ix["RANK"]])
        if g not in best or rk < best[g][0]:
            best[g] = (rk, float(r[ix["EXOMISER_GENE_COMBINED_SCORE"]]), r[ix["MOI"]])
    return sorted(((g, v[1], v[2]) for g, v in best.items()),
                  key=lambda t: -t[1]), len(best)


def load_profile(genes):
    rows = list(csv.reader(io.open(f"{RUN}/BASELINE-PRIMARY.variants.tsv", encoding="utf-8"),
                           delimiter="\t"))
    ix = {h.lstrip("#"): i for i, h in enumerate(rows[0])}
    n, nofreq, path = collections.Counter(), collections.Counter(), collections.Counter()
    for r in rows[1:]:
        g = r[ix["GENE_SYMBOL"]]
        n[g] += 1
        if not r[ix["MAX_FREQ"]].strip():
            nofreq[g] += 1
        c = r[ix["CLINVAR_PRIMARY_INTERPRETATION"]]
        if "PATHOGENIC" in c and "CONFLICT" not in c:
            path[g] += 1
    return {g: (n[g], nofreq[g], path[g]) for g in genes}


def load_ours():
    res = pickle.load(io.open("work/gw/mode_b_results_v4.pkl", "rb"))
    return [row[0] for row in res["B0_FULL_PROBAND"]]


ext, n_genes = load_genes()
ours = load_ours()
top = [g for g, _, _ in ext[:10]]
prof = load_profile(top)

# ---------------- A · los dos rankings ----------------
AY, RH = 190, 42
LX, RX = 220, 780
a = ""
for i, (g, sc, moi) in enumerate(ext[:10]):
    y = AY + i * RH
    hi = g == GENE
    a += ('<rect x="%d" y="%d" width="330" height="30" rx="6" fill="%s" opacity="%s"/>'
          '<text x="%d" y="%d" class="lbl" fill="%s">%d. %s</text>'
          '<text x="%d" y="%d" class="mono" fill="%s" text-anchor="end">%s · %.3f</text>'
          % (LX, y, "var(--alive)" if hi else "var(--panel2)", "0.9" if hi else "1",
             LX + 14, y + 20, "var(--on-hi)" if hi else "var(--ink)", i + 1, g,
             LX + 316, y + 20, "var(--on-hi)" if hi else "var(--ink-soft)", moi, sc))
for i, g in enumerate(ours[:10]):
    y = AY + i * RH
    hi = g == GENE
    a += ('<rect x="%d" y="%d" width="330" height="30" rx="6" fill="%s" opacity="%s"/>'
          '<text x="%d" y="%d" class="lbl" fill="%s">%d. %s</text>'
          % (RX, y, "var(--alive)" if hi else "var(--panel2)", "0.9" if hi else "1",
             RX + 14, y + 20, "var(--on-hi)" if hi else "var(--ink)", i + 1, g))

# la linea que une el mismo gen en los dos rankings
ei = next(i for i, (g, _, _) in enumerate(ext[:10]) if g == GENE)
oi = ours.index(GENE)
a += ('<path d="M%d,%d C%d,%d %d,%d %d,%d" stroke="var(--alive)" stroke-width="2.5" fill="none"/>'
      % (LX + 330, AY + ei * RH + 15, LX + 430, AY + ei * RH + 15,
         RX - 100, AY + oi * RH + 15, RX, AY + oi * RH + 15))

# ---------------- B · perfil de evidencia ----------------
BY = 900
maxn = max(p[0] for p in prof.values())
BW, BXL = 900, 220
b = ""
for i, g in enumerate(top):
    nv, nf, pt = prof[g]
    x = BXL + (i * (BW / 10))
    w = BW / 10 - 10
    h_all = 120 * nv / maxn
    h_nof = 120 * nf / maxn
    b += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="var(--flow)" opacity="0.45"/>'
          '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="var(--dead)" opacity="0.9"/>'
          % (x, BY - h_all, w, h_all, x, BY - h_nof, w, h_nof))
    if pt:
        b += ('<circle cx="%.1f" cy="%.1f" r="6" fill="var(--alive)"/>'
              '<text x="%.1f" y="%.1f" class="mono" text-anchor="middle" fill="var(--on-hi)">%d</text>'
              % (x + w / 2, BY - h_all - 18, x + w / 2, BY - h_all - 14.5, pt))
    b += ('<text x="%.1f" y="%d" class="mono" text-anchor="end" transform="rotate(-40 %.1f %d)">%s</text>'
          '<text x="%.1f" y="%d" class="mono" text-anchor="middle">%d</text>'
          % (x + w / 2, BY + 16, x + w / 2, BY + 16, g, x + w / 2, BY - h_all - 34 if pt else BY - h_all - 8, nv))

b += ('<rect x="%d" y="%d" width="14" height="10" rx="3" fill="var(--flow)" opacity="0.45"/>'
      '<text x="%d" y="%d" class="mono">variantes que sostienen al gen</text>'
      '<rect x="%d" y="%d" width="14" height="10" rx="3" fill="var(--dead)" opacity="0.9"/>'
      '<text x="%d" y="%d" class="mono">de esas, SIN frecuencia poblacional asignable</text>'
      '<circle cx="%d" cy="%d" r="6" fill="var(--alive)"/>'
      '<text x="%d" y="%d" class="mono">aserciones patogenicas en ClinVar</text>'
      % (BXL, BY + 46, BXL + 20, BY + 55,
         BXL + 300, BY + 46, BXL + 320, BY + 55,
         BXL + 707, BY + 51, BXL + 720, BY + 55))

svg = (
    '<svg viewBox="0 0 %d %d" role="img"\n'
    ' aria-label="Baseline externo con Exomiser frente a nuestro ranking">\n'
    '<style>\n'
    '.ttl{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:25px;fill:var(--ink)}\n'
    '.sub{font-family:"IBM Plex Mono",monospace;font-size:11px;fill:var(--ink-soft)}\n'
    '.big{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:16px;fill:var(--ink)}\n'
    '.lbl{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:13px;fill:var(--ink)}\n'
    '.mono{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.04em;fill:var(--ink-soft)}\n'
    '</style>\n'
    '<rect width="%d" height="%d" fill="var(--ground)"/>\n'
    '<text x="70" y="52" class="ttl">Baseline externo: dos motores sin codigo comun</text>\n'
    '<text x="70" y="78" class="sub">EXTERNAL: Exomiser 14.1.0, datos 2402 hg38 + fenotipo, '
    'desde el VCF original y los 7 terminos HPO. No recibio ningun resultado nuestro.</text>\n'
    '<text x="70" y="93" class="sub">DERIVED: la comparacion y el perfil de evidencia, calculados aqui.</text>\n'
    '<line x1="70" y1="112" x2="%d" y2="112" stroke="var(--rule)"/>\n'
    '<text x="70" y="146" class="big">A - los dos rankings, top 10</text>\n'
    '<text x="%d" y="172" class="mono">EXOMISER - %d genes unicos</text>\n'
    '<text x="%d" y="172" class="mono">NUESTRO modo B - B0_FULL_PROBAND</text>\n%s\n'
    '<text x="70" y="%d" class="big">B - que evidencia sostiene a cada gen del top 10 externo</text>\n'
    '<text x="70" y="%d" class="mono">'
    'un ranking sin esto dice quien gano, no si el ganador es creible</text>\n%s\n'
    '</svg>'
    % (W, H, W, H, W - 70, LX, n_genes, RX, a, BY - 200, BY - 182, b))

STYLE = """<!doctype html><meta charset="utf-8"><title>Figura 8</title><style>
:root{--ground:#FAFAF8;--panel2:#EFEFEC;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --flow:#8C99A4;--alive:#2E7D6B;--dead:#B4453A;--on-hi:#FFFFFF;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#0E1216;--panel2:#1B222A;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--flow:#4A555F;--alive:#2E7D6B;--dead:#E0776A;
 --on-hi:#FFFFFF;}}
:root[data-theme="dark"]{--ground:#0E1216;--panel2:#1B222A;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--flow:#4A555F;--alive:#2E7D6B;--dead:#E0776A;--on-hi:#FFFFFF;}
body{margin:0;background:var(--ground);font-family:"IBM Plex Sans",system-ui,sans-serif}
</style>"""

io.open("figures/fig8_baseline.html", "w", encoding="utf-8").write(STYLE + svg)
print("figures/fig8_baseline.html")
