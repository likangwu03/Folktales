from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from annotation.evaluator.tree import EvaluatorTree
from common.models.event import EventElements, EventMetadata, EventExample, Event, EventClass
from common.utils.loader import load_folktale_csv, load_json_folder, save_annotated_folktale, data_dir, out_dir
from annotation.tools.place_extractor import extract_places
from annotation.tools.agent_extractor import extract_agents
from annotation.tools.genre_extractor import extract_genre
from annotation.tools.event_extractor import extract_story_segments, extract_event_elements
from annotation.tools.event_classifier import hierarchical_event_classification_with_desc
from annotation.tools.event_instance_name import extract_event_instance_name
from annotation.tools.object_extractor import extract_objects
from annotation.tools.relationship_extractor import extract_relationships
from common.models.folktale import AnnotatedFolktale
from pandas import DataFrame
from annotation.visualization import show_genre_distribution
from loguru import logger
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

def get_folktales_by_count(folktales_df: DataFrame, start_index: int, n_folktales: int):
	n_folktales_df = len(folktales_df)
	end_index = min(start_index + n_folktales, n_folktales_df)

	selected_folktales_df = folktales_df.iloc[start_index:end_index]

	return selected_folktales_df

def display_genre_distribution(enabled: bool=False):
	if enabled:
		folktales_json = load_json_folder(f"{out_dir}/annotated")
		folktales = [AnnotatedFolktale(**folktale_json) for folktale_json in folktales_json.values()]
		show_genre_distribution(folktales)

def main():
	load_dotenv()

	model = get_model(temperature=0.4,
					  remote=False)

	hierarchies = load_json_folder(f"{data_dir}/hierarchies")

	examples = load_json_folder(f"{data_dir}/examples/annotated")
	cinderella = AnnotatedFolktale(**examples["cinderella"])

	event_examples = []
	cinderella_hero_works_hard = get_event_example(cinderella, 0)
	event_examples.append(cinderella_hero_works_hard)	

	event_hierarchy = hierarchies["event_with_descriptions"]

	folktales_df = load_folktale_csv()
	selected_folktales_df = get_folktales_by_count(folktales_df, 0, 2)

	for _, row in selected_folktales_df.iterrows():
		text = row["text"]
		uri = row["source"].rstrip('/')
		nation = row["nation"].lower()
		title = row["title"]

		logger.info(f"Annotating '{title}'...")

		place_hierarchy = hierarchies["place"]
		role_hierarchy = hierarchies["role"]
		object_hierarchy = hierarchies["object"]

		genre = extract_genre(model, text)

		objects = extract_objects(model, text, object_hierarchy)

		places = extract_places(model, text, place_hierarchy)

		agents = extract_agents(model, text, cinderella.agents, places, role_hierarchy)

		relationships = extract_relationships(model, text, agents)

		story_segments = extract_story_segments(model, text)

		events = []
		for segment in story_segments:
			event_metada = EventMetadata(
				title=title,
				agents=agents,
				objects=objects,
				places=places,
				story_segment=segment
			)

			elements = extract_event_elements(model, event_metada, event_examples)

			# Evaluator tree
			event_type, thinking = hierarchical_event_classification_with_desc(model=model,folktale_event=segment,taxonomy_tree=event_hierarchy,n_rounds=3, verbose = False)
			if event_type is None:
				event_type = "move" #TODO
			instance_name = extract_event_instance_name(model,event_type,segment,"\n".join(thinking))

			
			event = Event(
				class_name=EventClass(event_type),
				instance_name=instance_name,
				description=segment,
				agents=elements.agents,
				objects=elements.objects,
				place=elements.place
			)

			events.append(event)

		folktale = AnnotatedFolktale(
			uri=uri,
			nation=nation,
			has_genre=genre,
			title=title,
			relationships=relationships,
			agents=agents,
			places=places,
			objects=objects,
			events=events
		)

		save_annotated_folktale(folktale, folktale.title)

	display_genre_distribution(True)

if __name__ == "__main__":
	main()