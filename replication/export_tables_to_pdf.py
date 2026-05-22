from __future__ import annotations
"""Export generated CSV tables into rendered PDF review copies.

The PDFs are intended for artifact-evaluation convenience and show table content
as formatted tables, without requiring a TeX toolchain.
"""
from pathlib import Path
from typing import Iterable

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def _stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _column_widths(data: list[list[str]], total_width: float) -> list[float]:
    ncols = len(data[0]) if data else 1
    max_chars = [1] * ncols
    for row in data:
        for i, cell in enumerate(row):
            max_chars[i] = max(max_chars[i], len(cell))
    chars_sum = sum(max_chars)
    if chars_sum <= 0:
        return [total_width / ncols] * ncols
    widths = [total_width * (c / chars_sum) for c in max_chars]
    min_w = 0.7 * inch
    max_w = 3.0 * inch
    widths = [max(min_w, min(max_w, w)) for w in widths]

    # Rebalance to fit within the available page width.
    scale = total_width / sum(widths)
    return [w * scale for w in widths]


def _render_csv_to_pdf(csv_path: Path, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    df = pd.read_csv(csv_path)
    data = [list(df.columns)] + [[_stringify(v) for v in row] for row in df.values.tolist()]

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    available_width = letter[0] - doc.leftMargin - doc.rightMargin
    table = Table(data, colWidths=_column_widths(data, available_width), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story = [
        Paragraph(pdf_path.stem, styles["Title"]),
        Spacer(1, 0.15 * inch),
        table,
    ]
    doc.build(story)


def _csv_sources(root: Path) -> Iterable[Path]:
    for rel in ["results/tables", "results/rq1"]:
        src_dir = root / rel
        if src_dir.exists():
            yield from sorted(src_dir.glob("*.csv"))


def export(root: Path) -> None:
    out = root / "results" / "paper_tables_pdf"
    out.mkdir(parents=True, exist_ok=True)

    # Ensure a fresh PDF set for each run to avoid stale artifacts.
    for stale_pdf in out.glob("*.pdf"):
        stale_pdf.unlink()

    for csv_path in _csv_sources(root):
        pdf = out / f"{csv_path.stem}.pdf"
        _render_csv_to_pdf(csv_path, pdf)


if __name__ == "__main__":
    export(Path(__file__).resolve().parent.parent)
