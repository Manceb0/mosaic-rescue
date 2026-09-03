#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One command a reviewer can run without any patient data.

    python src/verify.py

WHY THIS IS A PYTHON SCRIPT AND NOT ONLY A MAKEFILE
    `make` is not present on a default Windows install, which is where this
    analysis was produced. A reproduction entry point that only works on the
    maintainer's platform is not an entry point. The Makefile is kept as a thin
    wrapper for reviewers who prefer it.

WHAT THIS CHECKS, AND WHAT IT CANNOT
    Checks: unit tests, that every figure and notebook module imports, that the
    Track 2 evidence matrix is complete and every non-empty cell carries a
    source, and that both project controls run.

    Cannot: rebuild figures or notebooks. Those need the local dataset declared
    in config/paths.yaml, which is gitignored and never distributed. Use
    `python src/figures/render_all.py` and `python src/nb/build_all.py` on a
    machine that has it.

    One honest caveat: the privacy scanner reads its list of case-specific
    forbidden values from work/sanitize/forbidden.txt, which is also gitignored.
    Where that file is absent, the scanner still checks structural patterns
    (coordinates, HGVS, genotypes, local user paths) but not the case values.
    The report below says which of the two happened.
"""
from __future__ import annotations
import io, os, subprocess, sys, time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Los modulos NO se listan a mano. Una lista escrita a mano se queda corta en
# silencio: la anterior decia "todos los modulos de figuras y notebooks" y
# omitia los ocho generadores src/nb/nb00..nb07, es decir, justo el codigo que
# construye los notebooks. Un control que afirma cubrir mas de lo que cubre es
# peor que no tenerlo, porque da permiso para no mirar.
PKGS = ("src/figures", "src/nb", "src/structure")


def discover():
    """Todo modulo importable bajo los paquetes de arriba, en orden estable."""
    out = []
    for pkg in PKGS:
        for fn in sorted(os.listdir(os.path.join(ROOT, pkg))):
            if fn.endswith(".py") and fn != "__init__.py":
                out.append(pkg.replace("/", ".") + "." + fn[:-3])
    return out


def run(cmd, env=None):
    e = dict(os.environ)
    e.setdefault("PYTHONIOENCODING", "utf-8")
    if env:
        e.update(env)
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=e,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def tests():
    # PYTEST_DISABLE_PLUGIN_AUTOLOAD: unrelated packages in a shared environment
    # can ship pytest plugins that fail to import against this pinned NumPy.
    # The project's own tests do not need any plugin.
    code, out = run([sys.executable, "-m", "pytest", "tests/", "-q"],
                    {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    last = [l for l in out.strip().splitlines() if l.strip()]
    return code == 0, last[-1] if last else "no output"


def imports():
    import importlib
    sys.path.insert(0, ROOT)
    mods = discover()
    for m in mods:
        importlib.import_module(m)
    n_nb = sum(1 for m in mods if ".nb.nb" in m)
    return True, (f"{len(mods)} modules import cleanly "
                  f"({n_nb} notebook generators, discovered not hand-listed)")


def evidence_matrix():
    sys.path.insert(0, ROOT)
    from src.figures.fig07_evidence import read, DIMS
    ev = read()
    bridges = sorted({int(e["puente"]) for e in ev})
    if len(ev) != len(bridges) * len(DIMS):
        return False, f"matrix incomplete: {len(ev)} rows for {len(bridges)} bridges"
    orphan = [(e["puente"], e["dimension"]) for e in ev
              if e["clase"] != "ABSENT" and not e["fuente"].strip()]
    if orphan:
        return False, f"cells without a source: {orphan}"
    sources = len({e["fuente"] for e in ev if e["fuente"].strip()})
    return True, (f"{len(ev)} cells over {len(bridges)} bridges, {sources} sources, "
                  "every non-absent cell sourced")


def candidate_matrix():
    """La tabla de candidatos, con las mismas exigencias que la de evidencia.

    Esta comprobacion se anadio despues de que una afirmacion falsa sobre
    evidencia farmacologica entrara en el fichero y pasara con todo en verde:
    verify.py solo miraba track2_evidence.tsv. Un control que no cubre el
    artefacto nuevo no protege del error nuevo.

    Y se AMPLIO despues de una segunda revision: solo exigia identificador en
    'evidencia directa' y 'evidencia indirecta'. Una afirmacion falsa metida en
    'evidencia contraria', 'exposicion' o 'seguridad' seguia pasando. La
    contraevidencia es precisamente donde este proyecto se juega la
    credibilidad, asi que ahora se valida igual. Tambien se comprueba que el
    recuento declarado en la cabecera coincida con las filas: la cabecera llego
    a decir "3 intervenciones y 2 controles" con tres controles dentro.
    """
    TAB = chr(9)
    raw = io.open(os.path.join(ROOT, "research/track2_candidates.tsv"),
                  encoding="utf-8").read().split(chr(10))
    head_txt = chr(10).join(l for l in raw if l.startswith("#"))
    rows = [l.split(TAB) for l in raw if not l.startswith("#") and l.strip()]
    hdr, body = rows[0], rows[1:]

    ragged = [r[0] for r in body if len(r) != len(hdr)]
    if ragged:
        return False, f"rows with the wrong column count: {ragged}"

    ROLES = {"SENTINEL", "ALLELE", "ADVERSARIAL", "CONTROL"}
    bad = [r[0] for r in body if r[1] not in ROLES]
    if bad:
        return False, f"unknown role in: {bad}"

    # Toda columna que AFIRME algo sobre el mundo necesita identificador. No
    # solo las dos de evidencia a favor.
    CLAIM_COLS = ("evidencia directa", "evidencia indirecta",
                  "evidencia contraria", "exposicion", "seguridad")
    # Formas aceptadas de procedencia. La ultima es la importante: se permite
    # declarar un hueco, pero no dejarlo implicito. O citas, o dices que no lo
    # has verificado; lo que no puedes es afirmar sin ninguna de las dos cosas.
    ID = ("DOI ", "PMID ", "PMC", "etiqueta MIPLYFFA",     # literatura y etiqueta
          "notebooks/", "track2_evidence.tsv",             # artefacto interno
          "no verificado")                                 # hueco DECLARADO
    # Vocabulario cerrado de "aqui no hay nada que citar". Cualquier otra cosa
    # es una afirmacion y necesita fuente.
    EMPTY = ("n/a", "ninguno", "ninguna", "no aplica", "")
    unsourced = []
    for r in body:
        for col in CLAIM_COLS:
            v = r[hdr.index(col)].strip()
            if v.lower() in EMPTY:
                continue
            if v.lower().startswith(("ninguna", "ninguno")):
                continue      # "Ninguna en BUB1B. Ninguna en MVA" es una ausencia declarada
            if not any(t in v for t in ID):
                unsourced.append(f"{r[0]}/{col}")
    if unsourced:
        return False, f"claims without an identifier: {unsourced}"

    roles = {}
    for r in body:
        roles[r[1]] = roles.get(r[1], 0) + 1
    n_ctl = roles.get("CONTROL", 0)
    n_int = sum(v for k, v in roles.items() if k != "CONTROL")

    # La cabecera no puede contradecir a las filas.
    import re as _re
    m = _re.search(r"(\d+)\s+intervenciones\s+y\s+(\d+)\s+controles", head_txt)
    if not m:
        return False, "the header does not declare how many interventions and controls it has"
    d_int, d_ctl = int(m.group(1)), int(m.group(2))
    if (d_int, d_ctl) != (n_int, n_ctl):
        return False, (f"header says {d_int} interventions and {d_ctl} controls, "
                       f"rows contain {n_int} and {n_ctl}")

    return True, (f"{n_int} interventions and {n_ctl} controls, matching the header, "
                  f"roles valid, every claim in {len(CLAIM_COLS)} columns carries an identifier")


def published_counts():
    """Los conteos publicados coinciden con los notebooks ejecutados.

    README y research/EXPERIMENT_REGISTRY.md publican un par de cifras
    "N figuras, M cientificas". Ese par ya se desincronizo dos veces (26/21, y
    despues 27/22 al anadir la cartera de Track 2), y nadie lo noto porque
    ningun control lo miraba. Ahora no se escribe a mano: se recalcula desde los
    notebooks ejecutados y se compara con lo que dicen los documentos.
    """
    sys.path.insert(0, ROOT)
    import glob
    from src.nb.nbutil import verify as nbverify
    figs = sci = errs = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "notebooks", "*.ipynb"))):
        e, f, s_, _ok = nbverify(p)
        errs += e; figs += f; sci += s_
    if errs:
        return False, f"{errs} error output(s) inside the executed notebooks"
    bad = []
    for doc in ("README.md", "research/EXPERIMENT_REGISTRY.md"):
        txt = io.open(os.path.join(ROOT, doc), encoding="utf-8").read()
        if str(figs) not in txt or str(sci) not in txt:
            bad.append(doc)
    if bad:
        return False, f"{figs} figures / {sci} scientific, not stated in: {bad}"
    return True, (f"{figs} figures, {sci} scientific, 0 errors; "
                  "README and the registry agree with the notebooks")


def contradiction_count():
    """El numero de contradicciones que se publica coincide con las que hay.

    Tres documentos distintos decian 14, 12 y 12 cuando eran 13. Ninguno estaba
    mintiendo a proposito: simplemente nadie recalcula un numero al anadir una
    fila. Por eso lo cuenta una maquina.
    """
    import re
    s = io.open(os.path.join(ROOT, "research/contradictions.md"), encoding="utf-8").read()
    main = s.split("## Contradicciones que a")[0]
    n = len(re.findall(r"^\| \*\*(C\d+)\*\*", main, re.M))
    bad = []
    for doc in ("docs/SCALABILITY.md", "research/evidence_registry.md", "AGENTS.md"):
        t = io.open(os.path.join(ROOT, doc), encoding="utf-8").read()
        for m in re.finditer(r"(\d+)\s+(?:entradas|contradicciones)", t):
            if int(m.group(1)) != n:
                bad.append(f"{doc}: '{m.group(0)}'")
    if bad:
        return False, f"{n} contradictions recorded, but: {bad}"
    return True, f"{n} contradictions, and every document that states a count agrees"


def privacy_scan():
    code, out = run([sys.executable, "src/sanitize_scan.py"])
    has_list = "valores prohibidos cargados   : 0" not in out
    verdict = "clean" if "LIMPIO" in out else "FINDINGS"
    scope = "structural patterns + case values" if has_list else "structural patterns only"
    return code == 0 and "LIMPIO" in out, f"{verdict} ({scope})"


def stale_claims():
    code, out = run([sys.executable, "src/audit_stale_claims.py"])
    line = next((l.strip() for l in out.splitlines() if "TOTAL" in l), "no summary")
    return code == 0, line


CHECKS = [("unit tests", tests),
          ("module imports", imports),
          ("published counts", published_counts),
          ("Track 2 evidence matrix", evidence_matrix),
          ("Track 2 candidate matrix", candidate_matrix),
          ("contradiction count", contradiction_count),
          ("privacy scan", privacy_scan),
          ("superseded-claim audit", stale_claims)]


def main() -> int:
    print("MOSAIC RESCUE, verification without patient data\n")
    failures = 0
    for name, fn in CHECKS:
        t0 = time.time()
        try:
            ok, detail = fn()
        except Exception as exc:
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        failures += not ok
        print(f"  [{'ok  ' if ok else 'FAIL'}] {name:<26}{time.time() - t0:5.1f}s  {detail}")

    print()
    if failures:
        print(f"  {failures} check(s) failed")
    else:
        print("  all checks passed. Figures and notebooks need the local dataset:")
        print("      python src/figures/render_all.py")
        print("      python src/nb/build_all.py")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
