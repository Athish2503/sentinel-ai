import uuid
from datetime import datetime, timezone
from sqlalchemy import Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Alert(Base):
    """
    Alert ORM Model representing an anomaly alert generated for a session.
    """
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="alerts"
    )
