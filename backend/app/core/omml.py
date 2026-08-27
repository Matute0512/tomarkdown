"""Conversor mínimo de OMML (Office Math Markup Language) a LaTeX.

OMML es el formato XML de las ecuaciones de Word 2007+ (elementos ``m:*``).
python-docx no los expone en ``paragraph.text``, así que este módulo traduce
los constructos más comunes a LaTeX y degrada a texto plano cualquier
constructo no soportado (nunca lanza).

Trabaja sobre elementos lxml con el namespace ``m`` de Office Math y no
depende de python-docx: recibe el elemento y devuelve un string.

Los mapas de símbolos se indexan por el codepoint en hexadecimal (``"2211"``)
en vez de por el carácter literal, para fijar el codepoint de forma
inequívoca en el código fuente.
"""

_M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

# Símbolos Unicode → comandos LaTeX, indexados por codepoint hex (sin 0x).
_MATH_CHARS = {
    "03b1": r"\alpha",  # α
    "03b2": r"\beta",  # β
    "03b3": r"\gamma",  # γ
    "03b4": r"\delta",  # δ
    "03b5": r"\epsilon",  # ε
    "03bb": r"\lambda",  # λ
    "03bc": r"\mu",  # μ
    "03c0": r"\pi",  # π
    "03c3": r"\sigma",  # σ
    "03c4": r"\tau",  # τ
    "03c6": r"\varphi",  # φ
    "03c9": r"\omega",  # ω
    "0393": r"\Gamma",  # Γ
    "0394": r"\Delta",  # Δ
    "0398": r"\Theta",  # Θ
    "039b": r"\Lambda",  # Λ
    "03a3": r"\Sigma",  # Σ
    "03a9": r"\Omega",  # Ω
    "221e": r"\infty",  # ∞
    "2264": r"\leq",  # ≤
    "2265": r"\geq",  # ≥
    "2260": r"\neq",  # ≠
    "00b1": r"\pm",  # ±
    "00d7": r"\times",  # ×
    "00f7": r"\div",  # ÷
    "22c5": r"\cdot",  # ⋅
    "2192": r"\rightarrow",  # →
    "2190": r"\leftarrow",  # ←
    "2208": r"\in",  # ∈
    "2205": r"\emptyset",  # ∅
    "2200": r"\forall",  # ∀
    "2203": r"\exists",  # ∃
    "2211": r"\sum",  # ∑
    "220f": r"\prod",  # ∏
    "222b": r"\int",  # ∫
    "221a": r"\sqrt",  # √
    "2202": r"\partial",  # ∂
    "2207": r"\nabla",  # ∇
    "2248": r"\approx",  # ≈
    "2261": r"\equiv",  # ≡
    "2282": r"\subset",  # ⊂
    "2286": r"\subseteq",  # ⊆
    "222a": r"\cup",  # ∪
    "2229": r"\cap",  # ∩
}

# Acentos (m:accPr → m:chr val) → comando LaTeX, por codepoint hex.
_ACCENTS = {
    "0302": r"\hat",  # circunflejo
    "0304": r"\bar",  # macron
    "0303": r"\tilde",  # tilde
    "20d7": r"\vec",  # flecha superior
    "0307": r"\dot",  # punto
    "0308": r"\ddot",  # diéresis
    "0301": r"\acute",  # agudo
    "0300": r"\grave",  # grave
}


def omml_to_latex(element) -> str:
    """Convierte un subárbol OMML (m:oMath, m:oMathPara o contenedor) a LaTeX."""
    return _convert(element)


def _convert(element) -> str:
    """Despacha por tag local y resuelve los hijos recursivamente."""
    local = _local_tag(element.tag)
    if local in {"oMathPara", "oMath", "box"}:
        return _inner(element)
    if local == "r":
        return _run_text(element)
    if local == "f":
        return _fraction(element)
    if local in {"sSub", "sSup", "sSubSup"}:
        # Tags OMML con S mayúscula: sSub, sSup, sSubSup.
        return _script(element, "Sub" in local, "Sup" in local)
    if local == "rad":
        return _radical(element)
    if local == "nary":
        return _nary(element)
    if local == "d":
        return _delimiters(element)
    if local == "acc":
        return _accent(element)
    if local == "func":
        return _function(element)
    # Constructos no soportados (matrices, ec. array…): degradan a texto plano.
    return _collect_text(element)


