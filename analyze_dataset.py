"""Command-line helper to score chat messages for toxicity."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import pandas as pd

from toxicity_analysis import Lexicon, analyze_text, load_lexicon, summarize_messages


def pick_text_column(frame: pd.DataFrame) -> str:
    for candidate in ("text", "comment_text", "message", "content"):
        if candidate in frame.columns:
            return candidate
    string_cols = frame.select_dtypes(include=["object"]).columns.tolist()
    if string_cols:
        return string_cols[0]
    return frame.columns[0]


def analyze_dataframe(frame: pd.DataFrame, lexicon: Lexicon) -> List[dict]:
    col = pick_text_column(frame)
    reports = []
    for idx, row in frame.iterrows():
        text = str(row.get(col, "") or "")
        report = analyze_text(text, lexicon)
        report["row_index"] = int(idx)
        report["text"] = text
        reports.append(report)
    return reports


def main() -> None:
    parser = argparse.ArgumentParser(description="Heuristic toxicity analysis for datasets")
    parser.add_argument("--input", required=True, help="CSV file containing messages to score")
    parser.add_argument("--lexicon", help="CSV file used to build the lexicon (defaults to comprehensive dataset)")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum rows to analyze")
    parser.add_argument("--out", help="Optional path to write per-message scores as CSV")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input dataset not found: {input_path}")

    lexicon_source = Path(args.lexicon) if args.lexicon else Path("data/datasets/comprehensive_toxicity_dataset.csv")
    if not lexicon_source.is_absolute():
        lexicon_source = (Path.cwd() / lexicon_source).resolve()

    lexicon = load_lexicon(lexicon_source)
    if not lexicon.keywords:
        print("[warn] Lexicon is empty; results may be low-confidence.")

    try:
        df = pd.read_csv(input_path, nrows=args.limit)
    except Exception as exc:
        raise SystemExit(f"Failed to read dataset: {exc}")

    if df.empty:
        print("No rows to analyze.")
        return

    reports = analyze_dataframe(df, lexicon)
    summary = summarize_messages(reports)

    print(f"Analyzed {len(reports)} rows from {input_path}")
    avg = summary["average_toxicity"] * 100
    risks = summary["risk_counts"]
    print(f"Average toxicity: {avg:.1f}%")
    print("Risk distribution:")
    for level in ("LOW", "MEDIUM", "HIGH"):
        print(f"  {level:>6}: {risks.get(level, 0)}")

    if args.out:
        out_path = Path(args.out)
        records = [
            {
                "row_index": r["row_index"],
                "toxicity_score": r["toxicity_score"],
                "risk_level": r["risk_level"],
                "top_category": r["top_category"],
                "keywords": ",".join(r["matched_keywords"]),
                "text": r["text"],
            }
            for r in reports
        ]
        pd.DataFrame.from_records(records).to_csv(out_path, index=False)
        print(f"Detailed report written to {out_path}")


if __name__ == "__main__":
    main()
