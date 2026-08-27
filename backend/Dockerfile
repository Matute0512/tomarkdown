# ToMarkdown API — imagen de producción
# Backend FastAPI gestionado con uv (Python 3.12), procesamiento 100% en memoria.

FROM python:3.12-slim

# Binario de uv desde la imagen oficial de astral-sh (versión fija para builds reproducibles)
COPY --from=ghcr.io/astral-sh/uv:0.12.6 /uv /uvx /bin/

WORKDIR /app

# Dependencias primero (aprovecha la cache de capas de Docker)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Luego el código fuente
COPY . .

EXPOSE 8000

# Configurable en runtime: CORS_ORIGINS (lista separada por comas)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
