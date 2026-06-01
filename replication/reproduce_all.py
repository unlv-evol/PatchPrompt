from __future__ import annotations
"""End-to-end replication orchestrator.

This is the canonical entrypoint for evaluators. It runs preprocessing, tables,
figures, manifests, and run-metadata capture in the correct order so that
`make reproduce` regenerates the package outputs from the canonical dataset.
"""
import argparse, csv, subprocess, sys, time
from pathlib import Path
import yaml
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import sha256_file
from collect_run_metadata import write_run_metadata
from reproduce_figures import reproduce_figures
from reproduce_tables import reproduce_tables
from capture_runtime import capture as capture_runtime
from export_tables_to_pdf import export as export_tables_to_pdf
from write_reproduction_report import write_report


def _run_preprocessing(root: Path) -> None:
    subprocess.check_call(
        [
            sys.executable,
            "Dataset_Construction/mining/preprocessing/build_processed_datasets.py",
            "--root",
            str(root),
        ],
        cwd=root,
    )


def _should_run_preprocessing(root: Path, cfg: dict, smoke: bool) -> bool:
    policy = str(cfg.get("fixture_policy", "generate_always"))
    required = [
        root / "Dataset_Construction/processed_data/final_analysis_dataset.csv",
        root / "Dataset_Construction/processed_data/gate_model_dataset.csv",
        root / "Dataset_Construction/processed_data/prompt_scores.csv",
        root / "Dataset_Construction/processed_data/qualitative_dataset.csv",
    ]
    have_all = all(p.exists() for p in required)
    if policy == "generate_when_processed_data_missing":
        return not have_all
    if smoke and have_all:
        return False
    return True


def _write_manifest(root: Path) -> None:
    manifests_dir = root / "RQ2_Prompt_Effectiveness_Modeling" / "results" / "manifests"; manifests_dir.mkdir(parents=True, exist_ok=True)
    def _collect_files(base: Path, suffixes: set[str], recursive: bool = False) -> list[Path]:
        if not base.exists():
            return []
        iterator = base.rglob("*") if recursive else base.glob("*")
        return sorted(
            p for p in iterator
            if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in suffixes
        )

    groups={
        "tables": sorted((root/"RQ2_Prompt_Effectiveness_Modeling/results/tables").glob("*.csv")),
        "figures": sorted((root/"RQ2_Prompt_Effectiveness_Modeling/results/figures").glob("*.png")),
        "diagnostics": sorted(list((root/"RQ2_Prompt_Effectiveness_Modeling/results/diagnostics").glob("*.csv")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/diagnostics").glob("*.md")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/diagnostics").glob("*.png")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/schoenfeld_residual_plots").glob("*.png"))),
        "qualitative": _collect_files(root/"RQ2_Prompt_Effectiveness_Modeling/results/qualitative", {".csv", ".md", ".xlsx", ".pdf", ".txt"}, recursive=True),
        "descriptive": sorted(list((root/"RQ2_Prompt_Effectiveness_Modeling/results/descriptive").glob("*.csv")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/descriptive").glob("*.md")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/descriptive/appendix_b_figures").glob("*.png")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/descriptive/appendix_b_tables").glob("*.csv"))),
        "runtime": sorted(list((root/"RQ2_Prompt_Effectiveness_Modeling/results/runtime").glob("*.json")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/runtime").glob("*.csv")) + list((root/"RQ2_Prompt_Effectiveness_Modeling/results/runtime").glob("*.md")) + [root/"RQ2_Prompt_Effectiveness_Modeling/results/reproduction_report.md"]),
        "paper_tables_pdf": sorted((root/"RQ2_Prompt_Effectiveness_Modeling/results/paper_tables_pdf").glob("*.pdf")),
    }
    for kind, files in groups.items():
        with (manifests_dir/f"{kind}_manifest.csv").open("w", newline="", encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["artifact","path","sha256","bytes"])
            for p in files: w.writerow([p.name, str(p.relative_to(root)), sha256_file(p), p.stat().st_size])


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--config", required=True); parser.add_argument("--smoke", action="store_true")
    args=parser.parse_args(); cfg_path=Path(args.config).resolve()
    with cfg_path.open("r", encoding="utf-8") as f: cfg=yaml.safe_load(f) or {}
    root=(cfg_path.parent.parent if cfg.get("project_root", ".")=="." else Path(cfg["project_root"])).resolve(); seed=int(cfg.get("seed",42))
    for rel in [
        "RQ2_Prompt_Effectiveness_Modeling/results/tables",
        "RQ2_Prompt_Effectiveness_Modeling/results/figures",
        "RQ2_Prompt_Effectiveness_Modeling/results/diagnostics",
        "RQ2_Prompt_Effectiveness_Modeling/results/qualitative",
        "RQ2_Prompt_Effectiveness_Modeling/results/descriptive",
        "RQ2_Prompt_Effectiveness_Modeling/results/manifests",
        "RQ2_Prompt_Effectiveness_Modeling/results/logs",
        "RQ2_Prompt_Effectiveness_Modeling/results/runtime",
        "RQ2_Prompt_Effectiveness_Modeling/results/paper_tables_pdf",
        "RQ1_Prompt_Evaluation_Validation/results/rq1",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    timings=[]
    def timed(label, fn):
        start=time.time(); fn(); timings.append({"step": label, "seconds": round(time.time()-start, 3)})
    if _should_run_preprocessing(root, cfg, args.smoke):
        timed("preprocessing", lambda: _run_preprocessing(root))
    timed("tables", lambda: reproduce_tables(root))
    timed("figures", lambda: reproduce_figures(root))
    if not args.smoke:
        timed(
            "methodological_alignment",
            lambda: subprocess.check_call(
                [
                    sys.executable,
                    "RQ2_Prompt_Effectiveness_Modeling/analysis/diagnostics/methodological_alignment_outputs.py",
                    "--root",
                    str(root),
                ],
                cwd=root,
            ),
        )
    timed("runtime_capture", lambda: capture_runtime(root))
    timed("table_pdf_exports", lambda: export_tables_to_pdf(root))
    import pandas as pd
    pd.DataFrame(timings).to_csv(root/"RQ2_Prompt_Effectiveness_Modeling/results/runtime/runtime_benchmarks.csv", index=False)
    (root/"RQ2_Prompt_Effectiveness_Modeling/results/runtime/reproduction_timing_summary.md").write_text("# Reproduction Timing Summary\n\n" + "\n".join([f"- {r['step']}: {r['seconds']} seconds" for r in timings]) + "\n", encoding="utf-8")
    write_run_metadata(root/"RQ2_Prompt_Effectiveness_Modeling/results/logs/last_run_metadata.json", smoke=args.smoke, seed=seed)
    write_report(root, verification_status="generated; run `make verify` for validation")
    timed("manifests", lambda: _write_manifest(root))
    (root/"RQ2_Prompt_Effectiveness_Modeling/results/logs/reproduction.log").write_text("Replication run completed successfully.\n", encoding="utf-8")
if __name__=="__main__": main()
