from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from generation.ontology.event_retriever import EventRetriever
import copy

class Node(BaseModel):
	parent: Optional[Node] = None
	f: float = 0
	g: float = 0
	h: float = 0
	events: list[str] = Field(default_factory=list)
	roles: dict[str, int] = Field(default_factory=dict)
	places: set[str] = Field(default_factory=set)
	objects: dict[str, int] = Field(default_factory=dict)
	event_elements: dict = Field(default_factory=dict)
	
	def is_goal(self, retriever: EventRetriever, max_events: int):
		event_count = len(self.events)

		if event_count >= max_events:
			return True
		
		if event_count > 0:
			last_event = self.events[-1]
			n_post_events = retriever.count_post_events(last_event)
			return n_post_events <= 0
		
		return False
	
	@staticmethod
	def _update_counted_elements(source: list[dict], target: dict[str, int]):
		element_map = {}
		for element in source:
			id = element["id"]
			count = element["count"]
			target[id] = max(count, target.get(id, 0))
			element_map[id] = count
		return element_map
	
	def add_event(self, event: str, retriever: EventRetriever):
		self.events.append(event)

		place_class = retriever.get_place_class(event)
		self.places.add(place_class)
		
		role_map = self._update_counted_elements(
			retriever.get_role_classes(event),
			self.roles
		)

		object_map = self._update_counted_elements(
			retriever.get_object_classes(event),
			self.objects
		)

		self.event_elements[event] = {
			"place": place_class,
			"object": object_map,
			"roles": role_map
		}

	def clone(self, parent: Node, g: float):
		return Node(
			events=list(self.events),
			places=set(self.places),
			objects=dict(self.objects),
			roles=dict(self.roles),
			event_elements=copy.deepcopy(self.event_elements),
			parent=parent,
			g=g,
		)
	
	def get_event_names(self):
		return [event.split("/")[-1] for event in self.events]