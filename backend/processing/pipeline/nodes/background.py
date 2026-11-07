import asyncio
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

        node_config = config
        if config.get("smart_fit"):
            node_config = await self._smart_fit(input_path, config, context)

        context["nodes"].append({"type": self.node_type, "config": node_config})
        return input_path

    async def _smart_fit(self, input_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect the useful region of the video (removing baked-in bars/templates) and the free
        area reserved by the template, so the compiler can fit the video proportionally inside it.
        Falls back to fitting the whole frame (no crop) when detection is not reliable.
        """
        from processing.analysis.smart_fit import analyze_video, detect_template_area, map_area_to_canvas

        node_config = dict(config)  # do not mutate the template stored in the database
        canvas_w, canvas_h = int(config["width"]), int(config["height"])

        manual = config.get("video_area")  # optional, already in canvas pixels
        area_px = None
        if manual:
            area_px = {k: int(manual[k]) for k in ("x", "y", "width", "height")}
        elif config.get("asset_path"):
            detected = await asyncio.to_thread(
                detect_template_area,
                Path(config["asset_path"]),
                int(config.get("area_margin_top", 40)),
                int(config.get("area_margin_bottom", 0)),
                int(config.get("area_margin_side", 0)),
            )
            if detected:
                area_px = map_area_to_canvas(detected, canvas_w, canvas_h)
        if not area_px or area_px["width"] < 16 or area_px["height"] < 16:
            area_px = {"x": 0, "y": 0, "width": canvas_w, "height": canvas_h}
        node_config["video_area_px"] = area_px

        # Generic aspect-ratio crops (no coordinates) would cut the footage blindly: smart fit replaces them.
        context["nodes"][:] = [
            n for n in context["nodes"]
            if not (n.get("type") == "crop" and "width" not in n.get("config", {}) and "aspect_ratio" in n.get("config", {}))
        ]

        source = Path(context.get("input_path", input_path))
        analysis = await asyncio.to_thread(analyze_video, source, float(context.get("video_duration", 0.0)))
        context["smart_fit"] = analysis.to_dict()
        if analysis.crop:
            x, y, w, h = analysis.crop
            # first node: crop the raw footage before subtitles/filters, then fit into the area
            context["nodes"].insert(0, {"type": "crop", "config": {"x": x, "y": y, "width": w, "height": h}})
        logger.info(f"[BackgroundNode] Smart fit: {analysis.to_dict()} area={area_px}")
        return node_config
