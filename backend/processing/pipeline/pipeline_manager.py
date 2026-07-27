"""
AUTOMA Processing Engine - Pipeline Manager.

Maintains a modular Node-based editing pipeline.
Each node only appends its parameters and descriptions to the execution plan.
The final node compiles and executes everything using the FFmpegPlugin.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional

from plugins.ffmpeg import FFmpegPlugin

logger = logging.getLogger("automa.processing.pipeline")


class BaseNode(ABC):
    """Abstract class representing a single processing node in the pipeline."""

    @property
    @abstractmethod
    def node_type(self) -> str:
        """The node identifier name (e.g., 'crop', 'zoom')."""
        pass

    @abstractmethod
    async def execute(self, input_path: Path, output_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Path:
        """Appends node configuration to context for compiled rendering."""
        pass


class ImportNode(BaseNode):
    """Import Node. Sets input path and starts the pipeline plan."""

    @property
    def node_type(self) -> str:
        return "import"

    async def execute(self, input_path: Path, output_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Path:
        logger.info(f"[Pipeline] Registering input: {input_path}")
        context["input_path"] = input_path
        context["nodes"] = []
        return input_path


# --- Export/Final Node ---

class NodeFactory:
    @staticmethod
    def create_standard_node(ntype: str) -> BaseNode:
        class StandardNode(BaseNode):
            @property
            def node_type(self) -> str:
                return ntype

            async def execute(self, input_path: Path, output_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Path:
                context["nodes"].append({"type": self.node_type, "config": config})
                return input_path
        return StandardNode()

class ExportNode(BaseNode):
    """Export Node. Compiles and executes the full FFmpeg command."""

    def __init__(self, ffmpeg_plugin: FFmpegPlugin) -> None:
        self.plugin = ffmpeg_plugin

    @property
    def node_type(self) -> str:
        return "export"

    async def execute(self, input_path: Path, output_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Path:
        logger.info(f"[Pipeline] Compiling and rendering execution plan to {output_path}")
        
        # Append export parameters description
        context["nodes"].append({"type": self.node_type, "config": config})
        
        # Pull parameters from context
        nodes_list = context.get("nodes", [])
        video_duration = float(context.get("video_duration", 0.0))
        
        # Handle time slicing for custom previews
        start_time = float(context.get("start_time", 0.0))
        duration_limit = float(context.get("duration_limit", 0.0))
        
        pid_cb = context.get("pid_callback")
        progress_cb = context.get("progress_callback")
        
        # Call FFmpegPlugin render pipeline
        return await self.plugin.render_pipeline(
            input_path=context["input_path"],
            output_path=output_path,
            nodes=nodes_list,
            video_duration=video_duration,
            start_time=start_time,
            duration_limit=duration_limit,
            pid_callback=pid_cb,
            progress_callback=progress_cb
        )


class PipelineManager:
    """Manages Node execution sequences and resolves parameters."""

    def __init__(self) -> None:
        self.ffmpeg_plugin = FFmpegPlugin()
        
        # Initialize registries
        self._node_classes: Dict[str, BaseNode] = {
            "import": ImportNode(),
            "export": ExportNode(self.ffmpeg_plugin)
        }
        
        standard_types = [
            "crop", "resize", "scale", "zoom", "rotate", "mirror",
            "brightness", "contrast", "saturation", "sharpness", "noisereduction",
            "framerate", "bitrate", "codec", "audiovolume", "audiofadein", 
            "audiofadeout", "metadatacleaner"
        ]
        for t in standard_types:
            self._node_classes[t] = NodeFactory.create_standard_node(t)
        
        # Try importing and registering SubtitleNode dynamically to avoid circular imports 
        # or load directly if it's available.
        try:
            from processing.pipeline.nodes.subtitle import SubtitleNode
            self._node_classes["subtitle"] = SubtitleNode()
        except ImportError as e:
            logger.warning(f"Failed to import SubtitleNode: {e}")

        try:
            from processing.pipeline.nodes.background import BackgroundNode
            self._node_classes["background"] = BackgroundNode()
        except ImportError as e:
            logger.warning(f"Failed to import BackgroundNode: {e}")


    def register_node(self, node: BaseNode) -> None:
        self._node_classes[node.node_type] = node

    async def execute_pipeline(
        self,
        input_file: Path,
        temp_dir: Path,
        nodes_config: List[Dict[str, Any]],
        context: Dict[str, Any],
        progress_callback: Optional[Callable[[float, float, float], Coroutine[Any, Any, None]]] = None,
    ) -> Path:
        """
        Runs the sequence of descriptive nodes.
        Delegates the execution of the completed filter plan to the ExportNode.
        """
        # Extract all nodes
        has_export = any(n.get("type") == "export" for n in nodes_config)
        has_import = any(n.get("type") == "import" for n in nodes_config)
        
        compiled_config = []
        if not has_import:
            compiled_config.append({"type": "import", "config": {}})
            
        # Reorder to ensure 'subtitle' is immediately after 'import'
        # 1. Get all import nodes
        # 2. Get all subtitle nodes
        # 3. Get the rest
        
        # We assume there's exactly 1 import if not has_import
        # If there's an import in nodes_config, let's just collect everything properly
        
        imports = [n for n in nodes_config if n.get("type") == "import"]
        subtitles = [n for n in nodes_config if n.get("type") == "subtitle"]
        exports = [n for n in nodes_config if n.get("type") == "export"]
        others = [n for n in nodes_config if n.get("type") not in ("import", "subtitle", "export")]
        
        if imports:
            compiled_config.extend(imports)
            
        if subtitles:
            compiled_config.extend(subtitles)
            
        compiled_config.extend(others)
        
        if exports:
            compiled_config.extend(exports)
        else:
            compiled_config.append({"type": "export", "config": {}})
            
        # Add callback hooks to context
        context["progress_callback"] = progress_callback
        
        # Inject export resolution to context so other nodes (like background) can use it
        export_node = next((n for n in exports), {})
        res = export_node.get("config", {}).get("resolution")
        if res:
            context["resolution"] = res
        
        current_file = input_file
        total_nodes = len(compiled_config)
        
        # Loop through all nodes except export to build execution description
        for index, node_spec in enumerate(compiled_config):
            node_type = node_spec.get("type", "unknown")
            node_config = node_spec.get("config", {})
            
            node = self._node_classes.get(node_type)
            if not node:
                logger.warning(f"Skipping unregistered node type: {node_type}")
                continue
                
            # Intermediate files are not written during intermediate stages!
            # We just pass the same file along and collect details.
            # Only the final ExportNode writes the real output file.
            stage_output = temp_dir / f"output_{input_file.name}"
            
            # Execute node
            current_file = await node.execute(current_file, stage_output, node_config, context)
            
        return current_file
