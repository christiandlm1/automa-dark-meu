from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models.asset import Asset
from processing.assets.asset_manager import AssetManager


from pydantic import BaseModel
from models.video_template import VideoTemplate
from models.project import Project

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None
    usage_count: Optional[int] = None

router = APIRouter(prefix="/assets", tags=["assets"])
asset_manager = AssetManager()

@router.get("/")
async def get_assets(type: Optional[str] = None, category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Asset)
    if type:
        query = query.where(Asset.type == type)
    if category:
        query = query.where(Asset.category == category)
    result = await db.execute(query)
    assets = result.scalars().all()
    return assets

@router.post("/upload")
async def upload_assets(
    files: List[UploadFile] = File(...),
    type: str = Form(...),
    category: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    uploaded_assets = []
    for file in files:
        saved_info = await asset_manager.save_upload(file, type, category or "")
        file_hash = saved_info.get("file_hash", "")
        
        # Check for duplicates using xxhash
        existing_result = await db.execute(select(Asset).where(Asset.file_hash == file_hash))
        existing_asset = existing_result.scalar_one_or_none()
        
        if existing_asset:
            # Delete the uploaded file since it's a duplicate
            asset_manager.delete_asset(saved_info["file_path"])
            # Returning existing asset is usually safer and transparent.
            uploaded_assets.append(existing_asset)
            continue
            
        # Determine mime type fallback
        mime_type = file.content_type or "application/octet-stream"
        
        new_asset = Asset(
            id=str(import_uuid()),
            name=file.filename,
            type=type,
            category=category or "",
            file_path=saved_info["file_path"],
            file_size=saved_info["file_size"],
            file_hash=file_hash,
            mime_type=mime_type,
            tags=[]
        )
        db.add(new_asset)
        uploaded_assets.append(new_asset)
    
    await db.commit()
    return uploaded_assets

@router.delete("/{asset_id}")
async def delete_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    asset_manager.delete_asset(asset.file_path)
    await db.delete(asset)
    await db.commit()
    return {"message": "Asset deleted successfully"}

def import_uuid():
    import uuid
    return uuid.uuid4()

@router.put("/{asset_id}")
async def update_asset(asset_id: str, payload: AssetUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    if payload.name is not None:
        asset.name = payload.name
    if payload.category is not None:
        asset.category = payload.category
    if payload.is_favorite is not None:
        asset.is_favorite = payload.is_favorite
    if payload.tags is not None:
        asset.tags = payload.tags
    if payload.usage_count is not None:
        asset.usage_count = payload.usage_count
        
    await db.commit()
    await db.refresh(asset)
    return asset

@router.get("/{asset_id}/usage")
async def get_asset_usage(asset_id: str, db: AsyncSession = Depends(get_db)):
    # Find all places where this asset is used
    # E.g. in video_templates pipeline config, or in projects
    
    # First get the asset to know its path/id
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    usage = {
        "templates": [],
        "projects": []
    }
    
    # Check templates
    templates_result = await db.execute(select(VideoTemplate))
    templates = templates_result.scalars().all()
    
    for t in templates:
        pipeline_str = str(t.pipeline_config)
        if asset.id in pipeline_str or asset.file_path in pipeline_str:
            usage["templates"].append({"id": t.id, "name": t.name})
            
    return usage
