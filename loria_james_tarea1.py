# -*- coding: utf-8 -*-
# =============================================================================
# Nombre:  James Loria
# Curso:   CIA02 – Introducción a la IA, UCreativa
# Tema 3:  Recomendador de plantas ornamentales para hogares costarricenses
# Fecha:   12 de noviembre de 2026
# Fuente de toxicidad: ASPCA, base de datos de plantas tóxicas y no tóxicas
#                      (consulta: 9 nov 2026).
#
# Sistema experto basado en reglas (IA simbólica). La base de conocimiento
# (catálogo, preguntas y reglas) está escrita como DATOS; el motor de
# inferencia es un conjunto de funciones que recorren esos datos. No hay un
# "if" por regla: agregar una regla nueva es agregar un diccionario.
#
# Uso:  python loria_james_tarea1.py            consulta en la terminal
#       python loria_james_tarea1.py --web      interfaz web en el navegador
#       python loria_james_tarea1.py --pruebas  casos de prueba integrados
# Solo usa la biblioteca estándar de Python (3.10 o superior).
# =============================================================================

import csv
import html
import json
import os
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


# =============================================================================
# 1. Configuración y colores
# =============================================================================

# Interruptor general: si la terminal no muestra bien los colores, se pone en
# False y el programa imprime texto plano.
USAR_COLOR = True

# Códigos de escape ANSI. Funcionan directo en la terminal de Codespaces.
VERDE = "\033[32m"
AMARILLO = "\033[33m"
ROJO = "\033[31m"
CIAN = "\033[36m"
NEGRITA = "\033[1m"
RESET = "\033[0m"

# Archivo donde se guarda el historial de consultas (extra opcional).
ARCHIVO_HISTORIAL = "historial_consultas.csv"

# Mínimos que exige el enunciado; validar_base_conocimiento() los verifica.
MINIMO_REGLAS = 20
MINIMO_PREGUNTAS = 6
MINIMO_CONCLUSIONES = 5


def color(texto, *estilos):
    """Envuelve un texto con códigos ANSI si USAR_COLOR está activo.

    Se centraliza aquí para que apagar los colores sea cambiar una sola
    constante y no tocar cada print del programa.
    """
    if not USAR_COLOR or not estilos:
        return texto
    return "".join(estilos) + texto + RESET


# =============================================================================
# 2. Catálogo de plantas
# =============================================================================
# Cada planta es un diccionario. Las reglas finales solo guardan el "id"; el
# nombre, el nombre científico, la toxicidad y el consejo se buscan aquí. Así
# un dato de una planta se corrige en un solo lugar.
#
# toxicidad:
#   "segura"       -> ASPCA la lista como no tóxica para perros y gatos.
#   "toxica"       -> ASPCA la lista como tóxica.
#   "sin_registro" -> ASPCA no tiene registro; no se asume que sea segura.

CATALOGO = [
    # --- Plantas que ASPCA registra como tóxicas ---------------------------
    {"id": "telefono", "nombre": "Teléfono", "cientifico": "Epipremnum aureum",
     "toxicidad": "toxica",
     "tip": "Riegue cuando el sustrato esté seco; tolera poca luz."},
    {"id": "lengua_suegra", "nombre": "Lengua de suegra",
     "cientifico": "Sansevieria trifasciata", "toxicidad": "toxica",
     "tip": "Riegue cada 2–3 semanas; el exceso de agua pudre la raíz."},
    {"id": "zamioculca", "nombre": "Zamioculca",
     "cientifico": "Zamioculcas zamiifolia", "toxicidad": "toxica",
     "tip": "Riego escaso; ideal para rincones con poca luz."},
    {"id": "mano_tigre", "nombre": "Mano de tigre",
     "cientifico": "Monstera deliciosa", "toxicidad": "toxica",
     "tip": "Dele un tutor para trepar y luz indirecta brillante."},
    {"id": "cuna_moises", "nombre": "Cuna de Moisés",
     "cientifico": "Spathiphyllum spp.", "toxicidad": "toxica",
     "tip": "Si se marchita está pidiendo agua; florece con luz indirecta."},
    {"id": "anturio", "nombre": "Anturio", "cientifico": "Anthurium spp.",
     "toxicidad": "toxica",
     "tip": "Sustrato aireado y humedad; evite el sol directo."},
    {"id": "cana_india", "nombre": "Caña india",
     "cientifico": "Dracaena fragrans", "toxicidad": "toxica",
     "tip": "Muy resistente; tolera sol y sombra."},
    {"id": "croton", "nombre": "Crotón", "cientifico": "Codiaeum variegatum",
     "toxicidad": "toxica",
     "tip": "A más sol, colores más intensos; su savia irrita la piel."},
    {"id": "itabo", "nombre": "Itabo", "cientifico": "Yucca guatemalensis",
     "toxicidad": "toxica",
     "tip": "Cerca viva casi sin riego; se siembra por estaca."},
    {"id": "hortensia", "nombre": "Hortensia",
     "cientifico": "Hydrangea macrophylla", "toxicidad": "toxica",
     "tip": "Semisombra y suelo húmedo; el color de la flor depende del pH."},
    {"id": "azalea", "nombre": "Azalea", "cientifico": "Rhododendron spp.",
     "toxicidad": "toxica",
     "tip": "Suelo ácido, semisombra y clima fresco."},
    {"id": "begonia", "nombre": "Begonia", "cientifico": "Begonia spp.",
     "toxicidad": "toxica",
     "tip": "Semisombra; evite mojar las hojas."},
    {"id": "ave_paraiso", "nombre": "Ave del paraíso",
     "cientifico": "Strelitzia reginae", "toxicidad": "toxica",
     "tip": "Pleno sol y riego moderado; tarda en dar su primera flor."},
    {"id": "sabila", "nombre": "Sábila", "cientifico": "Aloe vera",
     "toxicidad": "toxica",
     "tip": "Sol y riego escaso en sustrato arenoso."},

    # --- Plantas que ASPCA registra como no tóxicas -------------------------
    {"id": "mala_madre", "nombre": "Mala madre",
     "cientifico": "Chlorophytum comosum", "toxicidad": "segura",
     "tip": "Ideal colgante; sus hijos se propagan fácil."},
    {"id": "peperomia", "nombre": "Peperomia", "cientifico": "Peperomia spp.",
     "toxicidad": "segura",
     "tip": "Riego moderado; sus hojas carnosas guardan agua."},
    {"id": "palma_salon", "nombre": "Palma de salón",
     "cientifico": "Chamaedorea elegans", "toxicidad": "segura",
     "tip": "Tolera poca luz; mantenga el sustrato apenas húmedo."},
    {"id": "areca", "nombre": "Palma areca", "cientifico": "Dypsis lutescens",
     "toxicidad": "segura",
     "tip": "Al aire libre tolera sol si se riega bien; en interior prefiere "
            "luz indirecta brillante."},
    {"id": "helecho", "nombre": "Helecho",
     "cientifico": "Nephrolepis exaltata", "toxicidad": "segura",
     "tip": "Humedad constante; ideal en baños o corredores."},
    {"id": "calatea", "nombre": "Calatea", "cientifico": "Calathea spp.",
     "toxicidad": "segura",
     "tip": "Humedad alta y agua sin cloro; enrolla las hojas si le falta agua."},
    {"id": "phalaenopsis", "nombre": "Orquídea mariposa",
     "cientifico": "Phalaenopsis spp.", "toxicidad": "segura",
     "tip": "Riego semanal en corteza; luz indirecta."},
    {"id": "bromelia", "nombre": "Bromelia",
     "cientifico": "familia Bromeliaceae", "toxicidad": "segura",
     "tip": "Cambie el agua del centro cada semana para evitar zancudos."},
    # Guaria morada: ASPCA no la lista por nombre, pero sí lista varias
    # Cattleya (C. mossiae, C. trianaei, C. labiata) como no tóxicas. Por
    # pertenecer al mismo grupo se trata como "segura" por género.
    {"id": "guaria_morada", "nombre": "Guaria morada",
     "cientifico": "Guarianthe skinneri", "toxicidad": "segura",
     "tip": "Amárrela a un tronco con luz filtrada; es la flor nacional."},
    {"id": "hibisco", "nombre": "Amapola / hibisco",
     "cientifico": "Hibiscus rosa-sinensis", "toxicidad": "segura",
     "tip": "Pleno sol y riego regular; se poda para formar seto."},
    {"id": "chinas", "nombre": "Chinas", "cientifico": "Impatiens walleriana",
     "toxicidad": "segura",
     "tip": "Semisombra y riego frecuente; no tolera sol fuerte."},
    {"id": "rosa", "nombre": "Rosa", "cientifico": "Rosa spp.",
     "toxicidad": "segura",
     "tip": "Pleno sol y poda tras cada floración; cuidado con las espinas."},
    {"id": "echeveria", "nombre": "Echeveria", "cientifico": "Echeveria spp.",
     "toxicidad": "segura",
     "tip": "Sustrato muy drenado; protéjala de la lluvia directa."},

    # --- Plantas sin registro en ASPCA ---------------------------------------
    {"id": "veranera", "nombre": "Veranera", "cientifico": "Bougainvillea spp.",
     "toxicidad": "sin_registro",
     "tip": "Florece más con poco riego y pleno sol; cuidado con las espinas "
            "y la savia."},
    {"id": "mono_senora", "nombre": "Moño de señora",
     "cientifico": "Mussaenda erythrophylla", "toxicidad": "sin_registro",
     "tip": "Sol o semisombra; se propaga fácil por esquejes."},
    {"id": "heliconia", "nombre": "Platanilla / heliconia",
     "cientifico": "Heliconia spp.", "toxicidad": "sin_registro",
     "tip": "Semisombra, suelo húmedo y rico en materia orgánica."},
]

# Índice para buscar una planta por su id en tiempo constante.
PLANTAS_POR_ID = {planta["id"]: planta for planta in CATALOGO}

TOXICIDADES_VALIDAS = ("segura", "toxica", "sin_registro")


# =============================================================================
# 3. Preguntas
# =============================================================================
# Cada pregunta define la clave del hecho que produce, el texto que ve el
# usuario y sus opciones como pares (valor interno, texto visible).
#   tipo "menu" -> se responde con el número de la opción.
#   tipo "sn"   -> se responde con s o n.

PREGUNTAS = [
    {"clave": "zona", "tipo": "menu",
     "texto": "¿En qué zona vive?",
     "opciones": [
         ("bajura_caliente", "Bajura caliente (menos de 800 msnm)"),
         ("valle_central", "Valle Central (entre 800 y 1500 msnm)"),
         ("altura_fria", "Zona alta y fría (más de 1500 msnm)"),
     ]},
    {"clave": "ubicacion", "tipo": "menu",
     "texto": "¿Dónde estará la planta?",
     "opciones": [
         ("interior", "Dentro de la casa"),
         ("balcon_terraza", "Balcón o terraza"),
         ("jardin", "Jardín"),
     ]},
    {"clave": "luz", "tipo": "menu",
     "texto": "¿Cuánta luz recibe ese lugar?",
     "opciones": [
         ("pleno_sol", "Pleno sol (sol directo varias horas)"),
         ("semisombra", "Semisombra (sol solo una parte del día)"),
         ("luz_indirecta", "Luz indirecta (claridad, sin sol directo)"),
         ("poca_luz", "Poca luz (rincón oscuro)"),
     ]},
    {"clave": "cuidado", "tipo": "menu",
     "texto": "¿Cuánto tiempo puede dedicarle?",
     "opciones": [
         ("poco", "Poco"),
         ("medio", "Medio"),
         ("mucho", "Mucho"),
     ]},
    {"clave": "mascotas", "tipo": "sn",
     "texto": "¿Hay mascotas o niños pequeños en casa?",
     "opciones": [
         ("s", "Sí"),
         ("n", "No"),
     ]},
    {"clave": "objetivo", "tipo": "menu",
     "texto": "¿Qué busca?",
     "opciones": [
         ("flores", "Flores"),
         ("follaje", "Follaje (hojas decorativas)"),
         ("cerca_viva", "Cerca viva"),
     ]},
    {"clave": "experiencia", "tipo": "menu",
     "texto": "¿Cuál es su experiencia con plantas?",
     "opciones": [
         ("principiante", "Principiante"),
         ("con_experiencia", "Con experiencia"),
     ]},
]

# Hechos que el usuario NO responde: los deducen las reglas intermedias.
# Se declaran aquí, con un texto legible para cada valor, para que la
# validación detecte errores de escritura en las reglas.
HECHOS_DERIVADOS = {
    "clima": {"calido": "cálido", "templado": "templado",
              "fresco": "fresco"},
    "ambiente": {"interior": "interior",
                 "exterior_sol": "exterior con sol",
                 "exterior_sombra": "exterior con sombra"},
    "restriccion": {"no_toxicas": "solo plantas no tóxicas",
                    "ninguna": "ninguna"},
    "nivel": {"facil": "fácil", "avanzado": "avanzado"},
}


