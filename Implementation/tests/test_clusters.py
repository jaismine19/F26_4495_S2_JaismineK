"""Unit tests for neighbourhood crime-profile clustering."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils import clusters  # noqa: E402


def make_mix_df() -> pd.DataFrame:
    """6 neighbourhoods with two clear profiles: theft-heavy vs mischief-heavy."""
    data = {
        "Downtown": {"Theft": 80, "Mischief": 20},
        "Yaletown": {"Theft": 75, "Mischief": 25},
        "Gastown": {"Theft": 70, "Mischief": 30},
        "Sunset": {"Theft": 20, "Mischief": 80},
        "Killarney": {"Theft": 25, "Mischief": 75},
        "Marpole": {"Theft": 30, "Mischief": 70},
    }
    return pd.DataFrame(data).T


class TestCrimeMix:
    def test_rows_sum_to_one(self):
        mix = clusters.crime_mix(
            pd.DataFrame(
                {
                    "NEIGHBOURHOOD": ["A"] * 8 + ["B"] * 2,
                    "TYPE": ["Theft"] * 8 + ["Mischief"] * 2,
                }
            )
        )
        assert mix.loc["A", "Theft"] == pytest.approx(1.0)
        assert mix.loc["B", "Mischief"] == pytest.approx(1.0)
        np.testing.assert_allclose(mix.sum(axis=1), 1.0)


class TestClusterNeighbourhoods:
    def test_returns_labels_for_every_neighbourhood(self):
        mix = make_mix_df()
        result = clusters.cluster_neighbourhoods(mix, k=2)
        labels = result["labels"]
        assert len(labels) == 6
        assert set(labels["neighbourhood"]) == set(mix.index)

    def test_two_profiles_split_into_two_clusters(self):
        mix = make_mix_df()
        result = clusters.cluster_neighbourhoods(mix, k=2)
        labels = result["labels"].set_index("neighbourhood")
        # Theft-heavy trio and mischief-heavy trio should not mix.
        assert labels.loc["Downtown", "cluster"] == labels.loc["Yaletown", "cluster"]
        assert labels.loc["Downtown", "cluster"] != labels.loc["Sunset", "cluster"]

    def test_describe_clusters_covers_all_clusters(self):
        mix = make_mix_df()
        result = clusters.cluster_neighbourhoods(mix, k=2)
        table = clusters.describe_clusters(result["labels"], result["clusters"])
        assert len(table) == 2
        assert table["neighbourhoods"].sum() == 6
        assert all(table["signature types"].str.contains("Theft|Mischief"))
