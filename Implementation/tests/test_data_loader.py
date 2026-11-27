"""Tests for data loading and the live-data merge (app/utils/data_loader.py)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils.data_loader import merge_user_incidents  # noqa: E402


def public_df() -> pd.DataFrame:
    """Two public rows shaped like the cleaned dataset."""
    return pd.DataFrame({
        "TYPE": ["Mischief", "Other Theft"],
        "YEAR": [2025, 2025],
        "MONTH": [10, 11],
        "DAY": [8, 9],
        "HOUR": [21, 14],
        "MINUTE": [0, 30],
        "HUNDRED_BLOCK": ["35XX OXFORD ST", "12XX MAIN ST"],
        "NEIGHBOURHOOD": ["Hastings-Sunrise", "Mount Pleasant"],
        "X": [497950.3, 492000.0],
        "Y": [5459208.9, 5456500.0],
        "INCIDENT_DATETIME": pd.to_datetime(
            ["2025-10-08 21:00:00", "2025-11-09 14:30:00"]
        ),
        "DAY_OF_WEEK": ["Wednesday", "Sunday"],
        "SEASON": ["Fall", "Fall"],
    })


def user_record(**overrides) -> dict:
    record = {
        "crime_type": "Theft from Vehicle",
        "incident_date": "2026-03-15",
        "hour": 18,
        "neighbourhood": "West End",
        "location": "15XX DAVIE ST",
        "notes": "demo entry",
    }
    record.update(overrides)
    return record


class TestMergeUserIncidents:
    def test_empty_records_returns_public_unchanged(self):
        df = public_df()
        merged = merge_user_incidents(df, [])
        assert len(merged) == len(df)
        assert "SOURCE" not in merged.columns

    def test_record_mapped_to_public_schema(self):
        merged = merge_user_incidents(public_df(), [user_record()])
        assert len(merged) == 3
        row = merged.iloc[-1]
        assert row["TYPE"] == "Theft from Vehicle"
        assert row["YEAR"] == 2026 and row["MONTH"] == 3 and row["DAY"] == 15
        assert row["HOUR"] == 18.0
        assert row["NEIGHBOURHOOD"] == "West End"
        assert row["HUNDRED_BLOCK"] == "15XX DAVIE ST"
        assert row["DAY_OF_WEEK"] == "Sunday"  # 2026-03-15 is a Sunday
        assert row["SEASON"] == "Spring"
        assert row["SOURCE"] == "user"
        assert (merged["SOURCE"] == "public").sum() == 2

    def test_datetime_keeps_the_hour(self):
        merged = merge_user_incidents(public_df(), [user_record(hour=7)])
        assert merged.iloc[-1]["INCIDENT_DATETIME"] == pd.Timestamp(
            "2026-03-15 07:00:00"
        )

    def test_missing_hour_becomes_nan(self):
        merged = merge_user_incidents(public_df(), [user_record(hour=None)])
        row = merged.iloc[-1]
        assert np.isnan(row["HOUR"])
        assert row["INCIDENT_DATETIME"] == pd.Timestamp("2026-03-15")

    def test_coordinates_are_nan(self):
        merged = merge_user_incidents(public_df(), [user_record()])
        row = merged.iloc[-1]
        assert np.isnan(row["X"]) and np.isnan(row["Y"])

    def test_multiple_records_append(self):
        records = [user_record(), user_record(crime_type="Mischief", hour=None)]
        merged = merge_user_incidents(public_df(), records)
        assert len(merged) == 4
        assert (merged["SOURCE"] == "user").sum() == 2