# =============================================================================
# 4. Reglas
# =============================================================================
# Formato de cada regla:
#   "id":        identificador único (R1, R2, ...).
#   "tipo":      "intermedia" (deduce un hecho nuevo) o "final" (recomienda).
#   "si":        condiciones {clave: valor}. Si el valor es una LISTA, basta
#                con que el hecho tenga cualquiera de esos valores. Así una
#                sola regla cubre varios casos sin duplicarla.
#   "entonces":  intermedia -> (clave, valor) del hecho nuevo.
#                final      -> lista de ids del catálogo.
#   "certeza":   (solo finales) confianza de 0 a 100.
#
# Principio de diseño de la restricción por mascotas:
#   - Las reglas que concluyen plantas tóxicas llevan restriccion = ninguna,
#     así la explicación deja claro por qué no aplican cuando hay mascotas.
#   - Las reglas que solo concluyen plantas "segura" o "sin_registro" no
#     llevan esa condición: sirven para cualquier hogar. El filtro de
#     seguridad (sección 5) igual revisa cada planta y agrega los avisos.
#   - Si una situación tiene plantas tóxicas y seguras, se escriben dos
#     reglas (por ejemplo R32 y R33): una con restriccion = ninguna y todas
#     las plantas, y otra sin restricción solo con las seguras.

EXTERIOR = ["balcon_terraza", "jardin"]
CALIDO_O_TEMPLADO = ["calido", "templado"]
# Dentro de la casa, la "semisombra" equivale a una luz indirecta media: por
# eso las reglas de interior que aceptan luz indirecta también la aceptan.
LUZ_INTERIOR_MEDIA = ["luz_indirecta", "semisombra"]
LUZ_INTERIOR_SUAVE = ["poca_luz", "luz_indirecta", "semisombra"]

REGLAS = [
    # --- Reglas intermedias: traducen respuestas en hechos ------------------
    {"id": "R1", "tipo": "intermedia",
     "si": {"zona": "bajura_caliente"}, "entonces": ("clima", "calido")},
    {"id": "R2", "tipo": "intermedia",
     "si": {"zona": "valle_central"}, "entonces": ("clima", "templado")},
    {"id": "R3", "tipo": "intermedia",
     "si": {"zona": "altura_fria"}, "entonces": ("clima", "fresco")},
    {"id": "R4", "tipo": "intermedia",
     "si": {"ubicacion": "interior"}, "entonces": ("ambiente", "interior")},
    {"id": "R5", "tipo": "intermedia",
     "si": {"ubicacion": EXTERIOR, "luz": "pleno_sol"},
     "entonces": ("ambiente", "exterior_sol")},
    {"id": "R6", "tipo": "intermedia",
     "si": {"ubicacion": EXTERIOR,
            "luz": ["semisombra", "luz_indirecta", "poca_luz"]},
     "entonces": ("ambiente", "exterior_sombra")},
    {"id": "R7", "tipo": "intermedia",
     "si": {"mascotas": "s"}, "entonces": ("restriccion", "no_toxicas")},
    {"id": "R8", "tipo": "intermedia",
     "si": {"mascotas": "n"}, "entonces": ("restriccion", "ninguna")},
    {"id": "R9", "tipo": "intermedia",
     "si": {"cuidado": "poco"}, "entonces": ("nivel", "facil")},
    {"id": "R10", "tipo": "intermedia",
     "si": {"cuidado": ["medio", "mucho"], "experiencia": "principiante"},
     "entonces": ("nivel", "facil")},
    {"id": "R11", "tipo": "intermedia",
     "si": {"cuidado": ["medio", "mucho"], "experiencia": "con_experiencia"},
     "entonces": ("nivel", "avanzado")},

    # --- Reglas finales: interior -------------------------------------------
    {"id": "R12", "tipo": "final", "certeza": 90,
     "si": {"ambiente": "interior", "luz": LUZ_INTERIOR_SUAVE,
            "restriccion": "ninguna", "objetivo": "follaje"},
     "entonces": ["lengua_suegra", "zamioculca", "telefono"]},
    {"id": "R13", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "interior", "luz": LUZ_INTERIOR_SUAVE,
            "objetivo": "follaje"},
     "entonces": ["mala_madre", "peperomia", "palma_salon"]},
    {"id": "R14", "tipo": "final", "certeza": 80,
     "si": {"ambiente": "interior", "luz": LUZ_INTERIOR_MEDIA,
            "nivel": "avanzado", "restriccion": "ninguna",
            "objetivo": "follaje"},
     "entonces": ["mano_tigre"]},
    {"id": "R15", "tipo": "final", "certeza": 80,
     "si": {"ambiente": "interior", "luz": LUZ_INTERIOR_MEDIA,
            "nivel": "avanzado", "objetivo": "follaje"},
     "entonces": ["calatea", "helecho", "areca"]},
    {"id": "R16", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "interior", "luz": LUZ_INTERIOR_MEDIA,
            "restriccion": "ninguna", "objetivo": "flores"},
     "entonces": ["cuna_moises", "anturio"]},
    {"id": "R17", "tipo": "final", "certeza": 80,
     "si": {"ambiente": "interior", "luz": LUZ_INTERIOR_MEDIA,
            "objetivo": "flores"},
     "entonces": ["phalaenopsis", "bromelia"]},

    # --- Reglas finales: exterior con sol -----------------------------------
    {"id": "R18", "tipo": "final", "certeza": 90,
     "si": {"ambiente": "exterior_sol", "clima": CALIDO_O_TEMPLADO,
            "objetivo": "flores", "restriccion": "ninguna"},
     "entonces": ["veranera", "mono_senora", "ave_paraiso"]},
    {"id": "R19", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "exterior_sol", "clima": CALIDO_O_TEMPLADO,
            "objetivo": "flores"},
     "entonces": ["hibisco", "veranera", "mono_senora"]},
    {"id": "R20", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "exterior_sol", "clima": CALIDO_O_TEMPLADO,
            "objetivo": "follaje", "restriccion": "ninguna"},
     "entonces": ["croton", "cana_india"]},
    {"id": "R21", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "exterior_sol", "objetivo": "cerca_viva",
            "clima": CALIDO_O_TEMPLADO, "restriccion": "ninguna"},
     "entonces": ["itabo", "cana_india"]},
    {"id": "R22", "tipo": "final", "certeza": 80,
     "si": {"ambiente": "exterior_sol", "objetivo": "cerca_viva"},
     "entonces": ["hibisco", "areca"]},
    {"id": "R23", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "exterior_sol", "clima": "fresco",
            "objetivo": "flores"},
     "entonces": ["rosa"]},

    # --- Reglas finales: exterior con sombra --------------------------------
    {"id": "R24", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "exterior_sombra", "clima": "fresco",
            "objetivo": "flores", "restriccion": "ninguna"},
     "entonces": ["hortensia", "azalea", "begonia"]},
    {"id": "R25", "tipo": "final", "certeza": 80,
     "si": {"ambiente": "exterior_sombra", "clima": ["templado", "fresco"],
            "objetivo": "flores"},
     "entonces": ["chinas"]},
    {"id": "R26", "tipo": "final", "certeza": 75,
     "si": {"ambiente": "exterior_sombra", "clima": "calido",
            "objetivo": "flores"},
     "entonces": ["heliconia"]},
    {"id": "R27", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "exterior_sombra", "objetivo": "follaje"},
     "entonces": ["helecho", "calatea", "bromelia"]},
    {"id": "R28", "tipo": "final", "certeza": 80,
     "si": {"ambiente": "exterior_sombra", "objetivo": "follaje",
            "clima": CALIDO_O_TEMPLADO, "restriccion": "ninguna"},
     "entonces": ["mano_tigre", "anturio", "telefono"]},

    # --- Reglas finales: bajo mantenimiento y especiales ---------------------
    {"id": "R29", "tipo": "final", "certeza": 80,
     "si": {"ambiente": "exterior_sol", "cuidado": "poco"},
     "entonces": ["echeveria"]},
    {"id": "R30", "tipo": "final", "certeza": 85,
     "si": {"ambiente": "exterior_sol", "cuidado": "poco",
            "restriccion": "ninguna"},
     "entonces": ["sabila", "lengua_suegra"]},
    {"id": "R31", "tipo": "final", "certeza": 75,
     "si": {"ambiente": "exterior_sombra", "clima": "templado",
            "objetivo": "flores", "nivel": "avanzado"},
     "entonces": ["guaria_morada"]},
    # Cerca viva en sombra. La caña india "tolera sol y sombra" según su
    # propio consejo; la areca tolera exterior si se riega bien. Como la
    # caña india es tóxica, la situación se divide en dos reglas.
    {"id": "R32", "tipo": "final", "certeza": 75,
     "si": {"ambiente": "exterior_sombra", "objetivo": "cerca_viva",
            "clima": CALIDO_O_TEMPLADO, "restriccion": "ninguna"},
     "entonces": ["cana_india", "areca"]},
    {"id": "R33", "tipo": "final", "certeza": 75,
     "si": {"ambiente": "exterior_sombra", "objetivo": "cerca_viva",
            "clima": CALIDO_O_TEMPLADO},
     "entonces": ["areca"]},
]

# Huecos conocidos: combinaciones donde el sistema, a propósito, NO recomienda
# nada. No son reglas de recomendación; solo permiten dar una sugerencia más
# precisa que el mensaje general. Se evalúan con el mismo comparador que las
# reglas (también son datos).
HUECOS_CONOCIDOS = [
    {"id": "H1",
     "si": {"ambiente": "interior", "luz": "poca_luz", "objetivo": "flores"},
     "mensaje": "Con poca luz, las plantas de interior casi no florecen. "
                "Pruebe con plantas de follaje o acerque la planta a una "
                "ventana."},
    {"id": "H2",
     "si": {"ambiente": "interior", "objetivo": "cerca_viva"},
     "mensaje": "Una cerca viva se siembra afuera: la combinación interior + "
                "cerca viva es contradictoria. Elija jardín o balcón."},
    {"id": "H3",
     "si": {"ambiente": "interior", "luz": "pleno_sol"},
     "mensaje": "El sol directo detrás de un vidrio suele quemar las plantas "
                "de interior. Pruebe con un lugar de luz indirecta."},
    {"id": "H4",
     "si": {"ambiente": "exterior_sombra", "objetivo": "cerca_viva"},
     "mensaje": "En clima fresco y con sombra, el catálogo no tiene plantas "
                "de cerca viva. Elija un lugar soleado o busque plantas de "
                "follaje."},
]


# =============================================================================
# 5. Motor de inferencia
# =============================================================================

class BaseConocimientoInvalida(Exception):
    """Se lanza cuando la base de conocimiento tiene errores de escritura."""


def valores_aceptados(esperado):
    """Normaliza una condición: un valor único se convierte en lista de uno."""
    return esperado if isinstance(esperado, list) else [esperado]


def cumple_condiciones(condiciones, hechos):
    """Indica si TODAS las condiciones se cumplen con los hechos conocidos.

    Un hecho que todavía no se conoce no cumple la condición (se usa .get,
    que devuelve None y None nunca está en la lista de valores aceptados).
    """
    return all(hechos.get(clave) in valores_aceptados(esperado)
               for clave, esperado in condiciones.items())


def encadenar(respuestas, reglas=None):
    """Encadenamiento hacia adelante con las reglas intermedias.

    Parte de las respuestas del usuario y aplica reglas intermedias una y
    otra vez hasta llegar a un punto fijo: una vuelta completa sin hechos
    nuevos. Cada regla se dispara como máximo una vez.

    Devuelve una tupla (hechos, origen, disparadas):
      hechos     -> respuestas + hechos derivados.
      origen     -> {clave: id de la regla que lo dedujo} o "usuario".
      disparadas -> reglas intermedias activadas, en orden de disparo.
    """
    if reglas is None:
        reglas = REGLAS
    hechos = dict(respuestas)
    origen = {clave: "usuario" for clave in respuestas}
    disparadas = []
    ids_disparados = set()

    hubo_cambios = True
    while hubo_cambios:                       # se repite hasta el punto fijo
        hubo_cambios = False
        for regla in reglas:
            if regla["tipo"] != "intermedia" or regla["id"] in ids_disparados:
                continue                      # nunca se dispara dos veces
            if not cumple_condiciones(regla["si"], hechos):
                continue
            clave, valor = regla["entonces"]
            # Un hecho ya establecido no se sobrescribe: evita que dos reglas
            # se contradigan en silencio.
            if clave in hechos:
                continue
            hechos[clave] = valor
            origen[clave] = regla["id"]
            disparadas.append(regla)
            ids_disparados.add(regla["id"])
            hubo_cambios = True
    return hechos, origen, disparadas


def numero_de_regla(regla):
    """Devuelve el número de una regla (R12 -> 12) para desempatar."""
    return int(regla["id"][1:])


def evaluar(hechos, reglas=None):
    """Devuelve las reglas finales que se cumplen, de la más fuerte a la débil.

    Orden: 1) mayor certeza; 2) más condiciones (una regla más específica
    describe mejor el caso; una lista cuenta como una sola condición);
    3) id menor.
    """
    if reglas is None:
        reglas = REGLAS
    activadas = [regla for regla in reglas
                 if regla["tipo"] == "final"
                 and cumple_condiciones(regla["si"], hechos)]
    activadas.sort(key=lambda r: (-r["certeza"], -len(r["si"]),
                                  numero_de_regla(r)))
    return activadas


