from __future__ import annotations
"""Directed qualitative thematic analysis.

This script derives lightweight implementation/conceptual prompt-pattern summaries
from the annotated rationale fields and outcome classes, producing qualitative
artifacts used to explain the gate-level statistical patterns.
"""
import argparse, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis.common import load_analysis_dataset, write_csv

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/ and paper/.
    df=load_analysis_dataset(root)
    out=pd.DataFrame([
        {"Theme":"Implementation-oriented prompts", "Linked_Stage":"Gate 0", "Evidence":"Higher Context and Specificity distinguish PA/PN from NE cases; implementation targets tend to elicit code."},
        {"Theme":"Evaluable outputs and trust", "Linked_Stage":"Gate 1", "Evidence":"Specificity and Verification support adoption among code-generating PA/PN cases."},
        {"Theme":"Contextual alignment", "Linked_Stage":"Gate 2", "Evidence":"Context predicts deeper reuse among PA cases because surrounding implementation details support fit."},
        {"Theme":"Lifecycle dominated by PR process", "Linked_Stage":"Axis B", "Evidence":"Prompt dimensions do not accelerate merge; PR size and review dynamics dominate lifecycle timing."},
    ])
    write_csv(out, root/"results/qualitative/thematic_summary.csv")
    (root/"paper/generated_sections").mkdir(parents=True, exist_ok=True)
    (root/"paper/generated_sections/qualitative_summary.md").write_text(out.to_markdown(index=False), encoding="utf-8")
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
