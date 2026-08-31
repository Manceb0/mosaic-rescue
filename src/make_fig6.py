#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 6 — el funnel genomico como camino de FALSIFICACION.

No son cajas conectadas por flechas. Tres dimensiones simultaneas:
  1. cantidad -> el ancho del flujo, en escala logaritmica
  2. decision biologica -> los tres carriles, con destinos distintos
  3. evidencia que mato cada rama -> escrita al lado de cada muerte

Cada numero procede de docs/DECISIONS.md.
"""
import io, math

W, H = 1440, 1180
CX = 470                      # eje del flujo principal
FX0, FXW = 900, 500           # columna lateral de hipotesis muertas

# --- 1. el cuello: ancho ~ log(n) ---
STEPS = [
    (5012204, "variantes crudas", "VCF completo · GRCh38 · Sentieon"),
    (4943948, "anotadas a gen", "VEP 116 offline · 68 256 en contigs decoy sin genes"),
    (13581,   "HIGH + MODERATE", "928 HIGH · 12 653 MODERATE, contadas por variante"),
]
def wid(n): return 24 + 300 * (math.log10(n) - 3.5) / (math.log10(5012204) - 3.5)

neck, y = "", 120
for i, (n, lbl, sub) in enumerate(STEPS):
    w = wid(n)
    nxt = wid(STEPS[i + 1][0]) if i + 1 < len(STEPS) else wid(3000)
    neck += (f'<path d="M{CX-w/2:.1f},{y} L{CX+w/2:.1f},{y} L{CX+nxt/2:.1f},{y+86} '
             f'L{CX-nxt/2:.1f},{y+86} Z" fill="var(--flow)" opacity="{0.9-i*0.15:.2f}"/>'
             f'<text x="{CX}" y="{y+34}" class="big" text-anchor="middle">{n:,}</text>'
             f'<text x="{CX}" y="{y+52}" class="lbl" text-anchor="middle">{lbl}</text>'
             f'<text x="{CX+w/2+16:.1f}" y="{y+40}" class="mono">{sub}</text>')
    y += 86

# --- 2. los tres carriles, con destinos distintos ---
LY = y + 30
LANES = [
    (CX - 300, "MVA", "var(--alive)", "2 HIGH · 23 MODERATE", "SOBREVIVE", True),
    (CX,       "RENAL", "var(--dead)", "2 HIGH — ambas start_lost", "MUERE", False),
    (CX + 300, "GENOME-WIDE", "var(--open)", "928 HIGH en 533 genes", "ABIERTO", None),
]
lanes = ""
for lx, nm, col, det, fate, alive in LANES:
    lanes += (f'<line x1="{CX}" y1="{LY-30}" x2="{lx}" y2="{LY}" stroke="var(--rule)" stroke-width="1.5"/>'
              f'<rect x="{lx-118}" y="{LY}" width="236" height="62" rx="3" fill="var(--panel)" stroke="{col}" stroke-width="1.6"/>'
              f'<text x="{lx}" y="{LY+22}" class="lbl" text-anchor="middle" fill="{col}">{nm}</text>'
              f'<text x="{lx}" y="{LY+38}" class="mono" text-anchor="middle">{det}</text>'
              f'<text x="{lx}" y="{LY+54}" class="mono" text-anchor="middle" fill="{col}">{fate}</text>')
    if alive is True:
        lanes += (f'<path d="M{lx},{LY+62} L{lx},{LY+96} L{CX},{LY+96} L{CX},{LY+120}" '
                  f'fill="none" stroke="{col}" stroke-width="2.5"/>')
    elif alive is False:
        lanes += (f'<line x1="{lx}" y1="{LY+62}" x2="{lx}" y2="{LY+86}" stroke="{col}" stroke-width="1.5" stroke-dasharray="3 3"/>'
                  f'<text x="{lx}" y="{LY+100}" class="mono" fill="{col}" text-anchor="middle">alelos comunes de población</text>'
                  f'<text x="{lx}" y="{LY+114}" class="mono" fill="{col}" text-anchor="middle">AF 0,08 – 0,81 → DEGRADADO</text>')
    else:
        lanes += (f'<line x1="{lx}" y1="{LY+62}" x2="{lx}" y2="{LY+86}" stroke="{col}" stroke-width="1.5" stroke-dasharray="2 4" opacity=".7"/>'
                  f'<text x="{lx}" y="{LY+100}" class="mono" fill="{col}" text-anchor="middle" opacity=".9">ABIERTO — protección contra</text>'
                  f'<text x="{lx}" y="{LY+114}" class="mono" fill="{col}" text-anchor="middle" opacity=".9">sesgo de confirmación por panel</text>')

# --- 3. BUB1B: los dos alelos, tratados distinto ---
BY = LY + 176
AL, AR = CX - 190, CX + 190
def chain(x, items, col):
    out, yy = "", BY + 74
    for txt, mono in items:
        out += (f'<text x="{x}" y="{yy}" class="lbl" text-anchor="middle" fill="{col}">{txt}</text>'
                f'<text x="{x}" y="{yy+14}" class="mono" text-anchor="middle">{mono}</text>'
                f'<line x1="{x}" y1="{yy+20}" x2="{x}" y2="{yy+34}" stroke="var(--rule)" stroke-width="1.2"/>')
        yy += 54
    return out, yy

bub = (f'<rect x="{CX-100}" y="{BY}" width="200" height="46" rx="3" fill="var(--panel)" stroke="var(--ink)" stroke-width="2"/>'
       f'<text x="{CX}" y="{BY+30}" class="big" text-anchor="middle">BUB1B</text>'
       f'<line x1="{CX}" y1="{BY+46}" x2="{CX}" y2="{BY+58}" stroke="var(--ink)" stroke-width="1.5"/>'
       f'<line x1="{AL}" y1="{BY+58}" x2="{AR}" y2="{BY+58}" stroke="var(--ink)" stroke-width="1.5"/>'
       f'<line x1="{AL}" y1="{BY+58}" x2="{AL}" y2="{BY+72}" stroke="var(--alive)" stroke-width="2"/>'
       f'<line x1="{AR}" y1="{BY+58}" x2="{AR}" y2="{BY+72}" stroke="var(--vus)" stroke-width="2"/>')

left, ly = chain(AL, [("TRUNCANTE", "stop gained · PASS · het"),
                      ("PVS1", "PTC a 748 nt de la última unión"),
                      ("ClinVar", "pathogenic / likely pathogenic")], "var(--alive)")
right, ry = chain(AR, [("MISSENSE", "rara · PASS · het"),
                       ("ausente de gnomAD", "SIFT y PolyPhen preocupantes"),
                       ("REVEL 0,472", "PP3 NO SE CUMPLE"),
                       ("panorama ClinVar", "PM1 · PS1 · PM5 NO SE CUMPLEN")], "var(--vus)")
verdicts = (f'<rect x="{AL-86}" y="{ly-8}" width="172" height="34" rx="3" fill="var(--alive)" opacity=".16"/>'
            f'<text x="{AL}" y="{ly+14}" class="lbl" text-anchor="middle" fill="var(--alive)">LIKELY PATHOGENIC</text>'
            f'<rect x="{AR-56}" y="{ry-8}" width="112" height="34" rx="3" fill="var(--vus)" opacity=".16"/>'
            f'<text x="{AR}" y="{ry+14}" class="lbl" text-anchor="middle" fill="var(--vus)">VUS</text>')

# --- 4. la compuerta ---
GY = max(ly, ry) + 56
gate = (f'<path d="M{AL},{ly+26} L{AL},{GY} L{AR},{GY} L{AR},{ry+26}" fill="none" stroke="var(--rule)" stroke-width="1.5"/>'
        f'<rect x="{CX-250}" y="{GY}" width="500" height="62" rx="3" fill="var(--panel)" stroke="var(--gate)" stroke-width="2.5"/>'
        f'<text x="{CX}" y="{GY+26}" class="lbl" text-anchor="middle" fill="var(--gate)" font-size="15">BIALLELIC MODEL NOT ESTABLISHED</text>'
        f'<text x="{CX}" y="{GY+46}" class="mono" text-anchor="middle" fill="var(--gate)">PHASE UNRESOLVED · hueco más corto 13,8× la longitud de fragmento</text>')

# --- 5. la busqueda del segundo alelo ---
SY = GY + 136
SEARCH = [("BUB1B ± locus regulador", "gen ±100 kb · 270 kb"),
          ("321 variantes", "313 PASS · 8 en nivel de rescate"),
          ("4 raras", "&lt; 1e-3 · dos ya conocidas · una en PAK6"),
          ("1 candidato nuevo", "intrónico profundo · ausente de gnomAD"),
          ("AlphaGenome", "REF ≈ ALT · sin Δ coherente")]
search, sy = "", SY
for i, (a, b) in enumerate(SEARCH):
    search += (f'<text x="{CX}" y="{sy}" class="lbl" text-anchor="middle">{a}</text>'
               f'<text x="{CX}" y="{sy+14}" class="mono" text-anchor="middle">{b}</text>')
    if i < len(SEARCH) - 1:
        search += f'<line x1="{CX}" y1="{sy+20}" x2="{CX}" y2="{sy+32}" stroke="var(--rule)" stroke-width="1.2"/>'
    sy += 52
search += (f'<text x="{CX}" y="{sy-14}" class="big" text-anchor="middle" fill="var(--dead)">✕</text>')

# --- 6. el cuello de botella de datos, no un fracaso ---
NY = sy + 14
bottleneck = (f'<line x1="{CX}" y1="{NY-40}" x2="{CX}" y2="{NY}" stroke="var(--open)" stroke-width="2"/>'
              f'<rect x="{CX-250}" y="{NY}" width="500" height="72" rx="3" fill="var(--open)" opacity=".12"/>'
              f'<rect x="{CX-250}" y="{NY}" width="500" height="72" rx="3" fill="none" stroke="var(--open)" stroke-width="2"/>'
              f'<text x="{CX}" y="{NY+24}" class="lbl" text-anchor="middle" fill="var(--open)" font-size="15">BÚSQUEDA DE ALELO ESTRUCTURAL · SV / CNV</text>'
              f'<text x="{CX}" y="{NY+44}" class="lbl" text-anchor="middle" fill="var(--open)">NEXT DATA BOTTLENECK</text>'
              f'<text x="{CX}" y="{NY+62}" class="mono" text-anchor="middle">requiere BAM/CRAM de profundidad completa · solo L001 en disco (~13×)</text>')

# --- 7. columna lateral: hipotesis eliminadas ---
KILLED = [("✕", "Candidatas HIGH renales", "frecuencia poblacional 0,08 – 0,81", "var(--dead)"),
          ("✕", "Missense como segundo alelo establecido", "evidencia ACMG insuficiente", "var(--dead)"),
          ("✕", "Candidato regulador SNV/indel", "AlphaGenome REF ≈ ALT", "var(--dead)"),
          ("✕", "Deleción grande que abarque BUB1B", "sin señal de profundidad ni pérdida de heterocigosidad", "var(--dead)"),
          ("?", "SV pequeña o equilibrada", "sin resolver sin alineamientos de profundidad completa", "var(--open)")]
killed, ky = "", 300
killed += (f'<text x="{FX0}" y="{ky-24}" class="sect">Hipótesis eliminadas · y por qué</text>'
           f'<line x1="{FX0}" y1="{ky-14}" x2="{FX0+FXW}" y2="{ky-14}" stroke="var(--rule)"/>')
for mark, h, why, col in KILLED:
    killed += (f'<text x="{FX0}" y="{ky+12}" class="big" fill="{col}">{mark}</text>'
               f'<text x="{FX0+30}" y="{ky+8}" class="lbl">{h}</text>'
               f'<text x="{FX0+30}" y="{ky+24}" class="mono" fill="{col}">{why}</text>'
               f'<line x1="{FX0}" y1="{ky+38}" x2="{FX0+FXW}" y2="{ky+38}" stroke="var(--rule)" stroke-width=".7"/>')
    ky += 58
killed += (f'<text x="{FX0}" y="{ky+16}" class="mono" opacity=".85">El último lleva interrogante, no aspa:</text>'
           f'<text x="{FX0}" y="{ky+32}" class="mono" opacity=".85">no está descartado, está sin resolver.</text>')

TOTAL_H = NY + 130

HTML = f"""<title>The Genomic Funnel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --flow:#8C99A4;--alive:#2E7D6B;--dead:#B4453A;--open:#C07A2E;--vus:#7A8590;--gate:#B4453A;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--flow:#4A555F;--alive:#63BFA6;--dead:#E0776A;
 --open:#E0A458;--vus:#8B96A0;--gate:#E0776A;}}}}
