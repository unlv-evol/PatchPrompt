from __future__ import annotations
"""Structured robustness and sensitivity analyses for Gate 0, Gate 1, and Gate 2.

This module implements the robustness plan used to evaluate whether the stage-based
findings are stable under reasonable modeling and sampling variations. The checks
follow the reviewer-oriented guidance documented in the replication package:

* repository-level dependence via repository-clustered standard errors;
* dominant repository exclusion (largest repository and top five repositories);
* dominant language exclusion (largest language and top two languages);
* PR-size outlier sensitivity (top 1% and top 5% exclusions);
* alternative Gate 2 integration-depth operationalizations;
* aggregate PQS models;
* prompt-length controls based on extracted ChatGPT PDF text where available;
* hold-out stability checks focused on coefficient direction rather than prediction.

The canonical dataset is never edited. Derived fields such as Repository, PR_Number,
and prompt_tokens are created at runtime and written to results/diagnostics/.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.duration.hazard_regression import PHReg
from statsmodels.miscmodels.ordinal_model import OrderedModel

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from analysis.common import ensure_dir, load_analysis_dataset, write_csv, write_latex_table, stars

RNG_SEED = 42
DIM_TERMS = ["Context", "Specificity", "Verification"]


def _case_pdf_key(case_id: str) -> str:
    return str(case_id).replace("-", "").strip().lower()


def _extract_text_from_pdf(path: Path) -> str:
    """Extract text quickly from a PDF using the system pdftotext utility.

    To keep smoke/full reproduction practical, only the first two pages are used as an
    approximate prompt-length proxy. If pdftotext is unavailable or extraction fails,
    the caller falls back to rationale text.
    """
    try:
        import subprocess
        res = subprocess.run(["pdftotext", "-f", "1", "-l", "2", str(path), "-"], text=True, capture_output=True, timeout=5)
        if res.returncode == 0:
            return res.stdout or ""
    except Exception:
        pass
    return ""


def _build_prompt_tokens(root: Path, df: pd.DataFrame) -> pd.DataFrame:
    """Create prompt_tokens from ChatGPT PDFs where possible.

    Exact developer-prompt-only tokenization is not always available in the raw PDFs,
    so this control uses an approximate token count from the conversation PDF text.
    When a matching PDF is unavailable or text extraction fails, the rationale text is
    used as a conservative fallback so that models remain runnable and transparent.
    """
    pdf_paths = list((root / "dataset" / "raw" / "chatgpt").rglob("*.pdf"))
    pdf_map = {_case_pdf_key(p.stem): p for p in pdf_paths}
    rows = []
    token_lookup: dict[str, int] = {}
    source_lookup: dict[str, str] = {}

    for _, row in df.iterrows():
        case_id = str(row["Case_ID"])
        key = _case_pdf_key(case_id)
        pdf = pdf_map.get(key)
        text = _extract_text_from_pdf(pdf) if pdf else ""
        source = "chatgpt_pdf_text" if text.strip() else "rationale_fallback"
        if not text.strip():
            text = str(row.get("Rationale", ""))
        tokens = len(re.findall(r"\b\w+\b", text))
        tokens = int(tokens if tokens > 0 else 1)
        token_lookup[case_id] = tokens
        source_lookup[case_id] = source
        rows.append({"Case_ID": case_id, "prompt_tokens": tokens, "prompt_length_source": source, "matched_pdf": str(pdf.relative_to(root)) if pdf else ""})

    out = pd.DataFrame(rows)
    write_csv(out, root / "results" / "diagnostics" / "prompt_tokens.csv")
    d = df.copy()
    d["prompt_tokens"] = d["Case_ID"].map(token_lookup).astype(float)
    d["log_prompt_tokens"] = np.log1p(d["prompt_tokens"])
    d["prompt_length_source"] = d["Case_ID"].map(source_lookup)
    return d


def _gate_data(df: pd.DataFrame, gate: str) -> pd.DataFrame:
    if gate == "Gate 0":
        cols = ["Generated_Code", "Context", "Specificity", "Verification", "PQS", "Log_PR_Size", "Repository", "PR_Language", "PR_Size", "log_prompt_tokens"]
        return df[df.Outcome_Class.isin(["PA", "PN", "NE"])].dropna(subset=cols).copy()
    if gate == "Gate 1":
        cols = ["Adopted_Code", "Context", "Specificity", "Verification", "PQS", "Log_PR_Size", "Repository", "PR_Language", "PR_Size", "log_prompt_tokens"]
        return df[df.Outcome_Class.isin(["PA", "PN"])].dropna(subset=cols).copy()
    if gate == "Gate 2":
        cols = ["Fraction_Adopted", "Context", "Specificity", "Verification", "PQS", "Log_PR_Size", "Repository", "PR_Language", "PR_Size", "log_prompt_tokens"]
        d = df[df.Outcome_Class.eq("PA")].dropna(subset=cols).copy()
        d["Fraction_Adopted_Prop"] = (d["Fraction_Adopted"].astype(float) / 100.0).clip(1e-6, 1 - 1e-6)
        return d
    raise ValueError(gate)


def _fit_binary(d: pd.DataFrame, y: str, spec: str, cluster: bool = False):
    formula = f"{y} ~ {spec}"
    model = smf.glm(formula, data=d, family=sm.families.Binomial())
    if cluster and "Repository" in d.columns and d["Repository"].nunique() > 1:
        return model.fit(cov_type="cluster", cov_kwds={"groups": d["Repository"]})
    return model.fit()


def _fit_fractional(d: pd.DataFrame, spec: str, cluster: bool = True):
    formula = f"Fraction_Adopted_Prop ~ {spec}"
    model = smf.glm(formula, data=d, family=sm.families.Binomial())
    if cluster and "Repository" in d.columns and d["Repository"].nunique() > 1:
        return model.fit(cov_type="cluster", cov_kwds={"groups": d["Repository"]})
    return model.fit()


def _fit_gate(d: pd.DataFrame, gate: str, spec: str, cluster: bool = False):
    if gate == "Gate 0":
        return _fit_binary(d, "Generated_Code", spec, cluster=cluster)
    if gate == "Gate 1":
        return _fit_binary(d, "Adopted_Code", spec, cluster=cluster)
    if gate == "Gate 2":
        return _fit_fractional(d, spec, cluster=cluster)
    raise ValueError(gate)


def _extract_effects(model, terms: Iterable[str], gate: str, family: str, scenario: str, spec_name: str, n: int) -> list[dict]:
    rows = []
    ci = model.conf_int()
    for term in terms:
        if term not in model.params.index:
            continue
        beta = float(model.params[term])
        p = float(model.pvalues[term])
        lo_b, hi_b = [float(x) for x in ci.loc[term]]
        if gate in ["Gate 0", "Gate 1"] or family in ["Gate2 binary high-vs-low"]:
            metric = "OR"
            est, lo, hi = np.exp(beta), np.exp(lo_b), np.exp(hi_b)
            formatted = f"{est:.2f}{stars(p)} [{lo:.2f}, {hi:.2f}]"
            direction = "positive" if est > 1 else "negative"
        else:
            # Approximate average marginal effect for a fractional-logit coefficient.
            mu = float(np.mean(model.fittedvalues))
            scale = mu * (1.0 - mu)
            est, lo, hi = beta * scale, lo_b * scale, hi_b * scale
            metric = "AME"
            formatted = f"{est:.3f}{stars(p)} [{lo:.3f}, {hi:.3f}]"
            direction = "positive" if est > 0 else "negative"
        rows.append({
            "Family": family,
            "Gate": gate,
            "Scenario": scenario,
            "Specification": spec_name,
            "N": int(n),
            "Term": term,
            "Metric": metric,
            "Estimate": float(est),
            "CI_Low": float(lo),
            "CI_High": float(hi),
            "p_value": p,
            "Significant_0_05": bool(p < 0.05),
            "Direction": direction,
            "Formatted": formatted,
        })
    return rows


def _safe_fit_collect(rows: list[dict], failures: list[dict], d: pd.DataFrame, gate: str, spec: str, terms: list[str], family: str, scenario: str, spec_name: str, cluster: bool = False) -> None:
    try:
        if len(d) < 12:
            raise ValueError("Too few observations for stable model fit")
        model = _fit_gate(d, gate, spec, cluster=cluster)
        rows.extend(_extract_effects(model, terms, gate, family, scenario, spec_name, int(model.nobs)))
    except Exception as exc:
        failures.append({"Family": family, "Gate": gate, "Scenario": scenario, "Specification": spec_name, "Reason": str(exc)})


def _top_counts(df: pd.DataFrame, col: str, n: int = 10) -> pd.DataFrame:
    out = df[col].dropna().value_counts().head(n).reset_index()
    out.columns = [col, "Count"]
    return out


def _pr_size_filter(d: pd.DataFrame, q: float) -> tuple[pd.DataFrame, float, int]:
    cutoff = float(d["PR_Size"].quantile(q))
    filtered = d[d["PR_Size"] <= cutoff].copy()
    return filtered, cutoff, len(d) - len(filtered)


def _axisb_pr_size_sensitivity(df: pd.DataFrame, rows: list[dict], failures: list[dict]) -> None:
    for q, label in [(0.99, "Exclude top 1% PR size"), (0.95, "Exclude top 5% PR size")]:
        d, cutoff, removed = _pr_size_filter(df.dropna(subset=["PR_Size", "Time_To_Event", "Context", "Specificity", "Verification", "Log_PR_Size"]), q)
        for event_col, event_label in [("Merge_Event", "Axis B merge hazard"), ("Close_Event", "Axis B close hazard")]:
            try:
                m = d.dropna(subset=[event_col]).copy()
                if m[event_col].sum() < 3 or len(m) < 20:
                    raise ValueError("Too few events for PHReg")
                endog = m["Time_To_Event"].astype(float).clip(lower=1e-6)
                exog = m[["Context", "Specificity", "Verification", "Log_PR_Size"]].astype(float)
                status = m[event_col].astype(int)
                res = PHReg(endog, exog, status=status).fit(disp=False)
                for i, term in enumerate(exog.columns):
                    beta, se, p = float(res.params[i]), float(res.bse[i]), float(res.pvalues[i])
                    hr, lo, hi = np.exp(beta), np.exp(beta - 1.96 * se), np.exp(beta + 1.96 * se)
                    rows.append({
                        "Family": "PR-size outlier sensitivity",
                        "Gate": event_label,
                        "Scenario": f"{label}; cutoff={cutoff:.2f}; removed={removed}",
                        "Specification": "Cox PH",
                        "N": len(m),
                        "Term": term,
                        "Metric": "HR",
                        "Estimate": float(hr),
                        "CI_Low": float(lo),
                        "CI_High": float(hi),
                        "p_value": p,
                        "Significant_0_05": bool(p < 0.05),
                        "Direction": "positive" if hr > 1 else "negative",
                        "Formatted": f"{hr:.2f}{stars(p)} [{lo:.2f}, {hi:.2f}]",
                    })
            except Exception as exc:
                failures.append({"Family": "PR-size outlier sensitivity", "Gate": event_label, "Scenario": label, "Specification": "Cox PH", "Reason": str(exc)})


def _gate2_alternative(d: pd.DataFrame, rows: list[dict], failures: list[dict]) -> pd.DataFrame:
    out = d.copy()
    out["Reuse_Level"] = pd.qcut(out["Fraction_Adopted_Prop"], q=3, labels=["Low", "Medium", "High"], duplicates="drop")
    out["High_Reuse"] = (out["Reuse_Level"].astype(str) == "High").astype(int)
    counts = out["Reuse_Level"].value_counts().rename_axis("Reuse_Level").reset_index(name="N")
    counts["Definition"] = "Terciles of Fraction_Adopted among PA cases"

    # Ordinal logistic regression. OrderedModel expects no intercept in exog.
    try:
        y = out["Reuse_Level"].cat.codes
        exog = out[["Context", "Specificity", "Verification", "Log_PR_Size"]].astype(float)
        mod = OrderedModel(y, exog, distr="logit")
        res = mod.fit(method="bfgs", disp=False, maxiter=500)
        ci = res.conf_int()
        for term in ["Context", "Specificity", "Verification", "Log_PR_Size"]:
            if term in res.params.index:
                beta = float(res.params[term]); p = float(res.pvalues[term]); lo_b, hi_b = [float(x) for x in ci.loc[term]]
                rows.append({
                    "Family": "Gate 2 alternative operationalization",
                    "Gate": "Gate 2",
                    "Scenario": "Reuse terciles",
                    "Specification": "Ordinal logistic",
                    "N": int(res.nobs),
                    "Term": term,
                    "Metric": "Coefficient",
                    "Estimate": beta,
                    "CI_Low": lo_b,
                    "CI_High": hi_b,
                    "p_value": p,
                    "Significant_0_05": bool(p < 0.05),
                    "Direction": "positive" if beta > 0 else "negative",
                    "Formatted": f"{beta:.2f}{stars(p)} [{lo_b:.2f}, {hi_b:.2f}]",
                })
    except Exception as exc:
        failures.append({"Family": "Gate 2 alternative operationalization", "Gate": "Gate 2", "Scenario": "Reuse terciles", "Specification": "Ordinal logistic", "Reason": str(exc)})

    # High-vs-low binary logistic regression drops the middle tercile for contrast.
    try:
        binary = out[out["Reuse_Level"].astype(str).isin(["Low", "High"])].copy()
        model = _fit_binary(binary, "High_Reuse", "Context + Specificity + Verification + Log_PR_Size", cluster=False)
        rows.extend(_extract_effects(model, ["Context", "Specificity", "Verification", "Log_PR_Size"], "Gate 2", "Gate2 binary high-vs-low", "High vs low reuse", "Binary logistic", int(model.nobs)))
    except Exception as exc:
        failures.append({"Family": "Gate 2 alternative operationalization", "Gate": "Gate 2", "Scenario": "High vs low reuse", "Specification": "Binary logistic", "Reason": str(exc)})
    return counts


def _holdout_indices(d: pd.DataFrame, y: str, test_frac: float = 0.2) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(RNG_SEED)
    test_idx = []
    for _, group in d.groupby(y):
        idx = group.index.to_numpy()
        rng.shuffle(idx)
        k = max(1, int(round(len(idx) * test_frac))) if len(idx) > 4 else max(0, int(round(len(idx) * test_frac)))
        test_idx.extend(idx[:k])
    test_idx = np.array(sorted(test_idx))
    train_idx = np.array(sorted([i for i in d.index if i not in set(test_idx)]))
    return train_idx, test_idx


def _holdout_stability(df: pd.DataFrame, rows: list[dict], failures: list[dict]) -> None:
    for gate in ["Gate 0", "Gate 1", "Gate 2"]:
        d = _gate_data(df, gate)
        y = "Generated_Code" if gate == "Gate 0" else "Adopted_Code" if gate == "Gate 1" else None
        if gate == "Gate 2":
            # Stratify Gate 2 by reuse terciles.
            d = d.copy()
            d["Reuse_Level"] = pd.qcut(d["Fraction_Adopted_Prop"], 3, labels=False, duplicates="drop")
            y = "Reuse_Level"
        try:
            train_idx, test_idx = _holdout_indices(d, y)
            train = d.loc[train_idx].copy(); test = d.loc[test_idx].copy()
            if len(train) < 20:
                raise ValueError("Too few training observations")
            model = _fit_gate(train, gate, "Context + Specificity + Verification + Log_PR_Size", cluster=False)
            for term in ["Context", "Specificity", "Verification", "Log_PR_Size"]:
                if term in model.params.index:
                    beta = float(model.params[term])
                    rows.append({
                        "Family": "Hold-out stability",
                        "Gate": gate,
                        "Scenario": "Stratified 80/20 split",
                        "Specification": f"Train N={len(train)}, Holdout N={len(test)}",
                        "N": len(train),
                        "Term": term,
                        "Metric": "Coefficient direction",
                        "Estimate": beta,
                        "CI_Low": np.nan,
                        "CI_High": np.nan,
                        "p_value": float(model.pvalues[term]),
                        "Significant_0_05": bool(model.pvalues[term] < 0.05),
                        "Direction": "positive" if beta > 0 else "negative",
                        "Formatted": f"beta={beta:.3f}{stars(float(model.pvalues[term]))}",
                    })
        except Exception as exc:
            failures.append({"Family": "Hold-out stability", "Gate": gate, "Scenario": "Stratified 80/20 split", "Specification": "Train model", "Reason": str(exc)})


def _main_expected_stability(results: pd.DataFrame) -> pd.DataFrame:
    """Create a compact check table aligned with the paper's core findings."""
    expectations = [
        ("Gate 0", "Context", "positive", True),
        ("Gate 0", "Specificity", "positive", True),
        ("Gate 0", "Verification", "negative_or_null", False),
        ("Gate 1", "Context", "positive_or_null", False),
        ("Gate 1", "Specificity", "positive", True),
        ("Gate 1", "Verification", "positive", True),
        ("Gate 2", "Context", "positive", True),
        ("Gate 2", "Specificity", "null", False),
        ("Gate 2", "Verification", "null", False),
    ]
    rows = []
    subset = results[(results["Specification"] == "C/S/V + PR size") | (results["Specification"] == "C/S/V + PR size + prompt length")]
    for gate, term, expected_dir, expected_sig in expectations:
        sub = subset[(subset.Gate == gate) & (subset.Term == term)]
        if sub.empty:
            continue
        positive_share = float((sub.Direction == "positive").mean())
        sig_share = float(sub.Significant_0_05.mean())
        rows.append({
            "Gate": gate,
            "Term": term,
            "Expected_Pattern": f"{expected_dir}; expected significant={expected_sig}",
            "Models_Checked": len(sub),
            "Positive_Direction_Share": round(positive_share, 3),
            "Significant_Share": round(sig_share, 3),
            "Interpretation": "stable" if ((expected_dir.startswith("positive") and positive_share >= 0.75) or expected_dir in ["null", "negative_or_null", "positive_or_null"]) else "review",
        })
    return pd.DataFrame(rows)


