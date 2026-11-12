# Contexto completo – Tarea 1: Sistema Experto Basado en Reglas

> Copia de todos los archivos del proyecto en un solo lugar, más este
> resumen. Las copias se tomaron el 12 nov 2026 del commit `453a944`.
> **La fuente de verdad son los archivos de la raíz del repositorio**: si se
> cambia algo allá, estas copias no se actualizan solas.

## 1. Datos de la tarea

| Dato | Valor |
|---|---|
| Curso | CIA02 – Introducción a la Inteligencia Artificial, UCreativa |
| Profesor | Angelo Ortiz Vega |
| Estudiante | James Loria |
| Tema | 3 – «Qué cultivo o planta sembrar», enfocado en **plantas ornamentales** de hogares costarricenses (nada de hortalizas ni comestibles) |
| Valor | 15 % |
| Entrega | **Jueves 12 de noviembre de 2026, antes de las 23:59**, por Classroom |
| Qué se entrega | `loria_james_tarea1.py` y el informe `loria_james_tarea1.pdf` (3 a 5 páginas) |
| Entorno | GitHub Codespaces, Python 3.10+, solo biblioteca estándar |
| Fuente de toxicidad | ASPCA, base de datos de plantas tóxicas y no tóxicas (consulta: 9 nov 2026) |

El enunciado completo es `CIA002_-_Tarea_1_-_Sistema_Experto_Basado_en_Reglas_completo.pdf`.
No está en el repositorio, por decisión del autor.

## 2. Archivos de esta carpeta

| Archivo | Qué es |
|---|---|
| `loria_james_tarea1.py` | **El sistema experto** (se entrega). Base de conocimiento como datos, motor, terminal, historial CSV, interfaz web y casos de prueba integrados |
| `test_sistema.py` | 48 pruebas con `unittest` |
| `reglas.md` | Las 33 reglas en lenguaje natural, generadas desde el código (sirven para el informe) |
| `casos_prueba.md` | 9 casos con las teclas exactas y el resultado esperado, más validación y Ctrl+C |
| `guia_capturas.md` | Cómo tomar cada captura en Codespaces |
| `cobertura.py` | Recorre las 1296 combinaciones de respuestas y reporta la cobertura |
| `generar_reglas.py` | Regenera `reglas.md` desde los datos del programa |
| `README.md` | Cómo usar el sistema |
| `CLAUDE.md` | Reglas del proyecto y decisiones de diseño de la interfaz web |
| `render.yaml` | Despliegue opcional de la interfaz web en Render (lo agregó otra sesión) |
| `skill_frontend-design/SKILL.md` | El skill de diseño que se usó para la interfaz web |

## 3. Cómo se ejecuta

```bash
python loria_james_tarea1.py
```
Consulta en la terminal: 7 preguntas, recomendación, alternativas y «¿Por qué?».

```bash
python loria_james_tarea1.py --web
```
Interfaz web en el puerto 8000. En Codespaces: pestaña PORTS → *Preview in Editor*
u *Open in Browser*. Si aparece el error 401, ver la sección 9.

```bash
python loria_james_tarea1.py --pruebas
```
Corre los 9 casos integrados; debe decir «9/9 casos correctos».

```bash
python -m unittest
```
Debe terminar en «Ran 48 tests … OK».

```bash
python cobertura.py
```

## 4. Base de conocimiento (resumen)

- **7 preguntas**: zona, ubicación, luz, cuidado, mascotas (s/n), objetivo y experiencia.
- **4 hechos derivados**: clima, ambiente, restricción y nivel.
- **33 reglas**:
  - **11 intermedias** (R1–R11), que deducen los hechos derivados;
  - **22 finales** (R12–R33), cada una con certeza de 0 a 100.
- **22 conclusiones distintas** y **30 plantas** en el catálogo (14 tóxicas, 13 seguras, 3 sin registro en ASPCA).
- **Huecos conocidos con sugerencia propia**:
  - H1: interior + poca luz + flores;
  - H2: interior + cerca viva;
  - H3: interior + pleno sol;
  - H4: sombra + cerca viva en clima fresco.
