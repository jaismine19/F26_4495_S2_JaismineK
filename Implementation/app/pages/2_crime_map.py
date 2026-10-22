"""Crime Map - neighbourhood intelligence (geospatial + ML).

Pipeline: filter -> privacy-safe aggregation (median in-bounds coordinates
per neighbourhood) -> k-means clustering of crime-type mixes -> interactive
pydeck map colored by archetype.

Design for usability: the legend (color = archetype) sits right above the
map, all controls live in the sidebar, and archetype details are one expander.
"""
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from app.utils.clusters import (
    cluster_neighbourhoods,
    crime_mix,
)
from app.utils.geo import aggregate_neighbourhoods
from app.utils.ui import require_data

CLUSTER_COLORS = [
    [228, 26, 28, 180],    # red
    [55, 126, 184, 180],   # blue
    [77, 175, 74, 180],    # green
    [255, 127, 0, 180],    # orange
    [128, 0, 128, 180],    # purple
]
CLUSTER_EMOJI = ["🟥", "🟦", "🟩", "🟧", "🟪"]

st.title("Crime Map")
st.markdown(
    "Each circle is one neighbourhood (median location, aggregated counts - "
    "never raw incident points). Colors are **archetypes** found by k-means "
    "clustering on each neighbourhood's crime mix."
)

df = require_data()
if df is None:
    st.stop()

# ------------------------------------------------------------ sidebar filters
with st.sidebar:
    st.markdown("### Map filters")
    min_year, max_year = int(df["YEAR"].min()), int(df["YEAR"].max())
    year_range = st.slider(
        "Year range", min_value=min_year, max_value=max_year,
        value=(min_year, max_year),
    )
    all_types = sorted(df["TYPE"].dropna().unique())
    selected_types = st.multiselect("Crime types", all_types, default=all_types)
    k = st.select_slider(
        "Number of archetypes", options=[2, 3, 4, 5], value=4,
        help="How many neighbourhood groups should k-means look for?",
    )

mask = (
    df["YEAR"].between(*year_range)
    & df["TYPE"].isin(selected_types)
)
view = df.loc[mask]

if view.empty:
    st.warning("No incidents match the selected filters.")
    st.stop()

# ------------------------------------------------------- aggregate + cluster
hoods = aggregate_neighbourhoods(view)
if len(hoods) < 2:
    st.warning("Too few neighbourhoods in this filter to build the map.")
    st.stop()

mix = crime_mix(view)
n_clusters = min(k, len(mix))
if len(mix) >= 2:
    result = cluster_neighbourhoods(mix, k=n_clusters)
    hoods = hoods.merge(result["labels"], on="neighbourhood", how="left")
    clusters = result["clusters"]
else:
    hoods["cluster"] = 0
    hoods["archetype"] = "all"
    clusters = {0: {"name": "all", "top_types": []}}

hoods = hoods.dropna(subset=["cluster"])
if hoods.empty:
    st.warning("Not enough valid neighbourhood data in this filter.")
    st.stop()

hoods["color"] = hoods["cluster"].map(
    lambda c: CLUSTER_COLORS[int(c) % len(CLUSTER_COLORS)]
)
hoods["radius"] = np.sqrt(hoods["incidents"]) * 35
hoods["incidents_fmt"] = hoods["incidents"].map(lambda v: f"{v:,}")

st.caption(
    f"{len(hoods)} neighbourhoods, {len(view):,} incidents "
    f"({year_range[0]}-{year_range[1]}, {len(selected_types)} crime types), "
    f"{n_clusters} archetypes."
)

# -------------------------------------------------------------------- legend
st.markdown("### Color legend - each archetype is one color")
legend_cols = st.columns(n_clusters)
for i, (c, info) in enumerate(clusters.items()):
    emoji = CLUSTER_EMOJI[int(c) % len(CLUSTER_EMOJI)]
    legend_cols[i].markdown(
        f"{emoji} **{info['name']}**  \n"
        f"<small>{info['signature']}</small>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------- map
st.markdown("### Interactive map")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=hoods,
    get_position=["lon", "lat"],
    get_radius="radius",
    get_fill_color="color",
    pickable=True,
    radius_min_pixels=4,
    radius_max_pixels=70,
)
view_state = pdk.ViewState(latitude=49.26, longitude=-123.12, zoom=10.6)
st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="light",
        tooltip={
            "html": (
                "<div style='font-family:-apple-system, Segoe UI, Roboto, "
                "sans-serif; padding:4px 8px; min-width:180px;'>"
                "<b style='font-size:13px;'>{neighbourhood}</b><br/>"
                "<span style='font-size:12px; color:#444444;'>{incidents_fmt} "
                "incidents</span><br/>"
                "<span style='font-size:12px; color:#444444;'>Top type: "
                "{top_type}</span><br/>"
                "<span style='font-size:12px; color:#1a1a1a;'>"
                "<b>{archetype}</b></span>"
                "</div>"
            ),
            "style": {
                "backgroundColor": "white",
                "color": "#1a1a1a",
                "borderRadius": "6px",
                "boxShadow": "0 1px 6px rgba(0,0,0,0.25)",
                "fontSize": "12px",
            },
        },
    ),
    width="stretch",
)
st.caption(
    "How to read it: circle size = number of incidents. Hover any circle for "
    "its neighbourhood, top crime type, and archetype group. Colors match the "
    "legend above."
)

# ------------------------------------------------------- archetype details
with st.expander("What is in each archetype?"):
    for c, info in clusters.items():
        emoji = CLUSTER_EMOJI[int(c) % len(CLUSTER_EMOJI)]
        members = sorted(
            hoods.loc[hoods["cluster"] == c, "neighbourhood"].tolist()
        )
        st.markdown(
            f"{emoji} **{info['name']} - {info['signature']}** "
            f"({len(members)} neighbourhoods): "
            f"*{', '.join(members)}*"
        )

with st.expander("How this page works"):
    st.markdown(
        "1. Each neighbourhood's crime mix is normalized (share of each of "
        "the 11 types).\n"
        "2. k-means groups neighbourhoods with similar mixes into archetypes "
        "(set the number in the sidebar).\n"
        "3. The map colors each neighbourhood by archetype; circle size is "
        "incident count; positions are median in-bounds UTM coordinates "
        "converted to lat/lon.\n"
        "4. Out-of-bounds coordinates are excluded as data-quality errors."
    )
st.caption(
    "Aggregated display only - no individual incident locations. See the "
    "Methodology & Limitations page for dataset caveats."
)
