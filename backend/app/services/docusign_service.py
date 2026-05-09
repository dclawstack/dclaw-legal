"""DocuSign eSignature integration.

Operates in two modes:

* **Real** — when ``DOCUSIGN_ACCOUNT_ID`` and ``DOCUSIGN_ACCESS_TOKEN`` are set,
  envelopes are created via the DocuSign REST API.
* **Stub** — otherwise, a deterministic ``stub-<uuid>`` envelope id is returned
  so the rest of the workflow (UI, webhook handling, status tracking) still
  works in dev and tests without DocuSign credentials.
"""

import base64
import uuid

import httpx

from app.core.config import settings

_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


def _is_configured() -> bool:
    return bool(settings.docusign_account_id and settings.docusign_access_token)


async def send_envelope(
    *, contract_text: str, signer_email: str, signer_name: str, subject: str
) -> dict:
    """Send a contract for signature. Returns ``{envelope_id, status}``."""
    if not _is_configured():
        return {"envelope_id": f"stub-{uuid.uuid4().hex[:12]}", "status": "sent"}

    document_b64 = base64.b64encode(contract_text.encode("utf-8")).decode("ascii")
    payload = {
        "emailSubject": subject,
        "documents": [
            {
                "documentBase64": document_b64,
                "name": subject,
                "fileExtension": "txt",
                "documentId": "1",
            }
        ],
        "recipients": {
            "signers": [
                {
                    "email": signer_email,
                    "name": signer_name,
                    "recipientId": "1",
                    "routingOrder": "1",
                    "tabs": {
                        "signHereTabs": [
                            {
                                "anchorString": "Signed:",
                                "anchorYOffset": "10",
                                "anchorUnits": "pixels",
                                "anchorXOffset": "60",
                            }
                        ]
                    },
                }
            ]
        },
        "status": "sent",
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{settings.docusign_base_url}/v2.1/accounts/{settings.docusign_account_id}/envelopes",
            headers={
                "Authorization": f"Bearer {settings.docusign_access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        body = resp.json()
        return {
            "envelope_id": body.get("envelopeId", ""),
            "status": body.get("status", "sent"),
        }


def normalize_webhook_status(raw_status: str) -> str:
    """Map DocuSign envelope statuses to our short labels."""
    status = (raw_status or "").lower()
    return {
        "sent": "sent",
        "delivered": "delivered",
        "completed": "signed",
        "declined": "declined",
        "voided": "voided",
    }.get(status, status or "unknown")
