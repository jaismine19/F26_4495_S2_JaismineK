"""Clean the VPD crime dataset.

Run from the repository root:
    python Implementation/scripts/02_clean_data.py

Steps (each logged with before/after row counts):
  1. Load raw CSV
  2. Standardize categorical values (strip whitespace, fix casing)
  3. Remove exact duplicate rows
  4. Flag zero X/Y coordinates as missing (kept in dataset with NaN)
  5. Create datetime and derived temporal features (day-of-week, season)
  6. Save cleaned data to data/processed/crime_data_cleaned.csv
  7. Write cleaning log to data/processed/cleaning_log.txt
"""
from datetime import date
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data") / "raw" / "crimedata_csv_AllNeighbourhoods_AllYears.csv"
CLEAN_PATH = Path("data") / "processed" / "crime_data_cleaned.csv"
LOG_PATH = Path("data") / "processed" / "cleaning_log.txt"

ZERO_COORD_COLS = ["X", "Y"]

SEASON_MAP = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Fall", 10: "Fall", 11: "Fall",
}


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Apply every cleaning step to a raw dataframe.

    Returns (cleaned_df, log_lines) so the logic is unit-testable without
    touching the filesystem. Does not mutate the input dataframe.
    """
    lines: list[str] = []

    def log_step(msg: str) -> None:
        print(msg)
        lines.append(msg)

    df = df.copy()

    for col in ["TYPE", "NEIGHBOURHOOD", "HUNDRED_BLOCK"]:
        df[col] = df[col].astype(str).str.strip()
    log_step("Categorical values: stripped whitespace.")

    before = len(df)
    df = df.drop_duplicates()
    log_step(f"Duplicates removed: {before - len(df):,}")
    log_step(f"Rows after dedupe: {len(df):,}")

    zero_mask = (df["X"] == 0) | (df["Y"] == 0)
    log_step(f"Zero-coordinate rows flagged as missing: {int(zero_mask.sum()):,}")
    df.loc[zero_mask, ZERO_COORD_COLS] = pd.NA

    df["INCIDENT_DATETIME"] = pd.to_datetime(
        dict(
            year=df["YEAR"],
            month=df["MONTH"],
            day=df["DAY"],
            hour=df["HOUR"],
            minute=df["MINUTE"],
        )
    )
    df["DAY_OF_WEEK"] = df["INCIDENT_DATETIME"].dt.day_name()
    df["SEASON"] = df["MONTH"].map(SEASON_MAP)
    log_step("Created: INCIDENT_DATETIME, DAY_OF_WEEK, SEASON.")

    before = len(df)
    df = df.dropna(subset=["YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "TYPE"])
    log_step(f"Rows dropped for invalid core fields: {before - len(df):,}")

    log_step(f"Final rows: {len(df):,}")
    log_step(f"Final columns: {list(df.columns)}")

    return df, lines


def main() -> None:
    lines: list[str] = [
        "=" * 70,
        "VPD CRIME DATA - CLEANING LOG",
        f"Generated: {date.today().isoformat()}",
        "=" * 70,
    ]

    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")
    lines.append(f"Raw rows: {len(df):,}")

    cleaned, step_lines = clean_dataframe(df)
    lines.extend(step_lines)

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEAN_PATH, index=False)
    lines.append(f"Cleaned data saved to {CLEAN_PATH}")

    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Cleaning log written to {LOG_PATH}")


if __name__ == "__main__":
    main()
