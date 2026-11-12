# Recomendador de plantas ornamentales – Sistema experto basado en reglas

Tarea 1 de CIA02 – Introducción a la IA (UCreativa). Autor: James Loria.
Tema 3: qué planta ornamental sembrar en un hogar costarricense.

Todo el sistema está en **`loria_james_tarea1.py`** y usa solo la biblioteca
estándar de Python (3.10 o superior). No hay que instalar nada.

## Cómo usarlo

| Modo | Comando | Qué hace |
|---|---|---|
| Terminal | `python loria_james_tarea1.py` | Hace las 7 preguntas en la terminal, recomienda y explica el porqué |
| Interfaz web | `python loria_james_tarea1.py --web` | Abre la misma consulta en el navegador (puerto 8000) |
| Casos de prueba | `python loria_james_tarea1.py --pruebas` | Corre los 9 casos integrados y muestra ✅/❌ |

### Abrir la interfaz web en GitHub Codespaces

1. En la terminal del Codespace ejecute `python loria_james_tarea1.py --web`.
2. Aparece un aviso abajo a la derecha: *«Your application running on port
   8000 is available»* → **Open in Browser**.
   Si no aparece: pestaña **PORTS** (junto a TERMINAL) → fila del puerto
   **8000** → ícono del globo 🌐 (*Open in Browser*).
3. Responda las 7 preguntas y presione **Recomendar**.
4. Para detener el servidor, vuelva a la terminal y presione `Ctrl+C`.

Si el puerto 8000 está ocupado: `python loria_james_tarea1.py --web 8001`.

## Qué incluye

- **33 reglas** (11 intermedias + 22 finales) escritas como datos, separadas
  del motor de inferencia.
- **Encadenamiento hacia adelante**: las reglas intermedias deducen hechos
  (clima, ambiente, restricción, nivel) que usan las reglas finales; el motor
  itera hasta un punto fijo y ninguna regla se dispara dos veces.
- **Certeza 0–100**: recomendación principal y alternativas ordenadas.
- **Explicación estilo MYCIN**: qué reglas se activaron y de qué regla salió
  cada hecho (`[de R5]`).
- **Filtro de seguridad** para hogares con mascotas o niños (toxicidad según
  ASPCA, consulta 9 nov 2026).
- **Historial** de consultas en `historial_consultas.csv` (módulo `csv`),
  tanto desde la terminal como desde la interfaz web.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `loria_james_tarea1.py` | El sistema experto (archivo que se entrega) |
| `reglas.md` | Las reglas en lenguaje natural, generadas desde el código |
| `casos_prueba.md` | Casos de prueba con las teclas exactas y el resultado esperado |
| `guia_capturas.md` | Cómo tomar las capturas para el informe |
| `test_sistema.py` | Pruebas automáticas: `python -m unittest` |
| `cobertura.py` | Recorre las 1296 combinaciones de respuestas y reporta la cobertura |
| `generar_reglas.py` | Regenera `reglas.md` a partir de los datos del programa |
