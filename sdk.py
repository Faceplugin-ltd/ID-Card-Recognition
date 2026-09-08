"""DocumentReader Python kit — ctypes bindings to libDocSDK.so (lib/cpu/).

Role: thin native API for integrators. Used by app.py (Flask). Prefer ``python3 demo`` → HTTP → app.py
for UI demos rather than calling this module from Gradio directly.
"""

from __future__ import annotations

import base64
import ctypes
import io
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIB = ROOT / "lib" / "cpu"
SO = LIB / "libDocSDK.so"

os.chdir(ROOT)
os.environ["LD_LIBRARY_PATH"] = str(LIB) + (
    (":" + os.environ["LD_LIBRARY_PATH"]) if os.environ.get("LD_LIBRARY_PATH") else ""
)

if not SO.is_file():
    raise FileNotFoundError(
        f"missing {SO} — put Drive files in lib/cpu/ "
        "(export copies SDK lib/ → App lib/cpu/)"
    )

_dll = ctypes.cdll.LoadLibrary(str(SO))

_dll.DocSDK_initialize.restype = ctypes.c_int
_dll.DocSDK_initialize.argtypes = []
_dll.DocSDK_activate.restype = ctypes.c_int
_dll.DocSDK_activate.argtypes = [ctypes.c_char_p]
_dll.DocSDK_getMachineCode.restype = ctypes.c_int
_dll.DocSDK_getMachineCode.argtypes = [ctypes.c_char_p]
_dll.DocSDK_documentProcess.restype = ctypes.c_int
_dll.DocSDK_documentProcess.argtypes = [
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
]
_dll.DocSDK_generalProcess.restype = ctypes.c_int
_dll.DocSDK_generalProcess.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]

def _opt_sym(name, restype, argtypes):
    fn = getattr(_dll, name, None)
    if fn is None:
        return None
    fn.restype = restype
    fn.argtypes = argtypes
    return fn

_start_new_session = _opt_sym(
    "DocSDK_startNewSession", ctypes.c_int, [ctypes.c_char_p, ctypes.c_char_p]
)
_start_new_page = _opt_sym(
    "DocSDK_startNewPage", ctypes.c_int, [ctypes.c_char_p, ctypes.c_char_p]
)
_unload = _opt_sym("DocSDK_unload", ctypes.c_int, [ctypes.c_char_p])
_get_license_status = _opt_sym(
    "DocSDK_getLicenseStatus", ctypes.c_int, [ctypes.c_char_p]
)

_MC_BUF = 768
_STATUS_BUF = 512
_OUT_MIN = 1_000_000
_OUT_MAX = 16 * 1024 * 1024
_MAX_IMG = 8 * 1024 * 1024

def _b(v) -> bytes:
    if v is None:
        return b""
    if isinstance(v, bytes):
        return v
    return str(v).encode("utf-8")

def _out(*parts: bytes):
    n = min(max(_OUT_MIN, sum(len(p) for p in parts) * 2 + 262144), _OUT_MAX)
    return ctypes.create_string_buffer(n)

def _fit_b64(image_b64: str, max_bytes: int = _MAX_IMG) -> bytes:
    raw = _b(image_b64).strip()
    if len(raw) <= max_bytes:
        return raw
    from PIL import Image

    img = Image.open(io.BytesIO(base64.b64decode(raw)))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    quality, scale, last = 85, 1.0, raw
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.LANCZOS
    for _ in range(12):
        cand = img
        if scale < 1.0:
            cand = img.resize(
                (max(1, int(img.width * scale)), max(1, int(img.height * scale))),
                resample,
            )
        buf = io.BytesIO()
        cand.save(buf, format="JPEG", quality=quality, optimize=True)
        last = base64.b64encode(buf.getvalue())
        if len(last) <= max_bytes:
            return last
        if quality > 40:
            quality -= 10
        else:
            scale *= 0.75
            quality = 75
    return last

def get_machine_code() -> str:
    """Return FPMC1.… machine code."""
    buf = ctypes.create_string_buffer(_MC_BUF)
    _dll.DocSDK_getMachineCode(buf)
    return buf.value.decode("utf-8", errors="replace")


