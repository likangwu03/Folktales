from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from generation.ontology.event_retriever import EventRetriever

class Node(BaseModel):
	parent: Optional[Node] = None
	f: float = 0
	g: float = 0
	h: float = 0
	events: list[str] = Field(default_factory=list)
	
	def is_goal(self, retriever: EventRetriever, max_events: int):
		event_count = len(self.events)

		if event_count >= max_events:
			return True
		
		if event_count > 0:
			last_event = self.events[-1]
			n_post_events = retriever.count_post_events(last_event)
			return n_post_events <= 0
		
		return False
	
	def get_event_names(self):
		return [event.split("/")[-1] for event in self.events]