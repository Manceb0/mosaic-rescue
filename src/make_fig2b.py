#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 2 rehecha — lollipops sobre coordenadas de proteina, no barras resumen.

Cada variante missense de ClinVar se dibuja en SU posicion. Las 35 benignas se ven
donde caen, no como un numero. Ampliacion 950-1050 a resolucion de residuo.
"""
import io, json, collections

D = json.load(io.open("work/clinvar/landscape_missense.json", encoding="utf-8"))
V, CAND, L = D["variants"], D["candidate"], 1050
by = collections.defaultdict(list)
for v in V:
    by[v["cls"]].append(v["pos"])

X0, XW = 96, 1244
def px(r): return X0 + (r - 1) / (L - 1) * XW

# ---------- Panel A ----------
AXIS = 268
def lolli(poss, up, col, h, rad):
    out = ""
    for p in poss:
        x = px(p)
        y2 = AXIS - h if up else AXIS + h
        out += (f'<line x1="{x:.1f}" y1="{AXIS}" x2="{x:.1f}" y2="{y2}" stroke="{col}" stroke-width="1.3" opacity=".85"/>'
                f'<circle cx="{x:.1f}" cy="{y2}" r="{rad}" fill="{col}" opacity=".9"/>')
    return out

plp   = lolli(by["P/LP"], True, "var(--path)", 86, 5.5)
blb   = lolli(by["B/LB"], False, "var(--benign)", 74, 4)
confl = lolli(by["CONFLICTIVA"], False, "var(--confl)", 34, 2.8)

# VUS: 1426. Dibujados individualmente pero tenues: la MASA es el mensaje.
vus = "".join(f'<line x1="{px(p):.1f}" y1="{AXIS-30}" x2="{px(p):.1f}" y2="{AXIS-4}" '
              f'stroke="var(--vus)" stroke-width="1" opacity=".22"/>' for p in by["VUS"])

# dominios: CONTEXTO externo, no evidencia. Se dibujan tenues y etiquetados.
DOM = [(1, 200, "TPR N-terminal"), (400, 500, "GLEBS · unión a BUB3"), (766, 1050, "dominio pseudoquinasa · estabilidad")]
doms = ""
for a, b, nm in DOM:
    doms += (f'<rect x="{px(a):.1f}" y="{AXIS+108}" width="{px(b)-px(a):.1f}" height="16" '
             f'fill="var(--dom)" stroke="var(--rule)" stroke-width=".8"/>'
             f'<text x="{(px(a)+px(b))/2:.1f}" y="{AXIS+120}" class="mono" text-anchor="middle" opacity=".85">{nm}</text>')

# ---------- Panel B: ampliacion 950-1050 ----------
Z0, Z1 = 950, 1050
ZX0, ZXW, ZAXIS = 96, 1244, 660
def zx(r): return ZX0 + (r - Z0) / (Z1 - Z0) * ZXW
zoom = ""
zc = collections.Counter()
for v in V:
    if not (Z0 <= v["pos"] <= Z1):
        continue
    zc[v["cls"]] += 1
    x = zx(v["pos"])
    if v["cls"] == "B/LB":
        zoom += (f'<line x1="{x:.1f}" y1="{ZAXIS}" x2="{x:.1f}" y2="{ZAXIS+52}" stroke="var(--benign)" stroke-width="1.6"/>'
                 f'<circle cx="{x:.1f}" cy="{ZAXIS+52}" r="5" fill="var(--benign)"/>'
                 f'<text x="{x:.1f}" y="{ZAXIS+70}" class="mono" fill="var(--benign)" text-anchor="middle">{v["pos"]}</text>')
    elif v["cls"] == "CONFLICTIVA":
        zoom += (f'<line x1="{x:.1f}" y1="{ZAXIS}" x2="{x:.1f}" y2="{ZAXIS+30}" stroke="var(--confl)" stroke-width="1.4"/>'
                 f'<circle cx="{x:.1f}" cy="{ZAXIS+30}" r="3.5" fill="var(--confl)"/>')
    else:
        zoom += (f'<line x1="{x:.1f}" y1="{ZAXIS-46}" x2="{x:.1f}" y2="{ZAXIS-6}" '
                 f'stroke="var(--vus)" stroke-width="1.4" opacity=".55"/>')
# reglilla de residuos
ticks = ""
for r in range(Z0, Z1 + 1, 10):
    ticks += (f'<line x1="{zx(r):.1f}" y1="{ZAXIS}" x2="{zx(r):.1f}" y2="{ZAXIS+7}" stroke="var(--ink-soft)" stroke-width="1"/>'
              f'<text x="{zx(r):.1f}" y="{ZAXIS+20}" class="mono" text-anchor="middle">{r}</text>')

HTML = f"""<title>BUBR1 Missense Landscape</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --path:#B4453A;--benign:#2E7D6B;--vus:#8892A0;--confl:#C9A227;--target:#C07A2E;
 --measured:#1F4E5F;--dom:#EAE6DA;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--path:#E0776A;--benign:#63BFA6;--vus:#78848F;
 --confl:#E0C458;--target:#E0A458;--measured:#6FB3C6;--dom:#242C33;}}}}
