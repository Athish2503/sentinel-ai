import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Session(Base):
    """
    Session ORM Model representing an execution session for an AI Agent.
    """
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    anomaly_score: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"
    )

    # Relationships
    tool_calls: Mapped[list["ToolCall"]] = relationship(
        "ToolCall",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ToolCall.execution_order"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="session",
        cascade="all, delete-orphan"
    )
