"""Settings loaded from environment variables."""

from urllib.parse import quote_plus
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "CatobiGato"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Database — catobigato dedicated role
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "catobigato"
    db_user: str = "catobigato"
    db_password: str  # required — set via .env or environment variable

    @property
    def database_url(self) -> str:
        # URL-encode password so special chars (e.g. !) don't break asyncpg
        pw = quote_plus(self.db_password)
        return f"postgresql+asyncpg://{self.db_user}:{pw}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def sync_database_url(self) -> str:
        pw = quote_plus(self.db_password)
        return f"postgresql://{self.db_user}:{pw}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Keycloak
    keycloak_url: str = "https://www.keytomarvel.com"
    keycloak_realm: str = "catobigato"
    keycloak_client_id: str = "catobigato"

    @property
    def keycloak_jwks_url(self) -> str:
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}/protocol/openid-connect/certs"

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8001"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()