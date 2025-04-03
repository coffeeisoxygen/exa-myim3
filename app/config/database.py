import logging
import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config.paths import ROOT_DIR

logger = logging.getLogger(__name__)

# Database file path
DATABASE_PATH = os.path.join(ROOT_DIR, "exa_myim3.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create SQLModel Engine
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """Create database and tables."""
    try:
        logger.info(f"Initializing database at {DATABASE_PATH}")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_session() -> Generator[Session, None, None]:
    """Provide a database session."""
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
