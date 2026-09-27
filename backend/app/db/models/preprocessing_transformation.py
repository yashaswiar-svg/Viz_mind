import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PreprocessingTransformation(Base):
    """SQLAlchemy model for individual preprocessing transformation step execution."""

    __tablename__ = "preprocessing_transformations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("preprocessing_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    transformation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    column_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    rows_affected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    values_affected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    job: Mapped["PreprocessingJob"] = relationship("PreprocessingJob", back_populates="transformations")

    def __repr__(self) -> str:
        return f"<PreprocessingTransformation(id={self.id}, step={self.step_order}, type='{self.transformation_type}')>"
