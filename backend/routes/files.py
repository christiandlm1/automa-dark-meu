"""
AUTOMA Routes - Files
API route definitions for file system operations.
"""

from fastapi import APIRouter, Query

from controllers.file_controller import (
    CopyMoveRequest,
    FileController,
    VerifyRequest,
)

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/info")
async def get_file_info(
    path: str = Query(..., min_length=1),
    include_hash: bool = Query(False),
):
    """Retrieve details about a file (name, size, hash)."""
    controller = FileController()
    return await controller.get_info(path, include_hash=include_hash)


@router.post("/copy")
async def copy_file(data: CopyMoveRequest):
    """Copy a file (without deleting the source)."""
    controller = FileController()
    return await controller.copy(data)


@router.post("/move")
async def move_file(data: CopyMoveRequest):
    """Move a file from source to destination."""
    controller = FileController()
    return await controller.move(data)


@router.delete("")
async def delete_file(path: str = Query(..., min_length=1)):
    """Delete a file from disk."""
    controller = FileController()
    return await controller.delete(path)


@router.post("/directory")
async def create_directory(path: str = Query(..., min_length=1)):
    """Create a directory recursively."""
    controller = FileController()
    return await controller.create_directory(path)


@router.post("/verify")
async def verify_file(data: VerifyRequest):
    """Verify that a file's hash matches an expected value."""
    controller = FileController()
    return await controller.verify(data)


@router.get("/exists")
async def check_exists(path: str = Query(..., min_length=1)):
    """Check if a file or directory exists."""
    controller = FileController()
    return await controller.check_exists(path)
