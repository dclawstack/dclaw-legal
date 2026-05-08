"""Contract review repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract_review import ClauseFinding, ContractReview
from app.schemas.contract_review import ContractReviewCreate


class ContractReviewRepository:
    """Contract review data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_all(self, limit: int = 20, offset: int = 0) -> tuple[list[ContractReview], int]:
        """List contract reviews with pagination."""
        total_result = await self.db.execute(select(func.count()).select_from(ContractReview))
        total = total_result.scalar() or 0

        stmt = (
            select(ContractReview)
            .order_by(ContractReview.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        reviews = list(result.scalars().all())
        return reviews, total

    async def get_by_id(self, review_id: UUID) -> ContractReview | None:
        """Get a contract review by ID."""
        result = await self.db.execute(
            select(ContractReview).where(ContractReview.id == review_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ContractReviewCreate) -> ContractReview:
        """Create a new contract review."""
        review = ContractReview(
            title=data.title,
            contract_text=data.contract_text,
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def update_status(self, review: ContractReview, status: str, risk_score: int) -> ContractReview:
        """Update review status and risk score."""
        review.status = status
        review.risk_score = risk_score
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review: ContractReview) -> None:
        """Delete a contract review."""
        await self.db.delete(review)
        await self.db.commit()


class ClauseFindingRepository:
    """Clause finding data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_review(self, review_id: UUID) -> list[ClauseFinding]:
        """List clause findings for a review."""
        result = await self.db.execute(
            select(ClauseFinding)
            .where(ClauseFinding.contract_review_id == review_id)
            .order_by(ClauseFinding.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(self, review_id: UUID, clause_text: str, clause_type: str, risk_level: str, recommendation: str | None = None) -> ClauseFinding:
        """Create a clause finding."""
        finding = ClauseFinding(
            contract_review_id=review_id,
            clause_text=clause_text,
            clause_type=clause_type,
            risk_level=risk_level,
            recommendation=recommendation,
        )
        self.db.add(finding)
        await self.db.commit()
        await self.db.refresh(finding)
        return finding
