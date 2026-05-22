from __future__ import annotations
"""Full robustness and sensitivity analyses for the PatchTrack-Prompt study.

The main paper reports stage-based models for Gate 0 (code generation), Gate 1
(code adoption), and Gate 2 (integration depth). This script evaluates whether the
main qualitative findings are stable under common empirical-SE sensitivity checks:

1. Excluding the dominant repository in each modeling sample.
2. Excluding extreme pull-request sizes using the 95th percentile cutoff.
3. Excluding the most frequent programming language in each modeling sample.
4. Comparing individual prompt dimensions (C, S, V) with aggregate Prompt Quality
   Score (PQS) model specifications.

The canonical dataset is never modified. Repository and PR number are derived from
PR_Link at runtime via analysis.common.load_analysis_dataset().
"""

import argparse
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis.common import load_analysis_dataset, write_csv, write_latex_table, ensure_dir


def _or_ci(model, term: str) -> tuple[float, float, float, float]:
    ci = model.conf_int().loc[term]
    return (
        float(np.exp(model.params[term])),
        float(np.exp(ci[0])),
        float(np.exp(ci[1])),
        float(model.pvalues[term]),
    )


def _ame_ci_glm(model, term: str) -> tuple[float, float, float, float]:
    """Approximate AME and CI for fractional logit coefficient via derivative at sample mean.

    This is used for sensitivity comparison, not as a replacement for the primary
    Gate 2 table. It reports the marginal effect implied by the fitted fractional
    logit at the observed mean predicted probability.
    """
    beta = float(model.params[term])
    se = float(model.bse[term])
    mu = float(model.fittedvalues.mean())
    scale = mu * (1.0 - mu)
    ame = beta * scale
    lo = (beta - 1.96 * se) * scale
    hi = (beta + 1.96 * se) * scale
    p = float(model.pvalues[term])
    return ame, lo, hi, p


def _stars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def _fmt(value: float, lo: float, hi: float, p: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}{_stars(p)} [{lo:.{digits}f}, {hi:.{digits}f}]"


def _dominant_value(df: pd.DataFrame, col: str) -> str | None:
    vc = df[col].dropna().value_counts()
    if vc.empty:
        return None
    return str(vc.index[0])


def _gate_data(df: pd.DataFrame, gate: str) -> pd.DataFrame:
    if gate == "Gate 0":
        cols = ["Generated_Code", "Context", "Specificity", "Verification", "PQS", "Log_PR_Size"]
        return df[df.Outcome_Class.isin(["PA", "PN", "NE"])].dropna(subset=cols)
    if gate == "Gate 1":
        cols = ["Adopted_Code", "Context", "Specificity", "Verification", "PQS", "Log_PR_Size"]
        return df[df.Outcome_Class.isin(["PA", "PN"])].dropna(subset=cols)
    if gate == "Gate 2":
        cols = ["Fraction_Adopted", "Context", "Specificity", "Verification", "PQS", "Log_PR_Size"]
        d = df[df.Outcome_Class.eq("PA")].dropna(subset=cols).copy()
        # Fractional logit requires proportions in (0, 1). The canonical dataset stores percent values.
        d["Fraction_Adopted_Prop"] = d["Fraction_Adopted"] / 100.0
        d = d[(d["Fraction_Adopted_Prop"] > 0) & (d["Fraction_Adopted_Prop"] <= 1)]
        return d
    raise ValueError(gate)


def _apply_scenario(d: pd.DataFrame, scenario: str) -> tuple[pd.DataFrame, str]:
    if scenario == "Main sample":
        return d.copy(), "No exclusion"
    if scenario == "Exclude dominant repository":
        repo = _dominant_value(d, "Repository")
        if repo is None:
            return d.copy(), "No repository column available"
        return d[d["Repository"] != repo].copy(), f"Excluded repository: {repo}"
    if scenario == "Exclude extreme PR size":
        cutoff = float(d["PR_Size"].quantile(0.95))
        return d[d["PR_Size"] <= cutoff].copy(), f"Kept PR_Size <= 95th percentile ({cutoff:.2f})"
    if scenario == "Exclude dominant language":
        lang = _dominant_value(d, "PR_Language")
        if lang is None:
            return d.copy(), "No language column available"
        return d[d["PR_Language"] != lang].copy(), f"Excluded language: {lang}"
    raise ValueError(scenario)


def _fit_gate(gate: str, d: pd.DataFrame, spec: str):
    if gate in ["Gate 0", "Gate 1"]:
        y = "Generated_Code" if gate == "Gate 0" else "Adopted_Code"
        formula = f"{y} ~ {spec} + Log_PR_Size"
        return smf.logit(formula, data=d).fit(disp=False, maxiter=500)
    if gate == "Gate 2":
        formula = f"Fraction_Adopted_Prop ~ {spec} + Log_PR_Size"
        # Cluster by repository where possible, matching the paper's emphasis on repository-level dependence.
        model = smf.glm(formula, data=d, family=sm.families.Binomial())
        try:
            return model.fit(cov_type="cluster", cov_kwds={"groups": d["Repository"]})
        except Exception:
            return model.fit()
    raise ValueError(gate)


