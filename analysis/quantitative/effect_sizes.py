from __future__ import annotations
"""Descriptive effect-size summaries.

This script creates compact summaries of the main observed differences across
outcome classes, including PQS and adoption/integration measures. These outputs
are intended for quick inspection and paper appendix tables.
"""
import argparse, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis.common import load_analysis_dataset, write_csv, write_latex_table

def run(root:Path):
    # Load the canonical processed dataset and write regenerated artifacts under results/ and paper/.
    df=load_analysis_dataset(root)
    rows=[]
    for col in ["Context","Specificity","Verification","PQS","PR_Size","Exp_Author_Repo"]:
        if col in df:
            rows.append({"Variable":col,"Mean":df[col].mean(),"Median":df[col].median(),"StdDev":df[col].std(),"Min":df[col].min(),"Max":df[col].max(),"N":df[col].count()})
    out=pd.DataFrame(rows)
    write_csv(out, root/"results/tables/effect_sizes.csv"); write_latex_table(out.round(3), root/"paper/tables/effect_sizes.tex", "Extended descriptive statistics", "tab:effect-sizes")
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root', default='.')
    run(Path(p.parse_args().root).resolve())
