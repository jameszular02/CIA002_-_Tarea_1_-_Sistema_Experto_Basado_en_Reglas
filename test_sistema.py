# -*- coding: utf-8 -*-
"""Pruebas automáticas del sistema experto (solo biblioteca estándar).

Ejecutar con:
    python -m unittest            (descubre este archivo)
    python -m unittest -v         (muestra cada prueba)
"""

import csv
import io
import itertools
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import loria_james_tarea1 as sistema


def setUpModule():
    """Las pruebas comparan texto plano: se apagan los colores ANSI."""
    sistema.USAR_COLOR = False


# -----------------------------------------------------------------------------
# Casos de prueba (los mismos de casos_prueba.md).
# "teclas" es exactamente lo que se escribe en la terminal, en orden:
#   zona, ubicación, luz, cuidado, mascotas (s/n), objetivo, experiencia.
# -----------------------------------------------------------------------------
CASOS = {
    "a_interior_poca_luz_follaje": {
        "teclas": ["2", "1", "4", "2", "n", "2", "1"],
        "principal": "R12", "alternativas": ["R13"], "hueco": None},
    "b_interior_luz_indirecta_follaje_mascotas": {
        "teclas": ["2", "1", "3", "2", "s", "2", "1"],
        "principal": "R13", "alternativas": [], "hueco": None},
    "c_jardin_sol_bajura_flores": {
        "teclas": ["1", "3", "1", "2", "n", "1", "1"],
        "principal": "R18", "alternativas": ["R19"], "hueco": None},
    "d_jardin_semisombra_altura_flores": {
        "teclas": ["3", "3", "2", "2", "n", "1", "1"],
        "principal": "R24", "alternativas": ["R25"], "hueco": None},
    "e_balcon_sol_poco_cuidado_mascotas": {
        "teclas": ["2", "2", "1", "1", "s", "2", "1"],
        "principal": "R29", "alternativas": [], "hueco": None},
    "f_jardin_semisombra_bajura_flores_mascotas": {
        "teclas": ["1", "3", "2", "2", "s", "1", "1"],
        "principal": "R26", "alternativas": [], "hueco": None},
    "g_interior_poca_luz_flores_sin_conclusion": {
        "teclas": ["2", "1", "4", "2", "n", "1", "1"],
        "principal": None, "alternativas": [], "hueco": "H1"},
    "h_cerca_viva_sombra_mascotas_filtro": {
        "teclas": ["1", "3", "2", "2", "s", "3", "2"],
        "principal": "R32", "alternativas": [], "hueco": None},
    "i_sol_fresco_follaje_sin_cubrir": {
        "teclas": ["3", "2", "1", "2", "n", "2", "1"],
        "principal": None, "alternativas": [], "hueco": None},
}


def respuestas_desde_teclas(teclas):
    """Convierte la lista de teclas en el diccionario de respuestas."""
    respuestas = {}
    for pregunta, tecla in zip(sistema.PREGUNTAS, teclas):
        if pregunta["tipo"] == "sn":
            respuestas[pregunta["clave"]] = tecla
        else:
            respuestas[pregunta["clave"]] = (
                pregunta["opciones"][int(tecla) - 1][0])
    return respuestas


def todas_las_respuestas():
    """Las 1296 combinaciones posibles de respuestas."""
    claves = [p["clave"] for p in sistema.PREGUNTAS]
    opciones = [[v for v, _ in p["opciones"]] for p in sistema.PREGUNTAS]
    for valores in itertools.product(*opciones):
        yield dict(zip(claves, valores))


