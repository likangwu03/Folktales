from typing import Literal, Optional
from models.role import Role
from pydantic import ConfigDict, Field, BaseModel
from common.regex_utils import name_regex

AgentClass = Literal["human_being", "anthropomorphic_animal", "magical_creature", "group_of_agents"]

class Agent(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
	
	class_name: Literal["human_being", "anthropomorphic_animal", "magical_creature", "group_of_agents"]
	instance_name = AgentClass
	
	age_category: Literal["children", "young", "adult", "senior"]
	gender: Literal["male", "female"]
	has_personality: list[Literal["sociable", "joy", "active", "assertive", "anxious", "depressive", "tense", "aggressive", "cold", "egotism", "impersonal", "impulsive"]]
	name: Optional[str] = Field(None, pattern=name_regex)
	
	has_role: Role
	lives_in: Optional[int] = None
	