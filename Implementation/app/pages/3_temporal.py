"""Temporal Analysis - patterns in crime by time of day, week, and season.

Phase: Oct 7-12 (initial implementation)
Owner: Jaismine Kaur (Data Analytics workstream)
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from app.utils.ui import require_data

DAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]

st.title("Temporal Analysis")
st.markdown(
    "How reported incidents vary by hour, day of week, month, and season. "
    "Filters apply to all charts on this page."
)

df = require_data()
if df is None:
    st.stop()

# ---------------------------------------------------------------- filters
st.markdown("### Filters")
f1, f2, f3 = st.columns(3)

with f1:
    min_year, max_year = int(df["YEAR"].min()), int(df["YEAR"].max())
    year_range = st.slider(
        "Year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

with f2:
    all_types = sorted(df["TYPE"].dropna().unique())
    selected_types = st.multiselect(
        "Crime types",
        options=all_types,
        default=all_types,
    )

with f3:
    all_hoods = sorted(df["NEIGHBOURHOOD"].dropna().unique())
    selected_hoods = st.multiselect(
        "Neighbourhoods",
        options=all_hoods,
        default=all_hoods,
    )

mask = (
    df["YEAR"].between(*year_range)
    & df["TYPE"].isin(selected_types)
    & df["NEIGHBOURHOOD"].isin(selected_hoods)
)
view = df.loc[mask]

if view.empty:
    st.warning("No incidents match the selected filters.")
    st.stop()

st.caption(
    f"Showing {len(view):,} incidents "
    f"({year_range[0]}-{year_range[1]}, {len(selected_types)} crime types, "
    f"{len(selected_hoods)} neighbourhoods)."
)

# ---------------------------------------------------------------- peak hours
st.markdown("### Incidents by hour of day")
hour_counts = view["HOUR"].value_counts().sort_index().reset_index()
hour_counts.columns = ["hour", "incidents"]
peak_hour = int(hour_counts.loc[hour_counts["incidents"].idxmax(), "hour"])

st.plotly_chart(
    px.bar(
        hour_counts,
        x="hour",
        y="incidents",
        title=f"Incidents by hour of day (peak: {peak_hour:02d}:00)",
        labels={"hour": "Hour of day", "incidents": "Incidents"},
    ),
    width="stretch",
)

# ---------------------------------------------------------- day of week
st.markdown("### Incidents by day of week")
dow_counts = (
    view["DAY_OF_WEEK"].value_counts().reindex(DAY_ORDER).reset_index()
)
dow_counts.columns = ["day_of_week", "incidents"]
busiest_day = dow_counts.loc[dow_counts["incidents"].idxmax(), "day_of_week"]

st.plotly_chart(
    px.bar(
        dow_counts,
        x="day_of_week",
        y="incidents",
        title=f"Incidents by day of week (busiest: {busiest_day})",
        labels={"day_of_week": "Day of week", "incidents": "Incidents"},
    ),
    width="stretch",
)

# ---------------------------------------------------------------- month
st.markdown("### Incidents by month")
month_counts = (
    view.groupby("MONTH")
    .size()
    .reset_index(name="incidents")
    .assign(
        month_name=lambda d: d["MONTH"].map(
            {i + 1: name for i, name in enumerate(MONTH_ORDER)}
        )
    )
)

st.plotly_chart(
    px.bar(
        month_counts,
        x="month_name",
        y="incidents",
        category_orders={"month_name": MONTH_ORDER},
        title="Incidents by month (all years combined)",
        labels={"month_name": "Month", "incidents": "Incidents"},
    ),
    width="stretch",
)

# ------------------------------------------------------ year x month heatmap
st.markdown("### Year × month heatmap")
heat = (
    view.groupby(["YEAR", "MONTH"])
    .size()
    .reset_index(name="incidents")
    .pivot(index="YEAR", columns="MONTH", values="incidents")
    .reindex(columns=range(1, 13))
    .rename(columns={i + 1: name for i, name in enumerate(MONTH_ORDER)})
)

st.plotly_chart(
    px.imshow(
        heat,
        title="Incidents per year and month (blank = missing 2022 / filtered out)",
        labels=dict(x="Month", y="Year", color="Incidents"),
        aspect="auto",
    ),
    width="stretch",
)

# ---------------------------------------------------------------- season
st.markdown("### Incidents by season")
season_counts = (
    view["SEASON"].value_counts().reindex(SEASON_ORDER).reset_index()
)
season_counts.columns = ["season", "incidents"]

st.plotly_chart(
    px.pie(
        season_counts,
        names="season",
        values="incidents",
        title="Share of incidents by season",
        category_orders={"season": SEASON_ORDER},
    ),
    width="stretch",
)

# ---------------------------------------------------------------- insights
st.markdown("### Automatic insights")
weekend_mask = view["DAY_OF_WEEK"].isin(["Saturday", "Sunday"])
weekend_share = weekend_mask.mean() * 100
night_mask = view["HOUR"].isin(range(0, 6))
night_share = night_mask.mean() * 100
weekly = view.groupby("DAY_OF_WEEK").size()
weekend_avg = weekly[weekly.index.isin(["Saturday", "Sunday"])].mean()
weekday_avg = weekly[weekly.index.isin(DAY_ORDER[:5])].mean()

st.markdown(
    f"- **{weekend_share:.1f}%** of filtered incidents occurred on weekends.\n"
    f"- Weekend days average **{weekend_avg:,.0f}** incidents vs "
    f"**{weekday_avg:,.0f}** on weekdays.\n"
    f"- **{night_share:.1f}%** of filtered incidents occurred between "
    f"midnight and 6 AM.\n"
    f"- The busiest hour is **{peak_hour:02d}:00** and the busiest day is "
    f"**{busiest_day}**."
)
st.caption(
    "Insights describe patterns in *reported* incidents and do not explain "
    "causes. See the Methodology & Limitations page."
)