def get_license_status() -> dict:
    """Return license capability dict from DocSDK_getLicenseStatus."""
    fallback = {
        "licensed": False,
        "level": -1,
        "levelName": "None",
        "recognition": False,
        "authenticity": False,
        "label": "Not licensed",
    }
    if _get_license_status is None:
        return fallback
    buf = ctypes.create_string_buffer(_STATUS_BUF)
    if int(_get_license_status(buf)) != 0:
        return fallback
    try:
        data = json.loads(buf.value.decode("utf-8", errors="replace") or "{}")
        return data if isinstance(data, dict) else fallback
    except Exception:  # noqa: BLE001
        return fallback


def activate(license_path: str) -> int:
    """Activate with path to license.txt / license.dat, or an FP1.… key string."""
    return int(_dll.DocSDK_activate(_b(license_path)))

def init_sdk() -> int:
    return int(_dll.DocSDK_initialize())

def start_new_session(options: dict | None = None) -> str:
    """Start a document session."""
    if _start_new_session is None:
        return '{"msg":"DocSDK_startNewSession not in this libDocSDK.so"}'
    opts = options or {"scenario": "FullProcess", "series": False}
    options_b = _b(json.dumps(opts, separators=(",", ":")))
    out = _out(options_b)
    _start_new_session(options_b, out)
    return out.value.decode("utf-8", errors="replace")

def start_new_page(options: dict | None = None) -> str:
    """Start an additional page in the current session."""
    if _start_new_page is None:
        return '{"msg":"DocSDK_startNewPage not in this libDocSDK.so"}'
    opts = options or {}
    options_b = _b(json.dumps(opts, separators=(",", ":")))
    out = _out(options_b)
    _start_new_page(options_b, out)
    return out.value.decode("utf-8", errors="replace")

def unload() -> str:
    """Unload the SDK."""
    if _unload is None:
        return '{"msg":"DocSDK_unload not in this libDocSDK.so"}'
    out = _out()
    _unload(out)
    return out.value.decode("utf-8", errors="replace")

def document_process(images, rfid: str = "", options: dict | None = None) -> str:
    opts = options or {
        "response": {
            "OCR": "normal",
            "MRZ": "normal",
            "Barcode": "normal",
            "ImageQuality": "normal",
            "Authenticity": "normal",
        }
    }
    norm = []
    for item in images:
        if isinstance(item, dict):
            entry = {"image": _fit_b64(item["image"]).decode()}
            if item.get("page_idx") is not None:
                entry["page_idx"] = int(item["page_idx"])
            norm.append(entry)
        else:
            norm.append(_fit_b64(item).decode())
    images_json = _b(json.dumps(norm, separators=(",", ":")))
    options_b = _b(json.dumps(opts, separators=(",", ":")))
    rfid_b = _b(rfid or "")
    out = _out(images_json, rfid_b, options_b)
    _dll.DocSDK_documentProcess(images_json, rfid_b, options_b, out)
    return out.value.decode("utf-8", errors="replace")

def general_process(image: str, options: dict | None = None) -> str:
    opts = options or {}
    image_b = _fit_b64(image)
    options_b = _b(json.dumps(opts, separators=(",", ":")))
    out = _out(image_b, options_b)
    _dll.DocSDK_generalProcess(image_b, options_b, out)
    return out.value.decode("utf-8", errors="replace")


_RECOGNITION_RESPONSE = {
    "OCR": "normal",
    "MRZ": "normal",
    "Barcode": "normal",
    "ImageQuality": "normal",
    "Authenticity": "none",
    "RFID": "none",
}

_LIVENESS_RESPONSE = {
    "OCR": "none",
    "MRZ": "none",
    "Barcode": "none",
    "ImageQuality": "none",
    "Authenticity": "normal",
    "RFID": "none",
}


def _forced_process_options(response: dict, extra: dict | None) -> dict:
    opts = dict(extra or {})
    opts.pop("response", None)
    opts["response"] = dict(response)
    return opts


def document_recognition(images, rfid: str = "", extra: dict | None = None) -> str:
    """OCR / MRZ / barcode / image quality only. Authenticity is always off."""
    return document_process(
        images, rfid, _forced_process_options(_RECOGNITION_RESPONSE, extra)
    )


def document_liveness(images, rfid: str = "", extra: dict | None = None) -> str:
    """Authenticity / security only. OCR / MRZ / barcode / image quality are always off."""
    return document_process(
        images, rfid, _forced_process_options(_LIVENESS_RESPONSE, extra)
    )
