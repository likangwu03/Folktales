from generation.constructive_adaptation.query import Query
from generation.constructive_adaptation.node import Node
from generation.constructive_adaptation.similarity import event_similarity
from generation.ontology.event_retriever import EventRetriever
from rdflib import Graph
from loguru import logger
import heapq

class ConstructiveAdaptation:
	graph: Graph
	retriever: EventRetriever
	max_events: int
	
	def __init__(self, graph: Graph, retriever: EventRetriever, max_events: int):
		self.graph = graph
		self.retriever = retriever
		self.max_events = max_events

	def _heuristic(self, node: Node, query: Query):
		return 1 - event_similarity(node, query)
	
	def _debug_node(self, message: str, node: Node):
		logger.debug(f"{message}: events={node.get_event_names()}, g={node.g:.2f}, h={node.h:.2f}, f={node.f:.2f}")

	def generate(self, query: Query):
		open_heap: list[tuple[float, int, Node]] = []
		counter = 0

		initial_candidates = self.retriever.get_instances_of_class(query.initial_event_type)
		if not initial_candidates:
			initial_candidates = self.retriever.get_all_event_instances()

		for candidate in initial_candidates:
			node = Node(events=[candidate], parent=None, g=0)
			node.h = self._heuristic(node, query)
			node.f = node.g + node.h
			heapq.heappush(open_heap, (node.f, counter, node))
			counter += 1
			self._debug_node("Initial node added", node)

		while open_heap:
			_, _, node = heapq.heappop(open_heap)
			self._debug_node("Expandind node", node)

			if node.is_goal(self.retriever, self.max_events):
				logger.debug(f"Goal reached: {node.get_event_names()}")
				return node

			last_event = node.events[-1]
			candidates = self.retriever.get_post_event_instances(last_event, node.events)
			logger.debug(f"Candidates for expansion from '{last_event.split("/")[-1]}': {[candidate.split("/")[-1] for candidate in candidates]}")

			for candidate in candidates:
				new_events = node.events + [candidate]
				new_node = Node(events=new_events,
								parent=node,
								g=(node.g + 1) / self.max_events)
				new_node.h = self._heuristic(new_node, query)
				new_node.f = new_node.g + new_node.h
				heapq.heappush(open_heap, (new_node.f, counter, new_node))
				self._debug_node("New node added", new_node)
				counter += 1
		
		logger.debug("No valid sequence found.")
		return None