#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera figures/bubr1_landscape.html a partir de los datos de ClinVar ya cruzados.

Solo missense en la capa principal: PM1 se evalua sobre la clase comparable, y
mezclar sinonimas hace el grafico enganoso.

Uso: python src/make_landscape_figure.py
"""
import io, json, collections

D = json.load(io.open("work/clinvar/landscape_missense.json", encoding="utf-8"))
V, CAND = D["variants"], D["candidate"]
PROT_LEN = 1050

X0, X1, W = 90, 1350, 1260
def x(pos): return X0 + (pos / PROT_LEN) * W

# --- capas ---
layers = {"P/LP": [], "B/LB": [], "VUS": [], "CONFLICTIVA": []}
for v in V:
    layers.setdefault(v["cls"], []).append(v["pos"])

def marks(poss, y, color, h=9, op=".85"):
    return "".join(f'<line x1="{x(p):.1f}" y1="{y}" x2="{x(p):.1f}" y2="{y-h}" '
                   f'stroke="{color}" stroke-width="1.5" opacity="{op}"/>' for p in poss)

# densidad de VUS en ventanas de 10 residuos
dens = collections.Counter(p // 10 * 10 for p in layers["VUS"])
mx = max(dens.values()) if dens else 1
vus_bars = "".join(
    f'<rect x="{x(k):.1f}" y="{478 - 34*dens[k]/mx:.1f}" width="{max(1.6,(x(k+10)-x(k))-0.5):.1f}" '
    f'height="{34*dens[k]/mx:.1f}" fill="var(--vus)" opacity=".5"/>' for k in sorted(dens))

# --- zoom 950-1050 ---
Z0, Z1, ZX0, ZW = 950, 1050, 130, 560
def zx(p): return ZX0 + (p - Z0) / (Z1 - Z0) * ZW
zoom = ""
for cls, col, yy in (("VUS", "var(--vus)", 726), ("B/LB", "var(--benign)", 758), ("P/LP", "var(--path)", 694)):
    for p in layers.get(cls, []):
        if Z0 <= p <= Z1:
            zoom += (f'<line x1="{zx(p):.1f}" y1="{yy}" x2="{zx(p):.1f}" y2="{yy-13}" '
                     f'stroke="{col}" stroke-width="1.8" opacity=".8"/>')

# --- panel de consecuencias P/LP (todo el gen) ---
CONS = [("Frameshift", 38), ("Stop gained", 34), ("Splice acceptor", 6),
        ("Splice donor", 4), ("Splice region", 1), ("Missense", 1)]
BX, BY, BW = 830, 690, 300
bars = ""
for i, (lbl, n) in enumerate(CONS):
    yy = BY + i * 24
    w = n / 38 * BW
    hi = lbl == "Missense"
    bars += (f'<text x="{BX-10}" y="{yy+9}" class="lbl-sm" text-anchor="end">{lbl}</text>'
             f'<rect x="{BX}" y="{yy}" width="{max(w,2):.1f}" height="12" '
             f'fill="{"var(--accent)" if hi else "var(--path)"}" opacity="{".95" if hi else ".55"}"/>'
             f'<text x="{BX+max(w,2)+8}" y="{yy+10}" class="mono" '
             f'fill="{"var(--accent)" if hi else "var(--ink-soft)"}">{n}</text>')

T = dict(P=len(layers["P/LP"]), B=len(layers["B/LB"]), V=len(layers["VUS"]))

HTML = f"""<title>BUBR1 Variant Landscape</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --path:#B4453A;--benign:#2E7D6B;--vus:#8892A0;--accent:#C07A2E;--measured:#1F4E5F;--domain:#E7E3D8;}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--path:#E0776A;--benign:#63BFA6;--vus:#78848F;
 --accent:#E0A458;--measured:#6FB3C6;--domain:#242C33;}}}}
:root[data-theme="dark"]{{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--path:#E0776A;--benign:#63BFA6;--vus:#78848F;--accent:#E0A458;--measured:#6FB3C6;--domain:#242C33;}}
body{{background:var(--ground);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;
 margin:0;padding:clamp(20px,4vw,52px) clamp(16px,4vw,52px) 60px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:26px}}
.eyebrow{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--ink-soft);margin:0}}
h1{{font-size:clamp(25px,3.8vw,38px);font-weight:700;letter-spacing:-.022em;line-height:1.1;
 margin:10px 0 0;text-wrap:balance}}
.sub{{margin:12px 0 0;font-size:clamp(15px,1.7vw,19px);line-height:1.45;color:var(--ink);
 font-style:italic;border-left:2px solid var(--accent);padding-left:16px;max-width:52ch}}
