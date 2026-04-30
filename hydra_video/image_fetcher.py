"""Fetch real product images for Hydra video generation.

Priority order per call:
  1. Amazon product page scrape (ASIN extracted from affiliate URL)
  2. Pexels portrait photo search  (uses db pexels_api_key setting)
  3. Returns [] — caller falls back to PIL card slideshow

Images are cached under hydra_video/assets/product_images/{key}/
so repeated generations don't re-download.
"""

from __future__ import annotations

import html as _html_module
import json
import re
import time
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parent / "assets" / "product_images"
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_TIMEOUT = 20


def _cache_dir(key: str) -> Path:
    safe = re.sub(r"[^\w]", "_", key.lower())[:48]
    d = CACHE_DIR / safe
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download(url: str, dest: Path) -> bool:
    try:
        r = requests.get(
            url,
            headers={"User-Agent": _UA},
            timeout=_TIMEOUT,
            stream=True,
        )
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(8192):
                fh.write(chunk)
        return dest.stat().st_size > 1024
    except Exception:
        return False


def fetch_amazon_images(url: str, max_images: int = 5) -> list[Path]:
    """Scrape hi-res product images from an Amazon product page.

    Tries two extraction methods:
      A. colorImages JSON blob embedded in page source
      B. data-a-dynamic-image attribute on the main product image

    Returns cached paths if already downloaded today.
    """
    if not url:
        return []

    m = re.search(r"/dp/([A-Z0-9]{10})", url)
    if not m:
        return []
    asin = m.group(1)

    cache = _cache_dir(f"amz_{asin}")
    existing = sorted(cache.glob("img_*.jpg"))
    if len(existing) >= 2:
        return existing[:max_images]

    try:
        page_url = f"https://www.amazon.com/dp/{asin}"
        r = requests.get(
            page_url,
            headers={
                "User-Agent": _UA,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,*/*",
            },
            timeout=_TIMEOUT,
        )
        if r.status_code != 200:
            return []

        html = r.text
        image_urls: list[str] = []

        # Method A: colorImages initial array
        m_ci = re.search(
            r"'colorImages'\s*:\s*\{[^}]*'initial'\s*:\s*(\[.*?\])\s*\}",
            html,
            re.DOTALL,
        )
        if m_ci:
            try:
                imgs = json.loads(m_ci.group(1))
                for img in imgs:
                    for key in ("hiRes", "large", "thumb"):
                        val = img.get(key)
                        if val and val not in image_urls:
                            image_urls.append(val)
                            break
            except Exception:
                pass

        # Method B: data-a-dynamic-image (JSON dict: url -> [w, h])
        for m_dyn in re.finditer(r'data-a-dynamic-image="([^"]+)"', html):
            try:
                decoded = _html_module.unescape(m_dyn.group(1))
                img_dict = json.loads(decoded)
                for img_url in img_dict:
                    if img_url not in image_urls:
                        image_urls.append(img_url)
            except Exception:
                pass

        paths: list[Path] = []
        for i, img_url in enumerate(image_urls[:max_images]):
            dest = cache / f"img_{i:02d}.jpg"
            if _download(img_url, dest):
                paths.append(dest)

        return paths

    except Exception:
        return []


def fetch_pexels_photos(
    query: str,
    count: int = 4,
    api_key: str = "",
) -> list[Path]:
    """Search Pexels for portrait-oriented product/lifestyle photos."""
    if not api_key:
        try:
            import database as db
            api_key = (db.get_setting("pexels_api_key") or "").strip()
        except Exception:
            pass

    if not api_key:
        return []

    cache = _cache_dir(f"pex_{re.sub(chr(32), '_', query[:32])}")
    existing = sorted(cache.glob("pex_*.jpg"))
    if len(existing) >= 2:
        return existing[:count]

    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={
                "query": query,
                "per_page": min(count * 2, 20),
                "orientation": "portrait",
            },
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()

        paths: list[Path] = []
        for i, photo in enumerate(data.get("photos", [])):
            src = photo.get("src", {})
            img_url = (
                src.get("large2x") or src.get("large") or src.get("original")
            )
            if not img_url:
                continue
            dest = cache / f"pex_{i:02d}.jpg"
            if _download(img_url, dest):
                paths.append(dest)
            if len(paths) >= count:
                break

        return paths

    except Exception:
        return []


_NICHE_CONTEXT = {
    "productivity": "productivity desk workspace",
    "business": "business professional office",
    "ai": "technology computer modern",
    "work_from_home": "home office workspace remote work",
    "content_creation": "content creator studio recording",
}


def fetch_product_images(
    product: str,
    niche: str,
    affiliate_url: str = "",
    max_images: int = 6,
) -> list[Path]:
    """Orchestrate image fetching: Amazon → Pexels product → Pexels niche.

    Returns [] if nothing found so the caller can fall back to PIL cards.
    """
    images: list[Path] = []

    # 1. Real product shots from Amazon
    if affiliate_url:
        amz = fetch_amazon_images(affiliate_url, max_images=4)
        images.extend(amz)

    # 2. Pexels product search
    if len(images) < 3:
        context = _NICHE_CONTEXT.get(niche, niche.replace("_", " "))
        query = f"{product} {context}"
        pex = fetch_pexels_photos(query, count=max_images - len(images))
        images.extend(pex)

    # 3. Pexels niche fallback
    if len(images) < 2:
        context = _NICHE_CONTEXT.get(niche, niche.replace("_", " "))
        pex2 = fetch_pexels_photos(context, count=4)
        images.extend(pex2)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[Path] = []
    for p in images:
        key = p.name
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique[:max_images]
