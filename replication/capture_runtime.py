from __future__ import annotations
"""Capture runtime environment details for artifact evaluation.

This helper records the Python executable, platform details, selected dependency
versions, and a complete `pip freeze` snapshot. It is intentionally lightweight so it
can run during smoke reproduction without network access.
"""
import json, platform, subprocess, sys, time, os
from pathlib import Path

IMPORTANT_PACKAGES = ["pandas", "numpy", "statsmodels", "matplotlib", "scipy", "sklearn", "yaml", "reportlab"]


def _pkg_version(name: str) -> str | None:
    try:
        mod = __import__(name)
        return getattr(mod, "__version__", getattr(mod, "Version", None))
    except Exception:
        return None


def capture(root: Path) -> None:
    env_dir = root / "environment"
    runtime_dir = root / "RQ2_Prompt_Effectiveness_Modeling" / "results" / "runtime"
    env_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    try:
        freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    except Exception as exc:
        freeze = f"# pip freeze unavailable: {exc}\n"
    (env_dir / "pip_freeze.txt").write_text(freeze, encoding="utf-8")

    conda_yml = "name: patchtrack-replication-frozen\nchannels:\n  - conda-forge\n  - defaults\ndependencies:\n  - python=" + platform.python_version() + "\n  - pip\n  - pip:\n"
    for line in freeze.splitlines():
        if line.strip() and not line.startswith("#"):
            conda_yml += f"      - {line}\n"
    (env_dir / "conda_env_frozen.yml").write_text(conda_yml, encoding="utf-8")

    info = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "working_directory": str(root),
        "environment_variables_recorded": ["PYTHONPATH"],
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "package_versions": {pkg: _pkg_version(pkg) for pkg in IMPORTANT_PACKAGES},
    }
    for p in [env_dir / "runtime_capture.json", runtime_dir / "runtime_environment.json"]:
        p.write_text(json.dumps(info, indent=2), encoding="utf-8")


if __name__ == "__main__":
    capture(Path(__file__).resolve().parent.parent)
