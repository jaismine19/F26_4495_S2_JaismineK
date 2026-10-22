"""Crime Map - a plain-English explorer of Vancouver neighbourhood crime.

Designed for anyone, not just analysts:
- big-picture stats up top,
- an interactive folium map where circles = neighbourhoods (native hover
  tooltips + click-to-spotlight),
- a "spotlight" with an automatically written summary of any neighbourhood,
- and a full details table below.

Pipeline: filter -> privacy-safe aggregation (median in-bounds coordinates
per neighbourhood) -> k-means clustering of crime-type mixes -> folium map.
"""
import numpy as np
import pandas as pd
import streamlit as st

import folium
from streamlit_folium import st_folium

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
CLUSTER_HEX = ["#e41a1c", "#377eb8", "#4daf4a", "#ff7f00", "#800080"]
CLUSTER_EMOJI = ["🟥", "🟦", "🟩", "🟧", "🟪"]

st.title("Crime Map")
st.markdown(
    "Explore reported crime across Vancouver's 24 neighbourhoods. Each "
    "circle is one neighbourhood - **the bigger the circle, the more "
    "incidents**. Colors group neighbourhoods whose **crime patterns look "
    "similar**."
)

with st.expander("How to use this page (and what the words mean)"):
    st.markdown(
        "- **Incident** - one crime reported to and recorded by the Vancouver "
        "Police Department.\n"
        "- **Hover** any circle for a quick summary.\n"
        "- **Spotlight menu** (left sidebar) - pick a neighbourhood to see "
        "its full story below the map.\n"
        "- **Color groups (archetypes)** - neighbourhoods are automatically "
        "grouped by how similar their mix of crime types is. Same color = "
        "similar pattern.\n"
        "- This page shows neighbourhood-level summaries only - never exact "
        "crime locations."
    )

df = require_data()
if df is None:
    st.stop()

# ------------------------------------------------------------ sidebar controls
with st.sidebar:
    st.markdown("### Filters")
    min_year, max_year = int(df["YEAR"].min()), int(df["YEAR"].max())
    year_range = st.slider(
        "Year range", min_value=min_year, max_value=max_year,
        value=(min_year, max_year),
    )
    all_types = sorted(df["TYPE"].dropna().unique())
    selected_types = st.multiselect("Crime types", all_types, default=all_types)
    k = st.select_slider(
        "Number of color groups", options=[2, 3, 4, 5], value=4,
        help="How many crime-pattern groups should the map show?",
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
        help="Pick a neighbourhood to see its full profile below the map.",
    )

# --------------------------------------------------------------- map prep
max_incidents = float(hoods["incidents"].max())
hoods["marker_radius"] = (
    5.0 + np.sqrt(hoods["incidents"]) / np.sqrt(max_incidents) * 15.0
)
hoods["incidents_fmt"] = hoods["incidents"].map(lambda v: f"{v:,}")
hoods["rank"] = hoods["incidents"].rank(ascending=False, method="min").astype(int)

# ------------------------------------------------------- big picture stats
busiest = hoods.loc[hoods["incidents"].idxmax()]
common_type = view["TYPE"].mode().iloc[0]

st.markdown("### The big picture")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Reported incidents", f"{len(view):,}")
c2.metric("Neighbourhoods", len(hoods))
c3.metric("Busiest neighbourhood", busiest["neighbourhood"])
c4.metric("Most common type", common_type)
st.caption(
    f"Showing {year_range[0]}-{year_range[1]} with {len(selected_types)} "
    f"crime types selected."
)

