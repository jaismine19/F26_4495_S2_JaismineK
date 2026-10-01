"""Cached data loading for the Streamlit app."""
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
CLEAN_PATH = REPO_ROOT / "data" / "processed" / "crime_data_cleaned.csv"


@st.cache_data(show_spinner="Loading crime data...")
def load_crime_data() -> pd.DataFrame | None:
    """Load the cleaned crime dataset, or None if not yet generated."""
    if not CLEAN_PATH.exists():
        return None
    df = pd.read_csv(CLEAN_PATH, parse_dates=["INCIDENT_DATETIME"])
    return df


@st.cache_data
def load_neighbourhood_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Incident counts by neighbourhood (cached; df is hashable input)."""
    return df["NEIGHBOURHOOD"].value_counts().rename("incidents").to_frame()