class TestBaseConocimiento(unittest.TestCase):
    """La base de conocimiento cumple el enunciado y la validación funciona."""

    def test_validacion_pasa(self):
        self.assertTrue(sistema.validar_base_conocimiento())

    def test_minimos_del_enunciado(self):
        finales = [r for r in sistema.REGLAS if r["tipo"] == "final"]
        self.assertGreaterEqual(len(sistema.REGLAS), 20)
        self.assertGreaterEqual(len(sistema.PREGUNTAS), 6)
        self.assertGreaterEqual(len({tuple(r["entonces"]) for r in finales}),
                                5)

    def test_cada_regla_tiene_id_condiciones_y_conclusion(self):
        for regla in sistema.REGLAS:
            self.assertRegex(regla["id"], r"^R\d+$")
            self.assertTrue(regla["si"])
            self.assertTrue(regla["entonces"])

    def test_detecta_id_duplicado(self):
        duplicada = dict(sistema.REGLAS[0])
        with mock.patch.object(sistema, "REGLAS",
                               sistema.REGLAS + [duplicada]):
            with self.assertRaisesRegex(sistema.BaseConocimientoInvalida,
                                        "duplicado: R1"):
                sistema.validar_base_conocimiento()

    def test_detecta_clave_y_valor_inexistentes(self):
        mala = {"id": "R99", "tipo": "final", "certeza": 50,
                "si": {"humedad": "alta", "luz": "neon"},
                "entonces": ["rosa"]}
        with mock.patch.object(sistema, "REGLAS", sistema.REGLAS + [mala]):
            with self.assertRaises(sistema.BaseConocimientoInvalida) as ctx:
                sistema.validar_base_conocimiento()
        self.assertIn("'humedad' no existe", str(ctx.exception))
        self.assertIn("'neon' no es válido", str(ctx.exception))

    def test_detecta_planta_fuera_del_catalogo(self):
        mala = {"id": "R99", "tipo": "final", "certeza": 50,
                "si": {"objetivo": "flores"}, "entonces": ["tulipan"]}
        with mock.patch.object(sistema, "REGLAS", sistema.REGLAS + [mala]):
            with self.assertRaisesRegex(sistema.BaseConocimientoInvalida,
                                        "tulipan"):
                sistema.validar_base_conocimiento()

    def test_detecta_minimo_de_reglas(self):
        with mock.patch.object(sistema, "REGLAS", sistema.REGLAS[:5]):
            with self.assertRaisesRegex(sistema.BaseConocimientoInvalida,
                                        "mínimo es 20"):
                sistema.validar_base_conocimiento()


class TestMotor(unittest.TestCase):
    """Encadenamiento hacia adelante, orden por certeza y desempates."""

    def test_encadenar_deduce_hechos_y_su_origen(self):
        respuestas = respuestas_desde_teclas(CASOS["c_jardin_sol_bajura_flores"]
                                             ["teclas"])
        hechos, origen, disparadas = sistema.encadenar(respuestas)
        self.assertEqual(hechos["clima"], "calido")
        self.assertEqual(hechos["ambiente"], "exterior_sol")
        self.assertEqual(origen["ambiente"], "R5")
        self.assertEqual(origen["zona"], "usuario")
        self.assertEqual([r["id"] for r in disparadas],
                         ["R1", "R5", "R8", "R10"])

    def test_ninguna_regla_se_dispara_dos_veces(self):
        for respuestas in todas_las_respuestas():
            _, _, disparadas = sistema.encadenar(respuestas)
            ids = [r["id"] for r in disparadas]
            self.assertEqual(len(ids), len(set(ids)))

    def test_encadenar_llega_a_punto_fijo_con_hecho_intermedio(self):
        # Regla de prueba que depende de un hecho DERIVADO (clima), escrita
        # antes que la regla que lo produce: obliga a una segunda vuelta.
        reglas = [
            {"id": "R2", "tipo": "intermedia", "si": {"clima": "calido"},
             "entonces": ("nivel", "facil")},
            {"id": "R1", "tipo": "intermedia",
             "si": {"zona": "bajura_caliente"},
             "entonces": ("clima", "calido")},
        ]
        hechos, origen, disparadas = sistema.encadenar(
            {"zona": "bajura_caliente"}, reglas)
        self.assertEqual(hechos["nivel"], "facil")
        self.assertEqual(origen["nivel"], "R2")
        self.assertEqual([r["id"] for r in disparadas], ["R1", "R2"])

    def test_orden_por_certeza(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["a_interior_poca_luz_follaje"]["teclas"]))
        certezas = [r["regla"]["certeza"]
                    for r in resultado["recomendaciones"]]
        self.assertEqual(certezas, sorted(certezas, reverse=True))

    def test_desempate_por_cantidad_de_condiciones(self):
        reglas = [
            {"id": "R1", "tipo": "final", "certeza": 80,
             "si": {"objetivo": "flores"}, "entonces": ["rosa"]},
            {"id": "R2", "tipo": "final", "certeza": 80,
             "si": {"objetivo": "flores", "clima": ["calido", "fresco"]},
             "entonces": ["chinas"]},
        ]
        orden = sistema.evaluar({"objetivo": "flores", "clima": "calido"},
                                reglas)
        self.assertEqual([r["id"] for r in orden], ["R2", "R1"])

    def test_desempate_por_id_menor(self):
        # R22 y R29: misma certeza (80) y 2 condiciones cada una.
        respuestas = respuestas_desde_teclas(
            ["2", "2", "1", "1", "s", "3", "1"])
        orden = [r["regla"]["id"] for r in
                 sistema.resolver_consulta(respuestas)["recomendaciones"]]
        self.assertEqual(orden, ["R22", "R29"])


