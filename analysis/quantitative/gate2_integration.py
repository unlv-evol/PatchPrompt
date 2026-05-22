from __future__ import annotations
"""Gate 2 quantitative model: integration depth.

This script focuses on Patch Applied (PA) cases and models the fraction of
ChatGPT-generated code incorporated into the final PR. A fractional-logit style
GLM is used because the dependent variable is bounded between 0 and 1.
"""
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis.common import load_analysis_dataset, write_csv, write_latex_table, stars
import statsmodels.formula.api as smf
import statsmodels.api as sm
TERMS=[("Context","Context (C)"),("Specificity","Specificity (S)"),("Verification","Verification (V)"),("Log_PR_Size","Log(PR Size)")]
def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/ and paper/.
    df=load_analysis_dataset(root)
    d=df[df.Outcome_Class.eq("PA")].dropna(subset=["Context","Specificity","Verification","Log_PR_Size","Fraction_Adopted","Repository"]).copy()
    d["frac"]=(d["Fraction_Adopted"].astype(float)/100.0).clip(1e-6,1-1e-6)
    model=smf.glm("frac ~ Context + Specificity + Verification + Log_PR_Size", data=d, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups":d["Repository"]})
    me=model.get_margeff(at="overall", method="dydx")
    sf=me.summary_frame(); rows=[]
    for term,nice in TERMS:
        if term in sf.index:
            row=sf.loc[term]; eff=float(row["dy/dx"]); lo=float(row["Conf. Int. Low"]); hi=float(row["Cont. Int. Hi."] if "Cont. Int. Hi." in sf.columns else row["Conf. Int. Hi."]); p=float(row["Pr(>|z|)"])
            rows.append({"Variable":nice,"AME":eff,"CI_Low":lo,"CI_High":hi,"p_value":p,"Formatted":f"{eff:.3f}{stars(p)} [{lo:.3f}, {hi:.3f}]"})
    rows.append({"Variable":"Observations","AME":int(model.nobs),"CI_Low":np.nan,"CI_High":np.nan,"p_value":np.nan,"Formatted":str(int(model.nobs))})
    out=pd.DataFrame(rows)
    write_csv(out, root/"results/tables/gate2_integration_model.csv")
    write_latex_table(out[["Variable","Formatted"]], root/"paper/tables/gate2_integration_model.tex", "Gate 2: Fractional Logit Results for Fraction of Code Adopted", "tab:gate2")
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
