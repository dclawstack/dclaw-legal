"""Legal contract review endpoints."""

import io
import zipfile
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.batch_repo import BatchJobRepository
from app.repositories.contract_review_repo import ClauseFindingRepository, ContractReviewRepository
from app.schemas.batch_job import BatchJobListResponse, BatchJobResponse
from app.schemas.contract_review import (
    ContractReviewCreate,
    ContractReviewListResponse,
    ContractReviewResponse,
)
from app.schemas.diff import CompareRequest, CompareResponse, DiffBlock, DiffSummary
from app.services.batch_service import process_batch
from app.services.diff_service import compute_line_diff, compute_summary
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


@router.post("/legal/compare", response_model=CompareResponse)
async def compare_contracts(request: CompareRequest) -> CompareResponse:
    """Compute a line-level diff between two contract texts."""
    blocks = compute_line_diff(request.text_a, request.text_b)
    summary = compute_summary(blocks)
    return CompareResponse(
        label_a=request.label_a,
        label_b=request.label_b,
        blocks=[DiffBlock(**b) for b in blocks],
        summary=DiffSummary(**summary),
    )


# ---------- Batch Processing ----------

_MAX_BATCH_BYTES = 25 * 1024 * 1024  # 25 MB total


def _decode_text(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


async def _extract_items(files: list[UploadFile]) -> list[tuple[str, str]]:
    """Flatten the uploaded files (incl. zip archives) into (name, text) pairs."""
    items: list[tuple[str, str]] = []
    total_bytes = 0
    for uploaded in files:
        data = await uploaded.read()
        total_bytes += len(data)
        if total_bytes > _MAX_BATCH_BYTES:
            raise HTTPException(
                status_code=413, detail="Batch upload exceeds 25 MB limit"
            )
        name = uploaded.filename or "upload.txt"
        if name.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for member in zf.namelist():
                    if member.endswith("/"):
                        continue
                    with zf.open(member) as fh:
                        items.append((member, _decode_text(fh.read())))
        else:
            items.append((name, _decode_text(data)))
    return items


@router.post(
    "/legal/batch",
    response_model=BatchJobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
) -> BatchJobResponse:
    """Upload one or more contracts (or a zip) for batch review."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    items = await _extract_items(files)
    if not items:
        raise HTTPException(status_code=400, detail="No usable files found")

    repo = BatchJobRepository(db)
    job = await repo.create(name=f"Batch of {len(items)}", items=items)

    background_tasks.add_task(process_batch, job.id)

    return BatchJobResponse.model_validate(job)


@router.get("/legal/batch", response_model=BatchJobListResponse)
async def list_batches(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> BatchJobListResponse:
    repo = BatchJobRepository(db)
    jobs, total = await repo.list_all(
        limit=page_size, offset=(page - 1) * page_size
    )
    return BatchJobListResponse(
        items=[BatchJobResponse.model_validate(j) for j in jobs],
        total=total,
    )


@router.get("/legal/batch/{job_id}", response_model=BatchJobResponse)
async def get_batch(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BatchJobResponse:
    repo = BatchJobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchJobResponse.model_validate(job)
