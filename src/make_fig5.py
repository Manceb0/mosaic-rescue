#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 5 — AlphaGenome REF / ALT / Delta sobre el candidato no codificante.

Reglas congeladas antes de la llamada (docs/DECISIONS.md):
  - REF y ALT comparten EXACTAMENTE la misma escala Y dentro de cada pista.
  - Delta en carril propio con el cero visible.
  - Eje genomico real.
  - Seleccion de pistas fijada de antemano.

Un negativo dibujado, no narrado.
"""
import io, json

D = json.load(io.open("work/alphagenome/arrays_40216470.json", encoding="utf-8"))
TR, POS, FL = D["tracks"], D["pos"], D["flank_bp"]

X0, XW = 210, 1010
ROW_H, DELTA_H, GAP = 44, 22, 26
TOP = 150

NAMES = {"splice_sites": "Sitios de splicing", "splice_site_usage": "Uso de sitio",
         "splice_junctions": "Junciones", "chip_tf": "ChIP-seq TF",
         "rna_seq": "RNA-seq", "atac": "ATAC-seq", "dnase": "DNase-seq"}
GROUP = {"splice_sites": "SPLICING", "splice_site_usage": "SPLICING", "splice_junctions": "SPLICING",
         "chip_tf": "INSULADOR", "rna_seq": "EXPRESIÓN", "atac": "CROMATINA", "dnase": "CROMATINA"}

NPTS = 900   # ~1 punto por pixel util; mas es peso muerto

def downsample(vals, n=NPTS):
    """Reduce preservando EXTREMOS, no promediando: un pico no puede desaparecer."""
    if len(vals) <= n:
        return vals
    step = len(vals) / n
    out = []
    for i in range(n):
        a, b = int(i * step), max(int(i * step) + 1, int((i + 1) * step))
        seg = vals[a:b]
        out.append(max(seg, key=abs) if seg else 0.0)
    return out


def path(vals, x0, w, y0, h, vmax):
    n = len(vals)
    if n < 2 or vmax <= 0:
        return ""
    pts = [f"{x0 + i / (n - 1) * w:.1f},{y0 + h - (v / vmax) * h:.1f}" for i, v in enumerate(vals)]
    return " ".join(pts)

rows, y = "", TOP
prev_group = None
for t in TR:
    ref, alt = t["ref"], t["alt"]
    md_full = max(abs(a - r) for a, r in zip(alt, ref))
    base_full = max(abs(v) for v in ref) or 1.0
    ref, alt = downsample(ref), downsample(alt)
    md, base = md_full, base_full   # metricas del array COMPLETO, no del submuestreo
    rel = 100 * md / base
    grp = GROUP[t["mod"]]
    if grp != prev_group:
        rows += (f'<text x="{X0-14}" y="{y-8}" class="grp" text-anchor="end">{grp}</text>'
                 f'<line x1="{X0}" y1="{y-14}" x2="{X0+XW}" y2="{y-14}" stroke="var(--rule)" stroke-width=".8"/>')
        prev_group = grp

    # --- REF y ALT, MISMA escala Y ---
    vmax = base
    rows += (f'<rect x="{X0}" y="{y}" width="{XW}" height="{ROW_H}" fill="var(--lane)"/>'
             f'<polyline points="{path(ref, X0, XW, y, ROW_H, vmax)}" fill="none" '
             f'stroke="var(--ref)" stroke-width="2.2" opacity=".95"/>'
             f'<polyline points="{path(alt, X0, XW, y, ROW_H, vmax)}" fill="none" '
             f'stroke="var(--alt)" stroke-width="1.1" stroke-dasharray="3 2.5"/>')
    rows += (f'<text x="{X0-14}" y="{y+16}" class="lbl" text-anchor="end">{NAMES[t["mod"]]}</text>'
             f'<text x="{X0-14}" y="{y+30}" class="mono" text-anchor="end">{t["meta"][:38]}</text>'
             f'<text x="{X0-14}" y="{y+42}" class="mono" text-anchor="end" opacity=".7">escala Y 0–{vmax:.3g}</text>')

    # --- Delta, carril propio con el cero visible ---
    dy = y + ROW_H + 4
    delta = [a - r for a, r in zip(alt, ref)]
    dmax = max(abs(v) for v in delta) or 1e-9
    scale = max(dmax, base * 0.05)          # el cero y la escala de REF son comparables
    mid = dy + DELTA_H / 2
    dpts = " ".join(f"{X0 + i/(len(delta)-1)*XW:.1f},{mid - (v/scale)*(DELTA_H/2):.1f}"
                    for i, v in enumerate(delta)) if len(delta) > 1 else ""
    rows += (f'<rect x="{X0}" y="{dy}" width="{XW}" height="{DELTA_H}" fill="var(--lane-d)"/>'
             f'<line x1="{X0}" y1="{mid:.1f}" x2="{X0+XW}" y2="{mid:.1f}" stroke="var(--ink-soft)" stroke-width=".8"/>'
             f'<polyline points="{dpts}" fill="none" stroke="var(--delta)" stroke-width="1.5"/>'
             f'<text x="{X0-14}" y="{mid+4:.1f}" class="mono" text-anchor="end" fill="var(--delta)">Δ</text>'
             f'<text x="{X0+4}" y="{dy+8:.1f}" class="mono" opacity=".75">+{scale:.3g}</text>'
             f'<text x="{X0+4}" y="{dy+DELTA_H-2:.1f}" class="mono" opacity=".75">−{scale:.3g}</text>'
             f'<text x="{X0+XW-4}" y="{mid-3:.1f}" class="mono" text-anchor="end" opacity=".6">0</text>')

    # --- datos crudos a la derecha ---
    rx = X0 + XW + 16
    if "CTCF" in t["meta"] and "kidney" in t["meta"].lower():
        rows += (f'<rect x="{rx-4}" y="{y-2}" width="196" height="{ROW_H+4}" rx="2" '
                 f'fill="var(--predicted)" opacity=".10"/>'
                 f'<text x="{rx}" y="{y+56}" class="mono" fill="var(--predicted)">contexto relevante</text>'
                 f'<text x="{rx}" y="{y+68}" class="mono" fill="var(--predicted)">para el fenotipo —</text>'
                 f'<text x="{rx}" y="{y+80}" class="mono" fill="var(--predicted)">el efecto sigue siendo pequeño</text>')
    rows += (f'<text x="{rx}" y="{y+14}" class="mono">máx |Δ| <tspan class="num">{md:.4g}</tspan></text>'
             f'<text x="{rx}" y="{y+28}" class="mono">base <tspan class="num">{base:.4g}</tspan></text>'
             f'<text x="{rx}" y="{y+42}" class="mono">Δ rel <tspan class="num" '
             f'fill="{"var(--warn)" if rel>10 else "var(--ok)"}">{rel:.2f} %</tspan></text>')
    y += ROW_H + DELTA_H + GAP

# --- eje genomico con coordenadas reales y barra de escala ---
vx = X0 + XW / 2
axis = f'<line x1="{X0}" y1="{y+2}" x2="{X0+XW}" y2="{y+2}" stroke="var(--ink-soft)" stroke-width="1"/>'
for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
    gx_ = X0 + frac * XW
    coord = POS - FL + frac * 2 * FL
    axis += (f'<line x1="{gx_:.1f}" y1="{y+2}" x2="{gx_:.1f}" y2="{y+8}" stroke="var(--ink-soft)" stroke-width="1"/>'
             f'<text x="{gx_:.1f}" y="{y+20}" class="mono" text-anchor="middle">{int(coord):,}</text>')
axis += (f'<text x="{X0}" y="{y+36}" class="mono" opacity=".8">chr15 · GRCh38</text>')
# barra de escala de 2 kb
sb = 2000 / (2 * FL) * XW
axis += (f'<line x1="{X0+XW-sb:.1f}" y1="{y+32}" x2="{X0+XW:.1f}" y2="{y+32}" stroke="var(--ink)" stroke-width="2.5"/>'
         f'<text x="{X0+XW-sb/2:.1f}" y="{y+28}" class="mono" text-anchor="middle" fill="var(--ink)">2 kb</text>')
H = y + 130

HTML = f"""<title>AlphaGenome REF ALT Delta</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --ref:#1F4E5F;--alt:#C07A2E;--delta:#B4453A;--lane:#F2F3F1;--lane-d:#F7F6F3;
 --predicted:#C07A2E;--ok:#2E7D6B;--warn:#B4453A;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--ref:#6FB3C6;--alt:#E0A458;--delta:#E0776A;
 --lane:#1B222A;--lane-d:#161C22;--predicted:#E0A458;--ok:#63BFA6;--warn:#E0776A;}}}}
