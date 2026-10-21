"""Shared UI helpers for app pages."""
import streamlit as st


def under_construction(feature: str) -> None:
    st.title(feature)
    st.info("This page is still being built. Check back soon.")


def require_data():
    """Return the crime dataframe or show a friendly setup message."""
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
    return df
