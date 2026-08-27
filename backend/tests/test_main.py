"""Tests de la API de ToMarkdown (endpoint de conversión)."""

import io
from pathlib import Path

import pytest
from docx import Document
from httpx import AsyncClient
from pptx import Presentation

FIXTURES_DIR = Path(__file__).parent / "fixtures"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
MAX_FILE_SIZE = 10 * 1024 * 1024


def _make_sample_docx() -> bytes:
    """Genera un DOCX válido en memoria con un encabezado y un párrafo."""
    buffer = io.BytesIO()
    doc = Document()
    doc.add_heading("Titulo de Prueba", level=1)
    doc.add_paragraph("Parrafo de ejemplo.")
    doc.save(buffer)
    return buffer.getvalue()


def _make_sample_pptx() -> bytes:
    """Genera un PPTX válido en memoria con un título y una viñeta."""
    buffer = io.BytesIO()
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])  # Título y contenido
    slide.shapes.title.text_frame.text = "Diapositiva Uno"
    slide.placeholders[1].text_frame.text = "Punto de ejemplo"
    prs.save(buffer)
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
        files={"file": ("archivo.rtf", b"hola", "text/rtf")},
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
async def test_convert_pptx_happy_path(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/convert",
        files={"file": ("presentacion.pptx", _make_sample_pptx(), PPTX_MIME)},
    )

    assert response.status_code == 200
    markdown = response.json()["markdown"]
    assert "# Diapositiva Uno" in markdown
    assert "- Punto de ejemplo" in markdown


@pytest.mark.anyio
async def test_convert_txt_happy_path(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/convert",
        files={"file": ("notas.txt", b"Hola desde txt", "text/plain")},
    )

    assert response.status_code == 200
    assert "Hola desde txt" in response.json()["markdown"]


@pytest.mark.anyio
async def test_convert_txt_latin1_encoding(client: AsyncClient) -> None:
    # "Café" en Latin-1 no es UTF-8 válido → el parser hace fallback a Latin-1.
    latin1_bytes = "Café".encode("latin-1")
    response = await client.post(
        "/api/v1/convert",
        files={"file": ("cafe.txt", latin1_bytes, "text/plain")},
    )

    assert response.status_code == 200
    assert "Café" in response.json()["markdown"]


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
