"""
Pydantic models for chat messages and conversation history.
"""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """A single chat message in the conversation."""
    role: Literal["user", "assistant"] = "user"
    content: str
    timestamp: datetime | None = None


class ConversationHistory(BaseModel):
    """Complete conversation history for memory extraction."""
    messages: list[ChatMessage]
    user_id: str | None = None
    session_id: str | None = None
