from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from pydantic import ValidationError

from app.core.config import Settings


def test_production_settings_reject_placeholder_secrets_and_insecure_cookies() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            secret_key="cambiar-por-una-clave-aleatoria-segura-de-al-menos-32-caracteres",
            cookie_secure=True,
            cors_origins=["https://mesasync.example"],
        )

    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            secret_key="R4nd0m-But-Valid-Production-Key-2026!",
            cookie_secure=False,
            cors_origins=["https://mesasync.example"],
        )


def test_alembic_migrations_have_a_single_expected_head() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    script = ScriptDirectory.from_config(config)

    assert script.get_current_head() == "0003_auditable_deletions"
    latest = script.get_revision("0003_auditable_deletions")
    assert latest is not None
    assert latest.down_revision == "0002_usuario_ultimo_ingreso"
