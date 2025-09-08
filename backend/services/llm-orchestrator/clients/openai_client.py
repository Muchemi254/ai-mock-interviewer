# backend/services/llm-orchestrator/clients/openai_chat_client.py
"""Dedicated client for OpenAI chat interactions with session management."""

import os
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import openai
from openai import OpenAI, AsyncOpenAI

from app.chat_models import ChatMessage, ChatSession, MessageRole

import logging
logger = logging.getLogger(__name__)

class OpenAIChatClient:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI chat client.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        # Use AsyncOpenAI for FastAPI async compatibility
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(self, session_id: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Create a new chat session."""
        if session_id is None:
            session_id = str(uuid.uuid4())

        session = ChatSession(session_id=session_id)

        if system_prompt:
            system_message = ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
            session.messages.append(system_message)

        self.sessions[session_id] = session
        logger.info(f"Created new OpenAI chat session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted OpenAI chat session: {session_id}")
            return True
        return False

    def list_sessions(self) -> List[Dict]:
        """List all chat sessions with summary info."""
        sessions_info = []
        for session_id, session in self.sessions.items():
            user_messages = [msg for msg in session.messages if msg.role == MessageRole.USER]
            sessions_info.append({
                "session_id": session_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages),
                "user_message_count": len(user_messages),
                # Avoid sending too much data; truncate last message
                "last_message_preview": (session.messages[-1].content[:50] + "...") if session.messages else None
            })
        return sessions_info

    def add_message_to_session(self, session_id: str, role: MessageRole, content: str) -> bool:
        """Add a message to a session."""
        session = self.get_session(session_id)
        if not session:
            return False

        message = ChatMessage(role=role, content=content)
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        return True

    def get_session_messages_for_api(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get all messages from a session in the format expected by the OpenAI API.
        """
        session = self.get_session(session_id)
        if not session:
            return []

        # Ensure role is a string value as expected by OpenAI
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in session.messages
        ]

    async def chat_completion(
        self,
        session_id: str,
        user_message: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs
    ) -> Tuple[str, str, int]:
        """
        Send a chat completion request to OpenAI and update session.

        Returns:
            Tuple of (assistant_response_text, session_id_used, total_message_count_in_session)
        """
        # Ensure session exists
        if session_id not in self.sessions:
            # This shouldn't happen if called from the route correctly, but be safe
            self.create_session(session_id)

        # Add user message to session
        self.add_message_to_session(session_id, MessageRole.USER, user_message)

        # Get all messages for context (in OpenAI format)
        messages_for_api = self.get_session_messages_for_api(session_id)

        try:
            logger.debug(f"Calling OpenAI model '{model}' for session {session_id}")
            # Call OpenAI API asynchronously
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs # Allow passing other OpenAI parameters
            )

            # Extract assistant's response
            assistant_message_content = response.choices[0].message.content.strip()

            # Add assistant's response to session
            self.add_message_to_session(session_id, MessageRole.ASSISTANT, assistant_message_content)
            logger.debug(f"Received response for session {session_id}")

            session = self.get_session(session_id)
            message_count = len(session.messages) if session else 0

            return assistant_message_content, session_id, message_count

        except openai.APIError as e:
            logger.error(f"OpenAI API error for session {session_id}: {e}")
            raise # Re-raise for the route to handle
        except Exception as e:
            logger.error(f"Unexpected error during OpenAI call for session {session_id}: {e}", exc_info=True)
            raise

    def get_session_context(self, session_id: str) -> Optional[Dict]:
        """Get session context with metadata."""
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in session.messages
            ]
        }

    def clear_session_messages(self, session_id: str, keep_system: bool = True) -> bool:
        """Clear messages from a session, optionally keeping system messages."""
        session = self.get_session(session_id)
        if not session:
            return False

        if keep_system:
            session.messages = [
                msg for msg in session.messages
                if msg.role == MessageRole.SYSTEM
            ]
        else:
            session.messages = []

        session.updated_at = datetime.utcnow()
        return True

openai_client: Optional['OpenAIChatClient'] = None
