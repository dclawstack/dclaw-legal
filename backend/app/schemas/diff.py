"""Contract comparison schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    text_a: str = Field(..., min_length=1)
    text_b: str = Field(..., min_length=1)
    label_a: str = Field(default="Version A", max_length=100)
    label_b: str = Field(default="Version B", max_length=100)


class DiffBlock(BaseModel):
    op: Literal["equal", "insert", "delete", "replace"]
    a_lines: list[str] = Field(default_factory=list)
    b_lines: list[str] = Field(default_factory=list)


class DiffSummary(BaseModel):
    added: int
    removed: int
    modified: int
    unchanged: int


class CompareResponse(BaseModel):
    label_a: str
    label_b: str
    blocks: list[DiffBlock]
    summary: DiffSummary
