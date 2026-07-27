"""
AUTOMA Utils - File Utilities.

Helpers for file hashing (xxhash), extension validation, copying, moving,
deleting, and directory management.  CPU-bound work (hashing) is designed
to be called via ``asyncio.to_thread`` or an executor from the service layer.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

import xxhash

from config import settings


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def compute_file_hash(file_path: str, chunk_size: int = 1 << 20) -> str:
    """
    Compute an xxhash-based hex digest for a file.

    This is a CPU-bound / IO-bound operation and should be run in a
    thread pool executor when called from async code.

    Args:
        file_path: Absolute path to the file.
        chunk_size: Read buffer size in bytes (default 1 MiB).

    Returns:
        Hex string of the xxh64 hash.
    """
    hasher = xxhash.xxh64()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


# ---------------------------------------------------------------------------
# Extension helpers
# ---------------------------------------------------------------------------

def get_file_extension(file_path: str) -> str:
    """Return the lowercase extension with the leading dot."""
    return Path(file_path).suffix.lower()


def is_valid_video_extension(file_path: str) -> bool:
    """Check whether the file has an allowed video extension."""
    ext = get_file_extension(file_path)
    return ext in settings.ALLOWED_VIDEO_EXTENSIONS


# ---------------------------------------------------------------------------
# Size
# ---------------------------------------------------------------------------

def get_file_size(file_path: str) -> int:
    """Return file size in bytes. Raises FileNotFoundError if missing."""
    return os.path.getsize(file_path)


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def safe_copy_file(source: str, destination: str) -> str:
    """
    Copy a file, creating parent directories as needed.

    Returns:
        The destination path.
    """
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(dest_path)


def safe_move_file(source: str, destination: str) -> str:
    """
    Move a file, creating parent directories as needed.

    Returns:
        The destination path.
    """
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source, destination)
    return str(dest_path)


def safe_delete_file(file_path: str) -> bool:
    """
    Delete a file if it exists.

    Returns:
        True if the file was deleted, False if it didn't exist.
    """
    path = Path(file_path)
    if path.exists() and path.is_file():
        path.unlink()
        return True
    return False


# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------

def ensure_directory(directory_path: str) -> str:
    """
    Create a directory (and parents) if it does not exist.

    Returns:
        The absolute directory path.
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve())


def verify_file_exists(file_path: str) -> bool:
    """Return True if the given path points to an existing file."""
    return Path(file_path).is_file()


def verify_directory_exists(directory_path: str) -> bool:
    """Return True if the given path points to an existing directory."""
    return Path(directory_path).is_dir()
