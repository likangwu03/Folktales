from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from common.regex_utils import snake_case_regex

EventClass = Literal[
	"setup", 
	"initial_situation", 
	"hero_interdiction", 
	"villainy", 
	"false_matrimony", 
	"expulsion", 
	"kidnapping", 
	"murder", 
	"lack", 
	"lack_of_bride", 
	"lack_of_money", 
	"hero_departure", 
	"struggle", 
	"fight", 
	"branding", 
	"receive_mark", 
	"receive_injury", 
	"connective_incident", 
	"call_for_help", 
	"departure_decision", 
	"villain_gains_information", 
	"conflict", 
	"absentation", 
	"breaking_interdiction", 
	"acquisition", 
	"get_present", 
	"guidance", 
	"return", 
	"make_contact_with_enemy", 
	"mediation", 
	"trickery", 
	"beginning_of_counteraction", 
	"helper_move", 
	"receipt_object", 
	"liquidation_of_lack", 
	"release_from_captivity", 
	"pursuit_and_rescue", 
	"false_hero_make_unfounded_claim", 
	"attempt_at_reconnaissance", 
	"victory", 
	"villain_defeated", 
	"unrecognised_arrival", 
	"home_arrival", 
	"difficult_task_with_solution", 
	"difficult_task", 
	"solution_difficult_task", 
	"recognition", 
	"punishment", 
	"reward", 
	"exposure_of_villain", 
	"transfiguration", 
	"physical_transformation", 
	"psychological_transformation", 
	"wedding_or_throne", 
	"wedding", 
	"get_throne"
]

class Event(BaseModel):
	model_config = ConfigDict(str_strip_whitespace=True)

	class_name: EventClass
	instance_name: str = Field(..., pattern=snake_case_regex)

	has_agent: list[int] = Field(default_factory=list)
	has_object: list[int] = Field(default_factory=list)

MIN_EVENTS = 5
MAX_EVENTS = 15

class StorySegments(BaseModel):
	'''A collection representing the individual segments into which the story is divided.'''
	segments: list[str] = Field(
		..., 
		description="A list of textual segments, each representing a distinct event or part of the story.",
		max_length=MAX_EVENTS)