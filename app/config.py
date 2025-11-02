from functools import lru_cache
from pydantic import BaseSettings, Field, root_validator


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/fortaleza",
        description="SQLAlchemy database URL."
    )
    guardian_check_interval_hours: int = Field(
        default=6,
        description="Default number of hours between guardian mode safety checks.",
        ge=1,
    )
    guardian_min_check_interval_hours: int = Field(
        default=1,
        description="Minimum number of hours allowed between confirmations.",
        ge=1,
    )
    guardian_max_check_interval_hours: int = Field(
        default=24,
        description="Maximum number of hours allowed between confirmations.",
        ge=1,
    )

    @root_validator
    def _validate_guardian_intervals(cls, values: dict) -> dict:
        """Ensure guardian mode interval settings are coherent."""

        min_hours = values.get("guardian_min_check_interval_hours", 1)
        max_hours = values.get("guardian_max_check_interval_hours", min_hours)
        default_hours = values.get("guardian_check_interval_hours", min_hours)

        if max_hours < min_hours:
            raise ValueError(
                "guardian_max_check_interval_hours deve ser maior ou igual ao mínimo configurado"
            )

        if not (min_hours <= default_hours <= max_hours):
            raise ValueError(
                "guardian_check_interval_hours deve ficar dentro dos limites mínimo e máximo definidos"
            )

        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
