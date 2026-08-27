import io

import pymupdf
import pymupdf4llm


def parse_pdf_to_markdown(file_stream: io.BytesIO) -> str:
    """Convierte un PDF a Markdown con pymupdf4llm.

    Preserva tablas (formato GFM), orden de lectura y párrafos. Las fórmulas
    se conservan como glifos Unicode: pymupdf4llm no genera LaTeX.

    Se usa ``page_chunks=True`` para unir las páginas en un Markdown continuo
    y descartar los separadores de página que la librería inyecta por defecto.
    """
    data = file_stream.read()
    doc = pymupdf.open(stream=data, filetype="pdf")
    try:
        chunks = pymupdf4llm.to_markdown(doc, page_chunks=True)
        pages = [chunk["text"].strip() for chunk in chunks if chunk["text"].strip()]
        return "\n\n".join(pages)
    finally:
        doc.close()
