import io

from docx import Document


def parse_docx_to_markdown(file_stream: io.BytesIO) -> str:
    """
    Toma un stream binario de un DOCX y mapea los estilos de párrafo
    básicos (Headings y Normal) a la sintaxis Markdown.
    """
    doc = Document(file_stream)
    markdown_lines = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Validación defensiva que pide Pylance:
        style = para.style
        if not style or not style.name:
            markdown_lines.append(f"{text}\n")
            continue

        style_name = style.name

        if style_name.startswith('Heading 1'):
            markdown_lines.append(f"# {text}\n")
        elif style_name.startswith('Heading 2'):
            markdown_lines.append(f"## {text}\n")
        elif style_name.startswith('Heading 3'):
            markdown_lines.append(f"### {text}\n")
        else:
            markdown_lines.append(f"{text}\n")

    return "\n".join(markdown_lines)
