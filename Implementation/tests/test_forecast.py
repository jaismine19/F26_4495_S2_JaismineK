"""Unit tests for the forecasting baselines (app/utils/forecast.py)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils import forecast  # noqa: E402


def make_df(years: list[int], months: list[int], counts: list[int]) -> pd.DataFrame:
    rows = []
    for y, m, c in zip(years, months, counts):
        rows.append(
            {"TYPE": "Theft", "INCIDENT_DATETIME": pd.Timestamp(y, m, 15)}
        )
    # Each row contributes `count` incidents.
    return pd.DataFrame(rows).loc[lambda d: d.index.repeat(counts)].reset_index(drop=True)


class TestMonthlyCounts:
    def test_fills_missing_months_with_zero(self):
        df = pd.DataFrame(
            {
                "TYPE": ["Theft"] * 3,
                "INCIDENT_DATETIME": pd.to_datetime(
                    ["2023-01-15", "2023-03-15", "2023-04-15"]
                ),
            }
        )
        ts = forecast.monthly_counts(df)
        assert len(ts) == 4  # Jan-Apr
        assert ts.iloc[1] == 0  # Feb missing -> 0

    def test_filters_by_crime_type(self):
        df = pd.DataFrame(
            {
                "TYPE": ["Theft", "Mischief"],
                "INCIDENT_DATETIME": pd.to_datetime(["2023-01-15", "2023-01-20"]),
            }
        )
        ts = forecast.monthly_counts(df, "Mischief")
        assert ts.iloc[0] == 1


class TestForecasts:
    def test_moving_average_is_window_mean(self):
        history = pd.Series([10.0, 20.0, 30.0])
        out = forecast.moving_average_forecast(history, window=2, horizon=5)
        assert len(out) == 5
        assert np.allclose(out, 25.0)

    def test_naive_repeats_last_12(self):
        history = pd.Series(np.arange(1.0, 25.0))  # 24 months
        out = forecast.naive_forecast(history, horizon=15)
        assert len(out) == 15
        assert out[0] == 13.0  # repeats from month 13
        assert out[12] == 13.0  # wraps around

    def test_evaluate_known_values(self):
        mae, rmse = forecast.evaluate(np.array([1.0, 3.0]), np.array([2.0, 2.0]))
        assert mae == pytest.approx(1.0)
        assert rmse == pytest.approx(1.0)


class TestTrainEvaluate:
    def make_history(self, months: int = 40) -> pd.DataFrame:
        index = pd.date_range("2022-01-15", periods=months, freq="ME")
        rows = []
        for i, ts in enumerate(index):
            rows.extend([{"TYPE": "Theft", "INCIDENT_DATETIME": ts}] * (10 + i))
        return pd.DataFrame(rows)

    def test_returns_metrics_and_future(self):
        result = forecast.train_evaluate(self.make_history(), test_months=12, window=6)
        assert result is not None
        assert "mae_mv" in result and "rmse_mv" in result
        assert len(result["future"]) == 12
        assert len(result["future_index"]) == 12

    def test_not_enough_data_returns_none(self):
        df = pd.DataFrame(
            {"TYPE": ["Theft"], "INCIDENT_DATETIME": pd.to_datetime(["2023-01-15"])}
        )
        assert forecast.train_evaluate(df, test_months=12, window=12) is None
