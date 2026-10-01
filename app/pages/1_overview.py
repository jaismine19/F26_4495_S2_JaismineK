import plotly.express as px
import streamlit as st

from app.utils.ui import require_data

st.title("Overview")
st.markdown(
    "Interactive analysis of publicly available Vancouver Police Department "
    "crime data (GeoDASH open data)."
)

df = require_data()
if df is None:
    st.stop()

st.markdown("### Key figures")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Reported incidents", f"{len(df):,}")
c2.metric("Years covered", f"{df['YEAR'].min()} - {df['YEAR'].max()}")
c3.metric("Crime types", df["TYPE"].nunique())
c4.metric("Neighbourhoods", df["NEIGHBOURHOOD"].nunique())

st.markdown(
    ":warning: No records for **2022** exist in the dataset; the VPD data "
    "pipeline for that year is being investigated and will be documented in "
    "the final report."
)

st.markdown("### Incidents by year")
by_year = df.groupby("YEAR").size().reset_index(name="incidents")
st.plotly_chart(
    px.bar(
        by_year,
        x="YEAR",
        y="incidents",
        title="Reported incidents per year",
        labels={"YEAR": "Year", "incidents": "Incidents"},
    ),
    use_container_width=True,
)

st.markdown("### Top crime types")
top_types = df["TYPE"].value_counts().head(11)
st.plotly_chart(
    px.bar(
        top_types,
        x=top_types.index,
        y=top_types.values,
        title="Incidents by crime type",
        labels={"x": "Crime type", "y": "Incidents"},
    ),
    use_container_width=True,
)
