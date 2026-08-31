#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 3 — por que el alelo truncante es fuerte y por que no podemos unirlo al segundo.

Panel A: transcrito maduro a escala de CDS. La regla de los 50-55 nt se mide en
espacio de mRNA, no genomico, asi que se dibuja el mRNA.
Panel B: los 10,9 kb genomicos a escala, con fragmentos de libreria de ~300 pb
dibujados al mismo tamano real.

Todo procede de medicion: limites de exon sondeados a 2 pb sobre el mismo release
de VEP, y posiciones y huecos leidos del VCF.
"""
import io, json

E = json.load(io.open("work/struct/fig3_exons.json", encoding="utf-8"))
EX, PTC, MIS, LJ = E["exons"], E["ptc_cds"], E["mis_cds"], E["last_junction"]
CDS0, CDS1 = EX[0]["c0"], EX[-1]["c1"]

# ---------- Panel A: mRNA maduro en coordenadas CDS ----------
AX0, AY0, AW, AH = 96, 130, 1240, 46
def cx(c): return AX0 + (c - CDS0) / (CDS1 - CDS0) * AW

exons_svg = ""
for e in EX:
    x0, x1 = cx(e["c0"]), cx(e["c1"])
    last = e["n"] == EX[-1]["n"]
    exons_svg += (f'<rect x="{x0:.1f}" y="{AY0}" width="{max(x1-x0,2):.1f}" height="{AH}" '
                  f'fill="{"var(--exon-last)" if last else "var(--exon)"}" '
                  f'stroke="var(--rule)" stroke-width="1"/>'
                  f'<text x="{(x0+x1)/2:.1f}" y="{AY0+AH+15}" class="mono" text-anchor="middle">Ex{e["n"]}</text>'
                  f'<text x="{(x0+x1)/2:.1f}" y="{AY0+AH+28}" class="mono" text-anchor="middle" '
                  f'opacity=".6">{e["c1"]-e["c0"]+1}</text>')
    if not last:
        exons_svg += (f'<line x1="{x1:.1f}" y1="{AY0-6}" x2="{x1:.1f}" y2="{AY0+AH+6}" '
                      f'stroke="var(--ink-soft)" stroke-width="1" stroke-dasharray="2 2" opacity=".5"/>')

# zona NMD-escape: los ultimos 55 nt antes de la ultima union
nmd_x0, nmd_x1 = cx(LJ - 55), cx(LJ)
span_y = AY0 + AH + 76

HTML_A = f"""
<text x="{AX0}" y="34" class="sect">A · Transcrito maduro MANE · escala de CDS · exones sondeados a 2 pb</text>
<text x="1336" y="34" class="mono" text-anchor="end">MEASURED</text>
<line x1="{AX0}" y1="46" x2="1336" y2="46" stroke="var(--rule)"/>
<text x="{AX0}" y="72" class="lbl-sm">La regla de los 50–55 nt se mide en el mRNA maduro, no en coordenadas genómicas. Por eso se dibuja el transcrito, no el gen.</text>

{exons_svg}

<!-- zona de escape a NMD -->
<rect x="{nmd_x0:.1f}" y="{AY0-14}" width="{nmd_x1-nmd_x0:.1f}" height="{AH+28}"
      fill="var(--warn)" opacity=".16"/>
<line x1="{nmd_x0:.1f}" y1="{AY0-14}" x2="{nmd_x0:.1f}" y2="{AY0+AH+14}" stroke="var(--warn)" stroke-width="1.5" stroke-dasharray="3 3"/>
<text x="{nmd_x0-6:.1f}" y="{AY0-20}" class="mono" fill="var(--warn)" text-anchor="end">55 nt · frontera de escape a NMD</text>

<!-- ultima union exon-exon -->
<line x1="{cx(LJ):.1f}" y1="{AY0-32}" x2="{cx(LJ):.1f}" y2="{AY0+AH+8}" stroke="var(--ink)" stroke-width="2"/>
<text x="{cx(LJ)+8:.1f}" y="{AY0-36}" class="lbl">última unión exón–exón</text>
<text x="{cx(LJ)+8:.1f}" y="{AY0-22}" class="mono">CDS {LJ}</text>

