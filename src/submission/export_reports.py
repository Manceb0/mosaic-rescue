#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Empaqueta los informes de entrega (Markdown + PDF) con el formulario de metodos dentro.

    python src/submission/export_reports.py            # dependencias: openpyxl, markdown, playwright (Edge o Chromium)

POR QUE
    La plataforma de Track 1 solo tiene dos casillas: el CSV y UN informe (PDF o Markdown). La
    plantilla oficial de metodos (Excel) se pide "para organizar" ese informe, asi que sus
    respuestas tienen que viajar DENTRO del informe o el jurado no las ve. Este script:

    1. el informe maestro manda: las respuestas viven en el apendice de reports/TRACK{1,2}_REPORT.md,
       entre marcadores, y se ESCRIBEN en el Excel de entrega
       (work/submission/subir/<equipo>_methods_description.xlsx), nunca al reves. Hasta 2026-10-07 el
       sentido era Excel -> informe; con el apendice corregido despues (HLA-DRB1, Exomiser «externo»,
       EXP-029), ejecutar el exportador antiguo habria revertido esas correcciones con el Excel del
       26-sep. Una pregunta del Excel que no aparezca en el apendice detiene el proceso;
    2. escribe la copia Markdown de entrega con enlaces absolutos al repositorio;
    3. escribe un PDF con las figuras INCRUSTADAS, porque mientras el repositorio sea privado
       las imagenes enlazadas no se ven.

    No toca el CSV ni lee datos del paciente.
"""
from __future__ import annotations
import os, re, shutil, sys, pathlib

TEAM = "mosaic-rescue"
REPO_URL = "https://github.com/Manceb0/mosaic-rescue/blob/main/"
OUT = "work/submission/subir"
XLSX = os.path.join(OUT, f"{TEAM}_methods_description.xlsx")
EXTRA_OUT = os.environ.get("MVA_DELIVERY_DIR")  # copia opcional fuera del repo (p. ej. Descargas)
START, END = "<!-- methods-form:start -->", "<!-- methods-form:end -->"
REPORTS = {1: ("reports/TRACK1_REPORT.md", "Track 1 methods", range(7, 20)),
           2: ("reports/TRACK2_REPORT.md", "Track 2 methods", range(7, 18))}

CSS = """body{font-family:Cambria,Georgia,'Times New Roman',serif;font-size:10.5pt;line-height:1.5;color:#111;
  max-width:170mm;margin:auto}