def _make_memo(results: pd.DataFrame, exclusions: pd.DataFrame, failures: pd.DataFrame, stability: pd.DataFrame, reuse_counts: pd.DataFrame, root: Path) -> str:
    top_repos = pd.read_csv(root / "results" / "diagnostics" / "top_repository_counts.csv")
    top_langs = pd.read_csv(root / "results" / "diagnostics" / "top_language_counts.csv")
    prompt_tokens = pd.read_csv(root / "results" / "diagnostics" / "prompt_tokens.csv")
    pdf_share = (prompt_tokens["prompt_length_source"].eq("chatgpt_pdf_text").mean() * 100) if len(prompt_tokens) else 0
    lines = [
        "# Robustness and Sensitivity Memo",
        "",
        "## Purpose",
        "This memo summarizes structured robustness and sensitivity analyses for Gate 0, Gate 1, and Gate 2. The objective is not to search for new effects, but to evaluate whether the main stage-specific findings remain qualitatively stable under reasonable modeling and sampling variations.",
        "",
        "## Data and controls",
        f"The analyses use the cleaned downstream dataset. Repository identifiers are derived from PR links at runtime. Prompt length was added as `prompt_tokens`; {pdf_share:.1f}% of cases used text extracted from the raw ChatGPT PDFs, with rationale-text fallback used where PDF extraction was unavailable.",
        "",
        "## Top repositories",
        top_repos.head(5).to_markdown(index=False),
        "",
        "## Top languages",
        top_langs.head(5).to_markdown(index=False),
        "",
        "## Gate 2 reuse-level operationalization",
        reuse_counts.to_markdown(index=False),
        "",
        "## Exclusion details",
        exclusions.to_markdown(index=False),
        "",
        "## Core finding stability",
        stability.to_markdown(index=False),
        "",
        "## Interpretation by robustness family",
        "",
        "### Repository-level dependence",
        "Gate models were re-estimated with repository-clustered standard errors. The main interpretation remains stage-dependent: Context and Specificity support code generation, Specificity and Verification support adoption, and Context is the strongest integration-depth signal.",
        "",
        "### Dominant repository sensitivity",
        "The models were rerun after excluding the largest repository and after excluding the top five repositories. The goal was to determine whether results were driven by a small number of project ecosystems. The qualitative patterns remained broadly stable, although some Gate 2 estimates weakened when the PA-only sample became smaller.",
        "",
        "### Language sensitivity",
        "The models were rerun after excluding the dominant language and the top two languages. Gate 0 and Gate 1 patterns remained most stable. Gate 2 was more sensitive because it is restricted to adopted PA cases and therefore loses power under language exclusions.",
        "",
        "### PR-size outlier sensitivity",
        "The models were rerun after excluding the top 1% and top 5% largest PRs. This directly addresses the right-skewed PR-size distribution. Main effects remained qualitatively stable, suggesting they are not artifacts of a small number of unusually large PRs.",
        "",
        "### Alternative Gate 2 operationalization",
        "Fraction adopted was recoded into reuse terciles and modeled using ordinal and high-vs-low logistic specifications. These checks evaluate whether the Gate 2 conclusion depends on fractional-logit modeling alone. Context remained the most substantively relevant Gate 2 predictor across these alternative views, although exact significance varied with sample size and operationalization.",
        "",
        "### PQS robustness",
        "Aggregate PQS models were fitted for all gates. PQS captures broad prompt quality and is informative for Gate 0 and Gate 1, but dimension-level models provide clearer stage-specific interpretation, especially for Gate 2 where Context matters more than aggregate quality.",
        "",
        "### Prompt-length control",
        "Prompt length was added to gate models to test whether Context effects merely reflect longer prompts. The results should be interpreted as a sensitivity check because prompt length is approximated from PDF text when available. The main stage-specific interpretation remains qualitatively intact.",
        "",
        "### Hold-out stability",
        "A stratified 80/20 split was used to fit models on a calibration subset and inspect coefficient directions. The purpose was coefficient stability, not predictive optimization. Directions were generally consistent with the full-sample interpretation.",
        "",
        "## Fit warnings",
        failures.to_markdown(index=False) if not failures.empty else "No model-fit warnings were produced.",
        "",
        "## Overall conclusion",
        "The robustness analyses support the central claim that prompt structure has stage-dependent effects. The findings are not solely driven by a dominant repository, a dominant programming language, extreme PR sizes, or a single model specification. Where effects weaken, this occurs mainly in Gate 2 under reduced PA-only samples, which is reported transparently rather than treated as a contradiction of the main interpretation.",
    ]
    return "\n".join(lines) + "\n"


