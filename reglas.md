# Base de conocimiento – Recomendador de plantas ornamentales

> Documento **generado automáticamente** desde `loria_james_tarea1.py` con `python generar_reglas.py`. No se edita a mano: los ids son los mismos del código.

- Reglas: **31** (11 intermedias + 20 finales)
- Preguntas: **7**
- Conclusiones finales distintas: **20**
- Plantas en el catálogo: **31**

## 1. Preguntas al usuario

| Clave | Pregunta | Opciones (tecla → valor interno) |
|---|---|---|
| zona | ¿En qué zona vive? | `1` → bajura_caliente · `2` → valle_central · `3` → altura_fria |
| ubicacion | ¿Dónde estará la planta? | `1` → interior · `2` → balcon_terraza · `3` → jardin |
| luz | ¿Cuánta luz recibe ese lugar? | `1` → pleno_sol · `2` → semisombra · `3` → luz_indirecta · `4` → poca_luz |
| cuidado | ¿Cuánto tiempo puede dedicarle? | `1` → poco · `2` → medio · `3` → mucho |
| mascotas | ¿Hay mascotas o niños pequeños en casa? | `s` → s · `n` → n |
| objetivo | ¿Qué busca? | `1` → flores · `2` → follaje · `3` → cerca_viva |
| experiencia | ¿Cuál es su experiencia con plantas? | `1` → principiante · `2` → con_experiencia |

## 2. Hechos derivados

Los deducen las reglas intermedias; el usuario no los responde.

| Hecho | Valores posibles |
|---|---|
| clima | calido, templado, fresco |
| ambiente | interior, exterior_sol, exterior_sombra |
| restriccion | no_toxicas, ninguna |
| nivel | facil, avanzado |

## 3. Reglas intermedias (encadenamiento hacia adelante)

| Id | Regla en lenguaje natural | Notación del código |
|---|---|---|
| R1 | **SI** zona = bajura caliente **ENTONCES** clima = cálido | `zona = bajura_caliente → clima = calido` |
| R2 | **SI** zona = valle central **ENTONCES** clima = templado | `zona = valle_central → clima = templado` |
| R3 | **SI** zona = zona alta y fría **ENTONCES** clima = fresco | `zona = altura_fria → clima = fresco` |
| R4 | **SI** ubicación = dentro de la casa **ENTONCES** ambiente = interior | `ubicacion = interior → ambiente = interior` |
| R5 | **SI** ubicación = balcón o terraza o jardín **Y** luz = pleno sol **ENTONCES** ambiente = exterior con sol | `ubicacion ∈ [balcon_terraza, jardin], luz = pleno_sol → ambiente = exterior_sol` |
| R6 | **SI** ubicación = balcón o terraza o jardín **Y** luz = semisombra, luz indirecta o poca luz **ENTONCES** ambiente = exterior con sombra | `ubicacion ∈ [balcon_terraza, jardin], luz ∈ [semisombra, luz_indirecta, poca_luz] → ambiente = exterior_sombra` |
| R7 | **SI** mascotas o niños = sí **ENTONCES** restricción = solo plantas no tóxicas | `mascotas = s → restriccion = no_toxicas` |
| R8 | **SI** mascotas o niños = no **ENTONCES** restricción = ninguna | `mascotas = n → restriccion = ninguna` |
| R9 | **SI** tiempo de cuidado = poco **ENTONCES** nivel = fácil | `cuidado = poco → nivel = facil` |
| R10 | **SI** tiempo de cuidado = medio o mucho **Y** experiencia = principiante **ENTONCES** nivel = fácil | `cuidado ∈ [medio, mucho], experiencia = principiante → nivel = facil` |
| R11 | **SI** tiempo de cuidado = medio o mucho **Y** experiencia = con experiencia **ENTONCES** nivel = avanzado | `cuidado ∈ [medio, mucho], experiencia = con_experiencia → nivel = avanzado` |

## 4. Reglas finales (recomendaciones)