<!-- PTC -->
<line x1="{cx(PTC):.1f}" y1="{AY0-32}" x2="{cx(PTC):.1f}" y2="{AY0+AH+8}" stroke="var(--target)" stroke-width="2.5"/>
<circle cx="{cx(PTC):.1f}" cy="{AY0+AH/2}" r="6" fill="var(--target)"/>
<text x="{cx(PTC):.1f}" y="{AY0-36}" class="lbl" fill="var(--target)" text-anchor="middle">PTC</text>
<text x="{cx(PTC):.1f}" y="{AY0-22}" class="mono" fill="var(--target)" text-anchor="middle">CDS {PTC} · exón 17</text>

<!-- missense -->
<line x1="{cx(MIS):.1f}" y1="{AY0}" x2="{cx(MIS):.1f}" y2="{AY0+AH}" stroke="var(--measured)" stroke-width="2"/>
<circle cx="{cx(MIS):.1f}" cy="{AY0+AH/2}" r="5" fill="var(--measured)"/>
<text x="{cx(MIS):.1f}" y="{AY0+AH+46}" class="mono" fill="var(--measured)" text-anchor="middle">missense · CDS {MIS}</text>

<!-- medida de los 748 nt -->
<line x1="{cx(PTC):.1f}" y1="{span_y}" x2="{cx(LJ):.1f}" y2="{span_y}" stroke="var(--target)" stroke-width="1.5"/>
<line x1="{cx(PTC):.1f}" y1="{span_y-6}" x2="{cx(PTC):.1f}" y2="{span_y+6}" stroke="var(--target)" stroke-width="1.5"/>
<line x1="{cx(LJ):.1f}" y1="{span_y-6}" x2="{cx(LJ):.1f}" y2="{span_y+6}" stroke="var(--target)" stroke-width="1.5"/>
<rect x="{(cx(PTC)+cx(LJ))/2-46:.1f}" y="{span_y-12}" width="92" height="19" rx="2" fill="var(--panel)"/>
<text x="{(cx(PTC)+cx(LJ))/2:.1f}" y="{span_y+2}" class="lbl" fill="var(--target)" text-anchor="middle">{LJ-PTC} nt</text>

<text x="{AX0}" y="{span_y+40}" class="lbl">El PTC está {LJ-PTC} nt por encima de la última unión, frente a un umbral de 55.</text>
<text x="{AX0}" y="{span_y+58}" class="lbl-sm">Margen de {(LJ-PTC)/55:.1f}× → NMD predicho con holgura → <tspan class="lbl" fill="var(--target)">PVS1 con la ruta del árbol favorable</tspan></text>
"""

# ---------- Panel B: los 10,9 kb genomicos a escala ----------
GA, GH, GB = [REDACTED], [REDACTED], [REDACTED]
BX0, BY0, BW = 96, 470, 1240
def gx(p): return BX0 + (p - GA) / (GB - GA) * BW
FRAG = 300
frag_px = FRAG / (GB - GA) * BW

# fragmentos DISCRETOS y separados: cada uno se lee como una unidad
frags = ""
for k in range(9):
    x = BX0 + 30 + k * (BW - 80) / 9
    frags += (f'<rect x="{x:.1f}" y="{BY0+152}" width="{max(frag_px,1.2):.2f}" height="10" rx="1.5" '
              f'fill="var(--frag)" opacity=".9"/>')
# comparacion directa: un fragmento contra el hueco mas corto
CMPX, CMPY = BX0 + 16, BY0 + 200
gap_px = (GB - GH) / (GB - GA) * (BW - 300)
cmp_svg = (
  f'<text x="{CMPX}" y="{CMPY}" class="mono">1 FRAGMENTO</text>'
  f'<rect x="{CMPX+120}" y="{CMPY-10}" width="{max(frag_px,1.2):.1f}" height="12" rx="1.5" fill="var(--frag)"/>'
  f'<text x="{CMPX+120+max(frag_px,1.2)+8:.1f}" y="{CMPY}" class="mono" fill="var(--frag)">{FRAG} pb</text>'
  f'<text x="{CMPX}" y="{CMPY+26}" class="mono" fill="var(--warn)">HUECO MÁS CORTO</text>'
  f'<rect x="{CMPX+120}" y="{CMPY+16}" width="{gap_px:.1f}" height="12" rx="1.5" fill="var(--warn)" opacity=".8"/>'
  f'<text x="{CMPX+120+gap_px+8:.1f}" y="{CMPY+26}" class="mono" fill="var(--warn)">{GB-GH:,} pb</text>')

def dim(p0, p1, y, lbl, col):
    a, b = gx(p0), gx(p1)
    return (f'<line x1="{a:.1f}" y1="{y}" x2="{b:.1f}" y2="{y}" stroke="{col}" stroke-width="1.5"/>'
            f'<line x1="{a:.1f}" y1="{y-6}" x2="{a:.1f}" y2="{y+6}" stroke="{col}" stroke-width="1.5"/>'
            f'<line x1="{b:.1f}" y1="{y-6}" x2="{b:.1f}" y2="{y+6}" stroke="{col}" stroke-width="1.5"/>'
            f'<rect x="{(a+b)/2-52:.1f}" y="{y-12}" width="104" height="19" rx="2" fill="var(--panel)"/>'
            f'<text x="{(a+b)/2:.1f}" y="{y+2}" class="lbl" fill="{col}" text-anchor="middle">{lbl}</text>')

HTML_B = f"""
<text x="{BX0}" y="{BY0-36}" class="sect">B · Los 10 911 pb entre los dos candidatos · escala genómica real</text>
<text x="1336" y="{BY0-36}" class="mono" text-anchor="end">MEASURED</text>
<line x1="{BX0}" y1="{BY0-24}" x2="1336" y2="{BY0-24}" stroke="var(--rule)"/>

