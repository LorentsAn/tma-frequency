from functools import cache
from typing import Annotated

from pydantic import AfterValidator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    pg_dsn: Annotated[PostgresDsn, AfterValidator(str)] = (
        "postgresql://postgres:1234@localhost/postgres"
    )


@cache
def get_settings():
    return Settings()


settings = get_settings()
