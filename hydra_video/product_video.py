"""Product image slideshow for Hydra Video affiliate content.

Replaces the avatar/lipsync stage with a multi-slide image sequence:
  - Each slide is a PIL-rendered product card (gradient bg + bold text)
  - Every slide gets its own Ken Burns motion (zoom + micro-drift)
  - Hard cuts between slides every 2-4 seconds
  - Output is a silent MP4 at the target canvas size, ready for compose()

No external image APIs required — all slides are generated from the
idea metadata (product name, hook, problem, niche) using PIL only.
Real product image URLs can be passed via `image_urls` once a scraper
is added; the engine will use them in addition to the generated cards.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import DEFAULT_FPS, DEFAULT_VIDEO_SIZE, OUT_RAW_AVATAR, ensure_dirs


# ── Niche colour palettes ─────────────────────────────────────────────────────
# Each niche gets two gradient stops (top, bottom) in RGB.
_NICHE_COLOURS: dict[str, tuple[tuple, tuple]] = {
    "productivity":     ((12,  28,  64), (6,  14,  32)),
    "business":         ((10,  36,  20), (5,  18,  10)),
    "ai":               ((18,  12,  48), (9,   6,  24)),
    "work_from_home":   ((38,  24,  10), (19,  12,   5)),
    "content_creation": ((36,  10,  24), (18,   5,  12)),
}
_DEFAULT_COLOURS = ((14, 14, 28), (7, 7, 14))

_ACCENT: dict[str, tuple] = {
    "productivity":     (64,  148, 255),
    "business":         (80,  200, 120),
    "ai":               (160, 100, 255),
    "work_from_home":   (255, 165,  60),
    "content_creation": (255,  80, 120),
}
_DEFAULT_ACCENT = (100, 180, 255)


def _load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient_bg(size: tuple[int, int], top: tuple, bottom: tuple) -> Image.Image:
    """Vertical linear gradient from `top` RGB to `bottom` RGB."""
    w, h = size
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _wrap_text(text: str, font: ImageFont.ImageFont, max_w: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Greedy word-wrap into lines no wider than max_w pixels."""
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] > max_w and line:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines or [""]


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.ImageFont,
    canvas_w: int,
    y_center: int,
    fill: tuple = (255, 255, 255),
    stroke: int = 3,
    line_gap: int = 12,
) -> None:
    """Draw word-wrapped lines centered at y_center."""
    line_heights = []
    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=font)
        line_heights.append(bb[3] - bb[1])
    total_h = sum(line_heights) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2
    for ln, lh in zip(lines, line_heights):
        bb = draw.textbbox((0, 0), ln, font=font)
        x = (canvas_w - (bb[2] - bb[0])) // 2
        draw.text((x, y), ln, font=font, fill=fill,
                  stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += lh + line_gap


# ── Card types ────────────────────────────────────────────────────────────────

def _card_product(product: str, niche: str, size: tuple[int, int]) -> np.ndarray:
    """Slide 1 — bold product name on brand gradient."""
    w, h = size
    top, bot = _NICHE_COLOURS.get(niche, _DEFAULT_COLOURS)
    accent = _ACCENT.get(niche, _DEFAULT_ACCENT)
    img = _gradient_bg(size, top, bot)
    draw = ImageDraw.Draw(img)

    # Accent bar at top
    bar_h = max(6, h // 120)
    draw.rectangle([0, 0, w, bar_h], fill=accent)

    # Niche tag
    tag_font = _load_font(max(28, w // 28))
    tag = niche.upper().replace("_", " ")
    draw.text((w // 2, int(h * 0.14)), tag, font=tag_font, fill=accent,
              anchor="mm", stroke_width=1, stroke_fill=(0, 0, 0))

    # Product name — large, centered
    name_font = _load_font(max(52, w // 14))
    lines = _wrap_text(product.upper(), name_font, int(w * 0.84), draw)
    _draw_centered_text(draw, lines, name_font, w, int(h * 0.48),
                        fill=(255, 255, 255), stroke=4, line_gap=18)

    # Subtle divider
    div_y = int(h * 0.72)
    draw.line([(int(w * 0.3), div_y), (int(w * 0.7), div_y)],
              fill=accent, width=max(2, h // 300))

    return np.array(img)


def _card_hook(hook: str, niche: str, size: tuple[int, int]) -> np.ndarray:
    """Slide 2 — hook text, slightly brighter gradient for visual contrast."""
    w, h = size
    top, bot = _NICHE_COLOURS.get(niche, _DEFAULT_COLOURS)
    # Brighten top slightly
    top = tuple(min(255, int(c * 1.6)) for c in top)  # type: ignore[assignment]
    accent = _ACCENT.get(niche, _DEFAULT_ACCENT)
    img = _gradient_bg(size, top, bot)
    draw = ImageDraw.Draw(img)

    # Quotation mark / opener
    qt_font = _load_font(max(80, w // 9))
    draw.text((w // 2, int(h * 0.22)), "“", font=qt_font, fill=accent,
              anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))

    hook_font = _load_font(max(56, w // 13))
    lines = _wrap_text(hook.strip('"').strip("'"), hook_font, int(w * 0.82), draw)
    _draw_centered_text(draw, lines, hook_font, w, int(h * 0.50),
                        fill=(255, 255, 255), stroke=4, line_gap=20)

    return np.array(img)


def _card_problem(problem: str, niche: str, size: tuple[int, int]) -> np.ndarray:
    """Slide 3 — problem statement, darker and more urgent palette."""
    w, h = size
    top, bot = _NICHE_COLOURS.get(niche, _DEFAULT_COLOURS)
    # Darken for tension
    top = tuple(max(0, int(c * 0.7)) for c in top)  # type: ignore[assignment]
    accent = _ACCENT.get(niche, _DEFAULT_ACCENT)
    img = _gradient_bg(size, top, bot)
    draw = ImageDraw.Draw(img)

    label_font = _load_font(max(32, w // 24))
    draw.text((w // 2, int(h * 0.16)), "THE PROBLEM", font=label_font,
              fill=accent, anchor="mm", stroke_width=1, stroke_fill=(0, 0, 0))

    prob_font = _load_font(max(48, w // 16))
    lines = _wrap_text(problem, prob_font, int(w * 0.82), draw)
    _draw_centered_text(draw, lines, prob_font, w, int(h * 0.50),
                        fill=(255, 230, 230), stroke=3, line_gap=16)

    return np.array(img)


def _card_solution(product: str, niche: str, size: tuple[int, int]) -> np.ndarray:
    """Slide 4 — product as the solution, bright accent emphasis."""
    w, h = size
    top, bot = _NICHE_COLOURS.get(niche, _DEFAULT_COLOURS)
    accent = _ACCENT.get(niche, _DEFAULT_ACCENT)
    img = _gradient_bg(size, top, bot)
    draw = ImageDraw.Draw(img)

    label_font = _load_font(max(32, w // 24))
    draw.text((w // 2, int(h * 0.16)), "THE SOLUTION", font=label_font,
              fill=accent, anchor="mm", stroke_width=1, stroke_fill=(0, 0, 0))

    # Accent highlight box behind product name
    name_font = _load_font(max(50, w // 15))
    lines = _wrap_text(product, name_font, int(w * 0.80), draw)
    _draw_centered_text(draw, lines, name_font, w, int(h * 0.50),
                        fill=accent, stroke=4, line_gap=18)

    # Checkmark row
    chk_font = _load_font(max(36, w // 22))
    draw.text((w // 2, int(h * 0.76)), "✓  Real product  ✓  Amazon", font=chk_font,
              fill=(200, 255, 200), anchor="mm", stroke_width=1, stroke_fill=(0, 0, 0))

    return np.array(img)


def _card_cta(cta: str, affiliate_url: str, niche: str, size: tuple[int, int]) -> np.ndarray:
    """Slide 5 — call to action, maximum contrast and urgency."""
    w, h = size
    accent = _ACCENT.get(niche, _DEFAULT_ACCENT)
    # Nearly black background for CTA contrast
    img = _gradient_bg(size, (8, 8, 16), (4, 4, 8))
    draw = ImageDraw.Draw(img)

    # Thick accent bar
    bar_h = max(10, h // 80)
    draw.rectangle([0, 0, w, bar_h], fill=accent)
    draw.rectangle([0, h - bar_h, w, h], fill=accent)

    action_font = _load_font(max(64, w // 11))
    lines = _wrap_text(cta, action_font, int(w * 0.82), draw)
    _draw_centered_text(draw, lines, action_font, w, int(h * 0.44),
                        fill=(255, 255, 255), stroke=5, line_gap=20)

    sub = "link in description" if not affiliate_url else "tap the link below"
    sub_font = _load_font(max(38, w // 20))
    draw.text((w // 2, int(h * 0.68)), sub.upper(), font=sub_font,
              fill=accent, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))

    return np.array(img)


def generate_product_cards(
    product: str,
    niche: str,
    hook: str,
    problem: str,
    cta: str,
    affiliate_url: str,
    size: tuple[int, int] = DEFAULT_VIDEO_SIZE,
) -> list[np.ndarray]:
    """Return 5 styled RGB numpy arrays (one per slide)."""
    return [
        _card_product(product, niche, size),
        _card_hook(hook, niche, size),
        _card_problem(problem, niche, size),
        _card_solution(product, niche, size),
        _card_cta(cta, affiliate_url, niche, size),
    ]


# ── Ken Burns per-slide clip ───────────────────────────────────────────────────

def _ken_burns_clip(
    img_arr: np.ndarray,
    duration: float,
    canvas_size: tuple[int, int],
    fps: int = DEFAULT_FPS,
    zoom_start: float = 1.00,
    zoom_end: float = 1.07,
    drift_px: int = 10,
):
    """Wrap a static image array in a Ken Burns video clip (no audio)."""
    from moviepy import ColorClip, CompositeVideoClip, ImageClip

    cw, ch = canvas_size
    img = ImageClip(img_arr).with_duration(duration)
    src_w, src_h = img.size

    fill = max(cw / src_w, ch / src_h)
    base_scale = fill * zoom_end * 1.01

    def _zoom(t: float) -> float:
        progress = t / max(duration, 0.001)
        eased = (1.0 - math.cos(math.pi * progress)) / 2.0
        rel = zoom_start / zoom_end + (1.0 - zoom_start / zoom_end) * eased
        return base_scale * rel

    img = img.resized(_zoom)

    def _pos(t: float):
        progress = t / max(duration, 0.001)
        eased = (1.0 - math.cos(math.pi * progress)) / 2.0
        rel = zoom_start / zoom_end + (1.0 - zoom_start / zoom_end) * eased
        scale = base_scale * rel
        w = int(src_w * scale)
        h = int(src_h * scale)
        drift = drift_px * math.sin(math.pi * progress)
        return ((cw - w) / 2 + drift, (ch - h) / 2)

    img = img.with_position(_pos)
    bg = ColorClip(size=canvas_size, color=(0, 0, 0)).with_duration(duration)
    return CompositeVideoClip([bg, img], size=canvas_size).with_duration(duration)


# ── Slideshow builder ─────────────────────────────────────────────────────────

def build_slideshow(
    cards: list[np.ndarray],
    duration_sec: float,
    video_size: tuple[int, int] = DEFAULT_VIDEO_SIZE,
    fps: int = DEFAULT_FPS,
    min_clip_sec: float = 2.0,
    max_clip_sec: float = 5.0,
    out_path: Path | None = None,
) -> Path:
    """Concatenate Ken Burns clips from `cards` into a silent MP4.

    Each card gets equal screen time, clamped to [min_clip_sec, max_clip_sec].
    If the total card time doesn't fill duration_sec, the last card loops.
    Returns the output path (suitable as avatar_video for compose()).
    """
    from moviepy import concatenate_videoclips

    ensure_dirs()
    if out_path is None:
        out_path = OUT_RAW_AVATAR / f"product_slideshow_{int(time.time())}.mp4"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = len(cards)
    if n == 0:
        raise ValueError("No cards provided to build_slideshow")

    clip_dur = max(min_clip_sec, min(max_clip_sec, duration_sec / n))

    clips = []
    total = 0.0
    idx = 0
    # Fill duration_sec by cycling through cards as needed
    while total < duration_sec - 0.05:
        remaining = duration_sec - total
        dur = min(clip_dur, remaining)
        if dur < 0.2:
            break
        card = cards[idx % n]
        clips.append(_ken_burns_clip(card, dur, video_size, fps))
        total += dur
        idx += 1

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        str(out_path),
        fps=fps,
        codec="libx264",
        preset="medium",
        audio=False,
        threads=4,
        logger=None,
    )
    for c in clips:
        c.close()
    final.close()
    return out_path


# ── Real-image slideshow ───────────────────────────────────────────────────────

def _fit_image_vertical(img: "Image.Image", size: tuple[int, int]) -> np.ndarray:
    """Fit any aspect-ratio image to a 9:16 canvas.

    Strategy: blurred + darkened version fills the canvas; crisp original
    is scaled to fill the canvas width and composited centered on top.
    This avoids letterboxing and looks like real TikTok product content.
    """
    from PIL import Image as _PILImage

    cw, ch = size
    img = img.convert("RGB")

    # Background: upscale to canvas, heavy blur, darken
    bg = img.resize((cw, ch), _PILImage.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=24))
    bg_arr = (np.array(bg) * 0.30).astype(np.uint8)
    bg = _PILImage.fromarray(bg_arr)

    # Foreground: scale to fill canvas width
    src_w, src_h = img.size
    scale = cw / src_w
    new_h = int(src_h * scale)
    fg = img.resize((cw, new_h), _PILImage.LANCZOS)

    if new_h >= ch:
        # Taller than canvas — center-crop vertically
        y_off = (new_h - ch) // 2
        fg = fg.crop((0, y_off, cw, y_off + ch))
        return np.array(fg)

    canvas = bg.copy()
    y_off = (ch - new_h) // 2
    canvas.paste(fg, (0, y_off))
    return np.array(canvas)


def build_slideshow_from_images(
    image_paths: list["Path"],
    duration_sec: float,
    video_size: tuple[int, int] = DEFAULT_VIDEO_SIZE,
    fps: int = DEFAULT_FPS,
    min_clip_sec: float = 2.0,
    max_clip_sec: float = 4.0,
    out_path: "Path | None" = None,
) -> "Path":
    """Build a real-image Ken Burns slideshow (silent MP4, canvas-sized).

    Each image is fitted to 9:16 with blurred-background fill, then wrapped
    in a Ken Burns clip. Zoom and drift direction alternate per clip for
    visual variety. Suitable as avatar_video for compose(skip_fit=True).
    """
    from pathlib import Path as _Path
    from moviepy import concatenate_videoclips
    from PIL import Image as _PILImage

    ensure_dirs()
    if out_path is None:
        out_path = OUT_RAW_AVATAR / f"product_real_{int(time.time())}.mp4"
    out_path = _Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = len(image_paths)
    if n == 0:
        raise ValueError("No images provided to build_slideshow_from_images")

    clip_dur = max(min_clip_sec, min(max_clip_sec, duration_sec / n))

    # Alternating Ken Burns directions for variety
    _ZOOM_PATTERNS = [
        (1.00, 1.08, 10),   # zoom in, drift right
        (1.08, 1.00, -10),  # zoom out, drift left
        (1.02, 1.09, 8),    # zoom in faster
        (1.09, 1.02, -8),   # zoom out, drift left
    ]

    clips = []
    total = 0.0
    idx = 0
    while total < duration_sec - 0.05:
        remaining = duration_sec - total
        dur = min(clip_dur, remaining)
        if dur < 0.2:
            break

        img_path = image_paths[idx % n]
        try:
            img = _PILImage.open(img_path).convert("RGB")
        except Exception:
            idx += 1
            continue

        arr = _fit_image_vertical(img, video_size)
        zs, ze, drift = _ZOOM_PATTERNS[idx % len(_ZOOM_PATTERNS)]
        clips.append(_ken_burns_clip(arr, dur, video_size, fps,
                                     zoom_start=zs, zoom_end=ze, drift_px=drift))
        total += dur
        idx += 1

    if not clips:
        raise ValueError("No clips generated from images")

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        str(out_path),
        fps=fps,
        codec="libx264",
        preset="medium",
        audio=False,
        threads=4,
        logger=None,
    )
    for c in clips:
        c.close()
    final.close()
    return out_path