h1{font-size:19pt;font-weight:700;margin:0 0 4pt}h2{font-size:12.5pt;font-weight:700;margin:16pt 0 4pt}
h3{font-size:11pt;font-weight:700;font-style:italic;margin:12pt 0 3pt}
p{margin:0 0 7pt;text-align:justify;hyphens:auto}li{margin:0 0 3pt}
table{border-collapse:collapse;width:100%;font-size:9pt;line-height:1.35;margin:8pt 0 10pt;
  border-top:1.2pt solid #111;border-bottom:1.2pt solid #111}
th{font-weight:700;text-align:left;border-bottom:.6pt solid #111;padding:3pt 6pt;vertical-align:bottom}
td{padding:3pt 6pt;vertical-align:top;border:none}
code{font-family:inherit;font-size:inherit;background:none;padding:0}
pre{font-family:Consolas,'Courier New',monospace;font-size:8.5pt;margin:4pt 0 8pt 12pt;white-space:pre-wrap}
pre code{font-family:inherit}
blockquote{margin:6pt 18pt;padding:0;color:#333;font-style:italic}
img{max-width:100%;display:block;margin:8pt auto}a{color:#1d3f6e;text-decoration:none}hr{display:none}
h1,h2,h3{break-after:avoid}
img,tr,blockquote,pre{break-inside:avoid}
p:has(+ table),p:has(+ p > img){break-after:avoid}
thead:not(:has(th:not(:empty))){display:none}"""
# Formato de artículo, no de interfaz (2026-10-07, a petición del usuario): texto con serifa, títulos sin subrayar,
# tablas de tres rayas sin rejilla ni fondos, nombres y rutas sin «fichas» grises, sin reglas horizontales. Las
# últimas cuatro reglas vienen de revisar los PDF a ojo: un título solo al pie de página con su figura en la
# siguiente, una frase separada de su tabla y una fila de cabecera vacía en las tablas de dos columnas.


def appendix_answers(md: str) -> dict:
    """Pregunta -> respuesta, leidas del apendice del informe maestro (entre START y END)."""
    block = md[md.index(START):md.index(END)]
    parts = re.split(r"^\*\*(.+?)\*\*\s*$", block, flags=re.M)
    return {q.strip(): a.strip() for q, a in zip(parts[1::2], parts[2::2])}


def write_form(wb, sheet: str, rows, answers: dict) -> int:
    """Escribe en el Excel las respuestas del informe; falla si una pregunta no tiene respuesta."""
    ws, n = wb[sheet], 0
    for r in rows:
        q = ws.cell(r, 1).value
        if not q:
            continue
        key = str(q).strip()
        if key not in answers:
            raise SystemExit(f"{sheet}: la pregunta de la fila {r} no esta en el apendice del informe: {key[:60]}")
        ws.cell(r, 2).value = answers[key]
        n += 1
    return n


def absolute_links(md: str) -> str:
    def fix(m):
        bang, txt, url = m.groups()
        if url.startswith(("http", "#", "mailto", "file:")):
            return m.group(0)
        p = re.sub(r"^(\.\./)+", "", url)
        return f"{bang}[{txt}]({REPO_URL}{p}{'?raw=true' if bang else ''})"
    return re.sub(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)", fix, md)


def local_images(md: str, base: str) -> str:
    def fix(m):
        txt, url = m.groups()
        if url.startswith("http"):
            return m.group(0)
        return f"![{txt}]({pathlib.Path(base, url).resolve().as_uri()})"
    md = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", fix, md)
    return absolute_links(md)  # los enlaces normales, al repositorio


def to_pdf(md: str, pdf: str, title: str):
    import markdown
    # «6 321» no debe partirse al final de una línea: espacio que no se rompe entre grupos de miles.
    md = re.sub(r"(?<=\d) (?=\d{3}(?!\d))", " ", md)
    from playwright.sync_api import sync_playwright
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>" \
           + markdown.markdown(md, extensions=["tables", "fenced_code"]) + "</body></html>"
    tmp = pathlib.Path(pdf).with_suffix(".tmp.html"); tmp.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            b = p.chromium.launch(headless=True)
        pg = b.new_page(); pg.goto(tmp.resolve().as_uri()); pg.wait_for_load_state("networkidle")
        pg.pdf(path=pdf, format="A4", margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
               print_background=True, display_header_footer=True, header_template="<span></span>",
               footer_template="<div style='font-size:8px;width:100%;text-align:center;color:#777'>"
                               f"{title}, page <span class='pageNumber'></span> of <span class='totalPages'></span></div>")
        b.close()
    tmp.unlink()


def main() -> int:
    import openpyxl
    assert os.path.exists(XLSX), f"falta la plantilla del formulario: {XLSX}"
    wb = openpyxl.load_workbook(XLSX)
    try:
        import markdown  # noqa: F401  (solo para el PDF)
        pdf_ok = True
    except ImportError:
        pdf_ok = False
        print("AVISO: falta el paquete `markdown`; se escriben .md y .xlsx, NO el .pdf")
    for n, (src, sheet, rows) in REPORTS.items():
        md = open(src, encoding="utf-8").read()
        k = write_form(wb, sheet, rows, appendix_answers(md))
        stem = os.path.join(OUT, f"{TEAM}_track{n}_report")
        open(stem + ".md", "w", encoding="utf-8", newline="\n").write(absolute_links(md))
        exts = [".md"]
        if pdf_ok:
            to_pdf(local_images(md, os.path.dirname(src)), stem + ".pdf", f"MOSAIC RESCUE, Track {n} report")
            exts.append(".pdf")
        for ext in exts:
            if EXTRA_OUT:
                shutil.copy(stem + ext, EXTRA_OUT)
        print(f"track {n}: {k} respuestas del apendice de {src} escritas en el Excel; "
              f"{', '.join(stem + e for e in exts)}")
    wb.save(XLSX)
    if EXTRA_OUT:
        shutil.copy(XLSX, EXTRA_OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
