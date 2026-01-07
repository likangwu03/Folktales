import json
from common.utils.regex_utils import snake_case_to_pascal_case
from generation.ontology.event_retriever import EventRetriever
from collections import defaultdict

class StoryBuilder:
    def __init__(self, uri, title, genre, nation):
        self.story = {
            "uri": uri,
            "has_genre": genre,
            "nation": nation,
            "title": title,
            "relationships": [],
            "agents": [],
            "places": [],
            "objects": [],
            "events": []
        }

    # ---------- AGENTS ----------
    def add_agent(
        self,
        class_name,
        instance_name,
        name,
        age_category,
        gender,
        personality,
        lives_in,
        role_class,
        role_instance
    ):
        agent = {
            "class_name": class_name,
            "instance_name": instance_name,
            "age_category": age_category,
            "gender": gender,
            "has_personality": personality,
            "lives_in": lives_in,
            "name": name,
            "has_role": {
                "class_name": role_class,
                "instance_name": role_instance
            }
        }
        self.story["agents"].append(agent)

    # ---------- RELATIONSHIPS ----------
    def add_relationship(self, agent, other, relationship):
        self.story["relationships"].append({
            "agent": agent,
            "other": other,
            "relationship": relationship
        })

    # ---------- PLACES ----------
    def add_place(self, class_name, instance_name):
        self.story["places"].append({
            "class_name": class_name,
            "instance_name": instance_name
        })

    # ---------- OBJECTS ----------
    def add_object(self, class_name, instance_name):
        self.story["objects"].append({
            "class_name": class_name,
            "instance_name": instance_name
        })

    # ---------- EVENTS ----------
    def add_event(
        self,
        class_name,
        instance_name,
        agents,
        place,
        objects=None,
        description=None
    ):
        event = {
            "class_name": class_name,
            "instance_name": instance_name,
            "agents": agents,
            "place": place,
            "objects": objects or []
        }

        if description:
            event["description"] = description

        self.story["events"].append(event)

    # ---------- EXPORT ----------
    def to_dict(self):
        return self.story

    def save_to_file(self, filename, indent=4, ensure_ascii=False):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.story, f, indent=indent, ensure_ascii=ensure_ascii)


def story_builder(builder: StoryBuilder, events_data: dict[str, dict], places_dict: dict[str, list[str]], objects_dict: dict[str, list[str]], roles_dict: dict[str, list[str]], eventRetriever: EventRetriever):

    # ---------- PLACES ----------
    place_index_map: dict[str, int] = {}

    for place_id, uris in places_dict.items():
        for uri in uris:
            builder.add_place(
                class_name=snake_case_to_pascal_case(place_id),
                instance_name=uri
            )
            place_index_map[place_id] = len(place_index_map)

    # ---------- OBJECTS ----------
    object_index_map: dict[str, list[int]] = defaultdict(list)

    for obj_id, uris in objects_dict.items():
        for uri in uris:
            builder.add_object(
                class_name=snake_case_to_pascal_case(obj_id),
                instance_name=uri
            )
            object_index_map[obj_id].append(
                len(builder.story["objects"]) - 1
            )

    # ---------- ROLES ----------
    agent_index_map: dict[str, list[int]] = defaultdict(list)

    for role_id, uris in roles_dict.items():
        role_class = snake_case_to_pascal_case(role_id)

        for uri in uris:
            builder.add_agent(
                class_name="None",
                instance_name=uri,
                name=uri.split("/")[-1],
                age_category="unknown",
                gender="unknown",
                personality=[],
                lives_in=-1,
                role_class=role_class,
                role_instance=role_id
            )

            agent_index_map[role_id].append(
                len(builder.story["agents"]) - 1
            )

    # ---------- EVENTS ----------
    for event_id, data in events_data.items():
        event_type = eventRetriever.get_event_type_name(event_id)

        place_id = data["place"]
        place_index = place_index_map.get(place_id)

        # agentes del evento
        agent_indices: list[int] = []
        for role_id in data["roles"]:
            agent_indices.extend(agent_index_map.get(role_id, []))

        # objetos del evento
        object_indices: list[int] = []
        for obj_id in data["object"]:
            object_indices.extend(object_index_map.get(obj_id, []))

        builder.add_event(
            class_name=event_type,
            instance_name=event_id,
            agents=agent_indices,
            place=place_index,
            objects=object_indices
        )
