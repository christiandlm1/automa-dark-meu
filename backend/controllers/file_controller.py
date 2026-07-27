"""
AUTOMA Controllers - File Controller.

Thin controller that delegates to FileService.
"""

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from services.file_service import FileService


# Request schemas specific to file operations
class CopyMoveRequest(BaseModel):
    """Request body for copy/move operations."""
    source: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)


class VerifyRequest(BaseModel):
    """Request body for file integrity verification."""
    file_path: str = Field(..., min_length=1)
    expected_hash: str = Field(..., min_length=1)


class FileController:
    """Handles HTTP request/response translation for file endpoints."""

    def __init__(self) -> None:
        self.service = FileService()

    async def get_info(
        self, file_path: str, include_hash: bool = False
    ) -> dict:
        """Get file information."""
        info = await self.service.get_file_info(file_path, include_hash=include_hash)
        return {
            "path": info.path,
            "name": info.name,
            "extension": info.extension,
            "size_bytes": info.size_bytes,
            "exists": info.exists,
            "is_video": info.is_video,
            "hash": info.hash,
        }

    async def copy(self, data: CopyMoveRequest) -> dict[str, str]:
        """Copy a file."""
        if not await self.service.file_exists(data.source):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source file not found: {data.source}",
            )
        dest = await self.service.copy_file(data.source, data.destination)
        return {"detail": "File copied successfully", "destination": dest}

    async def move(self, data: CopyMoveRequest) -> dict[str, str]:
        """Move a file."""
        if not await self.service.file_exists(data.source):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source file not found: {data.source}",
            )
        dest = await self.service.move_file(data.source, data.destination)
        return {"detail": "File moved successfully", "destination": dest}

    async def delete(self, file_path: str) -> dict[str, str]:
        """Delete a file."""
        success = await self.service.delete_file(file_path)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}",
            )
        return {"detail": "File deleted successfully"}

    async def create_directory(self, directory_path: str) -> dict[str, str]:
        """Create a directory."""
        path = await self.service.create_directory(directory_path)
        return {"detail": "Directory created successfully", "path": path}

    async def verify(self, data: VerifyRequest) -> dict[str, bool]:
        """Verify file integrity."""
        is_valid = await self.service.verify_file_integrity(
            data.file_path, data.expected_hash
        )
        return {"valid": is_valid}

    async def check_exists(self, path: str) -> dict[str, bool]:
        """Check if a file or directory exists."""
        file_exists = await self.service.file_exists(path)
        dir_exists = await self.service.directory_exists(path)
        return {
            "exists": file_exists or dir_exists,
            "is_file": file_exists,
            "is_directory": dir_exists,
        }
