import re

with open("backend/routes/assets.py", "r", encoding="utf-8") as f:
    content = f.read()

new_imports = """
from pydantic import BaseModel
from models.video_template import VideoTemplate
from models.project import Project

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None
    usage_count: Optional[int] = None
"""

content = content.replace("router = APIRouter(prefix=\"/assets\", tags=[\"assets\"])", new_imports + "\nrouter = APIRouter(prefix=\"/assets\", tags=[\"assets\"])")

upload_old = """        saved_info = await asset_manager.save_upload(file, type, category or "")
        
        # Determine mime type fallback
        mime_type = file.content_type or "application/octet-stream"
        
        new_asset = Asset(
            id=str(import_uuid()),
            name=file.filename,
            type=type,
            category=category or "",
            file_path=saved_info["file_path"],
            file_size=saved_info["file_size"],
            mime_type=mime_type
        )
        db.add(new_asset)
        uploaded_assets.append(new_asset)"""

upload_new = """        saved_info = await asset_manager.save_upload(file, type, category or "")
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
        uploaded_assets.append(new_asset)"""

content = content.replace(upload_old, upload_new)

extra_routes = """
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
"""

content = content + extra_routes

with open("backend/routes/assets.py", "w", encoding="utf-8") as f:
    f.write(content)
