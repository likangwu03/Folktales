from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from annotation.evaluator.tree import EvaluatorTree
from common.loader import load_folktales, load_json_folder
from annotation.tools.place_extractor import extract_places
from annotation.tools.agent_extractor import extract_agents
from annotation.tools.genre_extractor import extract_genre
from annotation.tools.event_extractor import extract_events
from annotation.tools.relationship_extractor import extract_relationships
from common.models.folktale import AnnotatedFolktale
from annotation.utils import format_hierarchy
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

def main():
	load_dotenv()

	model = get_model(temperature=0.7,
					  remote=False)

	hierarchies = load_json_folder("hierarchies")
	# event_hierarchy = hierarchies["event"]

	# evaluator_tree = EvaluatorTree(event_hierarchy)
	# evaluator_tree.print()

	folktales = load_folktales()
	folktale = folktales.iloc[0]
	momotaro = folktale["text"]

	examples = load_json_folder("examples/annotated")
	agents_example = examples["cinderella"]["agents"]

	place_hierarchy = hierarchies["place"]
	role_hierarchy = hierarchies["role"]

	# genre = extract_genre(model, momotaro)

	places = extract_places(model, momotaro, place_hierarchy)

	agents = extract_agents(model, momotaro, agents_example, places, role_hierarchy)

	relationships = extract_relationships(model, momotaro, agents)

	# events = extract_events(model, momotaro)

	# for event in events:
	# 	pass

	# uri = folktale["source"].rstrip('/')

	# folktale = AnnotatedFolktale(
	#     uri=uri,
	#     nation=folktale["nation"],
	#     has_genre=genre,
	#     title=folktale["title"],
	#     agents=agents,
	# 	relationships=relationships
	#     places=places,
	# )

if __name__ == "__main__":
	main()