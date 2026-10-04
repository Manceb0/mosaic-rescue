#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Empaqueta los informes de entrega (Markdown + PDF) con el formulario de metodos dentro.

    python src/submission/export_reports.py            # dependencias: openpyxl, markdown, playwright (Edge o Chromium)

POR QUE
    La plataforma de Track 1 solo tiene dos casillas: el CSV y UN informe (PDF o Markdown). La
    plantilla oficial de metodos (Excel) se pide "para organizar" ese informe, asi que sus
    respuestas tienen que viajar DENTRO del informe o el jurado no las ve. Este script:

    1. lee las respuestas del Excel rellenado (work/submission/subir/<equipo>_methods_description.xlsx)
       y las inserta como apendice en reports/TRACK{1,2}_REPORT.md, entre marcadores, de forma
       idempotente;
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

CSS = """body{font-family:'Segoe UI',Arial,sans-serif;font-size:10.5pt;line-height:1.45;color:#1b1b1b;max-width:180mm;margin:auto}
h1{font-size:20pt;margin-bottom:2pt}h2{font-size:14pt;border-bottom:1px solid #ccc;padding-bottom:2pt;margin-top:18pt}h3{font-size:12pt}
table{border-collapse:collapse;width:100%;font-size:9pt;margin:8pt 0}th,td{border:1px solid #bbb;padding:3pt 5pt;vertical-align:top}th{background:#f1f1f1}
code{font-family:Consolas,monospace;font-size:9pt;background:#f4f4f4;padding:0 2pt}pre{background:#f4f4f4;padding:6pt;font-size:8.5pt;white-space:pre-wrap}
blockquote{border-left:3px solid #999;margin:6pt 0;padding:2pt 8pt;color:#444}img{max-width:100%;display:block;margin:8pt auto}a{color:#1a4f8b}
.q{font-weight:600;margin-top:10pt}"""


def form_appendix(sheet: str, rows) -> str:
    import openpyxl
    ws = openpyxl.load_workbook(XLSX)[sheet]
    out = [START, "", "## Appendix · Methods description (official hackathon form)", "",
           "Answers to the organisers' methods-description template, reproduced here because the "
           "submission accepts a single report file.", ""]
    for r in rows:
        q, a = ws.cell(r, 1).value, ws.cell(r, 2).value
        if not q:
            continue
        out += [f"**{str(q).strip()}**", "", str(a or "_(not answered)_").strip(), ""]
    return "\n".join(out + [END])


def upsert(path: str, block: str) -> str:
    s = open(path, encoding="utf-8").read()
    if START in s:
        s = s[:s.index(START)] + block + s[s.index(END) + len(END):]
    else:
        s = s.rstrip() + "\n\n" + block + "\n"
    open(path, "w", encoding="utf-8").write(s)
    return s


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
                               f"{title} · <span class='pageNumber'></span>/<span class='totalPages'></span></div>")
        b.close()
    tmp.unlink()


def main() -> int:
    assert os.path.exists(XLSX), f"falta el formulario rellenado: {XLSX}"
    for n, (src, sheet, rows) in REPORTS.items():
        md = upsert(src, form_appendix(sheet, rows))
        stem = os.path.join(OUT, f"{TEAM}_track{n}_report")
        open(stem + ".md", "w", encoding="utf-8", newline="\n").write(absolute_links(md))
        to_pdf(local_images(md, os.path.dirname(src)), stem + ".pdf", f"MOSAIC RESCUE · Track {n} report")
        for ext in (".md", ".pdf"):
            if EXTRA_OUT:
                shutil.copy(stem + ext, EXTRA_OUT)
        print(f"track {n}: apendice del formulario insertado en {src}; {stem}.md y .pdf escritos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
