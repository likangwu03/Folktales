from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class EvaluatorNode(BaseModel):
	id: str
	description: str
	parent: Optional[EvaluatorNode] = None
	children: list[EvaluatorNode] = Field(default_factory=list)
	thoughts: list[str] = Field(default_factory=list)