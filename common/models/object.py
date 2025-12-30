from pydantic import Field, BaseModel, ConfigDict
from common.regex_utils import snake_case_regex
from enum import StrEnum

class ObjectClass(StrEnum):
	# Animate objects
	ANIMATE_OBJECT = "animate_object"
	NON_ANTHROPOMORPHIC_ANIMAL = "non_anthropomorphic_animal"
	
	# Inanimate objects
	INANIMATE_OBJECT = "inanimate_object"
	MAGICAL_OBJECT = "magical_object"
	NATURAL_OBJECT = "natural_object"
	CRAFTED_OBJECT = "crafted_object"

class Object(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
	
	class_name: ObjectClass
	instance_name: str = Field(..., pattern=snake_case_regex)