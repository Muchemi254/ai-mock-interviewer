# backend/services/api-gateway/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware # Add if needed
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
import logging
from routes import auth as auth_routes # Import route handlers

from contextlib import asynccontextmanager
from common import database, redis_client, logging_config # Import database
from common.config import settings

# Setup logging
logger = logging_config.setup_logging()

# Setup logging
logger = logging_config.setup_logging()

# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up API Gateway...")
    await database.connect_to_db()
    await redis_client.connect_to_redis()
    # Add any other startup logic here (e.g., init LLM client)
    yield
    # Shutdown
    logger.info("Shutting down API Gateway...")
    await database.close_db_connection()
    await redis_client.close_redis_connection()
    # Add any other shutdown logic here

app = FastAPI(title="AI Mock Interviewer API Gateway", lifespan=lifespan)

# Add CORS middleware if frontend is on a different origin
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], # Configure appropriately for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

# Description:
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Mock Interviewer API Gateway"}


# Basic Health Check Endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    # Check database connection
    try:
        # Simple check - replace with actual DB ping if needed
        db_url = settings.database_url  # Replace with the correct way to get the database URL
        logger.info(f"Database URL configured: {db_url.split('@')[-1] if '@' in db_url else 'OK'}")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Check Redis connection
    try:
        redis_conn = redis_client.get_redis()
        if redis_conn:
            await redis_conn.ping()
            logger.info("Redis connection OK")
        else:
            logger.error("Redis client not initialized")
            raise HTTPException(status_code=503, detail="Redis client not initialized")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(status_code=503, detail="Redis unavailable")

    # Check LLM API Key (basic check)
    if not settings.gemini_api_key or settings.gemini_api_key == "your_google_gemini_api_key_here":
        logger.warning("Gemini API key not configured or using default placeholder")
        # Depending on requirements, you might want to fail the health check if critical
        # raise HTTPException(status_code=503, detail="LLM API key not configured")
    else:
        logger.info("LLM API key configured (basic check)")

    return {"status": "healthy", "service": "API Gateway"}

# --- Basic Auth Endpoint (moved to routes/auth.py, but shown here for completeness) ---
# @app.post("/auth/token", response_model=models.Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = auth.authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
#     access_token = auth.create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}
# --- End Basic Auth ---