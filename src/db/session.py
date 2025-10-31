"""
Database session management and utilities.
"""
from typing import Generator
from sqlalchemy.orm import Session
from contextlib import contextmanager

from src.models.base import SessionLocal, engine


def get_db() -> Generator[Session, None, None]:
    """Get database session with proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_database():
    """Initialize database tables."""
    from src.models.base import create_tables
    create_tables()


def reset_database():
    """Reset database (drop and recreate all tables)."""
    from src.models.base import drop_tables, create_tables
    drop_tables()
    create_tables()


def health_check() -> bool:
    """Check database connectivity."""
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        return True
    except Exception:
        return False


def get_connection_info() -> dict:
    """Get database connection information."""
    return {
        "database_url": str(engine.url).replace(engine.url.password or "", "***"),
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "invalid": engine.pool.invalid(),
        "driver": engine.driver
    }
