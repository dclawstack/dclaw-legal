"""E-signature schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class SendForSignatureRequest(BaseModel):
    signer_email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=255)
    signer_name: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(default="Please sign this contract", max_length=200)


class SendForSignatureResponse(BaseModel):
    review_id: UUID
    envelope_id: str
    signature_status: str


class WebhookPayload(BaseModel):
    """Subset of DocuSign Connect envelope-status webhook payload."""

    envelope_id: str = Field(..., alias="envelopeId")
    status: str

    class Config:
        populate_by_name = True
