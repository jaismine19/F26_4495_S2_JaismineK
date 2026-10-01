"""Shared UI helpers for app pages."""
import streamlit as st


def under_construction(feature: str, phase: str) -> None:
    st.title(feature)
    st.info(f"Under development - planned for the **{phase}** phase.")
    st.markdown(
        "See the proposal and repository for details:\n"
        "- `docs/research/` - dataset and analysis documentation\n"
        "- `docs/security/` - threat model and privacy review\n"
        "- `README.md` - project progress table"
    )


def require_data():
    """Return the crime dataframe or show a friendly setup message."""
    from app.utils.data_loader import load_crime_data

    df = load_crime_data()
    if df is None:
        st.warning(
            "Cleaned data not found. Run the pipeline first:\n\n"
            "```bash\n"
            "python scripts/00_download_data.py\n"
            "python scripts/01_inspect_data.py\n"
            "python scripts/02_clean_data.py\n"
            "```"
        )
        return None
    return df
