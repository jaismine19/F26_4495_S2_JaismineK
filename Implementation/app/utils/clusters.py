"""Unsupervised clustering of neighbourhood crime profiles.

Each neighbourhood is described by its normalized crime-type mix (share of
each of the 11 types). k-means groups neighbourhoods into archetypes, and
each cluster is auto-labelled from its dominant crime types.

Pure numpy/scipy logic, unit-testable, no Streamlit dependency.
"""
import numpy as np
import pandas as pd
from scipy.cluster.vq import kmeans2


def crime_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Neighbourhood x crime-type matrix of normalized shares (rows sum to 1)."""
    counts = pd.crosstab(df["NEIGHBOURHOOD"], df["TYPE"])
    return counts.div(counts.sum(axis=1), axis=0)


def cluster_neighbourhoods(mix: pd.DataFrame, k: int = 4) -> dict:
    """Cluster neighbourhoods by crime mix using k-means (kmeans2).

    Returns labels per neighbourhood, per-cluster dominant types, and a
    human-readable name for each cluster derived from its signature.
    """
    data = mix.to_numpy().astype(float)
    centroids, labels = kmeans2(data, k, minit="++", seed=42)

    cluster_info = {}
    for i in range(k):
        profile = pd.Series(centroids[i], index=mix.columns)
        top = profile.nlargest(2).index.tolist()
        cluster_info[i] = {
            "centroid": profile,
            "top_types": top,
            "name": f"Group {i + 1}",
            "signature": " & ".join(t.split(" (")[0] for t in top),
        }

    labels_df = pd.DataFrame(
        {"neighbourhood": mix.index, "cluster": labels}
    )
    labels_df["archetype"] = labels_df["cluster"].map(
        lambda c: f"{cluster_info[c]['name']} - {cluster_info[c]['signature']}"
    )
    return {"labels": labels_df, "clusters": cluster_info}


def describe_clusters(labels_df: pd.DataFrame, cluster_info: dict) -> pd.DataFrame:
    """Summary table: archetype name, members, and signature types."""
    rows = []
    for c, info in cluster_info.items():
        members = labels_df.loc[labels_df["cluster"] == c, "neighbourhood"].tolist()
        rows.append(
            {
                "archetype": info["name"],
                "neighbourhoods": len(members),
                "signature types": "; ".join(info["top_types"]),
                "members": ", ".join(sorted(members)),
            }
        )
    return pd.DataFrame(rows)
