"""
Pydantic models for user memory extraction with confidence scoring and source attribution.
"""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime, timezone


class Preference(BaseModel):
    """A user preference extracted from conversation history."""
    category: Literal["communication", "interests", "lifestyle", "values"]
    description: str = Field(..., description="What the user prefers")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="1.0=explicit statement, 0.7-0.9=strongly inferred, <0.7=weak signal"
    )
    source_message_ids: list[int] = Field(
        ..., 
        description="Message indices supporting this preference"
    )
    evidence: str = Field(..., description="Quote or paraphrase from messages")


class PreferenceList(BaseModel):
    """Wrapper for LLM extraction response."""
    preferences: list[Preference]


class EmotionalPattern(BaseModel):
    """A recurring emotional pattern observed in user messages."""
    pattern: str = Field(..., description="e.g., 'becomes anxious about deadlines'")
    triggers: list[str] = Field(..., description="What causes this emotional state")
    frequency: Literal["rare", "occasional", "frequent"]
    emotional_range: list[str] = Field(
        ..., 
        description="Emotions observed: anxious, excited, stressed, etc."
    )
    source_message_ids: list[int]


class EmotionalPatternList(BaseModel):
    """Wrapper for LLM extraction response."""
    emotional_patterns: list[EmotionalPattern]


class Fact(BaseModel):
    """A factual piece of information about the user."""
    category: Literal["personal", "professional", "relational", "temporal"]
    fact: str = Field(..., description="The factual information")
    importance: Literal["low", "medium", "high"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_message_ids: list[int]


class FactList(BaseModel):
    """Wrapper for LLM extraction response."""
    facts: list[Fact]


class UserMemory(BaseModel):
    """Complete extracted memory profile of a user."""
    preferences: list[Preference] = Field(default_factory=list)
    emotional_patterns: list[EmotionalPattern] = Field(default_factory=list)
    facts: list[Fact] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    extraction_errors: list[str] = Field(default_factory=list)
