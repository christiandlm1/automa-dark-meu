"""
AUTOMA Utils - Cache Manager.

Manages caching of metadata, thumbnails, previews, and temporary results.
Saves redundant processing by checking existing files inside settings.CACHE_DIR.
"""

import json
import logging
import shutil
from pathlib import Path

from config import settings

logger = logging.getLogger("automa.cache")


class CacheManager:
    """Manages system caching of media analysis and temporary files."""

    def __init__(self, cache_dir: Path = settings.CACHE_DIR) -> None:
        self.cache_dir = cache_dir
        self._ensure_subdirs()

    def _ensure_subdirs(self) -> None:
        """Create cache namespace subdirectories."""
        for subdir in ["metadata", "thumbnails", "previews", "temp"]:
            (self.cache_dir / subdir).mkdir(parents=True, exist_ok=True)

    def get_metadata(self, file_hash: str) -> dict | None:
        """Retrieve cached video metadata JSON using its file hash."""
        metadata_path = self.cache_dir / "metadata" / f"{file_hash}.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    logger.debug(f"Cache hit for metadata: {file_hash}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read cached metadata for {file_hash}: {e}")
        return None

    def set_metadata(self, file_hash: str, data: dict) -> None:
        """Save video metadata JSON to cache using its file hash."""
        metadata_path = self.cache_dir / "metadata" / f"{file_hash}.json"
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached metadata for: {file_hash}")
        except Exception as e:
            logger.error(f"Failed to write metadata cache for {file_hash}: {e}")

    def get_thumbnail(self, file_hash: str) -> Path | None:
        """Get the cached thumbnail path if it exists."""
        thumb_path = self.cache_dir / "thumbnails" / f"{file_hash}.jpg"
        if thumb_path.exists():
            logger.debug(f"Cache hit for thumbnail: {file_hash}")
            return thumb_path
        return None

    def set_thumbnail(self, file_hash: str, source_path: Path) -> Path | None:
        """Copy a generated thumbnail image to the cached thumbnails namespace."""
        dest_path = self.cache_dir / "thumbnails" / f"{file_hash}.jpg"
        try:
            shutil.copy2(source_path, dest_path)
            logger.debug(f"Cached thumbnail for: {file_hash}")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to cache thumbnail for {file_hash}: {e}")
            return None

    def get_preview(self, file_hash: str) -> Path | None:
        """Get the cached preview path if it exists."""
        preview_path = self.cache_dir / "previews" / f"{file_hash}.jpg"
        if preview_path.exists():
            return preview_path
        return None

    def set_preview(self, file_hash: str, source_path: Path) -> Path | None:
        """Copy a preview frame to cached previews namespace."""
        dest_path = self.cache_dir / "previews" / f"{file_hash}.jpg"
        try:
            shutil.copy2(source_path, dest_path)
            return dest_path
        except Exception as e:
            logger.error(f"Failed to cache preview for {file_hash}: {e}")
            return None

    def clear(self) -> None:
        """Clear all cached files."""
        try:
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._ensure_subdirs()
            logger.info("Cache cleared successfully.")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


# Global singleton instance
cache_manager = CacheManager()
