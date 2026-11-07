import json
import zipfile
import shutil
import uuid
import xxhash
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import settings
from models.asset import Asset


# --- Template Export / Import ---

def export_template_to_file(template_data: dict, assets: Optional[Dict[str, str]] = None) -> Path:
    """
    Export a template and its referenced assets to a ZIP file.

    :param template_data: The dict containing template metadata and pipeline_config.
    :param assets: A dict mapping asset_id -> asset_file_path.
    :return: Path to the created .automa_template file.
    """
    export_dir = settings.EXPORTS_DIR / "templates"
    export_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in template_data.get("name", "template"))
    filename = f"{safe_name}_{timestamp}.automa_template"
    file_path = export_dir / filename

    with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Write the template JSON
        zipf.writestr("template.json", json.dumps(template_data, indent=4))

        # 2. Add assets
        if assets:
            for asset_id, asset_file_path in assets.items():
                p = Path(asset_file_path)
                if p.exists():
                    ext = p.suffix
                    zipf.write(str(p), f"assets/{asset_id}{ext}")

    return file_path


def _extract_safe(zipf: zipfile.ZipFile, item: str, extract_dir: Path) -> Path:
    """Safely extract a single file from a ZIP, preventing path traversal."""
    item = item.replace("\\", "/")
    if item.startswith("/") or ".." in item:
        raise ValueError(f"Unsafe path in archive: {item}")

    target_path = (extract_dir / item).resolve()
    extract_dir_resolved = extract_dir.resolve()
    # Verify target is inside extract_dir
    try:
        target_path.relative_to(extract_dir_resolved)
    except ValueError:
        raise ValueError(f"Unsafe path in archive: {item}")

    target_path.parent.mkdir(parents=True, exist_ok=True)

    with zipf.open(item) as source, open(target_path, "wb") as target:
        shutil.copyfileobj(source, target)

    return target_path


def import_template_from_file(
    file_path: Path,
    db: Optional[AsyncSession] = None
) -> dict:
    """
    Import a template from a .automa_template file.
    If the package contains bundled assets and a db session is provided,
    they are registered and the asset IDs in the pipeline are remapped.
    """
    if not file_path.exists() or not zipfile.is_zipfile(file_path):
        raise ValueError("Invalid template file")

    with zipfile.ZipFile(file_path, 'r') as zipf:
        if "template.json" not in zipf.namelist():
            raise ValueError("No template.json found in package")

        with zipf.open("template.json") as f:
            template_data = json.load(f)

        bundled_assets = [item for item in zipf.namelist() if item.startswith("assets/")]

        if bundled_assets:
            if db is None:
                raise ValueError("Importing templates with bundled assets requires a database session")

            extract_dir = settings.TEMP_DIR / "template_import"
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Extract all bundled assets safely
                for asset_item in bundled_assets:
                    _extract_safe(zipf, asset_item, extract_dir)

                # Remap asset IDs
                pipeline = template_data.get("pipeline_config", [])
                old_to_new: Dict[str, str] = {}

                for node in pipeline:
                    if node.get("type") == "background":
                        old_asset_id = node["config"].get("asset_id")
                        if not old_asset_id or old_asset_id in old_to_new:
                            continue

                        # Find the extracted file
                        asset_file = next(
                            (extract_dir / "assets" / item.split("/")[-1])
                            for item in bundled_assets
                            if old_asset_id in item
                        ), None)
                        if not asset_file or not asset_file.exists():
                            continue

                        # Register the asset
                        new_asset_id, _ = _register_asset(db, asset_file, old_asset_id)
                        old_to_new[old_asset_id] = new_asset_id

                # Update pipeline references
                for node in pipeline:
                    if node.get("type") == "background":
                        old_id = node["config"].get("asset_id")
                        if old_id and old_id in old_to_new:
                            node["config"]["asset_id"] = old_to_new[old_id]

                template_data["pipeline_config"] = pipeline

            finally:
                if extract_dir.exists():
                    shutil.rmtree(extract_dir, ignore_errors=True)

    return template_data


async def _register_asset(db: AsyncSession, source_path: Path, source_asset_id: str) -> tuple[str, dict]:
    """Register an extracted asset file into the database. Returns (asset_id, metadata)."""
    hasher = xxhash.xxh64()
    with open(source_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    file_hash = hasher.hexdigest()

    # Check for duplicate by hash
    result = await db.execute(select(Asset).where(Asset.file_hash == file_hash))
    existing = result.scalar_one_or_none()
    if existing:
        return existing.id, {
            "id": existing.id,
            "file_path": existing.file_path,
        }

    # Create a new asset
    asset_id = str(uuid.uuid4())
    ext = source_path.suffix
    target_dir = settings.ASSETS_DIR / "image_background"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{asset_id}{ext}"

    shutil.copy2(str(source_path), str(target_path))

    new_asset = Asset(
        id=asset_id,
        name=f"Imported Asset {source_asset_id[:8]}",
        type="image_background",
        category="imported",
        file_path=str(target_path),
        file_size=source_path.stat().st_size,
        mime_type=f"image/{ext.lstrip('.').lower() or 'png'}",
        file_hash=file_hash,
        tags=[],
        usage_count=0,
    )
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)

    return new_asset.id, {
        "id": new_asset.id,
        "file_path": new_asset.file_path,
    }