:root[data-theme="dark"]{{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--path:#E0776A;--benign:#63BFA6;--vus:#78848F;--confl:#E0C458;
 --target:#E0A458;--measured:#6FB3C6;--dom:#242C33;}}
body{{background:var(--ground);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;
 margin:0;padding:clamp(20px,4vw,52px) clamp(16px,4vw,52px) 60px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:24px}}
.eyebrow{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--ink-soft);margin:0}}
h1{{font-size:clamp(25px,3.8vw,38px);font-weight:700;letter-spacing:-.022em;line-height:1.1;margin:10px 0 0}}
.sub{{margin:12px 0 0;font-size:clamp(15px,1.7vw,19px);line-height:1.45;color:var(--ink);
 font-style:italic;border-left:2px solid var(--target);padding-left:16px;max-width:54ch}}
.figframe{{background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:8px;overflow-x:auto}}
svg{{display:block;width:100%;height:auto;min-width:1000px}}
.cap{{display:grid;gap:8px;font-size:13px;line-height:1.55;color:var(--ink-soft);max-width:80ch}}
.cap strong{{color:var(--ink);font-weight:600}}
.foot{{display:flex;flex-wrap:wrap;gap:10px 26px;border-top:1px solid var(--rule);padding-top:16px;
 font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft)}}
</style>
<div class="wrap">
<header>
 <p class="eyebrow">Mosaic Rescue · Figura 2</p>
 <h1>BUBR1 missense landscape</h1>
 <p class="sub">A hypothesis that weakened under independent evidence.</p>
</header>

<div class="figframe">
<svg viewBox="0 0 1440 810" role="img" aria-label="Cada variante missense de ClinVar en su posición a lo largo de BUBR1.">
<style>
 .lbl{{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:13px;fill:var(--ink)}}
 .lbl-sm{{font-family:"IBM Plex Sans",sans-serif;font-weight:500;font-size:11.5px;fill:var(--ink-soft)}}
 .mono{{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.06em;font-weight:500;fill:var(--ink-soft)}}
 .sect{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
        text-transform:uppercase;fill:var(--ink-soft);font-weight:500}}
</style>

<text x="{X0}" y="34" class="sect">A · Las {len(V):,} missense de ClinVar, cada una en su residuo</text>
<text x="1340" y="34" class="mono" text-anchor="end">EXTERNAL · ClinVar 2026-08-22</text>
<line x1="{X0}" y1="46" x2="1340" y2="46" stroke="var(--rule)"/>

<text x="{X0-10}" y="{AXIS-84}" class="lbl" fill="var(--path)" text-anchor="end">P/LP</text>
<text x="{X0-10}" y="{AXIS-70}" class="mono" text-anchor="end">n={len(by['P/LP'])}</text>
{plp}
<text x="{X0-10}" y="{AXIS-20}" class="lbl" fill="var(--vus)" text-anchor="end">VUS</text>
<text x="{X0-10}" y="{AXIS-6}" class="mono" text-anchor="end">n={len(by['VUS']):,}</text>
{vus}
<line x1="{X0}" y1="{AXIS}" x2="{X0+XW}" y2="{AXIS}" stroke="var(--ink)" stroke-width="1.6"/>
{confl}
{blb}
<text x="{X0-10}" y="{AXIS+78}" class="lbl" fill="var(--benign)" text-anchor="end">B/LB</text>
<text x="{X0-10}" y="{AXIS+92}" class="mono" text-anchor="end">n={len(by['B/LB'])}</text>

<line x1="{px(CAND):.1f}" y1="{AXIS-120}" x2="{px(CAND):.1f}" y2="{AXIS+100}" stroke="var(--target)" stroke-width="2.5"/>
<circle cx="{px(CAND):.1f}" cy="{AXIS}" r="9" fill="var(--target)"/>
<circle cx="{px(CAND):.1f}" cy="{AXIS}" r="16" fill="none" stroke="var(--target)" stroke-width="1.5" opacity=".5"/>
<text x="{px(CAND):.1f}" y="{AXIS-130}" class="lbl" fill="var(--target)" text-anchor="middle">candidato del paciente · residuo {CAND}</text>
<text x="{px(CAND):.1f}" y="{AXIS-116}" class="mono" fill="var(--target)" text-anchor="middle">MEASURED · VUS</text>

{doms}
<text x="{X0}" y="{AXIS+146}" class="mono">1</text>
<text x="{X0+XW}" y="{AXIS+146}" class="mono" text-anchor="end">{L} aa</text>
<text x="{X0}" y="{AXIS+166}" class="lbl-sm">Los dominios son contexto externo (UniProt), no evidencia de este análisis. La evidencia son las posiciones de los lollipops.</text>

<text x="{X0}" y="{AXIS+206}" class="lbl">Una sola missense P/LP en todo el gen (residuo {by['P/LP'][0]}). Las 35 benignas se reparten de punta a punta. El 95 % son VUS.</text>

