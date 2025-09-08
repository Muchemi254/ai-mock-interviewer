# backend/common/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Global variables for engine and session
async_engine = None
AsyncSessionLocal = None

async def connect_to_db():
    global async_engine, AsyncSessionLocal
    try:
        # Create the async engine
        # asyncpg://user:password@host:port/database
        async_engine = create_async_engine(settings.database_url, echo=False) # Set echo=True for SQL debugging
        # Create the session factory
        AsyncSessionLocal = sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info(f"Connected to database at {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'OK'}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

async def close_db_connection():
    global async_engine
    if async_engine:
        await async_engine.dispose()
        logger.info("Database connection closed.")

# Dependency to get DB session
async def get_db_session() -> AsyncSession:
    """FastAPI dependency to get a database session."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        raise RuntimeError("Database session not initialized. Call connect_to_db() first.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Example function to get a user by username (using the ORM model)
from .database_models import User as DBUser # Import the SQLAlchemy model
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

async def get_user_by_username(db: AsyncSession, username: str) -> DBUser | None:
    """Fetch a user from the database by username."""
    try:
        # Use SQLAlchemy's select() with ORM model
        stmt = select(DBUser).where(DBUser.username == username)
        result = await db.execute(stmt)
        # scalars().first() gets the first result or None
        user = result.scalars().first()
        return user
    except NoResultFound:
        return None
    except Exception as e:
        logger.error(f"Error fetching user by username '{username}': {e}")
        raise

# Example function to create a user
import uuid
from datetime import datetime

async def create_user(db: AsyncSession, username: str, email: str, hashed_password: str) -> DBUser:
    """Create a new user in the database."""
    try:
        db_user = DBUser(
            id=uuid.uuid4(), # Generate UUID
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user) # Refresh to get the ID if needed
        logger.info(f"Created user: {db_user}")
        return db_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user '{username}': {e}")
        raise