import os
import shutil
import uuid
import xxhash
from typing import List, Optional
from fastapi import UploadFile
from config import settings

class AssetManager:
    def __init__(self):
        # Default directory to save assets (.assets folder at the backend root or user directory)
        # Using a folder next to config or projects based on how AUTOMA paths are resolved.
        self.base_dir = os.path.join(os.getcwd(), ".assets")
        self._ensure_dir(self.base_dir)

    def _ensure_dir(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    async def compute_hash(self, file_path: str) -> str:
        """Compute xxhash of a file."""
        hasher = xxhash.xxh64()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    async def save_upload(self, upload_file: UploadFile, asset_type: str, category: str) -> dict:
        """
        Save the uploaded file to disk, organized by type and category.
        Returns dict with file_path, file_size, and file_hash.
        """
        # Create type/category folder structure
        target_dir = os.path.join(self.base_dir, asset_type)
        if category:
            target_dir = os.path.join(target_dir, category)
        self._ensure_dir(target_dir)

        # Generate a unique filename to avoid collisions
        file_ext = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        file_path = os.path.join(target_dir, unique_filename)
        
        hasher = xxhash.xxh64()
        file_size = 0
        with open(file_path, "wb") as f:
            while chunk := await upload_file.read(8192):
                f.write(chunk)
                hasher.update(chunk)
                file_size += len(chunk)
                
        file_hash = hasher.hexdigest()
        
        return {
            "file_path": file_path,
            "file_size": file_size,
            "file_hash": file_hash
        }

    def delete_asset(self, file_path: str) -> bool:
        """Delete an asset file from disk."""
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
