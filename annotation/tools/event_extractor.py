from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, FewShotChatMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage
from common.models.event import StorySegments, MAX_EVENTS, EventElements, EventMetadata, EventExample
from common.utils.format_utils import format_agents, format_objects, format_places
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic_core import ValidationError
from typing import cast
from loguru import logger
import json

event_prompt = ChatPromptTemplate.from_messages(
	[
		SystemMessagePromptTemplate.from_template(template='''You are an AI designed to break down a folktale into distinct parts, each corresponding to a different event or progression in the story. Your task is to carefully analyze the story, identify key events, and divide it into sections, while maintaining the integrity of the original content.

Each section must be SUMMARY of a major event or progression in the story. Do NOT add or omit essential details in the story, only divide and condense the original content into meaningful segments. Each segment must represent a complete event or progression, and when combined, all the segments must make up the full story without any loss of information.

The sections must follow a logical and sequential order. For instance, the first part should introduces an event, and each subsequent section should progress naturally from the previous one, maintaining a smooth narrative flow. Each part should be distinct but also contribute to the overall coherence and development of the story, ensuring that the progression of events feels continuous and well-structured.

Focus on the key elements within each section, explicitly naming the characters involved, the significant objects to the development of the event and the setting.
'''),

		HumanMessagePromptTemplate.from_template(template='''Given the following folktale, divide it into at most {max_events} parts, with each part is a summary of a key event or progression. Do not to omit or alter any information in any section.

Folktale:
{folktale}
''')
	]
)

def extract_story_segments(model: BaseChatModel, folktale: str):
	event_chain = event_prompt | model.with_structured_output(StorySegments)

	print(event_prompt.format(folktale=folktale,
						   	max_events=MAX_EVENTS))

	events = event_chain.invoke({"folktale": folktale,
							  	"max_events": MAX_EVENTS})

	events = cast(StorySegments, events)
	
	for i, event in enumerate(events.segments):
		logger.debug(f"Event {i+1}: {event}")

	return events.segments

human_prompt = HumanMessagePromptTemplate.from_template(template='''Given the following segment from the folktale **{title}** and the corresponding list of characters, objects and places in the entire story, select the most appropriate ones for this segment.

Characters (Agents):
{characters}

Objects:
{objects}

Locations (Places):
{places}

Story segment:
{story_segment}
										   
Your task is to identify:
1. Which characters (agents) are involved in this segment?
2. Which objects are relevant to this segment (if any)?
3. Which location does this event take place in?

Please return the index of the selected characters, objects and place from the lists provided above.
''')

example_prompt = ChatPromptTemplate.from_messages(
    [
        human_prompt,
        ("ai", "{output}"),
    ]
)

system_prompt = SystemMessagePromptTemplate.from_template(template='''You are an AI designed to extract narrative elements from a segment of a folktale. Your task is to identify the characters, objects and location that are part of the segment provided.

For this task, you will be provided with:
- The full title of the folktale.
- A summary of the segment you should analyze to extract the elements.
- A complete list of possible characters, objects and places from the entire story.
											
Your job is to carefully analyze the segment and extract the correct elements based on the following instructions:
											
1. Characters (Agents):
	- Review the list of all characters in the story and identify the ones who are involved in this specific segment. There must be at least one character.
   
2. Objects:
   - Examine the list of all objects in the story and select the ones that are relevant to this segment. It’s possible that no object is mentioned in the event. If so, return an empty list.

3. Location (Place):
   - From the list of available locations, select the one where the segment occurs, based on the context.
											
Important Guidelines:
- Each element (character, object and location) can appear only once and should be represented by its index from the corresponding list.
- Be thorough in your analysis and ensure that you select only the relevant elements based on the context of the segment.
''')

def extract_event_elements(model: BaseChatModel, event: EventMetadata, examples: list[EventExample]):
	few_shot_examples = []

	for example in examples:
		output_json = example.output.model_dump(mode="json")
		output_json = json.dumps(output_json, indent=4)

		few_shot_example = {
			"title": example.title,
			"characters": format_agents(example.agents),
			"objects": format_objects(example.objects),
			"places": format_places(example.places),
			"story_segment": example.story_segment,
			"output": output_json
		}
		few_shot_examples.append(few_shot_example)
	
	few_shot_prompt = FewShotChatMessagePromptTemplate(
		example_prompt=example_prompt,
		examples=few_shot_examples,
	)

	elements_prompt = ChatPromptTemplate.from_messages(
		[
			system_prompt,	
			few_shot_prompt,
			human_prompt,
			MessagesPlaceholder(variable_name="messages")
		]
	)

	messages = []

	tools = [EventElements]
	elements_chain = elements_prompt | model.bind_tools(tools, tool_choice="any")
	# elements_chain = elements_prompt | model.with_structured_output(EventElements)

	formatted_agents = format_agents(event.agents)
	formatted_objects = format_objects(event.objects)
	formatted_places = format_places(event.places)

	done = False
	while not done:
		# logger.info(elements_prompt.format(story_segment=event.story_segment,
		# 									places=formatted_places,
		# 									objects=formatted_objects,
		# 									characters=formatted_agents,
		# 									title=event.title,
		# 									messages=messages))

		ai_message = elements_chain.invoke({
			"story_segment": event.story_segment,
			"places": formatted_places,
			"objects": formatted_objects,
			"characters": formatted_agents,
			"title": event.title,
			"messages": messages
		})

		print(ai_message)

		messages.append(ai_message)

		done = True

		try:
			args = ai_message.tool_calls[0]["args"]
			elements = EventElements.model_validate(args)
		except ValidationError as e:
			error_message = str(e)
			content = f"Validation error: {error_message}"
			done = False

		logger.debug(f"Event: {event.story_segment}\nElements: {args}")
		if done:
			content = elements.validate_indices(event.agents, event.objects, event.places)
			done = not bool(content)

		if not done:
			tool_message = ToolMessage(
				content=content,
				tool_call_id=ai_message.tool_calls[0]["id"]
			)
			messages.append(tool_message)
			logger.error(content)

	logger.debug(f"Event: {event.story_segment}\nFinal elements: {elements}")

	return elements