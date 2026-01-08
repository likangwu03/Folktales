from generation.adaptation.query import Query
from generation.adaptation.node import Node
from generation.adaptation.similarity import compute_event_similarity
from generation.ontology.event_retriever import EventRetriever
from generation.ontology.similarity_calculator import LocalSemanticSimilarityCalculator
from common.models.event import MAX_EVENTS
from rdflib import Graph
from loguru import logger
import heapq

class ConstructiveAdaptation:
	graph: Graph
	retriever: EventRetriever
	weights: dict[str, float]
	sim_calculator: LocalSemanticSimilarityCalculator
	top_n: int
	g_weight: float
	h_weight: float
	
	def __init__(self, graph: Graph, weights: dict[str, float], retriever: EventRetriever, sim_calculator: LocalSemanticSimilarityCalculator, top_n: int = 5, g_weight: float = 1.0, h_weight: float = 2.0):
		self.graph = graph
		self.weights = weights
		self.retriever = retriever
		self.sim_calculator = sim_calculator
		self.top_n = top_n
		self.g_weight = g_weight
		self.h_weight = h_weight

	def _heuristic(self, node: Node, query: Query):
		sim = compute_event_similarity(node, query, self.weights, self.retriever, self.sim_calculator)
		h = -sim * self.h_weight
		return h
	
	def _path_cost(self, node: Node, max_events: int):
		n_events = len(node.events)
		return ((max_events - n_events) / max_events) ** 2 * self.g_weight
	
	def _debug_node(self, message: str, node: Node):
		logger.debug(f"{message}: events={node.get_event_names()}, g={node.g:.2f}, h={node.h:.2f}, f={node.f:.2f}")

	def generate(self, query: Query, max_events: int = MAX_EVENTS):
		open_heap: list[tuple[float, int, Node]] = []
		counter = 0

		initial_candidates = self.retriever.get_instances_of_class(query.initial_event)
		if not initial_candidates:
			initial_candidates = self.retriever.get_all_event_instances()

		scored_initial_candidates: list[Node] = []

		for candidate in initial_candidates:
			node = Node()
			node.add_event(candidate, self.retriever)
			node.h = self._heuristic(node, query)
			node.f = node.g + node.h
			scored_initial_candidates.append(node)

		top_initial_candidates = heapq.nsmallest(self.top_n, scored_initial_candidates, key=lambda node: node.h)

		for node in top_initial_candidates:
			heapq.heappush(open_heap, (node.f, counter, node))
			counter += 1
			self._debug_node("Initial node added", node)

		while open_heap:
			_, _, node = heapq.heappop(open_heap)
			self._debug_node("Expanding node", node)

			if node.is_goal(self.retriever, max_events):
				logger.debug(f"Goal reached: events={node.get_event_names()}, g={node.g:.2f}, h={node.h:.2f}, f={node.f:.2f}, places={node.places}, objects={node.objects}, roles={node.roles}")
				return node

			last_event = node.events[-1]
			candidates = self.retriever.get_post_event_instances(last_event, node.events)
			# logger.debug(f"Candidates for expansion from '{last_event.split("/")[-1]}': {[candidate.split("/")[-1] for candidate in candidates]}")

			scored_candidates: list[Node] = []

			for candidate in candidates:
				new_node = node.clone(
					parent=node
				)
				new_node.add_event(candidate, self.retriever)
				new_node.g = self._path_cost(node, max_events)
				new_node.h = self._heuristic(new_node, query)
				new_node.f = new_node.g + new_node.h
				scored_candidates.append(new_node)

			top_candidates = heapq.nsmallest(self.top_n, scored_candidates, key=lambda node: node.h)

			for new_node in top_candidates:
				heapq.heappush(open_heap, (new_node.f, counter, new_node))
				self._debug_node("New node added", new_node)
				counter += 1
		
		logger.debug("No valid sequence found.")
		return None