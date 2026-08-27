"""Tests de la API de ToMarkdown (endpoint de conversión)."""

import io
from pathlib import Path

import pytest
from docx import Document
from httpx import AsyncClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_FILE_SIZE = 10 * 1024 * 1024


def _make_sample_docx() -> bytes:
    """Genera un DOCX válido en memoria con un encabezado y un párrafo."""
    buffer = io.BytesIO()
    doc = Document()
    doc.add_heading("Titulo de Prueba", level=1)
    doc.add_paragraph("Parrafo de ejemplo.")
    doc.save(buffer)
    return buffer.getvalue()


@pytest.mark.anyio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


@pytest.mark.anyio
async def test_convert_docx_happy_path(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/convert",
        files={"file": ("ejemplo.docx", _make_sample_docx(), DOCX_MIME)},
    )

    assert response.status_code == 200
    assert "# Titulo de Prueba" in response.json()["markdown"]


@pytest.mark.anyio
async def test_convert_pdf_happy_path(client: AsyncClient) -> None:
    pdf_bytes = (FIXTURES_DIR / "sample.pdf").read_bytes()
    response = await client.post(
        "/api/v1/convert",
        files={"file": ("sample.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    assert "Hola ToMarkdown" in response.json()["markdown"]


@pytest.mark.anyio
async def test_convert_unsupported_format(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/convert",
        files={"file": ("archivo.txt", b"hola", "text/plain")},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_convert_rejects_file_over_10mb(client: AsyncClient) -> None:
    oversized = b"x" * (MAX_FILE_SIZE + 1)  # 10 MB + 1 byte
    response = await client.post(
        "/api/v1/convert",
        files={"file": ("grande.pdf", oversized, "application/pdf")},
    )

    assert response.status_code == 413


@pytest.mark.anyio
async def test_rate_limit_returns_429(client: AsyncClient) -> None:
    pdf_bytes = (FIXTURES_DIR / "sample.pdf").read_bytes()
    files = {"file": ("sample.pdf", pdf_bytes, "application/pdf")}

    # Las 10 primeras conversiones del minuto pasan…
    for _ in range(10):
        response = await client.post("/api/v1/convert", files=files)
        assert response.status_code == 200

    # …la 11ª supera el límite (10/minute) y responde 429.
    response = await client.post("/api/v1/convert", files=files)
    assert response.status_code == 429
