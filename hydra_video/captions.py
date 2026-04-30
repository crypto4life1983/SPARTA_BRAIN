"""Caption + hook + CTA clips for Hydra Video.

Three families of overlay produced from edge-tts WordBoundary timings:

  * make_caption_clips     - the regular per-chunk subtitle stream
  * make_hook_clip         - giant centered hook text for the opening
  * make_cta_clip          - end-of-video call-to-action card

All three render the text with PIL (so font handling is reliable on
Windows) and wrap the result as a MoviePy ImageClip with explicit
start/end times. Keyword highlighting tints conversion-relevant words
yellow inside caption chunks.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .style import CLEAN, StyleConfig


# Stock high-value words that get highlighted yellow inside captions.
# Conversion lift > prettiness here - we want the eye to snag on these.
HIGHLIGHT_WORDS = {
    "free", "money", "save", "today", "now", "link", "check",
    "secret", "win", "viral", "best", "first", "limited", "only",
    "instant", "fast", "huge", "real", "proven", "deal", "off",
    "discount", "cashback", "bonus", "exclusive", "new",
}

_PUNCT_STRIP = re.compile(r"[^\w]+")


def _normalize_for_highlight(word: str) -> str:
    return _PUNCT_STRIP.sub("", word).lower()


def _is_highlight(word: str) -> bool:
    norm = _normalize_for_highlight(word)
    if not norm:
        return False
    if norm in HIGHLIGHT_WORDS:
        return True
    # ALL-CAPS word in source = author wanted emphasis
    bare = re.sub(r"[^A-Za-z]", "", word)
    return len(bare) >= 2 and bare.isupper()


def _load_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _chunk_words(timings: list[dict], max_words: int) -> list[dict]:
    """Group word timings into short chunks for captioning."""
    if not timings:
        return []
    chunks: list[dict] = []
    buf: list[dict] = []
    min_words = max(2, max_words - 2)
    for w in timings:
        buf.append(w)
        token = w["word"].strip()
        terminal = token.endswith((".", "!", "?", ",", ";", ":"))
        if len(buf) >= max_words or (terminal and len(buf) >= min_words):
            chunks.append({
                "words": [b["word"].strip() for b in buf],
                "start": buf[0]["start"],
                "end": buf[-1]["end"],
            })
            buf = []
    if buf:
        chunks.append({
            "words": [b["word"].strip() for b in buf],
            "start": buf[0]["start"],
            "end": buf[-1]["end"],
        })
    return chunks


def _draw_word_run(
    draw: ImageDraw.ImageDraw,
    words: list[str],
    font: ImageFont.ImageFont,
    canvas_size: tuple[int, int],
    y_anchor: float,
    upper: bool = True,
    fill_default: tuple[int, int, int, int] = (255, 255, 255, 255),
    fill_highlight: tuple[int, int, int, int] = (255, 220, 70, 255),
    stroke_width: int = 4,
    max_width_pct: float = 0.88,
    line_gap: int = 14,
    highlight_first: bool = False,
) -> None:
    """Word-wrap `words` and draw them centered, highlighting any hits.

    `y_anchor` is the vertical center of the text block (fraction of h).
    `highlight_first` forces the first word yellow regardless of content."""
    w, h = canvas_size
    max_w = int(w * max_width_pct)
    space_w = draw.textbbox((0, 0), " ", font=font, stroke_width=stroke_width)[2]

    # Pre-measure each word so we can wrap into lines.
    measured = []
    for i, word in enumerate(words):
        text = (word.upper() if upper else word)
        bb = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        measured.append({
            "text": text,
            "raw": word,
            "w": bb[2] - bb[0],
            "h": bb[3] - bb[1],
            "highlight": _is_highlight(word) or (highlight_first and i == 0),
        })

    lines: list[list[dict]] = [[]]
    line_w = 0
    for m in measured:
        candidate = m["w"] if not lines[-1] else line_w + space_w + m["w"]
        if candidate > max_w and lines[-1]:
            lines.append([m])
            line_w = m["w"]
        else:
            lines[-1].append(m)
            line_w = candidate

    line_heights = [max((m["h"] for m in line), default=0) for line in lines]
    block_h = sum(line_heights) + max(0, len(lines) - 1) * line_gap
    y = int(h * y_anchor) - block_h // 2

    for line, lh in zip(lines, line_heights):
        if not line:
            continue
        line_total_w = sum(m["w"] for m in line) + space_w * (len(line) - 1)
        x = (w - line_total_w) // 2
        for i, m in enumerate(line):
            color = fill_highlight if m["highlight"] else fill_default
            draw.text((x, y), m["text"], font=font,
                      fill=color, stroke_width=stroke_width,
                      stroke_fill=(0, 0, 0, 255))
            x += m["w"] + (space_w if i < len(line) - 1 else 0)
        y += lh + line_gap


def _render_caption_png(
    chunk_words: list[str],
    canvas_size: tuple[int, int],
    font_size: int,
) -> np.ndarray:
    # Scale all pixel measurements proportionally with canvas width so the
    # same StyleConfig values produce correctly-sized text at any resolution.
    # 720 is the reference width at which the font sizes were originally tuned.
    scale = max(1.0, canvas_size[0] / 720.0)
    scaled_font = max(24, int(font_size * scale))
    stroke = max(2, int(4 * scale))
    gap = max(8, int(14 * scale))

    w, h = canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _load_font(scaled_font)
    _draw_word_run(
        draw, chunk_words, font, canvas_size,
        y_anchor=0.80,          # lower-third: clear of face, TikTok position
        upper=True,
        stroke_width=stroke,
        line_gap=gap,
        highlight_first=True,   # first word always yellow
    )
    return np.array(img)


def _render_hook_png(
    text: str,
    canvas_size: tuple[int, int],
    font_size: int,
) -> np.ndarray:
    scale = max(1.0, canvas_size[0] / 720.0)
    scaled_font = max(32, int(font_size * scale))
    stroke = max(4, int(6 * scale))
    halo_stroke = max(10, int(14 * scale))
    blur_r = max(8, int(12 * scale))
    gap = max(10, int(16 * scale))

    w, h = canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _load_font(scaled_font)
    _draw_word_run(draw, text.split(), font, canvas_size,
                   y_anchor=0.45, upper=True,
                   stroke_width=stroke, line_gap=gap)
    # Soft shadow halo for that "produced" feel.
    halo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    _draw_word_run(halo_draw, text.split(), font, canvas_size,
                   y_anchor=0.45, upper=True,
                   fill_default=(0, 0, 0, 180),
                   fill_highlight=(0, 0, 0, 180),
                   stroke_width=halo_stroke, line_gap=gap)
    halo = halo.filter(ImageFilter.GaussianBlur(radius=blur_r))
    out = Image.alpha_composite(halo, img)
    return np.array(out)


def _render_cta_png(
    text: str,
    canvas_size: tuple[int, int],
    font_size: int,
) -> np.ndarray:
    """Lower-third CTA card: rounded translucent background + big text.

    Font auto-reduces until the text block fits inside the card's inner
    area, so no clipping regardless of input length.
    """
    scale = max(1.0, canvas_size[0] / 720.0)
    # Hard cap: never exceed 5% of canvas height (96px at 1920)
    scaled_font = min(max(28, int(font_size * scale)), int(canvas_size[1] * 0.05))
    stroke = max(2, int(3 * scale))
    radius = max(16, int(28 * scale))
    gap = max(8, int(12 * scale))
    v_pad = max(24, int(36 * scale))  # vertical padding inside card

    w, h = canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # Card: positioned in the lower 30% with safe margins from screen edge
    card_w = int(w * 0.86)
    card_x = (w - card_w) // 2
    card_top_y = int(h * 0.65)
    card_bot_y = int(h * 0.90)       # leaves 10% gap at bottom of screen
    inner_h = card_bot_y - card_top_y - 2 * v_pad

    # Auto-reduce font until text fits within the inner card height.
    # Uses the same greedy word-wrap as _draw_word_run to measure accurately.
    probe_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    probe_draw = ImageDraw.Draw(probe_img)
    max_text_w = int(card_w * 0.88)
    for _ in range(6):
        font = _load_font(scaled_font)
        space_w = probe_draw.textbbox((0, 0), " ", font=font)[2]
        words_upper = text.upper().split()
        lines_acc: list[list[str]] = [[]]
        cur_w = 0
        for word in words_upper:
            bb = probe_draw.textbbox((0, 0), word, font=font)
            ww = bb[2] - bb[0]
            cand = ww if not lines_acc[-1] else cur_w + space_w + ww
            if cand > max_text_w and lines_acc[-1]:
                lines_acc.append([word])
                cur_w = ww
            else:
                lines_acc[-1].append(word)
                cur_w = cand
        line_hs = [
            max(
                (probe_draw.textbbox((0, 0), t, font=font)[3]
                 - probe_draw.textbbox((0, 0), t, font=font)[1])
                for t in line
            )
            for line in lines_acc if line
        ]
        total_text_h = sum(line_hs) + gap * max(0, len(line_hs) - 1)
        if total_text_h <= inner_h:
            break
        scaled_font = max(24, int(scaled_font * 0.82))

    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle(
        [card_x, card_top_y, card_x + card_w, card_bot_y],
        radius=radius,
        fill=(20, 22, 30, 220),
    )
    img = Image.alpha_composite(img, card)

    draw = ImageDraw.Draw(img)
    font = _load_font(scaled_font)
    _draw_word_run(draw, text.split(), font, canvas_size,
                   y_anchor=(card_top_y + card_bot_y) / 2 / h,
                   upper=True,
                   fill_default=(255, 255, 255, 255),
                   fill_highlight=(255, 220, 70, 255),
                   stroke_width=stroke,
                   max_width_pct=0.82,
                   line_gap=gap)
    return np.array(img)


def make_caption_clips(
    word_timings: list[dict],
    video_size: tuple[int, int],
    style: StyleConfig = CLEAN,
    skip_before: float = 0.0,
    skip_after: float | None = None,
):
    """Per-chunk caption ImageClips with start/end + optional fade-in."""
    from moviepy import ImageClip

    chunks = _chunk_words(word_timings, max_words=style.chunk_max_words)
    clips = []
    for ch in chunks:
        if ch["start"] < skip_before - 0.05:
            continue
        if skip_after is not None and ch["start"] > skip_after - 0.05:
            continue
        if not ch["words"]:
            continue
        arr = _render_caption_png(ch["words"], video_size, style.caption_font_size)
        clip = (
            ImageClip(arr, transparent=True)
            .with_start(ch["start"])
            .with_end(ch["end"])
        )
        if style.caption_fade_sec > 0:
            try:
                from moviepy.video.fx import CrossFadeIn
                clip = clip.with_effects([CrossFadeIn(style.caption_fade_sec)])
            except Exception:  # noqa: BLE001
                pass
        clips.append(clip)
    return clips


def make_hook_clip(
    hook_text: str,
    video_size: tuple[int, int],
    start: float,
    end: float,
    style: StyleConfig = CLEAN,
):
    """Big centered hook overlay for the opening seconds.

    Returns None if the hook is empty or has no time to live."""
    from moviepy import ImageClip

    if not hook_text or not hook_text.strip():
        return None
    if end - start < 0.4:
        return None
    arr = _render_hook_png(hook_text, video_size, style.hook_font_size)
    clip = (
        ImageClip(arr, transparent=True)
        .with_start(start)
        .with_end(end)
    )
    if style.hook_fade_sec > 0:
        try:
            from moviepy.video.fx import CrossFadeIn, CrossFadeOut
            clip = clip.with_effects([
                CrossFadeIn(style.hook_fade_sec),
                CrossFadeOut(style.hook_fade_sec),
            ])
        except Exception:  # noqa: BLE001
            pass
    return clip


def make_cta_clip(
    cta_text: str,
    video_size: tuple[int, int],
    start: float,
    end: float,
    style: StyleConfig = CLEAN,
):
    """End-of-video CTA card. Returns None if there's no room."""
    from moviepy import ImageClip

    if not cta_text or not cta_text.strip():
        return None
    if end - start < 0.4:
        return None
    arr = _render_cta_png(cta_text, video_size, style.cta_font_size)
    clip = (
        ImageClip(arr, transparent=True)
        .with_start(start)
        .with_end(end)
    )
    if style.cta_fade_sec > 0:
        try:
            from moviepy.video.fx import CrossFadeIn, CrossFadeOut
            clip = clip.with_effects([
                CrossFadeIn(style.cta_fade_sec),
                CrossFadeOut(style.cta_fade_sec),
            ])
        except Exception:  # noqa: BLE001
            pass
    return clip
