# Dataset Documentation - VPD Crime Data

**Status:** Initial version - will be updated after cleaning decisions are finalized.

## 1. Source

| Item | Details |
|---|---|
| Publisher | Vancouver Police Department (VPD), GeoDASH open data |
| Download URL | `https://geodash.vpd.ca/opendata/crimedata_download/AllNeighbourhoods_AllYears/crimedata_csv_AllNeighbourhoods_AllYears.zip` |
| Dataset file | `crimedata_csv_AllNeighbourhoods_AllYears.csv` |
| Download date | October 8, 2026 (source file last modified by VPD: Oct 4, 2026) |
| License/Disclaimer | See `legal_disclaimer.txt` in `data/raw/` |
| Data dictionary | `VPD OpenData Crime Incidents Description.pdf` in `data/raw/` |

## 2. File Overview

- **Rows:** 928,362
- **Columns:** 10
- **Unit of analysis:** One reported, founded criminal incident.

## 3. Column Descriptions

| Column | Type | Description |
|---|---|---|
| `TYPE` | string | Broad crime category (11 distinct values) |
| `YEAR` | int | Year of incident (2003-2026) |
| `MONTH` | int | Month of incident (1-12) |
| `DAY` | int | Day of month (1-31) |
| `HOUR` | int | Hour of incident (0-23) |
| `MINUTE` | int | Minute of incident (0-59) |
| `HUNDRED_BLOCK` | string | Anonymized location (e.g., `10XX ALBERNI ST`) - privacy-protected |
| `NEIGHBOURHOOD` | string | Vancouver neighbourhood (24 distinct values) |
| `X` | float | UTM Zone 10N easting |
| `Y` | float | UTM Zone 10N northing |

## 4. Initial Quality Findings (see `data/processed/data_quality_summary.txt`)

1. **Missing year 2022:** The dataset contains no records for 2022.
   - 2003-2021, then 2023-2026. This will be confirmed against the VPD website
     and documented in the final report.
2. **Duplicate rows:** 34,511 exact duplicates were detected and will be removed
   during cleaning.
3. **Missing values:** HUNDRED_BLOCK (12), NEIGHBOURHOOD (99), X/Y (30).
4. **Zero coordinates:** 83,020 rows have X = 0 and/or Y = 0. These are treated
   as missing coordinates and will be handled in geospatial analysis.
5. **Coordinate range:** Valid-looking coordinates are consistent with UTM
   Zone 10N for the Vancouver area (X ~ 480,000-500,000; Y ~ 5,450,000-5,470,000).

## 5. Privacy Notes

- Locations are already anonymized by VPD to hundred-block level
  (e.g., `10XX ALBERNI ST`), not exact addresses.
- Broad crime categories are used for violent offences to reduce the risk of
  identifying individuals (per VPD documentation).
- Our app will continue this practice: exact coordinates may be aggregated or
  generalized in maps and visualizations.

## 6. Planned Transformations (to be implemented)

- [x] Remove duplicate records (34,511 removed)
- [x] Convert YEAR/MONTH/DAY into a single date field (INCIDENT_DATETIME)
- [x] Create derived features: season, day-of-week
- [x] Standardize categorical values (check whitespace/casing)
- [x] Handle rows with zero or missing X/Y (flagged as missing, kept in dataset)
- [x] Document every transformation with row counts before/after
      (see `data/processed/cleaning_log.txt`; 928,362 -> 893,851 rows)

## 7. Reprocessing Instructions

```bash
python scripts/00_download_data.py   # downloads + extracts raw data
python scripts/01_inspect_data.py    # generates quality summary
```
