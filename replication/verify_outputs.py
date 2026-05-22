from __future__ import annotations
"""Output validation script.

This script reads expected_outputs.yaml and checks that the expected artifacts exist,
are nonempty, and satisfy required CSV schemas where specified. It supports the
`make verify` evaluator workflow.
"""
import argparse, sys
from pathlib import Path
import yaml
import pandas as pd


def _check(path: Path, validation: str, required_columns: list[str] | None = None) -> list[str]:
    errors=[]
    if validation in {"exists", "nonempty", "csv_schema"} and not path.exists():
        return [f"Missing expected artifact: {path}"]
    if validation in {"nonempty", "csv_schema"} and path.stat().st_size == 0:
        errors.append(f"Artifact is empty: {path}")
    if validation == "csv_schema":
        df = pd.read_csv(path)
        missing = [c for c in (required_columns or []) if c not in df.columns]
        if missing:
            errors.append(f"{path} missing required columns {missing}")
    return errors


def main() -> None:
    parser=argparse.ArgumentParser(description="Verify generated replication outputs.")
    parser.add_argument("--expected", required=True)
    parser.add_argument("--smoke", action="store_true")
    args=parser.parse_args()
    expected_path=Path(args.expected).resolve()
    root=expected_path.parent.parent
    spec=yaml.safe_load(expected_path.read_text(encoding="utf-8")) or {}
    errors=[]
    for item in spec.get("artifacts", []):
        if args.smoke and not item.get("smoke", False):
            continue
        errors += _check(root / item["path"], item.get("validation", "exists"), item.get("required_columns"))
    if errors:
        for e in errors: print(f"[FAIL] {e}")
        sys.exit(1)
    print("All expected replication outputs verified successfully.")

if __name__ == "__main__":
    main()
