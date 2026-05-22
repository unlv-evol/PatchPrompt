from __future__ import annotations
"""Run metadata collector.

This helper records environment metadata, Python version, git hash when available,
seed, and timestamp so each replication run leaves an auditable trace.
"""
from pathlib import Path
import json, os, platform, subprocess, sys
from datetime import datetime, timezone

def _git_hash() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None

def write_run_metadata(path: Path, smoke: bool = False, seed: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "smoke": smoke,
        "seed": seed,
        "python": sys.version,
        "platform": platform.platform(),
        "git_hash": _git_hash(),
        "cwd": os.getcwd(),
    }
    path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
