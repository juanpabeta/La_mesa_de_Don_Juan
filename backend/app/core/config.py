"""Configuración centralizada de la aplicación."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de configuración cargadas exclusivamente desde el entorno."""

    app_name: str = "La mesa de Don Juan API"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    cookie_secure: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="")


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración singleton."""
    return Settings()
