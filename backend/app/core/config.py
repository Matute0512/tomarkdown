"""Configuración de la aplicación, tipada y validada con pydantic-settings.

Las variables de entorno (p. ej. CORS_ORIGINS, RATE_LIMIT) se leen de forma
automática y case-insensitive, con valores por defecto seguros para desarrollo.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno de la app → campos tipados con defaults."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Orígenes CORS permitidos, separados por comas.
    cors_origins: str = "http://localhost:3000,http://192.168.182.1:3000"
    # Límite de conversiones por minuto por cliente (sintaxis de `limits`).
    rate_limit: str = "10/minute"
    # Tamaño máximo de archivo en bytes (10 MB).
    max_file_size: int = 10 * 1024 * 1024

    @property
    def cors_origins_list(self) -> list[str]:
        """Lista de orígenes CORS a partir del campo `cors_origins`."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia única y cacheada de Settings."""
    return Settings()


settings = get_settings()