:root[data-theme="dark"]{{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--flow:#4A555F;--alive:#63BFA6;--dead:#E0776A;--open:#E0A458;--vus:#8B96A0;--gate:#E0776A;}}
body{{background:var(--ground);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;
 margin:0;padding:clamp(20px,4vw,52px) clamp(16px,4vw,52px) 60px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:24px}}
.eyebrow{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--ink-soft);margin:0}}
h1{{font-size:clamp(25px,3.8vw,38px);font-weight:700;letter-spacing:-.022em;line-height:1.1;margin:10px 0 0}}
.sub{{margin:12px 0 0;font-size:clamp(15px,1.7vw,19px);line-height:1.45;color:var(--ink);
 border-left:2px solid var(--open);padding-left:16px;max-width:56ch}}
.figframe{{background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:8px;overflow-x:auto}}
svg{{display:block;width:100%;height:auto;min-width:1040px}}
.cap{{display:grid;gap:8px;font-size:13px;line-height:1.55;color:var(--ink-soft);max-width:80ch}}
.cap strong{{color:var(--ink);font-weight:600}}
.foot{{display:flex;flex-wrap:wrap;gap:10px 26px;border-top:1px solid var(--rule);padding-top:16px;
 font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft)}}
</style>
<div class="wrap">
<header>
 <p class="eyebrow">Mosaic Rescue · Figura 6</p>
 <h1>The genomic funnel</h1>
 <p class="sub">Cinco millones de variantes. Un mecanismo sobrevive — pero sigue faltando
 un alelo.</p>
