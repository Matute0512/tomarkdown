"""Fixtures compartidos para los tests del backend."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
def anyio_backend() -> str:
    """Fuerza el backend asyncio en lugar de correr todos los disponibles."""
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Cliente HTTP asíncrono contra la app FastAPI (sin levantar un servidor)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
