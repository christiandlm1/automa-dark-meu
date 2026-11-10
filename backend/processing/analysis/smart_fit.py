"""
AUTOMA Processing - Smart Fit analysis.

Analyses an imported video to find the region that really contains the original
footage (removing black/white/solid bars and static templates/frames that were
baked into the video) and detects the free area reserved for the video inside a
template image.

Design rules:
- Only *dead* regions are removed: uniform black/white bars, or static strips that
  end in a sharp, full-width edge (old templates/frames). Content is never
  cropped "by the center".
- When the result is not safe, no crop is returned and the caller should simply
  fit the whole frame into the area (conservative fallback).
- Uses only OpenCV/numpy and the FFmpeg binary already shipped with AUTOMA.
- The input file is only ever read.
"""

from __future__ import annotations

import logging
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

logger = logging.getLogger("automa.processing.analysis.smart_fit")

# --- Tunables (gray values are 0..255 on a frame downscaled to ~360 px wide) ---
SAMPLE_COUNT = 12
ANALYSIS_WIDTH = 360
UNIFORM_STD = 2.5        # a row/column is "uniform" (true bar) when its spatial std stays below this
DARK_MEAN = 30.0         # mean below -> black bar
LIGHT_MEAN = 225.0       # mean above -> white bar
BAR_TEMPORAL_DRIFT = 14.0
TEMPORAL_STD = 5.0       # per-pixel temporal std above this -> pixel is "moving"
STATIC_ROW_ACTIVITY = 0.02
BLUR_HF = 1.2            # mean |laplacian| below this -> blurred/flat strip
EDGE_DIFF = 12.0
EDGE_FRACTION = 0.55     # fraction of the span that must show the boundary edge
DOMINANCE = 0.6          # share of the most common tone in a static strip
MAX_SIDE_CROP = 0.40     # never remove more than 40 % from one side
MIN_KEEP_AREA = 0.20     # the kept region must be at least 20 % of the frame
MIN_ACTIVITY_FOR_STATIC = 0.05
ACTIVE_BEYOND = 0.25     # content right after a static strip must be moving across >=25 % of the span
ALIVE_AFTER = 0.02       # share of the area below a template strip that must show motion (the footage is alive)
FLAT_STRIP = 0.5         # share of a strip in ONE 8-level tone to count as a flat (template-like) strip
BOTTOM_SAFE_RATIO = 0.086  # when the free area reaches the bottom of the template, keep ~8.6 % (165 px of 1920) free
                           # (safe zone for Reels/Shorts buttons and captions; matches the reference example)


@dataclass
class FitAnalysis:
    """Result of analysing one video."""

    width: int
    height: int
    crop: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h in full-resolution pixels
    confidence: float = 1.0
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "crop": None
            if self.crop is None
            else {"x": self.crop[0], "y": self.crop[1], "width": self.crop[2], "height": self.crop[3]},
            "confidence": round(self.confidence, 2),
            "reasons": list(self.reasons),
        }


# ----------------------------------------------------------------------------
# Frame sampling (through FFmpeg so geometry/rotation match the real render)
# ----------------------------------------------------------------------------

def _no_window_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def _ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def _grab(path: Path, t: float, scale_w: Optional[int]) -> Optional[np.ndarray]:
    cmd = [_ffmpeg_exe(), "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(path), "-frames:v", "1"]
    if scale_w:
        cmd += ["-vf", f"scale={scale_w}:-2:flags=area"]
    cmd += ["-f", "image2pipe", "-c:v", "png", "pipe:1"]
    try:
        out = subprocess.run(
            cmd, capture_output=True, timeout=60, creationflags=_no_window_flags()
        ).stdout
    except (subprocess.SubprocessError, OSError) as exc:
        logger.warning("frame grab failed at %.2fs: %s", t, exc)
        return None
    if not out:
        return None
    return cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)


