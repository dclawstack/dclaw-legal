"""Batch contract processing models."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class BatchJob(Base, UUIDMixin, TimestampMixin):
    """A batch of contracts queued for review."""

    __tablename__ = "batch_jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Batch")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    total: Mapped[int] = mapped_column(default=0)
    completed: Mapped[int] = mapped_column(default=0)
    failed: Mapped[int] = mapped_column(default=0)

    items: Mapped[list["BatchJobItem"]] = relationship(
        "BatchJobItem",
        back_populates="job",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class BatchJobItem(Base, UUIDMixin, TimestampMixin):
    """A single contract within a batch job."""

    __tablename__ = "batch_job_items"

    batch_job_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("batch_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    contract_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    contract_review_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("contract_reviews.id", ondelete="SET NULL"),
        nullable=True,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    job: Mapped["BatchJob"] = relationship("BatchJob", back_populates="items")
