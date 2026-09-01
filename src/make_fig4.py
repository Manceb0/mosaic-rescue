#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 4 — interrogatorio estructural del candidato missense.

TODO lo que se dibuja sale de la medicion: coordenadas 3D reales proyectadas por
PCA, distancias de puente de hidrogeno medidas, perfil de pLDDT residuo a residuo
y densidad por cascara. Nada de este panel se podia dibujar antes de analizar.

Uso: python src/make_fig4.py
"""
import io, json, numpy as np

def _anon(lbl):
    """VAL998:O -> "vecino 2:O". Conserva el atomo (importa quimicamente) y
    elimina identidad y posicion del residuo (no importan, y reidentifican)."""
    res, _, atom = lbl.partition(":")
    _anon.seen.setdefault(res, len(_anon.seen) + 1)
    return "vecino %d:%s" % (_anon.seen[res], atom)
_anon.seen = {}

D = json.load(io.open("work/struct/fig4.json", encoding="utf-8"))
AT, BO, HB, SH, PL = D["atoms"], D["bonds"], D["hbonds"], D["shells"], D["plddt_profile"]
T = D["target"]

# ---------- Panel A: perfil de pLDDT (1050 residuos medidos) ----------
AX0, AY0, AW, AH = 88, 96, 1264, 108
xs = np.array([p[0] for p in PL], dtype=float)
ys = np.array([p[1] for p in PL], dtype=float)
def ax(r): return AX0 + (r - xs[0]) / (xs[-1] - xs[0]) * AW
def ay(v): return AY0 + AH - (v / 100.0) * AH
area = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in zip(xs, ys))
bands = ""
for lvl, col, lbl in ((90, "var(--plddt-hi)", "muy alta"), (70, "var(--plddt-mid)", "alta"), (50, "var(--plddt-lo)", "baja")):
    bands += (f'<line x1="{AX0}" y1="{ay(lvl):.1f}" x2="{AX0+AW}" y2="{ay(lvl):.1f}" '
              f'stroke="{col}" stroke-width="1" stroke-dasharray="3 4" opacity=".7"/>'
              f'<text x="{AX0+AW+8}" y="{ay(lvl)+4:.1f}" class="mono" fill="{col}">{lvl}</text>')
glob = float(np.mean(ys))

# ---------- Panel B: entorno molecular, coordenadas reales ----------
BX0, BY0, BW, BH = 88, 300, 700, 470
P = np.array([a["xy"] for a in AT], dtype=float)
mn, mx = P.min(axis=0), P.max(axis=0)
span = (mx - mn).max()
sc = min(BW, BH) * 0.86 / span
cx, cy = BX0 + BW / 2, BY0 + BH / 2
mid = (mn + mx) / 2
def bx(p): return cx + (p[0] - mid[0]) * sc
def by(p): return cy - (p[1] - mid[1]) * sc
dep = np.array([a["depth"] for a in AT]); dep = (dep - dep.min()) / (dep.ptp() + 1e-9)

COL = {"C": "var(--at-c)", "N": "var(--at-n)", "O": "var(--at-o)", "S": "var(--at-s)"}
bonds_svg = ""
for i, j in BO:
    a, b = AT[i], AT[j]
    tgt = a["target"] and b["target"]
    op = 0.30 + 0.55 * (dep[i] + dep[j]) / 2
    bonds_svg += (f'<line x1="{bx(a["xy"]):.1f}" y1="{by(a["xy"]):.1f}" '
                  f'x2="{bx(b["xy"]):.1f}" y2="{by(b["xy"]):.1f}" '
                  f'stroke="{"var(--target)" if tgt else "var(--bond)"}" '
                  f'stroke-width="{2.4 if tgt else 1.5}" opacity="{op:.2f}" stroke-linecap="round"/>')
atoms_svg = ""
for k, a in enumerate(AT):
    r = (3.9 if a["target"] else 2.5) * (0.72 + 0.5 * dep[k])
    atoms_svg += (f'<circle cx="{bx(a["xy"]):.1f}" cy="{by(a["xy"]):.1f}" r="{r:.1f}" '
                  f'fill="{COL.get(a["el"],"var(--at-c)")}" '
                  f'opacity="{0.35+0.6*dep[k]:.2f}" '
                  f'{"stroke=\'var(--target)\' stroke-width=\'1.2\'" if a["target"] else ""}/>')
hb_svg = ""
for h in HB:
    a, b = AT[h["fr"]], AT[h["to"]]
    x1, y1, x2, y2 = bx(a["xy"]), by(a["xy"]), bx(b["xy"]), by(b["xy"])
    col = "var(--hb-don)" if h["don"] else "var(--hb-acc)"
    hb_svg += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
               f'stroke="{col}" stroke-width="2" stroke-dasharray="4 3"/>'
               f'<rect x="{(x1+x2)/2-20:.1f}" y="{(y1+y2)/2-9:.1f}" width="40" height="15" rx="2" '
               f'fill="var(--panel)" opacity=".92"/>'
               f'<text x="{(x1+x2)/2:.1f}" y="{(y1+y2)/2+2:.1f}" class="mono" '
               f'fill="{col}" text-anchor="middle">{h["d"]:.2f} A</text>')
tgt_xy = [a["xy"] for a in AT if a["target"] and a["name"] == "CB"]
tgt_px = (bx(tgt_xy[0]), by(tgt_xy[0])) if tgt_xy else (cx, cy)

# ---------- Panel E: quimica de los tres puentes ----------
EX0, EY0, EW = 856, 520, 496
ehb = ""
for k, h in enumerate(sorted(HB, key=lambda x: x["don"], reverse=True)):
    yy = EY0 + 40 + k * 62
    col = "var(--hb-don)" if h["don"] else "var(--hb-acc)"
    rol = "DONA" if h["don"] else "ACEPTA"
    verdict = "un amonio tambien dona" if h["don"] else "un amonio NO puede aceptar"
    mark = "" if h["don"] else "  ← IRRECUPERABLE"
    ehb += (f'<text x="{EX0}" y="{yy}" class="lbl" fill="{col}">cadena lateral {rol}</text>'
            f'<text x="{EX0+170}" y="{yy}" class="mono" fill="{col}">{h["d"]:.2f} A</text>'
            f'<text x="{EX0+240}" y="{yy}" class="lbl-sm">{_anon(h["lbl"])}</text>'
            f'<text x="{EX0}" y="{yy+18}" class="lbl-sm">{verdict}{mark}</text>'
            f'<line x1="{EX0}" y1="{yy+30}" x2="{EX0+EW}" y2="{yy+30}" stroke="var(--rule)"/>')

# ---------- Panel C: densidad por cascara ----------
CX0, CY0, CW, CH = 900, 300, 300, 150
maxd = max(s["dens"] for s in SH) or 1
shells_svg = ""
for k, s in enumerate(SH):
    yy = CY0 + k * 24
    w = s["dens"] / maxd * CW
    core = 60 <= s["dens"]
    shells_svg += (f'<text x="{CX0-8}" y="{yy+10}" class="mono" text-anchor="end">{s["lo"]}-{s["hi"]} A</text>'
                   f'<rect x="{CX0}" y="{yy}" width="{max(w,1.5):.1f}" height="13" '
                   f'fill="{"var(--warn)" if core else "var(--ok)"}" opacity=".8"/>'
                   f'<text x="{CX0+max(w,1.5)+7}" y="{yy+10}" class="mono" fill="var(--ink-soft)">{s["dens"]:.0f}</text>')
core_lo = CX0 + 60 / maxd * CW

HTML = f"""<title>Interrogatorio estructural del residuo candidato</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --at-c:#6B7680;--at-n:#2E5FA3;--at-o:#B4453A;--at-s:#C9A227;--bond:#9AA4AD;
 --target:#C07A2E;--hb-don:#2E7D6B;--hb-acc:#B4453A;--measured:#1F4E5F;
 --plddt-hi:#2E7D6B;--plddt-mid:#C9A227;--plddt-lo:#B4453A;--ok:#2E7D6B;--warn:#B4453A;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--at-c:#8B96A0;--at-n:#6FA3E0;--at-o:#E0776A;
 --at-s:#E0C458;--bond:#5A646D;--target:#E0A458;--hb-don:#63BFA6;--hb-acc:#E0776A;
 --measured:#6FB3C6;--plddt-hi:#63BFA6;--plddt-mid:#E0C458;--plddt-lo:#E0776A;--ok:#63BFA6;--warn:#E0776A;}}}}