# ------------------------------------------------------------------- legend
st.markdown("### What the colors mean")
legend_cols = st.columns(n_clusters)
for i, (c, info) in enumerate(clusters.items()):
    emoji = CLUSTER_EMOJI[int(c) % len(CLUSTER_EMOJI)]
    legend_cols[i].markdown(
        f"{emoji} **{info['name']}**  \n"
        f"<small>{info['signature']}</small>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------- map
selected_name = st.session_state.get("spotlight")

m = folium.Map(
    location=[49.26, -123.12],
    zoom_start=11,
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Street_Map/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri",
    control_scale=True,
)

for _, hood in hoods.iterrows():
    color = CLUSTER_HEX[int(hood["cluster"]) % len(CLUSTER_HEX)]
    is_selected = hood["neighbourhood"] == selected_name
    folium.CircleMarker(
        location=[hood["lat"], hood["lon"]],
        radius=float(hood["marker_radius"] * (1.35 if is_selected else 1.0)),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        weight=3 if is_selected else 1.5,
        tooltip=folium.Tooltip(
            (
                f"<b>{hood['neighbourhood']}</b><br>"
                f"{hood['incidents_fmt']} incidents<br>"
                f"{hood['archetype']}"
            ),
            sticky=True,
        ),
        popup=folium.Popup(
            (
                f"<b>{hood['neighbourhood']}</b><br>"
                f"{hood['incidents_fmt']} incidents<br>"
                f"Most common: {hood['top_type']}<br>"
                f"{hood['archetype']}"
            ),
            max_width=260,
        ),
    ).add_to(m)

map_result = st_folium(m, height=520, width="stretch", key="crime_map_folium")

# A map click returns coordinates: match them to the nearest neighbourhood
# and turn it into the spotlight pick.
clicked = (map_result or {}).get("last_object_clicked") if isinstance(map_result, dict) else None
if clicked and isinstance(clicked, dict):
    clat, clng = clicked.get("lat"), clicked.get("lng")
    if clat is not None and clng is not None:
        hoods["dist"] = np.hypot(hoods["lat"] - clat, hoods["lon"] - clng)
        best = hoods.loc[hoods["dist"].idxmin()]
        if best["dist"] < 0.03:
            if st.session_state.get("spotlight") != best["neighbourhood"]:
                st.session_state["spotlight"] = best["neighbourhood"]
                st.rerun()

st.caption(
    "Hover any circle for a quick summary, or click it. Pick a neighbourhood "
    "in the Spotlight menu (left) to highlight it and read its full story "
    "below."
)

# ------------------------------------------------------------- spotlight
if selected_name and selected_name in set(hoods["neighbourhood"]):
    st.markdown("### Neighbourhood spotlight")
    row = hoods.loc[hoods["neighbourhood"] == selected_name].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Incidents", row["incidents_fmt"])
    c2.metric("Rank by volume", f"#{int(row['rank'])} of {len(hoods)}")
    c3.metric("Most common type", row["top_type"])
    c4.metric("Color group", row["archetype"])

    # Auto-written plain-English story.
    hood_mix = mix.loc[selected_name]
    top_share = hood_mix.max() * 100
    city_mix = view["TYPE"].value_counts(normalize=True)
    ratio = hood_mix / city_mix.reindex(hood_mix.index).fillna(0)
    ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()
    over = ratio[ratio >= 1.15].sort_values(ascending=False).head(2)

    story = [
        f"**{selected_name}** reported **{row['incidents_fmt']}** incidents "
        f"in this selection - it ranks **#{int(row['rank'])}** out of "
        f"{len(hoods)} neighbourhoods.",
        f"The most common type is **{row['top_type']}**, making up "
        f"**{top_share:.0f}%** of its incidents.",
    ]
    for type_name, r in over.items():
        story.append(
            f"It reports **{r:.1f}x more {type_name}** than the city average."
        )
    if over.empty:
        story.append(
            "Its crime mix is close to the city average - no type stands out "
            "as unusually common."
        )
    group_members = sorted(
        hoods.loc[hoods["cluster"] == row["cluster"], "neighbourhood"].tolist()
    )
    story.append(
        f"Color group **{row['archetype']}** - neighbourhoods with a similar "
        f"crime pattern: {', '.join(group_members)}."
    )

    st.markdown(f"**{selected_name} at a glance**")
    for line in story:
        st.markdown(f"- {line}")

    st.markdown(f"**{selected_name}** - share of each crime type")
    st.bar_chart(hood_mix.sort_values(ascending=False) * 100, horizontal=True,
                 x_label="share of incidents (%)")
else:
    st.info(
        "Pick a neighbourhood in the **Spotlight** menu (left sidebar) to "
        "read its full story here."
    )

# ----------------------------------------------------- all neighbourhoods
st.markdown("### All neighbourhoods at a glance")
overview = hoods[
    ["neighbourhood", "incidents_fmt", "rank", "top_type", "archetype"]
].rename(
    columns={
        "neighbourhood": "Neighbourhood",
        "incidents_fmt": "Incidents",
        "rank": "Rank",
        "top_type": "Most common type",
        "archetype": "Color group",
    }
).sort_values("Rank")
st.dataframe(overview, width="stretch", hide_index=True)

# ------------------------------------------------------- archetype explainer
with st.expander("What do the color groups mean?"):
    st.markdown(
        "The app looks at each neighbourhood's mix of crime types and groups "
        "together the ones that look alike - like sorting music into genres. "
        "You can change how many groups it creates in the sidebar."
    )
    for c, info in clusters.items():
        emoji = CLUSTER_EMOJI[int(c) % len(CLUSTER_EMOJI)]
        members = sorted(
            hoods.loc[hoods["cluster"] == c, "neighbourhood"].tolist()
        )
        st.markdown(
            f"{emoji} **{info['name']} - {info['signature']}** "
            f"({len(members)}): *{', '.join(members)}*"
        )

st.caption(
    "Data: Vancouver Police Department open data (reported incidents, "
    "2003-2026; 2022 missing). Locations are aggregated - no exact crime "
    "locations are shown. See Methodology & Limitations for details."
)
