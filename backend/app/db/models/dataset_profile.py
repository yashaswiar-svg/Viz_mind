import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, JSON
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


class DatasetProfile(Base):
    """SQLAlchemy model for dataset-level profile metrics and quality score."""

    __tablename__ = "dataset_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    duplicate_row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_row_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    missing_cell_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing_cell_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    memory_usage_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    sheet_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    quality_level: Mapped[str] = mapped_column(String(50), nullable=False, default="Excellent")
    quality_issues: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    profiled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
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

    # Relationship to column profiles
    columns: Mapped[List["DatasetColumnProfile"]] = relationship(
        "DatasetColumnProfile",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="DatasetColumnProfile.column_index",
    )

    @property
    def column_profiles(self):
        return self.columns

    def __repr__(self) -> str:
        return f"<DatasetProfile(id={self.id}, dataset_id={self.dataset_id}, score={self.quality_score})>"
