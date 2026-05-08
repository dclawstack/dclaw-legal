"""Legal contract review endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.contract_review_repo import ClauseFindingRepository, ContractReviewRepository
from app.schemas.contract_review import (
    ContractReviewCreate,
    ContractReviewListResponse,
    ContractReviewResponse,
)
from app.services.legal_service import review_contract

router = APIRouter()


@router.get("/contracts/reviews", response_model=ContractReviewListResponse)
async def list_reviews(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ContractReviewListResponse:
    """List all contract reviews."""
    repo = ContractReviewRepository(db)
    reviews, total = await repo.list_all(limit=page_size, offset=(page - 1) * page_size)
    return ContractReviewListResponse(
        items=[ContractReviewResponse.model_validate(r) for r in reviews],
        total=total,
    )


@router.post("/contracts/review", response_model=ContractReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ContractReviewCreate,
    db: AsyncSession = Depends(get_db),
) -> ContractReviewResponse:
    """Create a contract review and run AI analysis."""
    repo = ContractReviewRepository(db)
    finding_repo = ClauseFindingRepository(db)

    review = await repo.create(data)

    # Run AI analysis
    analysis = await review_contract(data.contract_text)

    # Update review with results
    await repo.update_status(review, "completed", analysis["risk_score"])

    # Store findings
    for clause in analysis.get("key_clauses", []):
        await finding_repo.create(
            review_id=review.id,
            clause_text=clause,
            clause_type="Detected Clause",
            risk_level="medium" if analysis["risk_score"] > 30 else "low",
            recommendation="See review summary.",
        )

    # Refresh to load findings
    review = await repo.get_by_id(review.id)
    return ContractReviewResponse.model_validate(review)


@router.get("/contracts/reviews/{review_id}", response_model=ContractReviewResponse)
async def get_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ContractReviewResponse:
    """Get a contract review by ID."""
    repo = ContractReviewRepository(db)
    review = await repo.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ContractReviewResponse.model_validate(review)


@router.delete("/contracts/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a contract review."""
    repo = ContractReviewRepository(db)
    review = await repo.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    await repo.delete(review)
