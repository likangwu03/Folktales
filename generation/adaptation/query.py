from pydantic import BaseModel, Field, field_validator
from common.models.folktale import GenreClass
from common.models.event import EventClass
from common.models.role import RoleClass
from common.models.place import PlaceClass
from common.models.object import ObjectClass
from common.utils.regex_utils import snake_case_to_pascal_case

class Query(BaseModel):
	title: str
	initial_event: EventClass
	genre: GenreClass
	events: list[EventClass]
	roles: list[RoleClass]
	places: list[PlaceClass]
	objects: list[ObjectClass]
	max_events: int

	@field_validator("*", mode="after")
	@classmethod
	def postprocess_all_strings(cls, value):
		if isinstance(value, str):
			return snake_case_to_pascal_case(value)
		elif isinstance(value, list) and all(isinstance(v, str) for v in value):
			return [snake_case_to_pascal_case(v) for v in value]
		return value
