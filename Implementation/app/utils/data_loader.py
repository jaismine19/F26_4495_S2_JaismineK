"""Cached data loading for the Streamlit app."""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
CLEAN_PATH = REPO_ROOT / "data" / "processed" / "crime_data_cleaned.csv"

# Matches the season definition in scripts/02_clean_data.py.
SEASON_BY_MONTH = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Fall", 10: "Fall", 11: "Fall",
}


@st.cache_data(show_spinner="Loading crime data...")
def load_crime_data() -> pd.DataFrame | None:
    """Load the cleaned crime dataset, or None if not yet generated."""
    if not CLEAN_PATH.exists():
        return None
    df = pd.read_csv(CLEAN_PATH)
    # Coerce defensively: older CSV exports wrote midnight timestamps without
    # the time part, so parse_dates would leave the column as strings.
    df["INCIDENT_DATETIME"] = pd.to_datetime(df["INCIDENT_DATETIME"], errors="coerce")
    return df


def merge_user_incidents(public_df: pd.DataFrame,
                         records: list[dict]) -> pd.DataFrame:
    """Append user-entered incidents to the public dataset, same schema.

    Each manually added record is converted into the public column layout
    (TYPE, YEAR, ..., DAY_OF_WEEK, SEASON) and tagged SOURCE='user', while
    the public rows are tagged SOURCE='public'. User-entered records have no
    coordinates, so X/Y are NaN - the map counts them per neighbourhood but
    does not place them on the map. When no records are given, the public
    frame is returned untouched.
    """
    if not records:
        return public_df.copy()

    rows = []
    for r in records:
        date = pd.Timestamp(r["incident_date"])
        hour = r.get("hour")
        when = date + pd.Timedelta(hours=int(hour)) if hour is not None else date
        rows.append({
            "TYPE": r["crime_type"],
            "YEAR": date.year,
            "MONTH": date.month,
            "DAY": date.day,
            "HOUR": float(hour) if hour is not None else np.nan,
            "MINUTE": np.nan,
            "HUNDRED_BLOCK": r.get("location", ""),
            "NEIGHBOURHOOD": r["neighbourhood"],
            "X": np.nan,
            "Y": np.nan,
            "INCIDENT_DATETIME": when,
            "DAY_OF_WEEK": when.strftime("%A"),
            "SEASON": SEASON_BY_MONTH[date.month],
            "SOURCE": "user",
        })
    merged = pd.concat(
        [public_df.assign(SOURCE="public"), pd.DataFrame(rows)],
        ignore_index=True,
    )
    return merged


@st.cache_data
def load_neighbourhood_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Incident counts by neighbourhood (cached; df is hashable input)."""
    return df["NEIGHBOURHOOD"].value_counts().rename("incidents").to_frame()
