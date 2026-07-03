import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Baseline(Base):
    """
    Baseline ORM Model representing the trained behavioral baseline configuration.
    """
    __tablename__ = "baselines"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    model_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    training_runs: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
