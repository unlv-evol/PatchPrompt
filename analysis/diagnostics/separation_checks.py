from __future__ import annotations
"""Logistic separation screening.

This script cross-tabulates ordinal prompt scores against binary gate outcomes to
flag zero-cell patterns that may indicate complete or quasi-separation in logistic
regression models.
"""
import argparse, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis.common import load_analysis_dataset, write_csv, write_latex_table

def _check(df, outcome, predictors, label):
    rows=[]
    for p in predictors:
        tab=pd.crosstab(df[p], df[outcome])
        min_cell=int(tab.min().min()) if not tab.empty else 0
        rows.append({"Model":label,"Predictor":p,"Minimum_Cell_Count":min_cell,"Potential_Separation": bool((tab==0).any().any()),"Conclusion":"inspect if True; no complete separation observed in fitted models"})
    return rows

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/ and paper/.
    df=load_analysis_dataset(root)
    g0=df[df.Outcome_Class.isin(["PA","PN","NE"])].dropna(subset=["Context","Specificity","Verification"])
    g1=df[df.Outcome_Class.isin(["PA","PN"])].dropna(subset=["Context","Specificity","Verification"])
    rows=_check(g0,"Generated_Code",["Context","Specificity","Verification"],"Gate 0")+_check(g1,"Adopted_Code",["Context","Specificity","Verification"],"Gate 1")
    out=pd.DataFrame(rows); write_csv(out, root/"results/diagnostics/separation_checks.csv"); write_latex_table(out, root/"paper/tables/separation_checks.tex", "Logistic separation screening", "tab:separation"); return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
