import io

import anyio

from app.core.docx_parser import parse_docx_to_markdown
from app.core.pdf_parser import parse_pdf_to_markdown


class UnsupportedFormatError(Exception):
    """Excepción personalizada para formatos no soportados."""

    # Eliminamos el 'pass' redundante


async def convert_file_to_markdown(filename: str, file_content: bytes) -> str:
    """
    Orquesta la conversión evaluando la extensión del archivo.

    El parsing es CPU-bound (pypdf / python-docx): se ejecuta en un thread
    del pool para no bloquear el event loop mientras se convierte.
    """
    file_stream = io.BytesIO(file_content)
    lower_filename = filename.lower()

    if lower_filename.endswith(".pdf"):
        return await anyio.to_thread.run_sync(parse_pdf_to_markdown, file_stream)

    if lower_filename.endswith(".docx"):
        return await anyio.to_thread.run_sync(parse_docx_to_markdown, file_stream)

    raise UnsupportedFormatError(f"Formato no soportado: {filename}. Usa .pdf o .docx.")
