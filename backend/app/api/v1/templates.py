"""Document template endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.template_repo import DocumentTemplateRepository
from app.schemas.document_template import (
    DocumentTemplateCreate,
    DocumentTemplateListResponse,
    DocumentTemplateResponse,
    TemplateGenerateRequest,
    TemplateGenerateResponse,
)
from app.services.template_service import render_template

router = APIRouter()


@router.get("/templates", response_model=DocumentTemplateListResponse)
async def list_templates(
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
) -> DocumentTemplateListResponse:
    repo = DocumentTemplateRepository(db)
    items, total = await repo.list_all(
        limit=page_size, offset=(page - 1) * page_size
    )
    return DocumentTemplateListResponse(
        items=[DocumentTemplateResponse.model_validate(t) for t in items],
        total=total,
    )


@router.get("/templates/{template_id}", response_model=DocumentTemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentTemplateResponse:
    repo = DocumentTemplateRepository(db)
    template = await repo.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return DocumentTemplateResponse.model_validate(template)


@router.post(
    "/templates",
    response_model=DocumentTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    data: DocumentTemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> DocumentTemplateResponse:
    repo = DocumentTemplateRepository(db)
    template = await repo.create(data)
    return DocumentTemplateResponse.model_validate(template)


@router.post(
    "/templates/{template_id}/generate",
    response_model=TemplateGenerateResponse,
)
async def generate_from_template(
    template_id: UUID,
    request: TemplateGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> TemplateGenerateResponse:
    repo = DocumentTemplateRepository(db)
    template = await repo.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    rendered, missing = render_template(template, request.values)
    return TemplateGenerateResponse(
        template_id=template.id,
        rendered_text=rendered,
        missing_variables=missing,
    )


@router.delete(
    "/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = DocumentTemplateRepository(db)
    template = await repo.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    await repo.delete(template)
