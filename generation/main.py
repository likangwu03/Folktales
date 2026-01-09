from generation.ontology.event_retriever import EventRetriever
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator
from generation.adaptation.astar import ConstructiveAdaptation
from generation.adaptation.query import Query
from generation.adaptation.alignment import process_events, print_dict, process_roles, process_objects, process_places, print_selected_uris, build_unique_uri_dict
from generation.adaptation.story_builder import story_builder
from common.utils.loader import load_json_folder, load_txt_folder, data_dir, out_dir, save_raw_folktale, load_json, save_annotated_folktale
from generation.ontology.folktale_graph import FolktaleOntology
from loguru import logger
from rdflib import Graph
from dotenv import load_dotenv
from generation.story_generator import generate_story
from common.models.folktale import AnnotatedFolktale
from common.models.event import MIN_EVENTS
import os

def create_graph(folktales: list[AnnotatedFolktale], build: bool=False, render_html: bool=False) -> Graph:
    graph = FolktaleOntology()
    if build:
        hierarchies = load_json_folder(f"{data_dir}/hierarchies")
        graph.build(hierarchies)

        for folktale in folktales:
            graph.add_folktale(folktale)

        graph.add_imports()
        graph.save()
        if render_html:
            graph.render_html("instances")

    logger.debug(f"Grafo initialized with {len(graph)} triplets.")

    graph.load()

    logger.debug(f"Grafo initialized with {len(graph)} triplets after loading.")

    return graph

def main():
    load_dotenv()

    # examples_dir = os.path.join(data_dir, "examples")
    # raw_dir = os.path.join(examples_dir, "raw")
    # annotated_dir = os.path.join(examples_dir, "annotated")
    # examples_json = load_json_folder(annotated_dir)
    # raw_examples = load_txt_folder(raw_dir)
    
    # keys = ["the_hare_and_the_tortoise"]
    # examples = [(AnnotatedFolktale(**examples_json[key]), raw_examples[key]) for key in keys]

    # folktale = AnnotatedFolktale(**examples_json["cinderella"])
    
    # story = generate_story(folktale, examples)

    # save_raw_folktale(story, folktale.title)

    folktales = []
    # examples = load_json_folder(f"{data_dir}/examples/annotated")
    # examples = [AnnotatedFolktale(**folktale) for folktale in examples.values()]
    # folktales.extend(examples)

    out = load_json_folder(f"{out_dir}/annotated")
    out = [AnnotatedFolktale(**folktale) for folktale in out.values()]
    out = [folktale for folktale in out if len(folktale.events) > MIN_EVENTS]
    folktales.extend(out)

    print(len(folktales))

    graph = create_graph(
        folktales=folktales,
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

    constructive_adaptation = ConstructiveAdaptation(graph, weights, event_retriever, sim_calculator, top_n= 1)

    query_json = load_json("./query.json")
    query = Query.model_validate(query_json)

    logger.info(query)

    goal_node = constructive_adaptation.generate(query, 2)

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

        f = story_builder("Generated Story","fable" ,goal_node.event_elements,places_dict,objects_dict,roles_dict,event_retriever)

        save_annotated_folktale(f,"Matt")

if __name__ == "__main__":
    main()
