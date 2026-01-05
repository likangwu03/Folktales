from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel
from collections import Counter
from typing import Optional, cast

from pydantic import BaseModel, Field, ConfigDict

class Response(BaseModel):
	'''Model output for a single-option classification task.'''

	model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
	
	thinking: str = Field(
		...,
		description=(
			"Brief justification explaining why the selected option best matches "
			"the input text. This field is for interpretability only."
		),
		examples=[
			"The text sets up the hero's normal life and environment before any conflict occurs.",
			"The antagonist performs harmful acts that create obstacles for the hero.",
			"The hero is forced out of a safe place due to circumstances beyond their control.",
			"There is a direct confrontation involving physical combat."
		],
		min_length=1 # No permite strings vacíos
	)

	response: int = Field(
		...,
		description=(
			"Zero-based index of the selected option from the provided list. "
			"The value must correspond to exactly one available option."
		),
		examples=[0, 2, 5],
		ge=0  # Mayor o igual que 0
	)

system_prompt = SystemMessagePromptTemplate.from_template(template="""You are an expert narrative analysis assistant. Your task is to classify a text fragment by selecting the most specific narrative event from a closed list of options.

Instructions:
- Select exactly ONE option from the list.
- Each option is identified by its index number (0, 1, 2, ...).
- The value returned in "response" MUST be a valid index within the bounds of the provided options list.
- Do NOT return an index that is negative or greater than or equal to the number of available options.
- Return ONLY the index number as an integer in "response".
- Do NOT invent options or return natural language in "response".
- If multiple options are applicable, select the one that is the most detailed and specific.
- Abstract or general options should only be chosen if no specific option applies.
Available options:
\"\"\"{options}\"\"\"

{previous_thought}
Output format:
{{
  "thinking": "Brief justification based on the text",
  "response": int
}}
""")

human_prompt = HumanMessagePromptTemplate.from_template(
	"""Text to classify:
\"\"\"{event}\"\"\""""
)

event_prompt = ChatPromptTemplate.from_messages([
	system_prompt,
	human_prompt,
])


def build_options_prompt(node: dict, self_name: Optional[str] = None) -> tuple[str, list]:
	options = []
	
	for child_id, info in node.get("children", {}).items():
		options.append((child_id, info["description"]))

	if self_name:
		options.append((self_name, node["description"]))

	lines = [
		f"{idx}. {node_id}: {description}" 
		for idx, (node_id, description) in enumerate(options)
	]

	return "\n".join(lines), options

def build_options_prompt_by_list(options: list) -> str:
	lines = [
		f"{idx}. {node_id}: {description}" 
		for idx, (node_id, description) in enumerate(options)
	]
	return "\n".join(lines)


def extract_event(model: BaseChatModel, folktale_event: str, options:str, previous_thought:str = "" ):
	event_chain = event_prompt | model.with_structured_output(Response)
	response = event_chain.invoke({
		"options": options,
		"event": folktale_event,
		"previous_thought": previous_thought
	})

	response = cast(Response, response)

	return response.response, response.thinking


def hierarchical_event_classification_with_desc(model: BaseChatModel, folktale_event: str, taxonomy_tree: dict, n_rounds: int = 3, verbose: bool = False):
	"""
	Clasifica un evento usando una taxonomía jerárquica con descripciones.

	Args:
		model: Instancia de BaseChatModel.
		folktale_event: Texto del evento a clasificar.
		taxonomy_tree: Diccionario de taxonomía con estructura {node: {"description": ..., "children": {...}}}.
		n_rounds: Número de veces a preguntar al LLM por cada nivel.

	Returns:
		Tuple[str, str]: (evento final elegido, justificación final)
	"""

	current_nodes = taxonomy_tree["event"]["children"]
	previous_event = None
	final_thinking = []
	options_str,options_list = build_options_prompt(taxonomy_tree["event"])
	level = 0
	final_thinking_str = ""
	# retry_count = 0

	if verbose:
		print("=== Inicio de clasificación jerárquica ===")
		print(f"Evento a clasificar: {folktale_event}")

	while current_nodes:
		votes = []
		thoughts = []

		if verbose:
			print(f"\n--- Nivel {level} ---")
			print("Opciones disponibles:")
			print(options_str)

		# Preguntar al LLM n_rounds veces
		for i in range(n_rounds):
			event, thinking = extract_event(
				model=model,
				folktale_event=folktale_event,
				options=options_str,
				previous_thought=final_thinking_str
			)
			if 0 <= event < len(options_list):
				votes.append(event)
				thoughts.append(thinking)

				if verbose:
					print(f"\nLlamada al modelo ({i + 1}/{n_rounds})")
					print(f"  Evento propuesto: {options_list[event]}")
					print(f"  Justificación: {thinking}")
			else:
				if verbose:
					print("OUT OF RANGE")
					print(f"\nLlamada al modelo ({i + 1}/{n_rounds})")
					print(f"  Evento propuesto: {options_list[event]}")
					print(f"  Justificación: {thinking}")

		if not votes:
			return previous_event, final_thinking

		if verbose: print("\n---\n")

		# Voto por mayoría
		vote_count = Counter(votes)
		max_freq = max(vote_count.values())
		most_frequent = [v for v, c in vote_count.items() if c == max_freq]

		winning_event = most_frequent[0]
		# winning_event, _ = vote_count.most_common(1)[0]

		if len(most_frequent)>1:
			selected = [options_list[i] for i in most_frequent]
			selected_str = build_options_prompt_by_list(selected)
			event, thinking = extract_event(
				model=model,
				folktale_event=folktale_event,
				options=selected_str,
				previous_thought=final_thinking_str
			)
			winning_event = most_frequent[event]

			if verbose:
				print(f" Empate:")
				print(selected_str)
				print(f"  Evento propuesto: {selected[event]}")
				print(f"  Justificación: {thinking}")

		final_thinking.extend(
			thoughts[i] for i, v in enumerate(votes) if v == winning_event
		)
		
		winning_event = options_list[winning_event][0]

		if verbose:print(f"  Evento propuesto: {winning_event}")

		# Si el evento se repite o no tiene hijos
		if winning_event == previous_event:
			if verbose:
				print("Evento repetido. Finalizando clasificación.")
			return winning_event, final_thinking

		if not current_nodes[winning_event]["children"]:
			if verbose:
				print("El evento ganador no tiene hijos. Finalizando clasificación.")
			return winning_event, final_thinking
		

		options_str,options_list = build_options_prompt(current_nodes[winning_event],winning_event)

		current_nodes = current_nodes[winning_event]["children"]
		previous_event = winning_event

		final_thinking_str = "Previous decision or reasoning to consider:\n" + "\n".join(final_thinking)

		if verbose:print(f"Descendiendo a los hijos de: {winning_event}")
		level+=1

	if verbose:
		print("\n=== Fin de clasificación ===")
		print(f"  Evento propuesto: {previous_event}")
		print(f"  Justificación: {final_thinking}")

	return previous_event, final_thinking