<line x1="{BX0}" y1="{BY0+40}" x2="{BX0+BW}" y2="{BY0+40}" stroke="var(--ink-soft)" stroke-width="2"/>
<circle cx="{gx(GA):.1f}" cy="{BY0+40}" r="9" fill="var(--target)"/>
<circle cx="{gx(GH):.1f}" cy="{BY0+40}" r="6" fill="var(--ink-soft)"/>
<circle cx="{gx(GB):.1f}" cy="{BY0+40}" r="9" fill="var(--measured)"/>

<text x="{gx(GA):.1f}" y="{BY0+18}" class="lbl" fill="var(--target)" text-anchor="start">Candidato A · truncante</text>
<text x="{gx(GA):.1f}" y="{BY0+4}" class="mono" fill="var(--target)">Likely Pathogenic</text>
<text x="{gx(GH):.1f}" y="{BY0+18}" class="lbl-sm" text-anchor="middle">único heterocigoto informativo</text>
<text x="{gx(GB):.1f}" y="{BY0+18}" class="lbl" fill="var(--measured)" text-anchor="end">Candidato B · missense</text>
<text x="{gx(GB):.1f}" y="{BY0+4}" class="mono" fill="var(--measured)" text-anchor="end">VUS</text>

{dim(GA,GH,BY0+84,f"{GH-GA:,} pb","var(--ink-soft)")}
{dim(GH,GB,BY0+84,f"{GB-GH:,} pb","var(--warn)")}

<text x="{BX0}" y="{BY0+142}" class="lbl-sm">Fragmentos de librería (~{FRAG} pb) a la misma escala — obsérvese lo poco que abarca cada uno:</text>
{frags}

<rect x="{BX0}" y="{BY0+178}" width="{BW}" height="106" rx="3" fill="var(--warn)" opacity=".09"/>
{cmp_svg}
<text x="{CMPX}" y="{CMPY+58}" class="lbl" fill="var(--warn)">{(GB-GH)/FRAG:.1f}× más largo que cualquier fragmento</text>
<text x="{CMPX}" y="{CMPY+78}" class="lbl-sm">Ni el <tspan class="mono">PID</tspan> del caller (máx. 288 pb medidos en todo el genoma) ni un refaseado con WhatsHap o HapCUT2 pueden conectar estos dos puntos.</text>
"""

HTML = f"""<title>Two Alleles, No Phase</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --exon:#8C99A4;--exon-last:#5A6B78;--target:#C07A2E;--measured:#1F4E5F;--warn:#B4453A;--frag:#2E7D6B;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--exon:#6B7883;--exon-last:#8B98A4;
 --target:#E0A458;--measured:#6FB3C6;--warn:#E0776A;--frag:#63BFA6;}}}}
