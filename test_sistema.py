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
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import redirect_stdout
from unittest import mock

import loria_james_tarea1 as sistema


def setUpModule():
    """Las pruebas comparan texto plano: se apagan los colores ANSI."""
    sistema.USAR_COLOR = False


# -----------------------------------------------------------------------------
# Los casos de prueba viven en el programa (CASOS_PRUEBA), así el modo
# --pruebas, casos_prueba.md y estas pruebas usan exactamente los mismos.
# -----------------------------------------------------------------------------
CASOS = {caso["id"]: caso for caso in sistema.CASOS_PRUEBA}
respuestas_desde_teclas = sistema.respuestas_desde_teclas


def resultado_de(id_caso):
    """Resuelve un caso de prueba por su id (A, B, ...)."""
    return sistema.resolver_consulta(
        respuestas_desde_teclas(CASOS[id_caso]["teclas"]))


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
        respuestas = respuestas_desde_teclas(CASOS["C"]
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
            CASOS["A"]["teclas"]))
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
                ids = [r["regla"]["id"] for r in resultado["visibles"]]
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
            CASOS["C"]["teclas"]))
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
            CASOS["B"]["teclas"]))
        texto = "\n".join(sistema.explicar(resultado))
        self.assertIn("No se aplicó R12: exige restriccion = ninguna, pero "
                      "restriccion = no_toxicas [de R7]", texto)

    def test_salida_sin_conclusion(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["G"]["teclas"]))
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
            CASOS["I"]["teclas"]))
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

    def test_r32_no_aplica_con_mascotas_y_r33_da_solo_areca(self):
        resultado = resultado_de("H")
        ids = [r["regla"]["id"] for r in resultado["recomendaciones"]]
        self.assertEqual(ids, ["R33"])
        self.assertEqual(resultado["recomendaciones"][0]["plantas"],
                         [("areca", None)])
        self.assertIn("No se aplicó R32: exige restriccion = ninguna, pero "
                      "restriccion = no_toxicas [de R7]",
                      sistema.explicar(resultado))

    def test_toda_regla_con_toxicas_exige_restriccion_ninguna(self):
        # Principio de diseño: una regla que concluye plantas tóxicas debe
        # exigir restriccion = ninguna (el filtro queda como respaldo).
        for regla in sistema.REGLAS:
            if regla["tipo"] != "final":
                continue
            if any(sistema.PLANTAS_POR_ID[p]["toxicidad"] == "toxica"
                   for p in regla["entonces"]):
                self.assertEqual(regla["si"].get("restriccion"), "ninguna",
                                 regla["id"])

    def test_aviso_amarillo_para_sin_registro(self):
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["F"]["teclas"]))
        salida = io.StringIO()
        with redirect_stdout(salida):
            sistema.mostrar_recomendacion(resultado)
        self.assertIn(sistema.AVISO_SIN_REGISTRO, salida.getvalue())


class TestPlantasRepetidas(unittest.TestCase):
    """La salida no repite una planta ya mostrada en una recomendación previa."""

    def test_quitar_repetidas_con_datos_de_prueba(self):
        def rec(id_regla, plantas):
            return {"regla": {"id": id_regla}, "excluidas": [],
                    "plantas": [(p, None) for p in plantas]}
        visibles = sistema.quitar_repetidas([
            rec("R1", ["rosa", "chinas"]),
            rec("R2", ["chinas", "hibisco"]),     # chinas se repite
            rec("R3", ["rosa", "hibisco"]),       # queda vacía: no se muestra
            rec("R4", ["areca"]),
        ])
        self.assertEqual([v["regla"]["id"] for v in visibles],
                         ["R1", "R2", "R4"])
        self.assertEqual(visibles[1]["plantas"], [("hibisco", None)])
        self.assertEqual(visibles[1]["repetidas"], ["chinas"])

    def test_ninguna_planta_se_repite_en_las_1296_combinaciones(self):
        for respuestas in todas_las_respuestas():
            resultado = sistema.resolver_consulta(respuestas)
            mostradas = [p for v in resultado["visibles"]
                         for p, _ in v["plantas"]]
            self.assertEqual(len(mostradas), len(set(mostradas)), respuestas)
            # La principal nunca pierde plantas.
            if resultado["recomendaciones"]:
                self.assertEqual(resultado["visibles"][0],
                                 dict(resultado["recomendaciones"][0],
                                      repetidas=[]))

    def test_caso_c_alternativa_r19_solo_muestra_hibisco(self):
        resultado = resultado_de("C")
        self.assertEqual(resultado["visibles"][1]["plantas"],
                         [("hibisco", None)])
        salida = io.StringIO()
        with redirect_stdout(salida):
            sistema.mostrar_recomendacion(resultado)
        alternativas = salida.getvalue().split("Alternativas:")[1]
        alternativas = alternativas.split("¿Por qué?")[0]
        self.assertIn("Amapola / hibisco", alternativas)
        self.assertNotIn("Veranera", alternativas)
        self.assertIn("De R19 se omiten plantas ya mostradas: Veranera, "
                      "Moño de señora", sistema.explicar(resultado))

    def test_alternativa_vacia_no_se_muestra(self):
        # Sombra + cerca viva sin mascotas: R32 (caña india, areca) es la
        # principal; R33 (solo areca) queda vacía y no se muestra.
        resultado = sistema.resolver_consulta(respuestas_desde_teclas(
            ["1", "3", "2", "2", "n", "3", "1"]))
        self.assertEqual([r["regla"]["id"]
                          for r in resultado["recomendaciones"]],
                         ["R32", "R33"])
        self.assertEqual([v["regla"]["id"] for v in resultado["visibles"]],
                         ["R32"])
        salida = io.StringIO()
        with redirect_stdout(salida):
            sistema.mostrar_recomendacion(resultado)
        self.assertNotIn("Alternativas:", salida.getvalue())
        self.assertIn("R33 no se muestra como alternativa: sus plantas ya "
                      "aparecen arriba (Palma areca)", salida.getvalue())


