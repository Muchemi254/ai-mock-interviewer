# backend/common/redis_client.py
"""
Module responsible for initializing and managing the Redis connection.
This uses `redis.asyncio` for asynchronous compatibility with FastAPI.
"""

import redis.asyncio as redis
import logging
from typing import Optional
from .config import settings # Import settings to get the Redis URL

# Initialize logger
logger = logging.getLogger(__name__)

# Global variable to hold the Redis client instance
# Using Optional for explicit type hinting
redis_client: Optional[redis.Redis] = None

async def connect_to_redis():
    """
    Creates a connection to the Redis server using the URL from settings.
    Stores the client instance in the global `redis_client` variable.
    Includes basic error handling for connection failures.
    """
    global redis_client
    try:
        # Create the Redis client using the URL from environment/config
        # decode_responses=True ensures bytes are decoded to strings automatically
        redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info(f"Successfully connected to Redis at {settings.redis_url}")
        
        # Optional: Perform a quick ping to verify connectivity
        await redis_client.ping()
        logger.debug("Redis ping successful.")

    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis at {settings.redis_url}: {e}")
        # Depending on requirements, you might want to re-raise the exception
        # or handle it differently (e.g., retry logic)
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while connecting to Redis: {e}")
        raise

async def close_redis_connection():
    """
    Closes the connection to the Redis server.
    Ensures the global `redis_client` is properly closed and set back to None.
    """
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
            logger.info("Redis connection closed successfully.")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
        finally:
            # Ensure the client reference is cleared even if closing fails
            redis_client = None
    else:
        logger.debug("No Redis connection to close.")

def get_redis() -> redis.Redis:
    """
    Provides access to the initialized Redis client instance.
    Raises a RuntimeError if the client hasn't been initialized yet.
    This ensures that services using Redis fail fast if it's not set up.
    Returns:
        redis.Redis: The active Redis client instance.
    Raises:
        RuntimeError: If the Redis client is not initialized.
    """
    global redis_client
    if redis_client is None:
        # This indicates get_redis() was called before connect_to_redis()
        logger.error("Redis client requested but not initialized.")
        raise RuntimeError("Redis client is not initialized. Call connect_to_redis() first.")
    return redis_client

# Example of how to use it within an async context (like FastAPI lifespan):
# async def some_background_task():
#     redis_conn = get_redis()
#     await redis_conn.set("key", "value")
#     value = await redis_conn.get("key")
#     print(value)