class TestCasos(unittest.TestCase):
    """Los casos de casos_prueba.md, llamando al motor directamente."""

    def test_casos(self):
        for nombre, caso in CASOS.items():
            with self.subTest(caso=nombre):
                resultado = sistema.resolver_consulta(
                    respuestas_desde_teclas(caso["teclas"]))
                ids = [r["regla"]["id"]
                       for r in resultado["recomendaciones"]]
                self.assertEqual(ids[:1], [caso["principal"]]
                                 if caso["principal"] else [])
                self.assertEqual(ids[1:], caso["alternativas"])
                hueco = resultado["hueco"]["id"] if resultado["hueco"] else None
                self.assertEqual(hueco, caso["hueco"])

    def test_teclas_producen_las_respuestas_esperadas(self):
        # Simula la terminal con las teclas documentadas.
        for nombre, caso in CASOS.items():
            with self.subTest(caso=nombre):
                with mock.patch("builtins.input", side_effect=caso["teclas"]), \
                        redirect_stdout(io.StringIO()):
                    respuestas = sistema.recolectar_hechos()
                self.assertEqual(respuestas,
                                 respuestas_desde_teclas(caso["teclas"]))

    def test_explicacion_estilo_mycin(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["c_jardin_sol_bajura_flores"]["teclas"]))
        lineas = sistema.explicar(resultado)
        self.assertIn("Se activó R1 porque: zona = bajura_caliente → "
                      "clima = calido", lineas)
        self.assertIn("Se activó R5 porque: ubicacion = jardin y luz = "
                      "pleno_sol → ambiente = exterior_sol", lineas)
        self.assertIn("Se activó R18 (90%) porque: ambiente = exterior_sol "
                      "[de R5], clima = calido [de R1], objetivo = flores, "
                      "restriccion = ninguna [de R8]", lineas)

    def test_explicacion_de_reglas_excluidas_por_mascotas(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["b_interior_luz_indirecta_follaje_mascotas"]["teclas"]))
        texto = "\n".join(sistema.explicar(resultado))
        self.assertIn("No se aplicó R12: exige restriccion = ninguna, pero "
                      "restriccion = no_toxicas [de R7]", texto)

    def test_salida_sin_conclusion(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["g_interior_poca_luz_flores_sin_conclusion"]["teclas"]))
        salida = io.StringIO()
        with redirect_stdout(salida):
            sistema.mostrar_recomendacion(resultado)
        texto = salida.getvalue()
        self.assertIn("Sin conclusión", texto)
        self.assertIn("ambiente = interior", texto)
        self.assertIn("Pruebe con plantas de follaje", texto)
        self.assertNotIn("Recomendación principal", texto)

    def test_salida_sin_cubrir_usa_mensaje_general(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["i_sol_fresco_follaje_sin_cubrir"]["teclas"]))
        salida = io.StringIO()
        with redirect_stdout(salida):
            sistema.mostrar_recomendacion(resultado)
        self.assertIn(sistema.SUGERENCIA_GENERAL, salida.getvalue())


