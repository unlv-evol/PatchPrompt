from __future__ import annotations
"""Generate additional methodological-alignment outputs referenced in the paper.

These outputs complement the primary models by documenting repository-clustered
standard-error variants, mixed-effects approximations, holdout stability checks, and
prompt-length control feasibility. They are robustness aids rather than replacements
for the main reported models.
"""
import argparse, re
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


def _repo(link: str) -> str:
    m = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)", str(link))
    return m.group(1) if m else "unknown"


def _prep(root: Path) -> pd.DataFrame:
    df = pd.read_csv(root / "Dataset_Construction" / "processed_data" / "final_analysis_dataset.csv")
    df = df.rename(columns={"Case ID": "Case_ID", "PQS ": "PQS"})
    df["Repository"] = df["PR_Link"].map(_repo)
    df["Generated_Code"] = df["Outcome_Class"].isin(["PA", "PN"]).astype(int)
    df["Adopted_Code"] = (df["Outcome_Class"] == "PA").astype(int)
    df["Prompt_Text_Length"] = np.nan
    return df


def _clustered_models(df: pd.DataFrame, out: Path) -> None:
    rows = []
    specs = [
        ("Gate0", df[df["Outcome_Class"].isin(["PA", "PN", "NE"])].dropna(subset=["Generated_Code","Context","Specificity","Verification","Log_PR_Size"]), "Generated_Code ~ Context + Specificity + Verification + Log_PR_Size", "logit"),
        ("Gate1", df[df["Outcome_Class"].isin(["PA", "PN"])].dropna(subset=["Adopted_Code","Context","Specificity","Verification","Log_PR_Size"]), "Adopted_Code ~ Context + Specificity + Verification + Log_PR_Size", "logit"),
        ("Gate2", df[df["Outcome_Class"].eq("PA")].dropna(subset=["Fraction_Adopted","Context","Specificity","Verification","Log_PR_Size"]), "Fraction_Adopted ~ Context + Specificity + Verification + Log_PR_Size", "ols"),
    ]
    for gate, sub, formula, fam in specs:
        try:
            if fam == "logit":
                fit = smf.logit(formula, data=sub).fit(disp=False, maxiter=200)
                rob = fit.get_robustcov_results(cov_type="cluster", groups=sub["Repository"])
            else:
                fit = smf.ols(formula, data=sub).fit()
                rob = fit.get_robustcov_results(cov_type="cluster", groups=sub["Repository"])
            params = pd.Series(rob.params, index=fit.params.index)
            pvals = pd.Series(rob.pvalues, index=fit.params.index)
            conf = pd.DataFrame(rob.conf_int(), index=fit.params.index, columns=["CI_Low", "CI_High"])
            for term in params.index:
                rows.append({"Gate": gate, "Model": "repository_clustered_se", "N": len(sub), "Repositories": sub["Repository"].nunique(), "Term": term, "Estimate": params[term], "CI_Low": conf.loc[term, "CI_Low"], "CI_High": conf.loc[term, "CI_High"], "p_value": pvals[term], "Status": "estimated"})
        except Exception as exc:
            rows.append({"Gate": gate, "Model": "repository_clustered_se", "N": len(sub), "Repositories": sub["Repository"].nunique(), "Term": "model", "Estimate": np.nan, "CI_Low": np.nan, "CI_High": np.nan, "p_value": np.nan, "Status": f"not estimated: {exc}"})
    pd.DataFrame(rows).to_csv(out / "clustered_se_models.csv", index=False)


def _mixed_effects(df: pd.DataFrame, out: Path) -> None:
    rows = []
    specs = [
        ("Gate0", df[df["Outcome_Class"].isin(["PA", "PN", "NE"])].dropna(subset=["Generated_Code","Context","Specificity","Verification","Log_PR_Size"]), "Generated_Code ~ Context + Specificity + Verification + Log_PR_Size"),
        ("Gate1", df[df["Outcome_Class"].isin(["PA", "PN"])].dropna(subset=["Adopted_Code","Context","Specificity","Verification","Log_PR_Size"]), "Adopted_Code ~ Context + Specificity + Verification + Log_PR_Size"),
        ("Gate2", df[df["Outcome_Class"].eq("PA")].dropna(subset=["Fraction_Adopted","Context","Specificity","Verification","Log_PR_Size"]), "Fraction_Adopted ~ Context + Specificity + Verification + Log_PR_Size"),
    ]
    # Use linear mixed-effects approximations with repository random intercepts.
    for gate, sub, formula in specs:
        y = formula.split("~")[0].strip()
        try:
            if sub["Repository"].nunique() < 2:
                raise ValueError("fewer than two repository groups")
            fit = smf.mixedlm(formula, data=sub, groups=sub["Repository"]).fit(reml=False, method="lbfgs", disp=False)
            for term, est in fit.params.items():
                rows.append({"Gate": gate, "Model": "repository_random_intercept_lmm", "Outcome": y, "N": len(sub), "Repositories": sub["Repository"].nunique(), "Term": term, "Estimate": est, "p_value": fit.pvalues.get(term, np.nan), "Status": "estimated_linear_mixed_effects_approximation"})
        except Exception as exc:
            rows.append({"Gate": gate, "Model": "repository_random_intercept_lmm", "Outcome": y, "N": len(sub), "Repositories": sub["Repository"].nunique(), "Term": "model", "Estimate": np.nan, "p_value": np.nan, "Status": f"not estimated: {exc}"})
    pd.DataFrame(rows).to_csv(out / "mixed_effects_models.csv", index=False)


