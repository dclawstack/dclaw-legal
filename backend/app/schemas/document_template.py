"""Document template schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class TemplateVariable(BaseModel):
    """Variable definition for a template."""

    label: str = Field(..., min_length=1)
    type: str = Field(default="text", pattern="^(text|textarea|date|number)$")
    required: bool = True


class DocumentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="general", max_length=100)
    description: str | None = None
    template_text: str = Field(..., min_length=1)
    variables: dict[str, TemplateVariable] = Field(default_factory=dict)


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateResponse(DocumentTemplateBase):
    id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class DocumentTemplateListResponse(BaseModel):
    items: list[DocumentTemplateResponse]
    total: int


class TemplateGenerateRequest(BaseModel):
    """Variable values supplied to fill a template."""

    values: dict[str, str] = Field(default_factory=dict)


class TemplateGenerateResponse(BaseModel):
    template_id: UUID
    rendered_text: str
    missing_variables: list[str] = Field(default_factory=list)
