"""Route model for directed hyperspace edges."""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Route(Base):
    """Directed route between gates with a hyperspace-unit distance."""
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    from_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("gates.code", ondelete="CASCADE"), nullable=False
    )
    to_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("gates.code", ondelete="CASCADE"), nullable=False
    )
    hu_distance: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("from_code", "to_code", name="uq_route"),
    )
