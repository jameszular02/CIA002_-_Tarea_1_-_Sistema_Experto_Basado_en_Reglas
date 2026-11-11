---
name: frontend-design
description: Guía de diseño visual para crear o rediseñar la UI de este proyecto con una identidad propia, evitando el look genérico de plantilla. Úsalo siempre que se pida mejorar, rediseñar, estilizar o crear pantallas, componentes, estilos, colores, tipografía o layout (UI, frontend, diseño, "se ve feo", "mejora la interfaz").
---

# Frontend Design

Trabaja como el director de diseño de un estudio conocido por darle a cada cliente una identidad visual que no se confunde con la de nadie más. El cliente ya rechazó propuestas que se sentían cliché o de plantilla. Toma decisiones deliberadas y con opinión sobre paleta, tipografía y layout, específicas para este proyecto.

## 0. Si el proyecto ya existe: diagnostica antes de tocar

1. Identifica el stack de estilos (CSS plano, Tailwind, CSS modules, librería de componentes, Streamlit, etc.) y trabaja dentro de él. No metas un framework nuevo sin preguntar.
2. Haz un inventario: pantallas, componentes repetidos, colores y fuentes que ya se usan, valores de espaciado sueltos.
3. Lista los problemas concretos: jerarquía, espaciado, tipografía, contraste, consistencia, estados vacíos y de error.
4. **No cambies la lógica ni la funcionalidad.** Solo la presentación. Si algo de la lógica estorba al diseño, avísalo en vez de cambiarlo.
5. Presenta el diagnóstico y el plan de diseño (paso 2) y espera aprobación antes de editar archivos.

## 1. Ancla el diseño en el tema

Si no está claro qué es el producto, para quién es y cuál es su trabajo principal, propónlo y confírmalo. La industria, el tema, los materiales y el vocabulario del producto son de donde salen las decisiones visuales distintivas: un dashboard para analistas de precios no se ve como una app para niños. Usa contenido real del proyecto, no lorem ipsum.

## 2. Plan de diseño (antes de escribir código)

Crea un sistema de tokens compacto:

- **Color:** paleta base de 4–6 valores hex con nombre (y modo oscuro si aplica).
- **Tipo:** una o dos familias con roles claros. Si son dos, que sean claramente distintas. Escala tipográfica definida, con pesos y espaciado intencionales.
- **Layout:** concepto de layout en una frase + wireframes ASCII para comparar opciones. Define la alineación (izquierda, centro, etc.).
- **Principios:** qué hace única a esta interfaz.

Luego **revisa el plan contra el brief**: si alguna parte es lo que producirías por defecto para cualquier proyecto parecido, cámbiala y explica qué cambiaste y por qué. Solo entonces escribe código.

Centraliza los tokens (variables CSS, theme de Tailwind, config del framework) para que todo el proyecto los reutilice.

## 3. Defaults genéricos a evitar

El diseño generado por IA hoy suele caer en estos patrones. Son válidos si el brief los pide, pero no los uses por inercia:

1. Fondo crema cálido (~#F4F1EA) con serif de alto contraste y acento terracota (~#D97757).
2. Fondo casi negro con un solo acento verde ácido o bermellón.
3. Layout tipo periódico: líneas finas, border-radius cero, columnas densas.
4. Kit de tarjetas SaaS: todo cortado en tarjetas redondeadas idénticas, el mismo radio en todo, la misma sombra gris suave, gradientes como decoración. Gradientes morados.
5. Adornos de plantilla: etiqueta en MAYÚSCULAS espaciadas encima de cada título, metadatos unidos con puntos medios ("A · B · C"), negro teñido (#111) en vez de negro, monoespaciada para etiquetas pequeñas, "→" al final de cada botón.

Tipografía a evitar por defecto:
- Resaltar una sola palabra del título con otro color, cursiva o negrita.
- Etiquetas en mayúsculas.
- Etiquetas tipográficas innecesarias encima del contenido.
- Usar las mismas fuentes de siempre (Inter en todo) sin pensarlo.

## 4. Principios

- **La tipografía carga la personalidad.** Úsala como parte activa del diseño, no como vehículo neutro. Líneas de texto de menos de ~80 caracteres.
- **La estructura visual es información.** Bordes, divisores, numeración y etiquetas deben decir algo del contenido. Solo numera (01 / 02 / 03) si el contenido es de verdad una secuencia.
- **Jerarquía por importancia.** No todo merece una tarjeta; no todo lleva el mismo radio ni la misma sombra.
- **Movimiento con moderación.** Un solo momento orquestado vale más que animaciones en cada sección. Las animaciones que responden a una acción del usuario (abrir, expandir, confirmar) sí son bienvenidas.
- **Gasta la audacia en un solo lugar.** Un elemento memorable; todo lo demás, tranquilo y disciplinado. Antes de terminar, quita un accesorio.
- **Piso de calidad sin anunciarlo:** responsive hasta móvil, foco de teclado visible, respeta `prefers-reduced-motion`, contraste accesible, paleta armónica.

## 5. Textos de la interfaz

- Escribe desde la perspectiva del usuario: nombra las cosas como él las entiende, no como está construido el sistema.
- Voz activa. Un botón dice exactamente qué pasa: "Guardar cambios", no "Enviar". La acción mantiene su nombre en todo el flujo ("Publicar" → "Publicado").
- Errores: qué pasó y cómo arreglarlo, sin disculpas ni vaguedad. Estados vacíos: una invitación a actuar.
- Tono conversacional, verbos simples, sin relleno. Cada texto hace un solo trabajo.

## 6. Construir y autocriticar

- Rediseña **una pantalla a la vez**, empezando por la principal.
- Cuida la especificidad de los selectores CSS para que las clases no se cancelen entre sí (sobre todo padding/margin entre secciones).
- Si el entorno lo permite (Playwright, navegador), toma capturas después de cada cambio y critícalas antes de seguir.
- Anota en `CLAUDE.md` las decisiones de diseño aprobadas (paleta, fuentes, principios) para que futuras sesiones las respeten.
