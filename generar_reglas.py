# -*- coding: utf-8 -*-
"""Genera reglas.md a partir de la base de conocimiento del programa.

Las reglas se escriben UNA sola vez, como datos, en loria_james_tarea1.py.
Este script las traduce a lenguaje natural para el informe, así el documento
y el código no se pueden desincronizar.

Uso:
    python generar_reglas.py

Solo usa la biblioteca estándar.
"""

import loria_james_tarea1 as sistema
import cobertura

ARCHIVO_SALIDA = "reglas.md"

# Nombres legibles de cada hecho (solo para el documento).
ETIQUETAS = {
    "zona": "zona", "ubicacion": "ubicación", "luz": "luz",
    "cuidado": "tiempo de cuidado", "mascotas": "mascotas o niños",
    "objetivo": "objetivo", "experiencia": "experiencia",
    "clima": "clima", "ambiente": "ambiente", "restriccion": "restricción",
    "nivel": "nivel",
}


def texto_valor(clave, valor):
    """Texto legible de un valor: la opción de la pregunta o el hecho derivado."""
    for pregunta in sistema.PREGUNTAS:
        if pregunta["clave"] == clave:
            for interno, visible in pregunta["opciones"]:
                if interno == valor:
                    return visible.split(" (")[0].lower()
    return sistema.HECHOS_DERIVADOS[clave][valor]


def unir_con_o(valores):
    """Une una lista como "a, b o c"."""
    if len(valores) == 1:
        return valores[0]
    return ", ".join(valores[:-1]) + " o " + valores[-1]


def texto_condiciones(condiciones):
    """Convierte un bloque "si" en lenguaje natural."""
    partes = []
    for clave, esperado in condiciones.items():
        valores = [texto_valor(clave, v)
                   for v in sistema.valores_aceptados(esperado)]
        partes.append(f"{ETIQUETAS[clave]} = {unir_con_o(valores)}")
    return " **Y** ".join(partes)


def notacion_codigo(condiciones):
    """Notación compacta igual a la del código."""
    partes = []
    for clave, esperado in condiciones.items():
        if isinstance(esperado, list):
            partes.append(f"{clave} ∈ [{', '.join(esperado)}]")
        else:
            partes.append(f"{clave} = {esperado}")
    return ", ".join(partes)


def nombre_planta(id_planta):
    """Nombre común de una planta del catálogo."""
    return sistema.PLANTAS_POR_ID[id_planta]["nombre"]


