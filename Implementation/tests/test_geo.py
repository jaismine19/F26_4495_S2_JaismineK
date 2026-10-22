"""Unit tests for geospatial helpers (app/utils/geo.py)."""
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils import geo  # noqa: E402


class TestUtmToLatlon:
    def test_equator_at_central_meridian(self):
        # Easting 500000, northing 0 must be exactly (0, -123) in zone 10N.
        lat, lon = geo.utm_to_latlon(500000, 0)
        assert lat == pytest.approx(0.0, abs=1e-9)
        assert lon == pytest.approx(-123.0, abs=1e-9)

    def test_vancouver_lands_in_vancouver(self):
        lat, lon = geo.utm_to_latlon(491272, 5458075)
        assert 49.0 < lat < 49.5
        assert -123.4 < lon < -122.9

    def test_monotonic(self):
        # Moving north increases latitude; moving east increases longitude.
        lat1, lon1 = geo.utm_to_latlon(490000, 5458000)
        lat2, lon2 = geo.utm_to_latlon(490000, 5460000)
        assert lat2 > lat1
        _, lon3 = geo.utm_to_latlon(491000, 5458000)
        assert lon3 > lon1


def make_spatial_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "TYPE": ["Theft"] * 4 + ["Mischief"] * 2,
            "NEIGHBOURHOOD": ["West End"] * 3 + ["Strathcona"] * 3,
            "X": [490000.0, 490500.0, 491000.0, 493000.0, 493500.0, 494000.0],
            "Y": [5458000.0, 5458200.0, 5458400.0, 5459000.0, 5459100.0, 5459200.0],
        }
    )


class TestAggregateNeighbourhoods:
    def test_one_row_per_neighbourhood_with_counts(self):
        out = geo.aggregate_neighbourhoods(make_spatial_df())
        assert set(out["neighbourhood"]) == {"West End", "Strathcona"}
        by_name = out.set_index("neighbourhood")
        assert by_name.loc["West End", "incidents"] == 3
        assert by_name.loc["Strathcona", "incidents"] == 3

    def test_top_type_is_mode(self):
        out = geo.aggregate_neighbourhoods(make_spatial_df())
        west_end = out.loc[out["neighbourhood"] == "West End"]
        assert west_end["top_type"].iloc[0] == "Theft"

    def test_out_of_bounds_coordinates_are_excluded(self):
        df = make_spatial_df()
        # Add a West End row with garbage coordinates (outside Vancouver UTM).
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    {
                        "TYPE": ["Theft"],
                        "NEIGHBOURHOOD": ["West End"],
                        "X": [870000.0],
                        "Y": [999999.0],
                    }
                ),
            ]
        )
        out = geo.aggregate_neighbourhoods(df)
        west_end = out.loc[out["neighbourhood"] == "West End"]
        # Median must come from the 3 valid rows (490500), not the outlier.
        expected_lat, expected_lon = geo.utm_to_latlon(490500, 5458200)
        assert west_end["lat"].iloc[0] == pytest.approx(expected_lat, abs=1e-9)
        assert west_end["lon"].iloc[0] == pytest.approx(expected_lon, abs=1e-9)
        # Count still includes all 4 rows (aggregation vs coordinate validity).
        assert west_end["incidents"].iloc[0] == 4

    def test_all_invalid_coordinates_returns_empty_frame_with_columns(self):
        """No valid coordinates anywhere must yield an empty frame, not a crash."""
        df = pd.DataFrame(
            {
                "TYPE": ["Theft", "Mischief"],
                "NEIGHBOURHOOD": ["West End", "Strathcona"],
                "X": [0.0, 0.0],
                "Y": [0.0, 0.0],
            }
        )
        out = geo.aggregate_neighbourhoods(df)
        assert len(out) == 0
        assert list(out.columns) == ["neighbourhood", "incidents", "lat", "lon", "top_type"]
