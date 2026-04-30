"""Conversion-style presets for Hydra Video.

A `StyleConfig` bundle drives every visual decision the rest of the
pipeline makes - caption pacing, hook/CTA size, motion intensity,
product overlay timing, music level. This is the only place these
numbers should live, so swapping styles never means hunting through
the renderer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StyleConfig:
    name: str
    # Captions
    caption_font_size: int
    chunk_max_words: int
    caption_fade_sec: float
    # Hook overlay
    hook_font_size: int
    hook_max_seconds: float       # safety cap so very short scripts stay sane
    hook_fade_sec: float
    # CTA card
    cta_font_size: int
    cta_min_seconds: float
    cta_max_seconds: float
    cta_fade_sec: float
    # Motion / pacing
    zoom_amount: float            # final zoom (1.00 -> zoom_amount)
    drift_px: int
    pulse_every_sec: float        # subtle "pulse zoom" interval; 0 disables
    # Audio mixing
    music_volume_mult: float      # background music level under voice
    # Product overlay timing
    product_start_sec: float
    product_fade_sec: float


CLEAN = StyleConfig(
    name="clean",
    # Font sizes are at 720px reference width; captions.py scales them
    # proportionally for wider canvases (e.g. ×1.5 at 1080px).
    caption_font_size=56,
    chunk_max_words=4,       # 2–4 words = TikTok/Reels pacing
    caption_fade_sec=0.10,
    hook_font_size=88,
    hook_max_seconds=3.0,
    hook_fade_sec=0.30,
    cta_font_size=80,
    cta_min_seconds=1.6,
    cta_max_seconds=2.6,
    cta_fade_sec=0.30,
    zoom_amount=1.06,        # used by Ken Burns placeholder
    drift_px=12,
    pulse_every_sec=0.0,
    music_volume_mult=0.16,
    product_start_sec=2.0,
    product_fade_sec=0.40,
)

AGGRESSIVE = StyleConfig(
    name="aggressive",
    caption_font_size=66,
    chunk_max_words=3,
    caption_fade_sec=0.06,
    hook_font_size=112,
    hook_max_seconds=2.5,
    hook_fade_sec=0.18,
    cta_font_size=96,
    cta_min_seconds=1.6,
    cta_max_seconds=2.4,
    cta_fade_sec=0.18,
    zoom_amount=1.12,
    drift_px=20,
    pulse_every_sec=2.5,
    music_volume_mult=0.28,
    product_start_sec=1.2,
    product_fade_sec=0.25,
)

AFFILIATE = StyleConfig(
    name="affiliate",
    # Bigger captions (×1.18 vs CLEAN at 720px reference)
    caption_font_size=66,
    chunk_max_words=3,         # 3 words = fast TikTok pacing
    caption_fade_sec=0.06,
    hook_font_size=100,        # full-screen impact
    hook_max_seconds=1.5,      # short punchy hook
    hook_fade_sec=0.12,
    cta_font_size=62,
    cta_min_seconds=1.8,
    cta_max_seconds=3.0,
    cta_fade_sec=0.18,
    zoom_amount=1.08,
    drift_px=14,
    pulse_every_sec=0.0,
    music_volume_mult=0.18,
    product_start_sec=1.2,
    product_fade_sec=0.25,
)

PRESETS: dict[str, StyleConfig] = {"clean": CLEAN, "aggressive": AGGRESSIVE, "affiliate": AFFILIATE}


def resolve(style: str | None) -> StyleConfig:
    """Map a string ('clean' / 'aggressive' / unknown / None) to a preset.
    Anything we don't recognize falls back to CLEAN so the pipeline never
    breaks on a typo."""
    if not style:
        return CLEAN
    return PRESETS.get(style.strip().lower(), CLEAN)
