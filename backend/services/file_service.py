"""
AUTOMA Services - File Service.

Business logic for filesystem operations: create, delete, copy, move,
and verify files and directories.  IO-bound work is offloaded to a
thread pool executor.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path

from utils.file_utils import (
    compute_file_hash,
    ensure_directory,
    get_file_size,
    is_valid_video_extension,
    safe_copy_file,
    safe_delete_file,
    safe_move_file,
    verify_directory_exists,
    verify_file_exists,
)


@dataclass
class FileInfo:
    """Container returned by file inspection methods."""

    path: str
    name: str
    extension: str
    size_bytes: int
    exists: bool
    is_video: bool
    hash: str | None = None


class FileService:
    """Async file management operations backed by thread pool executors."""

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    async def get_file_info(
        self, file_path: str, include_hash: bool = False
    ) -> FileInfo:
        """
        Gather information about a file on disk.

        Args:
            file_path: Absolute path to the file.
            include_hash: If True, compute the xxhash digest.

        Returns:
            Populated ``FileInfo`` dataclass.
        """
        loop = asyncio.get_running_loop()
        p = Path(file_path)

        exists = await loop.run_in_executor(None, verify_file_exists, file_path)

        size = 0
        if exists:
            size = await loop.run_in_executor(None, get_file_size, file_path)

        file_hash: str | None = None
        if exists and include_hash:
            file_hash = await loop.run_in_executor(
                None, compute_file_hash, file_path
            )

        return FileInfo(
            path=str(p),
            name=p.name,
            extension=p.suffix.lstrip(".").lower(),
            size_bytes=size,
            exists=exists,
            is_video=is_valid_video_extension(file_path),
            hash=file_hash,
        )

    # ------------------------------------------------------------------
    # Copy / Move / Delete
    # ------------------------------------------------------------------

    async def copy_file(self, source: str, destination: str) -> str:
        """Copy a file asynchronously. Returns the destination path."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, safe_copy_file, source, destination
        )

    async def move_file(self, source: str, destination: str) -> str:
        """Move a file asynchronously. Returns the destination path."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, safe_move_file, source, destination
        )

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file asynchronously. Returns True if removed."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, safe_delete_file, file_path
        )

    # ------------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------------

    async def create_directory(self, directory_path: str) -> str:
        """Create a directory (and parents). Returns the absolute path."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, ensure_directory, directory_path
        )

    async def directory_exists(self, directory_path: str) -> bool:
        """Check if a directory exists."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, verify_directory_exists, directory_path
        )

    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, verify_file_exists, file_path
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    async def verify_file_integrity(
        self, file_path: str, expected_hash: str
    ) -> bool:
        """
        Verify a file's integrity by comparing its hash to an expected value.

        Returns:
            True if the hashes match.
        """
        loop = asyncio.get_running_loop()
        if not await loop.run_in_executor(None, verify_file_exists, file_path):
            return False

        actual_hash = await loop.run_in_executor(
            None, compute_file_hash, file_path
        )
        return actual_hash == expected_hash
