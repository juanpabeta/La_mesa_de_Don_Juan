"""Configuración de la aplicación cargada desde variables de entorno."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Gestión de Pedidos para Restaurantes"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:JP1806@db:5432/restaurantes"
    secret_key: str = Field(default="iYjm68g3tM4RWau66jdqjhjvx-OsO7JT8XmdcMI3skg", min_length=32)
    jwt_algorithm: Literal["HS256"] = Field(
        default="HS256",
        validation_alias=AliasChoices("ALGORITHM", "JWT_ALGORITHM"),
    )
    access_token_minutes: int = Field(
        default=60,
        gt=0,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "ACCESS_TOKEN_MINUTES"),
    )
    auth_cookie_name: str = "access_token"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    enable_delay_monitor: bool = False
    db_pool_size: int = Field(default=5, gt=0, le=50)
    db_max_overflow: int = Field(default=10, ge=0, le=100)
    db_pool_timeout_seconds: int = Field(default=30, gt=0, le=300)

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Make Railway's generic PostgreSQL URL use the installed psycopg driver."""
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        production = self.app_env.strip().lower() in {"prod", "production"}
        if production:
            placeholder_markers = ("cambiar", "change-me", "changeme", "replace-me", "placeholder", "example")
            if (
                any(marker in self.secret_key.casefold() for marker in placeholder_markers)
                or len(set(self.secret_key)) < 8
            ):
                raise ValueError("SECRET_KEY debe configurarse explícitamente en producción")
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE debe ser true en producción")
            if self.database_url.startswith("sqlite") or "postgres:postgres@" in self.database_url:
                raise ValueError("DATABASE_URL debe apuntar a una base de datos productiva segura")
            local_hosts = {"localhost", "127.0.0.1", "::1"}
            parsed_origins = [urlparse(origin) for origin in self.cors_origins]
            if any(
                origin.scheme != "https"
                or not origin.netloc
                or origin.hostname in local_hosts
                or origin.path not in {"", "/"}
                or origin.query
                or origin.fragment
                for origin in parsed_origins
            ):
                raise ValueError("CORS_ORIGINS debe contener orígenes HTTPS públicos del despliegue")
            
        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError("COOKIE_SECURE debe ser true cuando COOKIE_SAMESITE=none")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
