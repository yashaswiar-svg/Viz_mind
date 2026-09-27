import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.insight import Insight


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InsightEvidence(Base):
    """SQLAlchemy model linking individual insights to grounded source evidence metrics."""

    __tablename__ = "insight_evidences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    insight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("insights.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    evidence_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    source_phase: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    metrics: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    insight: Mapped["Insight"] = relationship(
        "Insight",
        back_populates="evidence_items",
    )

    def __repr__(self) -> str:
        return f"<InsightEvidence(id={self.id}, evidence_id='{self.evidence_id}', phase='{self.source_phase}')>"