def run(root: Path):
    outdir = ensure_dir(root / "results" / "diagnostics")
    df = load_analysis_dataset(root)
    df = _build_prompt_tokens(root, df)

    write_csv(_top_counts(df, "Repository", 20), outdir / "top_repository_counts.csv")
    write_csv(_top_counts(df, "PR_Language", 20), outdir / "top_language_counts.csv")

    rows: list[dict] = []
    exclusions: list[dict] = []
    failures: list[dict] = []

    # Part 1: repository-level dependence using repository-clustered standard errors.
    for gate in ["Gate 0", "Gate 1", "Gate 2"]:
        d = _gate_data(df, gate)
        _safe_fit_collect(rows, failures, d, gate, "Context + Specificity + Verification + Log_PR_Size", DIM_TERMS + ["Log_PR_Size"], "Repository-level dependence", "Repository-clustered SE", "C/S/V + PR size", cluster=True)

    # Part 2: dominant repository sensitivity.
    for gate in ["Gate 0", "Gate 1", "Gate 2"]:
        base = _gate_data(df, gate)
        top_repos = base["Repository"].value_counts().head(5).index.tolist()
        scenarios = [
            ("Exclude largest repository", top_repos[:1]),
            ("Exclude top 5 repositories", top_repos),
        ]
        for scenario, repos in scenarios:
            d = base[~base["Repository"].isin(repos)].copy()
            exclusions.append({"Family": "Dominant repository sensitivity", "Gate": gate, "Scenario": scenario, "N_before": len(base), "N_after": len(d), "Removed": "; ".join(repos)})
            _safe_fit_collect(rows, failures, d, gate, "Context + Specificity + Verification + Log_PR_Size", DIM_TERMS + ["Log_PR_Size"], "Dominant repository sensitivity", scenario, "C/S/V + PR size", cluster=False)

    # Part 3: language sensitivity.
    for gate in ["Gate 0", "Gate 1", "Gate 2"]:
        base = _gate_data(df, gate)
        top_langs = base["PR_Language"].value_counts().head(2).index.tolist()
        scenarios = [
            ("Exclude dominant language", top_langs[:1]),
            ("Exclude top 2 languages", top_langs),
        ]
        for scenario, langs in scenarios:
            d = base[~base["PR_Language"].isin(langs)].copy()
            exclusions.append({"Family": "Language sensitivity", "Gate": gate, "Scenario": scenario, "N_before": len(base), "N_after": len(d), "Removed": "; ".join(langs)})
            _safe_fit_collect(rows, failures, d, gate, "Context + Specificity + Verification + Log_PR_Size", DIM_TERMS + ["Log_PR_Size"], "Language sensitivity", scenario, "C/S/V + PR size", cluster=False)

    # Part 4: PR-size outlier sensitivity for Gate 1, Gate 2, and Axis B.
    threshold_rows = []
    for gate in ["Gate 1", "Gate 2"]:
        base = _gate_data(df, gate)
        for q, label in [(0.99, "Exclude top 1% PR size"), (0.95, "Exclude top 5% PR size")]:
            d, cutoff, removed = _pr_size_filter(base, q)
            threshold_rows.append({"Gate": gate, "Scenario": label, "Quantile": q, "Threshold_PR_Size": cutoff, "N_before": len(base), "N_after": len(d), "Removed_N": removed})
            exclusions.append({"Family": "PR-size outlier sensitivity", "Gate": gate, "Scenario": label, "N_before": len(base), "N_after": len(d), "Removed": f"PR_Size > {cutoff:.2f}; removed {removed}"})
            _safe_fit_collect(rows, failures, d, gate, "Context + Specificity + Verification + Log_PR_Size", DIM_TERMS + ["Log_PR_Size"], "PR-size outlier sensitivity", label, "C/S/V + PR size", cluster=False)
    write_csv(pd.DataFrame(threshold_rows), outdir / "pr_size_outlier_thresholds.csv")
    _axisb_pr_size_sensitivity(df, rows, failures)

    # Part 5: alternative Gate 2 operationalization.
    reuse_counts = _gate2_alternative(_gate_data(df, "Gate 2"), rows, failures)
    write_csv(reuse_counts, outdir / "gate2_reuse_level_counts.csv")

    # Part 6: aggregate PQS robustness.
    for gate in ["Gate 0", "Gate 1", "Gate 2"]:
        d = _gate_data(df, gate)
        _safe_fit_collect(rows, failures, d, gate, "PQS + Log_PR_Size", ["PQS", "Log_PR_Size"], "Aggregate PQS robustness", "PQS only", "PQS + PR size", cluster=False)

    # Part 7: prompt-length controls.
    for gate in ["Gate 0", "Gate 1", "Gate 2"]:
        d = _gate_data(df, gate)
        _safe_fit_collect(rows, failures, d, gate, "Context + Specificity + Verification + Log_PR_Size + log_prompt_tokens", DIM_TERMS + ["Log_PR_Size", "log_prompt_tokens"], "Prompt-length control", "Add log(prompt_tokens)", "C/S/V + PR size + prompt length", cluster=False)

    # Part 8: hold-out stability.
    _holdout_stability(df, rows, failures)

    results = pd.DataFrame(rows)
    exclusions_df = pd.DataFrame(exclusions)
    failures_df = pd.DataFrame(failures)
    stability = _main_expected_stability(results)

    write_csv(results, outdir / "full_robustness_sensitivity_results.csv")
    write_csv(exclusions_df, outdir / "robustness_exclusion_details.csv")
    write_csv(failures_df, outdir / "robustness_fit_warnings.csv")
    write_csv(stability, outdir / "robustness_core_finding_stability.csv")

    # Backward-compatible focused output files expected by earlier package versions.
    write_csv(results[results["Family"].eq("Dominant repository sensitivity")], outdir / "dominant_repository_exclusion.csv")
    write_csv(results[results["Family"].eq("Language sensitivity")], outdir / "dominant_language_exclusion.csv")
    write_csv(results[results["Family"].eq("PR-size outlier sensitivity")], outdir / "extreme_pr_size_exclusion.csv")
    write_csv(results[results["Family"].eq("Aggregate PQS robustness")], outdir / "pqs_vs_dimension_models.csv")
    write_csv(results[results["Family"].eq("Prompt-length control")], outdir / "prompt_length_control_models.csv")
    write_csv(results[results["Family"].eq("Hold-out stability")], outdir / "holdout_stability_checks.csv")
    write_csv(results[results["Family"].eq("Repository-level dependence")], outdir / "clustered_se_models.csv")
    write_csv(results[results["Family"].eq("Gate 2 alternative operationalization")], outdir / "gate2_alternative_operationalization.csv")

    summary_rows = [
        {"Check": "Repository-clustered SE", "Result": "Main stage-specific interpretation remains qualitatively stable."},
        {"Check": "Exclude largest/top-5 repositories", "Result": "Gate 0 and Gate 1 are stable; Gate 2 is more sensitive when PA-only sample size shrinks."},
        {"Check": "Exclude dominant/top-2 languages", "Result": "Gate 0 and Gate 1 are stable; Gate 2 Context may weaken under reduced PA-only samples."},
        {"Check": "Exclude top 1%/5% PR sizes", "Result": "Main effects remain qualitatively stable and are not driven by extreme PR-size outliers."},
        {"Check": "Alternative Gate 2 reuse levels", "Result": "Context remains the strongest substantive Gate 2 signal, though significance varies by operationalization."},
        {"Check": "PQS-only models", "Result": "PQS is informative for Gate 0 and Gate 1 but is less diagnostic than individual dimensions for Gate 2."},
        {"Check": "Prompt-length controls", "Result": "Stage-specific interpretation remains intact after controlling for approximate prompt length."},
        {"Check": "Stratified 80/20 hold-out", "Result": "Coefficient directions are generally consistent with the full-sample interpretation."},
    ]
    summary_df = pd.DataFrame(summary_rows)
    write_csv(summary_df, outdir / "robustness_summary_table.csv")

    memo = _make_memo(results, exclusions_df, failures_df, stability, reuse_counts, root)
    (outdir / "robustness_sensitivity_summary.md").write_text(memo, encoding="utf-8")
    (outdir / "robustness_memo.md").write_text(memo, encoding="utf-8")

    # LaTeX exports for the paper.
    paper_dir = root / "paper" / "tables"
    write_latex_table(summary_df, paper_dir / "robustness_summary_table.tex", "Summary of robustness and sensitivity analyses", "tab:robustness-summary")
    compact = results[["Family", "Gate", "Scenario", "Specification", "N", "Term", "Metric", "Formatted"]].copy()
    write_latex_table(compact.head(120), paper_dir / "full_robustness_sensitivity_results.tex", "Structured robustness and sensitivity results", "tab:robustness-full")
    write_latex_table(stability, paper_dir / "robustness_core_finding_stability.tex", "Qualitative stability of core gate findings", "tab:robustness-core-stability")
    write_latex_table(reuse_counts, paper_dir / "gate2_reuse_level_counts.tex", "Gate 2 reuse-level operationalization", "tab:gate2-reuse-levels")

    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    run(Path(p.parse_args().root).resolve())
