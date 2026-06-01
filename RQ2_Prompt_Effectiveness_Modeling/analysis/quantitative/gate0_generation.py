from __future__ import annotations
"""Gate 0 quantitative model: code generation.

This script estimates whether prompt structure predicts the transition from
guidance-only interactions (NE) to interactions where ChatGPT generated code
(PA/PN). It fits baseline and PR-size-controlled logistic regression models and
writes both CSV and LaTeX-ready outputs.
"""
import argparse, sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, write_csv, write_latex_table, safe_logit_fit, format_effect

TERMS = [("Context", "Context (C)"), ("Specificity", "Specificity (S)"), ("Verification", "Verification (V)"), ("Log_PR_Size", "Log(PR Size)")]

def _fit_table(df, formula, label):
    model = safe_logit_fit(formula, df)
    conf = model.conf_int()
    rows=[]
    for term, nice in TERMS:
        if term in model.params.index:
            lo, hi = np.exp(conf.loc[term])
            rows.append({"Model": label, "Variable": nice, "OR": float(np.exp(model.params[term])), "CI_Low": float(lo), "CI_High": float(hi), "p_value": float(model.pvalues[term]), "Formatted": format_effect(float(np.exp(model.params[term])), float(lo), float(hi), float(model.pvalues[term]))})
    rows.append({"Model": label, "Variable": "Observations", "OR": int(model.nobs), "CI_Low": np.nan, "CI_High": np.nan, "p_value": np.nan, "Formatted": str(int(model.nobs))})
    return pd.DataFrame(rows)

def run(root: Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/.
    df=load_analysis_dataset(root)
    d=df[df.Outcome_Class.isin(["PA","PN","NE"])].dropna(subset=["Context","Specificity","Verification","Log_PR_Size"])
    d1=d
    base=_fit_table(d, "Generated_Code ~ Context + Specificity + Verification", "(1) Baseline")
    size=_fit_table(d1, "Generated_Code ~ Context + Specificity + Verification + Log_PR_Size", "(2) + PR Size")
    out=pd.concat([base,size], ignore_index=True)
    write_csv(out, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables/gate0_generation_model.csv")
    wide=out.pivot(index="Variable", columns="Model", values="Formatted").reset_index()
    write_latex_table(wide, root/"RQ2_Prompt_Effectiveness_Modeling/results/tables_tex/gate0_generation_model.tex", "Gate 0: Logistic Regression Results for Code Generation", "tab:gate0")
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