<!-- ═══ PANEL B ═══ -->
<text x="{ZX0}" y="{ZAXIS-124}" class="sect">B · Ampliación {Z0}–{Z1} · resolución de residuo</text>
<text x="1340" y="{ZAXIS-124}" class="mono" text-anchor="end">{sum(zc.values())} missense en la ventana</text>
<line x1="{ZX0}" y1="{ZAXIS-112}" x2="1340" y2="{ZAXIS-112}" stroke="var(--rule)"/>
<text x="{ZX0-10}" y="{ZAXIS-24}" class="lbl-sm" fill="var(--vus)" text-anchor="end">VUS {zc['VUS']}</text>
<text x="{ZX0-10}" y="{ZAXIS+34}" class="lbl-sm" fill="var(--confl)" text-anchor="end">confl. {zc['CONFLICTIVA']}</text>
<text x="{ZX0-10}" y="{ZAXIS+56}" class="lbl-sm" fill="var(--benign)" text-anchor="end">B/LB {zc['B/LB']}</text>
{zoom}
<line x1="{ZX0}" y1="{ZAXIS}" x2="{ZX0+ZXW}" y2="{ZAXIS}" stroke="var(--ink)" stroke-width="1.4"/>
{ticks}
<line x1="{zx(CAND):.1f}" y1="{ZAXIS-104}" x2="{zx(CAND):.1f}" y2="{ZAXIS+8}" stroke="var(--target)" stroke-width="2.5"/>
<circle cx="{zx(CAND):.1f}" cy="{ZAXIS}" r="8" fill="var(--target)"/>
<g transform="translate({zx(CAND)-152:.1f},{ZAXIS-104})">
  <rect x="0" y="-24" width="304" height="66" rx="3" fill="var(--panel)" stroke="var(--target)"/>
  <text x="152" y="-8" class="lbl" fill="var(--target)" text-anchor="middle">residuo {CAND} · tres cambios distintos</text>
  <text x="12" y="12" class="mono" fill="var(--target)">T&gt;G</text>
  <text x="66" y="12" class="lbl-sm" fill="var(--target)">nuestro paciente — no está en ClinVar</text>
  <text x="12" y="28" class="mono" fill="var(--vus)">T&gt;A</text>
  <text x="66" y="28" class="lbl-sm">mismo aminoácido · ClinVar VUS</text>
  <text x="12" y="44" class="mono" fill="var(--benign)">T&gt;C</text>
  <text x="66" y="44" class="lbl-sm">sinónima · Likely benign</text>
</g>
<text x="{ZX0}" y="{ZAXIS+104}" class="lbl-sm">Vecinos inmediatos con missense benignas: residuos 977 (×2), 1004, 1013, 1040 y 1042.</text>

<line x1="{X0}" y1="762" x2="1340" y2="762" stroke="var(--rule)"/>
<text x="{X0}" y="786" class="lbl">Current clinical evidence does not support this region as a pathogenic missense hotspot,</text>
<text x="{X0}" y="802" class="lbl">and an independent submission of the same amino-acid substitution is also VUS.</text>
</svg>
</div>

<div class="cap">
<p><strong>Qué se ve aquí que una barra no mostraba.</strong> Las 35 benignas no son un
número: están repartidas de punta a punta del gen, incluidas <strong>seis en la ventana del
candidato</strong> y una en el residuo inmediatamente contiguo. La única P/LP del gen está
en el residuo {by['P/LP'][0]}, lejos.</p>

<p><strong>El residuo {CAND} tiene tres cambios nucleotídicos distintos documentados.</strong>
El del paciente no está en ClinVar. Otro produce <em>el mismo cambio de aminoácido</em> por
otra ruta y está clasificado <strong>VUS</strong> por un <em>submitter</em> independiente
con criterios. El tercero es sinónimo y benigno.</p>

<p><strong>Por eso <code>PS1</code> y <code>PM5</code> no aplican</strong>, y por eso el
mensaje no es «la missense es benigna» sino que la interpretación clínica de missense en
este gen está mayoritariamente sin resolver: {len(by['VUS']):,} de {len(V):,} son VUS.</p>

<p><strong>Los dominios son contexto, no evidencia.</strong> Se dibujan tenues a propósito:
esa banda se podía trazar antes de analizar al paciente. Lo que no se podía trazar antes es
dónde cae cada lollipop.</p>
</div>

<div class="foot">
 <span>CLINVAR 2026-08-22 · EXTERNAL</span>
 <span>CANDIDATO · MEASURED · VUS</span>
 <span>REVEL 0,472 — PP3 NO APLICA</span>
 <span>PM1 · PS1 · PM5 NO APLICAN</span>
</div>
</div>
"""
io.open("figures/fig2_landscape.html", "w", encoding="utf-8", newline="\n").write(HTML)
print(f"  figures/fig2_landscape.html ({len(HTML)/1024:.0f} KB)")
print(f"  P/LP {len(by['P/LP'])} · B/LB {len(by['B/LB'])} · confl {len(by['CONFLICTIVA'])} · VUS {len(by['VUS'])}")
print(f"  ventana {Z0}-{Z1}: {dict(zc)}")
