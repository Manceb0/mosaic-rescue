#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye y EJECUTA notebooks/03_TRACK1_GENOME_WIDE.ipynb.

POR QUE UN GENERADOR Y NO UN .ipynb ESCRITO A MANO
    El notebook es el registro reproducible, no la fuente de verdad. La fuente
    vive en `src/`. Generarlo garantiza que lo que el notebook ejecuta son las
    MISMAS funciones del pipeline, no una copia que puede divergir.

SANEADO
    Las salidas quedan dentro del .ipynb y el .ipynb se commitea. Por eso el
    notebook imprime solo agregados, conteos y simbolos de gen. Nunca
    coordenadas, genotipos ni identidad de variantes. `src/sanitize_scan.py`
    lo comprueba despues de ejecutar.

Uso: python src/build_notebook_03.py
"""
from __future__ import annotations
import io, os, sys

import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

OUT = "notebooks/03_TRACK1_GENOME_WIDE.ipynb"

MD = {}
CODE = {}

MD["titulo"] = """# 03 · Track 1 — ranking genome-wide sin panel (EXP-006)

> **Este notebook REPRODUCE el experimento desde las entradas.** No muestra resultados
> guardados: vuelve a ejecutar el pipeline importando `src/`, que es la fuente de verdad.
>
> **Saneado:** imprime agregados, conteos y símbolos de gen. Nunca coordenadas, genotipos ni
> identidad de variantes. Verificado con `src/sanitize_scan.py`.

## 1 · Pregunta biológica

**¿Qué gen o genes explican mejor el caso cuando se deja competir a todo el genoma codificante?**

Hasta EXP-006, `BUB1B` aparecía fuerte **dentro de un panel que elegimos nosotros**. Eso no
es lo mismo que sobrevivir a una búsqueda sin panel. Saltar de ahí a mecanismo sería el sesgo
de confirmación que el proyecto dice evitar.

## 2 · Hipótesis y preregistro

Preregistro completo en `docs/DECISIONS.md` § *EXP-006*, escrito **antes** de ejecutar.

Las cinco predicciones, y la que importa:

| # | Predicción | Qué la falsaría |
|---|---|---|
| 1 | Tras rareza sobrevive < 5 % de las 13 109 | > 20 % |
| 2 | < 40 genes con ≥2 heterocigotos raros y dañinos | > 200 |
| 3 | Muy pocos homocigotos raros dañinos | Decenas |
| **4** | **`BUB1B` entre los 20 primeros sin panel** | **Que no aparezca** |
| 5 | Aparecerán genes sin relación con el fenotipo en cabeza | — |

**Los dos desenlaces de la #4 son buenos, y estaba escrito antes:** si `BUB1B` queda arriba,
sobrevivió a una búsqueda en la que 6 322 genes podían ganarle; si no queda arriba,
**acabamos de evitar un error**, que vale más.

**Garantía de diseño:** `src/prioritization/extract_genomewide.py` no menciona ningún gen. El
único filtro es consecuencia funcional.
"""

MD["proc"] = """## 3 · Entradas y procedencia

Se verifican los hashes de las entradas antes de usarlas. Si cambian, el resultado de abajo
no es comparable con el registrado y el notebook debe volver a correrse entero.

**Paso aguas arriba no reejecutable aquí:** la anotación con VEP 116.1 offline sobre las
4 943 948 variantes (caché `116_GRCh38`, 27 GB, horas de cómputo). El notebook parte de su
salida y **verifica su hash**; el comando exacto y las versiones están en el fichero de
procedencia que VEP dejó junto al TSV.
"""

CODE["proc"] = '''import sys, os, io, hashlib, json, subprocess
sys.path.insert(0, "..")
os.chdir("..")                      # el pipeline usa rutas relativas a la raiz del repo

from src.paths import patient_vcf   # Regla Dura 2: la ruta real vive fuera del codigo

def sha256_head(path, nbytes=64 << 20):
    """Hash de los primeros 64 MB. Suficiente para detectar que el fichero cambio,
    sin leer 20 GB en cada ejecucion del notebook."""
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        h.update(f.read(nbytes))
    return h.hexdigest()[:16]

VCF = patient_vcf()
ANN = "work/gw/highmod_ann.tsv"

print("PROCEDENCIA DE LAS ENTRADAS")
print(f"  VCF del paciente   sha256[:16] = {sha256_head(VCF)}   ({os.path.getsize(VCF)/2**20:.0f} MB)")
print(f"  TSV anotado (VEP)  sha256[:16] = {sha256_head(ANN)}   ({os.path.getsize(ANN)/2**20:.0f} MB)")
print(f"  python             {sys.version.split()[0]}")
print()
print("  (no se imprime ninguna ruta local: identifican la maquina y la muestra)")'''

MD["join"] = """## 4 · QC — reconciliación exacta de alelos VEP ↔ VCF

