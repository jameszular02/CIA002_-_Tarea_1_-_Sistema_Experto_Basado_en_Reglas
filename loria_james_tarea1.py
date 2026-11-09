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
# Uso:  python loria_james_tarea1.py
# Solo usa la biblioteca estándar de Python (3.10 o superior).
# =============================================================================

import csv
import os
import sys
from datetime import datetime


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
       "  python loria_james_tarea1.py            consulta interactiva\n"
       "  python loria_james_tarea1.py --pruebas  corre los casos de prueba")


def main(argumentos=None):
    """Punto de entrada: elige el modo según los argumentos de la terminal.

    Sin argumentos: ciclo interactivo (validar, preguntar, inferir,
    explicar y repetir). Con --pruebas: corre los casos integrados.
    Devuelve el código de salida del programa (0 si todo salió bien).
    """
    if argumentos is None:
        argumentos = sys.argv[1:]
    if argumentos == ["--pruebas"]:
        return ejecutar_casos_prueba()
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


if __name__ == "__main__":
    sys.exit(main())
