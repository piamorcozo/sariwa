from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # sqlite = default for hosting / local demo. Set DATABASE_BACKEND=mysql to use MySQL.
    database_backend: str = "sqlite"
    sqlite_path: str = "sariwa.sqlite3"

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "sariwa"
    secret_key: str = "sariwa-dev-secret-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "http://localhost:4200,http://127.0.0.1:4200"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def uses_sqlite(self) -> bool:
        return self.database_backend.strip().lower() != "mysql"

    @property
    def sqlite_file(self) -> Path:
        path = Path(self.sqlite_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[1] / path
        return path

    @property
    def mysql_url(self) -> str:
        password = self.mysql_password or ""
        auth = self.mysql_user if not password else f"{self.mysql_user}:{password}"
        return (
            f"mysql+pymysql://{auth}@{self.mysql_host}:{self.mysql_port}/"
            f"{self.mysql_database}?charset=utf8mb4"
        )

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.sqlite_file}"

    @property
    def database_url(self) -> str:
        return self.sqlite_url if self.uses_sqlite else self.mysql_url

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
