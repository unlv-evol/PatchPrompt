from __future__ import annotations
"""Table reproduction orchestrator.

This module calls the descriptive, quantitative, diagnostic, and qualitative scripts
that generate CSV and LaTeX tables. It is used by the full reproduction pipeline and
can also be invoked independently.
"""
from pathlib import Path
import pandas as pd
from analysis.common import load_analysis_dataset, write_csv, write_latex_table
from analysis.descriptive import descriptive_statistics, appendix_b_descriptives
from analysis.quantitative import gate0_generation, gate1_adoption, gate2_integration, axisB_lifecycle, effect_sizes
from analysis.diagnostics import vif_analysis, separation_checks, schoenfeld_tests, sensitivity_analysis, robustness_sensitivity_outputs, diagnostic_plots_summary
from analysis.qualitative import code_frequency_analysis, thematic_analysis, triangulation_analysis, illustrative_examples
from analysis.qualitative import gate0_qualitative_patterns, gate1_qualitative_patterns, gate2_qualitative_patterns
from analysis.rq1 import agreement_analysis

def reproduce_tables(root_or_results_dir: Path) -> None:
    root = root_or_results_dir if (root_or_results_dir / "dataset").exists() else root_or_results_dir.parent
    df = load_analysis_dataset(root)
    summary = pd.DataFrame([
        {"Metric": "Cases", "Value": len(df)},
        {"Metric": "Repositories (derived from PR_Link)", "Value": df["Repository"].nunique()},
        {"Metric": "PA", "Value": int((df.Outcome_Class=="PA").sum())},
        {"Metric": "PN", "Value": int((df.Outcome_Class=="PN").sum())},
        {"Metric": "NE", "Value": int((df.Outcome_Class=="NE").sum())},
        {"Metric": "CL", "Value": int((df.Outcome_Class=="CL").sum())},
        {"Metric": "Mean PQS", "Value": round(df["PQS"].mean(), 2)},
        {"Metric": "Median PQS", "Value": round(df["PQS"].median(), 2)},
    ])
    write_csv(summary, root/"results/tables/table_1_summary.csv")
    write_latex_table(summary, root/"paper/tables/table_1_summary.tex", "Replication dataset summary", "tab:replication-summary")
    # Reproduce Section 4.1 human--LLM annotation reliability results before downstream modeling.
    agreement_analysis.run(root)
    # Reproduce Section 4.2.1 and Appendix B descriptive statistics before the models.
    descriptive_statistics.run(root)
    appendix_b_descriptives.run(root)
    parts=[gate0_generation.run(root), gate1_adoption.run(root), gate2_integration.run(root), axisB_lifecycle.run(root)]
    combined=pd.concat(parts, ignore_index=True, sort=False)
    write_csv(combined, root/"results/tables/table_2_models.csv")
    effect_sizes.run(root); vif_analysis.run(root); separation_checks.run(root); schoenfeld_tests.run(root); sensitivity_analysis.run(root); robustness_sensitivity_outputs.run(root); diagnostic_plots_summary.run(root)
    code_frequency_analysis.run(root); thematic_analysis.run(root); triangulation_analysis.run(root); illustrative_examples.run(root)
    gate0_qualitative_patterns.main(); gate1_qualitative_patterns.main(); gate2_qualitative_patterns.main()
if __name__=="__main__": reproduce_tables(Path("."))
