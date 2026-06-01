from __future__ import annotations
"""Extended Appendix B descriptive analyses.

This module expands the descriptive analysis layer beyond the paper's compact
Table 3 and Appendix B tables. It produces machine-readable CSV summaries,
figures, and a markdown narrative that support the paper's claims that pull
request size and contributor experience are highly right-skewed and therefore
motivate log transformations and robust modeling checks.

The canonical dataset is never edited. All repository identifiers, PR numbers,
and normalized PQS values are derived at runtime through ``load_analysis_dataset``.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, write_csv, write_latex_table

PROMPT_DIMS = ["Context", "Specificity", "Verification"]
NUMERIC_DESCRIPTIVE_FIELDS = ["PQS", "PR_Size", "Log_PR_Size", "Exp_Author_Repo", "Time_To_Event", "Fraction_Adopted"]


def _numeric_summary(series: pd.Series) -> dict[str, float | int]:
    """Return a compact distribution summary for a numeric series."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return {"N": 0, "Mean": np.nan, "Median": np.nan, "Std_Dev": np.nan, "Min": np.nan, "Q1": np.nan, "Q3": np.nan, "IQR": np.nan, "Max": np.nan, "Skewness": np.nan}
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    return {
        "N": int(s.shape[0]),
        "Mean": round(float(s.mean()), 2),
        "Median": round(float(s.median()), 2),
        "Std_Dev": round(float(s.std()), 2),
        "Min": round(float(s.min()), 2),
        "Q1": round(float(q1), 2),
        "Q3": round(float(q3), 2),
        "IQR": round(float(q3 - q1), 2),
        "Max": round(float(s.max()), 2),
        "Skewness": round(float(s.skew()), 2),
    }


def appendix_b_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize core numeric variables used in Appendix B and modeling."""
    rows = []
    for field in NUMERIC_DESCRIPTIVE_FIELDS:
        if field in df.columns:
            rows.append({"Variable": field, **_numeric_summary(df[field])})
    return pd.DataFrame(rows)


def prompt_dimension_distributions(df: pd.DataFrame) -> pd.DataFrame:
    """Count ordinal score frequencies for Context, Specificity, and Verification."""
    rows = []
    for dim in PROMPT_DIMS:
        counts = df[dim].value_counts(dropna=False).sort_index()
        for score, count in counts.items():
            rows.append({"Dimension": dim, "Score": score, "Count": int(count), "Percent": round(100 * count / len(df), 2)})
    return pd.DataFrame(rows)


def repository_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Count observations per GitHub repository derived from PR_Link."""
    return df["Repository"].fillna("Unknown").value_counts().rename_axis("Repository").reset_index(name="Count")


def language_distribution_full(df: pd.DataFrame) -> pd.DataFrame:
    """Count observations by primary programming language."""
    return df["PR_Language"].fillna("Unknown").value_counts().rename_axis("Language").reset_index(name="Count")


def skewness_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute skewness and mean--median gaps for skew-sensitive variables."""
    variables = ["PR_Size", "Exp_Author_Repo", "Time_To_Event", "PQS"]
    rows = []
    for var in variables:
        s = pd.to_numeric(df[var], errors="coerce").dropna()
        if s.empty:
            continue
        rows.append({
            "Variable": var,
            "N": int(len(s)),
            "Mean": round(float(s.mean()), 2),
            "Median": round(float(s.median()), 2),
            "Mean_Median_Gap": round(float(s.mean() - s.median()), 2),
            "Skewness": round(float(s.skew()), 2),
            "Interpretation": "right-skewed" if s.skew() > 1 else ("approximately symmetric" if abs(s.skew()) <= 1 else "left-skewed"),
        })
    return pd.DataFrame(rows)


def outlier_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Identify upper-tail outliers using the conventional 1.5*IQR rule."""
    rows = []
    for var in ["PR_Size", "Exp_Author_Repo", "Time_To_Event"]:
        s = pd.to_numeric(df[var], errors="coerce").dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        lower = q1 - 1.5 * iqr
        mask = pd.to_numeric(df[var], errors="coerce") > upper
        top_cases = df.loc[mask, ["Case ID", "PR_Link", var]].sort_values(var, ascending=False).head(10)
        rows.append({
            "Variable": var,
            "Q1": round(float(q1), 2),
            "Q3": round(float(q3), 2),
            "IQR": round(float(iqr), 2),
            "Lower_Threshold": round(float(lower), 2),
            "Upper_Threshold": round(float(upper), 2),
            "Upper_Outlier_Count": int(mask.sum()),
            "Top_Outlier_Cases": "; ".join(f"{r['Case ID']} ({int(r[var]) if pd.notna(r[var]) else 'NA'})" for _, r in top_cases.iterrows()),
        })
    return pd.DataFrame(rows)


