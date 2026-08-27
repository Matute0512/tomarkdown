"""Conteo de tokens usando el encoding cl100k_base de tiktoken."""

from tiktoken import Encoding, get_encoding

# El encoding se carga una sola vez a nivel de módulo para mitigar el cold
# start: tiktoken descarga el archivo BPE en el primer uso y lo cachea.
_ENCODING: Encoding = get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Devuelve cuántos tokens consumiría el texto en el modelo."""
    return len(_ENCODING.encode(text))
