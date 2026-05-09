"""Document template repository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_template import DocumentTemplate
from app.schemas.document_template import DocumentTemplateCreate


class DocumentTemplateRepository:
    """Document template data access repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_all(
        self, limit: int = 50, offset: int = 0
    ) -> tuple[list[DocumentTemplate], int]:
        total_result = await self.db.execute(
            select(func.count()).select_from(DocumentTemplate)
        )
        total = total_result.scalar() or 0
        stmt = (
            select(DocumentTemplate)
            .order_by(DocumentTemplate.category.asc(), DocumentTemplate.name.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, template_id: UUID) -> DocumentTemplate | None:
        result = await self.db.execute(
            select(DocumentTemplate).where(DocumentTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: DocumentTemplateCreate) -> DocumentTemplate:
        template = DocumentTemplate(
            name=data.name,
            category=data.category,
            description=data.description,
            template_text=data.template_text,
            variables={k: v.model_dump() for k, v in data.variables.items()},
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def delete(self, template: DocumentTemplate) -> None:
        await self.db.delete(template)
        await self.db.commit()
