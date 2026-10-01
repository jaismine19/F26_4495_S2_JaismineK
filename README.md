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
pip install pandas numpy matplotlib scikit-learn streamlit plotly folium geopandas
```

## Current Progress

| Phase (per proposal) | Status |
|---|---|
| Sep 24-28: Proposal submitted | Complete |
| Sep 29-Oct 6: Data acquisition | In progress |
| Oct 7-12: Initial implementation | Not started |

### Completed so far

- VPD crime dataset downloaded (all neighbourhoods, all years: 927,794 rows)
- Initial data quality inspection (see `data/processed/data_quality_summary.txt`)
- Dataset documentation drafted (`docs/research/dataset_documentation.md`)
- Cybersecurity threat model draft v0.1 (`docs/security/threat_model.md`)
- Reproducible download + inspection scripts (`scripts/`)

### Key data quality findings

- Missing year 2022 (2003-2021, 2023-2026)
- 34,527 duplicate rows
- 83,014 rows with zero coordinates
- 11 crime types, 24 neighbourhoods

## Reproduction

```bash
python scripts/00_download_data.py   # download + extract raw data
python scripts/01_inspect_data.py    # generate quality summary
```

## Disclaimer

This is a research prototype. It is not an official crime-reporting system and
does not make policing decisions.
