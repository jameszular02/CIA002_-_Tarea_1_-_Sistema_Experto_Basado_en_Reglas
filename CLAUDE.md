# CLAUDE.md

Proyecto: Tarea 1 de CIA02 (UCreativa), sistema experto basado en reglas que
recomienda plantas ornamentales para hogares costarricenses. Autor: James Loria.

## Reglas del proyecto

- Todo el sistema vive en `loria_james_tarea1.py` y usa solo la biblioteca
  estándar de Python 3.10+. No agregar dependencias.
- La base de conocimiento (catálogo, preguntas, reglas, huecos y casos de
  prueba) son datos. No cambiar reglas sin que el autor lo pida.
- Después de cualquier cambio: `python -m unittest`,
  `python loria_james_tarea1.py --pruebas` y, si cambian las reglas,
  `python generar_reglas.py` y `python cobertura.py`.

## Diseño de la interfaz web (`--web`), aprobado el 11 nov 2026

Se diseñó con el skill `frontend-design`. Respetar estas decisiones.

**Concepto: «etiqueta de vivero».** La recomendación principal se muestra
como la etiqueta de plástico que se clava en la maceta en un vivero: banda de
color con perforación, esquinas recortadas y punta abajo. Es el único
elemento llamativo y el único con sombra; todo lo demás es plano y tranquilo.

**Paleta** (tokens en `:root` de `PLANTILLA_HTML`, con versión oscura):

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--neblina` | `#EDF1EE` | `#0F1913` | Fondo (gris verdoso de bosque nuboso, no crema) |
| `--cal` | `#FFFFFF` | `#17251C` | Superficie de la etiqueta y de los controles |
| `--bosque` | `#1E3A2A` | `#E2ECE5` | Texto y estructura |
| `--musgo` | `#56745A` | `#8FB394` | Texto secundario, hechos deducidos |
| `--guaria` | `#8E3B7E` | `#C987BC` | Único acento (guaria morada): etiqueta y acción principal |
| `--peligro` | `#B3261E` | `#FF8A80` | Planta tóxica y errores |
| `--atencion` | `#8F5B00` | `#F2C46D` | Sin registro de toxicidad y sin conclusión |

Cada color significa una sola cosa.

**Tipografía** (Google Fonts, con las fuentes del sistema como respaldo):
- Bricolage Grotesque para títulos, la etiqueta y las insignias de regla.
- Atkinson Hyperlegible para el texto (pensada para leerse fácil).
- Sin monoespaciada. Escala: 13, 15, 17, 22 y 34 px.

**Espaciado:** 4, 8, 12, 16, 24, 32 y 48 px. **Radios:** 8 px en controles,
4 px en insignias; la etiqueta usa esquinas recortadas.

**Layout:** una pregunta por pantalla (como la terminal), con barra de avance
de 7 segmentos. El resultado va en dos columnas: etiqueta y alternativas a la
izquierda; «¿Por qué esta recomendación?» a la derecha, en tres tramos
numerados (Sus respuestas, Lo que deduje, La regla que decidió). En celular,
una columna. Todo alineado a la izquierda.

**Principios:**
- El razonamiento se escribe en lenguaje natural (`FRASES_WEB`); la terminal
  y `reglas.md` siguen con la notación `clave = valor`.
- Solo se numera lo que es secuencia (preguntas y tramos).
- Un solo movimiento orquestado: la etiqueta «se clava» al aparecer. Se
  respeta `prefers-reduced-motion`.
- Atajos iguales a la terminal: teclas 1–4 o s/n para elegir y Enter para
  avanzar.

**Evitar:** fondo crema con serif, tarjetas idénticas para todo, etiquetas en
mayúsculas, metadatos unidos con punto medio, monoespaciada para etiquetas,
flecha al final de los botones.
