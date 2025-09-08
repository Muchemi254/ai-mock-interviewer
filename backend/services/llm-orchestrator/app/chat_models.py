# backend/services/llm-orchestrator/app/chat_models.py
"""Pydantic models specifically for the chat-based LLM interaction."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str # The new user message
    session_id: Optional[str] = None # If None, a new session is created
    system_prompt: Optional[str] = None # System prompt for new sessions
    model: str = "gpt-3.5-turbo" # Specify the OpenAI model
    max_tokens: Optional[int] = Field(default=150, ge=1, le=4000) # Model-specific limit check
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    response: str # The AI's response
    session_id: str # The ID of the session used/created
    message_count: int # Total messages in the session after this interaction
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict) # For future use


class SessionContextResponse(BaseModel):
    """Model for returning full session context."""
    session_id: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    messages: List[Dict[str, Any]] # List of message dicts with role, content, timestamp


class SessionListResponse(BaseModel):
    sessions: List[Dict[str, Any]] # Summary info for each session
    total_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
