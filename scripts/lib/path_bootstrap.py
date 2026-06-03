"""Insert repo + scripts directories on sys.path for CLI scripts."""

from __future__ import annotations

import sys
from pathlib import Path


def bootstrap() -> tuple[Path, Path]:
    scripts_dir = Path(__file__).resolve().parent.parent
    repo_root = scripts_dir.parent
    for entry in (str(repo_root), str(scripts_dir)):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    return repo_root, scripts_dir
