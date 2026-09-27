import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.visualization_run import VisualizationRun


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VisualizationRecommendation(Base):
    """SQLAlchemy model for individual chart visualization recommendations."""

    __tablename__ = "visualization_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("visualization_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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
    )

    profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dataset_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chart_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    x_column: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    y_column: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    aggregation: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chart_spec: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
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

    run: Mapped["VisualizationRun"] = relationship(
        "VisualizationRun",
        back_populates="recommendations",
    )

    def __repr__(self) -> str:
        return f"<VisualizationRecommendation(id={self.id}, chart_type='{self.chart_type}', rank={self.rank}, score={self.score})>"
