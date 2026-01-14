# Anotación y Generación de Cuentos Populares
Este proyecto consiste en la anotación y generación de cuentos populares estructurados a partir de un esquema propio inspirado en las idea de *Morfología del cuento* de Vladimir Propp. 

## Descripción general
El sistema se compone de dos componentes principales:
1. **Anotación de cuentos**
   Permite la anotación automática de cuentos en lenguaje natural mediante un modelo de lenguaje y díferentes técnicas de prompt engineering.

2. **Generación de cuentos**
   Utiliza los cuentos previamente anotados para poblar un grafo de conocimiento, que a través de razonamiento por similitud, el sistema permite crear nuevos cuentos a partir de la recombinación de elementos provenientes de distintos relatos existentes.

## Dataset
Los datos utilizados para la anotación y la construcción del grafo de conocimiento, se han obtenido del siguiente dataset de Kaggle:

- [Folk Tales Dataset - Kaggle](https://www.kaggle.com/datasets/andrzejpanczenko/folk-tales-dataset)

Este conjunto de datos contiene cuentos populares de diversas nacionalidades y tradiciones culturales.

## Instalación
Clona el repositorio y asegúrate de tener `uv` correctamente instalado:

```bash
git clone <url-del-repositorio>
cd <nombre-del-repositorio>
```

## Ejecución
El  proyecto está compuesto por diferentes módulos. Cada uno puede ejecutarse mediante el siguiente comando:
```bash
uv run -m <módulo>.main
```

## Módulos

### `annotation`

Realiza la anotación automática del dataset ubicado en:

```
./data/folk_tales_deduplicated.csv
```

#### Configuración requerida

- Instalar Ollama
- Configurar la variable de entorno:

```bash
export OLLAMA_HOST=http://localhost:11434
```

- Descargar el modelo
```bash
ollama pull llama3.1:8b
```

**Ejecución**
```bash
uv run -m annotation.main
```

### `generation`
Permite generar un nuevo cuento popular a partir de la recombinación de elementos narrativos de distintos cuentos anotados.

#### Configuración requerida
Antes de ejecutar el módulo, hay que modificar el archivo de consulta:
```
./query.json
```

A continuación, se muestra un ejemplo de consulta:
```json
{
    "title": "The Tale of Ralph",
    "events": [
        "initial_situation",
        "villainy",
        "struggle",
        "helper_move"
    ],
    "roles": [
        "hero",
        "antagonist",
        "helper",
        "secondary_character",
    ],
    "objects": [],
    "places": [
        "city"
    ],
    "genre": "legend",
    "max_events": 15
}
```
Cada uno de los parámetros, a excepción del `title` y `max_events`, tienen que corresponder con tipos pertenecientes a sus respectivas clasificaciones. A continuación, se describe cada campo de forma detallada forma detallada. Además, cada uno de ellos actúa como recomendaciones y no como restricciones estrictas.
- `title`: Nombre del cuento generado.
- `events`: Secuencia ordenada de tipos eventos que deberían aparecer en el cueneto.
- `roles`: Tipos de roles de personajes que deberían aparecer en la historia.
- `objetos`: Tipos de objetos que al usuario le gustaría que aparecieran en el cuento.
- `places`: Tipos de lugares que al usuario le gustaría que estuvieran en el cuento.
- `genre`: Tipo del nuevo cuento.
- `max_events`: Número máximo recomendado de eventos por el que debería estar formado el relato.

Además, es necesario configurar la variable de entorno `GROQ_CLOUD` con el secreto de [Groq Cloud](https://console.groq.com/home):
```bash
export GROQ_CLOUD=<tu_api_key>
```

**Ejecución**
```bash
uv run -m generation.main
```

**Salida**

Los cuentos generados se almacenan en:
```
./generation/out
```

**Experimentos**

Dentro de este módulo puede ejecutarse el submódulo `experiments`, que realiza una evaluación *leave-one-out* para comprobar si el sistema es capaz de generar cuentos similares a los siguientes relatos anotados manualmente:
- *Cenicienta*
- *La liebre y la tortuga*
- *Los tres cerditos*

### `common`
Muestra información y estadísticas generales sobre los cuentos anotados.

**Ejecución**
```bash
uv run -m common.main
```

## Estructura del proyecto
```kotlin
.
├── annotation/
├── generation/
│   ├── experiments/
│   └── out/
|       ├── annotated/
|       └── raw/
├── common/
├── data/
│   └── folk_tales_deduplicated.csv
├── query.json
└── README.md
```

## Taxonomías
A continuación, se muestran las diferentes taxonomías, necesarias para definir una consulta al momento de generar un cuento.

### Género
Define el tipo del cuento.
```mermaid
graph LR
    genre --> fable
    genre --> fairy_tale
    genre --> legend
    genre --> myth
```

### Eventos
Describe los tipos de evento, que se basan en las 31 funciones de Propp. De manera general, se dividen en `move`, que representa el desarrollo de la trama principal, y `resolution`, que corresponde a la resolución del conflicto.
```mermaid
graph LR
    event --> move
    move --> setup
    setup --> initial_situation

    move --> conflict
    conflict --> hero_interdiction
    conflict --> villainy

    villainy --> false_matrimony
    villainy --> expulsion
    villainy --> kidnapping
    villainy --> murder
    villainy --> lack
    lack --> lack_of_bride
    lack --> lack_of_money

    conflict --> hero_departure

    conflict --> struggle
    struggle --> fight

    conflict --> branding
    branding --> receive_mark
    branding --> receive_injury

    conflict --> connective_incident

    connective_incident --> call_for_help
    connective_incident --> departure_decision

    conflict --> villain_gains_information

    move --> preparation
    preparation --> absentation
    preparation --> breaking_interdiction
    preparation --> acquisition
    acquisition --> get_present
    preparation --> guidance
    preparation --> return
    preparation --> make_contact_with_enemy
    preparation --> mediation
    preparation --> trickery

    move --> beginning_of_counteraction

    move --> helper_move
    helper_move --> receipt_object
    helper_move --> liquidation_of_lack
    liquidation_of_lack --> release_from_captivity
    helper_move --> pursuit_and_rescue

    move --> false_hero_make_unfounded_claim
    move --> attempt_at_reconnaissance

    event --> resolution
    resolution --> victory
    victory --> villain_defeated

    resolution --> arrival
    arrival --> unrecognised_arrival
    unrecognised_arrival --> home_arrival

    resolution --> difficult_task_with_solution
    difficult_task_with_solution --> difficult_task
    difficult_task_with_solution --> solution_difficult_task

    resolution --> resolution_function
    resolution_function --> recognition
    resolution_function --> punishment
    resolution_function --> reward

    resolution --> exposure_of_villain

    resolution --> transfiguration
    transfiguration --> physical_transformation
    transfiguration --> psychological_transformation

    resolution --> wedding_or_throne
    wedding_or_throne --> wedding
    wedding_or_throne --> get_throne
```

### Roles
Describe las funciones que cumplen los personajes dentro de la historia, tomando como referencia las 7 esferas de acción de Propp.
```mermaid
graph LR
    role --> primary_character
    role --> secondary_character
    role --> tertiary_character

    primary_character --> main_character
    primary_character --> antagonist
    primary_character --> false_hero

    main_character --> hero
    antagonist --> villain

    secondary_character --> helper
    helper --> magical_helper

    secondary_character --> prisoner
    secondary_character --> princess
    secondary_character --> quest_giver
    secondary_character --> hero_family
```

### Lugares
Especifica los distintos escenarios que pueden aparecer en un cuento, incluyendo tanto los entornos naturales como los creados por el ser humano.
```mermaid
graph LR
    place --> natural_place
    natural_place --> mountain
    natural_place --> forest
    natural_place --> river
    natural_place --> field

    place --> building
    building --> dwelling
    dwelling --> castle
    dwelling --> palace
    dwelling --> house
    dwelling --> hut
    dwelling --> farmhouse
    dwelling --> tower

    building --> community_building
    community_building --> shop
    community_building --> school
    community_building --> tavern

    place --> settlement
    settlement --> village
    settlement --> town
    settlement --> city
    settlement --> kingdom
```

### Objetos
Define los distintos objetos que pueden aparecer en un cuento, destacando los objetos mágicos, característicos de este tipo de narrativa.
```mermaid
graph LR
    object --> natural_object
    object --> magical_object
    object --> crafted_object
```
