from generation.ontology.event_retriever import EventRetriever
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator
from generation.adaptation.astar import ConstructiveAdaptation
from generation.adaptation.query import Query
from common.loader import load_json, load_hierarchies, load_examples
from generation.ontology.folktale_graph import FolktaleOntology
from loguru import logger
from rdflib import Graph

def create_graph(build: bool=False, render_html: bool=False) -> Graph:
    graph = FolktaleOntology()
    if build:
        hierarchies = load_hierarchies()
        graph.build(hierarchies)

        examples = load_examples()
        for folktale in examples:
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
    
    graph = create_graph(build=True,
                         render_html=True)

    event_retriever = EventRetriever(graph)
    sim_calculator = LocalSemanticSimilarityCalculator(graph)

    query_json = load_json("./query.json")

    query = Query.model_validate(query_json)

    logger.info(query)

    weights = {
        "genre": 0.30,
        "event": 0.35,
        "role": 0.15,
        "place": 0.10,
        "object": 0.10,
    }

    constructive_adaptation = ConstructiveAdaptation(graph, query.max_events, weights, event_retriever, sim_calculator)
    goal_node = constructive_adaptation.generate(query)

if __name__ == "__main__":
    main()