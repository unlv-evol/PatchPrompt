from __future__ import annotations
"""Shared utility functions for the replication package.

This module centralizes dataset loading, derived metadata creation, output writing,
and small formatting helpers used by the modeling, diagnostics, qualitative, and
figure-generation scripts. The canonical CSV is never modified in place: fields such
as Repository, PR_Number, Merged, and Closed are derived at runtime from PR_Link
and Status to preserve the final downstream dataset exactly as used in the study.
"""

import hashlib
import math
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

CANONICAL_COLUMNS = [
    "Case ID", "PR_Link", "Conversation_Link", "Outcome_Class", "Context",
    "Specificity", "Verification", "Rationale", "PQS ", "PR_Size", "Log_PR_Size",
    "Has_Code", "Adopt_Any", "Fraction_Adopted", "Status", "Exp_Author_Repo",
    "Time_To_Event", "PR_Language", "Merged_By_Author", "Closed_By_Author",
    "Closed_By_Author_new",
]

OUTCOME_ORDER = ["PA", "CL", "PN", "NE"]


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_repo(pr_link: str) -> str | None:
    m = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)", str(pr_link))
    return m.group(1) if m else None


def _extract_pr_number(pr_link: str) -> int | None:
    m = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)", str(pr_link))
    return int(m.group(2)) if m else None


def load_canonical_dataset(root: Path) -> pd.DataFrame:
    path = root / "Dataset_Construction" / "processed_data" / "final_analysis_dataset.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing canonical dataset: {path}")
    df = pd.read_csv(path)
    missing = [c for c in CANONICAL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Canonical dataset is missing expected columns: {missing}")
    return df


def derive_analysis_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Return a modeling view without modifying the canonical CSV on disk.

    Repository and PR number are intentionally derived from PR_Link rather than stored
    as duplicated canonical fields. Merged/closed lifecycle status is derived from the
    Status column, as documented in the paper and replication package.
    """
    out = df.copy()
    out["Case_ID"] = out["Case ID"]
    out["PQS"] = out["PQS "]
    out["Repository"] = out["PR_Link"].map(_extract_repo)
    out["PR_Number"] = out["PR_Link"].map(_extract_pr_number)
    status = out["Status"].astype(str).str.lower()
    out["Merged"] = status.str.contains("merged", na=False).astype(int)
    out["Closed"] = status.str.contains("closed", na=False).astype(int)
    out["Generated_Code"] = out["Outcome_Class"].isin(["PA", "PN"]).astype(int)
    out["Adopted_Code"] = out["Outcome_Class"].eq("PA").astype(int)
    out["Resolved"] = out["Status"].notna().astype(int)
    out["Close_Event"] = out["Closed"]
    out["Merge_Event"] = out["Merged"]
    return out


def load_analysis_dataset(root: Path) -> pd.DataFrame:
    return derive_analysis_dataset(load_canonical_dataset(root))


def write_csv(df: pd.DataFrame, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return p


def write_latex_table(df: pd.DataFrame, path: str | Path, caption: str, label: str) -> Path:
    """Compatibility no-op for retired root paper TeX exports.

    The replication package now treats CSV artifacts under RQ result folders as
    canonical outputs and renders reviewer PDFs from those CSVs. The historical
    
    """
    _ = (df, caption, label)
    return Path(path)


def ci_from_result(result, term: str, alpha: float = 0.05, transform=np.exp) -> tuple[float, float]:
    lo, hi = result.conf_int(alpha=alpha).loc[term]
    return float(transform(lo)), float(transform(hi))


def stars(p: float) -> str:
    if pd.isna(p): return ""
    if p < 0.001: return "***"
    if p < 0.01: return "**"
    if p < 0.05: return "*"
    return ""


def format_effect(effect: float, lo: float, hi: float, p: float, digits: int = 2) -> str:
    return f"{effect:.{digits}f}{stars(p)} [{lo:.{digits}f}, {hi:.{digits}f}]"


def safe_logit_fit(formula: str, data: pd.DataFrame):
    import statsmodels.formula.api as smf
    return smf.logit(formula, data=data).fit(disp=False, maxiter=500)