def filtrar_por_seguridad(activadas, hechos):
    """Filtro de seguridad, aplicado DESPUÉS de evaluar (defensa en profundidad).

    Aunque las reglas ya consideran la restricción, este filtro revisa planta
    por planta contra el catálogo, por si una regla quedó mal escrita:
      - con restriccion = no_toxicas se eliminan las plantas "toxica" y las
        "sin_registro" se conservan con un aviso amarillo;
      - sin restricción, las tóxicas se conservan con un aviso rojo.
    Si una conclusión queda sin plantas, se descarta.

    Devuelve una lista de recomendaciones:
      {"regla": regla, "plantas": [(id, aviso)], "excluidas": [ids]}
    donde aviso es None, "toxica" o "sin_registro".
    """
    hay_restriccion = hechos.get("restriccion") == "no_toxicas"
    recomendaciones = []
    for regla in activadas:
        plantas, excluidas = [], []
        for id_planta in regla["entonces"]:
            toxicidad = PLANTAS_POR_ID[id_planta]["toxicidad"]
            if hay_restriccion and toxicidad == "toxica":
                excluidas.append(id_planta)
            elif hay_restriccion and toxicidad == "sin_registro":
                plantas.append((id_planta, "sin_registro"))
            elif not hay_restriccion and toxicidad == "toxica":
                plantas.append((id_planta, "toxica"))
            else:
                plantas.append((id_planta, None))
        if plantas:
            recomendaciones.append({"regla": regla, "plantas": plantas,
                                    "excluidas": excluidas})
    return recomendaciones


def quitar_repetidas(recomendaciones):
    """Prepara las recomendaciones para mostrarlas sin plantas repetidas.

    Recorre las recomendaciones en orden (de mayor a menor certeza o
    prioridad) y quita de cada una las plantas que ya aparecieron en una
    anterior. Si una alternativa queda sin plantas, no se muestra. No
    modifica la lista original: la explicación y el historial siguen viendo
    todas las reglas que se activaron.

    Devuelve una lista de recomendaciones con la clave extra "repetidas"
    (ids de las plantas que se omitieron por estar ya mostradas).
    """
    vistas = set()
    visibles = []
    for recomendacion in recomendaciones:
        nuevas = [(p, aviso) for p, aviso in recomendacion["plantas"]
                  if p not in vistas]
        repetidas = [p for p, _ in recomendacion["plantas"] if p in vistas]
        vistas.update(p for p, _ in nuevas)
        if nuevas:
            visibles.append(dict(recomendacion, plantas=nuevas,
                                 repetidas=repetidas))
    return visibles


def buscar_hueco(hechos):
    """Devuelve el hueco conocido que corresponde a los hechos, o None."""
    for hueco in HUECOS_CONOCIDOS:
        if cumple_condiciones(hueco["si"], hechos):
            return hueco
    return None


def resolver_consulta(respuestas):
    """Ejecuta el ciclo completo de inferencia para unas respuestas.

    Encadena, evalúa, filtra y, si no queda ninguna recomendación, busca si
    el caso es un hueco conocido. No imprime nada: la salida es un
    diccionario que usan la interfaz, el historial y las pruebas.
      "recomendaciones" -> todas las reglas finales activadas (filtradas).
      "visibles"        -> las mismas, sin plantas repetidas (para mostrar).
    """
    hechos, origen, intermedias = encadenar(respuestas)
    activadas = evaluar(hechos)
    recomendaciones = filtrar_por_seguridad(activadas, hechos)
    hueco = None if recomendaciones else buscar_hueco(hechos)
    return {"respuestas": dict(respuestas), "hechos": hechos,
            "origen": origen, "intermedias": intermedias,
            "recomendaciones": recomendaciones,
            "visibles": quitar_repetidas(recomendaciones),
            "hueco": hueco}


def validar_base_conocimiento():
    """Revisa la base de conocimiento al iniciar y falla ruidosamente.

    Junta TODOS los errores encontrados y lanza BaseConocimientoInvalida con
    la lista completa, para corregirlos de una sola vez. Revisa:
      - ids duplicados (reglas, preguntas, plantas);
      - claves o valores de condiciones que no existen en las preguntas ni
        en los hechos derivados;
      - conclusiones que referencian plantas fuera del catálogo;
      - certezas fuera de 0–100;
      - casos de prueba con teclas inválidas o reglas inexistentes;
      - los mínimos del enunciado (reglas, preguntas y conclusiones).
    """
    errores = []

    # Valores válidos de cada hecho: los de las preguntas + los derivados.
    valores_validos = {}
    for pregunta in PREGUNTAS:
        if pregunta["clave"] in valores_validos:
            errores.append(f"Pregunta duplicada: {pregunta['clave']}")
        valores_validos[pregunta["clave"]] = {v for v, _ in
                                              pregunta["opciones"]}
        if len(pregunta["opciones"]) < 2:
            errores.append(f"La pregunta {pregunta['clave']} tiene menos de "
                           f"2 opciones")
    for clave, valores in HECHOS_DERIVADOS.items():
        if clave in valores_validos:
            errores.append(f"El hecho derivado {clave} choca con una pregunta")
        valores_validos[clave] = set(valores)

    # Catálogo.
    ids_plantas = [planta["id"] for planta in CATALOGO]
    for id_planta in sorted({i for i in ids_plantas
                             if ids_plantas.count(i) > 1}):
        errores.append(f"Planta duplicada en el catálogo: {id_planta}")
    for planta in CATALOGO:
        if planta["toxicidad"] not in TOXICIDADES_VALIDAS:
            errores.append(f"Toxicidad inválida en {planta['id']}: "
                           f"{planta['toxicidad']}")
        if not planta["id"].isascii():
            errores.append(f"El id {planta['id']} no debe llevar tildes")

    def revisar_condiciones(dueno, condiciones):
        """Valida claves y valores de un bloque "si"."""
        for clave, esperado in condiciones.items():
            if clave not in valores_validos:
                errores.append(f"{dueno}: la clave '{clave}' no existe")
                continue
            for valor in valores_aceptados(esperado):
                if valor not in valores_validos[clave]:
                    errores.append(f"{dueno}: el valor '{valor}' no es "
                                   f"válido para '{clave}'")

    # Reglas.
    ids_reglas = [regla["id"] for regla in REGLAS]
    for id_regla in sorted({i for i in ids_reglas
                            if ids_reglas.count(i) > 1}):
        errores.append(f"Id de regla duplicado: {id_regla}")
    for regla in REGLAS:
        revisar_condiciones(regla["id"], regla["si"])
        if regla["tipo"] == "intermedia":
            clave, valor = regla["entonces"]
            if valor not in HECHOS_DERIVADOS.get(clave, {}):
                errores.append(f"{regla['id']}: concluye un hecho no "
                               f"declarado ({clave} = {valor})")
        elif regla["tipo"] == "final":
            if not regla["entonces"]:
                errores.append(f"{regla['id']}: no recomienda ninguna planta")
            for id_planta in regla["entonces"]:
                if id_planta not in PLANTAS_POR_ID:
                    errores.append(f"{regla['id']}: la planta '{id_planta}' "
                                   f"no está en el catálogo")
            if not 0 <= regla.get("certeza", -1) <= 100:
                errores.append(f"{regla['id']}: certeza fuera de 0–100")
        else:
            errores.append(f"{regla['id']}: tipo desconocido {regla['tipo']}")

    for hueco in HUECOS_CONOCIDOS:
        revisar_condiciones(hueco["id"], hueco["si"])

    # Casos de prueba integrados: teclas válidas y resultados que existen.
    ids_finales = {r["id"] for r in REGLAS if r["tipo"] == "final"}
    ids_huecos = {h["id"] for h in HUECOS_CONOCIDOS}
    for caso in CASOS_PRUEBA:
        try:
            respuestas_desde_teclas(caso["teclas"])
        except ValueError as error:
            errores.append(f"Caso {caso['id']}: {error}")
        esperadas = caso["alternativas"] + ([caso["principal"]]
                                            if caso["principal"] else [])
        for id_regla in esperadas:
            if id_regla not in ids_finales:
                errores.append(f"Caso {caso['id']}: la regla final "
                               f"{id_regla} no existe")
        if caso["hueco"] and caso["hueco"] not in ids_huecos:
            errores.append(f"Caso {caso['id']}: el hueco {caso['hueco']} "
                           f"no existe")

    # Mínimos del enunciado.
    finales = [regla for regla in REGLAS if regla["tipo"] == "final"]
    conclusiones = {tuple(regla["entonces"]) for regla in finales}
    if len(REGLAS) < MINIMO_REGLAS:
        errores.append(f"Hay {len(REGLAS)} reglas; el mínimo es "
                       f"{MINIMO_REGLAS}")
    if len(PREGUNTAS) < MINIMO_PREGUNTAS:
        errores.append(f"Hay {len(PREGUNTAS)} preguntas; el mínimo es "
                       f"{MINIMO_PREGUNTAS}")
    if len(conclusiones) < MINIMO_CONCLUSIONES:
        errores.append(f"Hay {len(conclusiones)} conclusiones distintas; el "
                       f"mínimo es {MINIMO_CONCLUSIONES}")

    if errores:
        raise BaseConocimientoInvalida(
            "La base de conocimiento tiene errores:\n  - "
            + "\n  - ".join(errores))
    return True


# =============================================================================
# 6. Explicación y salida
# =============================================================================

AVISO_INICIAL = (
    "Aviso: estas son recomendaciones generales para plantas ornamentales "
    "del hogar.\nLa toxicidad se basa en la base de datos de ASPCA "
    "(consulta: 9 nov 2026).\nAnte una ingestión, consulte a un veterinario "
    "o a un médico.")
AVISO_TOXICA = "⚠ Tóxica para mascotas"
AVISO_SIN_REGISTRO = ("⚠ Sin registro de toxicidad en ASPCA; consulte a un "
                      "veterinario.")
SUGERENCIA_GENERAL = ("Pruebe con otra ubicación, otro tipo de luz u otro "
                      "objetivo, o consulte en un vivero de su zona.")
LINEA = "=" * 70


def mostrar_bienvenida():
    """Muestra el título del sistema y el aviso inicial."""
    print(color(LINEA, CIAN))
    print(color("  Recomendador de plantas ornamentales para hogares "
                "costarricenses", NEGRITA, VERDE))
    print(color(LINEA, CIAN))
    print(color(AVISO_INICIAL, AMARILLO))


def describir_hecho(clave, hechos, origen):
    """Devuelve "clave = valor" y, si lo dedujo una regla, "[de Rn]".

    La marca [de Rn] es la parte de encadenamiento de la explicación: deja
    ver qué regla intermedia produjo el hecho que usa otra regla.
    """
    texto = f"{clave} = {hechos[clave]}"
    if origen.get(clave, "usuario") != "usuario":
        texto += f" [de {origen[clave]}]"
    return texto


def reglas_excluidas_por_restriccion(hechos):
    """Reglas finales que solo fallaron por la restricción de mascotas.

    Son reglas cuyas demás condiciones se cumplen, pero exigen
    restriccion = ninguna. Mostrarlas explica por qué no se recomiendan
    ciertas plantas tóxicas cuando hay mascotas o niños.
    """
    excluidas = []
    for regla in REGLAS:
        if regla["tipo"] != "final" or "restriccion" not in regla["si"]:
            continue
        resto = {k: v for k, v in regla["si"].items() if k != "restriccion"}
        if (cumple_condiciones(resto, hechos)
                and not cumple_condiciones(regla["si"], hechos)):
            excluidas.append(regla)
    return excluidas


def explicar(resultado):
    """Arma la explicación al estilo MYCIN como una lista de líneas.

    Incluye, en orden: las reglas intermedias que se activaron (con las
    respuestas que las provocaron), las reglas finales activadas (con los
    hechos que usaron y de qué regla salió cada uno), las plantas que quitó
    el filtro de seguridad, las que no se repiten en la salida y las reglas
    que la restricción dejó por fuera.
    Devuelve texto sin imprimir para poder probarlo y reutilizarlo.
    """
    hechos, origen = resultado["hechos"], resultado["origen"]
    lineas = []
    visibles = {rec["regla"]["id"]: rec for rec in resultado["visibles"]}
    for regla in resultado["intermedias"]:
        causas = " y ".join(describir_hecho(clave, hechos, origen)
                            for clave in regla["si"])
        clave, valor = regla["entonces"]
        lineas.append(f"Se activó {regla['id']} porque: {causas} → "
                      f"{clave} = {valor}")
    for recomendacion in resultado["recomendaciones"]:
        regla = recomendacion["regla"]
        causas = ", ".join(describir_hecho(clave, hechos, origen)
                           for clave in regla["si"])
        lineas.append(f"Se activó {regla['id']} ({regla['certeza']}%) "
                      f"porque: {causas}")
        if recomendacion["excluidas"]:
            nombres = ", ".join(PLANTAS_POR_ID[p]["nombre"]
                                for p in recomendacion["excluidas"])
            lineas.append(f"El filtro de seguridad quitó de {regla['id']}: "
                          f"{nombres} (tóxica según ASPCA)")
        # Plantas que no se repiten en la salida porque ya se mostraron.
        if regla["id"] not in visibles:
            nombres = ", ".join(PLANTAS_POR_ID[p]["nombre"]
                                for p, _ in recomendacion["plantas"])
            lineas.append(f"{regla['id']} no se muestra como alternativa: "
                          f"sus plantas ya aparecen arriba ({nombres})")
        elif visibles[regla["id"]]["repetidas"]:
            nombres = ", ".join(PLANTAS_POR_ID[p]["nombre"]
                                for p in visibles[regla["id"]]["repetidas"])
            lineas.append(f"De {regla['id']} se omiten plantas ya mostradas: "
                          f"{nombres}")
    for regla in reglas_excluidas_por_restriccion(hechos):
        lineas.append(f"No se aplicó {regla['id']}: exige restriccion = "
                      f"ninguna, pero "
                      f"{describir_hecho('restriccion', hechos, origen)}")
    return lineas


