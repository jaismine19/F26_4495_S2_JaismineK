"""Unsupervised clustering of neighbourhood crime profiles.

Each neighbourhood is described by its normalized crime-type mix (share of
each of the 11 types). k-means groups neighbourhoods into archetypes, and
each cluster is auto-labelled from its dominant crime types.

Robustness: k-means can return empty clusters when profiles are duplicated
or sparse (e.g., few crime types selected). We retry with different
initializations and reduce k until every cluster is non-empty and finite.
"""
import numpy as np
import pandas as pd
from scipy.cluster.vq import kmeans2


def crime_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Neighbourhood x crime-type matrix of normalized shares (rows sum to 1)."""
    counts = pd.crosstab(df["NEIGHBOURHOOD"], df["TYPE"])
    return counts.div(counts.sum(axis=1), axis=0)


def _kmeans_with_retries(data: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray] | None:
    """Run kmeans2 until every cluster is non-empty and finite, else None."""
    for minit in ("++", "random"):
        for seed in range(10):
            try:
                centroids, labels = kmeans2(data, k, minit=minit, iter=30, seed=seed)
            except Exception:
                continue
            sizes = np.bincount(labels, minlength=k)
            if (sizes > 0).all() and np.isfinite(centroids).all():
                return centroids, labels
    return None


def _top_types(centroid: np.ndarray, columns) -> list[str]:
    """Dominant crime types of a centroid, skipping NaN values."""
    profile = pd.Series(centroid, index=columns).dropna()
    if profile.empty:
        return ["Mixed"]
    return profile.nlargest(2).index.tolist()


def cluster_neighbourhoods(mix: pd.DataFrame, k: int = 4) -> dict:
    """Cluster neighbourhoods by crime mix using k-means (kmeans2).

    Falls back gracefully: k is capped to the number of distinct profiles,
    retried with different initializations, and reduced until a valid
    clustering is found. Returns labels per neighbourhood, per-cluster
    dominant types, and a human-readable name for each cluster.
    """
    data = mix.to_numpy().astype(float)
    distinct = int(np.unique(data, axis=0).shape[0])
    k = min(k, max(1, distinct))

    if k < 2:
        return _single_group(mix)

    result = _kmeans_with_retries(data, k)
    if result is None:
        for smaller_k in range(k - 1, 1, -1):
            result = _kmeans_with_retries(data, smaller_k)
            if result is not None:
                k = smaller_k
                break
        if result is None:
            return _single_group(mix)

    centroids, labels = result
    cluster_info = {}
    for i in range(k):
        top = _top_types(centroids[i], mix.columns)
        cluster_info[i] = {
            "top_types": top,
            "name": f"Group {i + 1}",
            "signature": " & ".join(t.split(" (")[0] for t in top),
        }

    labels_df = pd.DataFrame({"neighbourhood": mix.index, "cluster": labels})
    labels_df["archetype"] = labels_df["cluster"].map(
        lambda c: f"{cluster_info[c]['name']} - {cluster_info[c]['signature']}"
    )
    return {"labels": labels_df, "clusters": cluster_info}


def _single_group(mix: pd.DataFrame) -> dict:
    """Fallback when clustering is not possible: everything is one group."""
    labels_df = pd.DataFrame(
        {"neighbourhood": mix.index, "cluster": 0, "archetype": "Group 1 - Mixed"}
    )
    return {
        "labels": labels_df,
        "clusters": {0: {"name": "Group 1", "top_types": ["Mixed"], "signature": "Mixed"}},
    }


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
