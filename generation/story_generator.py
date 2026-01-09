from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, FewShotChatMessagePromptTemplate
from loguru import logger
from common.models.folktale import AnnotatedFolktale
import json

def get_model(temperature: float) -> BaseChatModel:
	model = ChatGroq(
		model="llama-3.3-70b-versatile",
		temperature=temperature,
		timeout=5.0,
		max_retries=2
	)
	return model

human_prompt = HumanMessagePromptTemplate.from_template(template='''Using the following annotated folktale, create an original story in natural language that follows the same narrative structure. Pay close attention to how the events unfold to maintain consistency with the original structure.

Annotated folktale:
{folktale}
''')

example_prompt = ChatPromptTemplate.from_messages(
	[
		human_prompt,
		("ai", "{output}"),
	]
)

system_prompt = SystemMessagePromptTemplate.from_template(template='''You are an AI tasked with creating a unique and imaginative folktale in natural language based on a structured narrative.

Your goal is to create a compelling and original story that aligns with the providing outline. Ensure it features a clear beginning, middle and end. The story must flow naturally and be of moderate length, with enough detail to immerse the reader.
		  
Focus on the sequence of events that guide the plot, ensuring each event include the appropriate characters, places and objects. Make sure that each part of the story unfolds according to the narrative structure.
														  
The structured narrative is provided in JSON format below. It includes the following components:
														  
{{
    "has_genre": "Specifies the literary the genre of the folktale, such as fairy tale, myth or legend.",
    "nation": "Indicates the cultural origin of the folktale.",
    "title": "The name of the folktale.",
    "relationships": "A matrix of connections between characters. Each entry represents the relationship between two characters, references by their indices in the character array.",
    "agents": "An array listing the characters involved in the story, including details about each character such as their age, gender, personality traits, their place of residence, their name and their role in the narrative according to Prpp's 5 spheres of action).",
    "places": "An array representing the locations involved in the story, which each entry containing an identifier (instance_name) and a classification (class_name) that explains the nature of the place.",
    "objects": "An array listing significant objects that are crucial to the plot's progression. Each object has an identifier (instance_name) and a classification (class_name).",
    "events": "A chronological series of events that form the narrative of the story. Each event is classified by one of the 31 functions in Propp's narrative structure (class_name). Additionally, each event includes lists with characteres, places and objects involved, referenced by their indices in their corresponding arrays."
}}
''')

def generate_story(folktale: AnnotatedFolktale, examples: list[tuple[AnnotatedFolktale, str]]):
	model = get_model(0.9)

	few_shot_examples = []
	for example in examples:
		example_json = example[0].model_dump(mode="json")
		example_json = json.dumps(example_json, indent=4)

		few_shot_example = {
			"folktale": example_json,
			"output": example[1]
		}
		few_shot_examples.append(few_shot_example)
	
	few_shot_prompt = FewShotChatMessagePromptTemplate(
		example_prompt=example_prompt,
		examples=few_shot_examples,
	)

	story_prompt = ChatPromptTemplate.from_messages(
		[
			system_prompt,	
			few_shot_prompt,
			human_prompt
		]
	)

	story_chain = story_prompt | model

	folktale_json = folktale.model_dump(mode="json")
	folktale_json = json.dumps(folktale_json, indent=4)

	# print(story_prompt.format(folktale=folktale_json))

	ai_message = story_chain.invoke({
		"folktale": folktale_json
	})

	story = folktale.title + "\n" + ai_message.content.strip()

	logger.debug(f"Folktale:\n{story}")

	return story