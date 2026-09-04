#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 9 — la cancelacion de BAF, reproducida en simulacion.

El punto de la figura no es "nuestro estadistico gana". Es que en el escenario
VARIEGADO el estadistico de BAF con SIGNO se recentra en 0,5. OJO: la version
anterior decia que el estadistico ABSOLUTO se volvia anti-informativo por la
cancelacion, y EXP-015c lo falso -- eso lo producia la profundidad. Cuanto mayor es el
evento, peor detecta. Eso es un modo de fallo, y es lo que hay que ensenar.

La figura declara en el propio panel que la linea base de BAF NO es MoChA.

SANEADO: simulacion pura, sin dato alguno del paciente.
"""
import io, json

D = json.load(io.open("work/mosaic/dispersion_simulation.json", encoding="utf-8"))
R = D["results"]
W, H = 1440, 720
FR = sorted({r["fraction"] for r in R})


def series(mode, key):
    return [next(r[key] for r in R if r["mode"] == mode and r["fraction"] == f) for f in FR]


PX0, PY0, PW, PH = 190, 150, 480, 380
GAP = 120


def panel(x0, mode, title, note):
    s = ""
    # rejilla y ejes
    for p in (0, 0.25, 0.5, 0.75, 1.0):
        y = PY0 + PH - PH * p
        s += ('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--rule)"/>'
              '<text x="%d" y="%.1f" class="mono" text-anchor="end">%.2f</text>'
              % (x0, y, x0 + PW, y, x0 - 10, y + 3, p))
    for i, f in enumerate(FR):
        x = x0 + PW * i / (len(FR) - 1)
        s += ('<text x="%.1f" y="%d" class="mono" text-anchor="middle">%d %%</text>'
              % (x, PY0 + PH + 20, f * 100))

    for key, col, lbl in (("power_baf", "var(--dead)", "BAF"),
                          ("power_dispersion", "var(--alive)", "dispersion")):
        vals = series(mode, key)
        pts = " ".join("%.1f,%.1f" % (x0 + PW * i / (len(FR) - 1), PY0 + PH - PH * v)
                       for i, v in enumerate(vals))
        s += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>'
        for i, v in enumerate(vals):
            s += ('<circle cx="%.1f" cy="%.1f" r="5" fill="%s"/>'
                  % (x0 + PW * i / (len(FR) - 1), PY0 + PH - PH * v, col))

    s += ('<text x="%d" y="%d" class="big">%s</text>'
          '<text x="%d" y="%d" class="mono">%s</text>'
          % (x0, PY0 - 40, title, x0, PY0 - 22, note))
    return s


# anotacion del hallazgo: en variegado el BAF cae a cero justo donde el evento es mayor
x_last = PX0 + PW + GAP + PW
ann = ('<text x="%.1f" y="%.1f" class="lbl" fill="var(--dead)" text-anchor="end">'
       'potencia 0,000 al 20 %%</text>'
       '<text x="%.1f" y="%.1f" class="mono" fill="var(--dead)" text-anchor="end">'
       'cuanto MAYOR es el evento, peor detecta</text>'
       % (x_last - 12, PY0 + PH - 34, x_last - 12, PY0 + PH - 18))

svg = (
    '<svg viewBox="0 0 %d %d" role="img" aria-label="Simulacion de la cancelacion de BAF">\n'
    '<style>\n'
    '.ttl{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:25px;fill:var(--ink)}\n'
    '.sub{font-family:"IBM Plex Mono",monospace;font-size:11px;fill:var(--ink-soft)}\n'
    '.big{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:16px;fill:var(--ink)}\n'
    '.lbl{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:13px;fill:var(--ink)}\n'
    '.mono{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.04em;fill:var(--ink-soft)}\n'
    '</style>\n'
    '<rect width="%d" height="%d" fill="var(--ground)"/>\n'
    '<text x="70" y="52" class="ttl">La cancelacion de BAF, reproducida en simulacion</text>\n'
    '<text x="70" y="78" class="sub">DERIVED - simulacion pura, ningun dato del paciente - '
    'semilla %d - %d repeticiones por celda - tasa de falsos positivos fijada al %g</text>\n'
    '<line x1="70" y1="100" x2="%d" y2="100" stroke="var(--rule)"/>\n'
    '%s%s%s\n'
    '<text x="190" y="%d" class="mono">fraccion celular del evento</text>\n'
    '<rect x="190" y="%d" width="14" height="8" rx="3" fill="var(--dead)"/>'
    '<text x="212" y="%d" class="mono">desviacion media de BAF por sitio</text>'
    '<rect x="470" y="%d" width="14" height="8" rx="3" fill="var(--alive)"/>'
    '<text x="492" y="%d" class="mono">varianza del log-ratio de cobertura entre cromosomas</text>\n'
    '<text x="190" y="%d" class="lbl" fill="var(--gate)">La linea base de BAF NO es MoChA.</text>\n'
    '<text x="190" y="%d" class="mono">'
    'Es una desviacion por sitio, SIN FASE. MoChA obtiene su potencia del faseo de largo alcance, '
    'que amplifica una asimetria minuscula a lo largo de haplotipos enteros.</text>\n'
    '<text x="190" y="%d" class="mono">'
    'Por eso esta figura NO demuestra que el indice de dispersion supere al metodo estandar: '
    'la comparacion cara a cara no se ha hecho.</text>\n'
    '</svg>'
    % (W, H, W, H, D["seed"], D["n_rep"], D["alpha"], W - 70,
       panel(PX0, "clonal", "A - evento CLONAL", "todas las celulas ganan el mismo homologo"),
       panel(PX0 + PW + GAP, "variegated", "B - evento VARIEGADO (MVA)",
             "cada linaje gana un homologo al azar"),
       ann,
       PY0 + PH + 44, PY0 + PH + 62, PY0 + PH + 70, PY0 + PH + 62, PY0 + PH + 70,
       PY0 + PH + 110, PY0 + PH + 128, PY0 + PH + 144))

STYLE = """<!doctype html><meta charset="utf-8"><title>Figura 9</title><style>
:root{--ground:#FAFAF8;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --alive:#2E7D6B;--dead:#B4453A;--gate:#B4453A;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#0E1216;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--alive:#63BFA6;--dead:#E0776A;--gate:#E0776A;}}
:root[data-theme="dark"]{--ground:#0E1216;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--alive:#63BFA6;--dead:#E0776A;--gate:#E0776A;}
body{margin:0;background:var(--ground);font-family:"IBM Plex Sans",system-ui,sans-serif}
</style>"""

io.open("figures/fig9_mosaic_sim.html", "w", encoding="utf-8").write(STYLE + svg)
print("figures/fig9_mosaic_sim.html")
