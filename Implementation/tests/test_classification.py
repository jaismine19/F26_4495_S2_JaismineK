"""Tests for the crime-type classification module (app/utils/classification.py)."""
import numpy as np
import pandas as pd
import pytest

from app.utils import classification as clf


def tiny_df() -> pd.DataFrame:
    """Small synthetic dataset spanning two 'years' with a learnable pattern."""
    rows = []
    rng = np.random.default_rng(7)
    for year in (2020, 2021, 2025):
        for i in range(120):
            crime = "Theft" if i % 3 == 0 else "Mischief"
            rows.append({
                "TYPE": crime,
                "YEAR": year,
                "MONTH": int(rng.integers(1, 13)),
                "HOUR": int(rng.integers(0, 24)),
                "DAY_OF_WEEK": "Monday",
                "SEASON": "Winter",
                "NEIGHBOURHOOD": "Downtown" if year == 2025 else "Kitsilano",
                "INCIDENT_DATETIME": pd.Timestamp(f"{year}-01-01"),
            })
    return pd.DataFrame(rows)


def test_build_features_temporal_only():
    df = tiny_df()
    X, y = clf.build_features(df, include_geo=False)
    assert set(clf.TEMPORAL_FEATURES).issubset(X.columns)
    assert not any(c.startswith("nb_") for c in X.columns)
    assert len(X) == len(y)


def test_build_features_with_geo():
    df = tiny_df()
    X, y = clf.build_features(df, include_geo=True)
    assert any(c.startswith("nb_") for c in X.columns)
    assert len(X) == len(y)


def test_build_features_drops_missing_rows():
    df = tiny_df()
    df.loc[0, "HOUR"] = np.nan
    X, y = clf.build_features(df)
    assert len(X) == len(df) - 1


def test_time_split_respects_year():
    df = tiny_df()
    train, test = clf.time_split(df)
    assert (train["YEAR"] < clf.TEST_START_YEAR).all()
    assert (test["YEAR"] >= clf.TEST_START_YEAR).all()


def test_evaluate_models_returns_metrics():
    df = tiny_df()
    X, y = clf.build_features(df, include_geo=True)
    data = X.copy()
    data["TYPE"] = y.values
    train, test = clf.time_split(data)
    models = clf._models(seed=1)
    results = clf.evaluate_models(
        train.drop(columns=["TYPE"]), train["TYPE"],
        test.drop(columns=["TYPE"]), test["TYPE"],
        models, sample=60, knn_sample=30, seed=1)
    for name in ("Logistic Regression", "Decision Tree", "Random Forest"):
        metrics = results[name]
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["macro_f1"] <= 1.0
        assert 0.0 <= metrics["weighted_f1"] <= 1.0
        assert metrics["confusion"].shape == (2, 2)


def test_error_analysis_sorted_and_bounded():
    conf = np.array([[10, 6, 1], [5, 20, 0], [2, 1, 30]])
    pairs = clf.error_analysis(conf, ["a", "b", "c"], top=3)
    assert len(pairs) == 3
    assert pairs[0]["count"] >= pairs[1]["count"] >= pairs[2]["count"]
    assert all(p["true"] != p["predicted"] for p in pairs)


def test_run_experiment_end_to_end():
    result = clf.run_experiment(tiny_df(), sample=80, knn_sample=30, seed=3)
    assert set(result["experiment"]) == {"temporal", "temporal+geo"}
    assert result["best_model"] in result["experiment"][result["best_feature_set"]]
    assert "Most-common" not in result["best_model"]
    assert isinstance(result["confusions"], list)


def test_run_experiment_sample_cap_is_respected():
    result = clf.run_experiment(tiny_df(), sample=50, knn_sample=20, seed=3)
    rows = result["experiment"]["temporal"]["Random Forest"]["train_rows"]
    assert rows == 50
    knn_rows = result["experiment"]["temporal"]["K-Nearest Neighbours"]["train_rows"]
    assert knn_rows == 20
