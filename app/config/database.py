import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config.paths import ROOT_DIR

# Database file path
DATABASE_PATH = os.path.join(ROOT_DIR, "exa.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create SQLModel Engine
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Provide a database session."""
    with Session(engine) as session:
        yield session
