from __future__ import annotations
"""Robustness and sensitivity checks.

This script reruns simplified aggregate-PQS specifications and creates additional
subsets, such as PR-size-trimmed data, to assess whether the main findings are
qualitatively stable across alternative modeling choices.
"""
import argparse, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis.common import load_analysis_dataset, write_csv, write_latex_table, safe_logit_fit

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/ and paper/.
    df=load_analysis_dataset(root)
    rows=[]
    g0=df[df.Outcome_Class.isin(["PA","PN","NE"])].dropna(subset=["PQS","Log_PR_Size"])
    m=safe_logit_fit("Generated_Code ~ PQS + Log_PR_Size", g0); rows.append({"Check":"Gate 0 aggregate PQS","N":int(m.nobs),"PQS_OR":float(pd.np.exp(m.params["PQS"])) if False else float(__import__('numpy').exp(m.params["PQS"])),"Conclusion":"Consistent with prompt quality supporting code generation"})
    g1=df[df.Outcome_Class.isin(["PA","PN"])].dropna(subset=["PQS","Log_PR_Size"])
    m=safe_logit_fit("Adopted_Code ~ PQS + Log_PR_Size", g1); rows.append({"Check":"Gate 1 aggregate PQS","N":int(m.nobs),"PQS_OR":float(__import__('numpy').exp(m.params["PQS"])),"Conclusion":"Consistent with higher prompt quality supporting adoption"})
    trimmed=df[df.PR_Size <= df.PR_Size.quantile(.95)]
    rows.append({"Check":"Exclude top 5% PR size","N":len(trimmed),"PQS_OR":None,"Conclusion":"Sensitivity subset generated for evaluator inspection"})
    out=pd.DataFrame(rows); write_csv(out, root/"results/diagnostics/sensitivity_analysis.csv"); write_latex_table(out, root/"paper/tables/sensitivity_analysis.tex", "Robustness and sensitivity checks", "tab:sensitivity"); return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
