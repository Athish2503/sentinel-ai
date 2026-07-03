import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ToolCall(Base):
    """
    ToolCall ORM Model representing an individual tool invocation by the AI Agent.
    """
    __tablename__ = "tool_calls"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    tool_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    tool_arguments: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )
    execution_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    execution_time: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="tool_calls"
    )
