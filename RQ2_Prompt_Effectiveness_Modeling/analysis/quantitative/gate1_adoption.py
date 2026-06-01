from __future__ import annotations
"""Gate 1 quantitative model: code adoption.

This script restricts the data to cases where generated code exists (PA/PN) and
models whether that code was adopted in the pull request. It uses Context,
Specificity, Verification, and optionally log PR size as predictors, then exports
odds-ratio tables for the paper and replication results.
"""
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, write_csv, write_latex_table, safe_logit_fit, format_effect
TERMS=[("Context","Context (C)"),("Specificity","Specificity (S)"),("Verification","Verification (V)"),("Log_PR_Size","Log(PR Size)")]
def _fit_table(df, formula, label):
    model=safe_logit_fit(formula, df); conf=model.conf_int(); rows=[]
    for term,nice in TERMS:
        if term in model.params.index:
            lo,hi=np.exp(conf.loc[term]); effect=float(np.exp(model.params[term])); p=float(model.pvalues[term])
            rows.append({"Model":label,"Variable":nice,"OR":effect,"CI_Low":float(lo),"CI_High":float(hi),"p_value":p,"Formatted":format_effect(effect,float(lo),float(hi),p)})
    rows.append({"Model":label,"Variable":"Observations","OR":int(model.nobs),"CI_Low":np.nan,"CI_High":np.nan,"p_value":np.nan,"Formatted":str(int(model.nobs))})
    return pd.DataFrame(rows)
def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/.
    df=load_analysis_dataset(root)
    d=df[df.Outcome_Class.isin(["PA","PN"])].dropna(subset=["Context","Specificity","Verification","Log_PR_Size"])
    d1=d
    out=pd.concat([_fit_table(d,"Adopted_Code ~ Context + Specificity + Verification","(1) Baseline"), _fit_table(d1,"Adopted_Code ~ Context + Specificity + Verification + Log_PR_Size","(2) + PR Size")], ignore_index=True)
    write_csv(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables/gate1_adoption_model.csv")
    wide=out.pivot(index="Variable", columns="Model", values="Formatted").reset_index()
    write_latex_table(wide, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables_tex/gate1_adoption_model.tex", "Gate 1: Logistic Regression Results for Code Adoption", "tab:gate1")
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