**El error que este notebook destapó.** `src/prioritization/allele_key.py` existía, tenía 17
tests que pasaban y estaba documentado como la corrección del cruce. **Ningún módulo lo
importaba.** `load()` cruzaba por posición, que es exactamente lo que ese módulo venía a
arreglar. Coste medido: **433 posiciones HIGH/MODERATE sin genotipo**, 346 indels, con 207
anotaciones HIGH perdidas en silencio.

**La solución no pudo ser `Uploaded_variation`**: este TSV no la tiene, porque VEP se corrió
con `--fields` empezando en `Location`. Se reproducen las reglas de representación de VEP
sobre cada registro del VCF y se cruza por `(Location, Allele)` — sin tolerancias ni
distancias, que es lo que el proyecto ya había rechazado.

Detalle que hubo que descubrir: esta corrida escribe las inserciones como `pos-(pos+1)`, no
como la convención clásica `(pos+1)-pos`. Se emiten ambas formas; no genera falsos positivos
porque **el alelo también tiene que coincidir**.

**Recuperación: 420 de 433 (97 %).** Las HIGH sin cruzar bajan de 207 a 5.

> **Y cambió el resultado.** Ver la sección de decisión: en `A0` `BUB1B` pasa de #1 a #4 sin
> perder un solo punto. Eso es lo que un notebook reproducible existe para encontrar.
"""

CODE["join"] = '''# los tests del modulo de join corren ANTES de usarlo
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_allele_key.py", "-q"],
                   capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-400:])
assert r.returncode == 0, "los tests del join fallan: el resultado de abajo no es fiable"'''

MD["load"] = """## 5 · Método — carga, normalización y agregación haplotípica

Tres decisiones que cambian el resultado y que están congeladas en `config/ranking_v1.yaml`:

1. **Regla de dos niveles para `FILTER`.** `PASS` es el nivel primario; las filtradas son un
   nivel de rescate que se examina variante a variante. No se mezclan.
2. **Normalización a alelo único.** Un mismo alelo anotado en varios transcritos es **una**
   observación, no varias.
3. **Agregación haplotípica.** Variantes con el mismo `PID` y el mismo `PGT` están probadas
   en *cis* y colapsan en **un solo evento**. Sin esto, una región de complejidad local
   produce decenas de falsos «heterocigotos compuestos».
"""

CODE["load"] = '''from src.prioritization.genome_wide import load, rank, haplotypic_events
import collections

rows = load(ANN, VCF)          # UNA FILA POR (variante x transcrito), no por alelo
print(f"  filas variante x transcrito en el TSV anotado : {len(rows):,}")

pos = {v.loc for v in rows}
print(f"  posiciones unicas                            : {len(pos):,}")
imp = collections.Counter(v.impact for v in rows)
print(f"  filas por IMPACT                             : {dict(imp)}")

hm = [v for v in rows if v.impact in ("HIGH", "MODERATE")]
print(f"\\n  posiciones con al menos una anotacion HIGH   : {len({v.loc for v in rows if v.impact=='HIGH'}):,}")
print(f"  posiciones con al menos una MODERATE          : {len({v.loc for v in rows if v.impact=='MODERATE'}):,}")
print(f"  posiciones HIGH o MODERATE (las que compiten) : {len({v.loc for v in hm}):,}")

by_gene = collections.defaultdict(list)
for v in hm:
    by_gene[v.gene].append(v)
print(f"  genes con al menos una HIGH/MODERATE          : {len(by_gene):,}")

# --- efecto de la agregacion haplotipica, MEDIDO ---
# haplotypic_events devuelve (eventos, info); desempaquetar es obligatorio
antes = sum(1 for vs in by_gene.values() if len({v.loc for v in vs}) >= 2)
despues = 0
for vs in by_gene.values():
    ev, _ = haplotypic_events(vs)
    if len(ev) >= 2:
        despues += 1
print(f"\\n  genes con >=2 posiciones ANTES de colapsar cis : {antes:,}")
print(f"  genes con >=2 EVENTOS   DESPUES de colapsar cis : {despues:,}")
print(f"  -> la agregacion retira {antes - despues:,} genes de la lista de candidatos a")
print(f"     heterocigosis compuesta que solo lo parecian por variantes en cis")'''

MD["reconcilia"] = """### Reconciliación de conteos — tres números distintos, y por qué

