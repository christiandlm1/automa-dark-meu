"""
AUTOMA Processing Engine - Export Manager.

Handles naming, folder structuring, and file organization of exported videos.
Organizes output files into: exports/[Projeto]/[Data]/[NomeDoVideo]
Decoupled and integrated with the EventBus.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from config import settings
from utils.event_bus import event_bus, EVENT_EXPORT_COMPLETED

logger = logging.getLogger("automa.processing.engine.export")


class ExportManager:
    """Manages file storage organization for finalized project videos."""

    def __init__(self, exports_dir: Path = settings.EXPORTS_DIR) -> None:
        self.exports_dir = exports_dir

    def get_export_path(self, project_name: str, video_name: str) -> Path:
        """
        Calculate and generate the export file path.
        Saves under: exports/[Projeto]/[Data]/[NomeDoVideo]
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Clean folder names (replace path separators to prevent folder breakout)
        clean_project = "".join(c for c in project_name if c.isalnum() or c in (" ", "_", "-")).strip()
        
        target_dir = self.exports_dir / clean_project / current_date
        target_dir.mkdir(parents=True, exist_ok=True)
        
        return target_dir / video_name

    async def export_video(self, source_path: Path, project_name: str, video_name: str) -> Path:
        """
        Copies the processed source video to the structured export directory.
        Fires the ExportCompleted event on completion.
        """
        dest_path = self.get_export_path(project_name, video_name)
        
        logger.info(f"Exporting processed video from {source_path} to {dest_path}")
        
        # Perform file copy
        loop = asyncio = False
        try:
            # We can execute file copy block in a separate thread if it is huge
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            logger.error(f"Failed to copy video to export destination: {e}")
            raise IOError(f"Falha ao salvar vídeo final na pasta de exportação: {e}")
            
        # Broadcast completed export event
        await event_bus.publish(EVENT_EXPORT_COMPLETED, project_name, dest_path)
        
        return dest_path
