"""
AUTOMA Backend - Application Configuration
Centralized configuration using pydantic-settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application-wide configuration loaded from environment or defaults."""

    # --- Server ---
    APP_NAME: str = "AUTOMA"
    APP_VERSION: str = "1.0.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8420
    DEBUG: bool = False

    # --- Paths ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent  # AUTOMA root
    DATABASE_DIR: Path = BASE_DIR / "database"
    STORAGE_DIR: Path = BASE_DIR / "storage"
    PROJECTS_DIR: Path = BASE_DIR / "projects"
    LOGS_DIR: Path = BASE_DIR / "logs"
    CACHE_DIR: Path = BASE_DIR / "cache"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    TEMP_DIR: Path = BASE_DIR / "temp"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    THUMBNAILS_DIR: Path = BASE_DIR / "thumbnails"
    CONFIG_DIR: Path = BASE_DIR / "config"

    # --- Database ---
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'database' / 'automa.db'}"

    # --- Performance ---
    MAX_PROCESSES: int = 4
    MAX_CPU_USAGE: int = 80
    MAX_RAM_USAGE: int = 80
    MAX_GPU_USAGE: int = 80
    THUMBNAIL_WIDTH: int = 320
    THUMBNAIL_HEIGHT: int = 180
    THUMBNAIL_QUALITY: int = 85

    # --- Allowed file extensions ---
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

    # --- Hardware monitoring ---
    HARDWARE_MONITOR_INTERVAL: float = 2.0  # seconds

    class Config:
        env_prefix = "AUTOMA_"
        env_file = ".env"

    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        dirs = [
            self.DATABASE_DIR,
            self.STORAGE_DIR,
            self.PROJECTS_DIR,
            self.LOGS_DIR,
            self.CACHE_DIR,
            self.ASSETS_DIR,
            self.TEMP_DIR,
            self.EXPORTS_DIR,
            self.THUMBNAILS_DIR,
            self.CONFIG_DIR,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = AppConfig()
