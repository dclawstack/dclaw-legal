"""Contract comparison route tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_compare_identical_texts(client: AsyncClient) -> None:
    text = "Section 1. Term.\nThis Agreement begins on the Effective Date.\n"
    response = await client.post(
        "/api/v1/legal/compare",
        json={"text_a": text, "text_b": text},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["added"] == 0
    assert data["summary"]["removed"] == 0
    assert data["summary"]["modified"] == 0
    assert all(b["op"] == "equal" for b in data["blocks"])


@pytest.mark.asyncio
async def test_compare_with_addition(client: AsyncClient) -> None:
    a = "Line one\nLine two\n"
    b = "Line one\nLine two\nLine three\n"
    response = await client.post(
        "/api/v1/legal/compare",
        json={"text_a": a, "text_b": b, "label_a": "Old", "label_b": "New"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["added"] >= 1
    assert data["label_a"] == "Old"
    assert data["label_b"] == "New"


@pytest.mark.asyncio
async def test_compare_with_modification(client: AsyncClient) -> None:
    a = "Termination notice: 30 days.\n"
    b = "Termination notice: 60 days.\n"
    response = await client.post(
        "/api/v1/legal/compare",
        json={"text_a": a, "text_b": b},
    )
    assert response.status_code == 200
    data = response.json()
    ops = {b["op"] for b in data["blocks"]}
    assert "replace" in ops or ("insert" in ops and "delete" in ops)


@pytest.mark.asyncio
async def test_compare_empty_text_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/legal/compare",
        json={"text_a": "", "text_b": "something"},
    )
    assert response.status_code == 422
