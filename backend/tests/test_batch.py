"""Batch processing route tests."""

import asyncio
import io
import zipfile

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_batch_upload_creates_job(client: AsyncClient) -> None:
    files = [
        ("files", ("a.txt", b"Contract A. Indemnify everything.", "text/plain")),
        ("files", ("b.txt", b"Contract B. Standard terms.", "text/plain")),
    ]
    response = await client.post("/api/v1/legal/batch", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["total"] == 2
    assert data["status"] in {"pending", "processing", "completed"}
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_batch_upload_zip_extracts_members(client: AsyncClient) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("one.txt", "First contract.")
        zf.writestr("two.txt", "Second contract.")
    buf.seek(0)

    files = [("files", ("bundle.zip", buf.getvalue(), "application/zip"))]
    response = await client.post("/api/v1/legal/batch", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_batch_get_status(client: AsyncClient) -> None:
    files = [("files", ("c.txt", b"Sample contract for status test.", "text/plain"))]
    create = await client.post("/api/v1/legal/batch", files=files)
    job_id = create.json()["id"]

    # Give the background task a moment
    for _ in range(10):
        await asyncio.sleep(0.2)
        get_resp = await client.get(f"/api/v1/legal/batch/{job_id}")
        assert get_resp.status_code == 200
        if get_resp.json()["status"] not in {"pending", "processing"}:
            break

    final = await client.get(f"/api/v1/legal/batch/{job_id}")
    assert final.status_code == 200
    assert final.json()["id"] == job_id


@pytest.mark.asyncio
async def test_batch_empty_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/legal/batch",
        files=[("files", ("", b"", "application/octet-stream"))],
    )
    # FastAPI's UploadFile may accept empty filename — accept either client error
    assert response.status_code in {400, 422}


@pytest.mark.asyncio
async def test_batch_unknown_id_404(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/legal/batch/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
