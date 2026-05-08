"""Contract review router tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_reviews_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/contracts/reviews")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_review(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/contracts/review",
        json={"title": "Test Contract", "contract_text": "This agreement governs the terms..."},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Contract"
    assert data["status"] == "completed"
    assert isinstance(data["risk_score"], int)


@pytest.mark.asyncio
async def test_get_review(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/v1/contracts/review",
        json={"contract_text": "Party A agrees to indemnify Party B..."},
    )
    rid = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/contracts/reviews/{rid}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == rid


@pytest.mark.asyncio
async def test_delete_review(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/v1/contracts/review",
        json={"contract_text": "Sample contract text for deletion."},
    )
    rid = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/contracts/reviews/{rid}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/contracts/reviews/{rid}")
    assert get_resp.status_code == 404
