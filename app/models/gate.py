"""Gate model representing a hyperspace gate."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Gate(Base):
    """Gate entity with a stable 3-letter code and display name."""
    __tablename__ = "gates"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
