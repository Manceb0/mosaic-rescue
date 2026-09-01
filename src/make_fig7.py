#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 7 — conservacion ortologa como prueba de RESTRICCION, no de patogenicidad.

Cuatro preguntas, cuatro paneles:
  A. .Esta la posicion mas restringida que el resto de la proteina? -> linea base
     con COBERTURA COMPARABLE (no vale comparar contra posiciones peor sostenidas)
  B. .Que quimica admite la evolucion aqui? -> repertorio observado
  C. .Sobrevive fuera de los linajes sobremuestreados? -> desglose por clado
  D. .El bolsillo conserva identidad o solo propiedad? -> identidad vs clase

ETIQUETAS DE EVIDENCIA
  EXTERNAL = secuencias y alineamientos de Ensembl Compara.
  DERIVED  = identidad, percentil, clase quimica y desglose por clado (esto).
  NO es MEASURED: eso se reserva a observaciones directas sobre los datos del caso.

SANEADO: sin numero de residuo ni identidad de aminoacidos. Los clados se
describen por CATEGORIA quimica, no por letra. Detalle en work/conservation/.
"""
import io, json, collections

D = json.load(io.open("work/conservation/conservation_full.json", encoding="utf-8"))
C, POCKET, BASE = D["candidate"], D["pocket"], D["baseline"]
CC, CLADES = D["coverage_comparable"], D["by_clade"]
ACCEPTOR = set("NQDESTYHW")
HUMAN = max(C["observed"], key=C["observed"].get)      # el mas frecuente es el humano

W, H = 1440, 1400

# ----------------- A - linea base con cobertura comparable -----------------
AX, AY, AW, AH = 70, 205, 620, 240
vals = CC["all_positions"]
bins = collections.Counter(min(19, int(v // 5)) for v in vals)
top = max(bins.values())
a = ""
for b in range(20):
    n = bins.get(b, 0)
    if not n:
        continue
    lo = b * 5
    a += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="%s" rx="2"/>'
          % (AX + AW * b / 20, AY + AH - AH * n / top, AW / 20 - 2, AH * n / top,
             "var(--alive)" if lo >= 95 else "var(--flow)", "1" if lo >= 95 else "0.5"))

cx = AX + AW * C["identity_pct"] / 100
a += ('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="var(--gate)" stroke-width="2"/>'
      '<circle cx="%.1f" cy="%d" r="5" fill="var(--gate)"/>'
      '<text x="%.1f" y="%d" class="lbl" text-anchor="end" fill="var(--gate)">residuo candidato</text>'
      '<text x="%.1f" y="%d" class="mono" text-anchor="end">percentil %.0f entre posiciones de cobertura comparable</text>'
      % (cx, AY - 32, cx, AY + AH + 8, cx, AY - 32,
         cx - 10, AY - 44, cx - 10, AY - 28, CC["candidate_percentile"]))

mx = AX + AW * CC["median_identity_pct"] / 100
a += ('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="var(--ink-soft)" stroke-width="1" stroke-dasharray="4 3"/>'
      '<text x="%.1f" y="%d" class="mono" text-anchor="middle">mediana %.0f %%</text>'
      % (mx, AY, mx, AY + AH + 8, mx, AY + AH + 24, CC["median_identity_pct"]))

for t in (0, 25, 50, 75, 100):
    a += ('<text x="%.1f" y="%d" class="mono" text-anchor="middle">%d</text>'
          % (AX + AW * t / 100, AY + AH + 40, t))
a += ('<text x="%.1f" y="%d" class="mono" text-anchor="middle">'
      'identidad con el humano, %% de ortologos alineados</text>'
      '<text x="%d" y="%d" class="mono">'
      'solo las %d posiciones alineadas en %d +/- %d ortologos, para no competir contra denominadores menores</text>'
      % (AX + AW / 2, AY + AH + 58, AX, AY + AH + 76,
         CC["n_positions"], CC["candidate_coverage"], CC["band"]))

# ----------------- B - repertorio quimico -----------------
BX, BY = 780, 205
obs = C["observed"]
squares, i = "", 0
for aa, n in sorted(obs.items(), key=lambda kv: (-(kv[0] in ACCEPTOR), -kv[1])):
    acc = aa in ACCEPTOR
    for _ in range(n):
        squares += ('<rect x="%d" y="%d" width="20" height="20" rx="4" fill="%s" opacity="%s"/>'
                    % (BX + (i % 15) * 26, BY + (i // 15) * 26,
                       "var(--alive)" if acc else "var(--dead)", "0.92" if acc else "1"))
        i += 1

by = BY + ((i + 14) // 15) * 26 + 26
acc_n = sum(n for aa, n in obs.items() if aa in ACCEPTOR)
b = squares + (
    '<rect x="%d" y="%d" width="20" height="20" rx="4" fill="var(--alive)"/>'
    '<text x="%d" y="%d" class="lbl">cadena lateral capaz de ACEPTAR un puente de hidrogeno</text>'
    '<text x="%d" y="%d" class="mono">%d de %d ortologos alineados - %.1f %%</text>'
    '<rect x="%d" y="%d" width="20" height="20" rx="4" fill="var(--dead)"/>'
    '<text x="%d" y="%d" class="lbl">sin cadena lateral aceptora</text>'
    '<text x="%d" y="%d" class="mono">%d de %d</text>'
    '<rect x="%d" y="%d" width="20" height="20" rx="4" fill="none" stroke="var(--gate)" '
    'stroke-width="2" stroke-dasharray="3 2"/>'
    '<text x="%d" y="%d" class="lbl" fill="var(--gate)">la clase que introduce la sustitucion</text>'
    '<text x="%d" y="%d" class="mono" fill="var(--gate)">cation, solo donador - 0 de %d ortologos</text>'
    % (BX, by, BX + 30, by + 15, BX + 30, by + 31, acc_n, i, 100.0 * acc_n / i,
       BX, by + 46, BX + 30, by + 61, BX + 30, by + 77, i - acc_n, i,
       BX, by + 92, BX + 30, by + 107, BX + 30, by + 123, i))

# ----------------- C - desglose por clado -----------------
# El agregado del panel B puede estar sostenido por un solo linaje sobremuestreado.
# Aqui el ancho de cada barra es el numero de ESPECIES, para que la caida del
# alineamiento en los linajes profundos sea visible en vez de quedar promediada.
CY = 630
CXL, CBW = 250, 640
maxsp = max(r["n_species"] for r in CLADES)
c = ""
for j, r in enumerate(CLADES):
    y = CY + j * 34
    unit = CBW / maxsp
    same = r["observed"].get(HUMAN, 0)
    other_acc = sum(k for aa, k in r["observed"].items() if aa in ACCEPTOR and aa != HUMAN)
    non_acc = r["n_aligned"] - same - other_acc
    x = CXL
    for n, col, op in ((same, "var(--alive)", "0.92"),
                       (other_acc, "var(--open)", "0.85"),
                       (non_acc, "var(--dead)", "1"),
                       (r["gapped"], "var(--rule)", "1")):
        if n:
            c += ('<rect x="%.1f" y="%d" width="%.1f" height="16" rx="3" fill="%s" opacity="%s"/>'
                  % (x, y, n * unit, col, op))
            x += n * unit + 1.5
    note = ("%d de %d no alinean" % (r["gapped"], r["n_species"])) if r["gapped"] > r["n_aligned"] \
        else ("%d especies" % r["n_species"])
    c += ('<text x="%d" y="%d" class="lbl" text-anchor="end">%s</text>'
          '<text x="%.1f" y="%d" class="mono">%s</text>'
          % (CXL - 14, y + 13, r["clade"], x + 12, y + 12, note))

ly = CY + len(CLADES) * 34 + 14
for k, (lbl, col, op) in enumerate((("mismo residuo que el humano", "var(--alive)", "0.92"),
                                    ("otro residuo, tambien aceptor", "var(--open)", "0.85"),
                                    ("no aceptor", "var(--dead)", "1"),
                                    ("no alinea en este clado", "var(--rule)", "1"))):
    c += ('<rect x="%d" y="%d" width="14" height="10" rx="3" fill="%s" opacity="%s"/>'
          '<text x="%d" y="%d" class="mono">%s</text>'
          % (CXL + k * 230, ly, col, op, CXL + k * 230 + 20, ly + 9, lbl))

# ----------------- D - identidad vs clase en el bolsillo -----------------
DY = 1010
pk = sorted(POCKET, key=lambda p: -p["identity_pct"])
DXL, DBW = 250, 900
d = ""
for j, p in enumerate(pk):
    y = DY + j * 30
    d += ('<text x="%d" y="%d" class="lbl" text-anchor="end">vecino %d - %s</text>'
          '<rect x="%d" y="%d" width="%.1f" height="9" rx="3" fill="var(--flow)"/>'
          '<rect x="%d" y="%d" width="%.1f" height="9" rx="3" fill="var(--open)" opacity="0.85"/>'
          % (DXL - 14, y + 13, j + 1, p["human_class"],
             DXL, y + 2, DBW * p["identity_pct"] / 100,
             DXL, y + 13, DBW * p["class_pct"] / 100))
    if p["class_pct"] - p["identity_pct"] > 25:
        d += ('<text x="%.1f" y="%d" class="mono" fill="var(--open)">'
              'identidad %.0f %% - clase %.0f %% - propiedad retenida</text>'
              % (DXL + DBW * p["class_pct"] / 100 + 12, y + 16, p["identity_pct"], p["class_pct"]))
    elif p["class_pct"] < 40:
        d += ('<text x="%.1f" y="%d" class="mono" fill="var(--dead)">'
              'identidad %.0f %% - clase %.0f %% - sin restriccion detectable</text>'
              % (DXL + DBW * p["class_pct"] / 100 + 12, y + 16, p["identity_pct"], p["class_pct"]))

for t in (0, 25, 50, 75, 100):
    d += ('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="var(--rule)" stroke-width="1"/>'
          '<text x="%.1f" y="%d" class="mono" text-anchor="middle">%d %%</text>'
          % (DXL + DBW * t / 100, DY - 8, DXL + DBW * t / 100, DY + len(pk) * 30,
             DXL + DBW * t / 100, DY + len(pk) * 30 + 18, t))
d += ('<rect x="%d" y="%d" width="14" height="8" rx="3" fill="var(--flow)"/>'
      '<text x="%d" y="%d" class="mono">misma IDENTIDAD que el humano</text>'
      '<rect x="%d" y="%d" width="14" height="8" rx="3" fill="var(--open)" opacity="0.85"/>'
      '<text x="%d" y="%d" class="mono">misma CLASE QUIMICA</text>'
      % (DXL, DY - 34, DXL + 22, DY - 26, DXL + 240, DY - 34, DXL + 262, DY - 26))

svg = (
    # xmlns y viewBox los inyecta src/export_svg.py; declararlos aqui duplica el atributo
    '<svg viewBox="0 0 %d %d" role="img"\n'
    ' aria-label="Conservacion ortologa del residuo candidato de BUB1B, por clado">\n'
    # las clases van DENTRO del <svg>: export_svg.py extrae solo ese elemento
    '<style>\n'
    '.ttl{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:25px;fill:var(--ink)}\n'
    '.sub{font-family:"IBM Plex Mono",monospace;font-size:11px;fill:var(--ink-soft)}\n'
    '.big{font-family:"IBM Plex Sans",sans-serif;font-weight:700;font-size:16px;fill:var(--ink)}\n'
    '.lbl{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:12.5px;fill:var(--ink)}\n'
    '.mono{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.04em;fill:var(--ink-soft)}\n'
    '</style>\n'
    '<rect width="%d" height="%d" fill="var(--ground)"/>\n'
    '<text x="70" y="58" class="ttl">Conservacion ortologa del residuo candidato</text>\n'
    '<text x="70" y="84" class="sub">'
    'EXTERNAL: secuencias y alineamientos de ortologos, Ensembl Compara - %d ortologos 1:1, sin paralogos'
    '</text>\n'
    '<text x="70" y="99" class="sub">'
    'DERIVED: identidad, percentil, clase quimica y desglose por clado - calculados en este proyecto'
    '</text>\n'
    '<line x1="70" y1="118" x2="%d" y2="118" stroke="var(--rule)"/>\n'
    '<text x="70" y="146" class="big">A - esta mas restringido que el resto de la proteina?</text>\n%s\n'
    '<text x="780" y="146" class="big">B - que quimica admite la evolucion aqui?</text>\n%s\n'
    '<text x="70" y="%d" class="big">C - sobrevive fuera de los linajes sobremuestreados?</text>\n'
    '<text x="70" y="%d" class="mono">'
    'los ortologos no son observaciones independientes: 91 de 153 son mamiferos. '
    'El ancho es el numero de ESPECIES del clado.</text>\n%s\n'
    '<text x="70" y="%d" class="big">D - el bolsillo: identidad, o solo propiedad?</text>\n%s\n'
    '</svg>'
    % (W, H, W, H, D["n_orthologs_one2one"], W - 70, a, b,
       CY - 62, CY - 44, c, DY - 62, d))

STYLE = """<!doctype html><meta charset="utf-8"><title>Figura 7</title><style>
:root{--ground:#FAFAF8;--panel:#FFF;--ink:#14191E;--ink-soft:#5A646D;--rule:#DCE0E3;
 --flow:#8C99A4;--alive:#2E7D6B;--dead:#B4453A;--open:#C07A2E;--gate:#B4453A;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#0E1216;--panel:#161C22;
 --ink:#E8EBED;--ink-soft:#94A0A9;--rule:#2A333B;--flow:#4A555F;--alive:#63BFA6;--dead:#E0776A;
 --open:#E0A458;--gate:#E0776A;}}
:root[data-theme="dark"]{--ground:#0E1216;--panel:#161C22;--ink:#E8EBED;--ink-soft:#94A0A9;
 --rule:#2A333B;--flow:#4A555F;--alive:#63BFA6;--dead:#E0776A;--open:#E0A458;--gate:#E0776A;}
body{margin:0;background:var(--ground);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif}
</style>"""

io.open("figures/fig7_conservation.html", "w", encoding="utf-8").write(STYLE + svg)
print("figures/fig7_conservation.html")
