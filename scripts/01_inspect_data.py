"""Data inspection and quality summary for VPD crime data.

Run from the repository root:
    python scripts/01_inspect_data.py

Outputs a quality summary to data/processed/data_quality_summary.txt
"""
from datetime import date
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data") / "raw" / "crimedata_csv_AllNeighbourhoods_AllYears.csv"
OUT_PATH = Path("data") / "processed" / "data_quality_summary.txt"

CATEGORICAL_COLS = ["TYPE", "NEIGHBOURHOOD"]
TEMPORAL_COLS = ["YEAR", "MONTH", "DAY", "HOUR", "MINUTE"]
SPATIAL_COLS = ["X", "Y"]


def build_summary(df: pd.DataFrame) -> str:
    lines: list[str] = []

    def log(text: str = "") -> None:
        print(text)
        lines.append(text)

    log("=" * 70)
    log("VPD CRIME DATA - DATA QUALITY SUMMARY")
    log(f"Generated: {date.today().isoformat()}")
    log("=" * 70)
    log(f"Rows: {len(df):,}")
    log(f"Columns: {len(df.columns)}")
    log()
    log("Column list:")
    log(", ".join(df.columns))
    log()

    log("Dtypes:")
    log(df.dtypes.to_string())
    log()

    log("Missing values:")
    log(df.isna().sum().to_string())
    log()

    log("Duplicate rows:")
    log(str(df.duplicated().sum()))
    log()

    log("Temporal ranges:")
    for col in TEMPORAL_COLS:
        log(f"  {col}: min={df[col].min()} max={df[col].max()}")
    log()

    log("Distinct values:")
    for col in CATEGORICAL_COLS:
        log(f"  {col}: {df[col].nunique()}")
    log()

    log("Top 10 crime types:")
    log(df["TYPE"].value_counts().head(10).to_string())
    log()

    log("Top 10 neighbourhoods:")
    log(df["NEIGHBOURHOOD"].value_counts().head(10).to_string())
    log()

    log("Spatial coordinate checks (X/Y in UTM Zone 10N):")
    log(f"  X: min={df['X'].min():.0f} max={df['X'].max():.0f}")
    log(f"  Y: min={df['Y'].min():.0f} max={df['Y'].max():.0f}")
    log(f"  Invalid (non-finite) X/Y rows: {int((~df[['X', 'Y']].map(pd.api.types.is_number).all(axis=1)).sum())}")
    log(f"  Zero X/Y rows: {int(((df['X'] == 0) | (df['Y'] == 0)).sum())}")
    log()

    log("Missing year counts per YEAR value:")
    log(df.groupby("YEAR").size().to_string())
    return "\n".join(lines)


def main() -> None:
    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")
    summary = build_summary(df)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(summary + "\n", encoding="utf-8")
    print(f"\nSummary written to {OUT_PATH}")


if __name__ == "__main__":
    main()
