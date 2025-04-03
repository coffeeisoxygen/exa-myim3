"""
Database connection and session management.
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create SQLModel engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)


def create_db_and_tables() -> None:
    """Create database and tables."""
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Provide a database session.

    Yields:
        SQLModel session
    """
    session = Session(engine)
    try:
        yield session
    except Exception as e:
        logger.error(f"Database error: {e}")
        session.rollback()
        raise
    finally:
        session.close()
