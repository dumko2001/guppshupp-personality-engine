"""
Pydantic models for personality profiles and response generation.
"""
from pydantic import BaseModel, Field
from typing import Literal


class PersonalityProfile(BaseModel):
    """Configuration for a personality type."""
    id: str
    name: str
    description: str
    system_prompt: str
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    formality_level: int = Field(default=5, ge=1, le=10)
    humor_level: int = Field(default=5, ge=1, le=10)
    empathy_level: int = Field(default=5, ge=1, le=10)


class PersonalityResponse(BaseModel):
    """Response generated with a specific personality."""
    personality_id: str
    personality_name: str
    response: str


class ComparisonResult(BaseModel):
    """Before/after comparison of responses."""
    query: str
    without_memory: str
    with_memory: dict[str, PersonalityResponse]