def prompt_structure_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlations among prompt-quality dimensions and PQS."""
    cols = ["Context", "Specificity", "Verification", "PQS"]
    corr = df[cols].corr(method="pearson").round(3).reset_index().rename(columns={"index": "Variable"})
    return corr


def _plot_histogram(series: pd.Series, title: str, xlabel: str, path: Path, bins: int = 30) -> None:
    """Write a single histogram figure without changing the canonical data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4.5))
    pd.to_numeric(series, errors="coerce").dropna().hist(bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def _plot_bar(df: pd.DataFrame, label_col: str, count_col: str, title: str, xlabel: str, path: Path, top_n: int = 15) -> None:
    """Write a frequency bar chart for repository/language distributions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    top = df.head(top_n).iloc[::-1]
    plt.figure(figsize=(8, 5))
    plt.barh(top[label_col].astype(str), top[count_col])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def _plot_prompt_dimension_density(df: pd.DataFrame, path: Path) -> None:
    """Write a compact overlaid density plot for C/S/V ordinal scores."""
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4.5))
    for dim in PROMPT_DIMS:
        df[dim].dropna().plot(kind="kde", label=dim)
    plt.title("Prompt Dimension Density")
    plt.xlabel("Score")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def _write_markdown_summary(root: Path, summary: pd.DataFrame, skew: pd.DataFrame, outliers: pd.DataFrame, repo: pd.DataFrame, lang: pd.DataFrame) -> None:
    """Write a narrative Appendix B summary for readers and artifact evaluators."""
    pr = summary.loc[summary["Variable"] == "PR_Size"].iloc[0]
    exp = summary.loc[summary["Variable"] == "Exp_Author_Repo"].iloc[0]
    dominant_repo = repo.iloc[0]
    dominant_lang = lang.iloc[0]
    text = f"""# Appendix B Descriptive Analysis Summary

This file summarizes the extended descriptive outputs generated from the canonical
`Dataset_Construction/processed_data/final_analysis_dataset.csv` file. These outputs complement the
compact descriptive tables shown in the paper and provide additional distributional
evidence for the modeling decisions used downstream.

## Pull Request Size

Pull request size is strongly right-skewed. The mean PR size is {pr['Mean']}, while
the median is {pr['Median']}, with a maximum of {pr['Max']}. This substantial
mean--median discrepancy and the presence of upper-tail outliers motivate the use
of log-transformed PR-size controls and robustness checks that remove extreme PR-size
observations.

## Contributor Experience

Contributor experience is also right-skewed. The mean is {exp['Mean']}, the median
is {exp['Median']}, and the maximum is {exp['Max']}. This indicates that a small
number of highly experienced contributors contribute disproportionately large values,
which motivates careful interpretation of experience-related controls.

## Repository and Language Concentration

The most frequent repository is `{dominant_repo['Repository']}` with {int(dominant_repo['Count'])}
observations. The most frequent programming language is `{dominant_lang['Language']}`
with {int(dominant_lang['Count'])} observations. These concentrations motivate the
robustness checks that exclude the dominant repository and dominant language.

## Generated Artifacts

The extended descriptive analysis produces CSV summaries, LaTeX-ready tables, and
figures under `results/descriptive/`, `results/descriptive/appendix_b_tables/`, and
`results/descriptive/appendix_b_figures/`.

## Interpretation

Pull request size and contributor experience exhibit strong right-skew, with
substantial mean--median discrepancies and several extreme outliers. These patterns
support the paper's use of log-transformed controls and robust/sensitivity modeling
procedures.
"""
    (root / "RQ2_Prompt_Effectiveness_Modeling" / "results" / "descriptive" / "appendix_b_summary.md").write_text(text, encoding="utf-8")


def run(root: Path) -> list[pd.DataFrame]:
    """Generate extended Appendix B descriptive outputs and figures."""
    df = load_analysis_dataset(root)
    outdir = root / "RQ2_Prompt_Effectiveness_Modeling" / "results" / "descriptive"
    tables_dir = outdir / "appendix_b_tables"
    figs_dir = outdir / "appendix_b_figures"
    outdir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)

    summary = appendix_b_summary_statistics(df)
    dim_dist = prompt_dimension_distributions(df)
    repo_dist = repository_distribution(df)
    lang_dist = language_distribution_full(df)
    skew = skewness_analysis(df)
    outliers = outlier_summary(df)
    corr = prompt_structure_correlations(df)
    pr_summary = pd.DataFrame([{"Variable": "PR_Size", **_numeric_summary(df["PR_Size"])}])
    exp_summary = pd.DataFrame([{"Variable": "Exp_Author_Repo", **_numeric_summary(df["Exp_Author_Repo"])}])

    outputs = {
        "appendix_b_summary_statistics.csv": summary,
        "prompt_dimension_distributions.csv": dim_dist,
        "repository_distribution.csv": repo_dist,
        "language_distribution.csv": lang_dist,
        "skewness_analysis.csv": skew,
        "outlier_summary.csv": outliers,
        "prompt_structure_correlations.csv": corr,
        "contributor_experience_summary.csv": exp_summary,
        "pr_size_distribution_summary.csv": pr_summary,
    }
    for name, table in outputs.items():
        write_csv(table, outdir / name)
        write_csv(table, tables_dir / name)

    write_latex_table(summary, root / "paper" / "tables" / "appendix_b_summary_statistics.tex", "Appendix B summary statistics", "tab:appendix-b-summary")
    write_latex_table(skew, root / "paper" / "tables" / "appendix_b_skewness_analysis.tex", "Skewness analysis for key variables", "tab:appendix-b-skewness")
    write_latex_table(outliers, root / "paper" / "tables" / "appendix_b_outlier_summary.tex", "Outlier summary for skew-sensitive variables", "tab:appendix-b-outliers")
    write_latex_table(corr, root / "paper" / "tables" / "appendix_b_prompt_structure_correlations.tex", "Prompt-structure correlations", "tab:appendix-b-correlations")

    _plot_histogram(df["PR_Size"], "Pull Request Size Distribution", "PR size", figs_dir / "pr_size_histogram.png", bins=40)
    _plot_histogram(df["Exp_Author_Repo"], "Contributor Experience Distribution", "Author experience in repository", figs_dir / "contributor_experience_histogram.png", bins=40)
    _plot_prompt_dimension_density(df, figs_dir / "prompt_dimension_density.png")
    _plot_histogram(df["PQS"], "Prompt Quality Score Distribution", "PQS", figs_dir / "pqs_density.png", bins=7)
    _plot_bar(repo_dist, "Repository", "Count", "Top Repository Frequencies", "Observation count", figs_dir / "repository_frequency_plot.png", top_n=15)
    _plot_bar(lang_dist, "Language", "Count", "Top Programming Languages", "Observation count", figs_dir / "language_frequency_plot.png", top_n=15)

    _write_markdown_summary(root, summary, skew, outliers, repo_dist, lang_dist)
    return [summary, dim_dist, repo_dist, lang_dist, skew, outliers, corr, exp_summary, pr_summary]


if __name__ == "__main__":
    run(Path("."))
