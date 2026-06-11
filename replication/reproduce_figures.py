from __future__ import annotations
"""Figure reproduction script.

This module regenerates the figures used by the descriptive and modeling sections.
It uses the canonical processed dataset and writes figures under
``RQ2_Prompt_Effectiveness_Modeling/results/figures``.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, ensure_dir


OUTCOME_COLORS = {
    "CL": "#84541E",  # brown
    "NE": "#7F170E",  # dark red
    "PA": "#387B7C",  # teal
    "PN": "#213554",  # navy
}


def reproduce_figures(root_or_results_dir: Path):
    """Regenerate all figures available from the canonical dataset."""
    root = (
        root_or_results_dir
        if (root_or_results_dir / "Dataset_Construction").exists()
        else root_or_results_dir.parent
    )
    df = load_analysis_dataset(root)
    figs = ensure_dir(root / "RQ2_Prompt_Effectiveness_Modeling" / "results" / "figures")

    # Figure 2 in the paper: distribution of PQS by outcome class.
    # The class order matches the paper screenshot and LaTeX section.
    order = ["CL", "NE", "PA", "PN"]
    data = [df.loc[df["Outcome_Class"].eq(cls), "PQS"].dropna() for cls in order]
    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot(data, tick_labels=order, patch_artist=True)
    for patch, cls in zip(bp["boxes"], order):
        patch.set_facecolor(OUTCOME_COLORS[cls])
        patch.set_edgecolor("#111111")
        patch.set_alpha(0.9)
    for median in bp["medians"]:
        median.set_color("#FFFFFF")
        median.set_linewidth(1.8)
    for whisker in bp["whiskers"]:
        whisker.set_color("#111111")
    for cap in bp["caps"]:
        cap.set_color("#111111")
    for flier in bp["fliers"]:
        flier.set_markerfacecolor("#111111")
        flier.set_markeredgecolor("#111111")
        flier.set_alpha(0.35)
    ax.set_xlabel("Outcome Class")
    ax.set_ylabel("PQS")
    ax.set_title("Distribution of Prompt Quality Score (PQS) across outcome classes")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    f = figs / "figure_2_pqs_by_outcome.png"
    fig.savefig(f, dpi=200)
    plt.close(fig)

    # Outcome-class counts, useful for checking the final 273-case dataset composition.
    counts = df["Outcome_Class"].value_counts().reindex(["PA", "PN", "NE", "CL"])
    fig, ax = plt.subplots(figsize=(6, 4))
    counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("Outcome class")
    ax.set_ylabel("Number of cases")
    ax.set_title("Outcome class distribution")
    fig.tight_layout()
    f = figs / "figure_1_outcome_distribution.png"
    fig.savefig(f, dpi=200)
    plt.close(fig)

    # Gate 2 support figure: integration depth among PA cases by Context score.
    pa = df[df.Outcome_Class.eq("PA")].dropna(subset=["Context", "Fraction_Adopted"])
    context_order = sorted(pa["Context"].unique())
    data = [pa.loc[pa["Context"].eq(c), "Fraction_Adopted"] for c in context_order]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot(data, tick_labels=[str(int(c)) if float(c).is_integer() else str(c) for c in context_order], patch_artist=True)
    ax.set_title("Fraction adopted by Context score among PA cases")
    ax.set_xlabel("Context score")
    ax.set_ylabel("Fraction adopted (%)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    f = figs / "figure_3_fraction_adopted_by_context.png"
    fig.savefig(f, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    reproduce_figures(Path("."))