</header>

<div class="figframe">
<svg viewBox="0 0 {W} {TOTAL_H}" role="img" aria-label="Camino de filtrado y falsificación desde cinco millones de variantes hasta el cuello de botella actual.">
<style>
 .big{{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:19px;fill:var(--ink)}}
 .lbl{{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:12.5px;fill:var(--ink)}}
 .mono{{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.04em;fill:var(--ink-soft)}}
 .sect{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
        text-transform:uppercase;fill:var(--ink-soft);font-weight:500}}
</style>

<text x="40" y="52" class="sect">01 · Cantidad</text>
<text x="40" y="70" class="mono">ancho ∝ log(n) — a escala lineal el final sería invisible</text>
{neck}

<text x="40" y="{LY-30}" class="sect">02 · Decisión biológica</text>
{lanes}

<text x="40" y="{BY-14}" class="sect">03 · Investigación causal</text>
{bub}
{left}
{right}
{verdicts}
{gate}

<text x="40" y="{SY-54}" class="sect">04 · El alelo que falta</text>
{search}
{bottleneck}

{killed}
</svg>
</div>

<div class="cap">
<p><strong>Los dos alelos recibieron trato distinto según la evidencia, no según nos
convenía.</strong> El truncante acumuló <code>PVS1</code> y una clasificación de ClinVar; el
missense fue perdiendo apoyo en cada paso — <code>REVEL 0,472</code> mató <code>PP3</code>,
y el panorama de ClinVar mató <code>PM1</code>, <code>PS1</code> y <code>PM5</code>.</p>

