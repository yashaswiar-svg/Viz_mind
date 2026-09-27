import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.prediction_run import PredictionRun


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionResult(Base):
    """SQLAlchemy model for storing bounded individual prediction and forecast results."""

    __tablename__ = "prediction_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prediction_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    observation_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    actual_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    predicted_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    prediction_error: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    lower_bound: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    upper_bound: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    split: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="TEST",
        index=True,
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

    run: Mapped["PredictionRun"] = relationship(
        "PredictionRun",
        back_populates="results",
    )

    def __repr__(self) -> str:
        return f"<PredictionResult(id={self.id}, obs='{self.observation_reference}', split='{self.split}')>"
