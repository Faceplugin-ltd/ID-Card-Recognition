#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export API_BASE="${API_BASE:-http://127.0.0.1:8082}"
export DEMO_PORT="${DEMO_PORT:-9002}"
echo "Open the Gradio demo against ${API_BASE} (start ./run.sh first)."
exec python3 demo