<p><strong>El carril genome-wide se dibuja abierto a propósito.</strong> Es la protección
contra el sesgo de confirmación por panel: si el gen causal fuera uno que no está en
ninguna de nuestras listas, ese carril es el único que podría encontrarlo.</p>

<p><strong>El último cuadro no es un fracaso.</strong> Es saber qué dato resuelve la
pregunta. Se dejó de calcular cuando calcular más habría sido inventar: con un solo carril
(~13×) no se puede cerrar un negativo de variante estructural.</p>

<p><strong>La última hipótesis lleva interrogante, no aspa.</strong> Una SV pequeña o
equilibrada no está descartada — está sin resolver. Marcarla como muerta sería exactamente
la clase de sobreafirmación que este funnel documenta haber evitado cinco veces.</p>
</div>

<div class="foot">
 <span>5 012 204 → 1 MECANISMO</span>
 <span>4 HIPÓTESIS ELIMINADAS · 1 SIN RESOLVER</span>
 <span>FASE NO RESUELTA</span>
 <span>SIGUIENTE: BAM/CRAM PROFUNDIDAD COMPLETA</span>
</div>
</div>
"""
io.open("figures/fig6_funnel.html", "w", encoding="utf-8", newline="\n").write(HTML)
print(f"  figures/fig6_funnel.html ({len(HTML)/1024:.0f} KB · alto {TOTAL_H})")
