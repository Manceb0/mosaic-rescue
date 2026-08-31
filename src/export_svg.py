#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae el <svg> de una figura HTML y lo escribe como SVG independiente.

Emite el SVG con los colores RESUELTOS a literales, sin var(--x). Motivo: GitHub
sanea el SVG al renderizarlo en Markdown y puede eliminar el bloque <style>, con
lo que una figura basada en variables CSS saldria sin color. Un SVG plano con
fondo explicito se ve igual en cualquier tema y en cualquier visor.

Uso: python src/export_svg.py figures/figX.html [mas...]
"""
import io, re, sys, os

VAR = re.compile(r"var\(\s*--([\w-]+)\s*\)")
MEDIA = re.compile(r"@media[^{]*\{(?:[^{}]*\{[^}]*\})*?[^{}]*\}", re.S)


def extract(path):
    src = io.open(path, encoding="utf-8").read()

    # --- 1. paleta: primer bloque :root sin @media delante (tema claro) ---
    palette = {}
    head = src.split("</style>")[0] if "</style>" in src else src
    head_no_media = MEDIA.sub("", head)
    m = re.search(r":root\s*\{([^}]*)\}", head_no_media)
    if m:
        for name, val in re.findall(r"--([\w-]+)\s*:\s*([^;}]+)", m.group(1)):
            palette[name.strip()] = val.strip()

    # --- 2. el propio <svg> ---
    m = re.search(r"(<svg\b.*?</svg>)", src, re.S)
    if not m:
        return None, 0
    svg = m.group(1)

    # --- 3. resolver variables a literales, iterando por si anidan ---
    def resolve(mm):
        return palette.get(mm.group(1).strip(), "#333333")

    prev = None
    while prev != svg:
        prev = svg
        svg = VAR.sub(resolve, svg)

    # --- 4. fuera media queries del style interno: ya no aplican ---
    svg = MEDIA.sub("", svg)

    # --- 5. cabecera independiente + fondo explicito ---
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if vb:
        w, h = vb.group(1), vb.group(2)
        bg = palette.get("panel", "#FFFFFF")
        svg = re.sub(r"(<svg\b[^>]*>)",
                     r'\1<rect x="0" y="0" width="%s" height="%s" fill="%s"/>' % (w, h, bg),
                     svg, count=1)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + svg, len(palette)


for p in sys.argv[1:]:
    out, npal = extract(p)
    if not out:
        print(f"  {p}: no se encontro <svg>")
        continue
    dst = os.path.splitext(p)[0] + ".svg"
    io.open(dst, "w", encoding="utf-8", newline="\n").write(out)
    left = len(VAR.findall(out))
    flag = "" if left == 0 else f"  <-- QUEDAN {left} SIN RESOLVER"
    print(f"  {dst}  ({len(out)/1024:.0f} KB · {npal} colores resueltos){flag}")