| Id | Regla en lenguaje natural | Certeza |
|---|---|---|
| R12 | **SI** ambiente = interior **Y** luz = poca luz o luz indirecta **Y** restricción = ninguna **Y** objetivo = follaje **ENTONCES** recomendar: Lengua de suegra, Zamioculca, Teléfono | 90 % |
| R13 | **SI** ambiente = interior **Y** luz = poca luz o luz indirecta **Y** objetivo = follaje **ENTONCES** recomendar: Mala madre, Peperomia, Palma de salón | 85 % |
| R14 | **SI** ambiente = interior **Y** luz = luz indirecta **Y** nivel = avanzado **Y** restricción = ninguna **Y** objetivo = follaje **ENTONCES** recomendar: Mano de tigre | 80 % |
| R15 | **SI** ambiente = interior **Y** luz = luz indirecta **Y** nivel = avanzado **Y** objetivo = follaje **ENTONCES** recomendar: Calatea, Helecho, Palma areca | 80 % |
| R16 | **SI** ambiente = interior **Y** luz = luz indirecta **Y** restricción = ninguna **Y** objetivo = flores **ENTONCES** recomendar: Cuna de Moisés, Anturio | 85 % |
| R17 | **SI** ambiente = interior **Y** luz = luz indirecta **Y** objetivo = flores **ENTONCES** recomendar: Orquídea mariposa, Bromelia | 80 % |
| R18 | **SI** ambiente = exterior con sol **Y** clima = cálido o templado **Y** objetivo = flores **Y** restricción = ninguna **ENTONCES** recomendar: Veranera, Moño de señora, Ave del paraíso | 90 % |
| R19 | **SI** ambiente = exterior con sol **Y** clima = cálido o templado **Y** objetivo = flores **ENTONCES** recomendar: Amapola / hibisco, Veranera, Moño de señora | 85 % |
| R20 | **SI** ambiente = exterior con sol **Y** clima = cálido o templado **Y** objetivo = follaje **Y** restricción = ninguna **ENTONCES** recomendar: Crotón, Caña india | 85 % |
| R21 | **SI** ambiente = exterior con sol **Y** objetivo = cerca viva **Y** clima = cálido o templado **Y** restricción = ninguna **ENTONCES** recomendar: Itabo, Caña india | 85 % |
| R22 | **SI** ambiente = exterior con sol **Y** objetivo = cerca viva **ENTONCES** recomendar: Amapola / hibisco, Palma areca | 80 % |
| R23 | **SI** ambiente = exterior con sol **Y** clima = fresco **Y** objetivo = flores **ENTONCES** recomendar: Rosa | 85 % |
| R24 | **SI** ambiente = exterior con sombra **Y** clima = fresco **Y** objetivo = flores **Y** restricción = ninguna **ENTONCES** recomendar: Hortensia, Azalea, Begonia | 85 % |
| R25 | **SI** ambiente = exterior con sombra **Y** clima = templado o fresco **Y** objetivo = flores **ENTONCES** recomendar: Chinas | 80 % |
| R26 | **SI** ambiente = exterior con sombra **Y** clima = cálido **Y** objetivo = flores **ENTONCES** recomendar: Platanilla / heliconia | 75 % |
| R27 | **SI** ambiente = exterior con sombra **Y** objetivo = follaje **ENTONCES** recomendar: Helecho, Calatea, Bromelia | 85 % |
| R28 | **SI** ambiente = exterior con sombra **Y** objetivo = follaje **Y** clima = cálido o templado **Y** restricción = ninguna **ENTONCES** recomendar: Mano de tigre, Anturio, Teléfono | 80 % |
| R29 | **SI** ambiente = exterior con sol **Y** tiempo de cuidado = poco **ENTONCES** recomendar: Echeveria, Haworthia | 80 % |
| R30 | **SI** ambiente = exterior con sol **Y** tiempo de cuidado = poco **Y** restricción = ninguna **ENTONCES** recomendar: Sábila, Lengua de suegra | 85 % |
| R31 | **SI** ambiente = exterior con sombra **Y** clima = templado **Y** objetivo = flores **Y** nivel = avanzado **ENTONCES** recomendar: Guaria morada | 75 % |

Orden de las recomendaciones: mayor certeza; si empatan, la regla con más condiciones (una lista de valores cuenta como una sola condición); si siguen empatadas, el id menor.

## 5. Mascotas: restricción y filtro de seguridad

