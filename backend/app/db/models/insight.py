import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.insight_run import InsightRun
    from app.db.models.insight_evidence import InsightEvidence


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Insight(Base):
    """SQLAlchemy model for individual AI insights generated from analytical evidence."""

    __tablename__ = "insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("insight_runs.id", ondelete="CASCADE"),
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

    insight_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    importance_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        index=True,
    )

    importance_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
        index=True,
    )

    evidence_strength: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MODERATE",
    )

    columns: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    statistics: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    limitations: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    generation_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="LLM",
    )

    validation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="VALIDATED",
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

    run: Mapped["InsightRun"] = relationship(
        "InsightRun",
        back_populates="insights",
    )

    evidence_items: Mapped[List["InsightEvidence"]] = relationship(
        "InsightEvidence",
        back_populates="insight",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Insight(id={self.id}, type='{self.insight_type}', title='{self.title[:30]}', score={self.importance_score})>"
