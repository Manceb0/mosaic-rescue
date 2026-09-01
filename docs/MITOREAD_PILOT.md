# EXP-014a · MitoRead — piloto técnico sobre L001

> **`DERIVED` · NO INTERPRETABLE COMO BIOLOGÍA DEL PACIENTE.**
>
> **Origen ejecutable:** `src/mito/pilot_l001.py`

## Corrección de un error propio

Esta rama se declaró **BLOQUEADA porque «el VCF no contiene variantes mitocondriales»**.
Eso era irrelevante y la clasificación estaba mal: **mtDNA-CN es un cociente de cobertura y no
necesita ninguna variante mitocondrial**. El brief §7.1 lo define exactamente así.

El estado correcto tiene dos mitades:

| | |
|---|---|
| **EXP-014a · piloto técnico** | **DESBLOQUEADO** — se puede medir con L001 |
| **EXP-014b · interpretación biológica** | **BLOQUEADO** — profundidad completa, controles y hemograma |

## Resultado del prototipo

| | |
|---|---|
| Lecturas examinadas | 2 000 000 de L001 R1 |
| Compatibles con mitocondrial | 1 382 (**0,069 %**) |
| **Estimación ingenua de copias equivalentes a mtDNA** | **≈ 259, bajo los supuestos del piloto** |

El valor cae dentro del rango fisiológico habitual en sangre. **Eso no valida nada**: un
resultado plausible no es un resultado calibrado, y la plausibilidad es exactamente lo que
hace peligroso presentarlo como medida.

> **La formulación correcta es:** *naive mtDNA-equivalent copy estimate ≈ 259 under the pilot
> assumptions.* **NO** «mtDNA-CN del paciente = 259». La diferencia no es de estilo: el primero
> es un número de prototipo, el segundo sería una medida del niño.

## Método, y por qué este y no otro

No hay alineador instalable en esta máquina (`mappy` no compila sin toolchain de C) ni
referencia nuclear descargada. Se contaron lecturas que comparten **≥2 k-meros de 31 pb** con
el genoma mitocondrial de referencia, en ambas hebras y cerrando el círculo del cromosoma.

La secuencia de referencia se descargó de Ensembl. **Es secuencia pública: ningún dato del
paciente salió de la máquina.**

## Por qué NO es interpretable — cuatro razones, todas bastantes por sí solas

1. **Los NUMT no se pueden excluir.** Las inserciones de ADN mitocondrial en el genoma nuclear
   comparten secuencia con el mtDNA. Sin alinear al genoma completo con filtro de unicidad de
   mapeo, entran en el recuento. **El sesgo es al alza, y no está cuantificado aquí.** Es la
   diferencia exacta entre 014a y 014b.
2. **Un solo carril.** El VCF se generó con los cuatro; L001 es ~13×.
3. **Sin controles** procesados con pipeline idéntico. A esta profundidad el factor limitante
   es el sesgo sistemático, no el ruido binomial (brief §1).
4. **Sin hemograma.** Las plaquetas tienen mitocondrias y **no núcleo**, así que distorsionan
   directamente el cociente. La fórmula leucocitaria también. Sigue pendiente de respuesta.

Y el supuesto de fondo, que es el punto más atacable de toda la rama: que la `mtDNA-CN` en
**sangre periférica** refleje el estado mitocondrial de músculo y riñón.

## Cierre

| | |
|---|---|
| **EXP-014a** | **VIABILIDAD TÉCNICA · PROTOTIPO** — no `SURVIVES`: no hay nada calibrado que pueda sobrevivir todavía |
| **EXP-014b** | **BLOCKED** — BAM/CRAM de profundidad completa · controles · hemograma |
| Qué reduce | Solo una cosa: la duda de si la rama era **técnicamente** ejecutable. Lo es |
| Qué NO reduce | Nada sobre la biología del paciente |
| Siguiente | Alineamiento al genoma completo con exclusión de NUMT, controles y hemograma |

## Nivel de evidencia

`L0` para cualquier afirmación biológica. `L5` como método (el cociente de cobertura es una
técnica establecida, PMID 28453676).
