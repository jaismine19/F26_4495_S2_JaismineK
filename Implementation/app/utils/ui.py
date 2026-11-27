"""Shared UI helpers for app pages."""
import streamlit as st


def under_construction(feature: str) -> None:
    st.title(feature)
    st.info("This page is still being built. Check back soon.")


def require_data():
    """Return the crime dataframe or show a friendly setup message.

    When the sidebar "simulate live data" toggle is on, the manually added
    incidents (prototype.db) are merged into the public dataset, so every
    page analyzes the combined data.
    """
    from app.utils.data_loader import load_crime_data

    df = load_crime_data()
    if df is None:
        st.warning(
            "Cleaned data not found. Run the pipeline first:\n\n"
            "```bash\n"
            "python Implementation/scripts/00_download_data.py\n"
            "python Implementation/scripts/01_inspect_data.py\n"
            "python Implementation/scripts/02_clean_data.py\n"
            "```"
        )
        return None
    if st.session_state.get("include_user_incidents", False):
        from app.utils import db
        from app.utils.data_loader import merge_user_incidents

        records = db.fetch_incidents(limit=None)
        if records:
            df = merge_user_incidents(df, records)
    return df
