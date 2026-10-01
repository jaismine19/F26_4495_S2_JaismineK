"""Clean the VPD crime dataset.

Run from the repository root:
    python scripts/02_clean_data.py

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


def log_step(lines: list[str], msg: str) -> None:
    print(msg)
    lines.append(msg)


def main() -> None:
    lines: list[str] = []
    log_step(lines, "=" * 70)
    log_step(lines, "VPD CRIME DATA - CLEANING LOG")
    log_step(lines, f"Generated: {date.today().isoformat()}")
    log_step(lines, "=" * 70)

    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")
    log_step(lines, f"Raw rows: {len(df):,}")

    for col in ["TYPE", "NEIGHBOURHOOD", "HUNDRED_BLOCK"]:
        df[col] = df[col].astype(str).str.strip()
    log_step(lines, "Categorical values: stripped whitespace.")

    before = len(df)
    df = df.drop_duplicates()
    log_step(lines, f"Duplicates removed: {before - len(df):,}")
    log_step(lines, f"Rows after dedupe: {len(df):,}")

    zero_mask = (df["X"] == 0) | (df["Y"] == 0)
    log_step(lines, f"Zero-coordinate rows flagged as missing: {int(zero_mask.sum()):,}")
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
    df["SEASON"] = df["MONTH"].map(
        {
            12: "Winter", 1: "Winter", 2: "Winter",
            3: "Spring", 4: "Spring", 5: "Spring",
            6: "Summer", 7: "Summer", 8: "Summer",
            9: "Fall", 10: "Fall", 11: "Fall",
        }
    )
    log_step(lines, "Created: INCIDENT_DATETIME, DAY_OF_WEEK, SEASON.")

    before = len(df)
    df = df.dropna(subset=["YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "TYPE"])
    log_step(lines, f"Rows dropped for invalid core fields: {before - len(df):,}")

    log_step(lines, f"Final rows: {len(df):,}")
    log_step(lines, f"Final columns: {list(df.columns)}")

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    log_step(lines, f"Cleaned data saved to {CLEAN_PATH}")

    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Cleaning log written to {LOG_PATH}")


if __name__ == "__main__":
    main()
