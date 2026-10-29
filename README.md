# Vancouver Urban Safety Intelligence Platform

An applied research project combining data analytics, machine learning,
geospatial visualization, and cybersecurity to analyze publicly available
Vancouver crime data through a secure web application prototype.

**Course:** CSIS 4495, Section 002
**Instructor:** Padmapriya Arasanipalai Kandhadai

## Team

| Member | Student ID | Role |
|---|---|---|
| Jaismine Kaur (Team Lead) | 300415820 | Data Analytics |
| Shashank Chaudhary | 300392521 | Cybersecurity |

## Project Structure

```
F26_4495_S2_JaismineK/
├── Implementation/          # All code (per progress-report template)
│   ├── app/                 # Streamlit app (Home.py + 9 pages + utils/)
│   ├── scripts/             # Reproducible data pipeline scripts
│   ├── notebooks/           # Exploratory/statistical/ML notebooks
│   └── tests/               # pytest suite
├── data/
│   ├── raw/                 # Downloaded VPD dataset (gitignored)
│   └── processed/           # Cleaned data + quality summaries (gitignored)
├── docs/
│   ├── research/            # Dataset documentation, findings
│   └── security/            # Threat model, privacy review
├── DocumentsAndReports/     # Submitted progress reports (PDF)
└── worklogs/                # Individual work logs
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the app from the repository root:

```bash
streamlit run Implementation/app/Home.py
```

## Current Progress

| Phase (per proposal) | Status |
|---|---|
| Sep 24-28: Proposal submitted | Complete |
| Sep 29-Oct 6: Data acquisition | Complete |
| Oct 7-12: Initial implementation | Complete |
| Oct 13-20: Analytics & security | Complete |
| Oct 21-28: Mid-course prototype | In progress |
| Oct 29-Nov 9: Database & Add Incident | In progress (pulled forward) |

### Tech stack

| Layer | Technology |
|---|---|
| Web UI | Streamlit (multipage `st.navigation`) |
| Charts | Plotly (line/bar/heatmap) |
| Maps | Folium (Leaflet) on ESRI World Street Map tiles |
| Analytics | pandas, numpy, scipy (chi-square, k-means) |
| ML | Moving-average + seasonal-naive baseline forecast with MAE/RMSE |
| Data | VPD GeoDASH CSV pipeline (pandas) + SQLite (user-entered records) |
| Security | PBKDF2 password hashing, RBAC, login lockout, append-only audit log, input validation/sanitization, parameterized SQL, pip-audit dependency scanning |
| Testing | pytest (81 tests: pipeline, security, stats, geo, clustering, forecast, db) |

### Completed so far

- Reproducible Python environment (`requirements.txt`): pandas, numpy,
  matplotlib, plotly, streamlit, pytest, certifi, scipy, folium, streamlit-folium
- VPD crime dataset downloaded (all neighbourhoods, all years: 928,362 rows
  as of the Oct 4, 2026 source update)
- Initial data quality inspection (see `data/processed/data_quality_summary.txt`)
- Data cleaning pipeline: 928,362 -> 893,851 rows (see `data/processed/cleaning_log.txt`)
- Dataset documentation (`docs/research/dataset_documentation.md`)
- Cybersecurity threat model v0.4 (`docs/security/threat_model.md`)
- Privacy review & data protection requirements (`docs/security/privacy_and_data_protection.md`)
- Reproducible download, inspection, and cleaning scripts (`Implementation/scripts/`)
- Streamlit app: Overview, Temporal Analysis, Statistical Analysis, Crime Map,
  Machine Learning, Add Incident, Security, Methodology, and Audit Log pages
- End-to-end Add Incident feature: validated form (crime type, neighbourhood,
  date, hour, location, notes) -> SQLite (parameterized queries) -> RBAC +
  audit trail -> separate user-entries display (admins see all records,
  other roles only their own)
- Crime Map: UTM-to-latlon conversion, privacy-safe neighbourhood aggregation,
  k-means crime-profile clustering, interactive folium map with hover/click
- Statistical Analysis: chi-square tests (type x season, type x day-of-week)
  with plain-English interpretations
- Machine Learning: honest 12-month forecast with moving-average and
  same-as-last-year baselines, MAE/RMSE evaluation
- Temporal Analysis page: filters plus hour-of-day, day-of-week, month,
  season charts, year x month heatmap, and automatic insights
- Exploratory data analysis notebook (`notebooks/01_exploratory_analysis.ipynb`)
- Temporal & pandemic analysis notebook (`notebooks/02_temporal_and_pandemic_analysis.ipynb`):
  crime-type hour patterns, redacted-timestamp finding, COVID comparison,
  seasonality and neighbourhood-change hypotheses
- Test suite: 81 tests passing (pipeline, security, stats, geo, clustering,
  forecast, db) - run with `pytest Implementation/tests/ -v`
- Dependency scan: pip-audit run (Oct 26) - 41 vulnerabilities in certifi +
  pillow found and fixed; re-scan clean (see
  `docs/security/dependency_scan_report.md`)

### Key data quality findings

- Missing year 2022 (2003-2021, 2023-2026)
- 34,511 duplicate rows
- 83,020 rows with zero coordinates
- 11 crime types, 24 neighbourhoods

## Reproduction

```bash
python Implementation/scripts/00_download_data.py   # download + extract raw data
python Implementation/scripts/01_inspect_data.py    # generate quality summary
python Implementation/scripts/02_clean_data.py      # clean data + write cleaning log
```

## Disclaimer

This is a research prototype. It is not an official crime-reporting system and
does not make policing decisions.