:root[data-theme="dark"]{{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--exon:#6B7883;--exon-last:#8B98A4;--target:#E0A458;--measured:#6FB3C6;
 --warn:#E0776A;--frag:#63BFA6;}}
body{{background:var(--ground);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;
 margin:0;padding:clamp(20px,4vw,52px) clamp(16px,4vw,52px) 60px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:24px}}
.eyebrow{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--ink-soft);margin:0}}
h1{{font-size:clamp(25px,3.8vw,38px);font-weight:700;letter-spacing:-.022em;line-height:1.1;margin:10px 0 0}}
.sub{{margin:12px 0 0;font-size:clamp(14px,1.6vw,17px);line-height:1.45;color:var(--ink-soft);
 border-left:2px solid var(--target);padding-left:16px;max-width:62ch}}
.figframe{{background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:8px;overflow-x:auto}}
svg{{display:block;width:100%;height:auto;min-width:1000px}}
.cap{{display:grid;gap:8px;font-size:13px;line-height:1.55;color:var(--ink-soft);max-width:80ch}}
.cap strong{{color:var(--ink);font-weight:600}}
.foot{{display:flex;flex-wrap:wrap;gap:10px 26px;border-top:1px solid var(--rule);padding-top:16px;
 font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft)}}
</style>
<div class="wrap">
<header>
 <p class="eyebrow">Mosaic Rescue · Figura 3</p>
 <h1>Two alleles, one gene, no phase</h1>
 <p class="sub">Por qué el alelo truncante es fuerte — y por qué ningún análisis sobre
 lecturas cortas puede demostrar que los dos están en <em>trans</em>.</p>
</header>

<div class="figframe">
<svg viewBox="0 0 1440 840" role="img" aria-label="Arquitectura del transcrito con el codón de parada prematuro, y distancia genómica entre los dos candidatos.">
<style>
 .lbl{{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:13px;fill:var(--ink)}}
 .lbl-sm{{font-family:"IBM Plex Sans",sans-serif;font-weight:500;font-size:11.5px;fill:var(--ink-soft)}}
 .mono{{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.06em;font-weight:500;fill:var(--ink-soft)}}
 .sect{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
        text-transform:uppercase;fill:var(--ink-soft);font-weight:500}}
</style>
{HTML_A}
{HTML_B}
<line x1="96" y1="792" x2="1336" y2="792" stroke="var(--rule)"/>
<text x="96" y="816" class="lbl-sm">Límites de exón sondeados a 2 pb sobre el mismo <tspan class="mono">release</tspan> de VEP usado en todo el análisis. Distancias genómicas leídas del VCF.</text>
</svg>
</div>

<div class="cap">
<p><strong>Panel A — por qué <code>PVS1</code> tiene fuerza.</strong> «Exón 17 de 23» no
basta: la regla se define contra la <strong>última unión exón-exón</strong>. Dibujado en
coordenadas de mRNA maduro, el PTC queda <strong>{LJ-PTC} nt</strong> por encima de esa
unión, frente a un umbral de 55. La franja sombreada es la zona donde un PTC
<em>escaparía</em> a NMD — y el nuestro está muy lejos de ella.</p>

<p><strong>Panel B — por qué la fase es irresoluble aquí.</strong> Entre los dos candidatos
hay <strong>un solo heterocigoto informativo</strong>. Los fragmentos verdes son librería
real (~{FRAG} pb) al mismo tamaño: se ve de un vistazo que ninguno tiende un puente. El
hueco más corto es <strong>{(GB-GH)/FRAG:.1f}× más largo</strong> que un fragmento.</p>

<p><strong>Esto no se arregla con más análisis.</strong> Se arregla con genotipos parentales
o con lectura larga dirigida. Es el experimento de mayor valor del proyecto.</p>
</div>

<div class="foot">
 <span>ALELO A · LIKELY PATHOGENIC</span>
 <span>ALELO B · VUS</span>
 <span>PM3 BLOQUEADO</span>
 <span>FASE NO RESUELTA</span>
</div>
</div>
"""
io.open("figures/fig3_phase.html", "w", encoding="utf-8", newline="\n").write(HTML)
print(f"  figures/fig3_phase.html ({len(HTML)/1024:.0f} KB)")
print(f"  exones {len(EX)} · PTC->union {LJ-PTC} nt · hueco/fragmento {(GB-GH)/FRAG:.1f}x")
