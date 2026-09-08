"""Entry: ``python3 demo`` (or ``python3 -m demo``) from the App root."""

from __future__ import annotations

import sys
from pathlib import Path

# ``python3 demo`` puts this directory on sys.path; ``python3 -m demo`` puts the
# App root first, which would import Flask ``app.py`` instead of demo/app.py.
_DEMO_DIR = str(Path(__file__).resolve().parent)
if sys.path[:1] != [_DEMO_DIR]:
    sys.path.insert(0, _DEMO_DIR)

from app import main  # noqa: E402

if __name__ == "__main__":
    main()
