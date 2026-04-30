"""Avatar prep for Hydra Video.

Resolves the avatar source image. If the user has dropped a real photo at
`assets/avatars/avatar.jpg` (or passed an explicit path), we resize it to
the target canvas. Otherwise we synthesize a deterministic gradient
placeholder so the pipeline never breaks on a fresh install.

Swap-point: a future face-detection / framing module can replace
`prepare_avatar` while keeping the same signature.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import (
    AVATARS_DIR, DEFAULT_AVATAR, DEFAULT_VIDEO_SIZE,
    OUT_RAW_AVATAR, ensure_dirs,
)


def _generate_placeholder(size: tuple[int, int], out_path: Path) -> Path:
    """Render a gradient + silhouette placeholder PNG."""
    w, h = size
    img = Image.new("RGB", (w, h), "#0b1020")
    draw = ImageDraw.Draw(img)

    # Vertical gradient: top dark blue -> bottom near-black
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(11 + (5 - 11) * t)
        g = int(16 + (8 - 16) * t)
        b = int(32 + (16 - 32) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Soft silhouette: head circle + shoulder arc
    cx, cy = w // 2, int(h * 0.42)
    head_r = int(min(w, h) * 0.16)
    draw.ellipse(
        [cx - head_r, cy - head_r, cx + head_r, cy + head_r],
        fill=(35, 48, 80),
    )
    sh_w = int(w * 0.65)
    sh_h = int(h * 0.32)
    sh_y = cy + head_r - 10
    draw.ellipse(
        [cx - sh_w // 2, sh_y, cx + sh_w // 2, sh_y + sh_h],
        fill=(28, 40, 70),
    )

    img = img.filter(ImageFilter.GaussianBlur(radius=1.4))

    # Label so it's obvious this is a placeholder
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
    except OSError:
        font = ImageFont.load_default()
    label = "AVATAR PLACEHOLDER"
    bbox = ImageDraw.Draw(img).textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    ImageDraw.Draw(img).text(
        ((w - tw) // 2, int(h * 0.82)),
        label, fill=(180, 200, 230), font=font,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def prepare_avatar(
    avatar_path: str | Path | None = None,
    size: tuple[int, int] = DEFAULT_VIDEO_SIZE,
    out_path: Path | None = None,
) -> Path:
    """Return a path to a portrait-sized avatar image ready for lipsync.

    Resolution order:
      1. explicit `avatar_path` (if file exists)
      2. `assets/avatars/avatar.jpg` (the convention)
      3. generated gradient placeholder
    """
    ensure_dirs()
    if out_path is None:
        out_path = OUT_RAW_AVATAR / "avatar_prepared.png"
    out_path = Path(out_path)

    src: Path | None = None
    if avatar_path:
        p = Path(avatar_path)
        if p.exists():
            src = p
    if src is None and DEFAULT_AVATAR.exists():
        src = DEFAULT_AVATAR
    # Tolerate a different extension at the conventional location
    if src is None:
        for cand in AVATARS_DIR.glob("avatar.*"):
            if cand.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                src = cand
                break

    if src is None:
        return _generate_placeholder(size, out_path)

    img = Image.open(src).convert("RGB")
    # Cover-fit into target canvas without stretching
    iw, ih = img.size
    tw, th = size
    src_ratio = iw / ih
    dst_ratio = tw / th
    if src_ratio > dst_ratio:
        new_h = th
        new_w = int(round(new_h * src_ratio))
    else:
        new_w = tw
        new_h = int(round(new_w / src_ratio))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - tw) // 2
    # Bias the vertical crop upward by ~8% of canvas height so the face
    # sits in the upper-center of the frame rather than dead center.
    # Clamped to [0, new_h - th] so we never crop outside the image.
    raw_top = (new_h - th) // 2 - int(th * 0.08)
    top = max(0, min(raw_top, new_h - th))
    img = img.crop((left, top, left + tw, top + th))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path
