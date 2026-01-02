from pydantic import BaseModel, Field
from common.models.agent import Agent, Relationship
from common.models.place import Place
from common.models.object import Object
from common.models.event import Event
from enum import StrEnum

class GenreClass(StrEnum):
	'''Enumeration of common genres of folktales, classified by typical themes, characters and narrative conventions.'''
	FABLE = "fable"
	FAIRY_TALE = "fairy_tale"
	LEGEND = "legend"
	MYTH = "myth"
	TALL_TALE = "tall_tale"

class Genre(BaseModel):
	'''The genre classification of a foltkale, based on its theme, characters and narrative structure.'''
	genre: GenreClass = Field(..., description="The genre assigned to the folktale, chosen from a set of predefined categories.")

class AnnotatedFolktale(BaseModel):
	uri: str
	nation: str
	title: str
	has_genre: GenreClass
	
	agents: list[Agent] = Field(default_factory=list)
	relationships: list[Relationship] = Field(default_factory=list)
	places: list[Place] = Field(default_factory=list)
	objects: list[Object] = Field(default_factory=list)
	events: list[Event] = Field(default_factory=list)