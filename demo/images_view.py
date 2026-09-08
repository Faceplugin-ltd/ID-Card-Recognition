"""Images tab: portrait / signature / cropped pages from filtered JSON."""
from __future__ import annotations

import base64
import io
from typing import Any

def _b64_to_pil(raw: str):
    s = raw.strip()
    if s.startswith("data:") and "," in s[:128]:
        s = s.split(",", 1)[1]
    try:
        blob = base64.b64decode(s)
    except Exception:
        return None
    if len(blob) < 32:
        return None
    try:
        from PIL import Image

        return Image.open(io.BytesIO(blob)).convert("RGB")
    except Exception:
        return None


def _image_from_value(value: Any):
    if isinstance(value, str) and value.strip():
        return _b64_to_pil(value)
    if isinstance(value, dict):
        inner = value.get("image") or value.get("value")
        if isinstance(inner, str):
            return _b64_to_pil(inner)
        if isinstance(inner, dict):
            return _image_from_value(inner)
    return None


def gallery_from_payload(payload: dict) -> list:
    """Portrait / signature / cropped pages from ``payload["images"]``."""
    items = payload.get("images")
    if not isinstance(items, list):
        return []
    gallery: list = []
    for i, item in enumerate(items):
        caption = f"image {i + 1}"
        pic = None
        if isinstance(item, str):
            pic = _b64_to_pil(item)
        elif isinstance(item, dict):
            pic = _image_from_value(item)
            caption = str(item.get("name") or item.get("fieldName") or caption)
            page = item.get("pageIndex")
            if page is not None:
                caption = f"{caption} (page {page})"
        if pic is not None:
            gallery.append((pic, caption))
    return gallery
