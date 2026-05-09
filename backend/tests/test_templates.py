"""Document template router tests."""

import pytest
from httpx import AsyncClient


_NDA_BODY = {
    "name": "Test NDA",
    "category": "NDA",
    "description": "Sample NDA for tests.",
    "template_text": "NDA between {{party_a}} and {{party_b}} dated {{date}}.",
    "variables": {
        "party_a": {"label": "Party A", "type": "text", "required": True},
        "party_b": {"label": "Party B", "type": "text", "required": True},
        "date": {"label": "Effective date", "type": "date", "required": True},
    },
}


@pytest.mark.asyncio
async def test_list_templates_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/templates")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_template(client: AsyncClient) -> None:
    response = await client.post("/api/v1/templates", json=_NDA_BODY)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test NDA"
    assert data["category"] == "NDA"
    assert "party_a" in data["variables"]


@pytest.mark.asyncio
async def test_get_template(client: AsyncClient) -> None:
    create_resp = await client.post("/api/v1/templates", json=_NDA_BODY)
    template_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/templates/{template_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == template_id


@pytest.mark.asyncio
async def test_generate_template_complete(client: AsyncClient) -> None:
    create_resp = await client.post("/api/v1/templates", json=_NDA_BODY)
    template_id = create_resp.json()["id"]

    gen_resp = await client.post(
        f"/api/v1/templates/{template_id}/generate",
        json={
            "values": {
                "party_a": "Acme Corp",
                "party_b": "Beta LLC",
                "date": "2026-05-09",
            }
        },
    )
    assert gen_resp.status_code == 200
    data = gen_resp.json()
    assert "Acme Corp" in data["rendered_text"]
    assert "Beta LLC" in data["rendered_text"]
    assert "{{" not in data["rendered_text"]
    assert data["missing_variables"] == []


@pytest.mark.asyncio
async def test_generate_template_missing_required(client: AsyncClient) -> None:
    create_resp = await client.post("/api/v1/templates", json=_NDA_BODY)
    template_id = create_resp.json()["id"]

    gen_resp = await client.post(
        f"/api/v1/templates/{template_id}/generate",
        json={"values": {"party_a": "Acme Corp"}},
    )
    assert gen_resp.status_code == 200
    data = gen_resp.json()
    assert "party_b" in data["missing_variables"]
    assert "date" in data["missing_variables"]


@pytest.mark.asyncio
async def test_delete_template(client: AsyncClient) -> None:
    create_resp = await client.post("/api/v1/templates", json=_NDA_BODY)
    template_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/templates/{template_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/templates/{template_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_generate_unknown_template_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/templates/00000000-0000-0000-0000-000000000000/generate",
        json={"values": {}},
    )
    assert response.status_code == 404
