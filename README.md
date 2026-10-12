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
├── data/
│   ├── raw/            # Downloaded VPD dataset (gitignored, see scripts/)
│   └── processed/      # Cleaned data + quality summaries
├── notebooks/          # Exploratory/statistical/ML notebooks
├── scripts/            # Reproducible data pipeline scripts
├── docs/
│   ├── research/       # Dataset documentation, findings
│   └── security/       # Threat model, security assessment
├── app/                # Streamlit application
├── tests/              # Functional and security tests
└── worklogs/           # Individual work logs
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
| Oct 7-12: Initial implementation | In progress |
| Oct 13-20: Analytics & security | Not started |
| Oct 21-28: Mid-course prototype | Not started |
| Oct 29-Nov 9: Database & Add Incident | Not started |

### Completed so far

- Reproducible Python environment (`requirements.txt`): pandas, numpy,
  matplotlib, plotly, streamlit, pytest, certifi
- VPD crime dataset downloaded (all neighbourhoods, all years: 928,362 rows
  as of the Oct 4, 2026 source update)
- Initial data quality inspection (see `data/processed/data_quality_summary.txt`)
- Data cleaning pipeline: 928,362 -> 893,851 rows (see `data/processed/cleaning_log.txt`)
- Dataset documentation (`docs/research/dataset_documentation.md`)
- Cybersecurity threat model draft v0.1 (`docs/security/threat_model.md`)
- Privacy review & data protection requirements (`docs/security/privacy_and_data_protection.md`)
- Reproducible download, inspection, and cleaning scripts (`scripts/`)
- Streamlit app skeleton: multipage navigation (Overview, Crime Map, Temporal
  Analysis, Statistical Analysis, Machine Learning, Add Incident, Security,
  Methodology), login/RBAC prototype (PBKDF2 hashing, demo users), Security
  and Methodology pages (`app/`)
- Temporal Analysis page implemented: filters plus hour-of-day, day-of-week,
  month, season charts, year x month heatmap, and automatic insights
  (`app/pages/3_temporal.py`)
- Exploratory data analysis notebook (`notebooks/01_exploratory_analysis.ipynb`)
- Temporal & pandemic analysis notebook (`notebooks/02_temporal_and_pandemic_analysis.ipynb`):
  crime-type hour patterns, redacted-timestamp finding, COVID comparison,
  seasonality and neighbourhood-change hypotheses
- Functional test suite: 14 tests passing (`tests/test_pipeline.py`, run with
  `pytest Implementation/tests/ -v`)

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
