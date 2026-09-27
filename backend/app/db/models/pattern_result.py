import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.pattern_discovery_run import PatternDiscoveryRun


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PatternResult(Base):
    """SQLAlchemy model for storing individual discovered pattern records."""

    __tablename__ = "pattern_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pattern_discovery_runs.id", ondelete="CASCADE"),
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
        index=True,
    )

    pattern_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    columns: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    statistics: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    significant: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    strength: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="WEAK",
    )

    sample_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    raw_p_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    adjusted_p_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    effect_size: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    method: Mapped[str] = mapped_column(
        String(50),
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

    run: Mapped["PatternDiscoveryRun"] = relationship(
        "PatternDiscoveryRun",
        back_populates="results",
    )

    def __repr__(self) -> str:
        return f"<PatternResult(id={self.id}, pattern_type='{self.pattern_type}', rank={self.rank}, score={self.score})>"
