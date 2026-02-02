"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed settings with sensible local defaults."""
    # General
    app_name: str = "Hyperspace Tunneling Corp API"
    environment: str = "local"

    # Database (Postgres)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "hstc"
    db_user: str = "hstc"
    db_password: str = "hstc"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy async connection string from settings."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
