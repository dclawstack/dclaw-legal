"""Contract review model."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ContractReview(Base, UUIDMixin, TimestampMixin):
    """A contract review record."""

    __tablename__ = "contract_reviews"

    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Contract Review")
    contract_text: Mapped[str] = mapped_column(Text, nullable=False)
    risk_score: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )

    findings: Mapped[list["ClauseFinding"]] = relationship(
        "ClauseFinding", back_populates="contract_review", lazy="selectin", cascade="all, delete-orphan"
    )


class ClauseFinding(Base, UUIDMixin, TimestampMixin):
    """A clause finding from a contract review."""

    __tablename__ = "clause_findings"

    contract_review_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("contract_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clause_text: Mapped[str] = mapped_column(Text, nullable=False)
    clause_type: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="low"
    )
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    contract_review: Mapped["ContractReview"] = relationship("ContractReview", back_populates="findings")
