# Casos de prueba – Recomendador de plantas ornamentales

Cada caso indica **las teclas exactas** que se escriben (una por pregunta, cada
una seguida de Enter) y el **resultado esperado**. Los mismos casos están
guardados como datos dentro del programa (lista `CASOS_PRUEBA` de
`loria_james_tarea1.py`). Se comprueban de dos formas:

```bash
python loria_james_tarea1.py --pruebas
```

muestra ✅/❌ por caso y el resumen `9/9 casos correctos`; y
`python -m unittest` (archivo `test_sistema.py`) usa esa misma lista.

En la salida, una planta que ya apareció en una recomendación de mayor
certeza no se repite en las alternativas; si una alternativa queda vacía,
no se muestra. La explicación («¿Por qué?») sí menciona todas las reglas
activadas e indica qué plantas se omitieron.

Orden de las preguntas y sus opciones:

| # | Pregunta | Teclas |
|---|---|---|
| 1 | ¿En qué zona vive? | `1` bajura caliente · `2` Valle Central · `3` zona alta y fría |
| 2 | ¿Dónde estará la planta? | `1` dentro de la casa · `2` balcón o terraza · `3` jardín |
| 3 | ¿Cuánta luz recibe ese lugar? | `1` pleno sol · `2` semisombra · `3` luz indirecta · `4` poca luz |
| 4 | ¿Cuánto tiempo puede dedicarle? | `1` poco · `2` medio · `3` mucho |
| 5 | ¿Hay mascotas o niños pequeños en casa? | `s` sí · `n` no |
| 6 | ¿Qué busca? | `1` flores · `2` follaje · `3` cerca viva |
| 7 | ¿Cuál es su experiencia con plantas? | `1` principiante · `2` con experiencia |

## Resumen

| Caso | Teclas | Resultado esperado |
|---|---|---|
| A | `2 1 4 2 n 2 1` | Principal **R12** (90 %); alternativa R13 |
| B | `2 1 3 2 s 2 1` | Principal **R13** (85 %), sin plantas tóxicas; explica que R12 no aplica |
| C | `1 3 1 2 n 1 1` | Principal **R18** (90 %); alternativa R19 solo con hibisco (sin repetidas) |
| D | `3 3 2 2 n 1 1` | Principal **R24** (85 %); alternativa R25 |
| E | `2 2 1 1 s 2 1` | Principal **R29** (80 %): echeveria |
| F | `1 3 2 2 s 1 1` | Principal **R26** (75 %) con aviso amarillo de *sin registro* |
| G | `2 1 4 2 n 1 1` | **SIN CONCLUSIÓN**, sugerencia del hueco H1 |
| H | `1 3 2 2 s 3 2` | Principal **R33** (75 %): solo palma areca; explica que R32 no aplica |
| I | `3 2 1 2 n 2 1` | **SIN CONCLUSIÓN**, sugerencia general (caso no cubierto) |
| J | entradas inválidas | Avisa y vuelve a preguntar sin cerrarse |
| K | `Ctrl+C` | Sale con un mensaje limpio, sin error de Python |

---

## Caso A – Interior, poca luz, follaje, sin mascotas, principiante

**Teclas:** `2` `1` `4` `2` `n` `2` `1`
(Valle Central · dentro de la casa · poca luz · medio · no · follaje · principiante)

**Resultado esperado**
- Recomendación principal **R12 (certeza 90 %)**: Lengua de suegra, Zamioculca y
  Teléfono, cada una con **⚠ Tóxica para mascotas** en rojo.
- Alternativa **2. R13 (85 %)**: Mala madre, Peperomia y Palma de salón.
- ¿Por qué?: R2, R4, R8, R10 y luego
  `Se activó R12 (90%) porque: ambiente = interior [de R4], luz = poca_luz, restriccion = ninguna [de R8], objetivo = follaje`.

## Caso B – Interior, luz indirecta, follaje, con mascotas

**Teclas:** `2` `1` `3` `2` `s` `2` `1`
(Valle Central · dentro de la casa · luz indirecta · medio · sí · follaje · principiante)

**Resultado esperado**
- Recomendación principal **R13 (certeza 85 %)**: Mala madre, Peperomia y Palma
  de salón. **No aparece ninguna planta tóxica.**
- Sin alternativas.
- ¿Por qué?: incluye
  `No se aplicó R12: exige restriccion = ninguna, pero restriccion = no_toxicas [de R7]`.

## Caso C – Jardín, pleno sol, bajura, flores, sin mascotas

**Teclas:** `1` `3` `1` `2` `n` `1` `1`
(bajura caliente · jardín · pleno sol · medio · no · flores · principiante)

**Resultado esperado**
- Recomendación principal **R18 (certeza 90 %)**: Veranera, Moño de señora y
  Ave del paraíso (esta última con **⚠ Tóxica para mascotas**).
- Alternativa **2. R19 (85 %)**: solo Amapola / hibisco. Veranera y Moño de
  señora no se repiten porque ya aparecen en R18.
