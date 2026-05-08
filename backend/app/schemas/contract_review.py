"""Contract review schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class ClauseFindingBase(BaseModel):
    """Base clause finding fields."""

    clause_text: str = Field(..., min_length=1)
    clause_type: str = Field(..., min_length=1, max_length=100)
    risk_level: str = Field(default="low", pattern="^(low|medium|high|critical)$")
    recommendation: str | None = None


class ClauseFindingCreate(ClauseFindingBase):
    """Schema for creating a clause finding."""

    contract_review_id: UUID


class ClauseFindingResponse(ClauseFindingBase):
    """Clause finding response schema."""

    id: UUID
    contract_review_id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ContractReviewBase(BaseModel):
    """Base contract review fields."""

    title: str = Field(default="Contract Review", max_length=255)
    contract_text: str = Field(..., min_length=1)


class ContractReviewCreate(ContractReviewBase):
    """Schema for creating a contract review."""
    pass


class ContractReviewResponse(ContractReviewBase):
    """Contract review response schema."""

    id: UUID
    risk_score: int
    status: str
    findings: list[ClauseFindingResponse] = []
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ContractReviewListResponse(BaseModel):
    """List of contract reviews."""

    items: list[ContractReviewResponse]
    total: int