def formatear_planta(id_planta, aviso, con_tip=True):
    """Línea de una planta, con su aviso de toxicidad debajo si corresponde."""
    planta = PLANTAS_POR_ID[id_planta]
    linea = f"{color(planta['nombre'], NEGRITA)} ({planta['cientifico']})"
    if con_tip:
        linea += f" — {planta['tip']}"
    if aviso == "toxica":
        linea += "\n      " + color(AVISO_TOXICA, ROJO)
    elif aviso == "sin_registro":
        linea += "\n      " + color(AVISO_SIN_REGISTRO, AMARILLO)
    return linea


def mostrar_recomendacion(resultado):
    """Imprime la recomendación principal, las alternativas y el porqué.

    La principal es la primera de la lista (ya viene ordenada por certeza).
    Si no hay recomendación, lo dice con claridad, muestra los hechos que sí
    se dedujeron y da una sugerencia, sin inventar nada.
    """
    print()
    print(color(LINEA, CIAN))
    recomendaciones = resultado["recomendaciones"]
    explicacion = explicar(resultado)

    if not recomendaciones:
        print(color("Sin conclusión: ninguna regla de la base de conocimiento "
                    "cubre esta combinación de respuestas.", AMARILLO, NEGRITA))
        print("El sistema prefiere decirlo antes que inventar una "
              "recomendación.")
        print(color("Hechos derivados que sí se obtuvieron (¿por qué?):",
                    CIAN, NEGRITA))
        for linea in explicacion:
            print(f"  - {linea}")
        hueco = resultado["hueco"]
        if hueco:
            print(color(f"Sugerencia (hueco conocido {hueco['id']}):", CIAN,
                        NEGRITA))
            print(f"  {hueco['mensaje']}")
        else:
            print(color("Sugerencia:", CIAN, NEGRITA))
            print(f"  {SUGERENCIA_GENERAL}")
        print(color(LINEA, CIAN))
        return

    # Se muestran las recomendaciones sin plantas repetidas; la principal
    # nunca pierde plantas porque es la primera.
    visibles = resultado["visibles"]
    principal = visibles[0]
    regla = principal["regla"]
    print(color(f"Recomendación principal ({regla['id']}, certeza "
                f"{regla['certeza']}%):", VERDE, NEGRITA))
    for id_planta, aviso in principal["plantas"]:
        print(f"  • {formatear_planta(id_planta, aviso)}")

    if len(visibles) > 1:
        print(color("Alternativas:", CIAN, NEGRITA))
        for numero, alternativa in enumerate(visibles[1:], start=2):
            regla = alternativa["regla"]
            print(f"  {numero}. {regla['id']} (certeza {regla['certeza']}%):")
            for id_planta, aviso in alternativa["plantas"]:
                print(f"     • {formatear_planta(id_planta, aviso, False)}")

    print(color("¿Por qué?", CIAN, NEGRITA))
    for linea in explicacion:
        print(f"  - {linea}")
    print(color(LINEA, CIAN))


# =============================================================================
# 7. Historial
# =============================================================================

ENCABEZADO_HISTORIAL = ["fecha_hora", "respuestas", "hechos_derivados",
                        "reglas_activadas", "recomendacion_principal"]


def resumir_principal(resultado):
    """Texto corto de la recomendación principal para el historial."""
    if resultado["recomendaciones"]:
        principal = resultado["recomendaciones"][0]
        nombres = ", ".join(PLANTAS_POR_ID[p]["nombre"]
                            for p, _ in principal["plantas"])
        return (f"{principal['regla']['id']} "
                f"({principal['regla']['certeza']}%): {nombres}")
    if resultado["hueco"]:
        return f"Sin conclusión ({resultado['hueco']['id']})"
    return "Sin conclusión"


def guardar_historial(resultado, archivo=None):
    """Agrega la consulta al historial CSV usando el módulo csv.

    Si el archivo no existe (o está vacío) escribe primero el encabezado.
    Si no se puede escribir (por ejemplo, por permisos), avisa y devuelve
    False en lugar de cerrar el programa: el historial es un extra y no
    debe impedir la consulta.
    """
    if archivo is None:
        archivo = ARCHIVO_HISTORIAL      # se lee aquí para poder cambiarlo
    hechos, origen = resultado["hechos"], resultado["origen"]
    derivados = {k: v for k, v in hechos.items() if origen[k] != "usuario"}
    reglas = ([r["id"] for r in resultado["intermedias"]]
              + [rec["regla"]["id"] for rec in resultado["recomendaciones"]])
    fila = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "; ".join(f"{k}={v}" for k, v in resultado["respuestas"].items()),
        "; ".join(f"{k}={v}" for k, v in derivados.items()),
        " ".join(reglas),
        resumir_principal(resultado),
    ]
    try:
        es_nuevo = (not os.path.exists(archivo)
                    or os.path.getsize(archivo) == 0)
        with open(archivo, "a", newline="", encoding="utf-8") as salida:
            escritor = csv.writer(salida)
            if es_nuevo:
                escritor.writerow(ENCABEZADO_HISTORIAL)
            escritor.writerow(fila)
    except OSError as error:
        print(color(f"No se pudo guardar el historial: {error}", AMARILLO))
        return False
    return True


# =============================================================================
# 8. Programa principal
# =============================================================================

def interpretar_si_no(texto):
    """Convierte s, si, sí, n o no en "s" o "n". Otra cosa devuelve None."""
    texto = texto.strip().lower()
    if texto in ("s", "si", "sí"):
        return "s"
    if texto in ("n", "no"):
        return "n"
    return None


def avisar_error(mensaje):
    """Muestra un error de entrada en rojo, sin cerrar el programa."""
    print(color(f"  ✗ {mensaje}", ROJO))


def preguntar_si_no(mensaje):
    """Pregunta s/n y repite hasta recibir una respuesta válida."""
    while True:
        respuesta = input(mensaje)
        valor = interpretar_si_no(respuesta)
        if valor:
            return valor
        if not respuesta.strip():
            avisar_error("No escribió nada. Responda s o n.")
        else:
            avisar_error(f"«{respuesta.strip()}» no es válido. "
                         f"Responda s o n.")


def preguntar(pregunta, numero=None, total=None):
    """Hace una pregunta de la base de conocimiento y valida la respuesta.

    Para un menú acepta solo el número de una opción existente; para una
    pregunta s/n acepta s o n. Ante una respuesta vacía, con letras o fuera
    de rango, explica el error y vuelve a preguntar (nunca se cierra).
    Devuelve el valor interno de la opción elegida.
    """
    print()
    prefijo = f"Pregunta {numero} de {total} · " if numero else ""
    opciones = pregunta["opciones"]

    if pregunta["tipo"] == "sn":
        print(color(f"{prefijo}{pregunta['texto']} (s/n)", CIAN, NEGRITA))
        return preguntar_si_no("Responda s o n: ")

    print(color(f"{prefijo}{pregunta['texto']}", CIAN, NEGRITA))
    for indice, (_, texto) in enumerate(opciones, start=1):
        print(f"  {indice}. {texto}")
    while True:
        respuesta = input(f"Elija una opción (1-{len(opciones)}): ").strip()
        if not respuesta:
            avisar_error("No escribió nada. Escriba el número de una opción.")
        elif not respuesta.isdecimal():
            avisar_error(f"«{respuesta}» no es un número. Escriba solo el "
                         f"número de la opción.")
        elif not 1 <= int(respuesta) <= len(opciones):
            avisar_error(f"La opción {respuesta} no existe. Elija entre 1 y "
                         f"{len(opciones)}.")
        else:
            return opciones[int(respuesta) - 1][0]


def recolectar_hechos():
    """Hace todas las preguntas en orden y devuelve {clave: valor}."""
    respuestas = {}
    for numero, pregunta in enumerate(PREGUNTAS, start=1):
        respuestas[pregunta["clave"]] = preguntar(pregunta, numero,
                                                  len(PREGUNTAS))
    return respuestas


# -----------------------------------------------------------------------------
# Casos de prueba integrados (python loria_james_tarea1.py --pruebas)
# -----------------------------------------------------------------------------
# También son datos. "teclas" es exactamente lo que se escribe en la terminal,
# en el orden de PREGUNTAS: zona, ubicación, luz, cuidado, mascotas (s/n),
# objetivo y experiencia. "alternativas" son las que se MUESTRAN (sin las que
# quedan vacías al quitar plantas repetidas). Están documentados en
# casos_prueba.md y los usa también test_sistema.py.

CASOS_PRUEBA = [
    {"id": "A", "descripcion": "Interior, poca luz, follaje, sin mascotas",
     "teclas": ["2", "1", "4", "2", "n", "2", "1"],
     "principal": "R12", "alternativas": ["R13"], "hueco": None},
    {"id": "B", "descripcion": "Interior, luz indirecta, follaje, mascotas",
     "teclas": ["2", "1", "3", "2", "s", "2", "1"],
     "principal": "R13", "alternativas": [], "hueco": None},
    {"id": "C", "descripcion": "Jardín, pleno sol, bajura, flores",
     "teclas": ["1", "3", "1", "2", "n", "1", "1"],
     "principal": "R18", "alternativas": ["R19"], "hueco": None},
    {"id": "D", "descripcion": "Jardín, semisombra, zona alta, flores",
     "teclas": ["3", "3", "2", "2", "n", "1", "1"],
     "principal": "R24", "alternativas": ["R25"], "hueco": None},
    {"id": "E", "descripcion": "Balcón, pleno sol, poco cuidado, mascotas",
     "teclas": ["2", "2", "1", "1", "s", "2", "1"],
     "principal": "R29", "alternativas": [], "hueco": None},
    {"id": "F", "descripcion": "Jardín, semisombra, bajura, flores, mascotas",
     "teclas": ["1", "3", "2", "2", "s", "1", "1"],
     "principal": "R26", "alternativas": [], "hueco": None},
    {"id": "G", "descripcion": "Interior, poca luz, flores (sin conclusión)",
     "teclas": ["2", "1", "4", "2", "n", "1", "1"],
     "principal": None, "alternativas": [], "hueco": "H1"},
    {"id": "H", "descripcion": "Cerca viva en sombra, bajura, mascotas",
     "teclas": ["1", "3", "2", "2", "s", "3", "2"],
     "principal": "R33", "alternativas": [], "hueco": None},
    {"id": "I", "descripcion": "Pleno sol, clima fresco, follaje (no cubierto)",
     "teclas": ["3", "2", "1", "2", "n", "2", "1"],
     "principal": None, "alternativas": [], "hueco": None},
]


def respuestas_desde_teclas(teclas):
    """Traduce las teclas de un caso a respuestas {clave: valor interno}.

    Aplica las mismas reglas que preguntar(): número de opción en los menús
    y s/n en las preguntas de sí o no. Una tecla inválida lanza ValueError.
    """
    if len(teclas) != len(PREGUNTAS):
        raise ValueError(f"Se esperaban {len(PREGUNTAS)} teclas y hay "
                         f"{len(teclas)}")
    respuestas = {}
    for pregunta, tecla in zip(PREGUNTAS, teclas):
        if pregunta["tipo"] == "sn":
            valor = interpretar_si_no(tecla)
        elif tecla.isdecimal() and 1 <= int(tecla) <= len(pregunta["opciones"]):
            valor = pregunta["opciones"][int(tecla) - 1][0]
        else:
            valor = None
        if valor is None:
            raise ValueError(f"Tecla «{tecla}» inválida para "
                             f"{pregunta['clave']}")
        respuestas[pregunta["clave"]] = valor
    return respuestas


def verificar_caso(caso):
    """Ejecuta un caso de prueba y devuelve (correcto, texto_obtenido)."""
    resultado = resolver_consulta(respuestas_desde_teclas(caso["teclas"]))
    ids = [rec["regla"]["id"] for rec in resultado["visibles"]]
    principal = ids[0] if ids else None
    hueco = resultado["hueco"]["id"] if resultado["hueco"] else None
    correcto = (principal == caso["principal"]
                and ids[1:] == caso["alternativas"]
                and hueco == caso["hueco"])
    if principal:
        certeza = resultado["visibles"][0]["regla"]["certeza"]
        obtenido = f"{principal} ({certeza}%)"
        if ids[1:]:
            obtenido += ", alternativas " + ", ".join(ids[1:])
    else:
        obtenido = f"sin conclusión ({hueco or 'mensaje general'})"
    return correcto, obtenido


def ejecutar_casos_prueba():
    """Modo --pruebas: corre CASOS_PRUEBA y muestra ✅/❌ y un resumen.

    Devuelve 0 si todos los casos son correctos y 1 si alguno falla, para
    que el resultado también se pueda revisar desde otro programa.
    """
    validar_base_conocimiento()
    print(color("Casos de prueba integrados", NEGRITA, CIAN))
    correctos = 0
    for caso in CASOS_PRUEBA:
        correcto, obtenido = verificar_caso(caso)
        teclas = " ".join(caso["teclas"])
        if correcto:
            correctos += 1
            print(f"  {color('✅', VERDE)} Caso {caso['id']} · "
                  f"{caso['descripcion']} [{teclas}] → {obtenido}")
        else:
            esperado = caso["principal"] or f"sin conclusión ({caso['hueco']})"
            print(f"  {color('❌', ROJO)} Caso {caso['id']} · "
                  f"{caso['descripcion']} [{teclas}] → {obtenido}; "
                  f"se esperaba {esperado}, alternativas "
                  f"{caso['alternativas']}")
    total = len(CASOS_PRUEBA)
    estilo = VERDE if correctos == total else ROJO
    print(color(f"{correctos}/{total} casos correctos", NEGRITA, estilo))
    return 0 if correctos == total else 1