class TestFiltroSeguridad(unittest.TestCase):
    """El filtro nunca deja pasar una planta tóxica cuando hay mascotas."""

    def test_ninguna_toxica_con_mascotas_en_las_1296_combinaciones(self):
        for respuestas in todas_las_respuestas():
            if respuestas["mascotas"] != "s":
                continue
            resultado = sistema.resolver_consulta(respuestas)
            for recomendacion in resultado["recomendaciones"]:
                for id_planta, _ in recomendacion["plantas"]:
                    self.assertNotEqual(
                        sistema.PLANTAS_POR_ID[id_planta]["toxicidad"],
                        "toxica", f"{id_planta} con {respuestas}")

    def test_filtro_quita_toxicas_aunque_la_regla_este_mal_escrita(self):
        # Una regla "mal escrita" que recomienda tóxicas sin restricción.
        mala = {"id": "R99", "tipo": "final", "certeza": 99,
                "si": {}, "entonces": ["telefono", "rosa", "veranera"]}
        solo_toxicas = {"id": "R98", "tipo": "final", "certeza": 99,
                        "si": {}, "entonces": ["telefono", "sabila"]}
        recomendaciones = sistema.filtrar_por_seguridad(
            [mala, solo_toxicas], {"restriccion": "no_toxicas"})
        self.assertEqual(len(recomendaciones), 1)    # R98 queda vacía
        self.assertEqual(recomendaciones[0]["plantas"],
                         [("rosa", None), ("veranera", "sin_registro")])
        self.assertEqual(recomendaciones[0]["excluidas"], ["telefono"])

    def test_sin_mascotas_las_toxicas_llevan_aviso(self):
        regla = {"id": "R99", "tipo": "final", "certeza": 99, "si": {},
                 "entonces": ["telefono", "rosa"]}
        recomendaciones = sistema.filtrar_por_seguridad(
            [regla], {"restriccion": "ninguna"})
        self.assertEqual(recomendaciones[0]["plantas"],
                         [("telefono", "toxica"), ("rosa", None)])

    def test_r32_con_mascotas_quita_cana_india(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["h_cerca_viva_sombra_mascotas_filtro"]["teclas"]))
        recomendacion = resultado["recomendaciones"][0]
        self.assertEqual(recomendacion["plantas"], [("areca", None)])
        self.assertEqual(recomendacion["excluidas"], ["cana_india"])

    def test_aviso_amarillo_para_sin_registro(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["f_jardin_semisombra_bajura_flores_mascotas"]["teclas"]))
        salida = io.StringIO()
        with redirect_stdout(salida):
            sistema.mostrar_recomendacion(resultado)
        self.assertIn(sistema.AVISO_SIN_REGISTRO, salida.getvalue())