def _collect_results(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scenarios = [
        "Main sample",
        "Exclude dominant repository",
        "Exclude extreme PR size",
        "Exclude dominant language",
    ]
    gates = ["Gate 0", "Gate 1", "Gate 2"]
    specs = {
        "CSV dimensions": "Context + Specificity + Verification",
        "Aggregate PQS": "PQS",
    }

    rows = []
    exclusions = []
    fit_failures = []

    for gate in gates:
        base = _gate_data(df, gate)
        for scenario in scenarios:
            d, detail = _apply_scenario(base, scenario)
            exclusions.append({
                "Gate": gate,
                "Scenario": scenario,
                "N_before": len(base),
                "N_after": len(d),
                "Exclusion_Detail": detail,
            })
            for spec_name, spec in specs.items():
                if len(d) < 10:
                    fit_failures.append({"Gate": gate, "Scenario": scenario, "Specification": spec_name, "Reason": "Too few observations"})
                    continue
                try:
                    model = _fit_gate(gate, d, spec)
                except Exception as exc:  # keep pipeline robust and report failure transparently
                    fit_failures.append({"Gate": gate, "Scenario": scenario, "Specification": spec_name, "Reason": str(exc)})
                    continue

                terms = ["Context", "Specificity", "Verification"] if spec_name == "CSV dimensions" else ["PQS"]
                for term in terms:
                    if term not in model.params.index:
                        continue
                    if gate in ["Gate 0", "Gate 1"]:
                        value, lo, hi, p = _or_ci(model, term)
                        metric = "OR"
                        formatted = _fmt(value, lo, hi, p)
                    else:
                        value, lo, hi, p = _ame_ci_glm(model, term)
                        metric = "AME"
                        formatted = _fmt(value, lo, hi, p, digits=3)
                    rows.append({
                        "Gate": gate,
                        "Scenario": scenario,
                        "Specification": spec_name,
                        "N": int(model.nobs) if hasattr(model, "nobs") else len(d),
                        "Term": term,
                        "Metric": metric,
                        "Estimate": value,
                        "CI_Low": lo,
                        "CI_High": hi,
                        "p_value": p,
                        "Formatted": formatted,
                    })

    return pd.DataFrame(rows), pd.DataFrame(exclusions), pd.DataFrame(fit_failures)


def _make_summary(results: pd.DataFrame, exclusions: pd.DataFrame, failures: pd.DataFrame) -> str:
    def sig_terms(gate: str, scenario: str, spec: str) -> list[str]:
        sub = results[(results.Gate == gate) & (results.Scenario == scenario) & (results.Specification == spec)]
        return sub[sub.p_value < 0.05]["Term"].tolist()

    lines = [
        "# Robustness and Sensitivity Analysis Summary",
        "",
        "This file summarizes robustness checks for the stage-based models. The checks evaluate whether the main qualitative findings remain stable after excluding the dominant repository, excluding extreme pull-request sizes, excluding the most frequent programming language, and replacing individual prompt dimensions with aggregate PQS.",
        "",
        "## Exclusion details",
        "",
        exclusions.to_markdown(index=False),
        "",
        "## Qualitative stability of main findings",
        "",
    ]
    for gate in ["Gate 0", "Gate 1", "Gate 2"]:
        lines.append(f"### {gate}")
        for scenario in ["Main sample", "Exclude dominant repository", "Exclude extreme PR size", "Exclude dominant language"]:
            terms = sig_terms(gate, scenario, "CSV dimensions")
            phrase = ", ".join(terms) if terms else "no prompt dimension reaches p < 0.05"
            lines.append(f"- {scenario}: {phrase}.")
        lines.append("")

    if not failures.empty:
        lines += ["## Fit warnings/failures", "", failures.to_markdown(index=False), ""]
    else:
        lines += ["## Fit warnings/failures", "", "No model fits failed.", ""]
    return "\n".join(lines)


def run(root: Path):
    df = load_analysis_dataset(root)
    results, exclusions, failures = _collect_results(df)

    out_dir = root / "results" / "diagnostics"
    paper_dir = root / "paper" / "tables"
    ensure_dir(out_dir)
    ensure_dir(paper_dir)

    write_csv(results, out_dir / "full_robustness_sensitivity_results.csv")
    write_csv(exclusions, out_dir / "robustness_exclusion_details.csv")
    write_csv(failures, out_dir / "robustness_fit_warnings.csv")

    # Keep the previous file name as a concise evaluator-facing subset.
    concise = results[(results["Specification"] == "CSV dimensions")].copy()
    write_csv(concise, out_dir / "sensitivity_analysis.csv")

    # Separate key requested result files.
    write_csv(results[results["Scenario"] == "Exclude dominant repository"], out_dir / "dominant_repository_exclusion.csv")
    write_csv(results[results["Scenario"] == "Exclude extreme PR size"], out_dir / "extreme_pr_size_exclusion.csv")
    write_csv(results[results["Scenario"] == "Exclude dominant language"], out_dir / "dominant_language_exclusion.csv")
    write_csv(results[results["Specification"] == "Aggregate PQS"], out_dir / "pqs_vs_dimension_models.csv")

    # LaTeX outputs for paper appendix / replication appendix.
    latex_cols = ["Gate", "Scenario", "Specification", "N", "Term", "Metric", "Formatted"]
    write_latex_table(results[latex_cols], paper_dir / "full_robustness_sensitivity_results.tex", "Full robustness and sensitivity results", "tab:full_robustness_sensitivity")
    write_latex_table(results[results["Specification"] == "Aggregate PQS"][latex_cols], paper_dir / "pqs_vs_dimension_models.tex", "Aggregate PQS sensitivity models", "tab:pqs_sensitivity")

    summary = _make_summary(results, exclusions, failures)
    (out_dir / "robustness_sensitivity_summary.md").write_text(summary, encoding="utf-8")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    run(Path(args.root).resolve())