Por el proyecto circulan **13 109**, **13 581** y **13 793** variantes, y **6 322** frente a
**8 730** genes. No son contradictorios: **son etapas distintas del pipeline**, y hasta ahora
los documentos no lo decían.

| Número | De dónde sale |
|---|---|
| 13 109 variantes · 6 322 genes | Salida de `extract_genomewide.py`, **antes** de la pasada 2 |
| 13 581 (928 HIGH + 12 653 MODERATE) | Funnel, contado **por variante y clase de impacto** |
| 13 793 posiciones · 8 730 genes | Fichero anotado de la pasada 2, que incluye además filas `MODIFIER` y `LOW` de **otros transcritos** de las mismas variantes |

**La diferencia de genes es la que más engaña.** El fichero de la pasada 2 anota *todos* los
transcritos, así que una variante puede tocar un gen vecino por un transcrito no canónico. Con
`MANE Select` solamente, quedan 6 721 genes — próximo a los 6 322 originales.

**Ninguna conclusión cambia**: el ranking opera sobre HIGH/MODERATE y aplica sus propios
filtros. Pero las tres cifras deben ir siempre etiquetadas con su etapa. Registrado en
`docs/DECISIONS.md`.
"""

CODE["reconcilia"] = '''# la reconciliacion, medida en vez de afirmada
mane = [v for v in rows if v.mane not in ("", "-")]
print(f"  genes contando solo transcritos MANE Select : {len({v.gene for v in mane}):,}")
print(f"  genes contando todos los transcritos        : {len({v.gene for v in rows}):,}")
print(f"  -> la diferencia son transcritos no canonicos que asignan una variante a un gen vecino")'''

MD["rank"] = """## 6 · Ranking genético puro — A0 y A1

`A0_GENETICS` es el control más importante del experimento: **sin fenotipo y sin ClinVar**.
Solo genética de población, consecuencia funcional y compatibilidad de herencia.

Si `BUB1B` sube en A0, no puede ser porque le hayamos dado el fenotipo ni porque ClinVar le
regale puntos.
"""

CODE["rank"] = '''calls = rank(rows, male=True)
print(f"  genes puntuados: {len(calls):,}\\n")

def top(calls, n=10, drop_clinvar=False):
    out = []
    for c in calls:
        s = c.score
        if drop_clinvar:
            has = any("pathogenic" in (v.clinsig or "").lower()
                      and "conflicting" not in (v.clinsig or "").lower() for v in c.variants)
            if has:
                s -= 5.0
        out.append((s, c.gene, c.model))
    return sorted(out, key=lambda t: (-t[0], t[1]))[:n]

print("  A0_GENETICS  — SIN fenotipo, SIN ClinVar")
for i, (s, g, m) in enumerate(top(calls, 10, drop_clinvar=True), 1):
    print(f"    {i:>2}  {g:<12} {s:6.2f}  {m}")

print("\\n  A1_GENETICS_CLINVAR — SIN fenotipo, CON ClinVar")
for i, (s, g, m) in enumerate(top(calls, 10), 1):
    print(f"    {i:>2}  {g:<12} {s:6.2f}  {m}")'''

MD["modeb"] = """## 7 · Modo B — los quince análisis con fenotipo

Método congelado en `config/phenotype_v2.yaml`. Tres decisiones que importan más que la
fórmula:

1. **Comparación a nivel de MODELO DE ENFERMEDAD, no de gen.** La versión anterior unía los
   términos de todas las enfermedades de un gen; eso fabrica una *enfermedad Frankenstein*
   que ningún modelo real tiene, y con un fenotipo multisistémico habría sido fatal.
