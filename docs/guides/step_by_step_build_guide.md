# Step-by-Step Build Guide

**Project:** Vancouver Urban Safety Intelligence Platform (CSIS 4495, Section 002)
**Team:** Jaismine Kaur (Team Lead, Data Analytics) + Shashank Chaudhary (Cybersecurity)

This guide walks through building the project from scratch, phase by phase,
following the proposal timeline. Use it to (a) understand what is already in
the repo and how it was built, and (b) know exactly what to build next.

> Repo status as of Oct 8, 2026: Phases 1-2 (data acquisition + initial
> implementation) are complete. The current phase is **Oct 7-12: Initial
> implementation** (just completed), followed by **Oct 13-20: Analytics &
> security**.

---

## Phase 0 - Workspace setup (do this first on any machine)

```bash
# 1. Get the code
git clone https://github.com/jaismine19/F26_4495_S2_JaismineK.git
cd F26_4495_S2_JaismineK

# 2. Create an isolated Python environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install all dependencies (pandas, numpy, matplotlib, plotly,
#    streamlit, pytest, certifi)
pip install -r requirements.txt
```

Always run the commands below **from the repository root** (the folder with
`README.md`). The scripts use relative paths like `data/raw/...`.

**Checkpoint:** `python -c "import pandas, streamlit; print('ok')"` works.

---

## Phase 1 - Data acquisition (Sep 29 - Oct 6)  ✅ complete

**Goal:** reproducibly download, inspect, clean, and document the VPD dataset.

### 1.1 Download the raw data

`scripts/00_download_data.py`
- Downloads the zip from VPD GeoDASH open data (~10 MB) and extracts it to
  `data/raw/`.
- **Lesson:** we had to add the `certifi` CA bundle because macOS python.org
  installs fail SSL verification by default.

```bash
python scripts/00_download_data.py
```

### 1.2 Inspect the data

`scripts/01_inspect_data.py`
- Prints/writes a quality summary: rows, dtypes, missing values, duplicates,
  temporal ranges, distinct categories, spatial checks, counts per year.
- Output: `data/processed/data_quality_summary.txt`.

```bash
python scripts/01_inspect_data.py
```

### 1.3 Clean the data

`scripts/02_clean_data.py`
- Standardizes categorical whitespace, removes exact duplicates, flags
  zero-coordinates as missing, builds `INCIDENT_DATETIME`, adds
  `DAY_OF_WEEK` and `SEASON`, drops rows with invalid core fields.
- Every step logs before/after row counts.
- Output: `data/processed/crime_data_cleaned.csv` + `cleaning_log.txt`.

```bash
python scripts/02_clean_data.py
```

### 1.4 Document everything

- `docs/research/dataset_documentation.md` - source, schema, quality findings,
  privacy notes, transformation checklist.

**Key findings (from the Oct 4, 2026 source):** 928,362 raw rows, 34,511
duplicates, 83,020 zero-coordinate rows, missing year 2022, 11 crime types,
24 neighbourhoods. Cleaned: 893,851 rows.

**Checkpoint:** all three scripts run without errors and the CSV exists.

---

## Phase 2 - Initial implementation (Oct 7-12)  ✅ complete

**Goal:** first working version of the Streamlit app + first analysis +
tests.

### 2.1 Learn the data (EDA)

`notebooks/01_exploratory_analysis.ipynb`
- Distribution of crime types, yearly trend, top neighbourhoods, hour /
  day-of-week / season patterns, the 2022 gap.
- Findings feed the dashboard and later phases.

### 2.2 App skeleton

- `app/Home.py` - entry point; `st.navigation` with 8 pages.
- `app/pages/1_overview.py` - key figures + charts (plotly).
- `app/pages/6_add_incident.py` - login + RBAC prototype.
- `app/pages/7_security.py`, `8_methodology.py` - workstream summaries.
- Placeholders for Crime Map, Statistical, ML pages (built in later phases).
- `app/utils/` - `data_loader.py` (cached loading), `auth.py` (PBKDF2 hashing,
  demo users, roles), `ui.py` (shared helpers).

### 2.3 First real analysis page

