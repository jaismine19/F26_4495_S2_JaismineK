import streamlit as st

st.title("Methodology & Limitations")

st.markdown("### Data source")
st.markdown(
    "- Vancouver Police Department GeoDASH open data: all neighbourhoods, "
    "all years (2003-2026, no 2022).\n"
    "- Reported and founded incidents only; not a complete count of all crime.\n"
    "- Locations are anonymized to hundred-block level; violent incidents are "
    "aggregated under broad categories."
)

st.markdown("### Processing pipeline")
st.markdown(
    "1. Download (`scripts/00_download_data.py`)\n"
    "2. Quality inspection (`scripts/01_inspect_data.py`)\n"
    "3. Cleaning (`scripts/02_clean_data.py`): deduplication, categorical "
    "standardization, zero-coordinate flagging, datetime/day-of-week/season "
    "features. 927,794 -> 893,267 rows."
)

st.markdown("### Limitations")
st.markdown(
    "- **Missing 2022**: no records exist for this year in the source data.\n"
    "- **Reporting lag**: incidents may be reclassified or reported late.\n"
    "- **Association, not causation**: statistical and ML findings describe "
    "patterns in reported data; they do not explain causes.\n"
    "- **Prototype scope**: this app is a research prototype, not an official "
    "crime-reporting or policing-decision system."
)
