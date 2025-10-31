"""
SQLAlchemy base configuration and common model functionality.
"""
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, Integer, DateTime, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from src.core.config import db_settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    db_settings.database_url,
    poolclass=QueuePool,
    pool_size=db_settings.pool_size,
    max_overflow=db_settings.max_overflow,
    pool_timeout=db_settings.pool_timeout,
    pool_recycle=db_settings.pool_recycle,
    echo=db_settings.echo,  # SQL query logging
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields and methods."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    @classmethod
    def create(cls, **kwargs) -> 'BaseModel':
        """Create a new instance of the model."""
        instance = cls(**kwargs)
        return instance

    def save(self, db: Session) -> None:
        """Save the model instance to database."""
        db.add(self)
        db.commit()
        db.refresh(self)

    def delete(self, db: Session) -> None:
        """Delete the model instance from database."""
        db.delete(self)
        db.commit()


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    # Import all models to ensure they are registered with Base.metadata
    # Import in dependency order: base models first, then models with relationships
    from . import user  # noqa: F401
    from . import resume  # noqa: F401
    from . import job  # noqa: F401
    from . import application  # noqa: F401
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)


def init_db():
    """Initialize database with tables."""
    create_tables()
