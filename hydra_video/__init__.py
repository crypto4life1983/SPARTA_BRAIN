"""Hydra Video - local-first talking-head pipeline.

MVP: script -> voice -> avatar -> lipsync (placeholder) -> captions -> render.
Every stage is swappable. The pipeline must run end-to-end even if the
heavy AI models (SadTalker, Wav2Lip, XTTS, ComfyUI) are not installed,
by falling back to deterministic placeholders.
"""

from pathlib import Path

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
AVATARS_DIR = ASSETS / "avatars"
PRODUCTS_DIR = ASSETS / "products"
MUSIC_DIR = ASSETS / "music"
OUTPUTS = ROOT / "outputs"
OUT_AUDIO = OUTPUTS / "audio"
OUT_RAW_AVATAR = OUTPUTS / "raw_avatar"
OUT_FINAL = OUTPUTS / "final"

DEFAULT_AVATAR = AVATARS_DIR / "avatar.jpg"
DEFAULT_VIDEO_SIZE = (1080, 1920)  # Full HD vertical 9:16 (Shorts/Reels/TikTok)
DEFAULT_FPS = 30


def ensure_dirs() -> None:
    for d in (AVATARS_DIR, PRODUCTS_DIR, MUSIC_DIR,
              OUT_AUDIO, OUT_RAW_AVATAR, OUT_FINAL):
        d.mkdir(parents=True, exist_ok=True)
