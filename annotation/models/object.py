from typing import Literal
from pydantic import Field, BaseModel, ConfigDict
from common.regex_utils import snake_case_regex

ObjectClass = Literal["non_anthropomorphic_animal", "magical_object", "natural_object", "crafted_object"]

class Object(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
	
	class_name: ObjectClass
	instance_name: str = Field(..., pattern=snake_case_regex)