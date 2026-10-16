"""Unit tests for the statistical helpers used by the Statistical page."""
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils import stats  # noqa: E402


def associated_df() -> pd.DataFrame:
    """Theft is evenly split across seasons; Mischief is summer-heavy."""
    return pd.DataFrame(
        {
            "TYPE": ["Theft"] * 60 + ["Mischief"] * 40,
            "SEASON": ["Winter"] * 30 + ["Summer"] * 30
            + ["Winter"] * 10 + ["Summer"] * 30,
        }
    )


def independent_df() -> pd.DataFrame:
    """Perfectly independent: every type appears equally in every season."""
    return pd.DataFrame(
        {
            "TYPE": ["Theft"] * 50 + ["Mischief"] * 50,
            "SEASON": ["Winter", "Summer"] * 50,
        }
    )


class TestChiSquare:
    def test_detects_association(self):
        result = stats.chi_square_test(associated_df(), "TYPE", "SEASON")
        assert result["significant"] is True
        assert result["p"] < stats.ALPHA
        assert result["dof"] == 1

    def test_reports_no_association_when_independent(self):
        result = stats.chi_square_test(independent_df(), "TYPE", "SEASON")
        assert result["significant"] is False
        assert result["p"] >= stats.ALPHA

    def test_expected_table_matches_observed_shape(self):
        result = stats.chi_square_test(associated_df(), "TYPE", "SEASON")
        assert result["expected"].shape == result["observed"].shape
        assert list(result["expected"].columns) == list(result["observed"].columns)


class TestInterpret:
    def test_strong_evidence(self):
        assert "Strong evidence" in stats.interpret_p(0.0001)

    def test_significant(self):
        assert "statistically significant" in stats.interpret_p(0.01)

    def test_not_significant(self):
        assert "No statistically significant" in stats.interpret_p(0.5)


class TestSummaryStats:
    def make_df(self):
        dates = pd.to_datetime(
            ["2024-01-01 10:00"] * 3 + ["2024-01-02 22:00"] * 2
        )
        return pd.DataFrame(
            {
                "TYPE": ["Theft"] * 3 + ["Mischief"] * 2,
                "NEIGHBOURHOOD": ["West End"] * 5,
                "YEAR": [2024] * 5,
                "HOUR": [10, 10, 10, 22, 22],
                "INCIDENT_DATETIME": dates,
            }
        )

    def test_basic_counts(self):
        s = stats.summary_stats(self.make_df())
        assert s["incidents"] == 5
        assert s["types"] == 2
        assert s["top_type"] == "Theft"
        assert s["top_type_share"] == pytest.approx(60.0)
        assert s["mean_per_day"] == pytest.approx(2.5)

    def test_peak_hour_excludes_violent_types(self):
        df = self.make_df()
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    {
                        "TYPE": ["Homicide"],
                        "NEIGHBOURHOOD": ["West End"],
                        "YEAR": [2024],
                        "HOUR": [0],
                        "INCIDENT_DATETIME": pd.to_datetime(["2024-01-01 00:00"]),
                    }
                ),
            ]
        )
        s = stats.summary_stats(df)
        # Homicide's redacted hour (0) must not become the reported peak.
        assert s["peak_hour"] == 10
