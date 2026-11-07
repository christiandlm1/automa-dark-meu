"""
AUTOMA Plugins - FFmpeg Adaptor.

Full wrapper around the static FFmpeg binary (imageio-ffmpeg).
Translates Node execution plans via FFmpegCompiler and executes them locally,
reporting real-time progress, speed and FPS.
"""

import asyncio
import logging
import re
import shutil
import os
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional

import imageio_ffmpeg
from plugins.base import VideoProcessorPlugin, AudioProcessorPlugin
from plugins.ffmpeg.compiler import FFmpegCompiler

logger = logging.getLogger("automa.plugins.ffmpeg")


class FFmpegPlugin(VideoProcessorPlugin, AudioProcessorPlugin):
    """FFmpeg wrapper for reading, editing, and rendering media files."""

    def __init__(self) -> None:
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.compiler = FFmpegCompiler()

    @property
    def plugin_name(self) -> str:
        return "ffmpeg"

    @property
    def plugin_version(self) -> str:
        return "1.1.0-real"

    def is_available(self) -> bool:
        """Check if FFmpeg static binary exists and is executable."""
        return Path(self.ffmpeg_exe).exists()

    async def apply_crop(self, input_path: Path, output_path: Path, x: int, y: int, width: int, height: int) -> Path:
        # Descriptive crop, compile and run in a single node
        nodes = [{"type": "crop", "config": {"x": x, "y": y, "width": width, "height": height}}]
        return await self.render_pipeline(input_path, output_path, nodes)

    async def apply_zoom(self, input_path: Path, output_path: Path, factor: float) -> Path:
        nodes = [{"type": "zoom", "config": {"factor": factor}}]
        return await self.render_pipeline(input_path, output_path, nodes)

    async def apply_color_grading(
        self,
        input_path: Path,
        output_path: Path,
        contrast: float,
        brightness: float,
        saturation: float,
        bg_color: str | None = None,
        primary_color: str | None = None,
        secondary_color: str | None = None,
    ) -> Path:
        nodes = [{
            "type": "color",
            "config": {
                "contrast": contrast,
                "brightness": brightness,
                "saturation": saturation,
                "bg_color": bg_color,
                "primary_color": primary_color,
                "secondary_color": secondary_color
            }
        }]
        return await self.render_pipeline(input_path, output_path, nodes)

    async def apply_sharpness(self, input_path: Path, output_path: Path, intensity: float) -> Path:
        nodes = [{"type": "sharpness", "config": {"intensity": intensity}}]
        return await self.render_pipeline(input_path, output_path, nodes)

    async def adjust_volume(self, input_path: Path, output_path: Path, volume_db: float) -> Path:
        # Convert dB to multiplier factor
        factor = 10 ** (volume_db / 20)
        nodes = [{"type": "audiovolume", "config": {"volume": factor}}]
        return await self.render_pipeline(input_path, output_path, nodes)

    async def apply_fades(self, input_path: Path, output_path: Path, fade_in_sec: float, fade_out_sec: float) -> Path:
        nodes = [
            {"type": "audiofadein", "config": {"duration": fade_in_sec}},
            {"type": "audiofadeout", "config": {"duration": fade_out_sec}}
        ]
        return await self.render_pipeline(input_path, output_path, nodes)

    async def render_pipeline(
        self,
        input_path: Path,
        output_path: Path,
        nodes: List[Dict[str, Any]],
        video_duration: float = 0.0,
        start_time: float = 0.0,
        duration_limit: float = 0.0,
        pid_callback: Optional[Callable[[int], None]] = None,
        progress_callback: Optional[Callable[[float, float, float], Coroutine[Any, Any, None]]] = None,
    ) -> Path:
        """
        Compiles descriptive nodes into a single FFmpeg command and runs it.
        Parses live progress and reports percentages, speed and FPS.
        """
        if not self.is_available():
            raise RuntimeError("FFmpeg executable not available in virtual environment.")

        # Compile filters and options
        extra_inputs, vf_filters, af_filters, out_args, complex_filter = self.compiler.compile(nodes, video_duration)
        
        # Build command options
        args = [self.ffmpeg_exe, "-y"]
        
        # Handle time-sliced preview limiting
        if start_time > 0:
            args.extend(["-ss", f"{start_time:.3f}"])
        if duration_limit > 0:
            args.extend(["-t", f"{duration_limit:.3f}"])
            
        args.extend(["-i", str(input_path)])
        
        # Add extra inputs (like background)
        for ext_in in extra_inputs:
            args.extend(["-i", ext_in])
            
        if complex_filter:
            args.extend(["-filter_complex", complex_filter])
        else:
            # Chain video filters
            if vf_filters:
                args.extend(["-vf", ",".join(vf_filters)])
                
        # Chain audio filters
        if af_filters:
            args.extend(["-af", ",".join(af_filters)])
            
        # Add output options (codec, bitrate, FPS, metadata stripping)
        args.extend(out_args)
        
        # Request stdout machine progress logs
        args.extend(["-progress", "pipe:1", str(output_path)])
        
        logger.info(f"Executing compiled FFmpeg command: {' '.join(args)}")
        
        # Spawn process asynchronously
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        
        # Invoke pid callback so the WorkerManager registers it
        if pid_callback and process.pid:
            pid_callback(process.pid)
            
        # Read live logs/progress from stdout
        # FFmpeg prints progress fields line-by-line:
        # "frame=..."
        # "fps=..."
        # "out_time_us=..." (processed microseconds)
        # "speed=..." (multiplier, e.g. " 1.25x")
        # "progress=..."
        
        # Target duration to compute percentage
        target_dur = duration_limit if duration_limit > 0 else video_duration
        if target_dur <= 0:
            target_dur = 10.0  # Fallback duration if missing
            
        fps = 0.0
        speed = 1.0
        ffmpeg_tail: list = []  # last non-progress output lines (the real error message)
        
        try:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                line_str = line.decode("utf-8", errors="ignore").strip()
                
                if line_str and not any(
                    line_str.startswith(k)
                    for k in ("frame=", "fps=", "stream_", "bitrate=", "total_size=", "out_time", "dup_frames=", "drop_frames=", "speed=", "progress=")
                ):
                    ffmpeg_tail.append(line_str)
                    del ffmpeg_tail[:-25]
                    
                # Check for progress data key-value pairs
                if "=" in line_str:
                    key, value = line_str.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "fps":
                        try:
                            fps = float(value)
                        except ValueError:
                            pass
                    elif key == "speed":
                        try:
                            # Strip "x" from " 2.45x"
                            val_clean = value.replace("x", "").strip()
                            speed = float(val_clean)
                        except ValueError:
                            pass
                    elif key == "out_time_us":
                        try:
                            processed_us = float(value)
                            processed_sec = processed_us / 1000000.0
                            progress_percent = min(100.0, (processed_sec / target_dur) * 100.0)
                            
                            # Invoke progress callback (percentage, fps, speed)
                            if progress_callback:
                                await progress_callback(progress_percent, fps, speed)
                        except ValueError:
                            pass
                            
            await process.wait()
            
        except asyncio.CancelledError:
            # Kill process on cancellation
            try:
                process.kill()
            except Exception:
                pass
            raise
            
        if process.returncode != 0:
            details = "\n".join(ffmpeg_tail[-15:])
            logger.error(f"FFmpeg failed (code {process.returncode}):\n{details}")
            raise RuntimeError(f"FFmpeg process terminated with error code {process.returncode}: {details[-600:]}")
            
        return output_path
