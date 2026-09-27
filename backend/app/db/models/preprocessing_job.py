import uuid
from datetime import datetime, timezone
from typing import Optional
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


class PreprocessingJob(Base):
    """SQLAlchemy model for tracking a preprocessing job execution."""

    __tablename__ = "preprocessing_jobs"

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

    source_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dataset_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    output_dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rows_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    columns_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    columns_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    missing_cells_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing_cells_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    duplicate_rows_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_rows_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    source_checksum_before: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source_checksum_after: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    processed_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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

    transformations: Mapped[list["PreprocessingTransformation"]] = relationship(
        "PreprocessingTransformation",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="PreprocessingTransformation.step_order",
    )

    def __repr__(self) -> str:
        return f"<PreprocessingJob(id={self.id}, dataset_id={self.dataset_id}, status='{self.status}')>"
