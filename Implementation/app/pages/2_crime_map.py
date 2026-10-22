"""Crime Map - neighbourhood intelligence (geospatial + ML).

Pipeline: filter -> privacy-safe aggregation (median in-bounds coordinates
per neighbourhood) -> k-means clustering of crime-type mixes -> interactive
pydeck map colored by archetype.

Interactivity: hover any circle for a quick tooltip, or click it to
highlight it and see a full detail card (rank, top types, crime mix chart).
"""
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from app.utils.clusters import cluster_neighbourhoods, crime_mix
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
if len(mix) >= 2:
    result = cluster_neighbourhoods(mix, k=k)
    hoods = hoods.merge(result["labels"], on="neighbourhood", how="left")
    clusters = result["clusters"]
else:
    hoods["cluster"] = 0
    hoods["archetype"] = "Group 1 - Mixed"
    clusters = {0: {"name": "Group 1", "top_types": ["Mixed"], "signature": "Mixed"}}

hoods = hoods.dropna(subset=["cluster"])
n_clusters = len(clusters)
if hoods.empty:
    st.warning("Not enough valid neighbourhood data in this filter.")
    st.stop()

# ------------------------------------------------------- spotlight picker
hood_names = sorted(hoods["neighbourhood"].tolist())


def _set_spotlight() -> None:
    picked = st.session_state.get("spotlight_picker", "(none)")
    st.session_state["spotlight"] = None if picked == "(none)" else picked


with st.sidebar:
    st.markdown("### Spotlight")
    current = st.session_state.get("spotlight")
    default_idx = hood_names.index(current) + 1 if current in hood_names else 0
    st.selectbox(
        "Neighbourhood",
        ["(none)"] + hood_names,
        index=default_idx,
        key="spotlight_picker",
        on_change=_set_spotlight,
        help="Highlight a neighbourhood on the map and see its full profile.",
    )

max_incidents = float(hoods["incidents"].max())
hoods["radius"] = (
    60.0 + np.sqrt(hoods["incidents"]) / np.sqrt(max_incidents) * 3000.0
)
hoods["color"] = hoods["cluster"].map(
    lambda c: CLUSTER_COLORS[int(c) % len(CLUSTER_COLORS)]
)
hoods["incidents_fmt"] = hoods["incidents"].map(lambda v: f"{v:,}")
hoods["rank"] = hoods["incidents"].rank(ascending=False, method="min").astype(int)

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

base_layer = pdk.Layer(
    "ScatterplotLayer",
    data=hoods,
    get_position=["lon", "lat"],
    get_radius="radius",
    get_fill_color="color",
    get_line_color=[255, 255, 255, 200],
    line_width_min_pixels=1,
    stroked=True,
    pickable=True,
    radius_min_pixels=8,
    radius_max_pixels=45,
)

# The picked neighbourhood drives the highlight layer and the profile card.
selected_name = st.session_state.get("spotlight")

layers = [base_layer]
if selected_name and selected_name in set(hoods["neighbourhood"]):
    sel_df = hoods.loc[hoods["neighbourhood"] == selected_name].copy()
    sel_df["radius"] = sel_df["radius"] * 1.8
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=sel_df,
            get_position=["lon", "lat"],
            get_radius="radius",
            get_fill_color=[255, 255, 255, 40],
            get_line_color=[0, 0, 0, 255],
            line_width_min_pixels=2,
            stroked=True,
            pickable=False,
            radius_min_pixels=12,
            radius_max_pixels=70,
        )
    )

view_state = pdk.ViewState(latitude=49.26, longitude=-123.12, zoom=10.6)

st.pydeck_chart(
    pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="light",
        tooltip={
            "html": (
                "<div style='font-family:-apple-system, Segoe UI, Roboto, "
                "sans-serif; padding:4px 8px; min-width:170px;'>"
                "<b style='font-size:13px;'>{neighbourhood}</b><br/>"
                "<span style='font-size:12px; color:#444444;'>{incidents_fmt} "
                "incidents</span><br/>"
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
    "Hover any circle for a quick summary. Pick a neighbourhood in the "
    "sidebar (or above) to highlight it and see its full profile below."
)

# -------------------------------------------------------------- detail card
if selected_name and selected_name in set(hoods["neighbourhood"]):
    st.markdown("### Neighbourhood spotlight")
    row = hoods.loc[hoods["neighbourhood"] == selected_name].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Incidents", row["incidents_fmt"])
    c2.metric("Rank by volume", f"#{int(row['rank'])} of {len(hoods)}")
    c3.metric("Top crime type", row["top_type"])
    c4.metric("Archetype", row["archetype"])

    st.markdown(f"**{selected_name}** - crime mix (share of its incidents)")
    hood_mix = mix.loc[selected_name].sort_values(ascending=False) * 100
    st.bar_chart(hood_mix, horizontal=True, x_label="share of incidents (%)")
else:
    st.info("Tip: pick a neighbourhood from the sidebar Spotlight picker to "
            "see its full profile here.")

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
