# class Folktale(BaseModel):
# 	model_config = ConfigDict(str_strip_whitespace=True)

# 	has_genre: Literal["fable", "fairy_tale", "legend", "myth", "tall_tale"]
# 	agents: List[Agent]
# 	places: List[Place]
# 	objects: List[Object]
# 	events: List[Event]

# 	@model_validator(mode='after')
# 	def check_folktale(self) -> Self:
# 		# for i, agent in enumerate(self.agents):	
# 			# agent.relationships = pad_or_truncate(agent.relationships, len(self.agents), "none")
# 			# agent.relationships[i] = "none"

# 		for i, agent in enumerate(self.agents):
# 			if agent.lives_in >= len(self.places):
# 				raise ValueError(f"In agents: {agent.instance_name}. lives_in: {agent.lives_in} is out of bounds and must be a lower number. The places that exist are:\n{"\n".join(f"- Place {i+1}: {place.instance_name}" for i, place in enumerate(self.places))}")
			
			
# 		for event in self.events:
# 			for agentIndex in event.has_agent:
# 				if agentIndex >= len(self.agents):
# 					raise ValueError(f"In events: {event.instance_name}. has_agent: {agentIndex} is out of bounds and must be a lower number. The agents that exist are:\n{"\n".join(f"- Agent {i+1}: {agent.instance_name}" for i, agent in enumerate(self.agents))}")
				
# 			for objectIndex in event.has_object:
# 				if objectIndex >= len(self.objects):
# 					raise ValueError(f"In events: {event.instance_name}. has_object: {objectIndex} is out of bounds and must be a lower number. The objects that exist are:\n{"\n".join(f"- Object {i+1}: {object.instance_name}" for i, object in enumerate(self.objects))}")

# 		return self

from pydantic import BaseModel
from typing import Literal
from annotation.models.agent import Agent
from annotation.models.place import Place
from annotation.models.object import Object
from annotation.models.event import Event

Genre = Literal["fable", "fairy_tale", "legend", "myth", "tall_tale"] 

class AnnotatedFolktale(BaseModel):
	uri: str
	nation: str
	title: str
	has_genre: Genre
	
	agents: list[Agent]
	places: list[Place]
	objects: list[Object]
	events: list[Event]