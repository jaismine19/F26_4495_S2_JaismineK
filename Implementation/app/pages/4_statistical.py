"""Statistical Analysis - hypothesis tests and descriptive statistics.

Phase: Oct 13-20 (analytics & security)
Owner: Jaismine Kaur (Data Analytics workstream)

Tests are computed with scipy (see app/utils/stats.py) and every test is
shown with its p-value and a plain-English interpretation.
"""
import plotly.express as px
import streamlit as st

from app.utils.stats import (
    VIOLENT_TYPES,
    chi_square_test,
    interpret_p,
    summary_stats,
)
from app.utils.ui import require_data

st.title("Statistical Analysis")
st.markdown(
    "Descriptive statistics and chi-square tests of independence on the "
    "cleaned VPD dataset. Filters below apply to every section."
)

df = require_data()
if df is None:
    st.stop()

# ------------------------------------------------------------------ filters
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
    selected_types = st.multiselect("Crime types", all_types, default=all_types)
with f3:
    all_hoods = sorted(df["NEIGHBOURHOOD"].dropna().unique())
    selected_hoods = st.multiselect("Neighbourhoods", all_hoods, default=all_hoods)

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
    f"Testing {len(view):,} incidents ({year_range[0]}-{year_range[1]}, "
    f"{len(selected_types)} crime types, {len(selected_hoods)} neighbourhoods)."
)

# ------------------------------------------------------- descriptive stats
st.markdown("### Descriptive statistics")
s = summary_stats(view)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Incidents", f"{s['incidents']:,}")
c2.metric("Avg per day", f"{s['mean_per_day']:.0f}")
c3.metric("Top crime type", s["top_type"])
c4.metric("Share of total", f"{s['top_type_share']:.1f}%")
c5.metric("Peak hour", f"{s['peak_hour']:02d}:00" if s["peak_hour"] is not None else "n/a")

with st.expander("Incidents per crime type (share of total)"):
    shares = view["TYPE"].value_counts(normalize=True) * 100
    st.dataframe(shares.round(1).rename("share %").to_frame(), width="stretch")

st.info(
    "Peak hour excludes Homicide and Offence Against a Person: VPD redacts "
    "the timestamps of violent incidents (always hour = 0)."
)

# ------------------------------------------------------- test 1: type x season
st.markdown("### Test 1 - Is crime type related to season?")
t1 = chi_square_test(view, "TYPE", "SEASON")
st.markdown(
    f"- Chi-square statistic: **{t1['chi2']:,.1f}** (df = {t1['dof']})\n"
    f"- p-value: **{t1['p']:.3g}**\n"
    f"- Interpretation: **{interpret_p(t1['p'])}**"
)
with st.expander("Observed vs expected table (rows = crime type)"):
    st.markdown("Observed counts:")
    st.dataframe(t1["observed"], width="stretch")
    st.markdown("Expected counts if independent:")
    st.dataframe(t1["expected"].round(1), width="stretch")

st.plotly_chart(
    px.imshow(
        t1["observed"].div(t1["observed"].sum(axis=1), axis=0),
        title="Season share per crime type",
        labels=dict(color="Share of type"),
        aspect="auto",
    ),
    width="stretch",
)

# --------------------------------------------------- test 2: type x day of week
st.markdown("### Test 2 - Is crime type related to day of week?")
t2 = chi_square_test(view, "TYPE", "DAY_OF_WEEK")
st.markdown(
    f"- Chi-square statistic: **{t2['chi2']:,.1f}** (df = {t2['dof']})\n"
    f"- p-value: **{t2['p']:.3g}**\n"
    f"- Interpretation: **{interpret_p(t2['p'])}**"
)
with st.expander("Observed vs expected table (rows = crime type)"):
    st.markdown("Observed counts:")
    st.dataframe(t2["observed"], width="stretch")
    st.markdown("Expected counts if independent:")
    st.dataframe(t2["expected"].round(1), width="stretch")

# ------------------------------------------------------------- prior findings
st.markdown("### Findings carried over from the analysis notebooks")
with st.expander("The five documented findings"):
    st.markdown(
        "- **Data forensics:** violent-crime timestamps are redacted by VPD "
        "(hour = 0) - hour analysis must exclude Homicide and Offence Against "
        "a Person.\n"
        "- **Every crime has its own clock:** Commercial Break & Enter is ~49% "
        "nocturnal; Other Theft is ~58% daytime; collisions peak at 17:00.\n"
        "- **The pandemic reshaped the mix:** 2020 street crimes fell 38-43% "
        "while Commercial Break & Enter rose 12%; by 2023 Other Theft was +50% "
        "vs 2021.\n"
        "- **Rejected hypothesis:** Theft from Vehicle shows no seasonality "
        "(flat 24-26% across seasons).\n"
        "- **Neighbourhood divergence:** 21/24 neighbourhoods improved "
        "2019-2023; only Musqueam, Renfrew-Collingwood, and Sunset increased."
    )

st.caption(
    "Tests describe patterns in *reported* incidents and do not explain "
    "causes. Missing year 2022 affects multi-year comparisons. See the "
    "Methodology & Limitations page."
)