class TestEntradas(unittest.TestCase):
    """Validación de entradas simulando input() con unittest.mock.patch."""

    def preguntar_con(self, entradas, pregunta):
        """Ejecuta preguntar() con entradas simuladas; devuelve (valor, texto)."""
        salida = io.StringIO()
        with mock.patch("builtins.input", side_effect=entradas) as falso, \
                redirect_stdout(salida):
            valor = sistema.preguntar(pregunta)
        return valor, salida.getvalue(), falso.call_count

    def test_menu_rechaza_vacio_letras_y_fuera_de_rango(self):
        zona = sistema.PREGUNTAS[0]
        valor, texto, llamadas = self.preguntar_con(
            ["", "abc", "9", "0", "-1", " 2 "], zona)
        self.assertEqual(valor, "valle_central")
        self.assertEqual(llamadas, 6)
        self.assertIn("No escribió nada", texto)
        self.assertIn("«abc» no es un número", texto)
        self.assertIn("La opción 9 no existe", texto)
        self.assertIn("La opción 0 no existe", texto)
        self.assertIn("«-1» no es un número", texto)

    def test_pregunta_s_n(self):
        mascotas = next(p for p in sistema.PREGUNTAS
                        if p["clave"] == "mascotas")
        valor, texto, llamadas = self.preguntar_con(["x", "", "Sí"], mascotas)
        self.assertEqual(valor, "s")
        self.assertEqual(llamadas, 3)
        self.assertIn("«x» no es válido", texto)

    def test_interpretar_si_no(self):
        for texto, esperado in [("s", "s"), ("SI", "s"), ("sí", "s"),
                                ("n", "n"), ("No", "n"), ("talvez", None),
                                ("", None)]:
            self.assertEqual(sistema.interpretar_si_no(texto), esperado)


class TestHistorial(unittest.TestCase):
    """El historial CSV se escribe con encabezado y una fila por consulta."""

    def test_csv_se_escribe(self):
        resultado_c = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["c_jardin_sol_bajura_flores"]["teclas"]))
        resultado_g = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["g_interior_poca_luz_flores_sin_conclusion"]["teclas"]))
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "historial.csv")
            self.assertTrue(sistema.guardar_historial(resultado_c, ruta))
            self.assertTrue(sistema.guardar_historial(resultado_g, ruta))
            with open(ruta, newline="", encoding="utf-8") as archivo:
                filas = list(csv.reader(archivo))
        self.assertEqual(filas[0], sistema.ENCABEZADO_HISTORIAL)
        self.assertEqual(len(filas), 3)          # encabezado + 2 consultas
        self.assertIn("zona=bajura_caliente", filas[1][1])
        self.assertIn("ambiente=exterior_sol", filas[1][2])
        self.assertEqual(filas[1][3], "R1 R5 R8 R10 R18 R19")
        self.assertTrue(filas[1][4].startswith("R18 (90%): Veranera"))
        self.assertEqual(filas[2][4], "Sin conclusión (H1)")


class TestProgramaPrincipal(unittest.TestCase):
    """El programa corre de principio a fin y maneja Ctrl+C."""

    def ejecutar_main(self, entradas):
        """Corre main() con entradas simuladas y un historial temporal."""
        salida = io.StringIO()
        with tempfile.TemporaryDirectory() as carpeta, \
                mock.patch.object(sistema, "ARCHIVO_HISTORIAL",
                                  os.path.join(carpeta, "h.csv")), \
                mock.patch("builtins.input", side_effect=entradas), \
                redirect_stdout(salida):
            codigo = sistema.main()
        return codigo, salida.getvalue()

    def test_dos_consultas_completas(self):
        entradas = (CASOS["c_jardin_sol_bajura_flores"]["teclas"] + ["s"]
                    + CASOS["g_interior_poca_luz_flores_sin_conclusion"]
                    ["teclas"] + ["n"])
        codigo, texto = self.ejecutar_main(entradas)
        self.assertEqual(codigo, 0)
        self.assertIn("Recomendación principal (R18, certeza 90%)", texto)
        self.assertIn("Sin conclusión", texto)
        self.assertIn("Gracias por usar el recomendador", texto)

    def test_ctrl_c_sale_limpio(self):
        codigo, texto = self.ejecutar_main(KeyboardInterrupt())
        self.assertEqual(codigo, 0)
        self.assertIn("Consulta interrumpida", texto)


if __name__ == "__main__":
    unittest.main()