def _holdout(df: pd.DataFrame, out: Path, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    rows = []
    scenarios = [
        ("Gate0", df[df["Outcome_Class"].isin(["PA", "PN", "NE"])].dropna(subset=["Generated_Code","Context","Specificity","Verification","Log_PR_Size"]), "Generated_Code ~ Context + Specificity + Verification + Log_PR_Size", "Generated_Code"),
        ("Gate1", df[df["Outcome_Class"].isin(["PA", "PN"])].dropna(subset=["Adopted_Code","Context","Specificity","Verification","Log_PR_Size"]), "Adopted_Code ~ Context + Specificity + Verification + Log_PR_Size", "Adopted_Code"),
        ("Gate2", df[df["Outcome_Class"].eq("PA")].dropna(subset=["Fraction_Adopted","Context","Specificity","Verification","Log_PR_Size"]), "Fraction_Adopted ~ Context + Specificity + Verification + Log_PR_Size", "Fraction_Adopted"),
    ]
    terms = ["Context", "Specificity", "Verification", "Log_PR_Size"]
    for gate, sub, formula, outcome in scenarios:
        for rep in range(20):
            mask = rng.random(len(sub)) < 0.8
            train = sub.loc[mask]
            try:
                fit = (smf.logit(formula, data=train).fit(disp=False, maxiter=200) if gate in ["Gate0","Gate1"] else smf.ols(formula, data=train).fit())
                for term in terms:
                    rows.append({"Gate": gate, "Replicate": rep + 1, "Train_N": len(train), "Term": term, "Estimate": fit.params.get(term, np.nan), "p_value": fit.pvalues.get(term, np.nan), "Sign": np.sign(fit.params.get(term, np.nan)), "Status": "estimated"})
            except Exception as exc:
                rows.append({"Gate": gate, "Replicate": rep + 1, "Train_N": len(train), "Term": "model", "Estimate": np.nan, "p_value": np.nan, "Sign": np.nan, "Status": f"not estimated: {exc}"})
    pd.DataFrame(rows).to_csv(out / "holdout_stability_checks.csv", index=False)


def _prompt_length_controls(df: pd.DataFrame, out: Path) -> None:
    # The canonical processed dataset does not include the full prompt text. We record
    # this explicitly instead of using rationale length as a misleading proxy.
    rows = [
        {"Gate": "Gate0", "Model": "prompt_length_control", "Status": "not_estimated", "Reason": "Full prompt text is not included in final_analysis_dataset.csv; raw PDFs are provided for traceability.", "Required_Field": "Developer_Prompt_Text_Length"},
        {"Gate": "Gate1", "Model": "prompt_length_control", "Status": "not_estimated", "Reason": "Full prompt text is not included in final_analysis_dataset.csv; raw PDFs are provided for traceability.", "Required_Field": "Developer_Prompt_Text_Length"},
        {"Gate": "Gate2", "Model": "prompt_length_control", "Status": "not_estimated", "Reason": "Full prompt text is not included in final_analysis_dataset.csv; raw PDFs are provided for traceability.", "Required_Field": "Developer_Prompt_Text_Length"},
    ]
    pd.DataFrame(rows).to_csv(out / "prompt_length_control_models.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out = root / "RQ2_Prompt_Effectiveness_Modeling" / "results" / "diagnostics"
    out.mkdir(parents=True, exist_ok=True)
    df = _prep(root)
    # The comprehensive robustness script now owns clustered-SE, holdout,
    # and prompt-length-control outputs. This helper only generates the
    # mixed-effects approximation so it does not overwrite the reviewer-guided
    # robustness artifacts produced earlier in the pipeline.
    _mixed_effects(df, out)


if __name__ == "__main__":
    main()
