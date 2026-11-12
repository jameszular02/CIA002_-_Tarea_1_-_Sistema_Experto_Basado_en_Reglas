# -*- coding: utf-8 -*-
"""Cobertura de la base de conocimiento.

Recorre TODAS las combinaciones posibles de respuestas (producto cartesiano
de las opciones de las 7 preguntas) y pasa cada una por el mismo motor que
usa el programa (resolver_consulta). Reporta cuántas terminan con una
recomendación, cuántas caen en un hueco conocido y cuántas quedan sin
cubrir, agrupadas para que se vea qué falta.

Uso:
    python cobertura.py            # resumen
    python cobertura.py --detalle  # además, cada combinación de hechos sin cubrir

Solo usa la biblioteca estándar.
"""

import itertools
import sys
from collections import Counter, defaultdict

import loria_james_tarea1 as sistema

# Hechos que se muestran al describir un grupo sin cubrir. Se excluyen zona,
# ubicacion, mascotas y experiencia porque las reglas finales no los miran
# directamente: ya están resumidos en clima, ambiente, restriccion y nivel.
HECHOS_DESCRIPTIVOS = ["luz", "clima", "restriccion", "nivel", "cuidado"]


def todas_las_respuestas():
    """Genera cada combinación de respuestas como un diccionario."""
    claves = [pregunta["clave"] for pregunta in sistema.PREGUNTAS]
    opciones = [[valor for valor, _ in pregunta["opciones"]]
                for pregunta in sistema.PREGUNTAS]
    for valores in itertools.product(*opciones):
        yield dict(zip(claves, valores))


def calcular_cobertura():
    """Clasifica todas las combinaciones y devuelve un resumen.

    Devuelve un diccionario con:
      total, con_recomendacion, en_hueco (Counter por id de hueco),
      sin_cubrir (lista de resultados), principales (Counter por regla).
    """
    resumen = {"total": 0, "con_recomendacion": 0, "en_hueco": Counter(),
               "sin_cubrir": [], "principales": Counter()}
    for respuestas in todas_las_respuestas():
        resultado = sistema.resolver_consulta(respuestas)
        resumen["total"] += 1
        if resultado["recomendaciones"]:
            resumen["con_recomendacion"] += 1
            principal = resultado["recomendaciones"][0]["regla"]["id"]
            resumen["principales"][principal] += 1
        elif resultado["hueco"]:
            resumen["en_hueco"][resultado["hueco"]["id"]] += 1
        else:
            resumen["sin_cubrir"].append(resultado)
    return resumen


def firma(resultado):
    """Resume un resultado en los hechos que importan para describir un grupo."""
    hechos = resultado["hechos"]
    return tuple(hechos[clave] for clave in ["ambiente", "objetivo"]
                 + HECHOS_DESCRIPTIVOS)


def factorizar(casos, factibles):
    """Divide un conjunto de casos en subgrupos describibles con rasgos.

    Un subgrupo es "describible" cuando sus firmas son exactamente TODAS las
    firmas factibles que cumplen sus rasgos (por ejemplo, "clima: cualquiera"
    debe significar de verdad cualquier clima). Si no lo es, se parte por el
    primer hecho con varios valores y después se vuelven a unir los pedazos
    que quedaron con los mismos rasgos.
    Devuelve una lista de (rasgos, casos), donde rasgos = {clave: set}.
    """
    claves = ["ambiente", "objetivo"] + HECHOS_DESCRIPTIVOS
    firmas = {firma(c) for c in casos}
    rasgos = {clave: {f[i] for f in firmas} for i, clave in enumerate(claves)}
    cubiertas = {f for f in factibles
                 if all(f[i] in rasgos[clave] for i, clave in enumerate(claves))}
    if cubiertas == firmas:
        return [(rasgos, casos)]

    for i, clave in enumerate(claves):
        if len(rasgos[clave]) < 2:
            continue
        pedazos = []
        for valor in sorted(rasgos[clave]):
            parte = [c for c in casos if firma(c)[i] == valor]
            pedazos.extend(factorizar(parte, factibles))
        # Unir pedazos que solo difieren en el valor de "clave".
        unidos = {}
        for sub_rasgos, sub_casos in pedazos:
            llave = tuple(frozenset(sub_rasgos[k]) for k in claves if k != clave)
            if llave in unidos:
                unidos[llave][0][clave] |= sub_rasgos[clave]
                unidos[llave][1].extend(sub_casos)
            else:
                unidos[llave] = ({k: set(v) for k, v in sub_rasgos.items()},
                                 list(sub_casos))
        return list(unidos.values())
    return [(rasgos, casos)]


