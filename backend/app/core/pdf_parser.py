import io

from pypdf import PdfReader


def parse_pdf_to_markdown(file_stream: io.BytesIO) -> str:
    """Toma un stream binario de un PDF, extrae el texto por página
    y le da formato Markdown básico.

    Args:
        file_stream (io.BytesIO): _description_

    Returns:
        Str: _description_
    """
    reader = PdfReader(file_stream)
    markdown_lines = []

    for i, page in enumerate(reader.pages):
        # extra_text() puede devolver None si la página es solo una imagen
        text = page.extract_text()

        if text:
            # Agregamos un delimitador de página como encabezado H2
            markdown_lines.append(f"## Página {i + 1}\n\n{text.strip()}\n")

    return "\n".join(markdown_lines)