:root[data-theme="dark"]{{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--at-c:#8B96A0;--at-n:#6FA3E0;--at-o:#E0776A;--at-s:#E0C458;--bond:#5A646D;
 --target:#E0A458;--hb-don:#63BFA6;--hb-acc:#E0776A;--measured:#6FB3C6;
 --plddt-hi:#63BFA6;--plddt-mid:#E0C458;--plddt-lo:#E0776A;--ok:#63BFA6;--warn:#E0776A;}}
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
 <p class="eyebrow">Mosaic Rescue · Figura 4</p>
 <h1>Does the VUS destabilize BUBR1?</h1>
 <p class="sub">Todo lo dibujado procede de la medición: coordenadas atómicas reales,
 distancias de enlace medidas y pLDDT residuo a residuo. Nada de este panel podía trazarse
 antes de analizar la estructura.</p>
</header>

<div class="figframe">
<svg viewBox="0 0 1440 1030" role="img" aria-label="Interrogatorio estructural del residuo candidato en BUBR1.">
<style>
 .lbl{{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:13px;fill:var(--ink)}}
 .lbl-sm{{font-family:"IBM Plex Sans",sans-serif;font-weight:500;font-size:11.5px;fill:var(--ink-soft)}}
 .mono{{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.06em;font-weight:500;fill:var(--ink-soft)}}
 .sect{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
        text-transform:uppercase;fill:var(--ink-soft);font-weight:500}}
</style>

<!-- ═══ PANEL A ═══ -->
<text x="{AX0}" y="34" class="sect">A · Confianza del modelo, residuo a residuo (n=1050)</text>
<text x="1352" y="34" class="mono" text-anchor="end">PREDICTED · AlphaFold DB</text>
<line x1="{AX0}" y1="46" x2="1352" y2="46" stroke="var(--rule)"/>
{bands}
<polyline points="{area}" fill="none" stroke="var(--measured)" stroke-width="1.1" opacity=".85"/>
<line x1="{AX0}" y1="{ay(glob):.1f}" x2="{AX0+AW}" y2="{ay(glob):.1f}" stroke="var(--ink-soft)" stroke-width="1"/>
<text x="{AX0+6}" y="{ay(glob)-5:.1f}" class="mono">media global {glob:.1f}</text>
<line x1="{ax(T):.1f}" y1="{AY0-6}" x2="{ax(T):.1f}" y2="{AY0+AH}" stroke="var(--target)" stroke-width="2"/>
<circle cx="{ax(T):.1f}" cy="{ay(D['plddt_target']):.1f}" r="5" fill="var(--target)"/>
<text x="{ax(T)-8:.1f}" y="{AY0-12}" class="lbl" fill="var(--target)" text-anchor="end">residuo candidato · pLDDT {D['plddt_target']}</text>
<text x="{AX0}" y="{AY0+AH+16}" class="mono">1</text>
<text x="{AX0+AW}" y="{AY0+AH+16}" class="mono" text-anchor="end">1050 aa</text>
<text x="{AX0}" y="{AY0+AH+34}" class="lbl-sm">La media global baja refleja las regiones desordenadas de BUBR1. El residuo candidato está muy por encima: por eso su geometría local es utilizable.</text>

<!-- ═══ PANEL B ═══ -->
<text x="{BX0}" y="264" class="sect">B · Entorno atómico real · proyección PCA de coordenadas 3D</text>
<line x1="{BX0}" y1="276" x2="{BX0+BW}" y2="276" stroke="var(--rule)"/>
<rect x="{BX0}" y="{BY0}" width="{BW}" height="{BH}" fill="none" stroke="var(--rule)" stroke-dasharray="2 4"/>
{bonds_svg}
{hb_svg}
{atoms_svg}
<circle cx="{tgt_px[0]:.1f}" cy="{tgt_px[1]:.1f}" r="26" fill="none" stroke="var(--target)" stroke-width="1.5" opacity=".55"/>
<text x="{tgt_px[0]:.1f}" y="{tgt_px[1]-32:.1f}" class="lbl" fill="var(--target)" text-anchor="middle">candidato</text>
<g transform="translate({BX0+10},{BY0+BH-72})">
  <text x="0" y="0" class="mono">ÁTOMOS</text>
  <circle cx="6" cy="14" r="4" fill="var(--at-c)"/><text x="16" y="18" class="lbl-sm">C</text>
  <circle cx="46" cy="14" r="4" fill="var(--at-n)"/><text x="56" y="18" class="lbl-sm">N</text>
  <circle cx="86" cy="14" r="4" fill="var(--at-o)"/><text x="96" y="18" class="lbl-sm">O</text>
  <text x="0" y="42" class="mono">PUENTES DE H</text>
  <line x1="2" y1="54" x2="26" y2="54" stroke="var(--hb-don)" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="34" y="58" class="lbl-sm">la cadena lateral DONA</text>
  <line x1="2" y1="72" x2="26" y2="72" stroke="var(--hb-acc)" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="34" y="76" class="lbl-sm">la cadena lateral ACEPTA — irrecuperable</text>
</g>
<text x="{BX0}" y="{BY0+BH+22}" class="lbl-sm">{len(AT)} átomos de {len(D['neighbors'])+1} residuos. Opacidad y tamaño codifican profundidad en la proyección.</text>

<!-- ═══ PANEL C ═══ -->
<text x="{CX0-8}" y="264" class="sect" text-anchor="end">C · ¿Hay sitio?</text>
<line x1="{CX0-90}" y1="276" x2="1352" y2="276" stroke="var(--rule)"/>
<text x="{CX0-90}" y="294" class="lbl-sm">Densidad atómica por cáscara desde el Cβ (át./1000 Å³)</text>
{shells_svg}
<line x1="{core_lo:.1f}" y1="{CY0-6}" x2="{core_lo:.1f}" y2="{CY0+CH-6}" stroke="var(--warn)" stroke-dasharray="3 3"/>
<text x="{core_lo+6:.1f}" y="{CY0+CH+6}" class="mono" fill="var(--warn)">60 = umbral de núcleo</text>
<text x="{CX0-90}" y="{CY0+CH+30}" class="lbl-sm">La cadena entrante alcanzaría la cáscara 4–6 Å.</text>
<text x="{CX0-90}" y="{CY0+CH+48}" class="lbl" fill="var(--ok)">Por debajo del umbral: hay espacio.</text>

<!-- ═══ PANEL E ═══ -->
<text x="{EX0}" y="{EY0}" class="sect">E · El punto que sobrevive: química, no geometría</text>
<line x1="{EX0}" y1="{EY0+12}" x2="1352" y2="{EY0+12}" stroke="var(--rule)"/>
{ehb}
<text x="{EX0}" y="{EY0+230}" class="lbl-sm">Dos de los tres puentes son rescatables en principio. El tercero no:</text>
<text x="{EX0}" y="{EY0+248}" class="lbl" fill="var(--hb-acc)">ningún rotámero puede hacer que un amonio acepte.</text>

<!-- ═══ PANEL D ═══ -->
<text x="{AX0}" y="812" class="sect">D · Esperado vs observado</text>
<line x1="{AX0}" y1="824" x2="788" y2="824" stroke="var(--rule)"/>
<g transform="translate({AX0},848)">
  <text x="0" y="-24" class="mono">HIPÓTESIS</text><text x="300" y="-24" class="mono">RESULTADO</text>
  <text x="0" y="0" class="lbl-sm">Choque estérico</text><text x="300" y="0" class="lbl" fill="var(--ok)">NO SOSTENIDO</text>
  <text x="0" y="24" class="lbl-sm">Carga positiva enterrada</text><text x="300" y="24" class="lbl" fill="var(--plddt-mid)">DEBILITADO</text>
  <text x="0" y="48" class="lbl-sm">Pérdida de puente aceptor</text><text x="300" y="48" class="lbl" fill="var(--warn)">SOSTENIDO · química</text>
  <text x="0" y="72" class="lbl-sm">ΔΔG</text><text x="300" y="72" class="lbl-sm">NO MEDIDO — FoldX bloqueado</text>
  <text x="0" y="96" class="lbl-sm">Efecto funcional</text><text x="300" y="96" class="lbl-sm">DESCONOCIDO</text>
  <line x1="0" y1="116" x2="620" y2="116" stroke="var(--rule)"/>
  <text x="0" y="138" class="lbl-sm">RSA del residuo</text><text x="300" y="138" class="lbl">{D['rsa']} % · enterrado ({D['sasa']} Å²)</text>
</g>

<!-- ═══ PIE ═══ -->
<line x1="{AX0}" y1="968" x2="1352" y2="968" stroke="var(--rule)"/>
<text x="{AX0}" y="996" class="lbl" fill="var(--target)">PREDICCIÓN ESTRUCTURAL COMPUTACIONAL — NO ES EVIDENCIA FUNCIONAL</text>
<text x="{AX0}" y="1016" class="lbl-sm">Solo se inspeccionó el modelo silvestre. El mutante no se ha modelado. La clasificación clínica permanece VUS.</text>
</svg>
</div>

<div class="cap">
<p><strong>Qué se midió.</strong> El panel A es el pLDDT de los 1050 residuos del modelo de
AlphaFold DB: la media global de {glob:.1f} refleja las regiones desordenadas de BUBR1,
pero el residuo candidato está en <strong>{D['plddt_target']}</strong>. Eso es lo que
legitima analizar su geometría — en zona de baja confianza no significaría nada.</p>

<p><strong>El panel B son coordenadas atómicas reales</strong>, proyectadas al plano de
máxima varianza del entorno local. {len(AT)} átomos, {len(BO)} enlaces. Las tres líneas
discontinuas son puentes de hidrógeno con sus distancias medidas.</p>

<p><strong>El panel C desmonta parte de nuestra propia hipótesis.</strong> La cáscara donde
aterrizaría la cadena lateral entrante tiene una densidad por debajo del umbral de núcleo
globular: <em>hay espacio</em>. El argumento de choque estérico no se sostiene.</p>

<p><strong>Lo que sí queda en pie es químico, no geométrico.</strong> Uno de los tres
puentes tiene a la cadena lateral <em>aceptando</em> del nitrógeno del esqueleto. El grupo
entrante es un amonio: solo dona. Ese contacto se pierde por química y
<strong>ningún rotámero puede rescatarlo</strong>.</p>
</div>

<div class="foot">
 <span>ALPHAFOLD DB · AF-O60566-F1 · PREDICTED</span>
 <span>REVEL 0,472 — PP3 NO APLICA</span>
 <span>CLASIFICACIÓN: VUS</span>
 <span>FASE NO RESUELTA</span>
</div>
</div>
"""
io.open("figures/fig4_structural.html", "w", encoding="utf-8", newline="\n").write(HTML)
print(f"  figures/fig4_structural.html  ({len(HTML)/1024:.0f} KB)")
print(f"  atomos {len(AT)} · enlaces {len(BO)} · puentes {len(HB)} · pLDDT {len(PL)} puntos")
