import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
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

    # Relationships
    feature_vectors: Mapped[list["BaselineFeatureVector"]] = relationship(
        "BaselineFeatureVector",
        back_populates="baseline",
        cascade="all, delete-orphan"
    )

class BaselineFeatureVector(Base):
    """
    BaselineFeatureVector ORM Model representing the extracted features of a single run used for training a baseline.
    """
    __tablename__ = "baseline_feature_vectors"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    baseline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("baselines.id", ondelete="CASCADE"),
        nullable=False
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True
    )
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    sequence: Mapped[list] = mapped_column(
        JSON,
        nullable=False
    )
    tool_frequency: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )
    execution_order: Mapped[list] = mapped_column(
        JSON,
        nullable=False
    )
    execution_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    average_execution_time: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    parameter_length: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    baseline: Mapped["Baseline"] = relationship(
        "Baseline",
        back_populates="feature_vectors"
    )
    session: Mapped[Optional["Session"]] = relationship(
        "Session"
    )

