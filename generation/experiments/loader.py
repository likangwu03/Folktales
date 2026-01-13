from common.models.folktale import AnnotatedFolktale
from common.utils.loader import save_json
import os

main_dir = "generation/experiments/"
query_dir = os.path.join(main_dir, "query")
data_dir = os.path.join(main_dir, "data")

def generate_query(folktale: AnnotatedFolktale, filename: str):
    """
    Genera una query dado un cuento anotado
    """
    title = folktale.title
    genre = folktale.has_genre

    event_types = [e.class_name for e in folktale.events]

    max_events = len(folktale.events)

    roles = [agent.has_role.class_name for agent in folktale.agents]
    objects = [object.class_name for object in folktale.objects]
    places = [place.class_name for place in folktale.places]

    query = {
        "title": title,
        "events": event_types,
        "roles": roles,
        "objects": objects,
        "places": places,
        "genre": genre,
        "max_events": max_events
    }

    os.makedirs(query_dir, exist_ok=True)
    filename = filename + ".json"
    filepath = os.path.join(query_dir, filename)
    save_json(filepath,query)
    return query
