"""Machine Learning - an honest baseline forecast of monthly incidents.

A simple, explainable model: the next months are forecast as the average of
the last N months. Accuracy is measured on the past 12 months so the page
can say exactly how wrong the model has been - and compare it against a
"same as last year" baseline.

This is pattern description, not prediction for policing (see Methodology).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils.forecast import train_evaluate
from app.utils.ui import require_data

st.title("Machine Learning")
st.markdown(
    "What might monthly incidents look like over the next year? A simple, "
    "**honest** forecast - with its past accuracy measured, so you know how "
    "much to trust it."
)

df = require_data()
if df is None:
    st.stop()

with st.expander("How this forecast works (in plain English)"):
    st.markdown(
        "- **The model:** the next months are predicted as the average of "
        "the last few months (a moving average).\n"
        "- **The check:** the model is tested on the past 12 months it was "
        "not allowed to see, and its error is measured (MAE = average miss "
        "in incidents per month; RMSE = miss that punishes big errors).\n"
        "- **The rival:** a 'same as last year' baseline that just repeats "
        "last year's months - if our model cannot beat that, we say so.\n"
        "- **The honesty:** the missing year 2022 is filled with zeros and "
        "shown in the chart, not hidden. Reported incidents are not all "
        "crime, and past patterns may not continue."
    )

# ------------------------------------------------------------------ filters
f1, f2 = st.columns(2)
with f1:
    all_types = sorted(df["TYPE"].dropna().unique())
    crime_type = st.selectbox(
        "Crime type",
        ["All types"] + all_types,
        help="Forecast all incidents together, or one crime type.",
    )
with f2:
    window = st.select_slider(
        "Averaging window (months)",
        options=[3, 6, 12, 24],
        value=12,
        help="How many past months should the average use? Longer = smoother, shorter = reacts faster.",
    )

type_arg = None if crime_type == "All types" else crime_type
result = train_evaluate(df, crime_type=type_arg, test_months=12, window=window)

if result is None:
    st.warning("Not enough history for this selection to build a forecast.")
    st.stop()

# ------------------------------------------------------------------ metrics
st.markdown("### How accurate was it?")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average monthly incidents (model)", f"{result['future'].mean():,.0f}")
c2.metric("Past error (MAE)", f"±{result['mae_mv']:,.0f} / month")
c3.metric("Past error (RMSE)", f"±{result['rmse_mv']:,.0f} / month")
c4.metric(
    "vs 'same as last year'",
    "Better" if result["better_than_naive"] else "Worse",
    delta=f"{result['mae_naive'] - result['mae_mv']:+,.0f} MAE",
    delta_color="normal" if result["better_than_naive"] else "inverse",
)

st.caption(
    "MAE = how far off the model was per month on the past 12 months, on "
    "average. RMSE penalizes big misses more. Missing 2022 is filled with "
    "zeros."
)

# ------------------------------------------------------------------- chart
st.markdown("### Reported incidents and the forecast")
ts = result["series"]

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=ts.index, y=ts.values, name="Reported incidents",
        mode="lines", line=dict(color="#377eb8", width=1.5),
    )
)
fig.add_trace(
    go.Scatter(
        x=result["future_index"], y=result["future"],
        name=f"Moving-average forecast (last {window} months)",
        mode="lines", line=dict(color="#e41a1c", width=2, dash="dash"),
    )
)
fig.add_trace(
    go.Scatter(
        x=result["future_index"], y=result["future_naive"],
        name="Same-as-last-year baseline",
        mode="lines", line=dict(color="#999999", width=1.5, dash="dot"),
    )
)
fig.update_layout(
    title=f"{crime_type} - monthly incidents and 12-month forecast",
    xaxis_title=None, yaxis_title="Incidents per month",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=420,
)
st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------- plain-English
level = result["future"].mean()
st.markdown("### What this says")
if result["better_than_naive"]:
    verdict = (
        f"On the past 12 months, the moving average was off by "
        f"**{result['mae_mv']:,.0f}** incidents per month on average - "
        f"**{result['mae_naive'] - result['mae_mv']:,.0f} per month better** "
        f"than simply repeating last year."
    )
else:
    verdict = (
        f"On the past 12 months, the moving average was off by "
        f"**{result['mae_mv']:,.0f}** incidents per month on average - "
        f"about the same as (or worse than) the same-as-last-year baseline, "
        f"which is worth saying out loud."
    )
st.markdown(
    f"- For **{crime_type.lower()}**, the model expects about "
    f"**{level:,.0f}** incidents per month over the next 12 months.\n"
    f"- {verdict}\n"
    f"- The dip at 2022 is the missing year in the VPD source, shown as "
    f"zero rather than hidden."
)

st.caption(
    "This is a baseline description of reported incident patterns - not a "
    "prediction of future crime, and not used for any policing decision. "
    "See the Methodology & Limitations page."
)