def _probe_duration(path: Path) -> float:
    try:
        err = subprocess.run(
            [_ffmpeg_exe(), "-hide_banner", "-i", str(path)],
            capture_output=True,
            timeout=30,
            creationflags=_no_window_flags(),
        ).stderr.decode("utf-8", "ignore")
    except (subprocess.SubprocessError, OSError):
        return 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", err)
    if not m:
        return 0.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def sample_frames(
    path: Path, duration: float = 0.0, count: int = SAMPLE_COUNT, width: int = ANALYSIS_WIDTH
) -> Tuple[List[np.ndarray], Tuple[int, int]]:
    """Return (small BGR frames, (full_w, full_h)) sampled between 5 % and 95 % of the video."""
    if duration <= 0:
        duration = _probe_duration(path)
    if duration <= 0.2:
        times = [0.0]
    else:
        times = list(np.linspace(duration * 0.05, duration * 0.95, count))

    full = _grab(path, times[len(times) // 2], None)
    if full is None:
        raise ValueError(f"Não foi possível ler frames de {path}")
    full_h, full_w = full.shape[:2]
    del full

    with ThreadPoolExecutor(max_workers=4) as pool:
        frames = [f for f in pool.map(lambda t: _grab(path, t, width), times) if f is not None]
    if not frames:
        raise ValueError(f"Não foi possível amostrar frames de {path}")
    # all frames must share the same shape
    shape = frames[0].shape
    frames = [f for f in frames if f.shape == shape]
    return frames, (full_w, full_h)


# ----------------------------------------------------------------------------
# Border / template detection
# ----------------------------------------------------------------------------

def _edge_strength(f: np.ndarray, p: int) -> float:
    """Persistent straight-edge score for the boundary between rows p-1 and p."""
    h = f.shape[1]
    scores = []
    for t in range(f.shape[0]):
        best = 0.0
        pairs = [(p, p - 1)]
        if p + 1 < h:
            pairs.append((p + 1, p - 1))
        if p - 2 >= 0:
            pairs.append((p, p - 2))
        for a, b in pairs:
            d = np.abs(f[t, a, :] - f[t, b, :])
            best = max(best, float((d > EDGE_DIFF).mean()))
        scores.append(best)
    return float(np.percentile(scores, 25))


def _leading_crop(frames: np.ndarray, allow_static: bool) -> Tuple[int, str]:
    """Number of leading rows (top side) that are dead, plus a reason label."""
    _, height, _ = frames.shape
    max_p = int(height * MAX_SIDE_CROP)
    if max_p < 1:
        return 0, ""
    f = frames[:, : max_p + 3, :].astype(np.float32)
    h = f.shape[1]

    row_mean = f.mean(axis=2)
    row_std = f.std(axis=2)
    uniform = row_std.max(axis=0) < UNIFORM_STD
    mean_t = row_mean.mean(axis=0)
    drift = row_mean.max(axis=0) - row_mean.min(axis=0)
    bar_color = ((mean_t < DARK_MEAN) | (mean_t > LIGHT_MEAN)) & (drift < BAR_TEMPORAL_DRIFT)
    uni_bar = uniform & bar_color

    best, reason = 0, ""
    while best < max_p and uni_bar[best]:
        best += 1
    if best:
        reason = "barra uniforme"

    if allow_static and len(frames) >= 3:
        tstd = f.std(axis=0)
        tstd_all = frames.astype(np.float32).std(axis=0)  # whole frame, to know if the footage below is alive
        static = (tstd > TEMPORAL_STD).mean(axis=1) < STATIC_ROW_ACTIVITY
        hf = np.mean(
            [np.abs(cv2.Laplacian(f[t], cv2.CV_32F, ksize=3)).mean(axis=1) for t in range(f.shape[0])],
            axis=0,
        )
        blurred = hf < BLUR_HF
        dead = uni_bar | static | blurred

        length = 0
        while length < max_p and dead[length]:
            length += 1

        look = max(3, int(height * 0.03))
        for p in range(length, max(best, 0), -1):
            if p + look > h:
                below = tstd[p:, :]
            else:
                below = tstd[p : p + look, :]
            # the footage that starts at the boundary must be alive (moving), otherwise this
            # may be a static part of the scene (wall, tripod background) and not a template
            local_alive = below.size > 0 and (below > TEMPORAL_STD).mean() >= ACTIVE_BEYOND
            if not local_alive:
                # The footage may start with a still area (wall, sky). Accept the boundary only when
                # the footage below moves somewhere AND the strip is a flat, template-like one.
                if (tstd_all[p:, :] > TEMPORAL_STD).mean() < ALIVE_AFTER:
                    continue
                strip0 = frames[0, :p, :]
                if np.bincount((strip0 >> 3).ravel(), minlength=32).max() / strip0.size < FLAT_STRIP:
                    continue
            if _edge_strength(f, p) < EDGE_FRACTION:
                continue
            strip = frames[:, :p, :]
            tones = (strip[0] >> 4).ravel()
            dominance = np.bincount(tones, minlength=16).max() / tones.size
            if dominance >= DOMINANCE or blurred[:p].mean() >= 0.9:
                if p > best + 2:  # a few extra rows over a plain bar is still just a bar
                    best, reason = p, "template/moldura estática"
                else:
                    best = max(best, p)
                break
    return best, reason


def _detect_sides(
    frames: np.ndarray, allow_static: bool
) -> Tuple[int, int, int, int, List[str]]:
    """Dead rows/cols to remove at (top, bottom, left, right) of a (T,H,W) stack."""
    reasons: List[str] = []
    top, r1 = _leading_crop(frames, allow_static)
    bottom, r2 = _leading_crop(np.ascontiguousarray(frames[:, ::-1, :]), allow_static)
    t = np.ascontiguousarray(frames.transpose(0, 2, 1))
    left, r3 = _leading_crop(t, allow_static)
    right, r4 = _leading_crop(np.ascontiguousarray(t[:, ::-1, :]), allow_static)
    for name, val, why in (("topo", top, r1), ("base", bottom, r2), ("esquerda", left, r3), ("direita", right, r4)):
        if val:
            reasons.append(f"{name}: {val}px ({why})")
    return top, bottom, left, right, reasons


_FACE_CASCADE: Optional[cv2.CascadeClassifier] = None


def _detect_faces(gray_frames: Sequence[np.ndarray]) -> List[Tuple[int, int, int, int]]:
    global _FACE_CASCADE
    try:
        if _FACE_CASCADE is None:
            _FACE_CASCADE = cv2.CascadeClassifier(
                str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
            )
        if _FACE_CASCADE.empty():
            return []
        boxes: List[Tuple[int, int, int, int]] = []
        for g in gray_frames:
            for (x, y, w, h) in _FACE_CASCADE.detectMultiScale(g, 1.2, 6, minSize=(24, 24)):
                boxes.append((int(x), int(y), int(w), int(h)))
        return boxes
    except Exception as exc:  # face guard is best-effort only
        logger.debug("face detection unavailable: %s", exc)
        return []


def _protect_faces(
    rect: Tuple[int, int, int, int], faces: Sequence[Tuple[int, int, int, int]]
) -> Tuple[Tuple[int, int, int, int], bool]:
    """Expand rect (x0,y0,x1,y1) so no face is cut by it."""
    x0, y0, x1, y1 = rect
    changed = False
    for (fx, fy, fw, fh) in faces:
        ix0, iy0 = max(x0, fx), max(y0, fy)
        ix1, iy1 = min(x1, fx + fw), min(y1, fy + fh)
        inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
        if inter == 0 or inter >= fw * fh * 0.98:
            continue  # face fully inside, or fully outside (not part of the footage)
        pad = int(0.1 * max(fw, fh))
        x0, y0 = min(x0, max(fx - pad, 0)), min(y0, max(fy - pad, 0))
        x1, y1 = max(x1, fx + fw + pad), max(y1, fy + fh + pad)
        changed = True
    return (x0, y0, x1, y1), changed


def analyze_frames(
    frames_bgr: Sequence[np.ndarray],
    full_size: Tuple[int, int],
    faces: Optional[Sequence[Tuple[int, int, int, int]]] = None,
) -> FitAnalysis:
    """Core analysis on already sampled frames (pure function, easy to test)."""
    full_w, full_h = full_size
    result = FitAnalysis(width=full_w, height=full_h)
    gray = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames_bgr])
    t_count, sh, sw = gray.shape
    if sh < 16 or sw < 16:
        result.reasons.append("frame muito pequeno para analisar")
        return result

    x0, y0, x1, y1 = 0, 0, sw, sh
    all_reasons: List[str] = []
    for _ in range(3):
        sub = np.ascontiguousarray(gray[:, y0:y1, x0:x1])
        moving = (sub.astype(np.float32).std(axis=0) > TEMPORAL_STD).mean()
        allow_static = t_count >= 3 and moving >= MIN_ACTIVITY_FOR_STATIC
        top, bottom, left, right, reasons = _detect_sides(sub, allow_static)
        if not (top or bottom or left or right):
            break
        y0, y1 = y0 + top, y1 - bottom
        x0, x1 = x0 + left, x1 - right
        all_reasons = reasons
        if x1 - x0 < 8 or y1 - y0 < 8:
            break

    if (x0, y0, x1, y1) == (0, 0, sw, sh):
        result.reasons.append("nenhuma borda/moldura detectada: vídeo mantido inteiro")
        return result

    rect = (x0, y0, x1, y1)
    if faces is None:
        faces = _detect_faces([gray[i] for i in range(0, t_count, max(1, t_count // 4))])
    rect, expanded = _protect_faces(rect, faces)
    x0, y0, x1, y1 = rect
    result.confidence = 0.9
    if expanded:
        result.confidence = 0.7
        all_reasons.append("recorte ampliado para não cortar rostos")

    keep_area = ((x1 - x0) * (y1 - y0)) / float(sw * sh)
    aspect = (x1 - x0) / float(max(y1 - y0, 1))
    if keep_area < MIN_KEEP_AREA or not (0.2 <= aspect <= 5.0):
        result.confidence = 0.3
        result.reasons = all_reasons + ["recorte implausível: vídeo mantido inteiro (modo conservador)"]
        return result

    # Map to full resolution, safely inside the detected boundary.
    sx, sy = full_w / float(sw), full_h / float(sh)
    mx, my = max(2, int(np.ceil(sx))), max(2, int(np.ceil(sy)))
    fx0 = 0 if x0 == 0 else int(np.ceil(x0 * sx)) + mx
    fy0 = 0 if y0 == 0 else int(np.ceil(y0 * sy)) + my
    fx1 = full_w if x1 == sw else int(x1 * sx) - mx
    fy1 = full_h if y1 == sh else int(y1 * sy) - my
    fx0, fy0 = fx0 + (fx0 % 2), fy0 + (fy0 % 2)  # even offsets
    fx1, fy1 = fx1 - (fx1 % 2), fy1 - (fy1 % 2)
    w, h = fx1 - fx0, fy1 - fy0
    if w < 16 or h < 16:
        result.confidence = 0.3
        result.reasons = all_reasons + ["área útil muito pequena: vídeo mantido inteiro"]
        return result

    result.crop = (fx0, fy0, w, h)
    result.reasons = all_reasons
    return result


def analyze_video(path: Path, duration: float = 0.0) -> FitAnalysis:
    """Analyse a video file (read-only). Never raises: on failure returns "no crop"."""
    try:
        frames, full = sample_frames(Path(path), duration)
        return analyze_frames(frames, full)
    except Exception as exc:
        logger.warning("smart fit analysis failed for %s: %s", path, exc)
        result = FitAnalysis(width=0, height=0, confidence=0.0)
        result.reasons.append(f"análise falhou ({exc}): vídeo mantido inteiro")
        return result


# ----------------------------------------------------------------------------
# Template image: free area reserved for the video
# ----------------------------------------------------------------------------

def detect_template_area(
    image_path: Path,
    margin_top: int = 40,
    margin_bottom: int = 0,
    margin_side: int = 0,
    tolerance: int = 24,
) -> Optional[Dict[str, int]]:
    """
    Find the free area reserved for the video in a template image.

    The area is the largest empty horizontal band between the template's elements
    (header texts above, optional footer/watermark below).

    Returns {"x","y","width","height","image_width","image_height"} in template pixels,
    or None if the file is not a readable still image.
    """
    try:
        data = np.fromfile(str(image_path), dtype=np.uint8)  # unicode-safe on Windows
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None
    if img is None:
        return None
    h, w = img.shape[:2]
    edge = np.concatenate([img[:, :2].reshape(-1, 3), img[:, -2:].reshape(-1, 3)])
    bg = np.median(edge, axis=0)
    diff = np.abs(img.astype(np.int16) - bg.astype(np.int16)).max(axis=2)
    rows = np.where((diff > tolerance).sum(axis=1) >= 3)[0]

    # Group rows with content into blocks; gaps smaller than min_gap belong to the same block
    # (lines of text, avatar + name...). The video goes into the largest empty gap.
    min_gap = max(32, int(h * 0.04))
    if rows.size == 0:
        gap_start, gap_end = 0, h
    else:
        splits = np.where(np.diff(rows) > min_gap)[0]
        starts = [int(rows[0])] + [int(rows[i + 1]) for i in splits]
        ends = [int(rows[i]) + 1 for i in splits] + [int(rows[-1]) + 1]
        gaps = [(0, starts[0])]  # above the first block
        gaps += [(ends[i], starts[i + 1]) for i in range(len(starts) - 1)]
        gaps.append((ends[-1], h))  # below the last block
        gap_start, gap_end = max(gaps, key=lambda g: g[1] - g[0])

    top = gap_start + (margin_top if gap_start > 0 else 0)
    if gap_end < h:
        bottom = gap_end - 24  # a footer/watermark follows: stay clear of it
    else:
        # margin_bottom == 0 means "automatic" (safe zone at the bottom of the template)
        bottom = h - (margin_bottom if margin_bottom > 0 else int(round(h * BOTTOM_SAFE_RATIO)))
    top = min(top, h - 16)
    top += top % 2
    bottom = max(bottom, top + 16)
    height = bottom - top
    height -= height % 2
    side = margin_side - margin_side % 2
    return {
        "x": side,
        "y": top,
        "width": w - 2 * side,
        "height": height,
        "image_width": w,
        "image_height": h,
    }


def map_area_to_canvas(area: Dict[str, int], canvas_w: int, canvas_h: int) -> Dict[str, int]:
    """
    Convert an area measured on the template image into canvas (export) pixels, using the
    same "scale to cover + center crop" rule the compiler applies to the background.
    """
    iw, ih = area.get("image_width", canvas_w), area.get("image_height", canvas_h)
    s = max(canvas_w / float(iw), canvas_h / float(ih))
    ox, oy = (iw * s - canvas_w) / 2.0, (ih * s - canvas_h) / 2.0
    x0 = max(0.0, area["x"] * s - ox)
    y0 = max(0.0, area["y"] * s - oy)
    x1 = min(float(canvas_w), (area["x"] + area["width"]) * s - ox)
    y1 = min(float(canvas_h), (area["y"] + area["height"]) * s - oy)
    x0, y0 = int(round(x0)), int(round(y0))
    x0, y0 = x0 + x0 % 2, y0 + y0 % 2
    w, h = int(x1) - x0, int(y1) - y0
    return {"x": x0, "y": y0, "width": w - w % 2, "height": h - h % 2}
