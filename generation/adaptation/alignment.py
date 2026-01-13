from queue import PriorityQueue
from generation.ontology.event_retriever import EventRetriever
from generation.ontology.folktale_graph import FolktaleOntology
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator
from generation.adaptation.similarity import best_similarity
from common.utils.regex_utils import snake_case_to_pascal_case, camel_to_snake
from loguru import logger
from collections import defaultdict
import pandas as pd

class ItemContainer:
    def __init__(self, id: str, n: int = 2):
        self.n = n
        self.id = id
        self.events: list[str] = []
        self.event_types: list[str] = []
        self.queue: PriorityQueue[tuple[int, str]] = PriorityQueue()

    def add_event(self, event_uri: str,event_type:str):
        self.events.append(event_uri)
        self.event_types.append(event_type)


    def add_candidate(self, event_uri: str, value: int = 0):
        self.queue.put((value, event_uri))
        if self.queue.qsize() > self.n:
            self.queue.get()

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

def process_events(events: dict[str, dict], eventRetriever: EventRetriever):
    places: dict[str, list[ItemContainer]] = {}
    objects: dict[str, list[ItemContainer]] = {}
    roles: dict[str, list[ItemContainer]] = {}

    for event_uri, data in events.items():
        event_type= eventRetriever.get_type_name(event_uri)

        place_id ,place_uri= eventRetriever.get_place_uri(event_uri)
        object_dict= eventRetriever.get_object_classes_dict(event_uri)
        role_dict= eventRetriever.get_role_classes_dict(event_uri)

        # -------- PLACE --------
        place = data["place"]
        if place not in places:
            places[place] = [ItemContainer(place)]

        if place != place_id:
            logger.error(f"Lugar no coincide: {place},{place_id}")

        places[place][0].add_event(event_uri,event_type)
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
                containers.append(ItemContainer(obj_id,len(containers)+1))

            # añadir evento y candidates a los primeros n contenedores
            for i in range(expected_count):
                containers[i].add_event(event_uri,event_type)
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
                containers.append(ItemContainer(role_id,len(containers)+1))

            # añadir evento y candidates (agentes)
            for i in range(expected_count):
                containers[i].add_event(event_uri,event_type)
                if i < len(agents):
                    containers[i].add_candidate(agents[i])

    return places, objects, roles

def process_roles(genre: str, container_dict: dict[str, list[ItemContainer]], eventRetriever: EventRetriever, sim: LocalSemanticSimilarityCalculator):
    genre = camel_to_snake(genre)
    for key, container_list in container_dict.items():
        roles = eventRetriever.get_roles_by_type_and_genre(snake_case_to_pascal_case(key),FolktaleOntology.GENRE_MAP[genre])
        for uri, label, folktale_title in roles:
            events = eventRetriever.get_ordered_events_for_agent(uri)
            event_types = [row[0] for row in events]
            print(f"uri: {uri}")
            print(event_types)
            for container in container_list:
                score, _ = best_similarity(event_types,container.event_types,sim.path_similarity_class)
                print(f"    - event_types: {container.event_types}")
                print(f"    - events: {container.events}")
                print(f"    - score: {score}")
                container.add_candidate(uri,score)

def process_objects(genre: str, container_dict: dict[str, list[ItemContainer]], eventRetriever: EventRetriever, sim:LocalSemanticSimilarityCalculator):
    genre = camel_to_snake(genre)
    for key, container_list in container_dict.items():
        objects = eventRetriever.get_objects_by_type_and_genre(snake_case_to_pascal_case(key),FolktaleOntology.GENRE_MAP[genre])
        for uri, label, folktale_title in objects:
            events = eventRetriever.get_ordered_events_for_object(uri)
            event_types = [row[0] for row in events]
            print(f"uri: {uri}")
            print(event_types)
            for container in container_list:
                score, _ = best_similarity(event_types,container.event_types,sim.path_similarity_class)
                print(f"    - event_types: {container.event_types}")
                print(f"    - events: {container.events}")
                print(f"    - score: {score}")
                container.add_candidate(uri,score)

def process_places(genre: str, container_dict: dict[str, list[ItemContainer]], eventRetriever: EventRetriever, sim: LocalSemanticSimilarityCalculator):
    genre = camel_to_snake(genre)
    for key, container_list in container_dict.items():
        places = eventRetriever.get_place_by_type_and_genre(snake_case_to_pascal_case(key),FolktaleOntology.GENRE_MAP[genre])
        for uri, label, folktale_title in places:
            events = eventRetriever.get_ordered_events_for_place(uri)
            event_types = [row[0] for row in events]
            print(f"uri: {uri}")
            print(event_types)
            for container in container_list:
                score, _ = best_similarity(event_types,container.event_types,sim.path_similarity_class)
                print(f"    - event_types: {container.event_types}")
                print(f"    - events: {container.events}")
                print(f"    - score: {score}")
                container.add_candidate(uri,score)

def build_unique_uri_dict(container_dict: dict[str, list[ItemContainer]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    used_uris: set[str] = set()

    for key, containers in container_dict.items():
        for container in containers:
            # Obtener candidatos ordenados por score DESC
            candidates = sorted(
                container.queue.queue,
                key=lambda x: x[0],
                reverse=True
            )

            selected_uri = None
            for score, uri in candidates:
                if uri not in used_uris:
                    selected_uri = uri
                    break

            if selected_uri is not None:
                result[container.id].append(selected_uri)
                used_uris.add(selected_uri)
            else:
                # TODO
                pass

    return dict(result)

def print_selected_uris(title: str, uri_dict: dict[str, list[str]]):
    print(f"\n=== {title.upper()} ===")

    if not uri_dict:
        print("  (vacío)")
        return

    for id_, uris in uri_dict.items():
        print(f"{id_}:")
        if not uris:
            print("  - (sin URI asignada)")
        else:
            for uri in uris:
                print(f"  - {uri}")


def alignment_table(A, B, pairs):
    """
    A: lista A
    B: lista B
    pairs: lista de tuplas (i,j) que indican emparejamientos
    """
    pair_map = {i: j for i, j in pairs}

    i = 0
    j = 0
    table = []
    while i < len(A) or j < len(B):

        # Caso: hay una pareja A[i] ↔ B[j]
        if i in pair_map and pair_map[i] == j:
            table.append((A[i], B[j]))
            i += 1
            j += 1

        # Caso: A[i] no está emparejado aquí → va solo
        elif i < len(A) and i not in pair_map:
            table.append((A[i], None))
            i += 1

        # Caso: B[j] no es usado por ningún A → va solo
        else:
            table.append((None, B[j]))
            j += 1

    return table


def dataframe_alignment_table(A, B, pairs):
    table = alignment_table(A, B, pairs)
    df = pd.DataFrame(table, columns=['Query','Generated'])
    return df
