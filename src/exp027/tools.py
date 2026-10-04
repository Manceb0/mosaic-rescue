"""Órdenes exactas de herramientas y validación de sus salidas (Amendments 3-4; C3).

Solo construye y valida comandos; no descarga nada. Reglas que se hacen cumplir aquí:
sin --pedigree en la inferencia, sin --reference externo en phase_common, --seed 42 explícito,
mapa genético obligatorio, scaffold MAF ≥ 0.1 %, ligate con solape real (L_isec > 0) y salidas
validadas por contenido, nunca por código de salida.
"""
from __future__ import annotations

import re
from pathlib import Path

SHAPEIT5_IMAGE = "quay.io/biocontainers/shapeit5@sha256:cf3c988c2da4beda759f03300f767495944e25984a7dfa042f806c3113c6e450"
BCFTOOLS_IMAGE = "quay.io/biocontainers/bcftools@sha256:969314d56b9131683917cc5801734891a9af130daf7a0fb902b7707060b06027"
SEED = "42"
SCAFFOLD_MAF = "0.001"
ANALYTIC_MAF = 0.01
MPILEUP_ARGS = ("-q", "20", "-Q", "20", "--ff", "UNMAP,SECONDARY,QCFAIL,DUP,SUPPLEMENTARY",
                "-d", "10000", "-a", "FORMAT/AD")


def region_str(chrom: str, start: int, end: int) -> str:
    return f"{chrom}:{int(start)}-{int(end)}"


def phase_common_cmd(input_bcf: str, region: str, genetic_map: str, output: str) -> list[str]:
    if not genetic_map:
        raise ValueError("mapa genético obligatorio: no se permite el valor por defecto 1 cM/Mb")
    return ["SHAPEIT5_phase_common", "--input", input_bcf, "--region", region,
            "--map", genetic_map, "--filter-maf", SCAFFOLD_MAF, "--seed", SEED, "--output", output]


def phase_rare_cmd(input_bcf: str, input_region: str, scaffold: str, scaffold_region: str,
                   genetic_map: str, output: str) -> list[str]:
    if not genetic_map:
        raise ValueError("mapa genético obligatorio")
    # phase_rare no acepta --log (C3).
    return ["SHAPEIT5_phase_rare", "--input", input_bcf, "--input-region", input_region,
            "--scaffold", scaffold, "--scaffold-region", scaffold_region, "--map", genetic_map,
            "--seed", SEED, "--output", output]


def ligate_cmd(list_file: str, output: str) -> list[str]:
    return ["SHAPEIT5_ligate", "--input", list_file, "--output", output]


def switch_cmd(validation: str, estimation: str, pedigree: str, region: str, prefix: str) -> list[str]:
    """SER contra verdad mendeliana: -P con genotipos de trio NO faseados en --validation."""
    return ["SHAPEIT5_switch", "--validation", validation, "--estimation", estimation,
            "--pedigree", pedigree, "--region", region, "--output", prefix]


def cohort_subset_cmd(input_bcf: str, samples_file: str, output: str) -> list[str]:
    """Genotipos de la cohorte de conditioning sola (C_target: sin el objetivo ni su familia)."""
    return ["bcftools", "view", "-S", samples_file, "-Ob", "-o", output, input_bcf]


def cohort_tags_cmd(cohort_bcf: str, output: str) -> list[str]:
    """AC, AN y MAF calculados SOLO en C_target (Amendment 7): el propio objetivo no decide si un
    marcador entra en el scaffold ni en A1. Benchmark: C_target; paciente: los 2.504."""
    return ["bcftools", "+fill-tags", cohort_bcf, "-Ob", "-o", output, "--", "-t", "AC,AN,MAF"]


def annotate_cohort_tags_cmd(joint_bcf: str, tags_bcf: str, output: str) -> list[str]:
    """Copia a la entrada conjunta (C_target ∪ {objetivo}) los AC/AN/MAF de la cohorte, de modo que
    --filter-maf de phase_common y el filtro analítico usen la MAF de C_target."""
    return ["bcftools", "annotate", "-a", tags_bcf, "-c", "INFO/AC,INFO/AN,INFO/MAF",
            "-Ob", "-o", output, joint_bcf]


def analytic_subset_cmd(input_bcf: str, output: str) -> list[str]:
    """Marcadores analíticos (MAF ≥ 1 % de C_target, ya anotada en INFO/MAF), p. ej. antes de medir
    el SER común que adjudica A1. No recalcula la MAF con el objetivo dentro."""
    return ["bcftools", "view", "-i", f"INFO/MAF>={ANALYTIC_MAF}", "-Ob", "-o", output, input_bcf]


def exclude_regions_cmd(input_bcf: str, bed: str, output: str) -> list[str]:
    """Retira los registros cuyo span [POS, POS + len(REF) − 1] toca el BED (Amendment 8 r2-r3).

    `--targets-overlap 1` (record) usa el span del registro, no solo POS. El orquestador comprueba
    después, en Python, que ningún sitio enmascarado haya sobrevivido.
    """
    return ["bcftools", "view", "-T", f"^{bed}", "--targets-overlap", "1", "-Ob", "-o", output,
            input_bcf]


def mpileup_cmd(reference: str, sites: str, alignment: str, output: str) -> list[str]:
    """Extractor único de conteos (Amendment 4 regla 3), idéntico para 1000G y el caso."""
    return ["bcftools", "mpileup", "-f", reference, "-R", sites, *MPILEUP_ARGS,
            "-Ob", "-o", output, alignment]


def assert_frozen(cmd: list[str]) -> None:
    """Falla si un comando viola una regla congelada."""
    tool = cmd[0]
    if tool.startswith("SHAPEIT5_phase") and "--pedigree" in cmd:
        raise ValueError("--pedigree prohibido en la inferencia")
    if tool == "SHAPEIT5_phase_common" and "--reference" in cmd:
        raise ValueError("phase_common sin --reference externo")
    if tool.startswith("SHAPEIT5_phase") and cmd[cmd.index("--seed") + 1] != SEED:
        raise ValueError("--seed debe ser 42")
    if tool == "bcftools" and len(cmd) > 1 and cmd[1] == "mpileup":
        if "-x" in cmd:
            raise ValueError("la detección de solape de mates debe estar activada (sin -x)")


def docker_cmd(image: str, mount: str, cmd: list[str]) -> list[str]:
    assert_frozen(cmd)
    return ["docker", "run", "--rm", "-v", f"{mount}:/data", image, *cmd]


def require_output(path: str | Path) -> Path:
    """Valida por contenido: la herramienta puede devolver 0 sin haber escrito nada (C3)."""
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        raise RuntimeError(f"salida ausente o vacía: {p}")
    return p


_LISEC = re.compile(r"L_isec=(\d+)")


def ligate_overlaps(log_text: str) -> list[int]:
    """Valores L_isec del log de ligate; sin solape real ligate concatena sin alinear (C3)."""
    return [int(x) for x in _LISEC.findall(log_text)]


def require_ligate_overlap(log_text: str, n_chunks: int) -> None:
    vals = ligate_overlaps(log_text)
    if len(vals) != n_chunks - 1 or any(v <= 0 for v in vals):
        raise RuntimeError(f"ligate sin solape real entre chunks: L_isec={vals}")


def parse_switch_sample(lines) -> dict[str, float]:
    """Fichero *.sample.switch.txt de SHAPEIT5_switch: 'muestra errores evaluados SER%'."""
    out = {}
    for line in lines:
        f = line.split()
        if len(f) >= 4:
            out[f[0]] = float(f[3]) / 100.0
    return out
