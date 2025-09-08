# backend/services/llm-orchestrator/routes/openai_chat.py
"""API routes for OpenAI chat interactions with session context."""

from fastapi import APIRouter, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from clients.openai_client import OpenAIChatClient
from app.chat_models import (
    ChatRequest, ChatResponse, SessionContextResponse,
    SessionListResponse, ErrorResponse
)

router = APIRouter(prefix="/chat/openai") # Explicit prefix for OpenAI chat
logger = logging.getLogger(__name__)

# Assuming the client is initialized in main.py and passed here,
# or we get it from a common place. For simplicity, let's assume it's initialized here
# but in a full app, dependency injection (e.g., via FastAPI Depends) is better.
# We'll initialize it in main.py and make it available.
# For now, we'll use a global-like approach within the module scope.
openai_chat_client: OpenAIChatClient = None # Will be set by main.py

def get_openai_chat_client():
    """Dependency to get the initialized OpenAI chat client."""
    global openai_chat_client
    if openai_chat_client is None:
        logger.error("OpenAIChatClient not initialized.")
        raise HTTPException(status_code=503, detail="OpenAI chat client not initialized.")
    return openai_chat_client


# --- API Endpoints ---

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK, tags=["LLM Chat"])
async def chat_with_openai(request: ChatRequest):
    """
    Send a message to an OpenAI model within a session context.
    If no session_id is provided, a new session is created.
    The conversation history is maintained within the session.
    """
    client = get_openai_chat_client()
    logger.info(f"Received chat request for model: {request.model}")

    try:
        # Handle session creation/joining
        session_id_to_use = request.session_id
        if not session_id_to_use:
            session_id_to_use = client.create_session(system_prompt=request.system_prompt)
            logger.debug(f"Created new session: {session_id_to_use}")
        elif not client.get_session(session_id_to_use):
            # Session ID provided but doesn't exist, create it
            client.create_session(session_id_to_use, request.system_prompt)
            logger.debug(f"Joined and initialized session: {session_id_to_use}")

        # Perform the chat completion
        response_text, session_id_used, message_count = await client.chat_completion(
            session_id=session_id_to_use,
            user_message=request.message,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        logger.info(f"Successfully generated response for session: {session_id_used}")
        return ChatResponse(
            response=response_text,
            session_id=session_id_used,
            message_count=message_count
        )

    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail=f"Error communicating with OpenAI: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.get("/{session_id}", response_model=SessionContextResponse, tags=["LLM Chat"])
async def get_openai_chat_session(
    session_id: str = Path(..., description="Session ID to retrieve")
):
    """Get the full conversation history for an OpenAI chat session."""
    client = get_openai_chat_client()
    context = client.get_session_context(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    return context


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["LLM Chat"])
async def delete_openai_chat_session(
    session_id: str = Path(..., description="Session ID to delete")
):
    """Delete an OpenAI chat session and all its messages."""
    client = get_openai_chat_client()
    success = client.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    # 204 No Content is implicit for successful delete with no return body


# Optional endpoints can be added similarly:
# @router.post("/{session_id}/clear", tags=["LLM Chat"])
# async def clear_openai_session_messages(...)

# @router.get("/sessions", response_model=SessionListResponse, tags=["LLM Chat"])
# async def list_openai_chat_sessions():
#     client = get_openai_chat_client()
#     sessions = client.list_sessions()
#     return SessionListResponse(sessions=sessions, total_count=len(sessions))

# @router.post("/sessions", tags=["LLM Chat"]) # For creating a session with a system prompt upfront
# async def create_openai_chat_session(...)
