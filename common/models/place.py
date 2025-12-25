from typing import Literal, Annotated
from pydantic import Field, BaseModel, ConfigDict
from common.regex_utils import snake_case_regex

PlaceClass = Annotated[Literal["mountain", "forest", "river", "field", "castle", "palace", "house", "hut", "farmhouse", "tower", "shop", "school", "tavern", "village", "town", "city", "kingdom"], 
					   Field(..., description="The category of place this instant represents. Must be one of the predifined types.")]

class Place(BaseModel):
	'''A location that appears within the folktale.'''
	
	model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

	class_name: PlaceClass
	
	instance_name: str = Field(
		...,
		description= "An specified identifier for the place, written in snake case. It must provide a clear, descriptive name for the location instance.",
		examples=["hero_house", "royal_ballroom", "race_track", "straw_house", "stick_house", "brick_house", "near_forest"],
		pattern=snake_case_regex)
	
MAX_PLACES = 5
	
class Places(BaseModel):
	"A collection of locations that appear within the folktale."
	places: list[Place] = Field(
		...,
		description="A list of all locations explicitly mentioned in the folktale.",
		max_length=MAX_PLACES
	)