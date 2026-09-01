#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escaner de contenido sensible sobre los ficheros VERSIONADOS.

POR QUE EXISTE
    `.gitignore` no es un control de seguridad: solo evita que algo entre por
    descuido, no comprueba lo que YA entro. Esto revisa lo que git tiene hoy.

DONDE VIVEN LOS VALORES PROHIBIDOS
    En `work/sanitize/forbidden.txt` (gitignored), una cadena por linea. El
    escaner NO lleva dentro la posicion, el aminoacido ni el identificador de
    muestra: si los llevara, el propio control seria la filtracion.
    Sin ese fichero funcionan igualmente los patrones genericos de abajo.

QUE NO HACE
    No revisa el HISTORIAL. Un fichero saneado hoy sigue en los commits
    anteriores. Eso es una decision aparte y deliberada.

Uso:  python src/sanitize_scan.py [--staged]
Sale con codigo 1 si encuentra algo, para poder colgarlo de un hook.
"""
from __future__ import annotations
import io, os, re, sys, subprocess

# Patrones genericos. Cada uno con un nombre legible para el informe.
PATTERNS = [
    ("coordenada genomica",   re.compile(r"\bchr[0-9XYMT]{1,2}[:\-_]\d{4,}\b", re.I)),
    ("HGVS de nucleotido",    re.compile(r"\b[cgmn]\.\d+[+\-*]?\d*[ACGT]?>[ACGT]\b")),
    ("HGVS de proteina",      re.compile(r"\bp\.[A-Z][a-z]{2}\d+[A-Z][a-z]{2}\b")),
    # El token debe estar AISLADO. Sin esto, los colores hexadecimales de las
    # figuras (#5A646D) disparan en cada linea y el informe se vuelve ilegible:
    # es la forma mas comun de que un control asi acabe ignorandose.
    ("cambio de aminoacido",
     re.compile(r"""(?:^|[\s"'>(\[])[ACDEFGHIKLMNPQRSTVWY]\d{2,4}[ACDEFGHIKLMNPQRSTVWY](?=$|[\s"'<),.\];:])""")),
    ("genotipo VCF",          re.compile(r"\b[01]\|[01]:\d|\bGT=[01][/|][01]\b")),
    ("ruta local de usuario", re.compile(r"[A-Za-z]:[\\/]Users[\\/][^\\/\s\"']+|/home/[^/\s\"']+")),
    ("identificador dbSNP",   re.compile(r"\brs\d{6,}\b")),
]

# Extensiones que nunca deberian estar versionadas, pase lo que pase.
FORBIDDEN_EXT = re.compile(r"\.(vcf|bam|cram|bai|crai|tbi|fastq|fq|docx|xlsx)(\.gz)?$", re.I)

SKIP_DIRS = ("work/", "results/", ".git/")
BINARY_EXT = re.compile(r"\.(png|jpg|jpeg|gif|pdf|pyc|zip|gz|woff2?)$", re.I)


def tracked_files(staged: bool):
    cmd = ["git", "diff", "--cached", "--name-only"] if staged else ["git", "ls-files"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f and not f.startswith(SKIP_DIRS)]


def load_forbidden(path="work/sanitize/forbidden.txt"):
    if not os.path.exists(path):
        return []
    out = []
    for l in io.open(path, encoding="utf-8"):
        t = l.strip()
        if not t or t.startswith("#"):
            continue
        # Un token NUMERICO debe casar aislado: "1002" aparece a diario dentro de
        # coordenadas SVG ("1002.0", x="1002") y esos falsos positivos ahogan los
        # hallazgos de verdad. Uno alfanumerico (un ID de muestra) casa siempre.
        rx = (re.compile(r"(?<![\d.\-=\"])" + re.escape(t) + r"(?![\d.\"])") if t.isdigit()
              else re.compile(re.escape(t)))
        out.append((rx, t))
    return out


def scan(staged=False):
    forbidden = load_forbidden()
    hits, checked = [], 0

    for f in tracked_files(staged):
        if FORBIDDEN_EXT.search(f):
            hits.append((f, 0, "EXTENSION PROHIBIDA", f))
            continue
        if BINARY_EXT.search(f) or not os.path.exists(f):
            continue
        checked += 1
        for n, line in enumerate(io.open(f, encoding="utf-8", errors="replace"), 1):
            # Una linea que lleva un identificador bibliografico VERIFICADO es una
            # cita. Las variantes nombradas en una cita son alelos de referencia
            # publicados (p. ej. el I1061T de NPC1), no datos del paciente. La
            # exencion es NARROW a proposito: solo desactiva el patron generico de
            # cambio de aminoacido, y solo en lineas con PMID o DOI. Los valores de
            # la lista prohibida y el resto de patrones siguen aplicandose.
            is_citation = ("PMID" in line and any(c.isdigit() for c in line)) or "DOI 10." in line
            for rx_tok, tok in forbidden:
                if rx_tok.search(line):
                    hits.append((f, n, f"VALOR PROHIBIDO ({tok})", line.strip()[:110]))
            for name, rx in PATTERNS:
                if is_citation and name == "cambio de aminoacido":
                    continue
                m = rx.search(line)
                if m:
                    hits.append((f, n, name, line.strip()[:110]))

    print(f"  ficheros versionados revisados: {checked}")
    print(f"  valores prohibidos cargados   : {len(forbidden)}"
          + ("" if forbidden else "  (sin work/sanitize/forbidden.txt: solo patrones genericos)"))
    if not hits:
        print("\n  LIMPIO — ningun patron sensible en los ficheros versionados.")
        return 0
    print(f"\n  {len(hits)} COINCIDENCIAS:\n")
    for f, n, name, txt in hits:
        print(f"  {f}:{n}")
        print(f"    [{name}] {txt}")
    print("\n  NOTA: esto NO revisa el historial de git.")
    return 1


if __name__ == "__main__":
    sys.exit(scan(staged="--staged" in sys.argv))