- Las reglas que concluyen al menos una planta **tóxica** exigen `restriccion = ninguna`. Así la explicación deja claro por qué no aplican cuando hay mascotas o niños.
- Las reglas cuyas plantas son solo **seguras** o **sin registro** no llevan esa condición: sirven para cualquier hogar.
- Después de evaluar, un **filtro de seguridad** revisa planta por planta contra el catálogo (defensa en profundidad):
  - con mascotas: elimina las tóxicas y marca en amarillo las sin registro (*⚠ Sin registro de toxicidad en ASPCA; consulte a un veterinario.*); si una conclusión queda vacía, se descarta;
  - sin mascotas: marca en rojo las tóxicas (*⚠ Tóxica para mascotas*).

## 6. Casos sin conclusión

Cuando ninguna regla final aplica, el sistema lo dice con claridad, muestra los hechos que sí dedujo y da una sugerencia. Nunca inventa una recomendación.

### 6.1 Huecos conocidos (con sugerencia específica)

| Id | Condiciones | Sugerencia | Combinaciones |
|---|---|---|---|
| H1 | ambiente = interior **Y** luz = poca luz **Y** objetivo = flores | Con poca luz, las plantas de interior casi no florecen. Pruebe con plantas de follaje o acerque la planta a una ventana. | 36 |
| H2 | ambiente = interior **Y** objetivo = cerca viva | Una cerca viva se siembra afuera: la combinación interior + cerca viva es contradictoria. Elija jardín o balcón. | 144 |
| H3 | ambiente = interior **Y** luz = pleno sol | El sol directo detrás de un vidrio suele quemar las plantas de interior. Pruebe con un lugar de luz indirecta. | 72 |

### 6.2 Cobertura (`python cobertura.py`)

Se recorrieron las **1296** combinaciones posibles de respuestas con el mismo motor del programa:

| Resultado | Combinaciones | % |
|---|---|---|
| Con recomendación | 724 | 55.9 % |
| Hueco conocido (sugerencia específica) | 252 | 19.4 % |
| Sin cubrir (mensaje general) | 320 | 24.7 % |

### 6.3 Limitación: grupos sin cubrir

| # | Patrón | Casos | Ejemplo de respuestas |
|---|---|---|---|
| 1 | ambiente = exterior_sombra; objetivo = cerca_viva; luz = semisombra o luz_indirecta o poca_luz | 216 | `zona=bajura_caliente, ubicacion=balcon_terraza, luz=semisombra, cuidado=poco, mascotas=s, objetivo=cerca_viva, experiencia=principiante` |
| 2 | ambiente = interior; objetivo = flores; luz = semisombra | 36 | `zona=bajura_caliente, ubicacion=interior, luz=semisombra, cuidado=poco, mascotas=s, objetivo=flores, experiencia=principiante` |
| 3 | ambiente = interior; objetivo = follaje; luz = semisombra | 36 | `zona=bajura_caliente, ubicacion=interior, luz=semisombra, cuidado=poco, mascotas=s, objetivo=follaje, experiencia=principiante` |
| 4 | ambiente = exterior_sol; objetivo = follaje; luz = pleno_sol; clima = calido o templado; restriccion = no_toxicas; cuidado = medio o mucho | 16 | `zona=bajura_caliente, ubicacion=balcon_terraza, luz=pleno_sol, cuidado=medio, mascotas=s, objetivo=follaje, experiencia=principiante` |
| 5 | ambiente = exterior_sol; objetivo = follaje; luz = pleno_sol; clima = fresco; cuidado = medio o mucho | 16 | `zona=altura_fria, ubicacion=balcon_terraza, luz=pleno_sol, cuidado=medio, mascotas=s, objetivo=follaje, experiencia=principiante` |

## 7. Catálogo de plantas

Fuente de toxicidad: ASPCA, base de datos de plantas tóxicas y no tóxicas (consulta: 9 nov 2026). La guaria morada no aparece por nombre; se trata como segura por género, porque ASPCA lista varias *Cattleya* (C. mossiae, C. trianaei, C. labiata) como no tóxicas.

