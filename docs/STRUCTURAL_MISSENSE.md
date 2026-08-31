# Análisis estructural del candidato missense

> **PREDICCIÓN ESTRUCTURAL COMPUTACIONAL — NO ES EVIDENCIA FUNCIONAL.**
>
> Saneado: sin coordenadas, número de residuo ni identidad de aminoácidos. Detalle en
> `work/struct/`.

## Qué estructura se usó, y por qué importa

VEP mapeó el candidato a dos estructuras experimentales del PDB y al modelo de AlphaFold DB.
Se descargaron las tres y **se comprobó la cobertura antes de usarlas**:

| Estructura | Cadena de BUBR1 | ¿Cubre el residuo candidato? |
|---|---|---|
| PDB experimental 1 | 18–308 | **No** |
| PDB experimental 2 | 19–345 | **No** |
| AlphaFold DB (`AF-O60566-F1`) | 1–1050 | **Sí** |

**Las dos estructuras experimentales solo resuelven el extremo N-terminal.** Son complejos
APC/C donde el dominio C-terminal de BUBR1 no está resuelto. Para este residuo **la única
estructura disponible es un modelo predicho**, y eso hay que declararlo: es predicción sobre
predicción.

**No se ejecutó AlphaFold.** El modelo ya existe en AlphaFold DB. Correrlo habría gastado
GPU para reproducir algo descargable.

## Confianza local del modelo

| | pLDDT |
|---|---|
| Residuo candidato | **91,1** |
| Ventana ±10 residuos | 91,5 (mín 80,4 · máx 95,3) |
| Media de toda la proteína | 63,6 |

La media global baja refleja las regiones desordenadas de BUBR1. **Pero la región del
candidato está en confianza muy alta (>90)**, muy por encima de la media de la proteína.

Eso es lo que legitima el análisis: en una región de pLDDT bajo, medir enterramiento o
contactos no significaría nada.

> **Uso permitido de pLDDT:** evaluar si el modelo es fiable en esa posición.
> **Uso prohibido:** comparar pLDDT del silvestre contra el mutante como evidencia de
> desestabilización (brief §12: ΔpLDDT correlaciona muy débilmente con ΔΔG, PCC ≈ −0,17).

## Resultado

### El residuo está enterrado

| | |
|---|---|
| SASA absoluta | 31,5 Å² |
| **RSA relativa** | **16,2 %** |

Por debajo del 20 % convencional para «enterrado».

### En un bolsillo hidrofóbico y aromático

**10 residuos a menos de 5 Å, de los cuales 8 son hidrofóbicos y solo 1 cargado.** Entre los
vecinos hay **cuatro aromáticos** (dos triptófanos y dos fenilalaninas), formando un núcleo
compacto.

### Y hace tres puentes de hidrógeno con el esqueleto

La cadena lateral del residuo silvestre establece **tres enlaces con átomos del esqueleto
peptídico de residuos vecinos**, todos entre 2,83 y 2,95 Å. No es un residuo decorativo:
está grapando la conformación local.

## Predicción del efecto del cambio

El cambio sustituye un residuo **polar y corto** por uno **cargado positivamente y mucho más
largo**. En este contexto concreto eso implica:

1. **Carga enterrada.** Meter una carga positiva en un bolsillo hidrofóbico tiene coste de
   desolvatación. Es un mecanismo clásico de desestabilización.
2. **Pérdida de los tres puentes con el esqueleto.** La geometría del grupo funcional cambia
   por completo: en el silvestre está a la altura del Cγ, en el mutante queda ~3 Å más
   lejos, en el Cε. No puede reproducir esos contactos.
3. **Tensión estérica.** El entorno está densamente empaquetado y la cadena lateral entrante
   es considerablemente más larga.

> **Predicción: desestabilizante.** Coherente con el mecanismo publicado para MVA por
> `BUB1B`, donde los mutantes missense del dominio C-terminal muestran recambio proteico
> elevado y dependencia de chaperonas.

## La tensión con REVEL, declarada

**REVEL dio 0,472 — indeterminado.** El análisis estructural apunta a desestabilización.
Discrepan, y hay que decirlo en vez de elegir el que gusta más.

Explicación plausible: REVEL es un conjunto entrenado sobre variantes clasificadas y pesa
mucho la conservación evolutiva. Un residuo puede ser estructuralmente crítico en el
plegamiento y aun así no estar profundamente conservado. Además, la representación de
dominios pseudoquinasa en los conjuntos de entrenamiento es pobre.

> **Esto NO revierte la decisión de `PP3`.** Los umbrales estaban preregistrados y REVEL
> quedó por debajo. Usar el resultado estructural para reabrir `PP3` sería exactamente
> buscar el predictor que da la respuesta deseada. **La tabla ACMG no cambia.**

## Qué cambia y qué no

**No cambia:**
- La clasificación del candidato missense sigue siendo **VUS**.
- No hay `PP3`, no hay `PM1`, no hay `PS1`, no hay `PM5`.
- `PM3` sigue bloqueado. La fase sigue sin resolver.

**Sí cambia:** ahora hay una **hipótesis mecanística concreta y medible**, en lugar de una
intuición. Y es falsable con un experimento definido:

> Si el residuo enterrado que grapa el núcleo local se sustituye por uno cargado y largo, la
> abundancia de BUBR1 debería estar reducida. **Se mide.** Ensayo de estabilidad o
> abundancia proteica variante-específico → habilitaría `PS3`.

Ese ensayo es, junto con la fase, uno de los dos únicos caminos que pueden mover esta
variante de VUS.

## Pendiente

**Conservación.** Falta el alineamiento múltiple para evaluar cuán conservado está el
residuo entre ortólogos. Es el dato que reconciliaría —o no— la discrepancia con REVEL.

**ΔΔG cuantitativo.** El análisis actual es de descriptores estructurales, no un cálculo de
energía libre. Un ΔΔG con FoldX o equivalente, repetido varias veces, daría una magnitud.
Se ha preferido no dar un número que no se puede sostener antes que dar uno falso.
