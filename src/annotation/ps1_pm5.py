# -*- coding: utf-8 -*-
"""PS1 y PM5 con la semantica ACMG/AMP correcta, aislados para poder testearlos.

POR QUE EXISTE ESTE FICHERO. La version anterior vivia dentro del script
`src/clinvar_landscape.py`, sin funcion y sin test, y tenia dos defectos que la
propia definicion del criterio prohibe:

  1. Construia el conjunto del residuo a partir de TODO lo codificante. Un
     stop_gained o un frameshift `P`/`LP` en el mismo residuo entraba como
     soporte de PM5. **No lo es.** PS1 y PM5 comparan cambios de AMINOACIDO
     entre variantes MISSENSE; un truncante no es un cambio de aminoacido, es
     la perdida del resto de la proteina, y su mecanismo no dice nada sobre la
     tolerancia de ese residuo a una sustitucion.
     No era un riesgo teorico: de las 84 `P`/`LP` de ClinVar en este gen, **83
     no son missense**. El gen esta dominado por truncantes, asi que el defecto
     habria disparado en cuanto el residuo del caso hubiera tenido una.

  2. Fundia `Pathogenic` con `Likely pathogenic` en un solo cubo `P/LP`. La
     formulacion clasica de PM5 exige que la otra variante este **establecida
     como patogenica**. Aceptar `Likely pathogenic` con la misma fuerza es una
     decision de especificacion, no un default, y para `BUB1B` no existe hoy
     ninguna especificacion VCEP que la autorice. Aqui `LP` se REPORTA aparte y
     no otorga el criterio salvo que se declare explicitamente la
     especificacion aplicable.

QUE NO COMPRUEBA, y se dice en voz alta. PS1 exige, ademas del mismo cambio de
aminoacido, un cambio de NUCLEOTIDO distinto. Los campos que este proyecto
consume de ClinVar y VEP no bastan para comprobarlo de forma fiable, asi que la
funcion devuelve los candidatos de PS1 y **declara** esa comprobacion como
pendiente en vez de darla por hecha.

Ninguna de estas correcciones cambia el veredicto del caso: en el residuo
candidato ClinVar no tiene ninguna `P`/`LP` de ninguna consecuencia, asi que PS1
y PM5 no aplicaban antes y no aplican ahora. Lo que cambia es que ahora la
implementacion coincide con lo que el documento de curacion afirma.
"""
from __future__ import annotations

MISSENSE = "missense_variant"


def is_missense(consequence: str) -> bool:
    """VEP concatena consecuencias con `&`. Basta con que una sea missense."""
    return MISSENSE in (consequence or "")


def significance_tier(clnsig: str):
    """`P` establecida · `LP` · `P_LP` agregado en disputa · None el resto.

    `Conflicting classifications of pathogenicity` NO es soporte de nada: es
    justamente el estado en el que los submisores no se ponen de acuerdo.
    """
    s = " ".join((clnsig or "").lower().replace("|", " ").replace("/", " / ").split())
    if not s or "conflicting" in s:
        return None
    if s.startswith("pathogenic / likely pathogenic"):
        return "P_LP"
    if s.startswith("likely pathogenic"):
        return "LP"
    if s.startswith("pathogenic"):
        return "P"
    return None


def _aa(rec) -> str:
    """`R/W` y `RW` son la misma pareja escrita de dos formas."""
    return str(rec.get("aa") or "").replace("/", "").strip().upper()


def evaluate(same_residue, aa_ref, aa_alt, lp_specification=None):
    """Evalua PS1 y PM5 sobre los registros de ClinVar de UN residuo.

    same_residue : registros del MISMO residuo proteico, cada uno con las
                   claves `con` (consecuencia VEP), `aa` (`R/W` o `RW`) y
                   `sig` (CLNSIG tal como viene de ClinVar).
    aa_ref, aa_alt : el cambio de aminoacido de la variante EVALUADA. Si falta
                   alguno, o son iguales, la variante evaluada no es una
                   missense y ni PS1 ni PM5 son aplicables: se devuelve
                   `applicable=False` en vez de un `no` que parece un resultado.
    lp_specification : nombre de la especificacion que autorice usar
                   `Likely pathogenic` como soporte. Sin ella, los candidatos
                   `LP` se reportan pero NO otorgan el criterio.

    Devuelve un dict; `ps1` y `pm5` son las listas que SI otorgan el criterio.
    """
    change = f"{aa_ref or ''}{aa_alt or ''}".upper().strip()
    applicable = bool(aa_ref and aa_alt and aa_ref.upper() != aa_alt.upper())

    out = {
        "applicable": applicable,
        "ps1": [], "pm5": [],
        "ps1_pending_nucleotide_check": [],
        "pm5_lp_candidates": [],
        "excluded_not_missense": [],
        "excluded_not_pathogenic": [],
        "lp_specification": lp_specification,
        "reason": "",
    }
    if not applicable:
        out["reason"] = ("la variante evaluada no es una missense declarada "
                         "(falta el cambio de aminoacido, o ref y alt coinciden): "
                         "PS1 y PM5 no son aplicables")
        return out

    for r in same_residue:
        tier = significance_tier(r.get("sig"))
        if tier is None:
            continue                      # ni P ni LP: no es soporte de nada
        if not is_missense(r.get("con")):
            # AQUI estaba el defecto: un truncante P/LP en el mismo residuo
            # entraba como PM5. Se registra para poder decir cuantos se
            # excluyeron y por que, en vez de descartarlos en silencio.
            out["excluded_not_missense"].append(r)
            continue
        mismo_cambio = _aa(r) == change
        if tier != "P" and not lp_specification:
            if not mismo_cambio:
                out["pm5_lp_candidates"].append(r)
            else:
                out["excluded_not_pathogenic"].append(r)
            continue
        if mismo_cambio:
            out["ps1_pending_nucleotide_check"].append(r)
        else:
            out["pm5"].append(r)

    # PS1 solo se otorga cuando ademas se ha comprobado el cambio de nucleotido,
    # y esa comprobacion no se puede hacer con los campos disponibles.
    out["ps1"] = []

    partes = []
    if out["pm5"]:
        partes.append(f"PM5 aplicable: {len(out['pm5'])} missense P en el residuo "
                      "con otra sustitucion")
    else:
        partes.append("PM5 NO aplica")
    if out["ps1_pending_nucleotide_check"]:
        partes.append(f"PS1 con {len(out['ps1_pending_nucleotide_check'])} candidato(s), "
                      "pendiente de comprobar el cambio de nucleotido")
    if out["pm5_lp_candidates"]:
        partes.append(f"{len(out['pm5_lp_candidates'])} candidato(s) solo Likely pathogenic, "
                      "que no otorgan PM5 sin una especificacion declarada")
    if out["excluded_not_missense"]:
        partes.append(f"{len(out['excluded_not_missense'])} P/LP excluida(s) por NO ser "
                      "missense (truncantes: no son cambio de aminoacido)")
    out["reason"] = " · ".join(partes)
    return out
