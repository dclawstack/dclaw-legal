"""Batch processing — runs review for each item via FastAPI BackgroundTasks."""

from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.repositories.batch_repo import BatchJobRepository
from app.repositories.contract_review_repo import (
    ClauseFindingRepository,
    ContractReviewRepository,
)
from app.schemas.contract_review import ContractReviewCreate
from app.services.legal_service import review_contract


async def process_batch(job_id: UUID) -> None:
    """Process every item in a batch job. Runs in background.

    Each item gets its own DB session so failures don't poison siblings.
    The job's aggregate ``status`` / ``completed`` / ``failed`` counters are
    updated as items finish.
    """
    completed = 0
    failed = 0

    async with AsyncSessionLocal() as session:
        job_repo = BatchJobRepository(session)
        job = await job_repo.get_by_id(job_id)
        if not job:
            return
        item_ids = [item.id for item in job.items]
        await job_repo.update_counts(
            job, completed=0, failed=0, status="processing"
        )

    for item_id in item_ids:
        async with AsyncSessionLocal() as session:
            repo = BatchJobRepository(session)
            review_repo = ContractReviewRepository(session)
            finding_repo = ClauseFindingRepository(session)

            item = await repo.get_item(item_id)
            if not item:
                continue

            try:
                review = await review_repo.create(
                    ContractReviewCreate(
                        title=item.filename, contract_text=item.contract_text
                    )
                )
                analysis = await review_contract(item.contract_text)
                await review_repo.update_status(
                    review, "completed", analysis["risk_score"]
                )
                for clause in analysis.get("key_clauses", []):
                    await finding_repo.create(
                        review_id=review.id,
                        clause_text=clause,
                        clause_type="Detected Clause",
                        risk_level=(
                            "medium" if analysis["risk_score"] > 30 else "low"
                        ),
                        recommendation="See review summary.",
                    )
                await repo.update_item(
                    item,
                    status="completed",
                    contract_review_id=review.id,
                )
                completed += 1
            except Exception as exc:  # noqa: BLE001
                await repo.update_item(item, status="failed", error=str(exc))
                failed += 1

    async with AsyncSessionLocal() as session:
        repo = BatchJobRepository(session)
        job = await repo.get_by_id(job_id)
        if job:
            final_status = (
                "completed" if failed == 0
                else "partial" if completed > 0
                else "failed"
            )
            await repo.update_counts(
                job, completed=completed, failed=failed, status=final_status
            )
