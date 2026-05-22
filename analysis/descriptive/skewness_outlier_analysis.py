from __future__ import annotations
"""Convenience wrapper for skewness and outlier summaries."""
from pathlib import Path
from analysis.descriptive.appendix_b_descriptives import run

if __name__ == "__main__":
    run(Path("."))
