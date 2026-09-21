from functools import lru_cache
from secrets import token_urlsafe
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Mawasilati API'
    api_v1_prefix: str = '/api/v1'
    database_url: str = 'postgresql+psycopg2://postgres:postgres@localhost:5432/mawasilati'
    database_pool_size: int = Field(default=20, ge=1, le=200)
    database_max_overflow: int = Field(default=20, ge=0, le=200)
    database_pool_timeout_seconds: int = Field(default=30, ge=1, le=120)
    database_pool_recycle_seconds: int = Field(default=1800, ge=60, le=86_400)
    redis_url: str = 'redis://localhost:6379/0'
    secret_key: str = Field(default_factory=lambda: token_urlsafe(48))
    access_token_expire_minutes: int = Field(default=30, ge=5, le=240)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)
    require_session_bound_tokens: bool = True
    trip_quote_ttl_minutes: int = Field(default=10, ge=1, le=60)
    require_signed_quotes_in_production: bool = True
    cors_origins: str = 'http://localhost:3000,http://localhost:8080'
    environment: Literal['development', 'test', 'staging', 'production'] = 'development'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]

    @model_validator(mode='after')
    def validate_production_contract(self):
        if self.environment == 'production':
            if 'secret_key' not in self.model_fields_set or len(self.secret_key) < 32:
                raise ValueError('Production requires an explicit SECRET_KEY of at least 32 characters')
            if self.database_url.startswith('sqlite'):
                raise ValueError('Production requires a server database, not SQLite')
            if not self.cors_origin_list() or '*' in self.cors_origin_list():
                raise ValueError('Production requires explicit CORS origins')
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
