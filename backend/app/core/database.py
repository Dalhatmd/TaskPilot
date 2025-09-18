"""
Database configuration and session management.
Handles SQLAlchemy setup and database connections.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# For now, using SQLite for development
DATABASE_URL = "sqlite:///./taskpilot.db"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    Used with FastAPI's Depends() for dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
