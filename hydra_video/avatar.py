"""Avatar prep for Hydra Video.

Resolves the avatar source image. If the user has dropped a real photo at
`assets/avatars/avatar.jpg` (or passed an explicit path), we resize it to
the target canvas. Otherwise we synthesize a deterministic gradient
placeholder so the pipeline never breaks on a fresh install.

Swap-point: a future face-detection / framing module can replace
`prepare_avatar` while keeping the same signature.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from . import (
    AVATARS_DIR, DEFAULT_AVATAR, DEFAULT_VIDEO_SIZE,
    OUT_RAW_AVATAR, ensure_dirs,
)


def _analyze_image(img: Image.Image) -> dict:
    """Pure-PIL image analysis — no ML, no extra deps.

    Samples four corner patches to gauge background uniformity (very flat
    corners = likely studio backdrop or AI-generated solid BG) and checks
    the source aspect ratio to flag close/tight crops where the face
    already fills most of the frame.

    Both signals feed the crop-window bias in prepare_avatar so the framing
    adapts to the source rather than always applying the same fixed offset.
    """
    w, h = img.size
    patch = max(4, min(40, w // 6, h // 6))
    gray = img.convert("L")

    def _stdev(box: tuple) -> float:
        px = list(gray.crop(box).getdata())
        if len(px) < 2:
            return 0.0
        mean = sum(px) / len(px)
        return (sum((p - mean) ** 2 for p in px) / len(px)) ** 0.5

    stdevs = [
        _stdev((0, 0, patch, patch)),
        _stdev((w - patch, 0, w, patch)),
        _stdev((0, h - patch, patch, h)),
        _stdev((w - patch, h - patch, w, h)),
    ]
    avg_std = sum(stdevs) / 4

    return {
        # Flat corners (< 18 greyscale stdev) → probable studio / solid BG
        "uniform_background": avg_std < 18.0,
        # Tight crop: source aspect ratio wider than a natural 4:5 portrait
        "tight_crop": (w / h) > 0.80,
        "corner_stdev": round(avg_std, 1),
    }


def _soft_enhance(img: Image.Image) -> Image.Image:
    """Minimal two-step enhancement after the cover-fit resize.

    LANCZOS is the best resize filter but it still softens fine detail,
    especially on faces.  These two steps recover perceived sharpness and
    add a touch of micro-contrast without producing halos or artefacts
    that would look artificial on a talking-head video.

      - 8% contrast lift: adds presence; barely detectable individually
        but makes the face read as a real photo rather than a flat render.
      - UnsharpMask(0.8, 55, 4): very conservative radius + low percent
        so only genuine edges are sharpened, not noise or JPEG artefacts.
    """
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=55, threshold=4))
    return img


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

    # Analyse before resizing — original pixel data gives the cleanest signal.
    info = _analyze_image(img)
    notes = []
    if info["uniform_background"]:
        notes.append(f"uniform bg (corner_stdev={info['corner_stdev']})")
    if info["tight_crop"]:
        notes.append("tight crop")
    if notes:
        print(f"[hydra avatar] {src.name}: {', '.join(notes)}", file=sys.stderr)

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

    # Upward face bias: moves the crop window toward the top so the face
    # sits in the upper-center rather than dead center.
    #
    # Bias is tuned to the source image characteristics:
    #   8%  — natural portrait (default): strong upward shift, forehead visible
    #   5%  — studio/tight headshot: less shift so we don't cut the top of the head
    #   6%  — tight but natural background: middle ground
    if info["uniform_background"] and info["tight_crop"]:
        face_bias = 0.05
    elif info["tight_crop"]:
        face_bias = 0.06
    else:
        face_bias = 0.08

    raw_top = (new_h - th) // 2 - int(th * face_bias)
    top = max(0, min(raw_top, new_h - th))
    img = img.crop((left, top, left + tw, top + th))

    # Subtle post-crop enhancement to recover sharpness lost in LANCZOS resize.
    img = _soft_enhance(img)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path