.figframe{{background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:8px;overflow-x:auto}}
svg{{display:block;width:100%;height:auto;min-width:940px}}
.cap{{display:grid;gap:8px;font-size:13px;line-height:1.55;color:var(--ink-soft);max-width:80ch}}
.cap strong{{color:var(--ink);font-weight:600}}
.foot{{display:flex;flex-wrap:wrap;gap:10px 26px;border-top:1px solid var(--rule);padding-top:16px;
 font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-soft)}}
</style>
<div class="wrap">
<header>
 <p class="eyebrow">Mosaic Rescue · Figura 2</p>
 <h1>BUBR1 Variant Landscape</h1>
 <p class="sub">A hypothesis that weakened under independent evidence.</p>
</header>

<div class="figframe">
<svg viewBox="0 0 1440 830" role="img" aria-label="Distribución de variantes missense de ClinVar a lo largo de BUBR1.">
<style>
 .lbl{{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:13px;fill:var(--ink)}}
 .lbl-sm{{font-family:"IBM Plex Sans",sans-serif;font-weight:500;font-size:11.5px;fill:var(--ink-soft)}}
 .mono{{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.08em;font-weight:500}}
 .sect{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
        text-transform:uppercase;fill:var(--ink-soft);font-weight:500}}
</style>

<text x="{X0}" y="34" class="sect">Solo variantes missense · ClinVar 2026-08-22</text>
<text x="1350" y="34" class="mono" fill="var(--ink-soft)" text-anchor="end">EXTERNAL</text>
<line x1="{X0}" y1="46" x2="1350" y2="46" stroke="var(--rule)"/>

<!-- P/LP arriba -->
<text x="{X0-12}" y="122" class="lbl" text-anchor="end" fill="var(--path)">P / LP</text>
<text x="{X0-12}" y="138" class="mono" text-anchor="end" fill="var(--ink-soft)">n={T['P']}</text>
{marks(layers['P/LP'], 128, 'var(--path)', 34, '.95')}

<!-- eje proteina -->
<rect x="{X0}" y="132" width="{W}" height="16" fill="var(--domain)" stroke="var(--rule)"/>
<text x="{X0}" y="168" class="mono" fill="var(--ink-soft)">1</text>
<text x="1350" y="168" class="mono" fill="var(--ink-soft)" text-anchor="end">{PROT_LEN} aa</text>

<!-- B/LB abajo -->
{marks(layers['B/LB'], 182, 'var(--benign)', -34, '.95')}
<text x="{X0-12}" y="200" class="lbl" text-anchor="end" fill="var(--benign)">B / LB</text>
<text x="{X0-12}" y="216" class="mono" text-anchor="end" fill="var(--ink-soft)">n={T['B']}</text>

<!-- candidato -->
<line x1="{x(CAND):.1f}" y1="86" x2="{x(CAND):.1f}" y2="196" stroke="var(--measured)" stroke-width="2"/>
<circle cx="{x(CAND):.1f}" cy="140" r="6" fill="var(--measured)"/>
<text x="{x(CAND)-8:.1f}" y="80" class="lbl" text-anchor="end" fill="var(--measured)">candidato del paciente</text>
<text x="{x(CAND)-8:.1f}" y="96" class="mono" text-anchor="end" fill="var(--measured)">MEASURED · VUS</text>

<!-- dominios -->
<text x="{X0}" y="262" class="sect">Arquitectura de BUBR1</text>
<rect x="{x(1):.1f}" y="276" width="{x(200)-x(1):.1f}" height="22" fill="var(--domain)" stroke="var(--rule)"/>
<text x="{(x(1)+x(200))/2:.1f}" y="291" class="lbl-sm" text-anchor="middle">TPR N-terminal</text>
<rect x="{x(400):.1f}" y="276" width="{x(500)-x(400):.1f}" height="22" fill="var(--domain)" stroke="var(--rule)"/>
<text x="{(x(400)+x(500))/2:.1f}" y="291" class="lbl-sm" text-anchor="middle">GLEBS</text>
<rect x="{x(766):.1f}" y="276" width="{x(1050)-x(766):.1f}" height="22" fill="var(--accent)" opacity=".2" stroke="var(--accent)"/>
<text x="{(x(766)+x(1050))/2:.1f}" y="291" class="lbl-sm" text-anchor="middle" fill="var(--accent)">dominio pseudoquinasa · estabilidad</text>
<text x="{X0}" y="318" class="lbl-sm">Límites aproximados (UniProt). BUBR1 es pseudoquinasa: el dominio aporta integridad conformacional, no catálisis.</text>

