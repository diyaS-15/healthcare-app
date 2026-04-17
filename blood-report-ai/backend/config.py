"""
Configuration & Settings
All environment variables loaded from .env
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging
from typing import List

class Settings(BaseSettings):
    # ── Supabase ──────────────────────────────────────────────
    supabase_url: str
    supabase_service_key: str
    supabase_anon_key: str
    supabase_jwt_secret: str  # For JWT verification
    

    # ── OpenAI ────────────────────────────────────────────────
    openai_api_key: str

    # ── ElevenLabs ────────────────────────────────────────────
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice

    # ── Encryption ────────────────────────────────────────────
    # A 64-character hex string (32 bytes) for AES-256
    encryption_secret: str

    # ── JWT / Auth ────────────────────────────────────────────
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours

    # ── App Settings ──────────────────────────────────────────
    app_env: str = "development"
    app_name: str = "Blood Report AI"
    app_version: str = "2.0.0"
    
    allowed_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000"
    max_upload_size_mb: int = 20

    # ── Database ──────────────────────────────────────────────
    db_max_connections: int = 5

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Logging ───────────────────────────────────────────────
    log_level: str = "INFO"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def origins_list(self) -> List[str]:
        """Parse origins from comma-separated string."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Parse allowed hosts (without http:// scheme) for TrustedHostMiddleware."""
        hosts = []
        for origin in self.origins_list:
            # Remove http:// or https:// and port if present
            host = origin.replace("http://", "").replace("https://", "")
            host = host.split(":")[0].strip()  # Remove port
            if host:
                hosts.append(host)
        return hosts

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings singleton."""
    return Settings()


# ── Logging Configuration ────────────────────────────────────

def setup_logging():
    """Configure structured logging."""
    settings = get_settings()
    level = getattr(logging, settings.log_level)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger(__name__)
