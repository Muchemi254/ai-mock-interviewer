# backend/services/llm-orchestrator/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import existing modules
# Import new modules
from routes import openai_chat
from clients import openai_client as openai_client_module # Import the module

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up LLM Orchestrator...")
    # --- Initialize Clients ---
    init_errors = []
    try:
        # Initialize the new OpenAI Chat Client (this replaces the old simple client init)
        # We store the instance in the module itself for easy access
        openai_client_module.openai_client = openai_client_module.OpenAIChatClient()
        # Make it available to the router module
        openai_chat.openai_chat_client = openai_client_module.openai_client
        logger.info("OpenAI Chat Client initialized.")
    except Exception as e:
        error_msg = f"Failed to initialize OpenAI Chat Client: {e}"
        logger.error(error_msg)
        init_errors.append(error_msg)

    # --- Initialize old clients if still used ---
    # from clients import gemini_client, openai_client # Old simple clients
    # try:
    #     await gemini_client.initialize_gemini()
    #     logger.info("Gemini client initialized.")
    # except Exception as e:
    #     error_msg = f"Failed to initialize Gemini client: {e}"
    #     logger.error(error_msg)
    #     init_errors.append(error_msg)

    # try:
    #     await openai_client.initialize_openai() # Old simple client init
    #     if openai_client.openai_client_instance:
    #          logger.info("OpenAI (simple) client initialized.")
    #     else:
    #          logger.info("OpenAI (simple) client initialization skipped.")
    # except Exception as e:
    #     error_msg = f"Failed to initialize OpenAI (simple) client: {e}"
    #     logger.error(error_msg)
    #     init_errors.append(error_msg)
    # --- End old client init ---

    if init_errors:
        logger.warning(f"LLM Orchestrator started with initialization errors: {init_errors}")
    else:
         logger.info("LLM Orchestrator clients initialized successfully.")

    yield
    # Shutdown
    logger.info("Shutting down LLM Orchestrator...")
    # Add any cleanup logic here if needed for clients

app = FastAPI(
    title="AI Mock Interviewer - LLM Orchestrator",
    description="A dedicated service for interacting with various LLMs, with session context.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include routers
# app.include_router(generate.router, prefix="/api/v1", tags=["LLM Generation"]) # Old routes
app.include_router(openai_chat.router, prefix="/api/v1", tags=["LLM Chat"]) # New chat routes

# Basic Health Check Endpoint (can be enhanced)
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    # Check status of new client
    openai_chat_ready = openai_chat.openai_chat_client is not None

    is_healthy = openai_chat_ready # For now, base health on this

    if not is_healthy:
        logger.warning("LLM Orchestrator health check failed.")
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "service": "LLM Orchestrator"})

    logger.info("LLM Orchestrator health check passed.")
    return {"status": "healthy", "service": "LLM Orchestrator", "details": {"openai_chat": openai_chat_ready}}
