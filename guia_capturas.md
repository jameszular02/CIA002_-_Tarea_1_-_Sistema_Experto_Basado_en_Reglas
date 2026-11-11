# Guía para tomar las capturas (terminal de GitHub Codespaces)

El informe pide, para cada caso de prueba, **una captura donde se vean las
preguntas, la conclusión y la explicación**. Esta guía dice exactamente qué
teclear. Los resultados esperados están en `casos_prueba.md`.

## Preparación (una sola vez)

1. Abra el Codespace del repositorio y la terminal: `Ctrl+ñ` en teclado
   español, ``Ctrl+` `` en teclado inglés, o el menú *Terminal → New Terminal*.
2. Maximice el panel de la terminal (ícono **^** "Maximize Panel Size").
3. Si la salida no cabe en pantalla, reduzca la letra con `Ctrl+-` (y vuelva
   a agrandarla con `Ctrl+=` al terminar).
4. Verifique la versión de Python (debe ser 3.10 o superior):

```bash
python --version
```

## Procedimiento para cada caso

Corra el programa una vez por caso, así cada captura queda limpia:

```bash
clear && python loria_james_tarea1.py
```

Escriba las teclas del caso, **cada una seguida de Enter**. Cuando aparezca
`¿Desea hacer otra consulta? (s/n):`, **no responda todavía**: tome la
captura, luego escriba `n` + Enter para salir.

Si la salida es más alta que la pantalla, tome dos capturas: una con las
preguntas (desplazándose hacia arriba) y otra con la recomendación y el
«¿Por qué?».

| Captura | Caso | Teclas (cada una + Enter) | Qué debe verse en la captura |
|---|---|---|---|
| 1 | A | `2` `1` `4` `2` `n` `2` `1` | «Recomendación principal (R12, certeza 90%)», avisos rojos de tóxicas, alternativa R13 |
| 2 | B | `2` `1` `3` `2` `s` `2` `1` | R13 sin plantas tóxicas y la línea «No se aplicó R12…» |
| 3 | C | `1` `3` `1` `2` `n` `1` `1` | R18 (90 %), alternativa R19 solo con hibisco y la explicación con `[de R5]`, `[de R1]`, `[de R8]` |
| 4 | D | `3` `3` `2` `2` `n` `1` `1` | R24 (85 %) y alternativa R25 |
| 5 | E | `2` `2` `1` `1` `s` `2` `1` | R29 (80 %) con echeveria y «No se aplicó R20 / R30» |
| 6 | F | `1` `3` `2` `2` `s` `1` `1` | R26 con el aviso amarillo «⚠ Sin registro de toxicidad en ASPCA…» |
| 7 | G | `2` `1` `4` `2` `n` `1` `1` | «Sin conclusión», hechos derivados y «Sugerencia (hueco conocido H1)» |
| 8 | H | `1` `3` `2` `2` `s` `3` `2` | R33 solo con palma areca y «No se aplicó R32…» |
| 9 | I | `3` `2` `1` `2` `n` `2` `1` | «Sin conclusión» con la sugerencia general |

Los casos A, B, C, D y G cubren los 5 casos que pide el enunciado (G es el
caso sin conclusión). E, F, H e I son evidencia adicional.

## Capturas complementarias (recomendadas)

**10. Validación de entradas (caso J).** Ejecute:

```bash
clear && python loria_james_tarea1.py
```

En la primera pregunta escriba, cada una con Enter: (Enter vacío), `abc`,
`9`, `0`, `2`. Capture los cuatro mensajes rojos `✗ …` y la pregunta 2 en
pantalla. Luego presione `Ctrl+C`.

**11. Ctrl+C (caso K).** En la misma corrida anterior, el `Ctrl+C` debe
mostrar «Consulta interrumpida. ¡Hasta pronto!». Capture esa línea.

**12. Repetir consulta.** Ejecute el programa, complete el caso C, responda
`s` a «¿Desea hacer otra consulta? (s/n):» y capture cómo vuelve a aparecer
«Pregunta 1 de 7». Salga con `Ctrl+C`.

**13. Historial CSV.** Después de hacer algunas consultas:

```bash
cat historial_consultas.csv
```

**14. Pruebas automáticas:**

```bash
clear && python -m unittest -v
```

Capture el final: `Ran 46 tests … OK`.

**15. Casos de prueba integrados en el programa:**

```bash
clear && python loria_james_tarea1.py --pruebas
```

Capture las nueve líneas ✅ y el resumen `9/9 casos correctos`. Esta captura
es útil porque el modo `--pruebas` va dentro del archivo que se entrega.

**16. Cobertura de la base de conocimiento:**

```bash
clear && python cobertura.py
```

Capture el resumen (72.5 % con recomendación) y los grupos sin cubrir.

## Interfaz web (extra)

**17. La interfaz en el navegador.** En la terminal:

```bash
clear && python loria_james_tarea1.py --web
```

1. Abra la página: aviso de abajo a la derecha → **Open in Browser**, o
   pestaña **PORTS** → puerto **8000** → ícono del globo 🌐.
2. Responda el caso C (Bajura caliente · Jardín · Pleno sol · Medio · No ·
   Flores · Principiante) y presione **Recomendar**.
3. Capture la recomendación principal, las alternativas y la sección
   «¿Por qué? Encadenamiento hacia adelante» con sus tres pasos.
4. Presione **Recomendar** sin responder todo para capturar la validación
   (las preguntas faltantes se marcan en rojo).
5. Baje hasta «Historial de consultas» para capturar la tabla del CSV.
6. Vuelva a la terminal y presione `Ctrl+C` para detener el servidor.

## Si los colores se ven mal

En `loria_james_tarea1.py`, sección 1, cambie `USAR_COLOR = True` por
`USAR_COLOR = False` y vuelva a ejecutar.
