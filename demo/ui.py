#!/usr/bin/env python3
"""
Shared Gradio demo helpers for FacePlugin *-Linux products (local only).

Canonical copy: templates/linux-api/demo_ui.py
Kept inside the ``demo/`` package (run with ``python3 demo``).

UI conventions (every product demo):
  - Result tab: short markdown summary + Field/Value table
  - Raw JSON tab: full API response
  - Examples: every image under assets/examples/samples/ (or examples/)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import gradio as gr

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

# Result tables and galleries grow with content; the page scrolls. No inner viewport.
# Field / Value / Source stay on one screen: wrap long OCR/MRZ in Value, keep Source visible.
RESULT_CSS = """
.fp-result-table,
.fp-result-table .table-wrap,
.fp-result-table .wrap,
.fp-result-table .overflow-y-auto,
.fp-result-table .overflow-auto {
  max-height: none !important;
  height: auto !important;
  overflow: visible !important;
}
.fp-result-table table {
  table-layout: fixed !important;
  width: 100% !important;
}
.fp-result-table th,
.fp-result-table td {
  white-space: normal !important;
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
  vertical-align: top !important;
}
.fp-result-table th:nth-child(1),
.fp-result-table td:nth-child(1) {
  width: 24% !important;
}
.fp-result-table th:nth-child(2),
.fp-result-table td:nth-child(2) {
  width: 56% !important;
}
.fp-result-table th:nth-child(3),
.fp-result-table td:nth-child(3) {
  width: 20% !important;
  min-width: 5.5rem !important;
  position: sticky;
  right: 0;
  background: var(--table-even-background-fill, var(--body-background-fill, #fff));
}
.fp-result-gallery,
.fp-result-gallery .grid-wrap,
.fp-result-gallery .gallery-container,
.fp-result-gallery .overflow-y-auto,
.fp-result-gallery .overflow-auto {
  max-height: none !important;
  height: auto !important;
  overflow: visible !important;
}
"""


def result_dataframe(*, headers: list[str] | None = None, label: str = "Extracted fields"):
    """Field table that expands with rows (no inner scrollbar)."""
    cols = headers or ["Field", "Value", "Source"]
    kw = dict(
        headers=cols,
        datatype=["str"] * len(cols),
        interactive=False,
        wrap=True,
        label=label,
        elem_classes=["fp-result-table"],
    )
    if len(cols) == 3:
        kw["column_widths"] = ["24%", "56%", "20%"]
    try:
        return gr.Dataframe(**kw, max_height=None)
    except TypeError:
        kw.pop("column_widths", None)
        try:
            return gr.Dataframe(**kw, max_height=None)
        except TypeError:
            return gr.Dataframe(**kw)


def result_gallery(*, label: str = "Images", columns: int = 2):
    """Image grid that expands with items (no inner scrollbar)."""
    kw = dict(
        label=label,
        columns=columns,
        object_fit="contain",
        show_label=True,
        elem_classes=["fp-result-gallery"],
    )
    try:
        return gr.Gallery(**kw, height=None)
    except TypeError:
        return gr.Gallery(**kw)


def samples_dir(root: Path) -> Path:
    for rel in ("assets/examples/samples", "assets/samples", "examples/samples", "examples"):
        p = root / rel
        if p.is_dir():
            return p
    return root / "assets" / "examples" / "samples"


def list_images(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def list_image_paths(directory: Path) -> list[str]:
    return [str(p) for p in list_images(directory)]


def list_pair_examples(directory: Path) -> list[list[str]]:
    """Match-style pairs: ``pair(N)_1.*`` + ``pair(N)_2.*`` when both exist."""
    files = {p.name: p for p in list_images(directory)}
    pairs: list[list[str]] = []
    seen: set[str] = set()
    for name, path in sorted(files.items()):
        stem = path.stem  # pair(1)_1
        if "_1" not in stem or stem in seen:
            continue
        other_stem = stem.rsplit("_1", 1)[0] + "_2"
        for suf in IMAGE_SUFFIXES:
            other = files.get(other_stem + suf)
            if other:
                pairs.append([str(path), str(other)])
                seen.add(stem)
                seen.add(other_stem)
                break
    return pairs


def cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def flatten_rows(
    obj: Any,
    *,
    prefix: str = "",
    source: str = "",
    skip_keys: set[str] | None = None,
    max_rows: int = 200,
) -> list[list[str]]:
    """Flatten nested JSON into [Field, Value, Source] rows."""
    skip = skip_keys or set()
    rows: list[list[str]] = []

    def walk(node: Any, path: str) -> None:
        if len(rows) >= max_rows:
            return
        if isinstance(node, dict):
            for key, value in node.items():
                if key in skip:
                    continue
                child = f"{path}.{key}" if path else str(key)
                if isinstance(value, (dict, list)):
                    # Prefer compact attribute {value, confidence/status}
                    if (
                        isinstance(value, dict)
                        and "value" in value
                        and not any(isinstance(value[k], (dict, list)) for k in value)
                    ):
                        val = value.get("value")
                        extra = []
                        if "confidence" in value:
                            extra.append(f"conf={cell(value['confidence'])}")
                        if "status" in value:
                            extra.append(f"status={cell(value['status'])}")
                        if "range" in value:
                            extra.append(f"range={cell(value['range'])}")
                        shown = cell(val)
                        if extra:
                            shown = f"{shown} ({', '.join(extra)})"
                        rows.append([child, shown, source])
                    else:
                        walk(value, child)
                else:
                    rows.append([child, cell(value), source])
        elif isinstance(node, list):
            if not node:
                rows.append([path or "[]", "[]", source])
                return
            # Short list of scalars
            if all(not isinstance(x, (dict, list)) for x in node):
                rows.append([path, cell(node), source])
                return
            for i, item in enumerate(node):
                walk(item, f"{path}[{i}]")
        else:
            rows.append([path or "value", cell(node), source])

    walk(obj, prefix)
    return rows


def result_outputs(
    payload: Any,
    *,
    summary: str,
    source: str = "api",
    skip_keys: set[str] | None = None,
) -> tuple[str, list[list[str]], str]:
    rows = flatten_rows(payload, source=source, skip_keys=skip_keys)
    raw = json.dumps(payload, indent=2, ensure_ascii=False) if payload is not None else ""
    return summary, rows, raw


def error_outputs(message: str) -> tuple[str, list[list[str]], str]:
    return f"**Error:** {message}", [], ""


def result_panel(*, placeholder: str = "*Run an action to see fields.*"):
    """Create Result + Raw JSON tabs. Returns (summary, table, raw) components."""
    with gr.Tabs():
        with gr.Tab("Result"):
            summary = gr.Markdown(value=placeholder)
            table = result_dataframe()
        with gr.Tab("Raw JSON"):
            raw = gr.Code(language="json", label="API response")
    return summary, table, raw
