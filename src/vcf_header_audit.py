#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoria de la cabecera de un VCF. NO lee ninguna variante del paciente:
se detiene en la linea #CHROM.

Los nombres de muestra se redactan por defecto (Regla Dura 1). Usar --show-samples
solo en consola del operador, nunca volcando a un fichero versionado.

Uso:
  python src/vcf_header_audit.py RUTA.vcf.gz [--show-samples]

Resultados de la ejecucion sobre este proyecto: docs/VCF_HEADER.md
"""
import gzip, sys, re, collections

path = sys.argv[1]
show_samples = "--show-samples" in sys.argv

meta, chrom_line = [], None
with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.rstrip("\n")
        if line.startswith("#CHROM"):
            chrom_line = line
            break
        if line.startswith("##"):
            meta.append(line)
        else:                      # linea de datos antes de #CHROM: cabecera malformada
            break

def parse_blocks(tag):
    out = []
    for m in meta:
        if m.startswith("##" + tag + "=<"):
            body = m[len(tag) + 4:-1]
            d = dict(re.findall(r'(\w+)=("[^"]*"|[^,]*)', body))
            out.append({k: v.strip('"') for k, v in d.items()})
    return out

def find(*pats):
    hits = []
    for m in meta:
        for p in pats:
            if re.search(p, m, re.I):
                hits.append(m); break
    return hits

info    = parse_blocks("INFO")
fmt     = parse_blocks("FORMAT")
filt    = parse_blocks("FILTER")
contigs = parse_blocks("contig")

samples = chrom_line.split("\t")[9:] if chrom_line else []

print("=" * 74)
print("AUDITORIA DE CABECERA VCF — no se ha leido ninguna variante")
print("=" * 74)
print(f"  lineas de metadatos : {len(meta)}")
print(f"  version fileformat  : {next((m.split('=',1)[1] for m in meta if m.startswith('##fileformat')), '?')}")

# --- 1. build de referencia ---
print("\n[1] REFERENCIA")
for m in find(r"^##reference", r"^##assembly", r"GRCh|hg19|hg38|b37|b38"):
    print("   ", m[:150])
if contigs:
    c1 = contigs[0]
    print(f"    primer contig: {c1.get('ID')}  length={c1.get('length')}  assembly={c1.get('assembly','-')}")
    names = [c.get("ID", "") for c in contigs]
    estilo = "con prefijo chr" if any(n.startswith("chr") for n in names) else "sin prefijo chr"
    print(f"    contigs: {len(contigs)} ({estilo})")
    # firma de longitud de chr1: GRCh38=248956422, GRCh37=249250621
    for c in contigs:
        if c.get("ID") in ("chr1", "1"):
            L = c.get("length")
            sig = {"248956422": "GRCh38", "249250621": "GRCh37/hg19"}.get(L, "desconocido")
            print(f"    chr1 length={L}  ->  {sig}")
            break

# --- 2. caller / pipeline ---
print("\n[2] CALLER / PIPELINE")
hits = find(r"^##source", r"^##GATK", r"DRAGEN", r"DeepVariant", r"HaplotypeCaller",
            r"strelka", r"freebayes", r"^##CL=", r"commandline")
for m in hits[:12]:
    print("   ", m[:170])
if not hits:
    print("    (ningun campo de origen declarado)")

# --- 3. anotacion previa ---
print("\n[3] ANOTACION PREVIA")
ids = {d.get("ID", "") for d in info}
marcadores = {
    "VEP (CSQ)": "CSQ", "SnpEff (ANN)": "ANN", "SpliceAI": "SpliceAI",
    "CADD": "CADD_phred", "gnomAD": None, "ClinVar": None, "dbNSFP": None,
}
enc = []
for etiqueta, campo in marcadores.items():
    if campo and campo in ids:
        enc.append(etiqueta)
    elif not campo:
        clave = etiqueta.split()[0].lower()
        if any(clave in i.lower() for i in ids) or find(r"" + clave):
            enc.append(etiqueta)
print("    encontrado:", ", ".join(enc) if enc else "NINGUNA — VCF crudo del caller")

# --- 4. FORMAT ---
print("\n[4] CAMPOS FORMAT")
crit = ["GT", "AD", "DP", "GQ", "PL", "AF", "PS", "PGT", "PID"]
pres = {d.get("ID") for d in fmt}
for c in crit:
    marca = "SI " if c in pres else " - "
    desc = next((d.get("Description", "")[:64] for d in fmt if d.get("ID") == c), "")
    print(f"    [{marca}] {c:<5} {desc}")
otros = sorted(pres - set(crit))
if otros:
    print(f"    otros: {', '.join(otros)}")

fase = [c for c in ("PS", "PGT", "PID") if c in pres]
print("\n    >>> FASE FISICA:", ("PRESENTE — " + ", ".join(fase)) if fase else "AUSENTE")

# --- 5. INFO ---
print(f"\n[5] CAMPOS INFO ({len(info)})")
print("   ", ", ".join(sorted(ids)) if ids else "(ninguno)")

# --- 6. muestras ---
print(f"\n[6] MUESTRAS: {len(samples)}")
if show_samples:
    print("   ", samples)
else:
    print("    (nombres redactados — usar --show-samples en consola si hace falta)")

# --- 7. filtros ---
print(f"\n[7] FILTROS ({len(filt)})")
for d in filt:
    print(f"    {d.get('ID','?'):<22} {d.get('Description','')[:70]}")

# --- 8. gVCF? ---
print("\n[8] TIPO")
es_g = bool(find(r"NON_REF", r"GVCFBlock", r"END,Number"))
print("    gVCF" if es_g else "    VCF de variantes (no gVCF)")
print()
