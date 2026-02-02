"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_async_db_url(url: str) -> str:
    """
    Render provides DATABASE_URL like:
      postgresql://user:pass@host:5432/db

    SQLAlchemy async expects:
      postgresql+asyncpg://user:pass@host:5432/db
    """
    if not url:
        return url

    # Some providers use "postgres://" alias; normalize it too.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Convert sync URL to SQLAlchemy async URL (asyncpg)
    if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


class Settings(BaseSettings):
    """Strongly-typed settings with sensible local defaults."""

    # General
    app_name: str = "Hyperspace Tunneling Corp API"
    environment: str = "local"

    # Preferred on hosted platforms (Render/Heroku/etc.)
    # Render sets DATABASE_URL automatically if you link a Postgres instance,
    # or you can set it yourself in the Render dashboard.
    database_url: str | None = None

    # Database (local fallback)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "hstc"
    db_user: str = "hstc"
    db_password: str = "hstc"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Final SQLAlchemy async connection URL.

        Priority:
        1) DATABASE_URL (hosted envs)
        2) DB_* parts (local dev)
        """
        if self.database_url:
            return _normalize_async_db_url(self.database_url)

        # Local dev fallback
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
