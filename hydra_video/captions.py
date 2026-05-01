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
    force_default_idx: int | None = None,
) -> None:
    """Word-wrap `words` and draw them centered, highlighting any hits.

    `y_anchor` is the vertical center of the text block (fraction of h).
    `highlight_first` forces the first word yellow regardless of content.
    `force_default_idx` pins that word index to fill_default (white) even if
    it would normally be highlighted — used for visual hierarchy in hooks."""
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
            "highlight": (
                (_is_highlight(word) or (highlight_first and i == 0))
                and i != force_default_idx
            ),
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
    words = text.split()
    # Longest alphabetic word gets white — creates yellow/white hierarchy without
    # semantic guessing. Skips single-char words (I, A) so the contrast lands on
    # a visually substantial word.
    key_idx: int | None = None
    if len(words) > 1:
        key_idx = max(
            (i for i in range(len(words)) if len(re.sub(r"[^A-Za-z]", "", words[i])) >= 2),
            key=lambda i: len(re.sub(r"[^A-Za-z]", "", words[i])),
            default=None,
        )

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _load_font(scaled_font)
    _draw_word_run(draw, words, font, canvas_size,
                   y_anchor=0.45, upper=True,
                   stroke_width=stroke, line_gap=gap,
                   force_default_idx=key_idx)
    # Soft shadow halo for that "produced" feel.
    halo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    _draw_word_run(halo_draw, words, font, canvas_size,
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
    sub_text: str = "",
) -> np.ndarray:
    """Lower-third CTA card: rounded translucent background + big text.

    Optionally renders a smaller secondary line (sub_text) beneath the
    main action text — e.g. "(link in description)".
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

    # With sub_text, shift the main block upward to leave room for sub-line.
    sub_font_size = max(18, int(scaled_font * 0.52))
    sub_font = _load_font(sub_font_size) if sub_text else None
    sub_h = (draw.textbbox((0, 0), sub_text, font=sub_font)[3]
             - draw.textbbox((0, 0), sub_text, font=sub_font)[1]) if sub_font else 0
    sub_gap = max(10, int(16 * scale))

    # Main text y_anchor: center of card, shifted up by half sub_text height
    main_center_y = (card_top_y + card_bot_y) / 2
    if sub_font:
        main_center_y -= (sub_h + sub_gap) / 2

    _draw_word_run(draw, text.split(), font, canvas_size,
                   y_anchor=main_center_y / h,
                   upper=True,
                   fill_default=(255, 255, 255, 255),
                   fill_highlight=(255, 220, 70, 255),
                   stroke_width=stroke,
                   max_width_pct=0.82,
                   line_gap=gap)

    # Secondary line: smaller, muted, centered near bottom of card
    if sub_font and sub_text:
        sub_y = int(card_bot_y - v_pad - sub_h)
        bb = draw.textbbox((0, 0), sub_text, font=sub_font)
        sub_x = (w - (bb[2] - bb[0])) // 2
        draw.text(
            (sub_x, sub_y), sub_text, font=sub_font,
            fill=(190, 190, 210, 220),
            stroke_width=max(1, stroke - 1),
            stroke_fill=(0, 0, 0, 180),
        )

    return np.array(img)


PAYOFF_BY_NICHE: dict[str, str] = {
    "productivity":     "GAME CHANGER",
    "business":         "THIS ACTUALLY WORKS",
    "ai":               "I DIDN'T EXPECT THIS",
    "work_from_home":   "THIS CHANGED EVERYTHING",
    "content_creation": "TOTAL GAME CHANGER",
}

# Each entry: (keyword_list, payoff_phrase). First match wins.
# Keywords are checked against the lowercased product name.
_PAYOFF_PRODUCT_PATTERNS: list[tuple[list[str], str]] = [
    (["cable", "cord", "organizer", "wire management"],  "DESK = FINALLY CLEAN"),
    (["monitor light", "bias light", "screen light"],    "NO MORE EYE STRAIN"),
    (["webcam", "web cam"],                              "CRYSTAL CLEAR CALLS"),
    (["gpu", "graphics card", "video card"],             "NO MORE CLOUD FEES"),
    (["standing desk", "sit-stand", "height-adj"],       "BACK PAIN = GONE"),
    (["keyboard", "mechanical"],                         "TYPING FEELS PREMIUM"),
    (["ergonomic mouse", "vertical mouse"],              "ZERO WRIST PAIN"),
    (["headset", "headphones", "earbuds", "earphones"],  "CALLS SOUND CRISP"),
    (["microphone", " mic "],                            "YOU SOUND PROFESSIONAL"),
    (["ssd", "nvme", "hard drive", "storage drive"],     "STORAGE = SOLVED"),
    (["planner", "bullet journal", "notebook"],          "PLANS ACTUALLY HAPPEN"),
    (["credit card", "cashback", "rewards card"],        "MONEY BACK EVERY TIME"),
    (["scanner", "document scan"],                       "PAPER CLUTTER = GONE"),
    (["printer"],                                        "PRINTS IN SECONDS"),
    (["charger", "power bank", "usb-c hub"],             "ALWAYS FULLY CHARGED"),
    (["monitor", "display", "screen", "external screen"], "EYES THANK YOU"),
    (["chair", "lumbar", "seat cushion"],                "BACK PAIN = DONE"),
    (["desk lamp", "desk light"],                        "PERFECT LIGHTING"),
    (["laptop stand", "monitor stand", "riser"],         "POSTURE = FIXED"),
    (["mouse", "trackpad"],                              "ZERO WRIST FATIGUE"),
    (["camera", "ring light", "key light", "studio light"], "YOU LOOK PROFESSIONAL"),
    (["software", "subscription", "tool"],               "HOURS SAVED DAILY"),
]


def pick_payoff(product: str, niche: str) -> str:
    """Return the tightest payoff phrase for this specific product.

    Tries each keyword pattern against the product name (case-insensitive).
    Falls back to the niche phrase, then the global default."""
    lower = " " + product.lower() + " "
    for keywords, phrase in _PAYOFF_PRODUCT_PATTERNS:
        if any(kw in lower for kw in keywords):
            return phrase
    return PAYOFF_BY_NICHE.get(niche, "GAME CHANGER")


def _render_payoff_png(
    text: str,
    canvas_size: tuple[int, int],
    font_size: int,
) -> np.ndarray:
    """Mid-video payoff line — white text, vertically centered, distinct from
    the yellow flash interrupts so it reads as a content beat, not noise."""
    scale = max(1.0, canvas_size[0] / 720.0)
    scaled_font = max(36, int(font_size * scale))
    stroke = max(3, int(5 * scale))
    gap = max(8, int(12 * scale))

    w, h = canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _load_font(scaled_font)
    _draw_word_run(
        draw, text.split(), font, canvas_size,
        y_anchor=0.42,
        upper=True,
        fill_default=(255, 255, 255, 255),
        fill_highlight=(255, 255, 255, 255),
        stroke_width=stroke,
        line_gap=gap,
    )
    return np.array(img)


def make_payoff_clip(
    text: str,
    video_size: tuple[int, int],
    start: float,
    end: float,
    style: StyleConfig = CLEAN,
):
    """Single mid-video retention beat — white, centered, 0.8–1.0s duration.

    Returns None if text is empty or there is no room."""
    from moviepy import ImageClip

    if not text or not text.strip() or end - start < 0.3:
        return None
    font_size = max(52, int(style.hook_font_size * 0.72))
    arr = _render_payoff_png(text, video_size, font_size)
    clip = (
        ImageClip(arr, transparent=True)
        .with_start(start)
        .with_end(end)
    )
    if style.caption_fade_sec > 0:
        try:
            from moviepy.video.fx import CrossFadeIn, CrossFadeOut
            clip = clip.with_effects([
                CrossFadeIn(style.caption_fade_sec),
                CrossFadeOut(style.caption_fade_sec),
            ])
        except Exception:  # noqa: BLE001
            pass
    return clip


_FLASH_CYCLE = ["WAIT.", "REAL TALK.", "SERIOUSLY?", "NO JOKE.", "FACTS.", "LOOK."]


def _render_flash_png(
    text: str,
    canvas_size: tuple[int, int],
    font_size: int,
) -> np.ndarray:
    """Upper-center interrupt flash — bright yellow, bold stroke."""
    scale = max(1.0, canvas_size[0] / 720.0)
    scaled_font = max(32, int(font_size * scale))
    stroke = max(3, int(5 * scale))
    gap = max(8, int(12 * scale))

    w, h = canvas_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _load_font(scaled_font)
    _draw_word_run(
        draw, text.split(), font, canvas_size,
        y_anchor=0.22,
        upper=True,
        fill_default=(255, 220, 50, 255),
        fill_highlight=(255, 220, 50, 255),
        stroke_width=stroke,
        line_gap=gap,
    )
    return np.array(img)


def make_flash_clips(
    duration: float,
    video_size: tuple[int, int],
    style: StyleConfig = CLEAN,
    interval_sec: float = 3.5,
    flash_dur: float = 0.40,
    skip_before: float = 0.0,
    skip_after: float | None = None,
):
    """Short pattern-interrupt text flashes every interval_sec seconds.

    Cycles through _FLASH_CYCLE words (WAIT. / REAL TALK. / etc.) as bright
    yellow upper-center overlays lasting flash_dur seconds each. Fires only
    between skip_before and skip_after so it never clashes with hook or CTA.
    """
    from moviepy import ImageClip

    clips = []
    end_bound = (skip_after if skip_after is not None else duration) - 0.5
    font_size = max(48, int(style.hook_font_size * 0.65))

    t = skip_before + interval_sec
    idx = 0
    while t + flash_dur <= end_bound:
        word = _FLASH_CYCLE[idx % len(_FLASH_CYCLE)]
        arr = _render_flash_png(word, video_size, font_size)
        clips.append(
            ImageClip(arr, transparent=True)
            .with_start(t)
            .with_end(t + flash_dur)
        )
        t += interval_sec
        idx += 1

    return clips


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
    sub_text: str = "",
):
    """End-of-video CTA card. Returns None if there's no room."""
    from moviepy import ImageClip

    if not cta_text or not cta_text.strip():
        return None
    if end - start < 0.4:
        return None
    arr = _render_cta_png(cta_text, video_size, style.cta_font_size, sub_text=sub_text)
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
    # Scale-in "button arrival": 0.96 → 1.00 in 130 ms, ease-out cubic.
    # The clip is full-canvas RGBA; scaling it slightly and centering creates
    # a subtle pop-in that makes the card feel interactive.
    try:
        _anim = 0.15
        def _cta_scale(t: float) -> float:
            p = min(t / _anim, 1.0)
            return 0.96 + 0.04 * (1.0 - (1.0 - p) ** 3)
        clip = clip.resized(_cta_scale).with_position('center')
    except Exception:  # noqa: BLE001
        pass
    return clip
