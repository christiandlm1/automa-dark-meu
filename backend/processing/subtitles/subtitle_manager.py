import os
import json
from datetime import datetime, timezone
import xxhash
from plugins.subtitles.provider import TranscriptionProvider

class SubtitleManager:
    """
    Manages subtitle transcription and caching.
    """
    def __init__(self, provider: TranscriptionProvider, cache_dir: str = ".cache/subtitles"):
        self.provider = provider
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_file_hash(self, file_path: str) -> str:
        """
        Calculates xxhash of a file for caching purposes.
        """
        hasher = xxhash.xxh64()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    async def get_or_create_subtitle(self, video_path: str, language: str = "auto") -> str:
        """
        Gets an existing cached subtitle or creates a new one using the provider.
        Returns the path to the .srt file.
        """
        file_hash = self._get_file_hash(video_path)
        video_cache_dir = os.path.join(self.cache_dir, file_hash)
        
        cached_srt_path = os.path.join(video_cache_dir, "subtitle.srt")
        metadata_path = os.path.join(video_cache_dir, "metadata.json")
        
        if os.path.exists(cached_srt_path) and os.path.exists(metadata_path):
            return cached_srt_path
            
        os.makedirs(video_cache_dir, exist_ok=True)
            
        # Transcribe and save directly to cache
        result = await self.provider.transcribe(video_path, cached_srt_path, language=language)
        
        # Save metadata
        metadata = {
            "language": result.language,
            "duration": result.duration,
            "segments": result.segments,
            "word_count": result.word_count,
            "provider_used": result.source,
            "date": datetime.now(timezone.utc).isoformat()
        }
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
            
        return cached_srt_path
