"""Crime Map - neighbourhood intelligence (geospatial + ML).

Pipeline: filter -> privacy-safe aggregation (median in-bounds coordinates
per neighbourhood) -> k-means clustering of crime-type mixes -> interactive
pydeck map colored by archetype.

No raw incident coordinates are ever plotted (see docs/security/
privacy_and_data_protection.md).
"""
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from app.utils.clusters import (
    cluster_neighbourhoods,
    crime_mix,
    describe_clusters,
)
from app.utils.geo import aggregate_neighbourhoods
from app.utils.ui import require_data

CLUSTER_COLORS = [
    [228, 26, 28, 180],    # red
    [55, 126, 184, 180],   # blue
    [77, 175, 74, 180],    # green
    [255, 127, 0, 180],    # orange
]

st.title("Crime Map")
st.markdown(
    "Neighbourhood-level incident density, clustered by crime profile. "
    "Each circle is an entire neighbourhood (median location, aggregated "
    "counts) - never raw incident points."
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
        "Year range", min_value=min_year, max_value=max_year,
        value=(min_year, max_year),
    )
with f2:
    all_types = sorted(df["TYPE"].dropna().unique())
    selected_types = st.multiselect("Crime types", all_types, default=all_types)
with f3:
    k = st.select_slider("Number of archetypes (clusters)", options=[2, 3, 4, 5], value=4)

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

# Defensive: drop any neighbourhood that could not be clustered.
hoods = hoods.dropna(subset=["cluster"])
if hoods.empty:
    st.warning("Not enough valid neighbourhood data in this filter.")
    st.stop()

hoods["color"] = hoods["cluster"].map(
    lambda c: CLUSTER_COLORS[int(c) % len(CLUSTER_COLORS)]
)
hoods["radius"] = np.sqrt(hoods["incidents"]) * 35

st.caption(
    f"Showing {len(hoods)} neighbourhoods, {len(view):,} incidents "
    f"({year_range[0]}-{year_range[1]}, {len(selected_types)} crime types), "
    f"{n_clusters} archetypes."
)

# ---------------------------------------------------------------------- map
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
        tooltip={
            "html": (
                "<b>{neighbourhood}</b><br/>"
                "{incidents} incidents<br/>"
                "Top type: {top_type}<br/>"
                "Archetype: {archetype}"
            ),
            "style": {"backgroundColor": "steelblue", "color": "white"},
        },
    ),
    width="stretch",
)

# ------------------------------------------------------------- archetypes
st.markdown("### Neighbourhood archetypes (k-means on crime-type mix)")
summary = describe_clusters(
    result["labels"], clusters
) if len(mix) >= 2 else pd.DataFrame()
st.dataframe(summary, width="stretch", hide_index=True)

with st.expander("How this works"):
    st.markdown(
        "1. Each neighbourhood's crime mix is normalized (share of each of "
        "the 11 types).\n"
        "2. k-means groups neighbourhoods with similar mixes into archetypes.\n"
        "3. The map colors each neighbourhood by archetype; circle size is "
        "incident count; positions are median in-bounds UTM coordinates "
        "converted to lat/lon.\n"
        "4. Out-of-bounds coordinates are excluded as data-quality errors."
    )
st.caption(
    "Aggregated display only - no individual incident locations. See the "
    "Methodology & Limitations page for dataset caveats."
)
