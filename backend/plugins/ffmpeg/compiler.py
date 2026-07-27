"""
AUTOMA Plugins - FFmpeg Compiler.

Translates high-level Node descriptions into concrete FFmpeg filtergraphs and options.
Implements complete separation of concerns: Nodes describe, Compiler translates.
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("automa.plugins.ffmpeg.compiler")


class FFmpegCompiler:
    """Compiles a list of pipeline Nodes into FFmpeg CLI arguments."""

    def compile(self, nodes: List[Dict[str, Any]], video_duration: float = 0.0) -> Tuple[List[str], List[str], List[str], List[str], Optional[str]]:
        """
        Translates a list of descriptive nodes into:
        - extra_inputs: Additional input files
        - vf_filters: Video filter chain list (e.g. ['crop=...', 'transpose=1'])
        - af_filters: Audio filter chain list (e.g. ['volume=...', 'afade=...'])
        - output_args: Generic output options (e.g. ['-r', '30', '-b:v', '4000k'])
        - complex_filter: A full filter_complex string if needed (overrides vf_filters)
        """
        extra_inputs: List[str] = []
        vf_filters: List[str] = []
        af_filters: List[str] = []
        output_args: List[str] = []
        complex_filter: Optional[str] = None
        
        # Track if we have codec/container preferences
        video_codec = "libx264"  # Default
        audio_codec = "aac"      # Default
        
        # Pre-process background node as it forces a complex filter
        bg_node = next((n for n in nodes if n.get("type") == "background"), None)
        has_background = bg_node is not None
        if has_background:
            bg_path = bg_node.get("config", {}).get("asset_path")
            if bg_path:
                extra_inputs.append(bg_path)
        
        for index, node in enumerate(nodes):
            node_type = node.get("type", "").lower()
            config = node.get("config", {})
            
            # --- Video Filters ---
            if node_type == "crop":
                x = config.get("x", 0)
                y = config.get("y", 0)
                w = config.get("width", 1280)
                h = config.get("height", 720)
                vf_filters.append(f"crop={w}:{h}:{x}:{y}")
                
            elif node_type == "resize":
                w = config.get("width", 1280)
                h = config.get("height", 720)
                vf_filters.append(f"scale={w}:{h}")
                
            elif node_type == "scale":
                w = config.get("width")
                h = config.get("height")
                factor = config.get("factor")
                if factor is not None:
                    vf_filters.append(f"scale=iw*{factor}:ih*{factor}")
                elif w is not None and h is not None:
                    vf_filters.append(f"scale={w}:{h}")
                    
            elif node_type == "zoom":
                factor = config.get("factor", 1.0)
                if float(factor) != 1.0:
                    vf_filters.append(f"crop=iw/{factor}:ih/{factor},scale=iw:ih")
                    
            elif node_type == "rotate":
                degrees = int(config.get("degrees", 0))
                if degrees == 90:
                    vf_filters.append("transpose=1")
                elif degrees == 180:
                    vf_filters.append("transpose=1,transpose=1")
                elif degrees == 270:
                    vf_filters.append("transpose=2")
                    
            elif node_type == "mirror":
                direction = config.get("direction", "none").lower()
                if direction == "horizontal":
                    vf_filters.append("hflip")
                elif direction == "vertical":
                    vf_filters.append("vflip")
                elif direction == "both":
                    vf_filters.append("hflip,vflip")
                    
            elif node_type == "brightness":
                val = float(config.get("value", 0.0))
                vf_filters.append(f"eq=brightness={val}")
                
            elif node_type == "contrast":
                val = float(config.get("value", 1.0))
                vf_filters.append(f"eq=contrast={val}")
                
            elif node_type == "saturation":
                val = float(config.get("value", 1.0))
                vf_filters.append(f"eq=saturation={val}")
                
            elif node_type == "color":
                contrast = float(config.get("contrast", 1.0))
                brightness = float(config.get("brightness", 0.0))
                saturation = float(config.get("saturation", 1.0))
                vf_filters.append(f"eq=contrast={contrast}:brightness={brightness}:saturation={saturation}")
                
            elif node_type == "sharpness":
                intensity = float(config.get("intensity", 1.0))
                vf_filters.append(f"unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount={intensity}")
                
            elif node_type == "noisereduction":
                intensity = float(config.get("intensity", 1.0))
                # hqdn3d format: hqdn3d=luma_spatial:chroma_spatial:luma_tmp:chroma_tmp
                # Simple mapping: scale intensity to typical range (0 to 10)
                val = intensity * 4.0
                vf_filters.append(f"hqdn3d={val}:{val}:{val*1.5}:{val*1.5}")
                
            elif node_type == "subtitle":
                srt_path = config.get("srt_path")
                if srt_path:
                    # Windows paths in FFmpeg subtitles filter need escaping
                    escaped_path = str(srt_path).replace('\\', '/').replace('C:', 'C\\:')
                    
                    font_name = config.get("font_name", "Arial")
                    font_size = config.get("font_size", 48)
                    primary_color = config.get("primary_color", "&H00FFFFFF")
                    outline_color = config.get("outline_color", "&H00000000")
                    back_color = config.get("back_color", "&H80000000")
                    margin_v = config.get("margin_v", 20)
                    
                    # Convert alignment
                    # Substation Alpha alignments: 1=Bottom Left, 2=Bottom Center, 3=Bottom Right
                    align_str = config.get("alignment", "Center")
                    alignment = 2 # Default Bottom Center
                    if align_str == "Left":
                        alignment = 1
                    elif align_str == "Right":
                        alignment = 3
                        
                    # Format hex colors for ASS format (AABBGGRR in hex but ASS expects &HBBGGRR format usually, but we use what we have, assuming standard hex or we just pass it)
                    # For simplicity, if it's #RRGGBB, we replace # with &H
                    p_col = primary_color.replace('#', '&H00') if primary_color.startswith('#') else primary_color
                    o_col = outline_color.replace('#', '&H00') if outline_color.startswith('#') else outline_color
                    b_col = back_color.replace('#', '&H') if back_color.startswith('#') else back_color
                    
                    force_style = (
                        f"FontName={font_name},"
                        f"FontSize={font_size},"
                        f"PrimaryColour={p_col},"
                        f"OutlineColour={o_col},"
                        f"BackColour={b_col},"
                        f"MarginV={margin_v},"
                        f"Alignment={alignment}"
                    )
                    
                    vf_filters.append(f"subtitles='{escaped_path}':force_style='{force_style}'")
                
            # --- Output Parameters ---
            elif node_type == "framerate":
                fps = config.get("fps", 30)
                output_args.extend(["-r", str(fps)])
                
            elif node_type == "bitrate":
                bitrate = config.get("bitrate", 4000)
                output_args.extend(["-b:v", f"{bitrate}k"])
                
            elif node_type == "codec":
                codec = config.get("codec", "h264").lower()
                if codec == "h264":
                    video_codec = "libx264"
                elif codec == "hevc":
                    video_codec = "libx265"
                elif codec == "vp9":
                    video_codec = "libvpx-vp9"
                    
            # --- Audio Filters ---
            elif node_type == "audiovolume":
                volume = float(config.get("volume", 1.0))
                af_filters.append(f"volume={volume}")
                
            elif node_type == "audiofadein":
                duration = float(config.get("duration", 0.0))
                if duration > 0:
                    af_filters.append(f"afade=t=in:ss=0:d={duration}")
                    
            elif node_type == "audiofadeout":
                duration = float(config.get("duration", 0.0))
                if duration > 0 and video_duration > duration:
                    start_time = max(0.0, video_duration - duration)
                    af_filters.append(f"afade=t=out:st={start_time}:d={duration}")
                    
            elif node_type == "metadatacleaner":
                output_args.extend(["-map_metadata", "-1", "-map_chapters", "-1"])
                
            # --- Export configuration node ---
            elif node_type == "export":
                res = config.get("resolution")
                if res:
                    w, h = res.split("x")
                    vf_filters.append(f"scale={w}:{h}")
                    
                fps = config.get("fps")
                if fps:
                    output_args.extend(["-r", str(fps)])
                    
                codec = config.get("codec", "h264").lower()
                if codec == "h264":
                    video_codec = "libx264"
                elif codec == "hevc":
                    video_codec = "libx265"
                elif codec == "vp9":
                    video_codec = "libvpx-vp9"
                    
                bitrate = config.get("bitrate")
                if bitrate:
                    output_args.extend(["-b:v", f"{bitrate}k"])
                    
                # Audio volume and fades inside export node
                vol = config.get("volume")
                if vol is not None:
                    af_filters.append(f"volume={vol}")
                    
                fade_in = config.get("fade_in", 0.0)
                if float(fade_in) > 0.0:
                    af_filters.append(f"afade=t=in:ss=0:d={fade_in}")
                    
                fade_out = config.get("fade_out", 0.0)
                if float(fade_out) > 0.0 and video_duration > fade_out:
                    start_time = max(0.0, video_duration - fade_out)
                    af_filters.append(f"afade=t=out:st={start_time}:d={fade_out}")
                    
        # Apply compiled codecs
        output_args.extend(["-vcodec", video_codec])
        output_args.extend(["-acodec", audio_codec])
        
        # Build complex filter if background exists
        if has_background:
            bg_config = bg_node.get("config", {})
            w = bg_config.get("width", 1080)
            h = bg_config.get("height", 1920)
            # scale background [1:v]
            bg_scale = f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}[bg];"
            
            # apply standard video filters to the foreground [0:v]
            fg_chain = ",".join(vf_filters) if vf_filters else "copy"
            fg_scale = f"[0:v]{fg_chain}[fg];"
            
            # overlay fg on bg
            overlay = f"[bg][fg]overlay=(W-w)/2:(H-h)/2:format=auto,format=yuv420p[v]"
            
            complex_filter = bg_scale + fg_scale + overlay
            output_args.extend(["-map", "[v]", "-map", "0:a?"])
        
        return extra_inputs, vf_filters, af_filters, output_args, complex_filter
