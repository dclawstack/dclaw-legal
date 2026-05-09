"""E-signature router tests (uses DocuSign stub mode — no creds needed)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_for_signature_stub_mode(client: AsyncClient) -> None:
    create = await client.post(
        "/api/v1/contracts/review",
        json={"contract_text": "Sample contract for signing."},
    )
    review_id = create.json()["id"]

    sign = await client.post(
        f"/api/v1/contracts/reviews/{review_id}/sign",
        json={
            "signer_email": "alice@example.com",
            "signer_name": "Alice Smith",
            "subject": "Please sign",
        },
    )
    assert sign.status_code == 201
    data = sign.json()
    assert data["envelope_id"].startswith("stub-")
    assert data["signature_status"] == "sent"

    fetched = await client.get(f"/api/v1/contracts/reviews/{review_id}")
    assert fetched.json()["envelope_id"] == data["envelope_id"]
    assert fetched.json()["signer_email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_signature_webhook_updates_status(client: AsyncClient) -> None:
    create = await client.post(
        "/api/v1/contracts/review",
        json={"contract_text": "Contract for webhook test."},
    )
    review_id = create.json()["id"]
    sign = await client.post(
        f"/api/v1/contracts/reviews/{review_id}/sign",
        json={"signer_email": "bob@example.com", "signer_name": "Bob"},
    )
    envelope_id = sign.json()["envelope_id"]

    webhook = await client.post(
        "/api/v1/signatures/webhook",
        json={"envelopeId": envelope_id, "status": "completed"},
    )
    assert webhook.status_code == 204

    fetched = await client.get(f"/api/v1/contracts/reviews/{review_id}")
    assert fetched.json()["signature_status"] == "signed"


@pytest.mark.asyncio
async def test_send_for_signature_invalid_email(client: AsyncClient) -> None:
    create = await client.post(
        "/api/v1/contracts/review",
        json={"contract_text": "Sample contract."},
    )
    review_id = create.json()["id"]
    response = await client.post(
        f"/api/v1/contracts/reviews/{review_id}/sign",
        json={"signer_email": "not-an-email", "signer_name": "X"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_webhook_unknown_envelope_silent_204(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/signatures/webhook",
        json={"envelopeId": "stub-does-not-exist", "status": "sent"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_send_for_signature_unknown_review_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/contracts/reviews/00000000-0000-0000-0000-000000000000/sign",
        json={"signer_email": "x@example.com", "signer_name": "X"},
    )
    assert response.status_code == 404