:root[data-theme="dark"]{{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--ref:#6FB3C6;--alt:#E0A458;--delta:#E0776A;--lane:#1B222A;--lane-d:#161C22;
 --predicted:#E0A458;--ok:#63BFA6;--warn:#E0776A;}}
body{{background:var(--ground);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;
 margin:0;padding:clamp(20px,4vw,52px) clamp(16px,4vw,52px) 60px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:24px}}
.eyebrow{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--ink-soft);margin:0}}
h1{{font-size:clamp(25px,3.8vw,38px);font-weight:700;letter-spacing:-.022em;line-height:1.1;margin:10px 0 0}}
.sub{{margin:12px 0 0;font-size:clamp(14px,1.6vw,17px);line-height:1.45;color:var(--ink-soft);
 border-left:2px solid var(--predicted);padding-left:16px;max-width:62ch}}
.figframe{{background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:8px;overflow-x:auto}}
svg{{display:block;width:100%;height:auto;min-width:1000px}}
.cap{{display:grid;gap:8px;font-size:13px;line-height:1.55;color:var(--ink-soft);max-width:80ch}}
.cap strong{{color:var(--ink);font-weight:600}}
.foot{{display:flex;flex-wrap:wrap;gap:10px 26px;border-top:1px solid var(--rule);padding-top:16px;
 font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft)}}
