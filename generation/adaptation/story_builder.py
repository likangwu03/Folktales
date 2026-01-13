from common.utils.regex_utils import camel_to_snake, title_case_to_snake_case
from generation.ontology.event_retriever import EventRetriever
from collections import defaultdict
from common.models.folktale import AnnotatedFolktale, GenreClass
from common.models.place import Place, PlaceClass
from common.models.object import Object, ObjectClass
from common.models.agent import Agent, AgentClass
from common.models.role import Role, RoleClass
from common.models.event import Event, EventClass

def story_builder(title: str, genre:str, events_data: dict[str, dict], places_dict: dict[str, list[str]], objects_dict: dict[str, list[str]], roles_dict: dict[str, list[str]], eventRetriever: EventRetriever):

    # ---------- PLACES ----------
    place_index_map: dict[str, int] = {}
    places: list[Place] = []

    for place_id, uris in places_dict.items():
        uri = uris[0]
        place_class = PlaceClass(camel_to_snake(place_id))
        place_label = title_case_to_snake_case(eventRetriever.get_label(uri))
        place = Place(class_name=place_class,instance_name=place_label)
        places.append(place)
        place_index_map[place_id] = len(place_index_map)

    # ---------- OBJECTS ----------
    object_index_map: dict[str, list[int]] = defaultdict(list)
    objects: list[Object] = []
    for obj_id, uris in objects_dict.items():
        for uri in uris:
            object_class = ObjectClass(camel_to_snake(obj_id))
            object_label = title_case_to_snake_case(eventRetriever.get_label(uri))
            _object = Object(class_name=object_class,instance_name=object_label)
            objects.append(_object)
            object_index_map[obj_id].append(len(objects)- 1)

    # ---------- ROLES ----------
    agents: list[Agent] = []
    agent_index_map: dict[str, list[int]] = defaultdict(list)

    for role_id, uris in roles_dict.items():
        role_class = RoleClass(camel_to_snake(role_id))
        for uri in uris:
            print(uri)
            role_label = eventRetriever.get_role_labels(uri)
            role_label = title_case_to_snake_case(role_label)
            role = Role(class_name= role_class, instance_name= role_label)

            agent_label = title_case_to_snake_case(eventRetriever.get_label(uri))
            age_category = eventRetriever.get_age_category(uri)
            age_category = age_category.split("/")[-1] # TODO
            personality = eventRetriever.get_personality_traits(uri)
            personality = [camel_to_snake(obj.split("/")[-1]) for obj in personality]

            name = eventRetriever.get_name(uri)
            gender = eventRetriever.get_gender(uri)
            agent_class_name = eventRetriever.get_type_name(uri)
            agent_class = AgentClass(camel_to_snake(agent_class_name))
            agent = Agent(
                class_name= agent_class,
                instance_name= agent_label,
                age_category= age_category,
                gender=gender,
                name= name,
                has_role=role,
                has_personality=personality,
                lives_in=None
            )
            agents.append(agent)
            agent_index_map[role_id].append(
                len(agents) - 1
            )

    # ---------- EVENTS ----------

    events: list[Event] = []
    for event_uri, data in events_data.items():
        event_type = eventRetriever.get_type_name(event_uri)

        place_id = data["place"]
        place_index = place_index_map.get(place_id)

        # agentes del evento
        agent_indices: list[int] = []
        for role_id, n in data["roles"].items():
            agent_indices.extend(agent_index_map.get(role_id, [])[:n])


        # objetos del evento
        object_indices: list[int] = []
        for obj_id, n in data["object"].items():
            object_indices.extend(object_index_map.get(obj_id, [])[:n])
        
        event_class = EventClass(camel_to_snake(event_type))
        event_label = title_case_to_snake_case(eventRetriever.get_label(event_uri))
        event = Event(
            class_name=event_class,
            instance_name= event_label,
            agents= agent_indices,
            objects= object_indices,
            place= place_index
        )

        events.append(event)
        
    genre_class = GenreClass(camel_to_snake(genre))
    return AnnotatedFolktale(
        title= title,
        has_genre= genre_class,
        agents= agents,
        places= places,
        objects= objects,
        events= events
    )