- ¿Por qué?:
  - `Se activó R1 porque: zona = bajura_caliente → clima = calido`
  - `Se activó R5 porque: ubicacion = jardin y luz = pleno_sol → ambiente = exterior_sol`
  - `Se activó R18 (90%) porque: ambiente = exterior_sol [de R5], clima = calido [de R1], objetivo = flores, restriccion = ninguna [de R8]`
  - `De R19 se omiten plantas ya mostradas: Veranera, Moño de señora`

## Caso D – Jardín, semisombra, zona alta, flores, sin mascotas

**Teclas:** `3` `3` `2` `2` `n` `1` `1`
(zona alta y fría · jardín · semisombra · medio · no · flores · principiante)

**Resultado esperado**
- Recomendación principal **R24 (certeza 85 %)**: Hortensia, Azalea y Begonia,
  todas con **⚠ Tóxica para mascotas**.
- Alternativa **2. R25 (80 %)**: Chinas.

## Caso E – Balcón, pleno sol, poco cuidado, con mascotas

**Teclas:** `2` `2` `1` `1` `s` `2` `1`
(Valle Central · balcón o terraza · pleno sol · poco · sí · follaje · principiante)

**Resultado esperado**
- Recomendación principal **R29 (certeza 80 %)**: Echeveria.
- ¿Por qué?: incluye `No se aplicó R20` y `No se aplicó R30` porque exigen
  `restriccion = ninguna`.
- Se eligió follaje como objetivo a propósito: con flores en Valle Central,
  R19 (85 %) le ganaría a R29.

## Caso F – Jardín, semisombra, bajura, flores, con mascotas

**Teclas:** `1` `3` `2` `2` `s` `1` `1`
(bajura caliente · jardín · semisombra · medio · sí · flores · principiante)

**Resultado esperado**
- Recomendación principal **R26 (certeza 75 %)**: Platanilla / heliconia, con
  **⚠ Sin registro de toxicidad en ASPCA; consulte a un veterinario.** en amarillo.

## Caso G – Interior, poca luz, flores → SIN CONCLUSIÓN

**Teclas:** `2` `1` `4` `2` `n` `1` `1`
(Valle Central · dentro de la casa · poca luz · medio · no · flores · principiante)

**Resultado esperado**
- `Sin conclusión: ninguna regla de la base de conocimiento cubre esta combinación de respuestas.`
- Muestra los hechos derivados obtenidos: clima = templado [R2],
  ambiente = interior [R4], restriccion = ninguna [R8], nivel = facil [R10].
- `Sugerencia (hueco conocido H1)`: con poca luz las plantas de interior casi
  no florecen; pruebe con follaje o acerque la planta a una ventana.
- No inventa ninguna planta.

## Caso H – Cerca viva en sombra con mascotas

**Teclas:** `1` `3` `2` `2` `s` `3` `2`
(bajura caliente · jardín · semisombra · medio · sí · cerca viva · con experiencia)

**Resultado esperado**
- Recomendación principal **R33 (certeza 75 %)**: solo Palma areca.
- ¿Por qué?: incluye
  `No se aplicó R32: exige restriccion = ninguna, pero restriccion = no_toxicas [de R7]`
  (R32 es la regla con caña india, que es tóxica).
- Variante sin mascotas (`1 3 2 2 n 3 2`): principal R32 con Caña india y Palma
  areca; R33 no aparece como alternativa porque su única planta ya se mostró.

## Caso I – Pleno sol, clima fresco, follaje → SIN CONCLUSIÓN (no cubierto)

**Teclas:** `3` `2` `1` `2` `n` `2` `1`
(zona alta y fría · balcón o terraza · pleno sol · medio · no · follaje · principiante)

**Resultado esperado**
- `Sin conclusión` con la **sugerencia general**: pruebe con otra ubicación,
  otro tipo de luz u otro objetivo, o consulte en un vivero de su zona.
- Es uno de los 32 casos que `cobertura.py` reporta como no cubiertos.

## Caso J – Validación de entradas

En la primera pregunta escriba, una por una (cada una con Enter):

| Entrada | Mensaje esperado |
|---|---|
| *(Enter sin escribir)* | `✗ No escribió nada. Escriba el número de una opción.` |
| `abc` | `✗ «abc» no es un número. Escriba solo el número de la opción.` |
| `9` | `✗ La opción 9 no existe. Elija entre 1 y 3.` |
| `0` | `✗ La opción 0 no existe. Elija entre 1 y 3.` |
| `2` | Acepta (Valle Central) y pasa a la pregunta 2 |

En la pregunta de mascotas: `x` → `✗ «x» no es válido. Responda s o n.`
En «¿Desea hacer otra consulta? (s/n)», cualquier respuesta distinta de s o n
vuelve a preguntar. El programa nunca se cierra por una entrada inválida.

## Caso K – Salida con Ctrl+C

En cualquier pregunta, presione `Ctrl+C`.

**Resultado esperado:** `Consulta interrumpida. ¡Hasta pronto!` y el programa
termina sin mostrar un *traceback* de Python.

---

## Pruebas automáticas

```bash
python loria_james_tarea1.py --pruebas
```

Resultado esperado: nueve líneas con ✅ y `9/9 casos correctos`.

```bash
python -m unittest -v
```

Resultado esperado: `Ran 46 tests ... OK`.