</style>
<div class="wrap">
<header>
 <p class="eyebrow">Mosaic Rescue · Figura 5</p>
 <h1>No coherent molecular effect predicted across the preregistered tracks</h1>
 <p class="sub">Selección de pistas y reglas de escala <strong>congeladas antes</strong> de
 la llamada. REF y ALT comparten escala Y dentro de cada pista; el Δ va en carril propio con
 el cero visible.</p>
</header>

<div class="figframe">
<svg viewBox="0 0 1440 {H}" role="img" aria-label="Predicciones REF, ALT y delta de AlphaGenome para el candidato no codificante.">
<style>
 .lbl{{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:12.5px;fill:var(--ink)}}
 .mono{{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.04em;fill:var(--ink-soft)}}
 .num{{font-family:"IBM Plex Mono",monospace;font-size:9.5px;fill:var(--ink);font-weight:600}}
 .grp{{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.18em;fill:var(--ink-soft);font-weight:600}}
 .sect{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
        text-transform:uppercase;fill:var(--ink-soft);font-weight:500}}
</style>

<text x="{X0-14}" y="36" class="sect" text-anchor="end">PREDICTED</text>
<text x="{X0}" y="36" class="lbl" fill="var(--predicted)" font-size="17">AlphaGenome — predicción, no medición</text>
<text x="{X0}" y="56" class="mono">chr15:{POS-FL:,}–{POS+FL:,}  ·  ventana de contexto 1 Mb  ·  candidato intrónico profundo en el centro</text>
<line x1="{X0}" y1="70" x2="{X0+XW}" y2="70" stroke="var(--rule)"/>

<line x1="{vx:.1f}" y1="78" x2="{vx:.1f}" y2="{y-10}" stroke="var(--predicted)" stroke-width="1.6" stroke-dasharray="5 4" opacity=".65"/>
<circle cx="{vx:.1f}" cy="86" r="5" fill="var(--predicted)"/>
<text x="{vx:.1f}" y="106" class="lbl" fill="var(--predicted)" text-anchor="middle">variante candidata</text>
{axis}

<g transform="translate({X0+XW+16},96)">
  <line x1="0" y1="-4" x2="26" y2="-4" stroke="var(--ref)" stroke-width="2.2"/>
  <text x="34" y="0" class="mono">REF</text>
  <line x1="0" y1="12" x2="26" y2="12" stroke="var(--alt)" stroke-width="1.1" stroke-dasharray="3 2.5"/>
  <text x="34" y="16" class="mono">ALT</text>
</g>

{rows}

<line x1="{X0}" y1="{y+30}" x2="{X0+XW+180}" y2="{y+30}" stroke="var(--rule)"/>
<text x="{X0}" y="{y+58}" class="lbl" font-size="15">Ningún Δ relativo supera el 3,2 %. Las tres modalidades de splicing quedan por debajo del 0,7 %.</text>
<text x="{X0}" y="{y+80}" class="mono">The only rare noncoding candidate surviving locus-level filtering was not supported by global or track-level AlphaGenome predictions.</text>
<text x="{X0}" y="{y+100}" class="mono" opacity=".8">Selección de pistas y umbral de línea base (0,01) preregistrados en docs/DECISIONS.md antes de esta llamada.</text>
</svg>
</div>

<div class="cap">
<p><strong>Por qué REF y ALT se dibujan superpuestos y a la misma escala.</strong> Tres
gráficos con escalas independientes harían parecer grande un cambio minúsculo. Aquí la
línea discontinua (ALT) cae encima de la continua (REF) en las nueve pistas: <em>eso</em>
es el resultado.</p>

<p><strong>El carril Δ lleva su escala escrita</strong> y está anclada al 5 % de la línea
base de la pista, no autoajustada al propio Δ. Un eje autoescalado convertiría ruido
numérico en una montaña — por eso los límites van impresos en cada carril.</p>

<p><strong>Las líneas base importan.</strong> La primera pasada dio deltas relativos del
5 % que resultaron ser división por líneas base de ~0,0001. Por eso el preregistro exigió
un mínimo de 0,01: aquí las bases van de 0,94 a 7 872, y los cambios relativos caen entre
el 0,34 % y el 3,2 %.</p>

<p><strong>La pista que más podría tentarnos tampoco sobrevive.</strong> CTCF en célula
epitelial renal es <em>contexto relevante para el fenotipo</em> — y precisamente por eso se
marca en la figura. Su Δ relativo es del <strong>1,22 %</strong>: no sobrevive
cuantitativamente. Que el sesgo se resista incluso donde la biología invita es parte del
resultado.</p>
</div>

<div class="foot">
 <span>ALPHAGENOME · PREDICTED · NO ES MEDICIÓN</span>
 <span>9 PISTAS PRESELECCIONADAS</span>
 <span>MÁX Δ REL 3,2 %</span>
 <span>RAMA SNV/INDEL CERRADA</span>
</div>
</div>
"""
io.open("figures/fig5_alphagenome.html", "w", encoding="utf-8", newline="\n").write(HTML)
print(f"  figures/fig5_alphagenome.html ({len(HTML)/1024:.0f} KB · {len(TR)} pistas)")
