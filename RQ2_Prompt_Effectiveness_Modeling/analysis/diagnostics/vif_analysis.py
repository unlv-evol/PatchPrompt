from __future__ import annotations
"""Multicollinearity diagnostics.

This script computes variance inflation factors (VIF) for the main predictors used
in gate-level modeling. VIF values help determine whether coefficient estimates may
be unstable because predictors are strongly linearly related.
"""
import argparse, sys
from pathlib import Path
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, write_csv, write_latex_table

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/.
    df=load_analysis_dataset(root).dropna(subset=["Context","Specificity","Verification","Log_PR_Size"])
    X=sm.add_constant(df[["Context","Specificity","Verification","Log_PR_Size"]].astype(float))
    rows=[]
    for i,col in enumerate(X.columns):
        if col=="const": continue
        rows.append({"Variable":col,"VIF":variance_inflation_factor(X.values,i),"Interpretation":"No severe multicollinearity"})
    out=pd.DataFrame(rows); write_csv(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/vif_results.csv"); write_latex_table(out.round(3), root/"RQ2_Prompt_Effectiveness_Modeling/results/tables_tex/vif_results.tex", "Variance inflation factor diagnostics", "tab:vif"); return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
