from __future__ import annotations
"""Qualitative code-frequency summaries.

This script summarizes recurring qualitative code/theme assignments by outcome
class and prompt dimension. It supports triangulation between the quantitative gate
models and qualitative interpretation.
"""
import argparse, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, write_csv, write_latex_table

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/.
    df=load_analysis_dataset(root)
    rows=[]
    for dim in ["Context","Specificity","Verification"]:
        tab=df.groupby(["Outcome_Class", dim], dropna=False).size().reset_index(name="Count")
        tab["Dimension"]=dim; tab=tab.rename(columns={dim:"Score"}); rows.append(tab[["Dimension","Outcome_Class","Score","Count"]])
    out=pd.concat(rows, ignore_index=True); write_csv(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/qualitative/code_frequencies.csv"); write_latex_table(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables_tex/code_frequencies.tex", "Prompt-structure score frequencies by outcome class", "tab:code-frequencies"); return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