def _local_tag(tag: str) -> str:
    """' {ns}local ' → 'local'."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _q(local: str) -> str:
    """Tag Clark completo para un elemento ``m:*``."""
    return f"{{{_M_NS}}}{local}"


def _inner(container) -> str:
    """Concatena la conversión de los hijos de un contenedor OMML."""
    if container is None:
        return ""
    return "".join(_convert(child) for child in container)


def _run_text(r_element) -> str:
    """Texto de un run matemático (m:r) con los símbolos traducidos."""
    text = "".join(t.text or "" for t in r_element.iter(_q("t")))
    return _map_chars(text)


def _map_chars(text: str) -> str:
    """Aplica el mapa Unicode→LaTeX a un texto, conservando lo no mapeado."""
    return "".join(_MATH_CHARS.get(f"{ord(ch):04x}", ch) for ch in text)


def _fraction(f_element) -> str:
    num = _inner(f_element.find(_q("num")))
    den = _inner(f_element.find(_q("den")))
    return f"\\frac{{{num}}}{{{den}}}"


def _script(element, sub: bool, sup: bool) -> str:
    """Subíndice/superíndice (m:sSub, m:sSup, m:sSubSup)."""
    base = _inner(element.find(_q("e")))
    latex = f"{{{base}}}"
    if sub:
        latex += f"_{{{_inner(element.find(_q('sub')))}}}"
    if sup:
        latex += f"^{{{_inner(element.find(_q('sup')))}}}"
    return latex


def _radical(rad_element) -> str:
    base = _inner(rad_element.find(_q("e")))
    deg = rad_element.find(_q("deg"))
    if deg is not None and len(list(deg)):
        return f"\\sqrt[{_inner(deg)}]{{{base}}}"
    return f"\\sqrt{{{base}}}"


def _nary(nary_element) -> str:
    chr_el = nary_element.find(f"{_q('naryPr')}/{_q('chr')}")
    ch = chr_el.get(_q("val")) if chr_el is not None else None
    cmd = _map_chars(ch) if ch else r"\int"  # por defecto: integral
    sub = _inner(nary_element.find(_q("sub")))
    sup = _inner(nary_element.find(_q("sup")))
    body = _inner(nary_element.find(_q("e")))
    latex = cmd
    if sub or sup:
        latex += f"_{{{sub}}}^{{{sup}}}"
    return f"{latex} {body}"


def _delimiters(d_element) -> str:
    beg, end = "(", ")"
    pr = d_element.find(_q("dPr"))
    if pr is not None:
        beg_el = pr.find(_q("begChr"))
        end_el = pr.find(_q("endChr"))
        if beg_el is not None:
            beg = beg_el.get(_q("val")) or beg
        if end_el is not None:
            end = end_el.get(_q("val")) or end
    inner = _inner(d_element)
    return f"\\left{beg}{inner}\\right{end}"


def _accent(acc_element) -> str:
    chr_el = acc_element.find(f"{_q('accPr')}/{_q('chr')}")
    ch = chr_el.get(_q("val")) if chr_el is not None else None
    body = _inner(acc_element.find(_q("e")))
    if ch:
        cmd = _ACCENTS.get(f"{ord(ch):04x}")
        if cmd:
            return f"{cmd}{{{body}}}"
    return f"\\hat{{{body}}}"  # por defecto: circunflejo


def _function(func_element) -> str:
    name = _inner(func_element.find(_q("fName")))
    arg = _inner(func_element.find(_q("e")))
    return f"{name}({arg})"


def _collect_text(element) -> str:
    """Recolecta el texto de todos los m:t de un subárbol (fallback plano)."""
    return _map_chars("".join(t.text or "" for t in element.iter(_q("t"))))
