"""Vancouver Urban Safety Intelligence Platform - main entry point.

Run from the repository root:
    streamlit run Implementation/app/Home.py
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

st.set_page_config(
    page_title="Vancouver Urban Safety Intelligence",
    page_icon=":map:",
    layout="wide",
)

with st.sidebar:
    st.toggle(
        "Include manually added incidents in all analyses",
        key="include_user_incidents",
        value=False,
        help=(
            "Simulates live, changing data: incidents added through the "
            "Add Incident page are merged into the public dataset for every "
            "page (Overview, Temporal, Statistics, Crime Map, Machine "
            "Learning). The simulation is clearly labelled wherever it "
            "appears. Turn it off to analyze the public data only."
        ),
    )
    if st.session_state.get("include_user_incidents", False):
        from app.utils import db

        st.caption(
            f"Live-data simulation ON - {db.count_incidents()} manually "
            "added incident(s) are included in every analysis."
        )

pages = [
    st.Page("pages/1_overview.py", title="Overview", icon=":material/insights:"),
    st.Page("pages/2_crime_map.py", title="Crime Map", icon=":material/map:"),
    st.Page("pages/3_temporal.py", title="Temporal Analysis", icon=":material/schedule:"),
    st.Page("pages/4_statistical.py", title="Statistical Analysis", icon=":material/bar_chart:"),
    st.Page("pages/5_machine_learning.py", title="Machine Learning", icon=":material/model_training:"),
    st.Page("pages/6_add_incident.py", title="Add Incident", icon=":material/note_add:"),
    st.Page("pages/7_security.py", title="Security", icon=":material/security:"),
    st.Page("pages/8_methodology.py", title="Methodology & Limitations", icon=":material/description:"),
    st.Page("pages/9_audit_log.py", title="Audit Log (Admin)", icon=":material/description:"),
]

nav = st.navigation(pages)
nav.run()
