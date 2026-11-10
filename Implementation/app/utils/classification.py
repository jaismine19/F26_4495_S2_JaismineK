"""Crime-type classification experiments (proposal section 2.6).

Which model can best tell crime types apart from time and place features?

- Time-aware holdout: train on years <= 2024, evaluate on 2025-2026
  (crime records are time-dependent, so a random split would leak).
- Models: a "guess the most common type" baseline, Logistic Regression,
  Decision Tree, Random Forest, and K-Nearest Neighbours.
- Feature experiments: temporal features alone vs temporal + neighbourhood
  (proposal hypothesis H3 asks whether adding geography changes performance).
- Because K-Nearest Neighbours is slow, it uses a smaller reference set;
  this is documented, not hidden.

This is pattern description for research, not prediction for policing
(see the Methodology & Limitations page).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

TEMPORAL_FEATURES = ["YEAR", "MONTH", "HOUR", "DAY_OF_WEEK", "SEASON"]
GEO_FEATURES = ["NEIGHBOURHOOD"]

SEASON_ORDER = {"Winter": 0, "Spring": 1, "Summer": 2, "Fall": 3}
DOW_ORDER = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6,
}

TEST_START_YEAR = 2025

# Stratified training sample (keeps rare crime types represented) and the
# smaller reference set KNN uses because brute-force neighbours is slow.
DEFAULT_TRAIN_SAMPLE = 150_000
DEFAULT_KNN_SAMPLE = 25_000
RANDOM_SEED = 42


def build_features(df: pd.DataFrame, include_geo: bool = False
                   ) -> tuple[pd.DataFrame, pd.Series]:
    """Return (X, y) with temporal features (+ one-hot neighbourhoods).

    Rows with missing crime type, hour, or neighbourhood are dropped.
    """
    clean = df.dropna(subset=["TYPE", "HOUR", "NEIGHBOURHOOD"]).copy()
    features = pd.DataFrame(
        {
            "YEAR": clean["YEAR"].astype(int),
            "MONTH": clean["MONTH"].astype(int),
            "HOUR": clean["HOUR"].astype(int),
            "DAY_OF_WEEK": clean["DAY_OF_WEEK"].map(DOW_ORDER),
            "SEASON": clean["SEASON"].map(SEASON_ORDER),
        }
    )
    if include_geo:
        dummies = pd.get_dummies(clean["NEIGHBOURHOOD"], prefix="nb")
        features = pd.concat([features, dummies], axis=1)
    features = features.dropna()
    y = clean.loc[features.index, "TYPE"].astype(str)
    return features, y


def time_split(df: pd.DataFrame, test_start_year: int = TEST_START_YEAR
               ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split rows into train (before test_start_year) and test (from it on)."""
    mask = df["YEAR"] < test_start_year
    return df[mask].copy(), df[~mask].copy()


def _models(seed: int = RANDOM_SEED) -> dict:
    """Model factory: name -> (estimator, needs_scaling, uses_reference_sample)."""
    return {
        "Most-common-type baseline": (
            DummyClassifier(strategy="most_frequent"), False, False,
        ),
        "Logistic Regression": (
            LogisticRegression(max_iter=2000), True, False,
        ),
        "Decision Tree": (
            DecisionTreeClassifier(max_depth=12, random_state=seed), False, False,
        ),
        "Random Forest": (
            RandomForestClassifier(n_estimators=150, n_jobs=-1,
                                   random_state=seed), False, False,
        ),
        "K-Nearest Neighbours": (
            KNeighborsClassifier(n_neighbors=5, n_jobs=-1), True, True,
        ),
    }


def _metrics(model, X_test, y_test, classes) -> dict:
    """Fit has already happened; compute the shared metric block."""
    y_pred = model.predict(X_test)
    conf = confusion_matrix(y_test, y_pred, labels=classes)
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro",
                                   zero_division=0)),
        "weighted_f1": float(f1_score(y_test, y_pred, average="weighted",
                                      zero_division=0)),
        "confusion": conf,
        "predictions": y_pred,
    }


def evaluate_models(X_train, y_train, X_test, y_test, models,
                    sample: int | None = None,
                    knn_sample: int | None = None,
                    seed: int = RANDOM_SEED) -> dict:
    """Train each model and evaluate on the same test set.

    `sample` caps the (stratified) training size; `knn_sample` caps the
    reference size for K-Nearest Neighbours.
    """
    classes = sorted(y_train.unique())
    results = {}
    for name, (estimator, needs_scaling, uses_ref) in models.items():
        X_tr, y_tr = X_train, y_train
        if sample and sample < len(X_tr):
            # Stratified so rare crime types stay represented.
            X_tr, _, y_tr, _ = train_test_split(
                X_tr, y_tr, train_size=sample, stratify=y_tr,
                random_state=seed)
        if uses_ref and knn_sample and knn_sample < len(X_tr):
            X_tr, _, y_tr, _ = train_test_split(
                X_tr, y_tr, train_size=knn_sample, stratify=y_tr,
                random_state=seed)
        model = (make_pipeline(StandardScaler(), estimator)
                 if needs_scaling else estimator)
        model.fit(X_tr, y_tr)
        results[name] = _metrics(model, X_test, y_test, classes)
        results[name]["train_rows"] = len(X_tr)
    results["_classes"] = classes
    results["_test_rows"] = len(X_test)
    return results


def error_analysis(conf: np.ndarray, classes: list[str], top: int = 5
                   ) -> list[dict]:
    """Most common confusions: true type -> wrongly guessed type."""
    pairs = []
    for i, true_label in enumerate(classes):
        for j, pred_label in enumerate(classes):
            if i != j and conf[i, j] > 0:
                pairs.append({
                    "true": true_label,
                    "predicted": pred_label,
                    "count": int(conf[i, j]),
                })
    pairs.sort(key=lambda p: -p["count"])
    return pairs[:top]


def run_experiment(df: pd.DataFrame,
                   sample: int = DEFAULT_TRAIN_SAMPLE,
                   knn_sample: int = DEFAULT_KNN_SAMPLE,
                   seed: int = RANDOM_SEED) -> dict:
    """Full proposal experiment: models x feature sets on a time-aware split.

    Returns per-model metrics for "temporal" and "temporal+geo", plus the
    best combination (by macro F1) with its per-class report and the most
    common confusions for the error analysis.
    """
    models = _models(seed)
    experiment = {}
    for feature_set, include_geo in (("temporal", False), ("temporal+geo", True)):
        X, y = build_features(df, include_geo=include_geo)
        data = X.copy()
        data["TYPE"] = y.values
        train_df, test_df = time_split(data)
        X_train = train_df.drop(columns=["TYPE"])
        y_train = train_df["TYPE"]
        X_test = test_df.drop(columns=["TYPE"])
        y_test = test_df["TYPE"]
        experiment[feature_set] = evaluate_models(
            X_train, y_train, X_test, y_test, models,
            sample=sample, knn_sample=knn_sample, seed=seed)

    # Best combination by macro F1 (a "most-common" baseline is never best).
    best = None
    for feature_set in experiment:
        for name, metrics in experiment[feature_set].items():
            if name.startswith("_") or "Most-common" in name:
                continue
            if best is None or metrics["macro_f1"] > best[2]:
                best = (feature_set, name, metrics["macro_f1"])
    feature_set, model_name, _ = best
    classes = experiment[feature_set]["_classes"]
    conf = experiment[feature_set][model_name]["confusion"]
    return {
        "experiment": experiment,
        "best_feature_set": feature_set,
        "best_model": model_name,
        "classes": classes,
        "confusions": error_analysis(conf, classes),
    }
