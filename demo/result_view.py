"""Result tab: document identity, OCR/MRZ/barcode, verification, image QA."""
from __future__ import annotations

import json
from typing import Any

_SKIP = {
    "checkSums",
    "contrastPrint",
    "docFormat",
    "mrzFormat",
    "mrzFormatCheckdigit",
    "mrzStringsWithCorrectCheckSums",
    "numberChecksumValidity",
    "numberValidity",
    "overallValidity",
    "symbolMatrix",
    "images",
}

def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)

_VERIFY_ORDER = (
    "docType",
    "expiry",
    "text",
    "mrz",
    "security",
    "imageQA",
    "portrait",
)
_QA_ORDER = (
    "focus",
    "glares",
    "resolution",
    "colorness",
    "perspective",
    "bounds",
    "portrait",
    "handwritten",
    "brightness",
    "occlusion",
)


def _check_result(code: Any) -> int:
    try:
        return int(code)
    except (TypeError, ValueError):
        return 2


def _check_entry(raw: Any) -> tuple[int, str]:
    if isinstance(raw, dict):
        return _check_result(raw.get("result")), str(raw.get("reason") or "").strip()
    return _check_result(raw), ""


def _iter_named(data: Any, order: tuple[str, ...]):
    if isinstance(data, dict):
        seen: set[str] = set()
        for key in order:
            if key in data:
                seen.add(key)
                yield key, data[key]
        for key, value in data.items():
            if key in seen or key == "result":
                continue
            yield str(key), value
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            yield str(item.get("id") or item.get("name") or ""), item


def _check_label(code: Any, reason: Any = None) -> str:
    n = _check_result(code)
    if n == 1:
        return "Pass"
    if n == 0:
        why = str(reason).strip() if reason else ""
        return f"Fail — {why}" if why else "Fail"
    return "Not checked"


def _verification(payload: dict) -> dict | None:
    raw = payload.get("verification")
    if isinstance(raw, dict) and raw.get("checks") is not None:
        return raw
    status = payload.get("status")
    if not isinstance(status, dict):
        return None
    opt = status.get("detailsOptical")
    if not isinstance(opt, dict):
        opt = {}
    overall = _check_result(status.get("overallStatus", opt.get("overallStatus", 2)))
    checks = {
        "docType": {"result": _check_result(opt.get("docType", 2))},
        "expiry": {"result": _check_result(opt.get("expiry", 2))},
        "text": {"result": _check_result(opt.get("text", 2))},
        "mrz": {"result": _check_result(opt.get("mrz", 2))},
        "security": {"result": _check_result(opt.get("security", 2))},
        "imageQA": {"result": _check_result(opt.get("imageQA", 2))},
        "portrait": {"result": _check_result(status.get("portrait", opt.get("portrait", 2)))},
    }
    return {"result": overall, "checks": checks}


def _overall_label(code: Any) -> str:
    n = _check_result(code)
    if n == 1:
        return "Verified"
    if n == 2:
        return "Not checked"
    return "Not verified"


def _rows_from_verification(payload: dict) -> list[list[str]]:
    v = _verification(payload)
    if not v:
        return []
    overall = _overall_label(v.get("result"))
    why = str(v.get("reason") or "").strip()
    if v.get("result") == 0 and why:
        overall = f"{overall} — {why}"
    rows: list[list[str]] = [["overall", overall, "Verify"]]
    for key, raw in _iter_named(v.get("checks"), _VERIFY_ORDER):
        result, reason = _check_entry(raw)
        rows.append([key, _check_label(result, reason), "Verify"])
    return rows


def _qa_cell(value: Any) -> str:
    if isinstance(value, dict):
        if "score" in value:
            value = value["score"]
        elif "result" in value:
            value = value["result"]
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "" if value is None else str(value)
    s = f"{n:.3f}".rstrip("0").rstrip(".")
    return s or "0"


def _rows_from_image_quality(payload: dict) -> list[list[str]]:
    raw = payload.get("imageQuality")
    if not isinstance(raw, dict):
        return []
    rows: list[list[str]] = []
    for key, value in _iter_named(raw.get("checks"), _QA_ORDER):
        rows.append([key, _qa_cell(value), "Image QA"])
    return rows


def _rows_from_map(data: dict | None, source: str) -> list[list[str]]:
    if not isinstance(data, dict):
        return []
    rows: list[list[str]] = []
    for key, value in data.items():
        if key in _SKIP or isinstance(value, (dict, list)):
            continue
        rows.append([key, _cell(value), source])
    return rows


def build_result_view(payload: dict) -> tuple[str, list[list[str]]]:
    err = payload.get("errorCode")
    score = payload.get("score")
    score_s = f"{score:.3f}" if isinstance(score, (int, float)) else "—"
    status = (payload.get("status") or {}).get("overallStatus")
    verify = _verification(payload)
    verify_s = _overall_label(verify.get("result")) if verify else "—"
    summary = (
        f"**Status:** {'OK' if err == 0 else 'Failed'} (errorCode={err})\n\n"
        f"**Document:** {payload.get('documentName') or '—'}\n\n"
        f"**Country:** {payload.get('countryName') or '—'}\n\n"
        f"**Verification:** {verify_s}\n\n"
        f"**Score:** {score_s}"
        + (f"  ·  overallStatus={status}" if status is not None else "")
    )
    rows: list[list[str]] = [
        ["documentName", _cell(payload.get("documentName")), "meta"],
        ["countryName", _cell(payload.get("countryName")), "meta"],
        ["score", score_s, "meta"],
        ["errorCode", _cell(err), "meta"],
    ]
    rows.extend(_rows_from_verification(payload))
    rows.extend(_rows_from_image_quality(payload))
    rows.extend(_rows_from_map(payload.get("ocr"), "OCR"))
    rows.extend(_rows_from_map(payload.get("mrz"), "MRZ"))
    rows.extend(_rows_from_map(payload.get("barcode"), "Barcode"))
    return summary, rows