`app/pages/3_temporal.py`
- Filters (year range, crime types, neighbourhoods) applied to all charts.
- Hour-of-day, day-of-week, month, season charts + year x month heatmap +
  automatic insights (peak hour, busiest day, weekend share).

### 2.4 Tests

`tests/test_pipeline.py` - 14 tests: cleaning steps, quality summary, auth
utilities. Run:

```bash
pytest tests/ -v
```

### 2.5 Run the app

```bash
streamlit run app/Home.py
```

Demo logins (Add Incident page): `admin` / `demo_admin_123`,
`analyst` / `demo_analyst_123`, `entry` / `demo_entry_123`.

**Checkpoint:** app loads in the browser, every page renders, tests pass.

---

## Phase 3 - Analytics & security (Oct 13-20)  ⬜ next

### Jaismine - analytics

1. **Statistical Analysis page** (`app/pages/4_statistical.py`)
   - Distributions and summary stats by crime type and neighbourhood.
   - Chi-square test: crime type vs season / day of week.
   - Trend analysis: monthly totals, year-over-year change.
   - Correlation between neighbourhood crime counts and temporal patterns.
   - Add findings to a `docs/research/statistical_findings.md`.

2. **Machine Learning page** (`app/pages/5_machine_learning.py`)
   - Simple baseline first: moving-average forecast of monthly incidents
     (train/test split by year).
   - Optional: clustering neighbourhoods by crime-profile mix (KMeans on
     normalized counts), classification to predict high-incident months.
   - Log experiments in `docs/research/ml_experiments.md`.

### Shashank - security (from the threat model)

1. Replace PBKDF2 demo hashing with `bcrypt` or `argon2` + per-user salts.
2. Input validation + output encoding on every user-input path (XSS).
3. Database access via parameterized queries only.
4. Append-only audit log table for login attempts and record changes.
5. `pip-audit` dependency scan; fix or document findings.
6. Session hardening: regenerate on login, secure cookie config.
7. Security tests in `tests/` (role matrix: every page x every role).

**Checkpoint:** statistical + ML pages live, security controls implemented
and documented in `docs/security/`.

---

## Phase 4 - Mid-course prototype (Oct 21-28)  ⬜

1. **Crime Map page** (`app/pages/2_crime_map.py`)
   - `folium` or `pydeck` map; remember the privacy rule: **aggregate or
     generalize** coordinates (neighbourhood counts, density surfaces) - no
     raw precise points.
2. Neighbourhood dropdown + crime-type filter driving the map.
3. Mid-course presentation: demo script, slides, prepare demo logins.

**Checkpoint:** interactive map works in the app; demo rehearsed.

---

## Phase 5 - Database & Add Incident (Oct 29-Nov 9)  ⬜

1. SQLite database (`app/db.py`): `users`, `incidents`, `audit_log` tables.
2. `users` seeded from the auth module; password hashes only (no plaintext).
3. Full Add Incident form: crime type, date/time, neighbourhood, optional
   location, notes. Validation: lengths, allowed values, date ranges.
4. Records stored with `created_by`, `created_at`, `source='user'` - kept
   visually/logically separate from public data.
5. Audit log entries for login success/failure + record create/update/delete.
6. Role checks server-side on every privileged action.

**Checkpoint:** a Data Entry user can submit an incident; an admin can see
audit logs; SQL injection attempts fail.

---

## Phase 6 - Final testing & report (Nov 10+)  ⬜

1. Run the full test suite + security test checklist from the threat model.
2. Re-run the pipeline end-to-end on a clean checkout (reproducibility).
3. Final report sections: methodology, findings, limitations, security
   assessment, future work.
4. Confirm README progress table and both worklogs are complete and honest.

---

## Weekly routine (team lead)

- **Monday:** agree the week's tasks with Shashank; split by workstream.
- **During the week:** small commits per task; run `pytest` before pushing.
- **Sunday:** update the README progress table, both worklogs, and push.

## Common mistakes to avoid

1. Running scripts from the wrong directory (paths are relative to repo root).
2. Committing `data/` files or `.venv/` (already covered by `.gitignore`).
3. Forgetting the worklog - update it the same day.
4. Over-interpreting results: reported incidents != all crime (missing 2022,
   reporting lag, anonymized locations).
5. Putting real credentials or secrets in the repo.
