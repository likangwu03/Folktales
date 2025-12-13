from generation.ontology.namespaces import RES
from generation.ontology.event_retriever import EventRetriever
from generation.constructive_adaptation.astar import ConstructiveAdaptation
from generation.constructive_adaptation.query import Query
import generation.utils.sbc_tools as sbc

def main():
    graph = sbc.load("folktales.ttl")
    event_retriever = EventRetriever(graph)

    constructive_adaptation = ConstructiveAdaptation(graph, event_retriever, 15)
    query = Query(initial_event_type="InitialSituation")
    goal_node = constructive_adaptation.generate(query)

if __name__ == "__main__":
    main()