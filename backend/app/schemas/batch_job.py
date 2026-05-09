"""Batch job schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class BatchJobItemResponse(BaseModel):
    id: UUID
    batch_job_id: UUID
    filename: str
    status: str
    contract_review_id: UUID | None = None
    error: str | None = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BatchJobResponse(BaseModel):
    id: UUID
    name: str
    status: str
    total: int
    completed: int
    failed: int
    items: list[BatchJobItemResponse] = Field(default_factory=list)
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BatchJobListResponse(BaseModel):
    items: list[BatchJobResponse]
    total: int
