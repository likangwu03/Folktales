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
	max_events: int
	weights: dict[str, float]
	
	def __init__(self, graph: Graph, weights: dict[str, float], retriever: EventRetriever, sim_calculator: LocalSemanticSimilarityCalculator, max_events: int = MAX_EVENTS):
		self.graph = graph
		self.max_events = max_events
		self.weights = weights
		self.retriever = retriever
		self.sim_calculator = sim_calculator

	def _heuristic(self, node: Node, query: Query):
		return 1 - compute_event_similarity(node, query, self.weights, self.retriever, self.sim_calculator)
	
	def _debug_node(self, message: str, node: Node):
		logger.debug(f"{message}: events={node.get_event_names()}, g={node.g:.2f}, h={node.h:.2f}, f={node.f:.2f}")

	def generate(self, query: Query):
		open_heap: list[tuple[float, int, Node]] = []
		counter = 0

		initial_candidates = self.retriever.get_instances_of_class(query.initial_event)
		if not initial_candidates:
			initial_candidates = self.retriever.get_all_event_instances()

		for candidate in initial_candidates:
			node = Node()
			node.add_event(candidate, self.retriever)
			node.h = self._heuristic(node, query)
			node.f = node.g + node.h
			heapq.heappush(open_heap, (node.f, counter, node))
			counter += 1
			self._debug_node("Initial node added", node)

		while open_heap:
			_, _, node = heapq.heappop(open_heap)
			self._debug_node("Expanding node", node)

			if node.is_goal(self.retriever, self.max_events):
				logger.debug(f"Goal reached: events={node.get_event_names()}, places={node.places}, objects={node.objects}, roles={node.roles}")
				return node

			last_event = node.events[-1]
			candidates = self.retriever.get_post_event_instances(last_event, node.events)
			logger.debug(f"Candidates for expansion from '{last_event.split("/")[-1]}': {[candidate.split("/")[-1] for candidate in candidates]}")

			for candidate in candidates:
				new_node = node.clone(
					parent=node,
					g=(node.g + 1) / self.max_events
				)
				new_node.add_event(candidate, self.retriever)
				new_node.h = self._heuristic(new_node, query)
				new_node.f = new_node.g + new_node.h
				heapq.heappush(open_heap, (new_node.f, counter, new_node))
				self._debug_node("New node added", new_node)
				counter += 1
		
		logger.debug("No valid sequence found.")
		return None