USO = ("Uso:\n"
       "  python loria_james_tarea1.py              consulta en la terminal\n"
       "  python loria_james_tarea1.py --web [puerto]  interfaz web "
       "(por defecto, puerto 8000)\n"
       "  python loria_james_tarea1.py --pruebas    corre los casos de prueba")


def main(argumentos=None):
    """Punto de entrada: elige el modo según los argumentos de la terminal.

    Sin argumentos: ciclo interactivo (validar, preguntar, inferir,
    explicar y repetir). Con --pruebas: corre los casos integrados.
    Con --web [puerto]: abre la interfaz web (sección 9).
    Devuelve el código de salida del programa (0 si todo salió bien).
    """
    if argumentos is None:
        argumentos = sys.argv[1:]
    if argumentos == ["--pruebas"]:
        return ejecutar_casos_prueba()
    if argumentos[:1] == ["--web"] and len(argumentos) <= 2:
        if len(argumentos) == 1:
            return iniciar_interfaz_web(PUERTO_WEB)
        if argumentos[1].isdecimal() and 1 <= int(argumentos[1]) <= 65535:
            return iniciar_interfaz_web(int(argumentos[1]))
    if argumentos:
        print(USO)
        return 2

    try:
        validar_base_conocimiento()
    except BaseConocimientoInvalida as error:
        print(color(str(error), ROJO))
        return 1

    mostrar_bienvenida()
    try:
        while True:
            respuestas = recolectar_hechos()
            resultado = resolver_consulta(respuestas)
            mostrar_recomendacion(resultado)
            if guardar_historial(resultado):
                print(f"(Consulta guardada en {ARCHIVO_HISTORIAL})")
            print()
            if preguntar_si_no("¿Desea hacer otra consulta? (s/n): ") == "n":
                break
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C o fin de la entrada: se sale sin mostrar un error de Python.
        print("\n" + color("Consulta interrumpida. ¡Hasta pronto!", AMARILLO))
        return 0

    print(color("Gracias por usar el recomendador. ¡Pura vida!", VERDE))
    return 0


# =============================================================================
# 9. Interfaz web (extra: una interfaz más cuidada)
# =============================================================================
# Una página web servida con http.server (biblioteca estándar). Usa el mismo
# motor, la misma explicación y el mismo historial CSV que la terminal: la
# interfaz solo cambia cómo se pregunta y cómo se muestra el resultado.
# En GitHub Codespaces el puerto se reenvía solo y se abre en el navegador.

PUERTO_WEB = 8000
ANFITRION_WEB = "127.0.0.1"          # solo accesible desde esta máquina
TAMANO_MAXIMO_PETICION = 10_000      # bytes; una consulta real pesa ~200
FILAS_HISTORIAL_WEB = 10

# Varias peticiones pueden llegar a la vez: el candado evita que dos hilos
# escriban el CSV al mismo tiempo y mezclen las filas.
CANDADO_HISTORIAL = threading.Lock()


def validar_respuestas_web(datos):
    """Valida las respuestas que llegan del navegador.

    Es la misma idea que preguntar() en la terminal: no se confía en la
    entrada. Devuelve (respuestas, errores); si hay errores, respuestas
    es None y no se ejecuta la consulta.
    """
    if not isinstance(datos, dict):
        return None, ["La consulta debe ser un objeto JSON."]
    respuestas, errores = {}, []
    for pregunta in PREGUNTAS:
        valor = datos.get(pregunta["clave"])
        validos = [v for v, _ in pregunta["opciones"]]
        if valor in (None, ""):
            errores.append(f"Falta responder: {pregunta['texto']}")
        elif valor not in validos:
            errores.append(f"Opción inválida en «{pregunta['texto']}»: "
                           f"{valor}")
        else:
            respuestas[pregunta["clave"]] = valor
    return (None, errores) if errores else (respuestas, [])


# Frases en lenguaje natural para cada valor de cada hecho. Solo sirven para
# que la interfaz web explique el razonamiento como lo diría una persona; la
# terminal y reglas.md siguen usando la notación clave = valor.
FRASES_WEB = {
    "zona": {"bajura_caliente": "Vive en bajura caliente",
             "valle_central": "Vive en el Valle Central",
             "altura_fria": "Vive en zona alta y fría"},
    "ubicacion": {"interior": "La planta estará dentro de la casa",
                  "balcon_terraza": "La planta estará en un balcón o terraza",
                  "jardin": "La planta estará en el jardín"},
    "luz": {"pleno_sol": "Recibe sol directo varias horas",
            "semisombra": "Recibe sol solo una parte del día",
            "luz_indirecta": "Recibe claridad sin sol directo",
            "poca_luz": "Recibe poca luz"},
    "cuidado": {"poco": "Tiene poco tiempo para cuidarla",
                "medio": "Tiene un tiempo medio para cuidarla",
                "mucho": "Tiene mucho tiempo para cuidarla"},
    "mascotas": {"s": "Hay mascotas o niños pequeños en casa",
                 "n": "No hay mascotas ni niños pequeños en casa"},
    "objetivo": {"flores": "Busca flores",
                 "follaje": "Busca follaje decorativo",
                 "cerca_viva": "Busca una cerca viva"},
    "experiencia": {"principiante": "Es principiante con las plantas",
                    "con_experiencia": "Tiene experiencia con plantas"},
    "clima": {"calido": "Clima cálido", "templado": "Clima templado",
              "fresco": "Clima fresco"},
    "ambiente": {"interior": "Ambiente de interior",
                 "exterior_sol": "Exterior con sol",
                 "exterior_sombra": "Exterior con sombra"},
    "restriccion": {"no_toxicas": "Solo plantas no tóxicas",
                    "ninguna": "Cualquier planta, tóxica o no"},
    "nivel": {"facil": "Necesita plantas fáciles de cuidar",
              "avanzado": "Puede con plantas más exigentes"},
}


def hecho_a_dict(clave, hechos, origen):
    """Un hecho como datos: clave, valor y quién lo produjo (usuario o Rn)."""
    return {"clave": clave, "valor": hechos[clave],
            "origen": origen.get(clave, "usuario")}


def planta_a_dict(id_planta, aviso):
    """Datos de una planta listos para enviar al navegador."""
    planta = PLANTAS_POR_ID[id_planta]
    textos = {"toxica": AVISO_TOXICA, "sin_registro": AVISO_SIN_REGISTRO}
    return {"nombre": planta["nombre"], "cientifico": planta["cientifico"],
            "tip": planta["tip"], "aviso": aviso,
            "aviso_texto": textos.get(aviso)}


def resultado_a_dict(resultado, guardado):
    """Convierte el resultado del motor en un diccionario para JSON.

    Separa la cadena de inferencia en sus tres niveles (respuestas, reglas
    intermedias y reglas finales) para que la página pueda dibujar el
    encadenamiento hacia adelante paso a paso. Además del texto armado
    ("condiciones"), envía los hechos como datos ("hechos") para que la
    página los escriba en lenguaje natural. Solo convierte: no decide nada.
    """
    hechos, origen = resultado["hechos"], resultado["origen"]
    textos_opcion = {(p["clave"], v): t for p in PREGUNTAS
                     for v, t in p["opciones"]}
    visibles = resultado["visibles"]
    ids_visibles = {rec["regla"]["id"] for rec in visibles}
    repetidas = {rec["regla"]["id"]: rec["repetidas"] for rec in visibles}

    def nombres(ids_plantas):
        return [PLANTAS_POR_ID[p]["nombre"] for p in ids_plantas]

    recomendaciones = [
        {"id": rec["regla"]["id"], "certeza": rec["regla"]["certeza"],
         "plantas": [planta_a_dict(p, aviso) for p, aviso in rec["plantas"]]}
        for rec in visibles]
    return {
        "respuestas": [
            {"clave": clave, "valor": valor,
             "texto": textos_opcion[(clave, valor)]}
            for clave, valor in resultado["respuestas"].items()],
        "intermedias": [
            {"id": regla["id"],
             "condiciones": [describir_hecho(c, hechos, origen)
                             for c in regla["si"]],
             "conclusion": "{} = {}".format(*regla["entonces"]),
             "hechos": [hecho_a_dict(c, hechos, origen) for c in regla["si"]],
             "concluye": {"clave": regla["entonces"][0],
                          "valor": regla["entonces"][1]}}
            for regla in resultado["intermedias"]],
        "finales": [
            {"id": rec["regla"]["id"], "certeza": rec["regla"]["certeza"],
             "condiciones": [describir_hecho(c, hechos, origen)
                             for c in rec["regla"]["si"]],
             "mostrada": rec["regla"]["id"] in ids_visibles,
             "hechos": [hecho_a_dict(c, hechos, origen)
                        for c in rec["regla"]["si"]],
             "excluidas": nombres(rec["excluidas"]),
             "repetidas": nombres(repetidas.get(rec["regla"]["id"], []))}
            for rec in resultado["recomendaciones"]],
        "no_aplicadas": [r["id"] for r in
                         reglas_excluidas_por_restriccion(hechos)],
        "origen_restriccion": origen.get("restriccion"),
        "notas": [linea for linea in explicar(resultado)
                  if not linea.startswith("Se activó")],
        "principal": recomendaciones[0] if recomendaciones else None,
        "alternativas": recomendaciones[1:],
        "hueco": ({"id": resultado["hueco"]["id"]}
                  if resultado["hueco"] else None),
        "sugerencia": (resultado["hueco"]["mensaje"] if resultado["hueco"]
                       else SUGERENCIA_GENERAL),
        "guardado": guardado,
    }


def leer_historial(archivo=None, limite=FILAS_HISTORIAL_WEB):
    """Devuelve las últimas consultas del CSV, de la más reciente a la vieja."""
    if archivo is None:
        archivo = ARCHIVO_HISTORIAL
    try:
        with open(archivo, newline="", encoding="utf-8") as entrada:
            filas = list(csv.DictReader(entrada))
    except OSError:
        return []                    # todavía no hay historial
    return filas[::-1][:limite]


def pagina_html():
    """Arma la página: las preguntas salen de PREGUNTAS (datos), no de HTML."""
    preguntas = [{"clave": p["clave"], "texto": p["texto"],
                  "opciones": p["opciones"]} for p in PREGUNTAS]
    def a_json(objeto):
        # "</" se escapa para que un texto nunca cierre la etiqueta <script>.
        return json.dumps(objeto, ensure_ascii=False).replace("</", "<\\/")
    return (PLANTILLA_HTML
            .replace("__AVISO__", html.escape(AVISO_INICIAL))
            .replace("__PREGUNTAS__", a_json(preguntas))
            .replace("__FRASES__", a_json(FRASES_WEB)))


