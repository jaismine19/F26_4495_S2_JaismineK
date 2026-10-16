"""Statistical helpers for the Statistical Analysis page.

Pure pandas/scipy logic, kept separate from Streamlit so it can be unit-tested
without a running app. All functions work on an already-filtered DataFrame.
"""
import pandas as pd
from scipy import stats

# Crime types whose timestamps are redacted by VPD (always hour = 0).
# Hour-based analyses must exclude these.
VIOLENT_TYPES = ["Homicide", "Offence Against a Person"]

ALPHA = 0.05


def contingency_table(df: pd.DataFrame, col_a: str, col_b: str) -> pd.DataFrame:
    """Cross-tabulation of two categorical columns."""
    return pd.crosstab(df[col_a], df[col_b])


def chi_square_test(df: pd.DataFrame, col_a: str, col_b: str) -> dict:
    """Chi-square test of independence between two categorical columns.

    Returns a dict with the observed table, expected table, chi2 statistic,
    degrees of freedom, p-value, and whether it is significant at ALPHA.
    """
    observed = pd.crosstab(df[col_a], df[col_b])
    chi2, p, dof, expected = stats.chi2_contingency(observed.to_numpy())
    return {
        "observed": observed,
        "expected": pd.DataFrame(expected, index=observed.index, columns=observed.columns),
        "chi2": float(chi2),
        "p": float(p),
        "dof": int(dof),
        "significant": bool(p < ALPHA),
    }


def interpret_p(p: float) -> str:
    """Plain-English interpretation of a p-value."""
    if p < 0.001:
        return "Strong evidence of a relationship between the two variables (p < 0.001)."
    if p < 0.05:
        return "The relationship is statistically significant (p < 0.05)."
    return "No statistically significant relationship found."


def summary_stats(df: pd.DataFrame) -> dict:
    """Descriptive statistics for a filtered dataframe."""
    by_type = df["TYPE"].value_counts()
    peak_hour = df.loc[~df["TYPE"].isin(VIOLENT_TYPES), "HOUR"].mode()
    return {
        "incidents": len(df),
        "types": df["TYPE"].nunique(),
        "neighbourhoods": df["NEIGHBOURHOOD"].nunique(),
        "year_min": int(df["YEAR"].min()),
        "year_max": int(df["YEAR"].max()),
        "top_type": by_type.idxmax(),
        "top_type_share": float(by_type.max() / len(df) * 100),
        "peak_hour": int(peak_hour.iloc[0]) if not peak_hour.empty else None,
        "mean_per_day": float(len(df) / (df["INCIDENT_DATETIME"].dt.date.nunique() or 1)),
    }
