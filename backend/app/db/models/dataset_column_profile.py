import uuid
from typing import Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, JSON
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class DatasetColumnProfile(Base):
    """SQLAlchemy model for column-level profile statistics."""

    __tablename__ = "dataset_column_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dataset_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    column_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    inferred_type: Mapped[str] = mapped_column(String(50), nullable=False)
    pandas_dtype: Mapped[str] = mapped_column(String(50), nullable=False)

    null_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    null_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    non_null_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    unique_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_constant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Numerical statistics
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mean_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    std_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    q1_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    q3_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Categorical & Text statistics
    top_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    min_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_length: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Datetime statistics
    min_datetime: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_datetime: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Boolean statistics
    true_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    false_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationship to parent profile
    profile: Mapped["DatasetProfile"] = relationship("DatasetProfile", back_populates="columns")

    def __repr__(self) -> str:
        return f"<DatasetColumnProfile(name='{self.column_name}', type='{self.inferred_type}')>"
