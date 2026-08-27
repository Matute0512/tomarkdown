"""Parser de texto plano (.txt) a Markdown."""


def parse_text_to_markdown(content: bytes) -> str:
    """Decodifica texto plano respetando su encoding y normaliza el Markdown.

    Intenta UTF-8 (con soporte de BOM) y, ante bytes no válidos, hace
    fallback a Latin-1, que nunca falla y cubre la mayoría de los textos
    Windows-1252.
    """
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    # Normalizamos CRLF / CR a LF para un Markdown consistente.
    return text.replace("\r\n", "\n").replace("\r", "\n")