class ManejadorWeb(BaseHTTPRequestHandler):
    """Atiende las peticiones del navegador.

    GET  /               -> la página
    GET  /api/historial  -> últimas consultas guardadas en el CSV
    POST /api/consultar  -> valida, infiere, guarda en el historial y
                            devuelve el resultado con su explicación
    """

    def enviar(self, codigo, cuerpo, tipo):
        """Envía una respuesta HTTP con su tipo de contenido."""
        datos = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)

    def enviar_json(self, codigo, objeto):
        """Envía un objeto como JSON en UTF-8."""
        self.enviar(codigo, json.dumps(objeto, ensure_ascii=False),
                    "application/json; charset=utf-8")

    def do_GET(self):
        ruta = urlparse(self.path).path
        if ruta == "/":
            self.enviar(200, pagina_html(), "text/html; charset=utf-8")
        elif ruta == "/api/historial":
            self.enviar_json(200, leer_historial())
        else:
            self.enviar_json(404, {"errores": ["Página no encontrada."]})

    def do_POST(self):
        if urlparse(self.path).path != "/api/consultar":
            self.enviar_json(404, {"errores": ["Página no encontrada."]})
            return
        try:
            largo = int(self.headers.get("Content-Length", 0))
        except ValueError:
            largo = -1
        if not 0 < largo <= TAMANO_MAXIMO_PETICION:
            self.enviar_json(400, {"errores": ["Consulta vacía o demasiado "
                                               "grande."]})
            return
        try:
            datos = json.loads(self.rfile.read(largo).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.enviar_json(400, {"errores": ["La consulta no es JSON "
                                               "válido."]})
            return
        respuestas, errores = validar_respuestas_web(datos)
        if errores:
            self.enviar_json(400, {"errores": errores})
            return
        resultado = resolver_consulta(respuestas)
        with CANDADO_HISTORIAL:
            guardado = guardar_historial(resultado)
        self.enviar_json(200, resultado_a_dict(resultado, guardado))

    def log_message(self, formato, *argumentos):
        """Registro breve en la terminal: método, ruta y código."""
        print(f"  [web] {self.command} {urlparse(self.path).path} -> "
              f"{argumentos[1] if len(argumentos) > 1 else ''}")


def crear_servidor(puerto=PUERTO_WEB, anfitrion=ANFITRION_WEB):
    """Crea el servidor web (puerto 0 = cualquiera libre, útil en pruebas)."""
    return ThreadingHTTPServer((anfitrion, puerto), ManejadorWeb)


def iniciar_interfaz_web(puerto=PUERTO_WEB):
    """Modo --web: valida la base, levanta el servidor y espera Ctrl+C."""
    try:
        validar_base_conocimiento()
    except BaseConocimientoInvalida as error:
        print(color(str(error), ROJO))
        return 1
    try:
        servidor = crear_servidor(puerto)
    except OSError as error:
        print(color(f"No se pudo usar el puerto {puerto}: {error}", ROJO))
        print(f"Pruebe con otro: python loria_james_tarea1.py --web "
              f"{puerto + 1}")
        return 1
    mostrar_bienvenida()
    print(color(f"Interfaz web lista en http://localhost:{puerto}",
                VERDE, NEGRITA))
    print("En Codespaces: pestaña PORTS (o el aviso que aparece abajo a la "
          "derecha) → «Open in Browser».")
    print(f"El historial se guarda en {ARCHIVO_HISTORIAL}. "
          f"Presione Ctrl+C para detener el servidor.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n" + color("Servidor detenido. ¡Hasta pronto!", AMARILLO))
    finally:
        servidor.server_close()
    return 0


# Plantilla de la página (diseño "etiqueta de vivero"; ver CLAUDE.md).
# Es una cadena cruda (r"""...""") para que las expresiones regulares de JS
# conserven sus barras invertidas.
PLANTILLA_HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recomendador de plantas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,500..800&display=swap">
<style>
/* Tokens del diseño "etiqueta de vivero" (decisiones en CLAUDE.md). */
:root {
  --neblina: #EDF1EE;   /* fondo: gris verdoso del bosque nuboso */
  --cal: #FFFFFF;       /* superficie de la etiqueta y de los controles */
  --bosque: #1E3A2A;    /* texto y estructura */
  --musgo: #56745A;     /* texto secundario y hechos deducidos */
  --guaria: #8E3B7E;    /* único acento: la etiqueta y la acción principal */
  --peligro: #B3261E;   /* planta tóxica y errores */
  --atencion: #8F5B00;  /* sin registro de toxicidad y sin conclusión */
  --sobre-guaria: #FFFFFF;
  --linea: #C9D4CC;
  --seleccion: #DFE8E2;
  --peligro-suave: #FBE9E7;
  --atencion-suave: #FBF0D9;
  --sombra-etiqueta: rgba(30, 58, 42, .24);
  --f-rotulo: "Bricolage Grotesque", "Avenir Next", "Segoe UI Variable Display",
              "Segoe UI", system-ui, sans-serif;
  --f-texto: "Atkinson Hyperlegible", "Segoe UI", system-ui, -apple-system,
             sans-serif;
  --t-1: 13px; --t-2: 15px; --t-3: 17px; --t-4: 22px; --t-5: 34px;
  --e-1: 4px; --e-2: 8px; --e-3: 12px; --e-4: 16px; --e-5: 24px;
  --e-6: 32px; --e-7: 48px;
  --r-control: 8px;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root {
    --neblina: #0F1913; --cal: #17251C; --bosque: #E2ECE5; --musgo: #8FB394;
    --guaria: #C987BC; --peligro: #FF8A80; --atencion: #F2C46D;
    --sobre-guaria: #1A0F18; --linea: #2C3D32; --seleccion: #22362A;
    --peligro-suave: #3A1916; --atencion-suave: #382B10;
    --sombra-etiqueta: rgba(0, 0, 0, .55);
    color-scheme: dark;
  }
}

/* Base */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--neblina); color: var(--bosque);
  font: var(--t-3)/1.55 var(--f-texto); }
h1, h2, h3 { font-family: var(--f-rotulo); line-height: 1.15; margin: 0;
  letter-spacing: -0.01em; }
p { margin: 0; }
button { font: inherit; color: inherit; }
:focus-visible { outline: 3px solid var(--guaria); outline-offset: 2px; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden;
  clip: rect(0 0 0 0); white-space: nowrap; }
.pagina { max-width: 1040px; margin: 0 auto; padding: 0 var(--e-4); }

/* Encabezado: tranquilo, sin banda de color */
.cabecera { padding: var(--e-6) 0 var(--e-5);
  border-bottom: 1px solid var(--linea); }
.cabecera h1 { font-size: var(--t-4); font-weight: 700; }
.lema { color: var(--musgo); font-size: var(--t-2); margin-top: var(--e-1);
  max-width: 70ch; }
.aviso { color: var(--musgo); font-size: var(--t-1); margin-top: var(--e-3);
  max-width: 70ch; white-space: pre-line; }

/* Pantalla de preguntas: una a la vez */
.consulta { max-width: 640px; padding: var(--e-6) 0 var(--e-7); }
.progreso { list-style: none; display: flex; gap: var(--e-1); margin: 0;
  padding: 0; }
.progreso li { flex: 1; }
.progreso button { display: block; width: 100%; height: 24px; padding: 9px 0;
  border: 0; background: none; cursor: pointer; }
.progreso button::after { content: ""; display: block; height: 6px;
  border-radius: 3px; background: var(--linea); }
.progreso button.respondida::after { background: var(--musgo); }
.progreso button[aria-current="step"]::after { background: var(--bosque); }
.progreso button:disabled { cursor: default; }
.contador { color: var(--musgo); font-size: var(--t-2); margin-top: var(--e-2); }
.pregunta { border: 0; margin: var(--e-2) 0 0; padding: 0; min-width: 0; }
.pregunta legend { float: left; width: 100%; padding: 0;
  font-family: var(--f-rotulo); font-weight: 700; line-height: 1.12;
  font-size: clamp(26px, 6vw, var(--t-5)); letter-spacing: -0.02em;
  margin-bottom: var(--e-5); }
.pregunta legend:focus { outline: none; }
.opciones { clear: both; display: grid; gap: var(--e-2); }
.opcion { position: relative; display: grid; grid-template-columns: auto 1fr;
  align-items: center; gap: var(--e-3); padding: var(--e-3) var(--e-4);
  background: var(--cal); border: 1px solid var(--linea);
  border-radius: var(--r-control); cursor: pointer;
  transition: border-color .12s, background-color .12s; }
.opcion:hover { border-color: var(--musgo); }
.opcion:has(input:checked) { background: var(--seleccion);
  border-color: var(--bosque); box-shadow: inset 0 0 0 1px var(--bosque); }
.opcion:has(input:focus-visible) { outline: 3px solid var(--guaria);
  outline-offset: 2px; }
.opcion input { position: absolute; opacity: 0; width: 1px; height: 1px;
  margin: 0; }
.tecla { display: grid; place-items: center; width: 32px; height: 32px;
  border-radius: 6px; border: 1px solid var(--linea);
  font-family: var(--f-rotulo); font-weight: 700; font-size: var(--t-2);
  color: var(--musgo); }
.opcion:has(input:checked) .tecla { background: var(--bosque);
  border-color: var(--bosque); color: var(--neblina); }
.opcion-texto { display: grid; }
.opcion-detalle { color: var(--musgo); font-size: var(--t-2); }
.error-campo { color: var(--peligro); font-size: var(--t-2); font-weight: 700;
  margin-top: var(--e-3); }
.navegacion { display: flex; justify-content: space-between; align-items: center;
  gap: var(--e-3); margin-top: var(--e-5); }
.entrando { animation: entrar 180ms ease-out; }
@keyframes entrar { from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; } }

/* Botones, enlaces y alertas */
.boton { border: 0; border-radius: var(--r-control); min-height: 48px;
  padding: var(--e-3) var(--e-5); font-weight: 700; cursor: pointer; }
.boton.principal { background: var(--guaria); color: var(--sobre-guaria); }
.boton.principal:hover { filter: brightness(1.08); }
.boton.secundario { background: transparent; color: var(--bosque);
  box-shadow: inset 0 0 0 1px var(--linea); }
.boton.secundario:hover { box-shadow: inset 0 0 0 1px var(--bosque); }
.boton:disabled { opacity: .65; cursor: progress; }
.enlace { background: none; border: 0; padding: 0; color: var(--bosque);
  font-size: var(--t-2); text-decoration: underline;
  text-underline-offset: 3px; cursor: pointer; white-space: nowrap; }
.alerta { border-radius: var(--r-control); padding: var(--e-3) var(--e-4);
  font-size: var(--t-2); margin-top: var(--e-3); }
.alerta.peligro { background: var(--peligro-suave); color: var(--peligro); }
.aviso-planta { display: inline-block; font-size: var(--t-1); font-weight: 700;
  border-radius: 4px; padding: 2px 8px; margin-top: var(--e-2); }
.aviso-planta.toxica { background: var(--peligro-suave); color: var(--peligro); }
.aviso-planta.sin_registro { background: var(--atencion-suave);
  color: var(--atencion); }
.aviso-planta.corto { margin: 0 0 0 var(--e-1); padding: 0 6px; }
.regla { display: inline-flex; align-items: center; border-radius: 4px;
  padding: 1px 8px; font-family: var(--f-rotulo); font-weight: 700;
  font-size: var(--t-1); background: var(--bosque); color: var(--neblina);
  white-space: nowrap; }
.regla.decisiva { background: var(--guaria); color: var(--sobre-guaria); }
.regla.origen { background: transparent; color: var(--musgo); font-weight: 600;
  box-shadow: inset 0 0 0 1px var(--linea); }
.certeza-texto { color: var(--musgo); font-size: var(--t-2);
  white-space: nowrap; }

/* Pantalla de resultado */
.resultado { padding: var(--e-6) 0 var(--e-7); display: grid; gap: var(--e-7); }
.resultado:focus { outline: none; }
@media (min-width: 880px) {
  .resultado { grid-template-columns: minmax(0, 5fr) minmax(0, 6fr);
    align-items: start; }
}
.columna { display: grid; gap: var(--e-6); align-content: start; }

/* El elemento memorable: la etiqueta de vivero */
.etiqueta-sombra { filter: drop-shadow(0 14px 16px var(--sombra-etiqueta));
  animation: clavar 460ms cubic-bezier(.2, .8, .2, 1) both; }
@keyframes clavar {
  from { opacity: 0; transform: translateY(-18px) rotate(-1.5deg); }
  to { opacity: 1; transform: none; } }
.etiqueta { background: var(--cal); padding-bottom: var(--e-7);
  clip-path: polygon(8px 0, calc(100% - 8px) 0, 100% 8px,
    100% calc(100% - 36px), 50% 100%, 0 calc(100% - 36px), 0 8px); }
.etiqueta-banda { position: relative; display: flex; align-items: flex-end;
  justify-content: space-between; gap: var(--e-4);
  padding: var(--e-6) var(--e-5) var(--e-4);
  background: var(--guaria); color: var(--sobre-guaria); }
.perforacion { position: absolute; top: 10px; left: 50%; width: 14px;
  height: 14px; margin-left: -7px; border-radius: 50%;
  background: var(--neblina); box-shadow: inset 0 2px 3px rgba(0, 0, 0, .3); }
.etiqueta-tipo { font-size: var(--t-4); font-weight: 800; }
.etiqueta-regla { font-size: var(--t-2); margin-top: var(--e-1); }
.certeza { text-align: right; font-size: var(--t-1); line-height: 1.3; }
.certeza strong { display: block; font-family: var(--f-rotulo);
  font-size: var(--t-5); font-weight: 800; line-height: 1; }
.etiqueta-plantas { list-style: none; margin: 0; padding: 0 var(--e-5); }
.etiqueta-plantas > li { padding: var(--e-4) 0;
  border-bottom: 1px solid var(--linea); }
.etiqueta-plantas > li:last-child { border-bottom: 0; }
.planta-nombre { font-size: var(--t-4); font-weight: 700; }
.planta-cientifico { color: var(--musgo); font-size: var(--t-2);
  font-style: italic; }
.planta-tip { font-size: var(--t-2); margin-top: var(--e-2); max-width: 60ch; }
.etiqueta.en-blanco .etiqueta-banda { background: var(--atencion-suave);
  color: var(--atencion); }
.etiqueta-cuerpo { display: grid; gap: var(--e-3);
  padding: var(--e-5) var(--e-5) 0; font-size: var(--t-2); }
.etiqueta-cuerpo h3 { font-size: var(--t-4); font-weight: 700; }

/* Alternativas: filas compactas */
.titulo-bloque { font-size: var(--t-3); font-weight: 700;
  margin-bottom: var(--e-3); }
.alternativas { list-style: none; margin: 0; padding: 0;
  border-top: 1px solid var(--linea); }
.alternativas > li { border-bottom: 1px solid var(--linea); }
.alternativas summary { list-style: none; cursor: pointer;
  display: grid; grid-template-columns: auto 1fr auto; gap: var(--e-3);
  align-items: baseline; padding: var(--e-3) 0; }
.alternativas summary::-webkit-details-marker { display: none; }
.alternativas summary::after { content: "+"; font-family: var(--f-rotulo);
  font-weight: 700; font-size: var(--t-4); line-height: 1; color: var(--musgo); }
.alternativas details[open] summary::after { content: "–"; }
.alt-meta { display: inline-flex; align-items: baseline; gap: var(--e-2); }
.alt-plantas { font-size: var(--t-2); }
.alt-detalle { list-style: none; margin: 0; padding: 0 0 var(--e-4); }
.alt-detalle > li { padding: var(--e-2) 0 var(--e-2) var(--e-4);
  border-left: 2px solid var(--linea); }
.alt-detalle .planta-nombre { font-size: var(--t-3); }

.acciones { display: flex; flex-wrap: wrap; gap: var(--e-3);
  align-items: center; }
.guardado { color: var(--musgo); font-size: var(--t-1); margin-top: var(--e-2); }

/* Razonamiento: tres tramos en secuencia */
.razonamiento > h2 { font-size: var(--t-4); font-weight: 700;
  margin-bottom: var(--e-5); }
