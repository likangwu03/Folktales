from queue import PriorityQueue
from generation.ontology.event_retriever import EventRetriever
from generation.ontology.folktale_graph import FolktaleOntology
from generation.adaptation.similarity import best_similarity
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator

from common.utils.regex_utils import snake_case_to_pascal_case
from loguru import logger

class ItemContainer:
    def __init__(self, id_: str):
        self.id = id_
        self.events: list[str] = []
        self.event_types: list[str] = []
        self.queue: PriorityQueue[tuple[int, str]] = PriorityQueue()

    def add_event(self, event_id: str, event_type:str):
        self.events.append(event_id)
        self.event_types.append(event_type)


    def add_candidate(self, event_id: str, value: int = 0):
        self.queue.put((value, event_id))

def print_dict(title: str, container_dict: dict[str, list[ItemContainer]]):
    print(f"\n=== {title.upper()} ===")
    if not container_dict:
        print("  (vacío)")
        return
    for key, container_list in container_dict.items():
        print(f"{key}:")
        for container in container_list:
            print(f"  ItemContainer id: {container.id}")
            print(f"    events: {container.events}")
            # Mostrar los elementos de la cola sin vaciarla
            queue_contents = list(container.queue.queue)
            print(f"    queue: {queue_contents}")

def process_events(events: dict[str, dict], eventRetriever:EventRetriever):
    places: dict[str, list[ItemContainer]] = {}
    objects: dict[str, list[ItemContainer]] = {}
    roles: dict[str, list[ItemContainer]] = {}

    for event_id, data in events.items():
        event_type= eventRetriever.get_event_type_name(event_id)

        place_id ,place_uri= eventRetriever.get_place_uri(event_id)
        object_dict= eventRetriever.get_object_classes_dict(event_id)
        role_dict= eventRetriever.get_role_classes_dict(event_id)

        # -------- PLACE --------
        place = data["place"]
        if place not in places:
            places[place] = [ItemContainer(place)]

        if place != place_id:
            logger.error(f"Lugar no coincide: {place},{place_id}")

        places[place][0].add_event(event_id,event_type)
        places[place][0].add_candidate(place_uri)

        # -------- OBJECTS --------
        for obj_id, count_in_data in data["object"].items():
            if obj_id not in object_dict:
                logger.warning(f"Objeto {obj_id} no encontrado en eventRetriever")
                continue
            expected_count, uris = object_dict[obj_id]

            # Si el count de data difiere del count real, log
            if count_in_data != expected_count:
                logger.warning(f"Count de objeto {obj_id} difiere: data={count_in_data}, real={expected_count}")

            if obj_id not in objects:
                objects[obj_id] = []

            containers = objects[obj_id]

            # asegurar suficientes contenedores según count real
            while len(containers) < expected_count:
                containers.append(ItemContainer(obj_id))

            # añadir evento y candidates a los primeros n contenedores
            for i in range(expected_count):
                containers[i].add_event(event_id,event_type)
                # añadir candidate si hay suficientes uris
                if i < len(uris):
                    containers[i].add_candidate(uris[i])

        # -------- ROLES --------
        for role_id, count_in_data in data["roles"].items():
            if role_id not in role_dict:
                logger.warning(f"Rol {role_id} no encontrado en eventRetriever")
                continue

            expected_count, agents = role_dict[role_id]

            # log si el count difiere
            if count_in_data != expected_count:
                logger.warning(f"Count de rol {role_id} difiere: data={count_in_data}, real={expected_count}")

            if role_id not in roles:
                roles[role_id] = []

            containers = roles[role_id]

            # asegurar suficientes contenedores según count real
            while len(containers) < expected_count:
                containers.append(ItemContainer(role_id))

            # añadir evento y candidates (agentes)
            for i in range(expected_count):
                containers[i].add_event(event_id,event_type)
                if i < len(agents):
                    containers[i].add_candidate(agents[i])

    return places, objects, roles

def process_roles(genre: str, container_dict: dict[str, list[ItemContainer]], eventRetriever: EventRetriever, sim: LocalSemanticSimilarityCalculator):
    for key, container_list in container_dict.items():
        roles = eventRetriever.get_roles_by_type_and_genre(snake_case_to_pascal_case(key), FolktaleOntology.GENRE_MAP[genre])
        for uri, label, folktale_title in roles:
            events = eventRetriever.get_ordered_events_for_agent(uri)
            event_types = [row[0] for row in events]
            print(f"uri: {uri}")
            print(event_types)
            for container in container_list:
                score, _ = best_similarity(event_types,container.event_types, sim.wu_palmer_similarity_class)
                print(f"    - event_types: {container.event_types}")
                print(f"    - events: {container.events}")
                print(f"    - score: {score}")
                container.add_candidate(uri,score)

    return

# def process_roles(genre: str, container_dict: dict[str, list[ItemContainer]],eventRetriever:EventRetriever, sim:LocalSemanticSimilarityCalculator):
#     for key, container_list in container_dict.items():
#         roles = eventRetriever.get_roles_by_type_and_genre(snake_case_to_pascal_case(key),FolktaleOntology.GENRE_MAP[genre])
#         for uri, label, folktale_title in roles:
#             events = eventRetriever.get_ordered_events_for_agent(uri)
#             event_types = [row[0] for row in events]
#             print(f"uri: {uri}")
#             print(event_types)
#             for container in container_list:
#                 score, _ = best_similarity(event_types,container.event_types,sim.wu_palmer_similarity_class)
#                 print(f"    - event_types: {container.event_types}")
#                 print(f"    - events: {container.events}")
#                 print(f"    - score: {score}")
#                 container.add_candidate(uri,score)

#     return

# def process_roles(genre: str, container_dict: dict[str, list[ItemContainer]],eventRetriever:EventRetriever, sim:LocalSemanticSimilarityCalculator):
#     for key, container_list in container_dict.items():
#         roles = eventRetriever.get_roles_by_type_and_genre(snake_case_to_pascal_case(key),FolktaleOntology.GENRE_MAP[genre])
#         for uri, label, folktale_title in roles:
#             events = eventRetriever.get_ordered_events_for_agent(uri)
#             event_types = [row[0] for row in events]
#             print(f"uri: {uri}")
#             print(event_types)
#             for container in container_list:
#                 score, _ = best_similarity(event_types,container.event_types,sim.wu_palmer_similarity_class)
#                 print(f"    - event_types: {container.event_types}")
#                 print(f"    - events: {container.events}")
#                 print(f"    - score: {score}")
#                 container.add_candidate(uri,score)

#     return