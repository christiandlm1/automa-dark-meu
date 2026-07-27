import os
import asyncio
from pathlib import Path
from typing import Any, Dict

from processing.pipeline.pipeline_manager import BaseNode
from processing.subtitles.subtitle_manager import SubtitleManager
from plugins.subtitles.provider import DummyProvider

class SubtitleNode(BaseNode):
    """
    Subtitle Node.
    Ensures that the transcription exists (by using SubtitleManager) and appends
    the subtitle configuration (including the generated .srt path) to the context.
    """
    def __init__(self):
        # Instantiate the provider and manager.
        # In a real scenario, this could be injected via dependency injection.
        provider = DummyProvider()
        self.manager = SubtitleManager(provider=provider)

    @property
    def node_type(self) -> str:
        return "subtitle"

    async def execute(self, input_path: Path, output_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Path:
        # Request transcription. This will either return a cached .srt or generate a new one.
        language = config.get("language", "auto")
        srt_path = await self.manager.get_or_create_subtitle(str(input_path), language=language)
        
        # We store the resolved SRT path in the config so that the compiler can access it.
        config["srt_path"] = srt_path
        
        # Fetch SubtitlePreset if preset_id is provided
        preset_id = config.get("preset_id")
        if preset_id:
            from database import async_session_maker
            from models.subtitle_preset import SubtitlePreset
            from sqlalchemy import select
            
            async with async_session_maker() as session:
                stmt = select(SubtitlePreset).where(SubtitlePreset.id == preset_id)
                result = await session.execute(stmt)
                preset = result.scalar_one_or_none()
                if preset:
                    config["font_name"] = preset.font_name
                    config["font_size"] = preset.font_size
                    config["primary_color"] = preset.primary_color
                    config["outline_color"] = preset.outline_color
                    config["back_color"] = preset.back_color
                    config["margin_v"] = preset.margin_v
                    config["alignment"] = preset.alignment
                    
        context["nodes"].append({"type": self.node_type, "config": config})
        return input_path
