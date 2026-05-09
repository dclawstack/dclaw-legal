"""E-signature endpoints (DocuSign integration)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.contract_review_repo import ContractReviewRepository
from app.schemas.signature import (
    SendForSignatureRequest,
    SendForSignatureResponse,
    WebhookPayload,
)
from app.services.docusign_service import normalize_webhook_status, send_envelope

router = APIRouter()


@router.post(
    "/contracts/reviews/{review_id}/sign",
    response_model=SendForSignatureResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_for_signature(
    review_id: UUID,
    request: SendForSignatureRequest,
    db: AsyncSession = Depends(get_db),
) -> SendForSignatureResponse:
    """Send a reviewed contract to DocuSign for signature."""
    repo = ContractReviewRepository(db)
    review = await repo.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    try:
        result = await send_envelope(
            contract_text=review.contract_text,
            signer_email=request.signer_email,
            signer_name=request.signer_name,
            subject=request.subject,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502, detail=f"DocuSign request failed: {exc}"
        ) from exc

    await repo.update_signature(
        review,
        envelope_id=result["envelope_id"],
        signer_email=request.signer_email,
        signature_status=result["status"],
    )

    return SendForSignatureResponse(
        review_id=review.id,
        envelope_id=result["envelope_id"],
        signature_status=result["status"],
    )


@router.post("/signatures/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def signature_webhook(
    payload: WebhookPayload,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Receive envelope-status updates from DocuSign Connect."""
    repo = ContractReviewRepository(db)
    review = await repo.get_by_envelope(payload.envelope_id)
    if not review:
        # Unknown envelope — silently 204 so DocuSign doesn't keep retrying.
        return
    await repo.update_signature_status(
        review, normalize_webhook_status(payload.status)
    )
