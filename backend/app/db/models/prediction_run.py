import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.prediction_result import PredictionResult


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionRun(Base):
    """SQLAlchemy model for tracking prediction and forecasting execution runs."""

    __tablename__ = "prediction_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    processed_dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dataset_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    processed_checksum: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    problem_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    target_column: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    training_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    validation_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    test_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    feature_columns: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    metrics: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    baseline_metrics: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    model_parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    random_state: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=42,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    results: Mapped[list["PredictionResult"]] = relationship(
        "PredictionResult",
        back_populates="run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PredictionRun(id={self.id}, target='{self.target_column}', problem_type='{self.problem_type}', status='{self.status}')>"
