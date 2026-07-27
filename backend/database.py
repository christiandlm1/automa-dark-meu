"""
AUTOMA Backend - Database Engine & Session Factory
Async SQLAlchemy 2.0+ with aiosqlite, WAL mode enabled.
"""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


# --- Async Engine ---
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record):
    """Enable WAL mode, foreign keys and busy timeout for SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


# --- Session Factory ---
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents DetachedInstanceError in async
)


# --- Declarative Base ---
class Base(AsyncAttrs, DeclarativeBase):
    """Base model with AsyncAttrs for lazy relationship loading in async."""
    pass


# --- FastAPI Dependency ---
async def get_db():
    """Yield an async database session. Auto-commits or rolls back."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# --- Table Creation ---
async def migrate_history_table() -> None:
    """Safely add speed, cpu_usage, ram_usage, and gpu_usage columns to the history table if they don't exist."""
    from sqlalchemy import text
    columns = [
        ("speed", "FLOAT DEFAULT 0.0"),
        ("cpu_usage", "FLOAT DEFAULT 0.0"),
        ("ram_usage", "FLOAT DEFAULT 0.0"),
        ("gpu_usage", "FLOAT DEFAULT 0.0"),
    ]
    async with engine.begin() as conn:
        for col_name, col_type in columns:
            try:
                await conn.execute(text(f"ALTER TABLE history ADD COLUMN {col_name} {col_type}"))
            except Exception:
                # Column already exists
                pass

async def migrate_export_profile() -> None:
    """Safely add export_profile_id column to the jobs table if it doesn't exist."""
    from sqlalchemy import text
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN export_profile_id VARCHAR(36)"))
        except Exception:
            pass

async def migrate_video_templates() -> None:
    from sqlalchemy import text
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE video_templates ADD COLUMN versions_history JSON DEFAULT '[]'"))
        except Exception:
            pass

async def migrate_module_08() -> None:
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Jobs
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN priority INTEGER DEFAULT 0"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE jobs ADD COLUMN retry_count INTEGER DEFAULT 0"))
        except Exception:
            pass
        # History
        try:
            await conn.execute(text("ALTER TABLE history ADD COLUMN retry_count INTEGER DEFAULT 0"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE history ADD COLUMN attempts_details TEXT"))
        except Exception:
            pass

async def init_db() -> None:
    """Create all tables defined by ORM models."""
    import models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await migrate_history_table()
    await migrate_export_profile()
    await migrate_video_templates()
    await migrate_module_08()



async def close_db() -> None:
    """Dispose engine connections."""
    await engine.dispose()
