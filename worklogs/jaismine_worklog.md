# Work Log - Jaismine Kaur (300415820)

| Date | Hours | Description of work done |
|---|---|---|
| Oct 8, 2026 | 1 | Initial implementation kickoff: restored the Streamlit app skeleton (multipage navigation, Overview, placeholders) from git history for the Oct 7-12 phase |
| Oct 8, 2026 | 1.5 | Implemented the Temporal Analysis page (`app/pages/3_temporal.py`): year/crime-type/neighbourhood filters, hour-of-day, day-of-week, month, and season charts, a year x month heatmap, and automatic insights |
| Oct 8, 2026 | 1 | Environment setup: added `requirements.txt`; fixed SSL verification in `scripts/00_download_data.py` (certifi); re-ran the full data pipeline (download, inspect, clean) - 928,362 raw rows cleaned to 893,851 |
| Oct 8, 2026 | 1.5 | Refactored `scripts/02_clean_data.py` into a testable `clean_dataframe()` function; wrote functional tests (`tests/test_pipeline.py`) covering cleaning steps, quality summary, and auth utilities - 14 tests passing |
| Oct 8, 2026 | 1 | Created exploratory data analysis notebook (`notebooks/01_exploratory_analysis.ipynb`); updated dataset documentation, README progress table, and setup instructions |
