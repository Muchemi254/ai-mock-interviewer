# backend/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os
import logging

# Add the parent directory to the path so we can import 'common'
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import your SQLAlchemy Base and models
from common.database_models import Base  # Import the Base from your models file
# Import settings to get the DATABASE_URL
from common.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception as e:
        # Fallback to basic logging if fileConfig fails
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('alembic.env')
        logger.warning(f"Could not configure logging from file: {e}")

# Robust URL conversion for Alembic migrations
# Alembic requires synchronous database connections
if settings.database_url.startswith("postgresql+asyncpg://"):
    sync_database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
elif settings.database_url.startswith("postgresql+psycopg2://"):
    sync_database_url = settings.database_url  # Already sync
else:
    # Handle other cases by converting to standard postgresql://
    sync_database_url = f"postgresql://{settings.database_url.split('://')[1]}"

config.set_main_option('sqlalchemy.url', sync_database_url)
print(f"Alembic using sync URL: {sync_database_url}")

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata  # Use the metadata from your Base

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()