<!-- densidad VUS -->
<text x="{X0}" y="376" class="sect">Densidad de VUS · ventanas de 10 residuos</text>
<text x="1350" y="376" class="mono" fill="var(--ink-soft)" text-anchor="end">n={T['V']} · 95 % de las missense del gen</text>
<line x1="{X0}" y1="388" x2="1350" y2="388" stroke="var(--rule)"/>
{vus_bars}
<line x1="{X0}" y1="478" x2="1350" y2="478" stroke="var(--rule)"/>
<line x1="{x(CAND):.1f}" y1="440" x2="{x(CAND):.1f}" y2="484" stroke="var(--measured)" stroke-width="2"/>

<!-- zoom -->
<text x="{ZX0}" y="640" class="sect">Ampliación alrededor del candidato</text>
<line x1="{ZX0}" y1="652" x2="{ZX0+ZW}" y2="652" stroke="var(--rule)"/>
<text x="{ZX0-12}" y="690" class="lbl-sm" text-anchor="end" fill="var(--path)">P/LP</text>
<text x="{ZX0-12}" y="722" class="lbl-sm" text-anchor="end" fill="var(--vus)">VUS</text>
<text x="{ZX0-12}" y="754" class="lbl-sm" text-anchor="end" fill="var(--benign)">B/LB</text>
<rect x="{ZX0}" y="762" width="{ZW}" height="8" fill="var(--domain)" stroke="var(--rule)"/>
{zoom}
<line x1="{zx(CAND):.1f}" y1="676" x2="{zx(CAND):.1f}" y2="772" stroke="var(--measured)" stroke-width="2"/>
<circle cx="{zx(CAND):.1f}" cy="766" r="5" fill="var(--measured)"/>
<text x="{zx(CAND):.1f}" y="668" class="mono" fill="var(--measured)" text-anchor="middle">candidato</text>
<text x="{ZX0}" y="792" class="mono" fill="var(--ink-soft)">{Z0}</text>
<text x="{ZX0+ZW}" y="792" class="mono" fill="var(--ink-soft)" text-anchor="end">{Z1}</text>
<rect x="{zx(CAND)+14:.1f}" y="700" width="290" height="40" rx="3" fill="var(--panel)" stroke="var(--accent)"/>
<text x="{zx(CAND)+26:.1f}" y="716" class="lbl-sm" fill="var(--accent)">mismo cambio de aminoácido, reportado</text>
<text x="{zx(CAND)+26:.1f}" y="732" class="lbl-sm" fill="var(--accent)">de forma independiente — también VUS</text>

<!-- panel secundario -->
<text x="{BX-10}" y="640" class="sect" text-anchor="end">Qué es P/LP en BUB1B</text>
<line x1="{BX-300}" y1="652" x2="1350" y2="652" stroke="var(--rule)"/>
<text x="{BX-10}" y="672" class="lbl-sm" text-anchor="end">84 variantes, todo el gen</text>
{bars}
<text x="{BX-300}" y="838" class="lbl-sm"></text>
</svg>
</div>

<div class="cap">
<p><strong>Qué dice esta figura, y qué no.</strong> Dice que <em>la evidencia clínica actual
no respalda esta región como hotspot de missense patogénicas</em>, y que una sumisión
independiente del mismo cambio de aminoácido también quedó en VUS. <strong>No dice que la
missense sea benigna.</strong></p>

<p><strong>Solo missense en la capa principal.</strong> Un primer conteo mezcló todas las
consecuencias y dio «0 patogénicas frente a 35 benignas» en la ventana del candidato —
pero <strong>31 de esas 35 eran sinónimas</strong>, no comparables con una missense.
Corregido: 0 P/LP y 4 B/LB missense.</p>

<p><strong>El hallazgo real es más amplio.</strong> En todo <code>BUB1B</code> hay
<strong>una sola</strong> missense clasificada P/LP entre 1 497, y el 95 % son VUS. No es
que la región del candidato esté señalada en contra: es que <strong>ningún punto de este gen
tiene un hotspot de missense demostrable</strong>.</p>

<p><strong>El panel derecho es contexto, no prueba.</strong> Que el 97 % de lo patogénico en
este gen sea pérdida de función refleja también sesgo de constatación: las missense en genes
recesivos se quedan en VUS por falta de fase y datos funcionales — exactamente nuestro
problema.</p>
</div>

<div class="foot">
 <span>CLINVAR 2026-08-22 · EXTERNAL</span>
 <span>CANDIDATO DEL PACIENTE · MEASURED · VUS</span>
 <span>REVEL 0,472 — PP3 NO APLICA</span>
 <span>FASE NO RESUELTA</span>
</div>
</div>
"""
io.open("figures/bubr1_landscape.html", "w", encoding="utf-8", newline="\n").write(HTML)
print(f"  figures/bubr1_landscape.html generado")
print(f"  missense: P/LP={T['P']}  B/LB={T['B']}  VUS={T['V']}")
