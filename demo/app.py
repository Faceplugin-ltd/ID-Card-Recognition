"""Gradio UI — HTTP client for the DocumentReader Flask API.

Local only. Start the API first (``./run.sh``), then ``python3 demo``.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import gradio as gr
import requests

import ui
from images_view import gallery_from_payload
from result_view import build_result_view
from security_view import security_view_from_payload

APP_ROOT = Path(__file__).resolve().parent.parent
SAMPLES = APP_ROOT / "assets" / "examples" / "samples"
API = os.environ.get(
    "API_BASE",
    f"http://127.0.0.1:{os.environ.get('PORT', os.environ.get('DOCSDK_PORT', '8082'))}",
).rstrip("/")
DEMO_PORT = int(os.environ.get("DEMO_PORT", "9002"))
_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def _fetch_license_status() -> dict:
    try:
        r = requests.get(f"{API}/api/licenseStatus", timeout=5)
        body = r.json() if r.ok else {}
        data = body.get("data") if isinstance(body, dict) else None
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _license_banner_md(status: dict | None = None) -> str:
    st = status if status is not None else _fetch_license_status()
    label = str(st.get("label") or "").strip()
    if not label:
        if st.get("licensed"):
            label = str(st.get("levelName") or "Licensed")
        else:
            label = "Not licensed / unavailable"
    return f"**License:** {label}"


def _capability_notes(status: dict) -> list[str]:
    notes: list[str] = []
    if not status.get("authenticity"):
        notes.append(
            "Liveness is **not available** on this license — liveness checks will not run."
        )
    if not status.get("recognition"):
        notes.append(
            "Recognition (OCR / MRZ / Barcode) is **not available** on this license."
        )
    return notes


def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _list_images() -> list[Path]:
    if not SAMPLES.is_dir():
        return []
    return sorted(
        p for p in SAMPLES.iterdir() if p.is_file() and p.suffix.lower() in _IMAGE_SUFFIXES
    )


def _document_examples() -> list[list[str | None]]:
    files = {p.name: p for p in _list_images()}
    pairs: list[list[str | None]] = []
    used: set[str] = set()
    for path in sorted(files.values()):
        if "_front" not in path.stem:
            continue
        base = path.stem.rsplit("_front", 1)[0]
        back = None
        for suf in _IMAGE_SUFFIXES:
            cand = files.get(f"{base}_back{suf}")
            if cand:
                back = cand
                break
        pairs.append([str(path), str(back) if back else None])
        used.add(path.name)
        if back:
            used.add(back.name)
    for path in _list_images():
        if path.name not in used:
            pairs.append([str(path), None])
    return pairs


def document_process(front, back):
    empty: list[list[str]] = []
    none_gallery: list = []
    lic = _fetch_license_status()
    notes = _capability_notes(lic)
    if not front:
        err = "**Error:** Front image required."
        if notes:
            err = "\n\n".join(f"**Note:** {n}" for n in notes) + "\n\n" + err
        return (err, empty, "*No liveness checks in this response.*", empty, none_gallery, "")

    if notes and not lic.get("recognition") and not lic.get("authenticity"):
        msg = "\n\n".join(f"**Note:** {n}" for n in notes)
        return (
            msg,
            empty,
            "*No liveness checks — this license does not include liveness.*",
            empty,
            none_gallery,
            "",
        )

    images = [{"image": _b64(front), "page_idx": 0}]
    if back:
        images.append({"image": _b64(back), "page_idx": 1})

    try:
        r = requests.post(
            f"{API}/api/documentProcess",
            json={
                "images": images,
                "response": {
                    "OCR": "normal",
                    "MRZ": "normal",
                    "Barcode": "normal",
                    "Authenticity": "normal",
                },
            },
            timeout=180,
        )
    except Exception as ex:  # noqa: BLE001
        return (f"**Request failed:** {ex}", empty, "*No liveness checks in this response.*", empty, none_gallery, "")

    try:
        payload = r.json()
    except Exception:  # noqa: BLE001
        return (
            f"**Invalid JSON** (HTTP {r.status_code})",
            empty,
            "*No liveness checks in this response.*",
            empty,
            none_gallery,
            r.text or "",
        )

    if not isinstance(payload, dict):
        return (
            "**Unexpected response shape.**",
            empty,
            "*No liveness checks in this response.*",
            empty,
            none_gallery,
            json.dumps(payload, indent=2),
        )

    summary, rows = build_result_view(payload)
    prefix: list[str] = []
    for n in notes:
        prefix.append(f"**Note:** {n}")
    lic_err = str(payload.get("licenseError") or "").strip()
    if lic_err:
        prefix.append(f"**License:** {lic_err}")
    if prefix:
        summary = "\n\n".join(prefix) + "\n\n" + summary
    gallery = gallery_from_payload(payload)
    if not gallery:
        summary += "\n\n*No cropped images in this response (Images tab empty).*"
    sec_summary, sec_rows = security_view_from_payload(payload)
    if notes and not lic.get("authenticity"):
        sec_summary = "**Note:** Liveness is not available on this license.\n\n" + sec_summary
    return (summary, rows, sec_summary, sec_rows, gallery, json.dumps(payload, indent=2))


def main() -> None:
    examples = _document_examples()
    with gr.Blocks(title="Document Reader Demo") as demo:
        gr.Markdown(
            "# FacePlugin Document Reader — Demo\n"
            "Upload a document image and click **Recognize**."
        )
        license_md = gr.Markdown(value=_license_banner_md())
        with gr.Row():
            with gr.Column():
                front = gr.Image(type="filepath", label="Front")
                back = gr.Image(type="filepath", label="Back (optional)")
                if examples:
                    gr.Examples(examples, inputs=[front, back], label="Examples")
                btn = gr.Button("Recognize", variant="primary")
            with gr.Column():
                with gr.Tabs():
                    with gr.Tab("Result"):
                        summary = gr.Markdown(value="*Run Recognize to see fields.*")
                        table = ui.result_dataframe()
                    with gr.Tab("Liveness"):
                        sec_summary = gr.Markdown(
                            value="*Run Recognize to see liveness checks.*"
                        )
                        sec_table = ui.result_dataframe(
                            headers=["Page", "Check", "Status"],
                            label="Liveness by page",
                        )
                    with gr.Tab("Images"):
                        gallery = ui.result_gallery(
                            label="Portrait / signature / cropped pages"
                        )
                    with gr.Tab("Raw JSON"):
                        raw = gr.Code(language="json", label="API response")
        btn.click(
            document_process,
            inputs=[front, back],
            outputs=[summary, table, sec_summary, sec_table, gallery, raw],
        )
        btn.click(lambda: _license_banner_md(), outputs=[license_md])
        demo.load(lambda: _license_banner_md(), outputs=[license_md])

    print(f"Gradio demo -> http://127.0.0.1:{DEMO_PORT}  (API {API})")
    demo.launch(server_name="0.0.0.0", server_port=DEMO_PORT, css=ui.RESULT_CSS)
