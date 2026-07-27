"""
AUTOMA Plugins - Whisper Adaptor.

Whisper speech-to-text implementation shell. In Módulo 02, this serves as a mock
that logs actions and returns mock transcription data, preparing the ground for Módulo 03.
"""

from pathlib import Path
from typing import Any

from plugins.base import TranscriberPlugin


class WhisperPlugin(TranscriberPlugin):
    """Whisper transcription plugin wrapper."""

    @property
    def plugin_name(self) -> str:
        return "whisper"

    @property
    def plugin_version(self) -> str:
        return "1.0.0-mock"

    def is_available(self) -> bool:
        # For Módulo 02, return True.
        # In Módulo 03, we will verify PyTorch, CUDA (optional) and whisper library imports.
        return True

    async def transcribe(self, input_path: Path) -> dict[str, Any]:
        print(f"[WhisperPlugin] Mock Transcribe: {input_path}")
        return {
            "text": "Olá, bem-vindo ao processamento de vídeo automático do AUTOMA.",
            "language": "pt",
            "segments": [
                {"id": 0, "start": 0.0, "end": 2.5, "text": "Olá,"},
                {"id": 1, "start": 2.5, "end": 6.0, "text": "bem-vindo ao processamento de vídeo"},
                {"id": 2, "start": 6.0, "end": 9.5, "text": "automático do AUTOMA."}
            ]
        }
