from generation.ontology.event_retriever import EventRetriever
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator
from generation.adaptation.astar import ConstructiveAdaptation
from generation.adaptation.query import Query
from generation.adaptation.alignment import process_events, print_dict, process_roles, process_objects, process_places, print_selected_uris, build_unique_uri_dict
from generation.adaptation.story_builder import story_builder
from common.utils.loader import load_json_folder, data_dir, out_dir, load_json, load_txt_folder
from common.utils.regex_utils import clean_regex, title_case_to_snake_case
from generation.ontology.folktale_graph import create_graph
import generation.utils.sbc_tools as sbc
from loguru import logger
from dotenv import load_dotenv
from generation.story_generator import generate_story
from common.models.folktale import AnnotatedFolktale
from common.models.event import MIN_EVENTS
from generation.utils.loader import save_annotated_folktale, save_raw_folktale
import re

def main():
    load_dotenv()

    folktales = []

    raw_examples = load_txt_folder(f"{data_dir}/examples/raw")

    examples = load_json_folder(f"{data_dir}/examples/annotated")
    examples = {filename: AnnotatedFolktale(**folktale) for filename, folktale in examples.items()}

    folktales.extend(examples.values())

    keys = ["the_hare_and_the_tortoise"]
    generation_examples = [
        (examples[key], "\n".join(raw_examples[key].splitlines()[1:]))
        for key in keys
    ]
    
    out = load_json_folder(out_dir)
    out = [AnnotatedFolktale(**folktale) for folktale in out.values()]
    out = [folktale for folktale in out if len(folktale.events) > MIN_EVENTS]
    folktales.extend(out)

    graph = create_graph(
        folktales=folktales,
        filename="folktales.ttl",
        folder=sbc.data_path,
        build=True,
        render_html=False
    )
    
    event_retriever = EventRetriever(graph)
    sim_calculator = LocalSemanticSimilarityCalculator(graph)

    weights = {
        "genre": 0.15,
        "event": 0.40,
        "role": 0.20,
        "place": 0.15,
        "object": 0.10
    }

    constructive_adaptation = ConstructiveAdaptation(graph, weights, event_retriever, sim_calculator, top_n= 5)

    query_json = load_json("./query.json")
    query = Query.model_validate(query_json)

    logger.info(query)

    goal_node = constructive_adaptation.generate(query, query.max_events)

    if goal_node is not None:
        places, objects, roles = process_events(goal_node.event_elements,event_retriever)
        process_roles("fable", roles, event_retriever, sim_calculator)
        process_objects("fable",objects,event_retriever,sim_calculator)
        process_places("fable",places,event_retriever,sim_calculator)

        print_dict("places", places)
        print_dict("objects", objects)
        print_dict("roles", roles)

        places_dict = build_unique_uri_dict(places)
        objects_dict = build_unique_uri_dict(objects)
        roles_dict = build_unique_uri_dict(roles)

        print_selected_uris("Places", places_dict)
        print_selected_uris("Objects", objects_dict)
        print_selected_uris("Roles", roles_dict)

        folktale = story_builder(query.title,query.genre, goal_node.event_elements, places_dict, objects_dict, roles_dict, event_retriever)

        # story = generate_story(folktale, generation_examples)

        filename = re.sub(clean_regex, "", folktale.title)
        filename = title_case_to_snake_case(filename)
        # save_raw_folktale(story, filename)

        save_annotated_folktale(folktale, filename)

if __name__ == "__main__":
    main()
