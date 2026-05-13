"""SQLAlchemy models."""

from app.database import Base

# Re-export Base for migrations
__all__ = ["Base"]