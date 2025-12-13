from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from common.regex_utils import snake_case_regex

RoleClass = Literal["main_character", "hero", "antagonist" "villain", "false_hero", "helper", "magical_helper", "prisioner", "princess", "quest_giver", "hero_family"]

class Role(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    class_name = RoleClass
    instance_name: str = Field(..., pattern=snake_case_regex)