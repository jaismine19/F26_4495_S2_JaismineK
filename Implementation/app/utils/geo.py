"""Geospatial helpers for the Crime Map.

- utm_to_latlon: pure UTM Zone 10N -> WGS84 conversion (standard transverse
  Mercator formulas), so neighbourhood centroids can be placed on a map.
- aggregate_neighbourhoods: privacy-safe aggregation - incident counts and
  median coordinates per neighbourhood, never raw incident points.

All functions are pure and unit-testable.
"""
from math import cos, degrees, radians, sin, sqrt, tan

import pandas as pd

# Plausible UTM Zone 10N bounds for the City of Vancouver. Rows outside this
# box are data-quality errors (the raw data contains stray coordinates).
X_MIN, X_MAX = 470_000.0, 510_000.0
Y_MIN, Y_MAX = 5_440_000.0, 5_475_000.0


def utm_to_latlon(easting: float, northing: float, zone: int = 10,
                  northern: bool = True) -> tuple[float, float]:
    """Convert UTM (Zone 10N, WGS84) coordinates to (latitude, longitude).

    Standard USGS/Snyder transverse-Mercator inverse formulas.
    """
    a = 6378137.0            # WGS84 semi-major axis
    f = 1 / 298.257223563    # WGS84 flattening
    k0 = 0.9996              # UTM central scale factor

    e2 = f * (2 - f)                       # first eccentricity squared
    ep2 = e2 / (1 - e2)                    # second eccentricity squared
    e1 = (1 - sqrt(1 - e2)) / (1 + sqrt(1 - e2))

    x = easting - 500000.0                 # remove false easting
    y = northing - (0.0 if northern else 10000000.0)

    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256))

    phi1 = (
        mu
        + (3 * e1 / 2 - 27 * e1**3 / 32) * sin(2 * mu)
        + (21 * e1**2 / 16 - 55 * e1**4 / 32) * sin(4 * mu)
        + (151 * e1**3 / 96) * sin(6 * mu)
        + (1097 * e1**4 / 512) * sin(8 * mu)
    )

    c1 = ep2 * cos(phi1) ** 2
    t1 = tan(phi1) ** 2
    n1 = a / sqrt(1 - e2 * sin(phi1) ** 2)
    r1 = a * (1 - e2) / (1 - e2 * sin(phi1) ** 2) ** 1.5
    d = x / (n1 * k0)

    lat = phi1 - (n1 * tan(phi1) / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * ep2 - 3 * c1**2)
        * d**6 / 720
    )
    lon = (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * ep2 + 24 * t1**2)
        * d**5 / 120
    ) / cos(phi1)

    lon0 = radians((zone - 1) * 6 - 180 + 3)   # zone 10 central meridian
    return degrees(lat), degrees(lon0 + lon)


def aggregate_neighbourhoods(df: pd.DataFrame) -> pd.DataFrame:
    """One row per neighbourhood: count, median coordinates, top crime type.

    Coordinates are aggregated (median of in-bounds points only), following
    the privacy rule: the map never shows raw individual incident locations.
    """
    rows = []
    for hood, group in df.groupby("NEIGHBOURHOOD", dropna=True):
        valid = group[
            group["X"].between(X_MIN, X_MAX) & group["Y"].between(Y_MIN, Y_MAX)
        ]
        if valid.empty:
            continue
        median_x = valid["X"].median()
        median_y = valid["Y"].median()
        lat, lon = utm_to_latlon(median_x, median_y)
        rows.append(
            {
                "neighbourhood": hood,
                "incidents": int(len(group)),
                "lat": lat,
                "lon": lon,
                "top_type": group["TYPE"].mode().iloc[0],
            }
        )
    # Return a correctly-shaped empty frame (not a bare DataFrame()) so
    # callers can sort/downstream-process without KeyError surprises.
    if not rows:
        return pd.DataFrame(
            columns=["neighbourhood", "incidents", "lat", "lon", "top_type"]
        )
    return pd.DataFrame(rows).sort_values("incidents", ascending=False).reset_index(drop=True)
