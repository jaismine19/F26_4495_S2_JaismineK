# Dependency Scan Report

**Date:** October 29, 2026
**Tool:** pip-audit (Python dependency vulnerability scanner)
**Scope:** All Python packages in the project environment (pandas, numpy,
matplotlib, plotly, streamlit, pytest, certifi, scipy, folium,
streamlit-folium, and their dependencies).

## Result

First scan found **41 known vulnerabilities in 2 packages**. We fixed both by
upgrading to patched versions, and the re-scan reports **0 vulnerabilities**.

## Vulnerabilities found and fixed

| Package | Vulnerable version | Fix version | Issue |
|---|---|---|---|
| certifi | 2026.7.22 | 2026.10.23 | Outdated CA certificate bundle (PYSEC-2026-4320) |
| pillow | 12.3.0 | 13.0.0 | 40 advisories (PYSEC/CVE/GHSA) fixed in 13.0.0 |

## What we did

1. Ran `pip-audit` to list known vulnerabilities in every installed package.
2. Upgraded `certifi` and `pillow` to their fixed versions.
3. Pinned minimum versions in `requirements.txt` so a fresh install does not
   pull in the vulnerable versions again:
   - `certifi>=2026.10.23`
   - `pillow>=13.0.0`
4. Re-ran `pip-audit`: **No known vulnerabilities found.**

## Next steps

- Re-run `pip-audit` at the end of the project before the final submission.
- Consider adding pip-audit to a small script under `scripts/` so the check
  is reproducible.
