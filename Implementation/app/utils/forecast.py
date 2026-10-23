"""Time-series forecasting utilities - simple, explainable baselines.

Monthly incident counts with two baseline models:
- moving average: the next months are forecast as the mean of the last
  `window` months
- naive seasonal: the next 12 months repeat the last 12 observed months
  ("same as last year")

Accuracy is measured on a held-out tail (MAE / RMSE) so the app can honestly
say how wrong the model has been. The missing 2022 months are filled with 0
and documented, not hidden.
"""
import numpy as np
import pandas as pd


def monthly_counts(df: pd.DataFrame, crime_type: str | None = None) -> pd.Series:
    """Monthly incident counts; missing months (e.g., 2022) are filled with 0."""
    if crime_type:
        df = df[df["TYPE"] == crime_type]
    ts = df.set_index("INCIDENT_DATETIME").resample("ME").size()
    full_index = pd.date_range(ts.index.min(), ts.index.max(), freq="ME")
    return ts.reindex(full_index, fill_value=0)


def moving_average_forecast(history: pd.Series, window: int = 12,
                            horizon: int = 12) -> np.ndarray:
    """Forecast `horizon` months as the mean of the last `window` months."""
    if len(history) < window:
        window = max(1, len(history))
    level = float(history.iloc[-window:].mean())
    return np.full(horizon, level)


def naive_forecast(history: pd.Series, horizon: int = 12) -> np.ndarray:
    """Seasonal naive: repeat the last 12 observed months."""
    seasonal = history.iloc[-12:].to_numpy(dtype=float)
    if len(seasonal) == 0:
        return np.zeros(horizon)
    reps = int(np.ceil(horizon / len(seasonal)))
    return np.tile(seasonal, reps)[:horizon]


def evaluate(actual: np.ndarray, predicted: np.ndarray) -> tuple[float, float]:
    """Return (MAE, RMSE) - mean absolute and root-mean-squared error."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mae = float(np.mean(np.abs(actual - predicted)))
    rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
    return mae, rmse


def train_evaluate(df: pd.DataFrame, crime_type: str | None = None,
                   test_months: int = 12, window: int = 12) -> dict | None:
    """Train baselines on the past, evaluate on the last `test_months`.

    The final (current, possibly partial) month is excluded from evaluation.
    Returns None when there is not enough history.
    """
    ts = monthly_counts(df, crime_type)
    if len(ts) < test_months + window + 2:
        return None

    # Hold out the last `test_months` COMPLETE months (drop the partial month).
    test = ts.iloc[-test_months - 1: -1]
    train = ts.iloc[: -test_months - 1]

    mv_pred = moving_average_forecast(train, window=window, horizon=len(test))
    naive_pred = naive_forecast(train, horizon=len(test))

    mae_mv, rmse_mv = evaluate(test.to_numpy(), mv_pred)
    mae_naive, rmse_naive = evaluate(test.to_numpy(), naive_pred)

    # Forecast the next 12 months from the full history.
    future = moving_average_forecast(ts, window=window, horizon=12)
    future_naive = naive_forecast(ts, horizon=12)
    future_index = pd.date_range(ts.index[-1] + pd.offsets.MonthEnd(1),
                                 periods=12, freq="ME")

    return {
        "series": ts,
        "test": test,
        "test_pred_mv": mv_pred,
        "test_pred_naive": naive_pred,
        "mae_mv": mae_mv,
        "rmse_mv": rmse_mv,
        "mae_naive": mae_naive,
        "rmse_naive": rmse_naive,
        "better_than_naive": mae_mv < mae_naive,
        "future": future,
        "future_naive": future_naive,
        "future_index": future_index,
        "window": window,
    }
