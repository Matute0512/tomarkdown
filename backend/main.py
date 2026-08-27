import os
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.conversion_service import (
    UnsupportedFormatError,
    convert_file_to_markdown,
)

app = FastAPI(
    title="ToMarkdown API",
    description="API ultrarrápida para convertir PDF/DOCX a Markdown en memoria.",
    version="1.0.0",
)


def _parse_cors_origins(raw: str | None) -> list[str]:
    """Convierte la variable CORS_ORIGINS (separada por comas) en una lista.

    Si la variable no está definida, usa los orígenes de desarrollo local.
    """
    if not raw:
        return ["http://localhost:3000", "http://192.168.182.1:3000"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS")),
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ConversionResponse(BaseModel):
    markdown: str


MAX_FILE_SIZE = 10 * 1024 * 1024


@app.post("/api/v1/convert", response_model=ConversionResponse)
async def convert_document(
    file: Annotated[UploadFile, File(description="Archivo a convertir")],
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo.")

    try:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, detail="El archivo excede el límite de 10MB."
            )

        markdown_text = await convert_file_to_markdown(file.filename, content)
        return ConversionResponse(markdown=markdown_text)

    except UnsupportedFormatError as e:
        raise HTTPException(status_code=422, detail=str(e))
    # Eliminamos el `except Exception` genérico.
    # FastAPI se encarga automáticamente de devolver un HTTP 500 si ocurre algo inesperado.


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
