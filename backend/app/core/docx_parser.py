"""Conversión de DOCX a Markdown respetando el orden del cuerpo del documento.

Camina ``doc.element.body`` en orden real para intercalar párrafos y tablas,
procesa los hijos de cada párrafo (runs, soft breaks, tabs) para no aplastar
el texto, y resuelve el estilo (headings, negrita, cursiva).
"""

import io
import re

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

_HEADING_MAX_LEVEL = 6


def parse_docx_to_markdown(file_stream: io.BytesIO) -> str:
    """Toma un stream binario de un DOCX y lo convierte a Markdown.

    Recorre el cuerpo del documento en orden real (``w:p`` y ``w:tbl``)
    para intercalar texto y tablas tal como aparecen en el original.
    """
    doc = Document(file_stream)
    blocks = []

    for child in doc.element.body:
        if child.tag == qn("w:p"):
            block = _paragraph_block(child, doc)
            if block:
                blocks.append(block)
        elif child.tag == qn("w:tbl"):
            table = Table(child, doc)
            block = _table_to_markdown(table)
            if block:
                blocks.append(block)
        # w:sectPr y demás nodos estructurales se ignoran.

    return _normalize_markdown("\n\n".join(blocks))


def _paragraph_block(p_element, doc: Document) -> str:
    """Devuelve un párrafo como bloque Markdown (heading o texto plano)."""
    para = Paragraph(p_element, doc)
    text = _paragraph_inline_markdown(p_element)
    text = re.sub(r"[ \t]+", " ", text).strip()
    if not text:
        return ""

    style = para.style
    style_name = style.name if style and style.name else ""
    if style_name.startswith("Heading "):
        level = style_name[len("Heading ") :].strip()
        if level.isdigit() and 1 <= int(level) <= _HEADING_MAX_LEVEL:
            return f"{'#' * int(level)} {text}"

    return text


def _paragraph_inline_markdown(container) -> str:
    """Concatena el contenido inline de un elemento (párrafo o hyperlink)."""
    return "".join(_inline_node_markdown(child) for child in container)


def _inline_node_markdown(node) -> str:
    """Traduce un hijo de párrafo: run (con negrita/cursiva), break o tab."""
    if node.tag == qn("w:r"):
        return _run_markdown(node)
    if node.tag == qn("w:hyperlink"):
        # El texto del enlace vive en runs anidados; recursión directa.
        return _paragraph_inline_markdown(node)
    if node.tag == qn("w:br"):
        # Soft break (Shift+Enter): deja de pegar el texto contiguo.
        return "\n"
    if node.tag == qn("w:tab"):
        return "\t"
    # w:pPr, m:oMath, bookmarks… no aportan texto en este paso.
    return ""


def _run_markdown(r_element) -> str:
    """Devuelve el texto de un ``w:r`` aplicando negrita y cursiva."""
    text = ""
    for child in r_element:
        if child.tag == qn("w:t"):
            text += child.text or ""
        elif child.tag == qn("w:br"):
            text += "\n"
        elif child.tag == qn("w:tab"):
            text += "\t"

    if not text:
        return ""

    rpr = r_element.find(qn("w:rPr"))
    bold = rpr is not None and rpr.find(qn("w:b")) is not None
    italic = rpr is not None and rpr.find(qn("w:i")) is not None
    if bold and italic:
        return f"***{text}***"
    if bold:
        return f"**{text}**"
    if italic:
        return f"*{text}*"
    return text


def _table_to_markdown(table: Table) -> str:
    """Convierte una tabla python-docx a Markdown GFM (encabezado + filas)."""
    if not table.rows:
        return ""

    header = [_cell_text(cell) for cell in table.rows[0].cells]
    lines = [
        f"| {' | '.join(header)} |",
        f"| {' | '.join(['---'] * len(header))} |",
    ]
    for row in table.rows[1:]:
        cells = [_cell_text(cell) for cell in row.cells]
        lines.append(f"| {' | '.join(cells)} |")
    return "\n".join(lines)


def _cell_text(cell) -> str:
    """Texto de celda seguro para una tabla GFM."""
    return (cell.text or "").replace("|", "\\|").replace("\n", "<br>").strip()


def _normalize_markdown(markdown: str) -> str:
    """Quita espacios al final de línea y limita las líneas en blanco a una."""
    out = []
    blank = 0
    for ln in markdown.splitlines():
        blank = blank + 1 if not ln else 0
        if blank <= 1:
            out.append(ln.rstrip())
    return "\n".join(out).strip()
