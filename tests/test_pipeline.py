"""Functional tests for the data pipeline and app utilities.

Run from the repository root:
    pytest tests/ -v

The pipeline scripts live under scripts/ with numeric filenames, so they are
loaded by path here rather than imported as modules.
"""
import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(REPO_ROOT))

from app.utils import auth  # noqa: E402  (pure stdlib; no streamlit import)


def _load_module(path: Path):
    """Load a python file by path (for numeric script names)."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


clean_data = _load_module(REPO_ROOT / "scripts" / "02_clean_data.py")
inspect_data = _load_module(REPO_ROOT / "scripts" / "01_inspect_data.py")


def make_raw_df() -> pd.DataFrame:
    """Small synthetic raw dataframe with known cleaning needs.

    Rows 0-1 are exact duplicates; row 2 has zero coordinates and
    leading/trailing whitespace in its categorical fields.
    """
    return pd.DataFrame(
        {
            "TYPE": ["Theft from Vehicle ", "Theft from Vehicle ", " Mischief"],
            "YEAR": [2024, 2024, 2024],
            "MONTH": [1, 1, 7],
            "DAY": [5, 5, 20],
            "HOUR": [14, 14, 0],
            "MINUTE": [30, 30, 0],
            "HUNDRED_BLOCK": ["10XX ROBSON ST", "10XX ROBSON ST", " 1XX MAIN ST"],
            "NEIGHBOURHOOD": ["West End", "West End", "Mount Pleasant"],
            "X": [490000.0, 490000.0, 0.0],
            "Y": [5458000.0, 5458000.0, 0.0],
        }
    )


# ------------------------------------------------------------ cleaning
class TestCleanDataframe:
    def test_removes_exact_duplicates(self):
        df, _ = clean_data.clean_dataframe(make_raw_df())
        assert len(df) == 2

    def test_strips_whitespace_from_categoricals(self):
        df, _ = clean_data.clean_dataframe(make_raw_df())
        assert set(df["TYPE"]) == {"Theft from Vehicle", "Mischief"}
        assert set(df["NEIGHBOURHOOD"]) == {"West End", "Mount Pleasant"}

    def test_flags_zero_coordinates_as_missing(self):
        df, _ = clean_data.clean_dataframe(make_raw_df())
        zero_row = df.loc[df["HUNDRED_BLOCK"] == "1XX MAIN ST"]
        assert pd.isna(zero_row["X"].iloc[0]) and pd.isna(zero_row["Y"].iloc[0])

    def test_creates_temporal_features(self):
        df, _ = clean_data.clean_dataframe(make_raw_df())
        assert "INCIDENT_DATETIME" in df.columns
        assert "DAY_OF_WEEK" in df.columns
        assert "SEASON" in df.columns
        january_row = df.loc[df["MONTH"] == 1].iloc[0]
        assert january_row["SEASON"] == "Winter"
        july_row = df.loc[df["MONTH"] == 7].iloc[0]
        assert july_row["SEASON"] == "Summer"

    def test_does_not_mutate_input(self):
        raw = make_raw_df()
        clean_data.clean_dataframe(raw)
        assert len(raw) == 3


# ------------------------------------------------------------ inspection
class TestInspectSummary:
    def test_summary_reports_row_count(self):
        summary = inspect_data.build_summary(make_raw_df())
        assert "Rows: 3" in summary

    def test_summary_reports_duplicates(self):
        summary = inspect_data.build_summary(make_raw_df())
        # Value sits on the line after the "Duplicate rows:" label.
        value = summary.split("Duplicate rows:")[1].split("\n")[1].strip()
        assert value == "1"


# ------------------------------------------------------------ auth
class TestAuth:
    def test_authenticate_valid_admin(self):
        user = auth.authenticate("admin", "demo_admin_123")
        assert user is not None
        assert user["role"] == "Administrator"
        assert "password" not in user
        assert "view_all" in user["permissions"]

    def test_authenticate_rejects_wrong_password(self):
        assert auth.authenticate("admin", "wrong-password") is None

    def test_authenticate_rejects_unknown_user(self):
        assert auth.authenticate("nobody", "demo_admin_123") is None

    def test_authenticate_is_case_insensitive_username(self):
        assert auth.authenticate("ADMIN", "demo_admin_123") is not None

    def test_hash_password_roundtrip(self):
        digest, salt_hex = auth.hash_password("s3cret")
        assert auth.verify_password("s3cret", digest, salt_hex)
        assert not auth.verify_password("other", digest, salt_hex)

    def test_has_permission(self):
        analyst = auth.authenticate("analyst", "demo_analyst_123")
        assert auth.has_permission(analyst, "add_incident")
        assert not auth.has_permission(analyst, "manage_users")
        assert not auth.has_permission(None, "add_incident")

    def test_demo_hashes_match_store(self):
        for username, stored in auth.DEMO_USERS.items():
            assert auth.verify_password(
                stored["password"], stored["password_hash"], stored["salt"]
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
