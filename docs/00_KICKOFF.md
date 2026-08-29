# Prompt de arranque

Pega esto como primer mensaje en Claude Code, dentro del repositorio.

---

Estás trabajando en el análisis genómico de un paciente pediátrico real con sospecha de Mosaic Variegated Aneuploidy, para el Rare Disease Real Kid MVA Hackathon 2026.

Lee, en este orden y completos, antes de escribir una sola línea de código:

1. `CLAUDE.md`
2. `docs/01_MASTER_BRIEF.md`
3. `docs/02_ANALYSIS_PLAN.md`

No los resumas para mí. Léelos y trabaja con ellos.

Después de leerlos, haz exactamente esto y nada más:

**Primero**, ejecuta la comprobación de seguridad del repositorio de la Fase 0.1 y dime si el historial de git está limpio de datos del paciente. Si el repositorio no es privado, para y avísame antes de continuar.

**Segundo**, crea la estructura de directorios y los archivos de configuración: `config/paths.example.yaml`, `config/panels/mva.txt`, `config/panels/nephrocalcinosis.txt`, `.gitignore`, `docs/DECISIONS.md` y `docs/EVIDENCE.md` vacíos con sus cabeceras. Los paneles ya están especificados en el plan; transcríbelos.

**Tercero**, dime qué rutas necesitas en `config/paths.yaml` y espera a que yo las rellene. No inventes rutas ni asumas que los datos están en el repositorio.

**Cuarto**, antes de ejecutar la Fase 0.2, escribe en `docs/DECISIONS.md` qué esperas encontrar en la cabecera del VCF y por qué importa cada campo. Preregistra antes de mirar.

Reglas que voy a hacer cumplir durante todo el proyecto:

- Ningún dato del paciente entra en el repositorio. Nunca. Ni temporalmente.
- Nada de recomendaciones clínicas. El entregable es una hipótesis falsable.
- Si no verificaste un PMID o un DOI en esta sesión, escribe `no verificado`. No lo inventes.
- Etiqueta cada afirmación con su nivel de evidencia L0 a L5.
- Los resultados negativos se documentan, no se esquivan. Si una rama muere, muere.
- Si te pido algo que contradice el plan, dímelo antes de hacerlo.

Cuando termines los cuatro puntos, párate y espera. No avances a la Fase 1 sin que yo te lo diga.

---

## Archivos de referencia rápida

| Archivo | Contenido |
|---|---|
| `CLAUDE.md` | Reglas duras, convenciones, estructura, lo que no hay que hacer |
| `docs/01_MASTER_BRIEF.md` | Contexto científico completo: datos, fenotipo, genética MVA, arquitectura, el problema de cancelación de BAF, MitoRead, HPO Residual/Bartter, evidencia y contraevidencia, ideas descartadas, preguntas abiertas |
| `docs/02_ANALYSIS_PLAN.md` | Fases 0-8 con comandos, tablas de decisión preregistradas y entregable final |
| `docs/DECISIONS.md` | Bitácora viva. Se escribe **antes** de cada fase |
| `docs/EVIDENCE.md` | Tabla de evidencia viva. Se actualiza al leer cada paper |

## Las tres cosas que más fácil se olvidan

1. **No alinees los 86 GB hasta la Fase 6.** Hay tres atajos documentados que ahorran días.
2. **`unphased` ≠ `trans`.** Sin genotipos parentales, la fase no resuelta se reporta como no resuelta.
3. **La cancelación de BAF es estructural, no de profundidad.** Más cobertura no la arregla. Ver brief §6.

## Las tres preguntas que valen más que cualquier análisis

Mandar por email hoy, no en la semana seis:

1. ¿Hubo polihidramnios u oligohidramnios en el embarazo?
2. ¿La librería es PCR-free?
3. ¿Cuál era el hemograma (plaquetas y fórmula) contemporáneo a la extracción?
