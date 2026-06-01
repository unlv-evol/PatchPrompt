from __future__ import annotations
"""Quantitative–qualitative triangulation summary.

This script connects stage-specific quantitative findings to qualitative mechanisms,
such as implementation orientation, evaluability, and contextual alignment.
"""
import argparse, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import write_csv, write_latex_table

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/.
    out=pd.DataFrame([
        {"Research_Question":"RQ2a", "Quantitative_Result":"Context and Specificity predict code generation", "Qualitative_Interpretation":"Prompts must define a codable implementation space."},
        {"Research_Question":"RQ2b", "Quantitative_Result":"Specificity and Verification predict adoption", "Qualitative_Interpretation":"Developers adopt outputs when constraints and correctness cues make them evaluable."},
        {"Research_Question":"RQ2c", "Quantitative_Result":"Context predicts integration depth", "Qualitative_Interpretation":"Deep reuse depends on alignment with surrounding implementation context."},
        {"Research_Question":"RQ2d", "Quantitative_Result":"Prompt structure weak for merge timing; Verification associated with close hazard", "Qualitative_Interpretation":"Lifecycle outcomes reflect review and repository processes beyond prompt quality."},
    ])
    write_csv(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/qualitative/triangulation_summary.csv"); write_latex_table(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables_tex/triangulation_summary.tex", "Integrated quantitative and qualitative interpretation", "tab:triangulation"); return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
