from __future__ import annotations
"""Axis B lifecycle model: merge and close outcomes.

This script approximates the paper's PR lifecycle analysis by fitting
cause-specific time-to-resolution models for merge and closure outcomes using the
available processed dataset. It exports hazard-ratio-style summaries and keeps the
analysis separate from the code-level gate models.
"""
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, write_csv, write_latex_table, format_effect
from statsmodels.duration.hazard_regression import PHReg
TERMS=[("Context","Context (C)"),("Specificity","Specificity (S)"),("Verification","Verification (V)"),("Log_PR_Size","Log(PR Size)")]

def _fit(d, event_col, label):
    cols=["Time_To_Event",event_col,"Context","Specificity","Verification","Log_PR_Size"]
    m=d.dropna(subset=cols).copy()
    endog=m["Time_To_Event"].astype(float).clip(lower=1e-6)
    exog=m[["Context","Specificity","Verification","Log_PR_Size"]].astype(float)
    event=m[event_col].astype(int)
    res=PHReg(endog, exog, status=event).fit(disp=False)
    names=list(exog.columns); rows=[]
    for i,(term,nice) in enumerate(TERMS):
        beta=float(res.params[i]); se=float(res.bse[i]); p=float(res.pvalues[i])
        lo=np.exp(beta-1.96*se); hi=np.exp(beta+1.96*se); hr=np.exp(beta)
        rows.append({"Model":label,"Variable":nice,"HR":hr,"CI_Low":lo,"CI_High":hi,"p_value":p,"Formatted":format_effect(hr,lo,hi,p)})
    rows.append({"Model":label,"Variable":"Observations","HR":len(m),"CI_Low":np.nan,"CI_High":np.nan,"p_value":np.nan,"Formatted":str(len(m))})
    return pd.DataFrame(rows)

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/.
    df=load_analysis_dataset(root).dropna(subset=["PQS"]).copy()
    out=pd.concat([_fit(df,"Merge_Event","Merge Hazard"), _fit(df,"Close_Event","Close Hazard")], ignore_index=True)
    write_csv(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables/axisb_lifecycle_model.csv")
    wide=out.pivot(index="Variable", columns="Model", values="Formatted").reset_index()
    write_latex_table(wide, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables_tex/axisb_lifecycle_model.tex", "Axis B: Cause-Specific Cox Results for PR Lifecycle", "tab:axisb")
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
