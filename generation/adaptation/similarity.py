from generation.adaptation.node import Node
from generation.adaptation.query import Query
from generation.ontology.event_retriever import EventRetriever
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator
from typing import Iterable

def safe_max(values: Iterable[float]):
    return max(values, default=0)

def safe_mean(values: Iterable[float]):
    values = tuple(values)
    return sum(values) / len(values) if values else 0

def genre_similarity(node: Node, query: Query, retriever: EventRetriever):
    last_event = node.events[-1]
    _, genre_label = retriever.get_genre(last_event)
    return float(query.genre == genre_label.replace(" ", ""))

def event_similarity(node: Node, query: Query, sim_calculator: LocalSemanticSimilarityCalculator):
    last_event = node.events[-1]
    return safe_max(
        sim_calculator.wu_palmer_similarity_class_instance(q_event, last_event)
        for q_event in query.events
    )

def place_similarity(node: Node, query: Query, sim_calculator: LocalSemanticSimilarityCalculator):
    return safe_max(
        sim_calculator.wu_palmer_similarity_class(query.place, place)
        for place in node.places
    )

def object_similarity(node: Node, query: Query, sim_calculator: LocalSemanticSimilarityCalculator):
    return safe_max(
        sim_calculator.wu_palmer_similarity_class(query.object, object)
        for object in node.objects
    )

def role_similarity(node: Node, query: Query, sim_calculator: LocalSemanticSimilarityCalculator):
    return safe_mean(
        safe_max(
            sim_calculator.wu_palmer_similarity_class(q_role, role)
            for role in node.roles
        )
        for q_role in query.role
    )

def compute_event_similarity(node: Node, query: Query, weights: dict[str, float], retriever: EventRetriever, sim_calculator: LocalSemanticSimilarityCalculator):

    components = {
        "genre": genre_similarity(node, query, retriever),
        "event": event_similarity(node, query, sim_calculator),
        "place": place_similarity(node, query, sim_calculator),
        "object": object_similarity(node, query, sim_calculator),
        "role": role_similarity(node, query, sim_calculator),
    }

    total_sim = sum(
        components[name] * weights.get(name, 0)
        for name in components
    )

    return total_sim