class TestModoPruebas(unittest.TestCase):
    """El modo --pruebas corre CASOS_PRUEBA y resume el resultado."""

    def test_todos_los_casos_correctos(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = sistema.main(["--pruebas"])
        self.assertEqual(codigo, 0)
        total = len(sistema.CASOS_PRUEBA)
        self.assertIn(f"{total}/{total} casos correctos", salida.getvalue())
        self.assertEqual(salida.getvalue().count("✅"), total)

    def test_un_caso_incorrecto_se_marca_con_x(self):
        malo = dict(sistema.CASOS_PRUEBA[0], principal="R13")
        casos = [malo] + sistema.CASOS_PRUEBA[1:]
        salida = io.StringIO()
        with mock.patch.object(sistema, "CASOS_PRUEBA", casos), \
                redirect_stdout(salida):
            codigo = sistema.ejecutar_casos_prueba()
        self.assertEqual(codigo, 1)
        self.assertIn("❌ Caso A", salida.getvalue())
        self.assertIn(f"{len(casos) - 1}/{len(casos)} casos correctos",
                      salida.getvalue())

    def test_argumento_desconocido_muestra_uso(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = sistema.main(["--otra-cosa"])
        self.assertEqual(codigo, 2)
        self.assertIn("--pruebas", salida.getvalue())

    def test_validacion_detecta_caso_con_tecla_invalida(self):
        malo = dict(sistema.CASOS_PRUEBA[0], teclas=["9"] * 7)
        with mock.patch.object(sistema, "CASOS_PRUEBA", [malo]):
            with self.assertRaisesRegex(sistema.BaseConocimientoInvalida,
                                        "Caso A"):
                sistema.validar_base_conocimiento()


class TestInterfazWeb(unittest.TestCase):
    """Modo --web: validación, conversión a JSON y servidor HTTP real."""

    RESPUESTAS_C = {"zona": "bajura_caliente", "ubicacion": "jardin",
                    "luz": "pleno_sol", "cuidado": "medio", "mascotas": "n",
                    "objetivo": "flores", "experiencia": "principiante"}

    @classmethod
    def setUpClass(cls):
        # Servidor real en un puerto libre (0) y un historial temporal.
        cls.carpeta = tempfile.TemporaryDirectory()
        cls.ruta_csv = os.path.join(cls.carpeta.name, "h.csv")
        cls.parche = mock.patch.object(sistema, "ARCHIVO_HISTORIAL",
                                       cls.ruta_csv)
        cls.parche.start()
        # Silencia el registro de peticiones mientras corren las pruebas.
        cls.silencio = mock.patch.object(sistema.ManejadorWeb, "log_message",
                                         lambda *args: None)
        cls.silencio.start()
        cls.servidor = sistema.crear_servidor(0)
        cls.hilo = threading.Thread(target=cls.servidor.serve_forever,
                                    daemon=True)
        cls.hilo.start()
        cls.base = f"http://127.0.0.1:{cls.servidor.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.silencio.stop()
        cls.parche.stop()
        cls.carpeta.cleanup()

    def pedir(self, ruta, datos=None, crudo=None):
        """Hace una petición y devuelve (código, cuerpo como texto)."""
        cuerpo = crudo if crudo is not None else (
            json.dumps(datos).encode("utf-8") if datos is not None else None)
        peticion = urllib.request.Request(
            self.base + ruta, data=cuerpo,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(peticion, timeout=5) as respuesta:
                return respuesta.status, respuesta.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_validar_respuestas_web(self):
        respuestas, errores = sistema.validar_respuestas_web(self.RESPUESTAS_C)
        self.assertEqual((respuestas, errores), (self.RESPUESTAS_C, []))
        malas = dict(self.RESPUESTAS_C, zona="marte")
        del malas["luz"]
        respuestas, errores = sistema.validar_respuestas_web(malas)
        self.assertIsNone(respuestas)
        self.assertEqual(len(errores), 2)
        self.assertIn("marte", errores[0])
        self.assertIn("Falta responder: ¿Cuánta luz", errores[1])
        self.assertEqual(sistema.validar_respuestas_web([1, 2])[1],
                         ["La consulta debe ser un objeto JSON."])

    def test_resultado_a_dict_muestra_el_encadenamiento(self):
        datos = sistema.resultado_a_dict(resultado_de("C"), True)
        self.assertEqual(datos["principal"]["id"], "R18")
        self.assertEqual([a["id"] for a in datos["alternativas"]], ["R19"])
        self.assertEqual([i["id"] for i in datos["intermedias"]],
                         ["R1", "R5", "R8", "R10"])
        self.assertIn("clima = calido [de R1]",
                      datos["finales"][0]["condiciones"])
        self.assertEqual(datos["principal"]["plantas"][2]["aviso_texto"],
                         sistema.AVISO_TOXICA)
        json.dumps(datos)                    # debe poder enviarse como JSON

    def test_pagina_principal(self):
        codigo, cuerpo = self.pedir("/")
        self.assertEqual(codigo, 200)
        self.assertIn("<!doctype html>", cuerpo)
        self.assertIn("¿Cuánta luz recibe ese lugar?", cuerpo)
        self.assertNotIn("__PREGUNTAS__", cuerpo)

    def test_consulta_valida_responde_y_guarda_historial(self):
        codigo, cuerpo = self.pedir("/api/consultar", self.RESPUESTAS_C)
        self.assertEqual(codigo, 200)
        datos = json.loads(cuerpo)
        self.assertEqual(datos["principal"]["id"], "R18")
        self.assertTrue(datos["guardado"])
        codigo, cuerpo = self.pedir("/api/historial")
        filas = json.loads(cuerpo)
        self.assertEqual(codigo, 200)
        self.assertTrue(filas[0]["recomendacion_principal"].startswith("R18"))
        with open(self.ruta_csv, newline="", encoding="utf-8") as archivo:
            self.assertEqual(next(csv.reader(archivo)),
                             sistema.ENCABEZADO_HISTORIAL)

    def test_consulta_sin_conclusion(self):
        respuestas = dict(self.RESPUESTAS_C, zona="valle_central",
                          ubicacion="interior", luz="poca_luz")
        codigo, cuerpo = self.pedir("/api/consultar", respuestas)
        datos = json.loads(cuerpo)
        self.assertEqual(codigo, 200)
        self.assertIsNone(datos["principal"])
        self.assertEqual(datos["hueco"], {"id": "H1"})

    def test_consultas_invalidas_dan_400(self):
        codigo, cuerpo = self.pedir("/api/consultar", {"zona": "marte"})
        self.assertEqual(codigo, 400)
        self.assertIn("errores", json.loads(cuerpo))
        codigo, _ = self.pedir("/api/consultar", crudo=b"no es json")
        self.assertEqual(codigo, 400)
        codigo, _ = self.pedir("/no-existe")
        self.assertEqual(codigo, 404)

    def test_puerto_invalido_muestra_uso(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = sistema.main(["--web", "abc"])
        self.assertEqual(codigo, 2)
        self.assertIn("--web", salida.getvalue())


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
            CASOS["C"]["teclas"]))
        resultado_g = sistema.resolver_consulta(respuestas_desde_teclas(
            CASOS["G"]["teclas"]))
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
            codigo = sistema.main([])
        return codigo, salida.getvalue()

    def test_dos_consultas_completas(self):
        entradas = (CASOS["C"]["teclas"] + ["s"]
                    + CASOS["G"]
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
