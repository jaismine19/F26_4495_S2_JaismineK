# Work Log - Jaismine Kaur (300415820)

| Date | Hours | Description of work done |
|---|---|---|
| Sep 26, 2026 | 1.5 | GitHub/repository setup: created the project repository, added Shashank as collaborator, initial commit |
| Oct 9, 2026 | 1.0 | Reviewed project state, timeline phases, and upcoming deliverables against the repo |
| Oct 9, 2026 | 0.5 | Project setup with Shashank: created folder structure (data/, scripts/, docs/, app/, tests/, worklogs/) and .gitignore |
| Oct 9, 2026 | 0.5 | Data acquisition with Shashank: downloaded VPD crime dataset from GeoDASH open data; reviewed the data quality summary (928,362 rows; missing 2022; 83K zero coordinates) |
| Oct 9, 2026 | 0.25 | Contributed to docs/research/dataset_documentation.md (source, schema, quality findings, privacy notes) |
| Oct 9, 2026 | 0.25 | Reviewed Shashank's threat model draft (docs/security/threat_model.md) |
| Oct 9, 2026 | 0.25 | Data cleaning with Shashank: reviewed scripts/02_clean_data.py and the cleaning log (928,362 -> 893,851 rows) |
| Oct 9, 2026 | 0.25 | Reviewed privacy review draft (docs/security/privacy_and_data_protection.md) |
| Oct 9, 2026 | 0.25 | Repository maintenance: README progress table updates; commit and push |
| Oct 11, 2026 | 1.0 | Local environment setup: created virtual environment and installed requirements |
| Oct 11, 2026 | 1.0 | Ran the full data pipeline end-to-end: downloaded VPD dataset, generated quality summary, ran cleaning (928,362 -> 893,851 rows) |
| Oct 11, 2026 | 0.5 | Reviewed the data pipeline scripts (00_download_data, 01_inspect_data, 02_clean_data) and their quality/cleaning reports |
| Oct 11, 2026 | 0.5 | Reviewed the dataset documentation and privacy notes (docs/research/, docs/security/) |
| Oct 11, 2026 | 0.5 | Ran and explored the Streamlit app: Overview, Temporal Analysis, and the Add Incident role-based demo (admin/analyst/entry) |
| Oct 11, 2026 | 0.5 | Reviewed the app structure: Home.py navigation, pages, and utils (auth, data loader, UI helpers) |
| Oct 11, 2026 | 0.5 | Reviewed the functional test suite and ran pytest (14 tests passing: cleaning, inspection, auth) |
| Oct 11, 2026 | 0.5 | App edit: removed the course-code/prototype caption from the sidebar; committed and pushed |
| Oct 11, 2026 | 1.5 | Performed exploratory analysis: crime-type x hour patterns (including the redacted-timestamp finding for violent types) and pandemic comparison (2019-2020-2021-2023) |
| Oct 11, 2026 | 1.0 | Built the temporal & pandemic analysis notebook (notebooks/02_temporal_and_pandemic_analysis.ipynb) with 5 documented findings and charts |
| Oct 11, 2026 | 1.0 | Read about EDA techniques and brainstormed approaches to reduce redundancy in the dataset |
| Oct 12, 2026 | 1.0 | Reviewed and refined the analysis notebook structure, headings, and findings formatting |
| Oct 12, 2026 | 0.5 | Prepared Progress Report #1: work-log table, summary, repo check-in, and AI-use section |
| Oct 16, 2026 | 1.5 | Worked on the Statistical Analysis page: chi-square tests (crime type x season, crime type x day of week), reviewed observed/expected tables and the season-share heatmap |
| Oct 16, 2026 | 3.0 | Debugged and fixed a datetime parsing bug: midnight timestamps were written without the time part, breaking INCIDENT_DATETIME loading; added ISO date format in the cleaning script and defensive parsing in the data loader |
| Oct 22, 2026 | 1.0 | Went through the project to figure out which features could be built all the way through (from the screen to the database and back) for the mid-course demo - decided on the Add Incident feature |
| Oct 22, 2026 | 1.5 | Built the Add Incident feature from front to back: set up the SQLite database with safe queries, connected the incident form to the validation rules, saved each record with who added it and when, and showed the saved entries in the app |
| Oct 22, 2026 | 1.0 | Wrote tests for the database, including trying SQL injection attacks to check they are stored as plain text and cannot break anything; the test suite now has 51 passing tests |
| Oct 22, 2026 | 1.5 | Fixed merge conflicts with Shashank's work (login lockout and the Audit Log page) and updated the Security page statuses |
| Oct 22, 2026 | 1.0 | Practiced the demo flow (login, roles, audit trail) and made a cheat sheet for the presentation |
| Oct 22, 2026 | 1.0 | Tested the Crime Map from a first-time user's point of view and listed what felt unclear (color meaning, hover info, circle sizes) |
| Oct 22, 2026 | 1.0 | Redesigned the map page for non-technical users: plain-English how-to guide, big-picture stats, auto-written neighbourhood summaries, and a full details table |
| Oct 22, 2026 | 1.5 | Fixed the map interactivity: switched to a map engine with reliable hover tooltips and click-to-highlight selection |
| Oct 22, 2026 | 0.5 | Fixed the broken map background (the old free map provider started requiring an API key) by switching to a free street-map provider |
| Oct 22, 2026 | 1.0 | Fixed a crash that happened when filters left no usable map coordinates, and added a regression test; the test suite now has 62 passing tests |
| Oct 23, 2026 | 1.0 | Started planning the neighbourhood map feature: decided to show neighbourhood-level data instead of raw points to keep it privacy-safe, and sketched how the page should work (filters -> grouped data -> map) |
| Oct 23, 2026 | 1.5 | Worked on the coordinate conversion: turned the dataset's UTM coordinates into latitude and longitude using the standard map formulas, and checked the math against known Vancouver locations |
| Oct 24, 2026 | 1.0 | Wrote the neighbourhood grouping logic: counts and median location per neighbourhood, with a check that skips coordinates outside Vancouver (data-quality guard) |
| Oct 24, 2026 | 1.0 | Added the clustering part: grouped neighbourhoods by how similar their crime mixes are (k-means), so the map can show neighbourhood archetypes instead of plain dots |
| Oct 25, 2026 | 1.5 | Built the Crime Map page in the app: filters, the interactive map with circles sized by incident count and colored by archetype, hover details, and the archetype summary table |
| Oct 25, 2026 | 1.0 | Wrote tests for the map code (coordinate math, grouping, clustering) and fixed a bug where neighbourhoods with missing names crashed the page; the test suite now has 61 passing tests |
| Oct 26, 2026 | 0.5 | Went through the map page end to end with the demo in mind and updated the demo cheat sheet |
