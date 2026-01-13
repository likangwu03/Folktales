from generation.ontology.event_retriever import EventRetriever
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator
from generation.adaptation.astar import ConstructiveAdaptation
from generation.adaptation.query import Query
from generation.adaptation.alignment import process_events, print_dict, process_roles, process_objects, process_places, print_selected_uris, build_unique_uri_dict
from generation.adaptation.story_builder import story_builder
from generation.adaptation.alignment import dataframe_alignment_table
from generation.adaptation.similarity import best_similarity
from common.utils.loader import load_json_folder, data_dir, out_dir
from common.models.folktale import AnnotatedFolktale
from common.models.event import MIN_EVENTS
import generation.experiments.loader as loader
from generation.ontology.folktale_graph import create_graph
from loguru import logger

def main():
    folktales = []

    examples = load_json_folder(f"{data_dir}/examples/annotated")
    examples = {filename: AnnotatedFolktale(**folktale) for filename, folktale in examples.items()}

    for filename, folktale in examples.items():
        loader.generate_query(folktale, f"{filename}_query")

    folktales.extend(examples.values())
    
    out = load_json_folder(out_dir)
    out = [AnnotatedFolktale(**folktale) for folktale in out.values()]
    out = [folktale for folktale in out if len(folktale.events) > MIN_EVENTS]
    folktales.extend(out)

    graph = create_graph(
        folktales=folktales,
        filename="folktales.ttl",
        folder=loader.data_dir,
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

    queries = load_json_folder(loader.query_dir)
    for query in queries.values():
        query = Query.model_validate(query)

        logger.info(query)

        goal_node = constructive_adaptation.generate(query, query.max_events)

        if goal_node is not None:
            places, objects, roles = process_events(goal_node.event_elements, event_retriever)
            print(query.genre)
            process_roles(query.genre, roles, event_retriever, sim_calculator)
            process_objects(query.genre, objects,event_retriever, sim_calculator)
            process_places(query.genre, places,event_retriever, sim_calculator)

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
            
            goal_events =  [event_retriever.get_type_name(event_uri) for event_uri in goal_node.events]

            def sim(class1_id: str, class2_id: str):
                return sim_calculator.path_similarity_class(class1_id, class2_id) * 2

            score, pairs = best_similarity(query.events, goal_events,sim)
            score = score / (len(goal_events) + len(goal_events))
            print(f"Score: {score}")
            print(dataframe_alignment_table(query.events, goal_events,pairs))

if __name__ == "__main__":
    main()