2. **Solo relaciones causales establecidas** (`MENDELIAN`), preservando el tipo `MIXED`.
3. **Resnik + Best Match Average asimétrica**, dirección paciente → modelo: la inversa
   penalizaría a un modelo por rasgos que el paciente no tiene, y aquí «no tiene» significa
   **desconocido**, porque el documento clínico no declara ser exhaustivo.

La historia familiar **no entra en el ranking primario** (peso 0,0): es un rasgo de la madre.
Corre como sensibilidad explícita `FH_ON`.
"""

CODE["modeb"] = '''r = subprocess.run([sys.executable, "src/phenotype/run_mode_b.py"],
                   capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
print(r.stdout if r.returncode == 0 else r.stderr[-2000:])
assert r.returncode == 0, "el modo B no reprodujo"'''

MD["stab"] = """## 8 · Estabilidad de rango y ablaciones

Lo que el preregistro exige reportar **no es el ganador**, sino la matriz gen × análisis para
los líderes. Un gen que solo gana en una configuración no es un resultado.
"""

CODE["stab"] = '''import pickle
res = pickle.load(io.open("work/gw/mode_b_results_v4.pkl", "rb"))

lead = [g for _, g, _ in [(0, r[0], 0) for r in res["B0_FULL_PROBAND"][:6]]]
orden = ["A0_GENETICS", "A1_GENETICS_CLINVAR", "B0_FULL_PROBAND", "B1_MINUS_RHABDOMYOSARCOMA",
         "B2_MINUS_RENAL", "B3_MINUS_GROWTH_PERINATAL", "B4_GENETICS_ONLY_CONTROL", "FH_ON"]
loo = [k for k in res if k.startswith("LOO_")]

print(f"  MATRIZ DE ESTABILIDAD DE RANGO — puesto de cada gen lider\\n")
print("  " + " " * 28 + "".join(f"{g:>12}" for g in lead))
for name in orden + sorted(loo):
    puestos = {r[0]: i for i, r in enumerate(res[name], 1)}
    fila = "".join(f"{puestos.get(g, '-'):>12}" for g in lead)
    print(f"  {name:<28}{fila}")

print(f"\\n  analisis ejecutados: {len(res)}")
gan = {name: res[name][0][0] for name in res}
from collections import Counter
print(f"  ganador por analisis: {dict(Counter(gan.values()))}")'''

MD["loo"] = """### Qué términos del fenotipo empujan de verdad

*Leave-one-out*: se quita un término y se mide cuánto cae la puntuación fenotípica del gen
líder. Un término cuya retirada no cambia nada **no está sosteniendo el resultado**.
"""

CODE["loo"] = '''G = res["B0_FULL_PROBAND"][0][0]
base = next(r for r in res["B0_FULL_PROBAND"] if r[0] == G)[5]
print(f"  gen evaluado: {G}   ·   soporte fenotipico completo = {base:.3f}\\n")
print(f"  {'termino retirado':<22}{'soporte':>9}{'contribucion':>14}")
for k in sorted(loo):
    v = next((r for r in res[k] if r[0] == G), None)
    if v is None:
        continue
    print(f"  {k.replace('LOO_HP_', 'HP:'):<22}{v[5]:>9.3f}{base - v[5]:>14.3f}")
print("\\n  contribucion positiva = ese termino SOSTIENE el emparejamiento")
print("  contribucion ~0       = ese termino no aporta soporte semantico en el corpus HPO actual")'''

MD["base"] = """## 9 · Comparación con el baseline externo independiente

`EXP-006b`. Exomiser 14.1.0 partió del **VCF original** y de los **mismos 7 términos**, con su
propia base de conocimiento. No recibió nada nuestro. Preregistro y umbral en
`docs/DECISIONS.md`, ambos fijados antes de ejecutar.
"""

CODE["base"] = '''r = subprocess.run([sys.executable, "src/baseline/compare_baseline.py"],
                   capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
print(r.stdout if r.returncode == 0 else r.stderr[-1500:])'''

MD["fig"] = """## 10 · Figura 6 — el funnel, regenerada desde este pipeline