- **Cobertura de las 1296 combinaciones**:

| Resultado | Combinaciones | % |
|---|---|---|
| Con recomendación | 940 | 72.5 % |
| Hueco conocido | 324 | 25.0 % |
| Sin cubrir | 32 | 2.5 % |

Los 32 casos sin cubrir son pleno sol + follaje con cuidado medio o mucho, en dos situaciones: con mascotas en clima cálido o templado, o cualquier hogar en clima fresco.

## 5. Decisiones tomadas durante el desarrollo

1. **Reglas como datos**: listas de diccionarios. Una condición acepta un valor o una lista de valores. No hay un `if` por regla.
2. **Encadenamiento hacia adelante**: el motor itera hasta un punto fijo y ninguna regla se dispara dos veces. La explicación marca de qué regla salió cada hecho (`[de R5]`).
3. **Orden de las recomendaciones**:
   1. mayor certeza;
   2. más condiciones (una lista cuenta como una sola condición);
   3. id menor.
4. **Mascotas o niños**:
   - las reglas con alguna planta tóxica exigen `restriccion = ninguna`, y una prueba lo verifica;
   - las reglas con solo plantas seguras o sin registro no llevan esa condición;
   - un **filtro de seguridad** posterior quita las tóxicas cuando hay mascotas, y marca en amarillo las «sin registro» y en rojo las tóxicas.
5. **Cambios aprobados por el autor sobre la base original**:
   - R12 sin `nivel=facil`;
   - R12–R17 aceptan semisombra dentro de la casa;
   - R32 (caña india y areca, sin mascotas) y R33 (solo areca);
   - se sacó la haworthia del catálogo;
   - nuevo tip de la palma areca;
   - hueco H4.
6. **Salida sin repeticiones**: una planta que ya apareció en una recomendación de mayor prioridad no se repite en las alternativas, y una alternativa vacía no se muestra.
7. **Casos de prueba** dentro del `.py` (`CASOS_PRUEBA` y modo `--pruebas`), porque a Classroom solo se sube ese archivo.
8. **Interfaz web** con `http.server` (biblioteca estándar), rediseñada con el skill `frontend-design`. Las decisiones están en `CLAUDE.md`.
9. **Despliegue en Render** (otra sesión): `HOST` es configurable por variable de entorno, por defecto `127.0.0.1`. En Render el disco no es permanente, así que el historial CSV se borra en cada reinicio.

## 6. Requisitos del enunciado: estado

| # | Requisito (sección 6 del PDF) | Estado | Dónde |
|---|---|---|---|
| 1 | ≥20 reglas con id, condiciones y conclusión | ✅ 33 | `REGLAS` |
| 2 | ≥6 preguntas con opciones definidas | ✅ 7 | `PREGUNTAS` |
| 3 | ≥5 conclusiones distintas | ✅ 22 | `validar_base_conocimiento()` |
| 4 | Reglas separadas del motor | ✅ | `encadenar()`, `evaluar()` |
| 5 | Validar entradas sin cerrarse | ✅ | `preguntar()`, `preguntar_si_no()`, Ctrl+C en `main()` |
| 6 | Explicar la decisión | ✅ | `explicar()` (estilo MYCIN) |
| 7 | Caso sin conclusión | ✅ | `mostrar_recomendacion()`, casos G e I |
| 8 | Repetir la consulta | ✅ | «¿Desea hacer otra consulta? (s/n)» en `main()` |
| 9 | ≥4 funciones con comentarios | ✅ | Más de 40 funciones con docstrings, en 9 secciones |
| 10 | Solo biblioteca estándar | ✅ | `csv`, `html`, `json`, `os`, `sys`, `threading`, `datetime`, `http.server`, `urllib` |
| 11 | ≥5 casos de prueba | ✅ 9 | `CASOS_PRUEBA`, `casos_prueba.md` |
| Extra | Encadenamiento | ✅ | `encadenar()` |
| Extra | Niveles de certeza | ✅ | Certeza en cada regla final, principal y alternativas |
| Extra | Historial CSV | ✅ | `guardar_historial()` → `historial_consultas.csv` |
| Extra | Interfaz más cuidada | ✅ | Colores ANSI (`USAR_COLOR`) e interfaz web (`--web`) |
| Entrega | Encabezado con nombre, tema y fecha | ✅ | Primeras líneas del `.py` |

