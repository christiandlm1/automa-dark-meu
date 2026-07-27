"""
AUTOMA Plugins Package.

Exposes all media wrappers under a clean interface.
"""

from plugins.base import BaseMediaPlugin, VideoProcessorPlugin, AudioProcessorPlugin, TranscriberPlugin
from plugins.ffmpeg import FFmpegPlugin
from plugins.opencv import OpenCVPlugin
from plugins.whisper import WhisperPlugin
from plugins.future import FutureAIPlugin

__all__ = [
    "BaseMediaPlugin",
    "VideoProcessorPlugin",
    "AudioProcessorPlugin",
    "TranscriberPlugin",
    "FFmpegPlugin",
    "OpenCVPlugin",
    "WhisperPlugin",
    "FutureAIPlugin",
]
