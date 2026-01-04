from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel
from pydantic import BaseModel, Field, ConfigDict

class EventInstanceName(BaseModel):
    """
    Model output for generating a generic snake_case narrative event identifier.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    instance_name: str = Field(
        ...,
        description=(
            "Generic narrative event identifier in snake_case. "
            "Must correspond to the event type and contain no story-specific details."
        ),
        examples=[
            "antagonist_rushes_to_finish_line",
            "hero_passing_antagonist",
            "loss_of_safe_space",
            "magical_helper_grants_wish",
            "hero_works_hard"
        ],
        min_length=1
    )

system_prompt = SystemMessagePromptTemplate.from_template(
    template="""You are an expert narrative annotation assistant.
Your task is to generate a GENERIC instance name for a narrative event.

You will be given:
- The event type
- The event text
- A brief reasoning explaining why this is that event type

Instructions:
- Output ONLY a generic instance name.
- Do NOT include specific characters, places, objects, or story-specific details.
- The name must be abstract and reusable.
- Use snake_case.
- Do NOT repeat or summarize the input fields.
- Do NOT output explanations or additional fields.

Output format:
{{
  "instance_name": "generic_event_name"
}}
"""
)
human_prompt = HumanMessagePromptTemplate.from_template(
    """Event type:
{event_type}

Event text:
\"\"\"{event_text}\"\"\"

Reasoning:
{thinking}
"""
)

event_instance_prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    human_prompt,
])

def extract_event_instance_Name(model: BaseChatModel, event_type: str, event_text:str, thinking:str = "" ):
	event_chain = event_instance_prompt | model.with_structured_output(EventInstanceName)
	response = event_chain.invoke({
		"event_type": event_type,
		"event_text": event_text,
		"thinking": thinking
	})
	return response.instance_name