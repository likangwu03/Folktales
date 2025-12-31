from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from annotation.evaluator.tree import EvaluatorTree
from common.models.event import EventElements, EventMetadata, EventExample, Event, EventClass
from common.utils.loader import load_folktale_csv, load_json_folder, save_folktale, data_dir, out_dir
from annotation.tools.place_extractor import extract_places
from annotation.tools.agent_extractor import extract_agents
from annotation.tools.genre_extractor import extract_genre
from annotation.tools.event_extractor import extract_story_segments, extract_event_elements
from annotation.tools.object_extractor import extract_objects
from annotation.tools.relationship_extractor import extract_relationships
from common.models.folktale import AnnotatedFolktale
import os

def get_model(temperature: float, remote: bool=False) -> BaseChatModel:
	if remote:
		model = ChatGroq(
			# api_key=os.environ.get("GROQ_API_KEY"),
			model="llama-3.1-8b-instant",
			temperature=temperature,
			timeout=5.0,
			max_retries=2
		)
	else:
		model = ChatOllama(
			base_url=os.environ.get("OLLAMA_HOST"),
			model="llama3.1:8b",
			num_gpu=-1,
			validate_model_on_init=True,
			temperature=temperature
		)
	return model

def get_event_example(folktale: AnnotatedFolktale, event_index: int):
	n_events = len(folktale.events)

	if event_index < n_events:
		event = folktale.events[event_index]
		if event.description:
			example = EventExample(
				title=folktale.title,
				agents=folktale.agents,
				objects=folktale.objects,
				places=folktale.places,
				story_segment=event.description,
				output=EventElements(
					agents=event.agents,
					objects=event.objects,
					place=event.place
				)
			)
			return example
	return None

def main():
	load_dotenv()

	model = get_model(temperature=0.4,
					  remote=False)

	hierarchies = load_json_folder(f"{data_dir}/hierarchies")

	# event_hierarchy = hierarchies["event"]
	# evaluator_tree = EvaluatorTree(event_hierarchy)
	# evaluator_tree.print()

	folktales = load_folktale_csv()
	folktale = folktales.iloc[0]
	momotaro = folktale["text"]

	examples = load_json_folder(f"{data_dir}/examples/annotated")
	cinderella = AnnotatedFolktale(**examples["cinderella"])

	event_examples = []
	cinderella_hero_works_hard = get_event_example(cinderella, 0)
	event_examples.append(cinderella_hero_works_hard)	

	place_hierarchy = hierarchies["place"]
	role_hierarchy = hierarchies["role"]
	object_hierarchy = hierarchies["object"]

	genre = extract_genre(model, momotaro)

	objects = extract_objects(model, momotaro, object_hierarchy)

	places = extract_places(model, momotaro, place_hierarchy)

	agents = extract_agents(model, momotaro, cinderella.agents, places, role_hierarchy)

	relationships = extract_relationships(model, momotaro, agents)

	story_segments = extract_story_segments(model, momotaro)

	events = []
	for segment in story_segments:
		event_metada = EventMetadata(
			title=folktale["title"],
			agents=agents,
			objects=objects,
			places=places,
			story_segment=segment
		)

		elements = extract_event_elements(model, event_metada, event_examples)

		# Evaluator tree

		event = Event(
			class_name=EventClass.MOVE,
			instance_name="instance_name",
			description=segment,
			agents=elements.agents,
			objects=elements.objects,
			place=elements.place
		)

		events.append(event)

	uri = folktale["source"].rstrip('/')

	folktale = AnnotatedFolktale(
	    uri=uri,
	    nation=folktale["nation"],
	    has_genre=genre,
	    title=folktale["title"],
		relationships=relationships,
	    agents=agents,
	    places=places,
		objects=objects,
		events=events
	)

	save_folktale(folktale)

if __name__ == "__main__":
	main()