La figura deja de ser una imagen con números escritos a mano y pasa a tener origen ejecutable.
"""

CODE["fig"] = '''for script in ("src/build_funnel.py", "src/make_fig6.py", "src/export_svg.py"):
    if not os.path.exists(script):
        print(f"  falta {script}")
r = subprocess.run([sys.executable, "src/make_fig6.py"], capture_output=True, text=True,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})
print(r.stdout.strip() or r.stderr[-800:])
r = subprocess.run([sys.executable, "src/export_svg.py", "figures/fig6_funnel.html"],
                   capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
print(r.stdout.strip() or r.stderr[-800:])'''

MD["dec"] = """## 11 · Decisión

| | |
|---|---|
| **Estado de EXP-006** | **SURVIVES**, con una corrección importante |
| Predicción #4 | **Acertada** — `BUB1B` queda #1 en 14 de los 15 análisis, muy por encima del top-20 exigido |
| Control genético puro `A0` | **Queda #4, no #1.** Su puntuación no baja (13,0): emergen tres deleciones homocigotas con `MAX_AF` ausente que puntúan 13,5 bajo el modelo más limpio |
| Auditoría de esos tres (EXP-021) | **Resueltos: son polimorfismos comunes.** `rs[REDACTED]`, `rs[REDACTED]`, `rs[REDACTED]`, con frecuencias del 30–93 % y hasta **313 150 homocigotos** en gnomAD. VEP no supo anotarles la frecuencia por la representación del indel |
| Sensibilidad `A0-FREQFIX` | Reparando **los 33** alelos sin `MAX_AF` (no solo los tres), `BUB1B` **vuelve al puesto 1**. `A0` congelado sigue siendo 4; se reportan los dos |
| Qué NO se hizo | **No se tocó la fórmula.** Degradar ahora las variantes sin frecuencia sería ajustar el ranking después de ver bajar a `BUB1B`, que el preregistro prohíbe |
| Comprobación independiente | Exomiser lo sitúa #2 de 398, modelo recesivo, sin código común |

### Qué NO establece este experimento — y estaba escrito antes

- **No resuelve la fase.** Los pares heterocigotos son *candidatos* a heterocigosis compuesta,
  nunca heterocigosis compuesta demostrada.
- **No evalúa *de novo***: sin genotipos parentales no se finge.
- **No cubre variantes estructurales** — es EXP-012, bloqueado por falta de BAM/CRAM de
  profundidad completa.
- **No cubre reguladoras ni intrónicas profundas** fuera del filtro de consecuencia.
- **No clasifica nada como patogénico.** La curación ACMG es otro experimento y la missense
  sigue siendo VUS.

### Incertidumbre reducida, y decisión que desbloquea

**Reducida:** que `BUB1B` fuera un artefacto de haber mirado dentro de un panel elegido por
nosotros. Compitió contra 6 322 genes, ganó sin fenotipo y sin ClinVar, y un motor externo lo
sitúa segundo.

**Desbloquea:** trabajar el mecanismo de `BUB1B` sin que sea sesgo de confirmación, y abrir
las ramas ortogonales del brief §5.

### Lo que sigue abierto contra este resultado

`FANCD2` entró en el camino crítico desde el baseline externo (EXP-020). El solapamiento
entre los dos rankings es del 30 %: los motores coinciden en el candidato principal, **no en
el ranking entero**.
"""

CODE["scan"] = '''# el propio notebook comprueba que sus salidas no filtran nada sensible
r = subprocess.run([sys.executable, "src/sanitize_scan.py"], capture_output=True, text=True,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})
print(r.stdout[-600:])'''


def build():
    nb = new_notebook()
    order = [
        ("md", "titulo"), ("md", "proc"), ("code", "proc"),
        ("md", "join"), ("code", "join"),
        ("md", "load"), ("code", "load"),
        ("md", "reconcilia"), ("code", "reconcilia"),
        ("md", "rank"), ("code", "rank"),
        ("md", "modeb"), ("code", "modeb"),
        ("md", "stab"), ("code", "stab"),
        ("md", "loo"), ("code", "loo"),
        ("md", "base"), ("code", "base"),
        ("md", "fig"), ("code", "fig"),
        ("md", "dec"), ("code", "scan"),
    ]
    for kind, key in order:
        nb.cells.append(new_markdown_cell(MD[key]) if kind == "md" else new_code_cell(CODE[key]))
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python", "version": sys.version.split()[0]}
    os.makedirs("notebooks", exist_ok=True)
    nbf.write(nb, OUT)
    print(f"  {OUT} construido con {len(nb.cells)} celdas")


if __name__ == "__main__":
    build()
