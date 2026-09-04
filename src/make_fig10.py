#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 10 — Track 2: dos rutas, ocho puentes, y el corredor de rescate seguro.

El punto de la figura NO es "tenemos un farmaco". Es lo contrario: ensenar
DONDE esta rota la cadena, y que las dos rutas tienen consecuencias oncologicas
opuestas aunque compartan la palabra "proteostasis".

SANEADO: solo mecanismo y evidencia publicada. Ningun dato del paciente.
"""
import io

# ALTURA COMPACTADA. Con el paso de carril a 300 px para cajas de 96 px, y el
# corredor en y=990, la figura arrastraba ~308 px de blanco puro (24 % del
# alto) repartidos en dos huecos: entre el carril A y el B, y entre el carril
# B y el corredor. Nada ocupaba ese espacio. Paso 215 y corredor en 810.
W, H = 1440, 1100

# (n, texto, ruta, fuerza) — fuerza: 'ok' evidencia, 'weak' inferencia, 'gap' hueco
BRIDGES = [
    (1, "variante de ESTE paciente\n-> inestabilidad de BUBR1", "A", "gap"),
    (2, "inestabilidad\n-> menos proteina", "A", "ok"),
    (3, "subir chaperonas\n-> SUBIR abundancia", "A", "gap"),
    (4, "mas BUBR1\n-> menos CIN", "A", "ok"),
    (5, "aneuploidia\n-> estres proteotoxico", "B", "ok"),
    (6, "subir HSP (genetico)\n-> rescate del estres", "B", "ok"),
    (7, "coinduccion FARMACOLOGICA\n-> el mismo rescate", "B", "gap"),
    (8, "la intervencion\n-> efecto sobre CIN", "B", "empty"),
]
COL = {"ok": "var(--alive)", "weak": "var(--open)", "gap": "var(--dead)",
       "against": "var(--dead)", "empty": "var(--void)"}
LBL = {"ok": "evidencia publicada", "weak": "inferencia", "gap": "HUECO",
       "against": "CONTRAEVIDENCIA", "empty": "SIN EVIDENCIA QUE CUALIFIQUE"}

# ---------------- A · los ocho puentes ----------------
AY, BW, BH, GAP = 240, 250, 96, 34
a = ""
for lane, route, title, sub in ((0, "A", "T2-A · rescate AGUAS ARRIBA",
                                 "menos celulas aneuploides NUEVAS"),
                                (1, "B", "T2-B · tolerancia AGUAS ABAJO",
                                 "las que ya existen viven mejor")):
    y = AY + lane * 215
    items = [b for b in BRIDGES if b[2] == route]
    a += (f'<text x="70" y="{y - 44}" class="big">{title}</text>'
          f'<text x="70" y="{y - 24}" class="mono">{sub}</text>')
    for i, (n, txt, _, strength) in enumerate(items):
        x = 70 + i * (BW + GAP)
        a += (f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="10" '
              f'fill="var(--panel)" stroke="{COL[strength]}" stroke-width="3"/>'
              f'<circle cx="{x + 20}" cy="{y + 20}" r="12" fill="{COL[strength]}"/>'
              f'<text x="{x + 20}" y="{y + 24}" class="num" text-anchor="middle">{n}</text>')
        for j, line in enumerate(txt.split("\n")):
            a += (f'<text x="{x + 40}" y="{y + 18 + j * 15}" class="lbl-s">{line}</text>')
        a += (f'<text x="{x + 12}" y="{y + BH - 12}" class="mono" '
              f'fill="{COL[strength]}">{LBL[strength]}</text>')
        if i < len(items) - 1:
            a += (f'<path d="M{x + BW + 4},{y + BH / 2} L{x + BW + GAP - 6},{y + BH / 2}" '
                  f'stroke="var(--ink-soft)" stroke-width="2" marker-end="url(#ar)"/>')

# ---------------- B · el corredor ----------------
CY, CX, CW, CH = 810, 380, 620, 160
b = (f'<rect x="{CX}" y="{CY - CH}" width="{CW / 2}" height="{CH}" '
     f'fill="var(--alive)" opacity="0.13"/>'
     f'<rect x="{CX + CW / 2}" y="{CY}" width="{CW / 2}" height="{CH}" '
     f'fill="var(--dead)" opacity="0.13"/>'
     f'<line x1="{CX}" y1="{CY}" x2="{CX + CW}" y2="{CY}" stroke="var(--ink)" stroke-width="1.5"/>'
     f'<line x1="{CX + CW / 2}" y1="{CY - CH}" x2="{CX + CW / 2}" y2="{CY + CH}" '
     f'stroke="var(--ink)" stroke-width="1.5"/>'
     f'<text x="{CX + CW / 2}" y="{CY - CH - 14}" class="lbl" text-anchor="middle">BENEFICIO</text>'
     f'<text x="{CX + CW / 2}" y="{CY + CH + 26}" class="lbl" text-anchor="middle" '
     f'fill="var(--dead)">RIESGO ONCOLOGICO</text>'
     f'<text x="{CX + CW + 14}" y="{CY + 4}" class="mono">mayor supervivencia</text>'
     f'<text x="{CX + CW + 14}" y="{CY + 17}" class="mono">de celulas con CIN</text>'
     f'<text x="{CX + 26}" y="{CY - CH + 30}" class="lbl" fill="var(--alive)">CORREDOR DE</text>'
     f'<text x="{CX + 26}" y="{CY - CH + 48}" class="lbl" fill="var(--alive)">RESCATE SEGURO</text>'
     f'<circle cx="{CX + 150}" cy="{CY - 130}" r="9" fill="var(--alive)"/>'
     f'<text x="{CX + 166}" y="{CY - 126}" class="lbl-s">T2-A · mas BUBR1, menos CIN nueva</text>'
     f'<circle cx="{CX + CW - 190}" cy="{CY + 120}" r="9" fill="var(--dead)"/>'
     f'<text x="{CX + CW - 176}" y="{CY + 124}" class="lbl-s">T2-B · la celula tolera mejor</text>'
     f'<text x="{CX + CW - 176}" y="{CY + 139}" class="mono">ser aneuploide</text>'
     f'<text x="{CX + 26}" y="{CY + CH - 40}" class="mono" fill="var(--dead)">ZONA PROHIBIDA</text>'
     f'<text x="{CX + 26}" y="{CY + CH - 26}" class="mono">rescata, pero hace viable</text>'
     f'<text x="{CX + 26}" y="{CY + CH - 13}" class="mono">el clon inestable</text>')

svg = (
    f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Track 2: rutas, puentes y corredor">\n'
    '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">'
    '<path d="M0,0 L7,3 L0,6 Z" fill="var(--ink-soft)"/></marker></defs>\n'
    '<style>\n'
    '.ttl{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:25px;fill:var(--ink)}\n'
    '.sub{font-family:"IBM Plex Mono",monospace;font-size:11px;fill:var(--ink-soft)}\n'
    '.big{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:16px;fill:var(--ink)}\n'
    '.lbl{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:13px;fill:var(--ink)}\n'
    '.lbl-s{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:11.5px;fill:var(--ink)}\n'
    '.num{font-family:"IBM Plex Mono",monospace;font-weight:700;font-size:12px;fill:#FFF}\n'
    '.mono{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.04em;fill:var(--ink-soft)}\n'
    '</style>\n'
    f'<rect width="{W}" height="{H}" fill="var(--ground)"/>\n'
    '<text x="70" y="52" class="ttl">Track 2 — dos rutas con consecuencias oncologicas opuestas</text>\n'
    '<text x="70" y="78" class="sub">EXTERNAL: evidencia publicada, tabla verificada del brief. '
    'DERIVED: la asignacion de cada evidencia a su puente.</text>\n'
    '<text x="70" y="93" class="sub">Se nominan BRAZOS farmacologicos para discriminacion preclinica, no un ganador terapeutico. La figura ensena DONDE esta '
    'rota la cadena.</text>\n'
    f'<line x1="70" y1="112" x2="{W - 70}" y2="112" stroke="var(--rule)"/>\n'
    f'<text x="70" y="146" class="big">A - los ocho puentes, y cuales estan vacios</text>\n'
    f'<text x="70" y="166" class="mono">la evidencia de un puente NO vale para otro. '
    'Agrupar las dos rutas bajo "proteostasis" hacia que lo pareciera.</text>\n'
    f'{a}\n'
    f'<text x="70" y="{CY - CH - 46}" class="big">B - el corredor de rescate seguro</text>\n'
    f'<text x="70" y="{CY - CH - 26}" class="mono">el buen candidato no es el que mas rescata:</text>\n'
    f'<text x="70" y="{CY - CH - 13}" class="mono">es el que mejora el mecanismo SIN aumentar</text>\n'
    f'<text x="70" y="{CY - CH}" class="mono">la tolerancia clonal de celulas aneuploides</text>\n'
    f'{b}\n'
    f'<text x="70" y="{H - 46}" class="lbl" fill="var(--void)">El puente 8 no esta debil: esta VACIO.</text>\n'
    f'<text x="70" y="{H - 28}" class="mono">Nuestra busqueda acotada no encontro evidencia que cualifique sobre que le hace ninguna de estas '
    'intervenciones a la CIN ni a la supervivencia clonogenica de celulas aneuploides frente a '
    'euploides isogenicas.</text>\n'
    f'<text x="70" y="{H - 14}" class="mono">Es el puente que decide si la hipotesis entra en el '
    'corredor o solo hace que una celula aneuploide se sienta mejor.</text>\n'
    '</svg>')

STYLE = """<!doctype html><meta charset="utf-8"><title>Figura 10</title><style>
:root{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --alive:#2E7D6B;--dead:#B4453A;--open:#C07A2E;--void:#6B5F87;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--alive:#63BFA6;--dead:#E0776A;--open:#E0A458;
 --void:#9C8FBC;}}
:root[data-theme="dark"]{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--alive:#63BFA6;--dead:#E0776A;--open:#E0A458;--void:#9C8FBC;}
body{margin:0;background:var(--ground);font-family:"IBM Plex Sans",system-ui,sans-serif}
</style>"""

io.open("figures/fig10_track2_bridges.html", "w", encoding="utf-8").write(STYLE + svg)
print("figures/fig10_track2_bridges.html")
