"""Final composer for Hydra Video.

Layers (bottom -> top):
  1. talking-head video (avatar + lipsync output) — scaled to fill canvas
  2. optional product image overlay (bottom-right)
  3. captions
  4. voice audio track (+ optional background music duck)

Outputs an H.264 / AAC MP4 to outputs/final/.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

from . import DEFAULT_FPS, OUT_FINAL, ensure_dirs
from .style import CLEAN, StyleConfig


def _lower_third(duration: float, video_size: tuple[int, int]):
    """Translucent gradient at the bottom 35% so captions read on any
    avatar. Returns a MoviePy ImageClip; safe to skip if PIL trips."""
    import numpy as np
    from PIL import Image
    from moviepy import ImageClip

    w, h = video_size
    band_h = int(h * 0.45)
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    # Linear top->bottom alpha ramp inside the band: 0 -> 200
    for i in range(band_h):
        alpha = int(200 * (i / max(band_h - 1, 1)))
        arr[h - band_h + i, :, 0] = 0
        arr[h - band_h + i, :, 1] = 0
        arr[h - band_h + i, :, 2] = 0
        arr[h - band_h + i, :, 3] = alpha
    return ImageClip(arr, transparent=True).with_duration(duration)


def _product_overlay(
    product_path: Path,
    full_duration: float,
    video_size: tuple[int, int],
    style: StyleConfig,
):
    """Top-right product card with delayed fade-in.

    Sits at top-right (not bottom) so it never collides with captions or
    the CTA card in the lower third. Appears at `style.product_start_sec`
    with a `style.product_fade_sec` cross-fade and stays to the end."""
    from moviepy import ImageClip

    p = ImageClip(str(product_path))
    target_w = int(video_size[0] * 0.32)
    scale = target_w / p.w
    p = p.resized(scale)

    start = max(0.0, min(style.product_start_sec, full_duration - 0.5))
    duration = max(0.4, full_duration - start)
    p = p.with_duration(duration).with_start(start)

    pad = 32
    top = int(video_size[1] * 0.07)
    p = p.with_position((video_size[0] - p.w - pad, top))

    if style.product_fade_sec > 0:
        try:
            from moviepy.video.fx import CrossFadeIn, CrossFadeOut
            p = p.with_effects([
                CrossFadeIn(style.product_fade_sec),
                CrossFadeOut(min(0.3, style.product_fade_sec)),
            ])
        except Exception:  # noqa: BLE001
            pass
    return p


def _fit_talking_head(
    clip,
    canvas_size: tuple[int, int],
    duration: float,
    zoom_start: float = 1.00,
    zoom_end: float = 1.06,
    face_offset_frac: float = -0.04,
    drift_px: int = 12,
):
    """Scale talking-head clip to fill the canvas, add Ken Burns zoom + micro-drift.

    Handles any input resolution (e.g. SadTalker 640x896 -> 1080x1920 canvas).

    Motion model:
    - Zoom: zoom_start -> zoom_end using ease-in-out (cosine curve) so the
      camera movement feels organic rather than mechanical.
    - Drift: a sinusoidal horizontal micro-movement over the full duration
      (max drift_px pixels) simulates a handheld lock-off shot.
    - No vertical drift — would fight the face offset.

    Guarantees:
    - Clip always fills the full canvas — no black edges at any frame.
    - Face sits slightly above dead center (face_offset_frac = -4%).
    """
    cw, ch = canvas_size
    src_w, src_h = clip.size

    # Cover-fill at zoom_end + 1% buffer so edges never go black.
    fill = max(cw / src_w, ch / src_h)
    base_scale = fill * zoom_end * 1.01

    offset_px = int(ch * face_offset_frac)  # negative = shift up

    def _ease(t: float) -> float:
        progress = t / max(duration, 0.001)
        # Cosine ease-in-out: slow start, accelerates mid, slows at end
        eased = (1.0 - math.cos(math.pi * progress)) / 2.0
        relative = zoom_start / zoom_end + (1.0 - zoom_start / zoom_end) * eased
        return base_scale * relative

    clip = clip.resized(_ease)

    def _pos(t: float):
        progress = t / max(duration, 0.001)
        eased = (1.0 - math.cos(math.pi * progress)) / 2.0
        relative = zoom_start / zoom_end + (1.0 - zoom_start / zoom_end) * eased
        scale = base_scale * relative
        w = int(src_w * scale)
        h = int(src_h * scale)
        # Horizontal micro-drift: one sine arc across full duration
        drift = drift_px * math.sin(math.pi * progress)
        x = (cw - w) / 2 + drift
        y = (ch - h) / 2 + offset_px
        return (x, y)

    return clip.with_position(_pos)


def compose(
    avatar_video: Path,
    audio_path: Path,
    caption_clips: list,
    video_size: tuple[int, int],
    duration_sec: float,
    product_path: Path | None = None,
    music_path: Path | None = None,
    hook_clip=None,
    cta_clip=None,
    out_path: Path | None = None,
    fps: int = DEFAULT_FPS,
    style: StyleConfig = CLEAN,
) -> Path:
    """Compose the final MP4. Returns the output path."""
    ensure_dirs()
    if out_path is None:
        out_path = OUT_FINAL / f"hydra_{int(time.time())}.mp4"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    from moviepy import (
        AudioFileClip, CompositeAudioClip, CompositeVideoClip, VideoFileClip,
    )

    _raw_base = VideoFileClip(str(avatar_video)).with_duration(duration_sec)
    base = _fit_talking_head(_raw_base, video_size, duration_sec)
    layers = [base]

    # Cinematic lower-third behind captions so text reads on any avatar.
    try:
        layers.append(_lower_third(duration_sec, video_size))
    except Exception:  # noqa: BLE001
        pass

    if product_path and Path(product_path).exists():
        layers.append(_product_overlay(
            Path(product_path), duration_sec, video_size, style,
        ))

    layers.extend(caption_clips)

    if hook_clip is not None:
        layers.append(hook_clip)
    if cta_clip is not None:
        layers.append(cta_clip)

    voice = AudioFileClip(str(audio_path)).with_duration(duration_sec)
    audio_track = voice
    if music_path and Path(music_path).exists():
        try:
            from moviepy.audio.fx import MultiplyVolume
            music = (
                AudioFileClip(str(music_path))
                .with_duration(duration_sec)
                .with_effects([MultiplyVolume(style.music_volume_mult)])
            )
            audio_track = CompositeAudioClip([music, voice])
        except Exception:  # noqa: BLE001
            audio_track = voice

    final = (
        CompositeVideoClip(layers, size=video_size)
        .with_duration(duration_sec)
        .with_audio(audio_track)
    )
    final.write_videofile(
        str(out_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="6000k",
        threads=4,
        logger=None,
    )

    final.close()
    _raw_base.close()
    voice.close()
    return out_path
