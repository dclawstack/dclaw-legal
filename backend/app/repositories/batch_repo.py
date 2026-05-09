"""Batch job repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch_job import BatchJob, BatchJobItem


class BatchJobRepository:
    """Batch job data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_all(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[list[BatchJob], int]:
        total_result = await self.db.execute(
            select(func.count()).select_from(BatchJob)
        )
        total = total_result.scalar() or 0
        stmt = (
            select(BatchJob)
            .order_by(BatchJob.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, job_id: UUID) -> BatchJob | None:
        result = await self.db.execute(
            select(BatchJob).where(BatchJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, items: list[tuple[str, str]]) -> BatchJob:
        """Create a job with the given items.

        ``items`` is a list of ``(filename, contract_text)`` pairs.
        """
        job = BatchJob(name=name, status="pending", total=len(items))
        self.db.add(job)
        await self.db.flush()
        for filename, text in items:
            self.db.add(
                BatchJobItem(
                    batch_job_id=job.id,
                    filename=filename,
                    contract_text=text,
                    status="pending",
                )
            )
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def update_counts(
        self, job: BatchJob, *, completed: int, failed: int, status: str
    ) -> BatchJob:
        job.completed = completed
        job.failed = failed
        job.status = status
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_item(self, item_id: UUID) -> BatchJobItem | None:
        result = await self.db.execute(
            select(BatchJobItem).where(BatchJobItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def update_item(
        self,
        item: BatchJobItem,
        *,
        status: str,
        contract_review_id: UUID | None = None,
        error: str | None = None,
    ) -> BatchJobItem:
        item.status = status
        item.contract_review_id = contract_review_id
        item.error = error
        await self.db.commit()
        await self.db.refresh(item)
        return item
