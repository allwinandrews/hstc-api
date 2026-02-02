"""Application configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed settings with sensible local defaults."""

    # General
    app_name: str = "Hyperspace Tunneling Corp API"
    environment: str = "local"

    # Render typically provides DATABASE_URL (sync-style URL)
    database_url_raw: str | None = Field(default=None, alias="DATABASE_URL")

    # Local DB vars (still supported for docker-compose / local dev)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "hstc"
    db_user: str = "hstc"
    db_password: str = "hstc"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        """
        Build the SQLAlchemy async connection string.

        Priority:
        1) DATABASE_URL (Render)
        2) Individual DB_* vars (local/dev)

        Also normalize:
        - postgres:// -> postgresql://
        - postgresql:// -> postgresql+asyncpg://
        """
        if self.database_url_raw:
            url = self.database_url_raw.strip()

            # Normalize legacy prefix
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)

            # Ensure async driver
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

            return url

        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
