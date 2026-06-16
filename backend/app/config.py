from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/osint_db"
    redis_url: str = "redis://localhost:6379/0"
    nmap_path: str = "nmap"
    nmap_top_ports: int = 100
    port_scan_enabled: bool = True
    secret_key: str = "change-me-in-production"
    upload_dir: str = "uploads"
    reports_dir: str = "reports"
    max_upload_size_mb: int = 50
    allowed_origins: str = "http://localhost:3000"
    rate_limit_max: int = 5
    rate_limit_window_seconds: int = 600

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
