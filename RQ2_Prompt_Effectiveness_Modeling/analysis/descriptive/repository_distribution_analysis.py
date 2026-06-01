from __future__ import annotations
"""Convenience wrapper for repository-frequency descriptive outputs."""
from pathlib import Path
from RQ2_Prompt_Effectiveness_Modeling.analysis.descriptive.appendix_b_descriptives import run

if __name__ == "__main__":
    run(Path("."))
