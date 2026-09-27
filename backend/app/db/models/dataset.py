import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy import JSON, Uuid as UUID
try:
    from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
    JSONB = JSON().with_variant(PG_JSONB, "postgresql")
except Exception:
    JSONB = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user import User


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Dataset(Base):
    """SQLAlchemy model for dataset entity."""

    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    parent_dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=True,
    )
    dataset_kind: Mapped[str] = mapped_column(String(50), nullable=False, default="SOURCE")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

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

    derived_datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="parent_dataset",
        cascade="all, delete-orphan",
    )
    parent_dataset: Mapped[Optional["Dataset"]] = relationship(
        "Dataset",
        back_populates="derived_datasets",
        remote_side=[id],
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="datasets",
    )


    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name='{self.name}', kind='{self.dataset_kind}', status='{self.status}')>"

