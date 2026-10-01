"""Vancouver Urban Safety Intelligence Platform - main entry point.

Run from the repository root:
    streamlit run app/Home.py
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

pages = [
    st.Page("pages/1_overview.py", title="Overview", icon=":material/insights:"),
    st.Page("pages/2_crime_map.py", title="Crime Map", icon=":material/map:"),
    st.Page("pages/3_temporal.py", title="Temporal Analysis", icon=":material/schedule:"),
    st.Page("pages/4_statistical.py", title="Statistical Analysis", icon=":material/bar_chart:"),
    st.Page("pages/5_machine_learning.py", title="Machine Learning", icon=":material/model_training:"),
    st.Page("pages/6_add_incident.py", title="Add Incident", icon=":material/note_add:"),
    st.Page("pages/7_security.py", title="Security", icon=":material/security:"),
    st.Page("pages/8_methodology.py", title="Methodology & Limitations", icon=":material/description:"),
]

nav = st.navigation(pages)
nav.run()

with st.sidebar:
    st.caption("CSIS 4495 - Research Prototype")
    st.caption("Not an official crime-reporting system.")
