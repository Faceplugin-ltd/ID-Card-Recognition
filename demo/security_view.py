"""Liveness tab: authenticity by page, Pass / Fail / Not checked."""
from __future__ import annotations

from typing import Any

_SECURITY_PAGE_META = frozenset({"pageIndex", "overall", "label", "pages", "presentation"})


def _humanize_key(key: str) -> str:
    spaced = ""
    for ch in str(key):
        if ch.isupper() and spaced:
            spaced += " "
        spaced += ch
    spaced = spaced.strip()
    return spaced[:1].upper() + spaced[1:] if spaced else str(key)


def _page_side(page_index: Any) -> str:
    try:
        n = int(page_index)
    except (TypeError, ValueError):
        n = 0
    if n == 0:
        return "Front"
    if n == 1:
        return "Back"
    return f"Page {n}"


def _status_kind(value: Any) -> str:
    if isinstance(value, dict):
        if "score" in value and not isinstance(value.get("score"), dict):
            return "score"
        value = value.get("result", value.get("label"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "score"
    s = str(value or "").strip().lower().replace(" ", "").replace("_", "")
    if s in ("success", "pass", "ok", "authentic", "1"):
        return "success"
    if s in ("notchecked", "wasnotdone", "2"):
        return "notChecked"
    if s in ("fail", "failed", "error", "notauthentic", "0"):
        return "fail"
    return "other"


def _format_score(value: Any) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value or "")
    s = f"{n:.1f}".rstrip("0").rstrip(".")
    return f"{s or '0'}%"


def _status_cell(value: Any) -> str:
    kind = _status_kind(value)
    if kind == "success":
        return "Pass"
    if kind == "notChecked":
        return "Not checked"
    if kind == "fail":
        return "Fail"
    if kind == "score":
        if isinstance(value, dict):
            return _format_score(value.get("score", value.get("result")))
        return _format_score(value)
    if isinstance(value, dict):
        value = value.get("result", value.get("label"))
    return str(value or "")


def _check_title(key: str, raw: Any) -> str:
    if isinstance(raw, dict):
        title = str(raw.get("title") or "").strip()
        if title:
            return title
    return _humanize_key(key)


def _iter_security_pages(sec: dict) -> list[dict]:
    pages = sec.get("pages")
    if isinstance(pages, list) and pages:
        return [p for p in pages if isinstance(p, dict)]
    flat = {k: v for k, v in sec.items() if k not in _SECURITY_PAGE_META}
    if flat:
        return [{"pageIndex": 0, **flat, "overall": sec.get("overall"), "label": sec.get("label")}]
    return []


def _append_security_value(
    rows: list[list[str]],
    *,
    page_name: str,
    key: str,
    raw: Any,
) -> None:
    title = _check_title(key, raw)
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        rows.append([page_name, title, _status_cell(raw)])
        return
    if not isinstance(raw, dict):
        rows.append([page_name, title, _status_cell(raw)])
        return
    if "score" in raw and not isinstance(raw.get("score"), dict):
        rows.append([page_name, title, _status_cell(raw)])
        return
    kind = _status_kind(raw)
    rows.append([page_name, title, _status_cell(raw.get("result"))])
    checks = raw.get("checks")
    if not isinstance(checks, dict):
        return
    if kind != "fail" and not any(_status_kind(v) == "fail" for v in checks.values()):
        return
    for ck, cv in checks.items():
        if _status_kind(cv) == "notChecked" and kind != "fail":
            continue
        sub_title = _check_title(str(ck), cv)
        rows.append([page_name, f"  -> {sub_title}", _status_cell(cv)])


def security_view_from_payload(payload: dict) -> tuple[str, list[list[str]]]:
    sec = payload.get("security")
    if not isinstance(sec, dict):
        return "*No liveness checks in this response. If you expected checks, this license may not include liveness.*", []

    pages = _iter_security_pages(sec)
    doc_label = str(sec.get("label") or "").strip() or _status_cell(sec.get("overall"))
    if not pages:
        if doc_label:
            return (
                f"### Document: **{doc_label}**\n\n*No per-page checks in this response.*",
                [["—", "Overall", doc_label]],
            )
        return (
            "*No liveness checks in this response. If you expected checks, this license may not include liveness.*",
            [],
        )
    lines = [f"### Document: **{doc_label or '—'}**", ""]
    rows: list[list[str]] = []

    for page in pages:
        name = _page_side(page.get("pageIndex", 0))
        page_label = str(page.get("label") or "").strip() or _status_cell(page.get("overall"))
        rows.append([name, "Overall", page_label or "—"])

        ok = fail = not_checked = 0
        pattern_bit = ""
        for key, raw in page.items():
            if key in _SECURITY_PAGE_META:
                continue
            _append_security_value(rows, page_name=name, key=str(key), raw=raw)
            if isinstance(raw, dict) and "score" in raw:
                pattern_bit = _status_cell(raw)
                continue
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                pattern_bit = _status_cell(raw)
                continue
            kind = _status_kind(raw)
            if kind == "success":
                ok += 1
            elif kind == "fail":
                fail += 1
            elif kind == "notChecked":
                not_checked += 1

        bits: list[str] = []
        if ok:
            bits.append(f"{ok} ok")
        if fail:
            bits.append(f"{fail} fail")
        if pattern_bit:
            bits.append(f"score {pattern_bit}")
        if not_checked:
            bits.append(f"{not_checked} not checked")
        detail = ", ".join(bits) if bits else "no checks"
        lines.append(f"- **{name}** — **{page_label or '—'}** ({detail})")

    return "\n".join(lines), rows