.tramos { list-style: none; margin: 0; padding: 0; counter-reset: tramo; }
.tramo { position: relative; counter-increment: tramo;
  padding: 0 0 var(--e-6) 48px; }
.tramo::before { content: counter(tramo); position: absolute; left: 0;
  top: -3px; width: 32px; height: 32px; border-radius: 50%; display: grid;
  place-items: center; font-family: var(--f-rotulo); font-weight: 800;
  background: var(--cal); box-shadow: inset 0 0 0 2px var(--bosque); }
.tramo::after { content: ""; position: absolute; left: 15px; top: 36px;
  bottom: 6px; width: 2px; background: var(--linea); }
.tramo:last-child { padding-bottom: 0; }
.tramo:last-child::after { display: none; }
.tramo h3 { font-size: var(--t-3); font-weight: 700;
  margin-bottom: var(--e-3); }
.lista-respuestas, .deducciones, .condiciones, .notas { list-style: none;
  margin: 0; padding: 0; display: grid; gap: var(--e-2);
  font-size: var(--t-2); }
.lista-respuestas li { display: flex; justify-content: space-between;
  align-items: baseline; gap: var(--e-3); }
.deducciones { gap: var(--e-4); }
.deduccion { display: grid; align-items: center; gap: var(--e-1) var(--e-3);
  grid-template-columns: minmax(0, 1fr) 6em minmax(0, 1fr); }
.paso-regla { display: inline-flex; align-items: center; gap: var(--e-1);
  justify-self: center; }
.flecha { color: var(--musgo); }
@media (max-width: 560px) {
  .deduccion { grid-template-columns: auto minmax(0, 1fr); }
  .paso-regla { justify-self: start; }
  .deduccion .causas { grid-column: 1 / -1; }
}
.hecho-derivado { font-weight: 700; }
.regla-final + .regla-final { margin-top: var(--e-4); }
.regla-final-cabecera { display: flex; flex-wrap: wrap; align-items: center;
  gap: var(--e-2); }
.condiciones { margin-top: var(--e-3); }
.condiciones li { display: flex; flex-wrap: wrap; align-items: center;
  gap: var(--e-2); }
.condiciones li::before { content: "✓"; color: var(--musgo);
  font-weight: 700; }
.otras-reglas { margin-top: var(--e-4); }
.otras-reglas summary { margin-bottom: var(--e-3); }
.desplegable summary { list-style: none; cursor: pointer; font-size: var(--t-2); }
.desplegable summary::-webkit-details-marker { display: none; }
.desplegable summary::before { content: "+"; display: inline-block; width: 1em;
  font-family: var(--f-rotulo); font-weight: 700; color: var(--musgo); }
.desplegable[open] summary::before { content: "–"; }
.notas { margin-top: var(--e-4); color: var(--musgo); max-width: 60ch; }

/* Historial */
.historial { border-top: 1px solid var(--linea);
  padding: var(--e-6) 0 var(--e-7); }
.historial h2 { font-size: var(--t-4); font-weight: 700; }
.historial .nota { color: var(--musgo); font-size: var(--t-2);
  margin: var(--e-1) 0 var(--e-4); }
.vacio { color: var(--musgo); font-size: var(--t-2); }
.tabla { width: 100%; border-collapse: collapse; font-size: var(--t-2); }
.tabla th { text-align: left; font-size: var(--t-1); font-weight: 700;
  color: var(--musgo); padding: var(--e-2);
  border-bottom: 1px solid var(--linea); }
.tabla td { padding: var(--e-3) var(--e-2); vertical-align: top;
  border-bottom: 1px solid var(--linea); }
.tabla td.reglas { white-space: nowrap; }
.tabla ul { margin: var(--e-2) 0 0; padding-left: var(--e-4); }
@media (max-width: 720px) {
  .tabla thead { position: absolute; width: 1px; height: 1px;
    overflow: hidden; clip: rect(0 0 0 0); }
  .tabla, .tabla tbody, .tabla tr, .tabla td { display: block; width: 100%; }
  .tabla tr { padding: var(--e-3) 0; border-bottom: 1px solid var(--linea); }
  .tabla td { border: 0; padding: var(--e-1) 0; }
  .tabla td.reglas { white-space: normal; }
  .tabla td::before { content: attr(data-etiqueta); display: block;
    font-size: var(--t-1); font-weight: 700; color: var(--musgo); }
}
.pie { color: var(--musgo); font-size: var(--t-1);
  padding: var(--e-5) 0 var(--e-7); border-top: 1px solid var(--linea); }
.pie p { max-width: 70ch; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important;
    transition: none !important; scroll-behavior: auto !important; }
}
</style>
</head>
<body>
<div class="pagina">
<header class="cabecera">
  <h1>Recomendador de plantas ornamentales</h1>
  <p class="lema">Responda siete preguntas sobre su espacio y le digo qué
    planta sembrar, y por qué.</p>
  <p class="aviso">__AVISO__</p>
</header>

<main>
  <section id="pantalla-consulta" class="consulta" aria-label="Consulta">
    <form id="formulario" novalidate>
      <ol class="progreso" id="progreso" aria-label="Avance de la consulta"></ol>
      <p class="contador" id="contador" aria-live="polite"></p>
      <div id="contenedor-pregunta"></div>
      <p class="error-campo" id="error-pregunta" role="alert" hidden></p>
      <p class="alerta peligro" id="error-servidor" role="alert" hidden></p>
      <div class="navegacion">
        <button type="button" class="boton secundario" id="atras">Atrás</button>
        <button type="submit" class="boton principal" id="siguiente">Siguiente</button>
      </div>
    </form>
  </section>
  <section id="pantalla-resultado" class="resultado" tabindex="-1"
           aria-label="Resultado de la consulta" hidden></section>
</main>

<section class="historial" aria-labelledby="titulo-historial">
  <h2 id="titulo-historial">Consultas anteriores</h2>
  <p class="nota">Cada consulta se guarda en historial_consultas.csv.</p>
  <div id="historial"></div>
</section>

<footer class="pie"><p>Hecho por James Loria para el curso CIA02 Introducción
  a la IA de UCreativa. La toxicidad se basa en la base de datos de ASPCA,
  consultada el 9 de noviembre de 2026.</p></footer>
</div>

<script>
const PREGUNTAS = __PREGUNTAS__;
const FRASES = __FRASES__;
const MOVIMIENTO = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const estado = { paso: 0, respuestas: {}, enviando: false };
const $ = (selector) => document.querySelector(selector);

// Crea un elemento con textContent (nunca innerHTML con datos).
function el(etiqueta, clase, texto) {
  const nodo = document.createElement(etiqueta);
  if (clase) nodo.className = clase;
  if (texto !== undefined) nodo.textContent = texto;
  return nodo;
}

// "Bajura caliente (menos de 800 msnm)" -> ["Bajura caliente", "menos de 800 msnm"]
function partirOpcion(texto) {
  const partes = texto.match(/^(.*?)\s*\((.*)\)$/);
  return partes ? [partes[1], partes[2]] : [texto, ""];
}

function frase(clave, valor) {
  return (FRASES[clave] && FRASES[clave][valor]) || `${clave} = ${valor}`;
}

function unirConY(lista) {
  if (lista.length < 2) return lista.join("");
  return `${lista.slice(0, -1).join(", ")} y ${lista[lista.length - 1]}`;
}

// Une frases completas: "Tiene mucho tiempo… y tiene experiencia…".
function unirFrases(frases) {
  return unirConY(frases.map((texto, i) =>
    i ? texto.charAt(0).toLowerCase() + texto.slice(1) : texto));
}

function insigniaRegla(texto, variante) {
  return el("span", variante ? `regla ${variante}` : "regla", texto);
}

function respondida(clave) { return estado.respuestas[clave] !== undefined; }

// ---- Pantalla de preguntas -------------------------------------------------

function pintarProgreso() {
  const lista = $("#progreso");
  lista.replaceChildren();
  PREGUNTAS.forEach((pregunta, i) => {
    const boton = el("button");
    boton.type = "button";
    if (respondida(pregunta.clave)) boton.classList.add("respondida");
    if (i === estado.paso) boton.setAttribute("aria-current", "step");
    boton.disabled = !PREGUNTAS.slice(0, i).every((p) => respondida(p.clave));
    boton.setAttribute("aria-label", `Pregunta ${i + 1}: ${pregunta.texto}` +
      (respondida(pregunta.clave) ? " (respondida)" : ""));
    boton.addEventListener("click", () => irA(i));
    const item = el("li");
    item.append(boton);
    lista.append(item);
  });
}

function pintarPregunta(animar) {
  const pregunta = PREGUNTAS[estado.paso];
  $("#contador").textContent =
    `Pregunta ${estado.paso + 1} de ${PREGUNTAS.length}`;
  const grupo = el("fieldset", animar && MOVIMIENTO ? "pregunta entrando"
                                                   : "pregunta");
  const titulo = el("legend", null, pregunta.texto);
  titulo.id = "titulo-pregunta";
  titulo.tabIndex = -1;
  const opciones = el("div", "opciones");
  pregunta.opciones.forEach(([valor, texto], i) => {
    const etiqueta = el("label", "opcion");
    const radio = el("input");
    radio.type = "radio";
    radio.name = pregunta.clave;
    radio.value = valor;
    radio.checked = estado.respuestas[pregunta.clave] === valor;
    radio.addEventListener("change", () => {
      estado.respuestas[pregunta.clave] = valor;
      ocultarError();
      pintarProgreso();
    });
    const tecla = el("span", "tecla", pregunta.opciones.length === 2 &&
                     /^[sn]$/.test(valor) ? valor : String(i + 1));
    tecla.setAttribute("aria-hidden", "true");
    const [principal, detalle] = partirOpcion(texto);
    const textos = el("span", "opcion-texto");
    textos.append(el("span", null, principal));
    if (detalle) textos.append(el("span", "opcion-detalle", detalle));
    etiqueta.append(radio, tecla, textos);
    opciones.append(etiqueta);
  });
  grupo.append(titulo, opciones);
  $("#contenedor-pregunta").replaceChildren(grupo);
  $("#atras").style.visibility = estado.paso === 0 ? "hidden" : "visible";
  $("#siguiente").textContent = estado.paso === PREGUNTAS.length - 1
    ? "Ver mi recomendación" : "Siguiente";
  pintarProgreso();
}

function radios() {
  return [...document.querySelectorAll("#contenedor-pregunta input")];
}

function mostrarError(texto) {
  const error = $("#error-pregunta");
  error.textContent = texto;
  error.hidden = false;
  radios().forEach((radio) => {
    radio.setAttribute("aria-invalid", "true");
    radio.setAttribute("aria-describedby", "error-pregunta");
  });
}

function ocultarError() {
  $("#error-pregunta").hidden = true;
  radios().forEach((radio) => {
    radio.removeAttribute("aria-invalid");
    radio.removeAttribute("aria-describedby");
  });
}

function mostrarPantalla(nombre) {
  $("#pantalla-consulta").hidden = nombre !== "consulta";
  $("#pantalla-resultado").hidden = nombre !== "resultado";
}

function irA(indice) {
  estado.paso = indice;
  $("#error-servidor").hidden = true;
  mostrarPantalla("consulta");
  pintarPregunta(true);
  ocultarError();
  $("#titulo-pregunta").focus({ preventScroll: true });
}

async function avanzar(evento) {
  evento.preventDefault();
  // Un Enter de más mientras la consulta va en camino no debe repetirla
  // (ni guardarla dos veces en el historial).
  if (estado.enviando) return;
  const pregunta = PREGUNTAS[estado.paso];
  if (!respondida(pregunta.clave)) {
    mostrarError("Elija una opción para continuar.");
    radios()[0].focus();
    return;
  }
  if (estado.paso < PREGUNTAS.length - 1) { irA(estado.paso + 1); return; }
  const falta = PREGUNTAS.findIndex((p) => !respondida(p.clave));
  if (falta !== -1) {
    irA(falta);
    mostrarError("Falta esta pregunta para poder recomendarle una planta.");
    return;
  }
  await consultar();
}

