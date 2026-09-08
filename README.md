<div align="center">
<img alt="FacePlugin" src="https://avatars.githubusercontent.com/u/160751046?s=200&v=4" width="200"/>
</div>

#### 🌐 Company Site - [Here](https://faceplugin.com)

#### 🤗 Hugging Face - [Here](https://huggingface.co/spaces/FacePlugin-Ltd/ID-Document-Recognition-SDK)

#### 🛟 Help Center - [Here](https://doc.faceplugin.com)

#### 🐳 Docker Hub - [Here](https://hub.docker.com/r/faceplugin/document-reader)

# FacePlugin ID Document Recognition SDK — Linux / Docker (Fully On-Premise)

> **Fastest:** `docker pull faceplugin/document-reader:latest` → run → copy `FPMC1.…` → activate.
> **From source:** put files in `lib/cpu/` → `./run.sh` → Postman / `python3 demo`.
> **Try online:** [Hugging Face Space](https://huggingface.co/spaces/FacePlugin-Ltd/ID-Document-Recognition-SDK) (Gradio UI → your Linux API).
> Jump: [Quick start](#quick-start) · [Start the API](#start-the-api) · [SDK License](#sdk-license) · [Company Overview](#company-overview) · [Setup](#setup-on-your-own-app) · [About SDK](#about-sdk) · [Contact](#contact)

## Quick start

- [ ] Download and run the appropriate Docker image from [FacePlugin Docker Hub](https://hub.docker.com/r/faceplugin/document-reader). [See Option A for details](#option-a--docker-hub-no-drive-download).
- [ ] **Confirm it is running:** `curl -s http://127.0.0.1:8082/api/health` (no license needed yet)
- [ ] [Contact us](#contact) with your machine code (`FPMC1.…`) to obtain a license key, then activate with `POST /api/activate` — [SDK License](#sdk-license)
- [ ] **Try it:** Postman, curl, or local Gradio demo on **9002** (`python3 demo`)

Docs: [https://doc.faceplugin.com](https://doc.faceplugin.com)

## Introduction

FacePlugin **ID Document Recognition SDK for Linux / Docker** is a fully on-premise identity verification engine for ID cards, passports, and driver licenses. It runs OCR, MRZ reading, barcode and QR extraction, document detection and classification, image quality analysis, face extraction from the document, optional NFC/RFID, and authenticity / document liveness (security) checks.

All processing stays on your server. **No** biometric data is sent to FacePlugin cloud — built for KYC, eKYC, banking, and on-premise compliance workflows.

**Standalone repository** — pull Docker Hub (no Drive) or clone this repo, fill `lib/cpu/` from Google Drive, and run. No other FacePlugin repository is required.

**One repository** for Linux SDK + Docker. Native libraries are **linux/amd64**; the Docker image runs on Linux, Windows, and macOS hosts via Docker (Apple Silicon uses amd64 emulation).

**API server** in Docker — test with Postman, curl, or the local Gradio demo (`python3 demo`) covering Result, Liveness, Images, and Raw JSON.

### Main Functionalities


| Feature                             | Supported |
| ----------------------------------- | --------- |
| ID Card, Passport, and Driver License recognition | ✓         |
| MRZ, Barcode, QR, and OCR data extraction            | ✓         |
| Document detection and type classification | ✓         |
| Auto-capture and image quality analysis        | ✓         |
| Face, portrait, and signature extraction from document       | ✓         |
| NFC / RFID chip reading (where available)        | ✓         |


### Product List


| Platform           | Repository                                                                                                             |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Android            | [ID-Document-Recognition-Android](https://github.com/Faceplugin-ltd/ID-Document-Recognition-Android)                   |
| iOS                | [ID-Document-Recognition-iOS](https://github.com/Faceplugin-ltd/ID-Document-Recognition-iOS)                           |
| Windows            | [ID-Document-Recognition-Windows](https://github.com/Faceplugin-ltd/ID-Document-Recognition-Windows)                   |
| **Linux / Docker** | **[ID-Document-Recognition-Docker](https://github.com/Faceplugin-ltd/ID-Document-Recognition-Docker)** (**this repo**) |
| React Native       | [ID-Document-Recognition-React-Native](https://github.com/Faceplugin-ltd/ID-Document-Recognition-React-Native)         |
| Flutter            | [ID-Document-Recognition-Flutter](https://github.com/Faceplugin-ltd/ID-Document-Recognition-Flutter)                   |
| Ionic Capacitor    | [ID-Document-Recognition-Ionic-Capacitor](https://github.com/Faceplugin-ltd/ID-Document-Recognition-Ionic-Capacitor)   |
| Ionic Cordova      | [ID-Document-Recognition-Ionic-Cordova](https://github.com/Faceplugin-ltd/ID-Document-Recognition-Ionic-Cordova)       |
| Linux / Docker (Liveness) |[ID-Document-Liveness-Detection-Docker](https://github.com/Faceplugin-ltd/ID-Document-Liveness-Detection-Docker)         |


---

## Before you start


| Step | What you need                                                                                                                                                                                                                         |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | A Linux host **or** Docker (Desktop or Engine)                                                                                                                                                                                        |
| 2    | Docker Hub pull does **not** need Drive. Fill `./lib/cpu/` only for Compose / `./run.sh` — see Option B / C under [Start the API](#start-the-api)                                                                                     |
| 3    | You do not need a license to start the API the first time. Copy the machine code (`FPMC1.…`) from the logs or `GET /api/machinecode`. Send it to FacePlugin ([contact](#contact)) to get an `FP1.…` key and unlock product endpoints. |


You do **not** need a license to start the API once. Product endpoints unlock after you activate.

### System requirements


| Item | Minimum                | Recommended          |
| ---- | ---------------------- | -------------------- |
| CPU  | 2 cores                | 4 cores              |
| RAM  | 4 GB                   | 8 GB                 |
| Disk | 4 GB                   | 8 GB                 |
| OS   | Ubuntu 20.04+ (x86_64) | Ubuntu 22.04 / 24.04 |
| GPU  | —                      | — (CPU-only product) |


---

## Start the API

You can start **without** a license — the server prints your machine code on startup.

The API starts even if activation fails. Copy the **machine code** (`FPMC1.…`) from the log and send it to FacePlugin.

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/document-reader/desktop/unactivated.png" alt="Docker logs: machine code printed, activation failed, Flask API still listening" width="900"/>
</p>

### Option A — Docker Hub (no Drive download)

Runtime is already inside the image. No Google Drive step.

```bash
sudo docker pull faceplugin/document-reader:latest
docker run -d --name faceplugin-document-reader \
  --shm-size=2gb --privileged \
  -p 8082:8082 \
  -v /etc/machine-id:/etc/machine-id:ro \
  faceplugin/document-reader:latest
sudo docker logs -f faceplugin-document-reader
# Look for the machine code line: FPMC1.…
```

`--shm-size=2gb` is required (`dcr.fpk` extracts to `/dev/shm`). Keep `--privileged` and the `/etc/machine-id` volume as shown.

### Optional — Run multiple containers with one license

You only need this section if you want to run multiple DocumentReader containers on the same Linux host.

On Linux, mount `/etc/machine-id` into each container so they use the same machine code. Each container must have a different container name and host port.

For example:

```bash
sudo docker run -d --name faceplugin-document-reader-2 \
  --shm-size=2gb --privileged \
  -p 8083:8082 \
  -v /etc/machine-id:/etc/machine-id:ro \
  faceplugin/document-reader:latest
```

You can then activate each container using the same `FP1.…` license key.

Note: On Docker Desktop (macOS/Windows), do not use the `/etc/machine-id` volume. Each container may require its own license.

### Download runtime libraries (lib folder) — Options B and C only

**Skip this if you used Docker Hub** (`docker pull` / `docker run`). Runtime is already inside the image.

The `./lib/` tree is empty on GitHub because native binaries and model files are too large.

If you are building or running directly from this repository, download the **CPU** package into `./lib/cpu/`. DocumentReader is **CPU-only** — there is no `gpu/` package.

**[DocumentReader Linux runtime (Google Drive)](https://drive.google.com/drive/folders/16DFGKtyGbyL-0gfVOmNVaQ9vgXCYDr2M)**

1. Clone the repo (if you have not already):

```bash
git clone https://github.com/Faceplugin-ltd/ID-Document-Recognition-Docker.git
cd ID-Document-Recognition-Docker
```

1. Download **all files** from the Drive folder.
2. Put every file into `./lib/cpu/` — not inside a nested subfolder under `cpu/`.

```text
ID-Document-Recognition-Docker/
└── lib/
    └── cpu/
        ├── libDocSDK.so
        ├── libDocumentEngine.so
        └── dcr.fpk
```

Wrong layout: `lib/cpu/SomeFolder/libDocSDK.so`.

```bash
ls lib/cpu/libDocSDK.so
ls lib/cpu/libDocumentEngine.so
ls lib/cpu/dcr.fpk
```

### Option B — Docker Compose

Requires `./lib/cpu/` filled from Drive (above).

```bash
cd ID-Document-Recognition-Docker
# macOS/Windows Docker Desktop: remove the /etc/machine-id volume from docker-compose.yml first
sudo docker compose up --build -d
sudo docker compose logs -f
# Look for the machine code line: FPMC1.…
# Detached Compose has no TTY — there is no license prompt. Activate with curl (below).
```

### Option C — Native Linux (no Docker)

Requires `./lib/cpu/` filled from Drive (above).

```bash
cd ID-Document-Recognition-Docker
./run.sh
# or: python3 app.py
# The machine code (FPMC1.…) is printed in the terminal on startup.
```

API: **[http://127.0.0.1:8082](http://127.0.0.1:8082)**

---

## SDK License

Licenses are **offline** and bound to your machine code (`FPMC1.…`).

1. **Start the server** ([above](#start-the-api)) — Docker or local. A license is not required for the first start.
2. **Copy the machine code** from the startup log. It looks like `FPMC1.…`.
3. **Send that machine code** to FacePlugin ([contact](#contact)). We will issue an `FP1.…` key for that code.
4. **Activate** with the license key:

```bash
# Paste the FP1. key into ./license.txt (overwrite the file).

# Docker Hub (A) and Compose (B) both expose the API on this host port.
# `docker compose up -d` does not activate — the container is already running
# with no TTY, so it will not re-read license.txt. POST the key instead:
curl -s -X POST http://127.0.0.1:8082/api/activate \
  -H 'Content-Type: text/plain' \
  --data-binary @license.txt

# Compose alternative: after writing license.txt, restart so startup activates:
# sudo docker compose restart

# Local (Option C): stop the process (Ctrl+C), then:
./run.sh
```

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/document-reader/desktop/activate.png" alt="POST /api/activate with license.txt — success true" width="900"/>
</p>

Use the machine code from the environment you will run in production. **Docker and local host codes are different** — if you run in Docker, send the Docker machine code.

### License capabilities (Recognition + Liveness)

After activation, `GET /api/licenseStatus` reports what the key unlocks. The Gradio demo shows the same summary as **License: …** at the top of the page.


| Capability                  | Meaning                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------- |
| **Recognition**             | OCR, MRZ, barcode/QR, and document type classification                                |
| **Liveness** (authenticity) | Document authenticity: physical document, security patterns, photo origin, barcode format |


Typical labels:

- **Recognition + Liveness** — full identity verification (Result + Liveness tabs)
- **Recognition** — OCR, MRZ, and barcode only; Security stays empty / not checked
- **Liveness** — authenticity / document liveness only; OCR/MRZ/barcode stays empty / not checked
- **Not licensed** — machine code only until you activate

Check status anytime:

```bash
curl -s http://127.0.0.1:8082/api/licenseStatus
```

Request authenticity in `documentProcess` with `"Authenticity": "normal"`. `"none"` turns Liveness off. The demo and Postman default to `"normal"`.

## Try it

### Hugging Face (online demo)

Live ZeroGPU Document Reader (OCR, MRZ, barcode, security) — same Linux SDK as this repo:

- **[ID-Document-Recognition-SDK Space](https://huggingface.co/spaces/FacePlugin-Ltd/ID-Document-Recognition-SDK)**

### Health

```bash
curl -s http://127.0.0.1:8082/api/health
```

### Documentation

[https://doc.faceplugin.com](https://doc.faceplugin.com)

### Postman

Import `[postman/DocumentReader-API.postman_collection.json](postman/DocumentReader-API.postman_collection.json)`.

Default base URL: `http://127.0.0.1:8082`

Canonical protocol: `/api/*`. No version segment in route paths.

### Demo UI (Gradio) — local only

The Docker image is **API/SDK server only** (no Gradio). For a local FacePlugin Document Reader demo in the browser — Result, Liveness, Images, and Raw JSON — on the host (API must already be running on port 8082):

```bash
pip3 install -r requirements-demo.txt
./run_demo.sh
```

Or:

```bash
pip3 install -r requirements-demo.txt
DEMO_PORT=9002 API_BASE=http://127.0.0.1:8082 python3 demo
```

Open **[http://127.0.0.1:9002](http://127.0.0.1:9002)**. Examples when present: `assets/examples/samples/`. The header shows **License:** (for example `Recognition + Liveness`) from `/api/licenseStatus`.

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/document-reader/desktop/demo-ui-result.png" alt="FacePlugin Document Reader Linux demo — Result tab with OCR, MRZ, barcode, and verification" width="900"/>
</p>

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/document-reader/desktop/demo-ui-security.png" alt="FacePlugin Document Reader Linux demo — Liveness tab with authenticity and document liveness checks" width="900"/>
</p>

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/document-reader/desktop/demo-ui-images.png" alt="FacePlugin Document Reader Linux demo — Images tab with portrait, signature, and barcode crops" width="900"/>
</p>
<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/document-reader/desktop/demo-ui-raw.png" alt="FacePlugin Document Reader Linux demo — Raw JSON API response" width="900"/>
</p>


- **Result** — document type, country, verification, image quality, and OCR / MRZ / barcode fields  
- **Security** — overall and per-page authenticity: photo origin, physical document, security patterns, barcode format (`Authenticity: "normal"`; needs a Liveness-capable license)  
- **Images** — portrait, signature, ghost portrait, barcodes, and cropped pages  
- **Raw JSON** — full `/api/documentProcess` response for integration

---

## Setup on your own app

Two paths. You do **not** need the Gradio demo in production.

**HTTP** (any language) — run Option A, B, or C, then call the API:

```bash
curl -s -X POST http://127.0.0.1:8082/api/documentRecognition \
  -H 'Content-Type: application/json' \
  -d '{"images":[{"image":"<BASE64>"}]}'
curl -s -X POST http://127.0.0.1:8082/api/documentLiveness \
  -H 'Content-Type: application/json' \
  -d '{"images":[{"image":"<BASE64>"}]}'
curl -s -X POST http://127.0.0.1:8082/api/documentProcess \
  -H 'Content-Type: application/json' \
  -d '{"images":[{"image":"<BASE64>"}],"response":{"OCR":"normal","MRZ":"normal","Barcode":"normal","Authenticity":"normal"}}'
```

**Python in-process** — keep `lib/cpu/` beside `[sdk.py](sdk.py)`:

```python
import sdk

machine_code = sdk.get_machine_code()  # FPMC1.…
sdk.activate("license.txt")
sdk.init_sdk()
result = sdk.document_process(
    [{"image": base64_front}],
    rfid="",
    options={"response": {"OCR": "normal", "MRZ": "normal", "Barcode": "normal", "Authenticity": "normal"}},
)
```

---

## About SDK

Use the Python bindings in `[sdk.py](sdk.py)`. Return code `0` means success.

```python
import sdk

machine_code = sdk.get_machine_code()
print("machineCode:", machine_code)  # FPMC1.…

ret = sdk.activate("license.txt")
ret = sdk.init_sdk()

result = sdk.document_recognition([{"image": base64_front}])
result = sdk.document_liveness([{"image": base64_front}])
result = sdk.document_process(
    [{"image": base64_front}],
    rfid="",
    options={"response": {"OCR": "normal", "MRZ": "normal", "Barcode": "normal", "Authenticity": "normal"}},
)

# Front + back
result = sdk.document_process(
    [
        {"image": base64_front, "page_idx": 0},
        {"image": base64_back, "page_idx": 1},
    ],
    rfid="",
    options={"response": {"OCR": "normal", "MRZ": "normal", "Barcode": "normal", "Authenticity": "normal"}},
)

result = sdk.general_process(base64_image, options={})
print(sdk.get_license_status())  # recognition / authenticity flags + label
```

Optional session APIs: `sdk.start_new_session()`, `sdk.start_new_page()`, `sdk.unload()`.

HTTP endpoints: `/api/health`, `/api/machinecode`, `/api/licenseStatus`, `/api/backend`, `/api/activate`, `/api/documentRecognition`, `/api/documentLiveness`, `/api/documentProcess`, `/api/generalProcess`.

## Company Overview

**FacePlugin** builds **on-premises biometric AI SDKs** for **face recognition**, **face liveness detection** (presentation-attack detection), **deepfake detection**, **ID document recognition** (OCR / MRZ / barcode), **ID document liveness**, and full **eKYC / identity verification** workflows.

Deploy on your own servers, private cloud, or fully on-device. **Biometric data never leaves your infrastructure.** Face matching is **NIST FRVT**-evaluated; liveness targets **iBeta Level 2** class PAD. License once for **unlimited on-prem inference** — **no per-call fees**.

- Website: [faceplugin.com](https://faceplugin.com)
- Docs: [doc.faceplugin.com](https://doc.faceplugin.com)
- Hugging Face demo: [ID-Document-Recognition-SDK](https://huggingface.co/spaces/FacePlugin-Ltd/ID-Document-Recognition-SDK)
- Docker Hub: [faceplugin/document-reader](https://hub.docker.com/r/faceplugin/document-reader)

## Contact

Request a license, machine-code activation (`FPMC1.…` → `FP1.…`), or integration help:

<div align="left">
<a target="_blank" href="mailto:info@faceplugin.com"><img src="https://img.shields.io/badge/email-info@faceplugin.com-blue.svg?logo=gmail" alt="Email FacePlugin info@faceplugin.com"></a>&emsp;
<a target="_blank" href="https://t.me/faceplugin"><img src="https://img.shields.io/badge/telegram-@faceplugin-blue.svg?logo=telegram" alt="Telegram @faceplugin"></a>&emsp;
<a target="_blank" href="https://wa.me/+14692784822"><img src="https://img.shields.io/badge/whatsapp-+1_469_278_4822-blue.svg?logo=whatsapp" alt="WhatsApp +1 469 278 4822"></a>
</div>