def agrupar_sin_cubrir(sin_cubrir):
    """Agrupa los casos sin cubrir en patrones fáciles de leer.

    Para cada grupo indica qué valores toma cada hecho descriptivo; si toma
    todos los valores posibles se resume como "cualquiera".
    """
    factibles = {firma(sistema.resolver_consulta(r))
                 for r in todas_las_respuestas()}
    posibles = {p["clave"]: [v for v, _ in p["opciones"]]
                for p in sistema.PREGUNTAS}
    for clave, valores in sistema.HECHOS_DERIVADOS.items():
        posibles[clave] = list(valores)

    por_ambiente_objetivo = defaultdict(list)
    for resultado in sin_cubrir:
        hechos = resultado["hechos"]
        por_ambiente_objetivo[(hechos["ambiente"], hechos["objetivo"])].append(
            resultado)

    descripcion = []
    for (ambiente, objetivo), casos in por_ambiente_objetivo.items():
        for rasgos, sub_casos in factorizar(casos, factibles):
            texto = {}
            for clave in HECHOS_DESCRIPTIVOS:
                if set(posibles[clave]) <= rasgos[clave]:
                    texto[clave] = "cualquiera"
                else:
                    texto[clave] = " | ".join(v for v in posibles[clave]
                                               if v in rasgos[clave])
            descripcion.append({"ambiente": ambiente, "objetivo": objetivo,
                                "casos": sub_casos, "rasgos": texto})
    descripcion.sort(key=lambda g: -len(g["casos"]))
    return descripcion


def formatear_respuestas(respuestas):
    """Convierte unas respuestas en texto compacto clave=valor."""
    return ", ".join(f"{clave}={valor}" for clave, valor in respuestas.items())


def porcentaje(parte, total):
    """Porcentaje con un decimal."""
    return f"{100 * parte / total:.1f} %"


def imprimir_reporte(detalle=False):
    """Imprime el reporte de cobertura en la terminal."""
    sistema.validar_base_conocimiento()
    resumen = calcular_cobertura()
    total = resumen["total"]
    en_hueco = sum(resumen["en_hueco"].values())
    sin_cubrir = len(resumen["sin_cubrir"])
    sin_conclusion = en_hueco + sin_cubrir

    print("COBERTURA DE LA BASE DE CONOCIMIENTO")
    print("=" * 60)
    print(f"Combinaciones posibles de respuestas: {total}")
    print(f"  Con recomendación:  {resumen['con_recomendacion']:4d}  "
          f"({porcentaje(resumen['con_recomendacion'], total)})")
    print(f"  Sin conclusión:     {sin_conclusion:4d}  "
          f"({porcentaje(sin_conclusion, total)})")
    print(f"    - hueco conocido, con sugerencia específica: {en_hueco:4d}  "
          f"({porcentaje(en_hueco, total)})")
    print(f"    - sin cubrir, solo mensaje general:          {sin_cubrir:4d}  "
          f"({porcentaje(sin_cubrir, total)})")

    print("\nHuecos conocidos:")
    for hueco in sistema.HUECOS_CONOCIDOS:
        cantidad = resumen["en_hueco"][hueco["id"]]
        condiciones = ", ".join(f"{k}={v}" for k, v in hueco["si"].items())
        print(f"  {hueco['id']} ({condiciones}): {cantidad}")

    print("\nRecomendación principal por regla (casos con recomendación):")
    for id_regla, cantidad in sorted(resumen["principales"].items(),
                                     key=lambda x: int(x[0][1:])):
        print(f"  {id_regla}: {cantidad}")

    print("\nGrupos sin cubrir:")
    if not resumen["sin_cubrir"]:
        print("  (ninguno)")
    for numero, grupo in enumerate(
            agrupar_sin_cubrir(resumen["sin_cubrir"]), start=1):
        print(f"  {numero}. ambiente={grupo['ambiente']}, "
              f"objetivo={grupo['objetivo']}: {len(grupo['casos'])} casos")
        for clave, valores in grupo["rasgos"].items():
            print(f"       {clave}: {valores}")
        ejemplo = grupo["casos"][0]["respuestas"]
        print(f"       ejemplo: {formatear_respuestas(ejemplo)}")

    if detalle:
        print("\nDetalle: combinaciones de hechos sin cubrir")
        firmas = Counter(
            tuple(zip(["ambiente", "objetivo"] + HECHOS_DESCRIPTIVOS,
                      firma(r)))
            for r in resumen["sin_cubrir"])
        for firma, cantidad in sorted(firmas.items()):
            print(f"  {cantidad:3d}  " + ", ".join(f"{k}={v}"
                                                  for k, v in firma))


if __name__ == "__main__":
    imprimir_reporte(detalle="--detalle" in sys.argv)