async function consultar() {
  const boton = $("#siguiente");
  estado.enviando = true;
  boton.disabled = true;
  boton.textContent = "Buscando su planta…";
  try {
    const respuesta = await fetch("api/consultar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(estado.respuestas) });
    const datos = await respuesta.json();
    if (!respuesta.ok) {
      mostrarErrorServidor((datos.errores || []).join(" ") ||
                           "El programa no aceptó la consulta.");
      return;
    }
    pintarResultado(datos);
    cargarHistorial();
  } catch (error) {
    mostrarErrorServidor("No pude conectarme con el programa. Revise que " +
      "siga corriendo en la terminal y vuelva a intentar.");
  } finally {
    estado.enviando = false;
    boton.disabled = false;
    boton.textContent = "Ver mi recomendación";
  }
}

function mostrarErrorServidor(texto) {
  const alerta = $("#error-servidor");
  alerta.textContent = texto;
  alerta.hidden = false;
}

// ---- Pantalla de resultado -------------------------------------------------

function avisoPlanta(planta) {
  return el("p", `aviso-planta ${planta.aviso}`, planta.aviso_texto);
}

function itemPlanta(planta) {
  const item = el("li");
  item.append(el("h3", "planta-nombre", planta.nombre),
              el("p", "planta-cientifico", planta.cientifico),
              el("p", "planta-tip", planta.tip));
  if (planta.aviso) item.append(avisoPlanta(planta));
  return item;
}

function etiquetaVivero(recomendacion) {
  const sombra = el("div", "etiqueta-sombra");
  const etiqueta = el("article", "etiqueta");
  etiqueta.setAttribute("aria-labelledby", "titulo-etiqueta");
  const banda = el("header", "etiqueta-banda");
  const perforacion = el("span", "perforacion");
  perforacion.setAttribute("aria-hidden", "true");
  const izquierda = el("div");
  const titulo = el("h2", "etiqueta-tipo", "Le recomiendo");
  titulo.id = "titulo-etiqueta";
  izquierda.append(titulo,
    el("p", "etiqueta-regla", `Regla ${recomendacion.id}`));
  const certeza = el("p", "certeza");
  certeza.append(el("strong", null, `${recomendacion.certeza} %`),
                 "de certeza");
  banda.append(perforacion, izquierda, certeza);
  const lista = el("ul", "etiqueta-plantas");
  recomendacion.plantas.forEach((planta) => lista.append(itemPlanta(planta)));
  etiqueta.append(banda, lista);
  sombra.append(etiqueta);
  return sombra;
}

function etiquetaEnBlanco(resultado) {
  const sombra = el("div", "etiqueta-sombra");
  const etiqueta = el("article", "etiqueta en-blanco");
  etiqueta.setAttribute("aria-labelledby", "titulo-etiqueta");
  const banda = el("header", "etiqueta-banda");
  const perforacion = el("span", "perforacion");
  perforacion.setAttribute("aria-hidden", "true");
  const titulo = el("h2", "etiqueta-tipo", "Sin recomendación");
  titulo.id = "titulo-etiqueta";
  banda.append(perforacion, titulo);
  const cuerpo = el("div", "etiqueta-cuerpo");
  const sugerencia = el("p");
  sugerencia.append(el("strong", null, "Sugerencia: "), resultado.sugerencia);
  cuerpo.append(
    el("h3", null, "No tengo una planta para esta combinación"),
    el("p", null, "Ninguna regla de mi base de conocimiento cubre sus " +
       "respuestas, así que prefiero no inventar una recomendación."),
    sugerencia);
  etiqueta.append(banda, cuerpo);
  sombra.append(etiqueta);
  return sombra;
}

function bloqueAlternativas(alternativas) {
  const bloque = el("section");
  bloque.append(el("h2", "titulo-bloque", "También le pueden servir"));
  const lista = el("ul", "alternativas");
  alternativas.forEach((alternativa) => {
    const detalles = el("details");
    const resumen = el("summary");
    const meta = el("span", "alt-meta");
    meta.append(insigniaRegla(alternativa.id),
                el("span", "certeza-texto", `${alternativa.certeza} %`));
    const nombres = el("span", "alt-plantas");
    alternativa.plantas.forEach((planta, i) => {
      if (i) nombres.append(", ");
      nombres.append(planta.nombre);
      // El aviso de seguridad se ve aunque la fila esté cerrada.
      if (planta.aviso) {
        nombres.append(el("span", `aviso-planta corto ${planta.aviso}`,
          planta.aviso === "toxica" ? "tóxica" : "sin registro"));
      }
    });
    resumen.append(meta, nombres);
    const detalle = el("ul", "alt-detalle");
    alternativa.plantas.forEach((planta) => detalle.append(itemPlanta(planta)));
    detalles.append(resumen, detalle);
    const item = el("li");
    item.append(detalles);
    lista.append(item);
  });
  bloque.append(lista);
  return bloque;
}

function acciones(resultado) {
  const contenedor = el("div");
  const fila = el("div", "acciones");
  const otra = el("button", "boton principal", "Hacer otra consulta");
  otra.type = "button";
  otra.addEventListener("click", nuevaConsulta);
  const cambiar = el("button", "boton secundario", "Cambiar respuestas");
  cambiar.type = "button";
  cambiar.addEventListener("click", () => irA(PREGUNTAS.length - 1));
  fila.append(otra, cambiar);
  contenedor.append(fila, el("p", "guardado", resultado.guardado
    ? "Consulta guardada en el historial."
    : "No pude guardar el historial; revise la terminal."));
  return contenedor;
}

function reglaFinal(regla, decisiva) {
  const bloque = el("div", "regla-final");
  const cabecera = el("p", "regla-final-cabecera");
  cabecera.append(insigniaRegla(regla.id, decisiva ? "decisiva" : ""),
                  el("span", "certeza-texto", `${regla.certeza} % de certeza`));
  const condiciones = el("ul", "condiciones");
  regla.hechos.forEach((hecho) => {
    const item = el("li");
    item.append(el("span", null, frase(hecho.clave, hecho.valor)));
    if (hecho.origen !== "usuario") {
      item.append(insigniaRegla(`de ${hecho.origen}`, "origen"));
    }
    condiciones.append(item);
  });
  bloque.append(cabecera, condiciones);
  return bloque;
}

function notasDelRazonamiento(resultado) {
  const notas = [];
  if (resultado.no_aplicadas.length) {
    const varias = resultado.no_aplicadas.length > 1;
    const origen = resultado.origen_restriccion &&
      resultado.origen_restriccion !== "usuario"
      ? ` (${resultado.origen_restriccion})` : "";
    notas.push(`Descarté ${unirConY(resultado.no_aplicadas)} porque ` +
      `${varias ? "solo aplican" : "solo aplica"} en casas sin mascotas ` +
      `ni niños pequeños, y en la suya los hay${origen}.`);
  }
  resultado.finales.forEach((regla) => {
    if (regla.excluidas.length) {
      notas.push(`Quité ${unirConY(regla.excluidas)} de ${regla.id} porque ` +
        `${regla.excluidas.length > 1 ? "son tóxicas" : "es tóxica"} ` +
        "según ASPCA.");
    }
    if (!regla.mostrada) {
      notas.push(`${regla.id} no aparece entre las opciones porque sus ` +
                 "plantas ya están más arriba.");
    } else if (regla.repetidas.length) {
      notas.push(`En ${regla.id} no repito ${unirConY(regla.repetidas)} ` +
        `porque ya ${regla.repetidas.length > 1 ? "aparecen" : "aparece"} ` +
        "más arriba.");
    }
  });
  return notas;
}

function razonamiento(resultado) {
  const seccion = el("section", "razonamiento");
  seccion.setAttribute("aria-labelledby", "titulo-razonamiento");
  const titulo = el("h2", null, resultado.principal
    ? "¿Por qué esta recomendación?" : "¿Por qué no hay recomendación?");
  titulo.id = "titulo-razonamiento";
  const tramos = el("ol", "tramos");

  const tramo1 = el("li", "tramo");
  const respuestas = el("ul", "lista-respuestas");
  resultado.respuestas.forEach((respuesta) => {
    const indice = PREGUNTAS.findIndex((p) => p.clave === respuesta.clave);
    const cambiar = el("button", "enlace", "Cambiar");
    cambiar.type = "button";
    cambiar.setAttribute("aria-label", `Cambiar: ${PREGUNTAS[indice].texto}`);
    cambiar.addEventListener("click", () => irA(indice));
    const item = el("li");
    item.append(el("span", null, frase(respuesta.clave, respuesta.valor)),
                cambiar);
    respuestas.append(item);
  });
  tramo1.append(el("h3", null, "Sus respuestas"), respuestas);

  const tramo2 = el("li", "tramo");
  const deducciones = el("ul", "deducciones");
  resultado.intermedias.forEach((regla) => {
    const item = el("li", "deduccion");
    const pasoRegla = el("span", "paso-regla");
    const flecha1 = el("span", "flecha", "→");
    const flecha2 = el("span", "flecha", "→");
    flecha1.setAttribute("aria-hidden", "true");
    flecha2.setAttribute("aria-hidden", "true");
    pasoRegla.append(flecha1, insigniaRegla(regla.id), flecha2);
    item.append(
      el("span", "causas",
         unirFrases(regla.hechos.map((h) => frase(h.clave, h.valor)))),
      pasoRegla,
      el("span", "hecho-derivado",
         frase(regla.concluye.clave, regla.concluye.valor)));
    deducciones.append(item);
  });
  tramo2.append(el("h3", null, "Lo que deduje"), deducciones);

  const tramo3 = el("li", "tramo");
  if (resultado.principal) {
    const decisiva = resultado.finales.find(
      (regla) => regla.id === resultado.principal.id);
    tramo3.append(el("h3", null, "La regla que decidió"),
                  reglaFinal(decisiva, true));
    const otras = resultado.finales.filter((regla) => regla !== decisiva);
    if (otras.length) {
      const detalles = el("details", "otras-reglas desplegable");
      detalles.append(el("summary", null,
        `Otras reglas que también se cumplieron (${otras.length})`));
      otras.forEach((regla) => detalles.append(reglaFinal(regla, false)));
      tramo3.append(detalles);
    }
  } else {
    tramo3.append(el("h3", null, "Ninguna regla de recomendación se cumplió"),
      el("p", "vacio", "Con lo que deduje, a ninguna regla final le " +
         "alcanzan las condiciones."));
  }
  const notas = notasDelRazonamiento(resultado);
  if (notas.length) {
    const lista = el("ul", "notas");
    notas.forEach((nota) => lista.append(el("li", null, nota)));
    tramo3.append(lista);
  }

  tramos.append(tramo1, tramo2, tramo3);
  seccion.append(titulo, tramos);
  return seccion;
}

function pintarResultado(resultado) {
  const pantalla = $("#pantalla-resultado");
  const izquierda = el("div", "columna");
  izquierda.append(resultado.principal ? etiquetaVivero(resultado.principal)
                                       : etiquetaEnBlanco(resultado));
  if (resultado.alternativas.length) {
    izquierda.append(bloqueAlternativas(resultado.alternativas));
  }
  izquierda.append(acciones(resultado));
  const derecha = el("div", "columna");
  derecha.append(razonamiento(resultado));
  pantalla.replaceChildren(izquierda, derecha);
  mostrarPantalla("resultado");
  window.scrollTo({ top: 0, behavior: MOVIMIENTO ? "smooth" : "auto" });
  pantalla.focus({ preventScroll: true });
}

function nuevaConsulta() {
  estado.respuestas = {};
  irA(0);
  window.scrollTo({ top: 0, behavior: MOVIMIENTO ? "smooth" : "auto" });
}

// ---- Historial -------------------------------------------------------------

const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep",
               "oct", "nov", "dic"];

function fechaCorta(texto) {
  const partes = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/.exec(texto || "");
  if (!partes) return texto;
  return `${Number(partes[3])} ${MESES[Number(partes[2]) - 1]} ${partes[1]}, ` +
         `${partes[4]}:${partes[5]}`;
}

function respuestasNaturales(texto) {
  return (texto || "").split(";").map((par) => par.trim()).filter(Boolean)
    .map((par) => { const [clave, valor] = par.split("="); return frase(clave, valor); });
}

function celda(etiqueta, contenido, clase) {
  const td = el("td", clase);
  td.dataset.etiqueta = etiqueta;
  td.append(contenido);
  return td;
}

async function cargarHistorial() {
  const contenedor = $("#historial");
  let filas;
  try {
    filas = await (await fetch("api/historial")).json();
  } catch (error) {
    contenedor.replaceChildren(el("p", "vacio", "No pude leer el historial."));
    return;
  }
  if (!filas.length) {
    contenedor.replaceChildren(el("p", "vacio",
      "Todavía no hay consultas. La primera que haga aparecerá aquí."));
    return;
  }
  const tabla = el("table", "tabla");
  const cabecera = el("tr");
  ["Fecha", "Recomendación principal", "Reglas activadas", "Respuestas"]
    .forEach((texto) => cabecera.append(el("th", null, texto)));
  const thead = el("thead");
  thead.append(cabecera);
  const cuerpo = el("tbody");
  filas.forEach((fila) => {
    const frases = respuestasNaturales(fila.respuestas);
    const detalles = el("details", "desplegable");
    detalles.append(el("summary", null, `Ver ${frases.length} respuestas`));
    const lista = el("ul");
    frases.forEach((texto) => lista.append(el("li", null, texto)));
    detalles.append(lista);
    const tr = el("tr");
    tr.append(celda("Fecha", fechaCorta(fila.fecha_hora)),
              celda("Recomendación principal", fila.recomendacion_principal),
              celda("Reglas activadas", fila.reglas_activadas, "reglas"),
              celda("Respuestas", detalles));
    cuerpo.append(tr);
  });
  tabla.append(thead, cuerpo);
  contenedor.replaceChildren(tabla);
}

// ---- Teclado: los mismos atajos que la terminal ----------------------------

document.addEventListener("keydown", (evento) => {
  if ($("#pantalla-consulta").hidden || evento.altKey || evento.ctrlKey ||
      evento.metaKey) return;
  const pregunta = PREGUNTAS[estado.paso];
  const indice = pregunta.opciones.findIndex(([valor], i) =>
    evento.key === String(i + 1) || (valor.length === 1 && evento.key === valor));
  if (indice !== -1) {
    const radio = radios()[indice];
    radio.checked = true;
    radio.dispatchEvent(new Event("change"));
    radio.focus();
    evento.preventDefault();
  } else if (evento.key === "Enter" &&
             !(document.activeElement instanceof HTMLButtonElement)) {
    // Como en la terminal, Enter confirma la respuesta (los botones ya
    // responden a Enter por su cuenta).
    $("#formulario").requestSubmit();
    evento.preventDefault();
  }
});

$("#formulario").addEventListener("submit", avanzar);
$("#atras").addEventListener("click", () => irA(estado.paso - 1));
pintarPregunta(false);
cargarHistorial();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