| Id | Nombre | Nombre científico | Toxicidad | Consejo |
|---|---|---|---|---|
| telefono | Teléfono | *Epipremnum aureum* | toxica | Riegue cuando el sustrato esté seco; tolera poca luz. |
| lengua_suegra | Lengua de suegra | *Sansevieria trifasciata* | toxica | Riegue cada 2–3 semanas; el exceso de agua pudre la raíz. |
| zamioculca | Zamioculca | *Zamioculcas zamiifolia* | toxica | Riego escaso; ideal para rincones con poca luz. |
| mano_tigre | Mano de tigre | *Monstera deliciosa* | toxica | Dele un tutor para trepar y luz indirecta brillante. |
| cuna_moises | Cuna de Moisés | *Spathiphyllum spp.* | toxica | Si se marchita está pidiendo agua; florece con luz indirecta. |
| anturio | Anturio | *Anthurium spp.* | toxica | Sustrato aireado y humedad; evite el sol directo. |
| cana_india | Caña india | *Dracaena fragrans* | toxica | Muy resistente; tolera sol y sombra. |
| croton | Crotón | *Codiaeum variegatum* | toxica | A más sol, colores más intensos; su savia irrita la piel. |
| itabo | Itabo | *Yucca guatemalensis* | toxica | Cerca viva casi sin riego; se siembra por estaca. |
| hortensia | Hortensia | *Hydrangea macrophylla* | toxica | Semisombra y suelo húmedo; el color de la flor depende del pH. |
| azalea | Azalea | *Rhododendron spp.* | toxica | Suelo ácido, semisombra y clima fresco. |
| begonia | Begonia | *Begonia spp.* | toxica | Semisombra; evite mojar las hojas. |
| ave_paraiso | Ave del paraíso | *Strelitzia reginae* | toxica | Pleno sol y riego moderado; tarda en dar su primera flor. |
| sabila | Sábila | *Aloe vera* | toxica | Sol y riego escaso en sustrato arenoso. |
| mala_madre | Mala madre | *Chlorophytum comosum* | segura | Ideal colgante; sus hijos se propagan fácil. |
| peperomia | Peperomia | *Peperomia spp.* | segura | Riego moderado; sus hojas carnosas guardan agua. |
| palma_salon | Palma de salón | *Chamaedorea elegans* | segura | Tolera poca luz; mantenga el sustrato apenas húmedo. |
| areca | Palma areca | *Dypsis lutescens* | segura | Luz indirecta brillante; las puntas cafés indican aire seco. |
| helecho | Helecho | *Nephrolepis exaltata* | segura | Humedad constante; ideal en baños o corredores. |
| calatea | Calatea | *Calathea spp.* | segura | Humedad alta y agua sin cloro; enrolla las hojas si le falta agua. |
| phalaenopsis | Orquídea mariposa | *Phalaenopsis spp.* | segura | Riego semanal en corteza; luz indirecta. |
| bromelia | Bromelia | *familia Bromeliaceae* | segura | Cambie el agua del centro cada semana para evitar zancudos. |
| guaria_morada | Guaria morada | *Guarianthe skinneri* | segura | Amárrela a un tronco con luz filtrada; es la flor nacional. |
| hibisco | Amapola / hibisco | *Hibiscus rosa-sinensis* | segura | Pleno sol y riego regular; se poda para formar seto. |
| chinas | Chinas | *Impatiens walleriana* | segura | Semisombra y riego frecuente; no tolera sol fuerte. |
| rosa | Rosa | *Rosa spp.* | segura | Pleno sol y poda tras cada floración; cuidado con las espinas. |
| echeveria | Echeveria | *Echeveria spp.* | segura | Sustrato muy drenado; protéjala de la lluvia directa. |
| haworthia | Haworthia | *Haworthia spp.* | segura | Luz brillante sin sol fuerte; riego escaso. |
| veranera | Veranera | *Bougainvillea spp.* | sin_registro | Florece más con poco riego y pleno sol; cuidado con las espinas y la savia. |
| mono_senora | Moño de señora | *Mussaenda erythrophylla* | sin_registro | Sol o semisombra; se propaga fácil por esquejes. |
| heliconia | Platanilla / heliconia | *Heliconia spp.* | sin_registro | Semisombra, suelo húmedo y rico en materia orgánica. |
