from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from common.models.place import Places, MAX_PLACES
from langchain_core.language_models.chat_models import BaseChatModel
from loguru import logger

places_prompt = ChatPromptTemplate.from_messages(
	[
		SystemMessagePromptTemplate.from_template(template='''You are an AI that extracts locations from a folktale. Your task is to analyze the folktale and identify the locations that appear in it. Each location must include:
- a category choose strictly from the taxonomy below
- an instance, which you create to describe the specific place in the story
                
TAXONOMY (choose the most specific applicable category):

- natural_place: a geographic or environmental area that exists in nature without being constructed.
    - mountain: a large natural elevation of the earth’s surface.
    - forest: a large area covered mainly by trees.
    - field: a wide, open area of grass and crops.
- building: a structure built by people.
    - dwelling: a place where someone could live or stay.
        - castle: a fortified, large residence, typically for royalty or nobility.
    	- palace: a large and luxurious house belonging to royalty or high-ranking figures.
        - house: a typical residential building for a family or individual.
        - hut: a very small, simple dwelling, often made of natural materials like wood, straw, or mud.
        - farmhouse: a house associated with agricultural life, usually rural.
        - tower
	- community_building: buildings for work, trade, education, or public gatherings.
        - shop: a place where goods are sold.
        - school: a building where teaching and learning happen.
        - tavern: a place where travelers rest, eat or drink.
- settlement: a community where groups of people live.
    - village: a small settlement, usually rural, with few buildings and population.
    - town: a settlement larger than a village, with more buildings and services.
    - city: a large, densely populated settlement with many buildings, districts, and institutions.
    - kingdom: a territory ruled by a kingdom or a queen.
                
GUIDELINES:
- Include only locations explicitly mentioned in the story, ignore generic or irrelevant places.
- Select the most specific category from the taxonomy.
- Provide a concise, story-appropriate name for each instance.
- Do not invent locations, use only the places described in the story.
- List each place only once.
- Identify the minimal set of places needed to represent the story accurately, with a maximum of {max_places}.'''),

		HumanMessagePromptTemplate.from_template(template='''Generate a list of the places that appear in the folktale presented below. For each place, select the most specific category from the taxonomy and create an appropriate instance name.
                                           
Folktale:
{folktale}''')
	]
)

def extract_places(model: BaseChatModel, folktale: str):
    places_chain = places_prompt | model.with_structured_output(Places)
    places = places_chain.invoke({"folktale": folktale,
                                  "max_places": MAX_PLACES})
    
    logger.debug(f"Places: {places}")

    # print(places_prompt.format(folktale=folktale, max_places=MAX_PLACES))

    return places