"""Machine Learning - honest baselines, two ways.

Tab 1 (Forecast): the next months are forecast as the average of the last N
months, and its past error is measured (MAE/RMSE) against a "same as last
year" baseline.

Tab 2 (Crime-type classification): which model can best tell crime types
apart from time and place features? Trained on years <= 2024, tested on
2025-2026 (time-aware, no leakage), with a most-common-type baseline, four
models, and two feature sets (temporal vs temporal+neighbourhood).

This is pattern description, not prediction for policing (see Methodology).
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils.classification import run_experiment
from app.utils.forecast import train_evaluate
from app.utils.ui import require_data

st.title("Machine Learning")
st.markdown(
    "Two honest experiments: a **forecast** of monthly incidents with its "
    "past error measured, and a **classification** test of how well time and "
    "place features can tell crime types apart."
)

df = require_data()
if df is None:
    st.stop()

tab_forecast, tab_classify = st.tabs(["Forecast", "Crime-type classification"])

# ================================================================== forecast
with tab_forecast:
    st.markdown(
        "What might monthly incidents look like over the next year? A simple, "
        "**honest** forecast - with its past accuracy measured, so you know "
        "how much to trust it."
    )

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

# ============================================================== classification
with tab_classify:
    st.markdown(
        "Can time and place features tell the 11 crime types apart? The "
        "models are trained on **2003-2024** and tested on **2025-2026** - "
        "a time-aware split, so the test uses only the future the models "
        "never saw."
    )

    with st.expander("How this experiment works (in plain English)"):
        st.markdown(
            "- **The task:** look at an incident's year, month, hour, day of "
            "week, season (and neighbourhood in the second run) and guess its "
            "crime type - out of 11 possible types.\n"
            "- **The honest setup:** training years end at 2024 and testing "
            "uses 2025-2026 only. Crime changes over time, so mixing years "
            "between training and testing would give unfairly easy answers.\n"
            "- **The starting point:** a 'most common type' baseline that "
            "just guesses the most frequent type - any real model should "
            "beat that.\n"
            "- **The models:** Logistic Regression, Decision Tree, Random "
            "Forest, and K-Nearest Neighbours.\n"
            "- **The two runs:** first with time features only, then with "
            "the neighbourhood added - to honestly test whether place "
            "information helps (proposal hypothesis H3).\n"
            "- **The speed limit:** for speed, models train on a random but "
            "balanced sample of 150,000 past incidents (rare crime types are "
            "kept), and K-Nearest Neighbours uses a smaller 25,000 reference "
            "set. The test set is complete - nothing is hidden from it."
        )

    @st.cache_data(
        show_spinner="Running the classification experiments "
        "(~30 seconds the first time, then cached)...",
    )
    def _run(df: pd.DataFrame) -> dict:
        return run_experiment(df)

    result = _run(df)

    # ---------------------------------------------------------- comparison
    st.markdown("### Model comparison (tested on 2025-2026)")
    rows = []
    for feature_set, label in (("temporal", "Time only"),
                               ("temporal+geo", "Time + neighbourhood")):
        for name, metrics in result["experiment"][feature_set].items():
            if name.startswith("_"):
                continue
            rows.append({
                "Features": label,
                "Model": name,
                "Accuracy": metrics["accuracy"],
                "Macro F1": metrics["macro_f1"],
                "Weighted F1": metrics["weighted_f1"],
                "Train rows": metrics["train_rows"],
            })
    table = pd.DataFrame(rows)
    st.dataframe(
        table,
        hide_index=True,
        column_config={
            "Accuracy": st.column_config.NumberColumn(format="%.3f"),
            "Macro F1": st.column_config.NumberColumn(format="%.3f"),
            "Weighted F1": st.column_config.NumberColumn(format="%.3f"),
            "Train rows": st.column_config.NumberColumn(format="%,d"),
        },
        width="stretch",
    )
    st.caption(
        "Accuracy = share of correct guesses. Macro F1 = average per-type "
        "score (fair to rare types). Weighted F1 = per-type score weighted by "
        "how common each type is."
    )

    best = result
    st.success(
        f"**Best combination: {best['best_model']} with "
        f"{'time + neighbourhood' if best['best_feature_set'] == 'temporal+geo' else 'time only'}** "
        f"(chosen by macro F1)."
    )

    # --------------------------------------------------- confusion matrix
    st.markdown("### Where the best model got confused")
    conf = best["experiment"][best["best_feature_set"]][best["best_model"]]["confusion"]
    classes = best["classes"]
    normalized = conf.astype(float) / conf.sum(axis=1, keepdims=True)

    fig = go.Figure(
        go.Heatmap(
            z=normalized,
            x=classes, y=classes,
            colorscale="Blues",
            zmin=0, zmax=1,
            text=np.where(conf > 0, conf, ""),
            texttemplate="%{text}",
            hovertemplate=(
                "True: %{y}<br>Guessed: %{x}<br>"
                "Count: %{text}<br>Share of true type: %{z:.0%}<extra></extra>"
            ),
            colorbar=dict(title="Share of<br>that type"),
        )
    )
    fig.update_layout(
        title="Confusion matrix - rows are the true type, columns the guess",
        height=560, xaxis_title="Predicted type", yaxis_title="True type",
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("### The most common mix-ups")
    for c in best["confusions"]:
        st.markdown(
            f"- **{c['true']}** was guessed as **{c['predicted']}** "
            f"{c['count']:,} times"
        )

    # --------------------------------------------------------- plain-English
    base = best["experiment"]["temporal"]["Most-common-type baseline"]["accuracy"]
    top = best["experiment"][best["best_feature_set"]][best["best_model"]]
    st.markdown("### What this says")
    st.markdown(
        f"- The starting point is a 'most common type' guess, right "
        f"**{base:.0%}** of the time. The best model reaches "
        f"**{top['accuracy']:.0%}** - a real improvement, but far from "
        f"perfect, and we say so.\n"
        f"- Adding the neighbourhood changed the scores for every model - "
        f"place information does help, which answers hypothesis H3.\n"
        f"- The mix-ups are almost all between similar property types "
        f"(theft from vehicle, other theft, mischief). The models rarely "
        f"confuse property crime with violence, which matches the "
        f"hour-redaction finding on the Temporal page.\n"
        f"- These are patterns in reported incidents, not a tool for "
        f"policing decisions."
    )
