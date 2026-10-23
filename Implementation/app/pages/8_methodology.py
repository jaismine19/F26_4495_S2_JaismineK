import streamlit as st

st.title("Methodology & Limitations")

st.markdown("### Data source")
st.markdown(
    "- Vancouver Police Department GeoDASH open data: all neighbourhoods, "
    "all years (2003-2026, no 2022).\n"
    "- Reported and founded incidents only; not a complete count of all crime.\n"
    "- Locations are anonymized to hundred-block level; violent incidents are "
    "aggregated under broad categories and their timestamps are redacted "
    "(always hour 0)."
)

st.markdown("### Processing pipeline")
st.markdown(
    "1. Download (`scripts/00_download_data.py`)\n"
    "2. Quality inspection (`scripts/01_inspect_data.py`)\n"
    "3. Cleaning (`scripts/02_clean_data.py`): deduplication, categorical "
    "standardization, zero-coordinate flagging, datetime/day-of-week/season "
    "features. 928,362 -> 893,851 rows.\n"
    "4. Analysis: chi-square tests (scipy), k-means neighbourhood clustering "
    "(scipy), and moving-average / same-as-last-year baseline forecasts with "
    "MAE/RMSE evaluation.\n"
    "5. Geospatial: neighbourhood-level aggregation (median in-bounds UTM "
    "coordinates converted to latitude/longitude); no raw incident points "
    "are ever plotted.\n"
    "6. Secure entry: user-entered prototype records go through input "
    "validation and sanitization into SQLite via parameterized queries, "
    "tagged `source='user'` and kept separate from public data, with an "
    "append-only audit log."
)

st.markdown("### Tech stack")
st.markdown(
    "- **UI:** Streamlit (multipage)\n"
    "- **Charts:** Plotly\n"
    "- **Maps:** Folium (Leaflet) on ESRI World Street Map tiles\n"
    "- **Analytics/ML:** pandas, numpy, scipy (chi-square, k-means)\n"
    "- **Storage:** SQLite (user records only; VPD data stays read-only)\n"
    "- **Security:** PBKDF2 hashing, RBAC, login lockout, audit log, "
    "input validation, parameterized SQL\n"
    "- **Testing:** pytest (62 tests)"
)

st.markdown("### Limitations")
st.markdown(
    "- **Missing 2022**: no records exist for this year in the source data; "
    "forecasts fill it with zeros and show it rather than hide it.\n"
    "- **Reporting lag**: incidents may be reclassified or reported late.\n"
    "- **Association, not causation**: statistical and ML findings describe "
    "patterns in reported data; they do not explain causes.\n"
    "- **Baseline models only**: the forecast is a moving average; it is "
    "measured honestly against the past, not presented as a prediction of "
    "future crime.\n"
    "- **Prototype scope**: this app is a research prototype, not an official "
    "crime-reporting or policing-decision system."
)