def generar():
    """Arma el contenido completo de reglas.md y lo devuelve como texto."""
    sistema.validar_base_conocimiento()
    intermedias = [r for r in sistema.REGLAS if r["tipo"] == "intermedia"]
    finales = [r for r in sistema.REGLAS if r["tipo"] == "final"]
    lineas = []
    agregar = lineas.append

    agregar("# Base de conocimiento – Recomendador de plantas ornamentales")
    agregar("")
    agregar("> Documento **generado automáticamente** desde "
            "`loria_james_tarea1.py` con `python generar_reglas.py`. "
            "No se edita a mano: los ids son los mismos del código.")
    agregar("")
    agregar(f"- Reglas: **{len(sistema.REGLAS)}** "
            f"({len(intermedias)} intermedias + {len(finales)} finales)")
    agregar(f"- Preguntas: **{len(sistema.PREGUNTAS)}**")
    agregar(f"- Conclusiones finales distintas: "
            f"**{len({tuple(r['entonces']) for r in finales})}**")
    agregar(f"- Plantas en el catálogo: **{len(sistema.CATALOGO)}**")
    agregar("")

    # --- Preguntas ---------------------------------------------------------
    agregar("## 1. Preguntas al usuario")
    agregar("")
    agregar("| Clave | Pregunta | Opciones (tecla → valor interno) |")
    agregar("|---|---|---|")
    for pregunta in sistema.PREGUNTAS:
        if pregunta["tipo"] == "sn":
            opciones = " · ".join(f"`{v}` → {v}"
                                  for v, _ in pregunta["opciones"])
        else:
            opciones = " · ".join(
                f"`{i}` → {v}"
                for i, (v, _) in enumerate(pregunta["opciones"], start=1))
        agregar(f"| {pregunta['clave']} | {pregunta['texto']} | {opciones} |")
    agregar("")

    # --- Hechos derivados --------------------------------------------------
    agregar("## 2. Hechos derivados")
    agregar("")
    agregar("Los deducen las reglas intermedias; el usuario no los responde.")
    agregar("")
    agregar("| Hecho | Valores posibles |")
    agregar("|---|---|")
    for clave, valores in sistema.HECHOS_DERIVADOS.items():
        agregar(f"| {clave} | {', '.join(valores)} |")
    agregar("")

    # --- Reglas intermedias ------------------------------------------------
    agregar("## 3. Reglas intermedias (encadenamiento hacia adelante)")
    agregar("")
    agregar("| Id | Regla en lenguaje natural | Notación del código |")
    agregar("|---|---|---|")
    for regla in intermedias:
        clave, valor = regla["entonces"]
        natural = (f"**SI** {texto_condiciones(regla['si'])} **ENTONCES** "
                   f"{ETIQUETAS[clave]} = {texto_valor(clave, valor)}")
        codigo = f"{notacion_codigo(regla['si'])} → {clave} = {valor}"
        agregar(f"| {regla['id']} | {natural} | `{codigo}` |")
    agregar("")

    # --- Reglas finales ----------------------------------------------------
    agregar("## 4. Reglas finales (recomendaciones)")
    agregar("")
    agregar("| Id | Regla en lenguaje natural | Certeza |")
    agregar("|---|---|---|")
    for regla in finales:
        plantas = ", ".join(nombre_planta(p) for p in regla["entonces"])
        natural = (f"**SI** {texto_condiciones(regla['si'])} **ENTONCES** "
                   f"recomendar: {plantas}")
        agregar(f"| {regla['id']} | {natural} | {regla['certeza']} % |")
    agregar("")
    agregar("Orden de las recomendaciones: mayor certeza; si empatan, la regla "
            "con más condiciones (una lista de valores cuenta como una sola "
            "condición); si siguen empatadas, el id menor.")
    agregar("")

    # --- Restricción y filtro ----------------------------------------------
    agregar("## 5. Mascotas: restricción y filtro de seguridad")
    agregar("")
    agregar("- Las reglas que concluyen al menos una planta **tóxica** exigen "
            "`restriccion = ninguna`. Así la explicación deja claro por qué no "
            "aplican cuando hay mascotas o niños.")
    agregar("- Las reglas cuyas plantas son solo **seguras** o **sin "
            "registro** no llevan esa condición: sirven para cualquier hogar.")
    agregar("- Después de evaluar, un **filtro de seguridad** revisa planta "
            "por planta contra el catálogo (defensa en profundidad):")
    agregar("  - con mascotas: elimina las tóxicas y marca en amarillo las "
            "sin registro (*⚠ Sin registro de toxicidad en ASPCA; consulte a "
            "un veterinario.*); si una conclusión queda vacía, se descarta;")
    agregar("  - sin mascotas: marca en rojo las tóxicas (*⚠ Tóxica para "
            "mascotas*).")
    agregar("")

    # --- Huecos y cobertura ------------------------------------------------
    resumen = cobertura.calcular_cobertura()
    total = resumen["total"]
    en_hueco = sum(resumen["en_hueco"].values())
    sin_cubrir = len(resumen["sin_cubrir"])

    agregar("## 6. Casos sin conclusión")
    agregar("")
    agregar("Cuando ninguna regla final aplica, el sistema lo dice con "
            "claridad, muestra los hechos que sí dedujo y da una sugerencia. "
            "Nunca inventa una recomendación.")
    agregar("")
    agregar("### 6.1 Huecos conocidos (con sugerencia específica)")
    agregar("")
    agregar("| Id | Condiciones | Sugerencia | Combinaciones |")
    agregar("|---|---|---|---|")
    for hueco in sistema.HUECOS_CONOCIDOS:
        agregar(f"| {hueco['id']} | {texto_condiciones(hueco['si'])} | "
                f"{hueco['mensaje']} | {resumen['en_hueco'][hueco['id']]} |")
    agregar("")
    agregar("### 6.2 Cobertura (`python cobertura.py`)")
    agregar("")
    agregar(f"Se recorrieron las **{total}** combinaciones posibles de "
            f"respuestas con el mismo motor del programa:")
    agregar("")
    agregar("| Resultado | Combinaciones | % |")
    agregar("|---|---|---|")
    agregar(f"| Con recomendación | {resumen['con_recomendacion']} | "
            f"{cobertura.porcentaje(resumen['con_recomendacion'], total)} |")
    agregar(f"| Hueco conocido (sugerencia específica) | {en_hueco} | "
            f"{cobertura.porcentaje(en_hueco, total)} |")
    agregar(f"| Sin cubrir (mensaje general) | {sin_cubrir} | "
            f"{cobertura.porcentaje(sin_cubrir, total)} |")
    agregar("")
    agregar("### 6.3 Limitación: grupos sin cubrir")
    agregar("")
    if not resumen["sin_cubrir"]:
        agregar("No quedan combinaciones sin cubrir.")
    else:
        agregar("| # | Patrón | Casos | Ejemplo de respuestas |")
        agregar("|---|---|---|---|")
        for numero, grupo in enumerate(
                cobertura.agrupar_sin_cubrir(resumen["sin_cubrir"]), start=1):
            rasgos = [f"ambiente = {grupo['ambiente']}",
                      f"objetivo = {grupo['objetivo']}"]
            # El "|" rompería la tabla de markdown: se reemplaza por "o".
            rasgos += [f"{k} = {v.replace(' | ', ' o ')}"
                       for k, v in grupo["rasgos"].items()
                       if v != "cualquiera"]
            ejemplo = cobertura.formatear_respuestas(
                grupo["casos"][0]["respuestas"])
            agregar(f"| {numero} | {'; '.join(rasgos)} | "
                    f"{len(grupo['casos'])} | `{ejemplo}` |")
    agregar("")

    # --- Catálogo ----------------------------------------------------------
    agregar("## 7. Catálogo de plantas")
    agregar("")
    agregar("Fuente de toxicidad: ASPCA, base de datos de plantas tóxicas y no "
            "tóxicas (consulta: 9 nov 2026). La guaria morada no aparece por "
            "nombre; se trata como segura por género, porque ASPCA lista "
            "varias *Cattleya* (C. mossiae, C. trianaei, C. labiata) como no "
            "tóxicas.")
    agregar("")
    agregar("| Id | Nombre | Nombre científico | Toxicidad | Consejo |")
    agregar("|---|---|---|---|---|")
    for planta in sistema.CATALOGO:
        agregar(f"| {planta['id']} | {planta['nombre']} | "
                f"*{planta['cientifico']}* | {planta['toxicidad']} | "
                f"{planta['tip']} |")
    agregar("")
    return "\n".join(lineas)


if __name__ == "__main__":
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as archivo:
        archivo.write(generar())
    print(f"Se generó {ARCHIVO_SALIDA}.")
