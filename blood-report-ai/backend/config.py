"""
Configuration & Settings
All environment variables loaded from .env
"""

from dataclasses import dataclass
from functools import lru_cache
import logging
import os
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover - optional dependency
    BaseSettings = None


@dataclass
class _SettingsFallback:
    supabase_url: str
    supabase_service_key: str
    supabase_anon_key: str
    supabase_jwt_secret: str
    openai_api_key: str
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    encryption_secret: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    app_env: str = "development"
    app_name: str = "Blood Report AI"
    app_version: str = "2.0.0"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000"
    max_upload_size_mb: int = 20
    db_max_connections: int = 5
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"

    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def allowed_hosts_list(self) -> List[str]:
        hosts = []
        for origin in self.origins_list:
            host = origin.replace("http://", "").replace("https://", "")
            host = host.split(":")[0].strip()
            if host:
                hosts.append(host)
        return hosts

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


if BaseSettings is not None:
    class Settings(BaseSettings):
        supabase_url: str
        supabase_service_key: str
        supabase_anon_key: str
        supabase_jwt_secret: str
        openai_api_key: str
        elevenlabs_api_key: str = ""
        elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
        encryption_secret: str = ""
        jwt_secret: str = ""
        jwt_algorithm: str = "HS256"
        jwt_expire_minutes: int = 60 * 24
        app_env: str = "development"
        app_name: str = "Blood Report AI"
        app_version: str = "2.0.0"
        allowed_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000"
        max_upload_size_mb: int = 20
        db_max_connections: int = 5
        redis_url: str = "redis://localhost:6379/0"
        log_level: str = "INFO"

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False

        @property
        def origins_list(self) -> List[str]:
            return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

        @property
        def allowed_hosts_list(self) -> List[str]:
            hosts = []
            for origin in self.origins_list:
                host = origin.replace("http://", "").replace("https://", "")
                host = host.split(":")[0].strip()
                if host:
                    hosts.append(host)
            return hosts

        @property
        def is_production(self) -> bool:
            return self.app_env.lower() == "production"

        @property
        def is_development(self) -> bool:
            return self.app_env.lower() == "development"
else:
    Settings = _SettingsFallback


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings singleton."""
    if BaseSettings is not None:
        return Settings()

    return Settings(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        encryption_secret=os.getenv("ENCRYPTION_SECRET", ""),
        jwt_secret=os.getenv("JWT_SECRET", ""),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "1440")),
        app_env=os.getenv("APP_ENV", "development"),
        app_name=os.getenv("APP_NAME", "Blood Report AI"),
        app_version=os.getenv("APP_VERSION", "2.0.0"),
        allowed_origins=os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000",
        ),
        max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "20")),
        db_max_connections=int(os.getenv("DB_MAX_CONNECTIONS", "5")),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


def setup_logging():
    """Configure structured logging."""
    settings = get_settings()
    level = getattr(logging, settings.log_level, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    return logging.getLogger(__name__)