## 7. Casos de prueba

Las teclas van en el orden zona, ubicación, luz, cuidado, mascotas, objetivo, experiencia.

| Caso | Teclas | Resultado |
|---|---|---|
| A | `2 1 4 2 n 2 1` | R12 (90 %); alternativa R13 |
| B | `2 1 3 2 s 2 1` | R13 (85 %), sin tóxicas |
| C | `1 3 1 2 n 1 1` | R18 (90 %); alternativa R19 (solo hibisco) |
| D | `3 3 2 2 n 1 1` | R24 (85 %); alternativa R25 |
| E | `2 2 1 1 s 2 1` | R29 (80 %): echeveria |
| F | `1 3 2 2 s 1 1` | R26 (75 %) con aviso de «sin registro» |
| G | `2 1 4 2 n 1 1` | Sin conclusión (H1) |
| H | `1 3 2 2 s 3 2` | R33 (75 %): solo palma areca |
| I | `3 2 1 2 n 2 1` | Sin conclusión (mensaje general) |

Los 5 obligatorios para el informe son A, B, C, D y G (este último es el caso sin conclusión).

## 8. Lo que falta (todo del autor)

1. **Confirmar el tema 3 en Figma**, si no se hizo (sección 5 del enunciado).
2. **Investigación**: al menos 3 fuentes confiables (Wikipedia no cuenta), cada una con título, autor u organización, enlace y fecha de consulta. Hoy solo está ASPCA; faltan **2 o más** para lo agronómico.
3. **Capturas** de los casos A, B, C, D y G (`guia_capturas.md`).
4. **Informe PDF** `loria_james_tarea1.pdf` (3 a 5 páginas), con estas secciones en este orden:
   1. Portada: nombre, curso, tema y fecha.
   2. Justificación del tema, en máximo 5 líneas. Conviene explicar por qué no hay pregunta de suelo (plantas en maceta o sustrato).
   3. Investigación: factores, valores, conclusiones y las 3 fuentes o más.
   4. Reglas en lenguaje natural con los mismos ids (copiar de `reglas.md`).
   5. Pruebas: 5 casos con respuestas, conclusión y captura.
   6. Declaración de uso de herramientas de IA, en una línea.
5. **Subir a Classroom** `loria_james_tarea1.py` y `loria_james_tarea1.pdf` antes de las 23:59 del 12 de noviembre.

## 9. Limitaciones (para la reflexión del informe)

- **Conocimiento incompleto**: veranera, moño de señora y heliconia no tienen registro en ASPCA. Se muestran con aviso y no se asumen seguras.
- **Casos sin respuesta**: el 27.5 % de las combinaciones no tiene conclusión. El sistema lo dice en vez de inventar.
- **Reglas escritas a mano**: cada combinación nueva exige escribir una regla, y los huecos se descubrieron recorriendo todas las combinaciones con `cobertura.py`.
- **Nombres comunes**: varían por región (por ejemplo «amapola» o «chinas»), por eso se muestra también el nombre científico.

## 10. Problema conocido al abrir la interfaz web en Codespaces

Un **error 401** al abrir el puerto 8000 viene de GitHub, no del programa: el puerto es privado y el navegador no tiene la sesión de GitHub o bloquea la cookie (pasa mucho en Edge). Soluciones, de más a menos recomendada:

1. Abrirla dentro del editor: PORTS → *Preview in Editor*.
2. Desactivar la prevención de seguimiento de Edge para `github.dev`, o usar un navegador con la sesión de GitHub abierta.
3. Poner el puerto en *Public* mientras se toman las capturas y volverlo a *Private* después.
