import io

from app.core.docx_parser import parse_docx_to_markdown
from app.core.pdf_parser import parse_pdf_to_markdown


class UnsupportedFormatError(Exception):
    """Excepción personalizada para formatos no soportados."""

    # Eliminamos el 'pass' redundante


async def convert_file_to_markdown(filename: str, file_content: bytes) -> str:
    """
    Orquesta la conversión evaluando la extensión del archivo.
    """
    file_stream = io.BytesIO(file_content)
    lower_filename = filename.lower()

    if lower_filename.endswith(".pdf"):
        return parse_pdf_to_markdown(file_stream)

    if lower_filename.endswith(".docx"):
        return parse_docx_to_markdown(file_stream)

    raise UnsupportedFormatError(f"Formato no soportado: {filename}. Usa .pdf o .docx.")
