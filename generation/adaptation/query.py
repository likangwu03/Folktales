from pydantic import BaseModel

class Query(BaseModel):
	initial_event_type: str