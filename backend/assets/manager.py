"""
AUTOMA Assets - Asset Manager.

Organizes auxiliary resources like fonts, audios, overlays and watermarks.
Ensures assets subfolders are structured and ready for upcoming editing features.
"""

import logging
import shutil
from pathlib import Path
from typing import List

from config import settings

logger = logging.getLogger("automa.assets")


class AssetManager:
    """Manages system folders and registers design assets (fonts, logo, music, overlays)."""

    def __init__(self, assets_dir: Path = settings.ASSETS_DIR) -> None:
        self.assets_dir = assets_dir
        self._ensure_folders()

    def _ensure_folders(self) -> None:
        """Create structured asset subdirectories."""
        subdirs = ["fonts", "music", "sfx", "overlays", "logos", "images", "videos"]
        for d in subdirs:
            (self.assets_dir / d).mkdir(parents=True, exist_ok=True)

    def get_category_dir(self, category: str) -> Path:
        """Get directory path for a specific category namespace."""
        cat_map = {
            "fonts": "fonts",
            "music": "music",
            "sfx": "sfx",
            "audio": "music",
            "overlays": "overlays",
            "logos": "logos",
            "watermarks": "logos",
            "images": "images",
            "videos": "videos"
        }
        sub = cat_map.get(category.lower(), "images")
        return self.assets_dir / sub

    def register_asset(self, category: str, source_path: Path) -> Path:
        """Copy a design asset into the organized assets directory."""
        if not source_path.exists():
            raise FileNotFoundError(f"Source asset file not found: {source_path}")
            
        target_dir = self.get_category_dir(category)
        dest_path = target_dir / source_path.name
        
        shutil.copy2(source_path, dest_path)
        logger.info(f"Registered asset in category {category}: {dest_path}")
        return dest_path

    def list_assets(self, category: str) -> List[str]:
        """List filenames of all registered assets in a category."""
        target_dir = self.get_category_dir(category)
        if not target_dir.exists():
            return []
        return [f.name for f in target_dir.iterdir() if f.is_file()]

    def delete_asset(self, category: str, filename: str) -> bool:
        """Remove an asset file from the system folder."""
        target_dir = self.get_category_dir(category)
        target_file = target_dir / filename
        if target_file.exists():
            target_file.unlink()
            logger.info(f"Deleted asset {filename} from category {category}")
            return True
        return False


# Global singleton instance
asset_manager = AssetManager()
