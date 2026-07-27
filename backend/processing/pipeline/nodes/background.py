import logging
from pathlib import Path
from typing import Any, Dict

from processing.pipeline.pipeline_manager import BaseNode
from database import async_session_maker
from models.asset import Asset
from sqlalchemy.future import select

logger = logging.getLogger("automa.processing.pipeline.nodes.background")

class BackgroundNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "background"

    async def execute(self, input_path: Path, output_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Path:
        asset_id = config.get("asset_id")
        if asset_id:
            try:
                async with async_session_maker() as session:
                    result = await session.execute(select(Asset).where(Asset.id == asset_id))
                    asset = result.scalar_one_or_none()
                    if asset:
                        # Append the resolved asset_path to config so compiler can use it
                        config["asset_path"] = asset.file_path
                        logger.info(f"[BackgroundNode] Resolved asset_id {asset_id} to {asset.file_path}")
                    else:
                        logger.warning(f"[BackgroundNode] Asset {asset_id} not found in database.")
            except Exception as e:
                logger.error(f"[BackgroundNode] Error resolving asset_id {asset_id}: {e}")

        # The FFmpegCompiler expects 'width' and 'height' for background scaling
        # If not provided in config, use context's export resolution
        res = context.get("resolution", "1080x1920")
        w, h = res.split("x")
        config.setdefault("width", int(w))
        config.setdefault("height", int(h))

        context["nodes"].append({"type": self.node_type, "config": config})
        return input_path
