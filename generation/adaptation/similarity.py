from generation.adaptation.node import Node
from generation.adaptation.query import Query
from generation.ontology.event_retriever import EventRetriever
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator

from typing import Iterable, Callable, Any
import numpy as np

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
    def sim(class1_id, class2_id):
        return sim_calculator.wu_palmer_similarity_class(class1_id, class2_id) * 2
    score, pairs = best_similarity(query.events,node.events_type,sim)
    score = score / (len(query.events) + len(node.events_type))

    return score
    last_event = node.events[-1]
    return safe_max(
        sim_calculator.wu_palmer_similarity_class_instance(q_event, last_event)
        for q_event in query.events
    )

def place_similarity(node: Node, query: Query, sim_calculator: LocalSemanticSimilarityCalculator):
    return safe_mean(
        safe_max(
            sim_calculator.wu_palmer_similarity_class(q_place, place)
            for place in node.places
        )
        for q_place in query.places
    )

def object_similarity(node: Node, query: Query, sim_calculator: LocalSemanticSimilarityCalculator):
    return safe_mean(
        safe_max(
            sim_calculator.wu_palmer_similarity_class(q_object, object)
            for object in node.objects
        )
        for q_object in query.objects
    )
    # return safe_max(
    #     sim_calculator.wu_palmer_similarity_class(query.object, object)
    #     for object in node.objects
    # )

def role_similarity(node: Node, query: Query, sim_calculator: LocalSemanticSimilarityCalculator):
    return safe_mean(
        safe_max(
            sim_calculator.wu_palmer_similarity_class(q_role, role)
            for role in node.roles
        )
        for q_role in query.roles
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

def best_similarity(A: list[Any], B: list[Any], sim: Callable[[Any, Any], float],penalty: float = 0.0) -> tuple[float, list[tuple[int, int]]]:
    """
    Devuelve:
    - score óptimo
    - lista de emparejamientos (i, j), índices en A y B
      Los eventos no usados no aparecen en la lista
    """

    n, m = len(A), len(B)

    # DP y backtracking
    dp = np.zeros((n + 1, m + 1), dtype=float)
    bt = np.empty((n + 1, m + 1), dtype=object)
    
    # dp[i][j] La mejor similitud total posible usando los primeros i eventos de la lista A y los primeros j eventos de la lista B.
    # dp[0][0] → no usar ningún evento
    # dp[i][0] → usar i eventos de A y ninguno de B
    # dp[n][m] → solución óptima final

    # Casos base
    for i in range(1, n + 1):
        dp[i, 0] = -i * penalty
        bt[i, 0] = ('A', i - 1)

    for j in range(1, m + 1):
        dp[0, j] = -j * penalty
        bt[0, j] = ('B', j - 1)

    # DP principal
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = dp[i - 1, j - 1] + sim(A[i - 1], B[j - 1])
            skip_a = dp[i - 1, j] - penalty
            skip_b = dp[i, j - 1] - penalty

            best = max(match, skip_a, skip_b)
            dp[i, j] = best

            if best == match:
                bt[i, j] = ('M', i - 1, j - 1)
            elif best == skip_a:
                bt[i, j] = ('A', i - 1)
            else:
                bt[i, j] = ('B', j - 1)

    # Reconstrucción
    i, j = n, m
    matches = []

    while i > 0 or j > 0:
        step = bt[i, j]

        if step[0] == 'M':
            _, ai, bj = step
            matches.append((ai, bj))
            i -= 1
            j -= 1
        elif step[0] == 'A':
            i -= 1
        else:  # 'B'
            j -= 1

    matches.reverse()
    return float(dp[n, m]), matches
