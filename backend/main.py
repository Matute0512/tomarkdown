from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import settings
from app.services.conversion_service import (
    UnsupportedFormatError,
    convert_file_to_markdown,
)

app = FastAPI(
    title="ToMarkdown API",
    description="API ultrarrápida para convertir PDF/DOCX a Markdown en memoria.",
    version="1.0.0",
)

# Rate limiting por IP de cliente (key_func lee request.client.host).
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Responde 429 cuando el cliente supera el límite de conversiones."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas peticiones. Intenta de nuevo en un minuto."},
    )


class ConversionResponse(BaseModel):
    markdown: str


@app.post("/api/v1/convert", response_model=ConversionResponse)
@limiter.limit(settings.rate_limit)
async def convert_document(
    request: Request,
    file: Annotated[UploadFile, File(description="Archivo a convertir")],
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo.")

    try:
        content = await file.read()

        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=413, detail="El archivo excede el límite de 10MB."
            )

        markdown_text = await convert_file_to_markdown(file.filename, content)
        return ConversionResponse(markdown=markdown_text)

    except UnsupportedFormatError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/")
async def health_check():
    """
    Endpoint base para verificar que la API está funcionando.
    """
    return {
        "status": "online",
        "message": "ToMarkdown API is running",
        "docs_url": "/docs",
    }
