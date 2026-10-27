"""Unit tests for the prototype SQLite storage (app/utils/db.py)."""
import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils import db  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Point the db module at a throwaway file for every test."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "prototype.db")
    yield


def valid_record(**overrides) -> dict:
    record = {
        "crime_type": "Mischief",
        "incident_date": date(2026, 1, 15),
        "neighbourhood": "West End",
        "location": "10XX ROBSON ST",
        "notes": "demo entry",
    }
    record.update(overrides)
    return record


class TestInsertFetch:
    def test_roundtrip(self):
        new_id = db.insert_incident(valid_record(), "entry")
        rows = db.fetch_incidents()
        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == new_id
        assert row["crime_type"] == "Mischief"
        assert row["incident_date"] == "2026-01-15"
        assert row["neighbourhood"] == "West End"
        assert row["location"] == "10XX ROBSON ST"
        assert row["notes"] == "demo entry"
        assert row["source"] == "user"
        assert row["created_by"] == "entry"
        assert row["created_at"]

    def test_fetch_is_newest_first(self):
        db.insert_incident(valid_record(), "entry")
        db.insert_incident(
            valid_record(crime_type="Other Theft", notes="second"), "entry"
        )
        rows = db.fetch_incidents()
        assert rows[0]["crime_type"] == "Other Theft"
        assert rows[1]["crime_type"] == "Mischief"

    def test_fetch_limit(self):
        for _ in range(5):
            db.insert_incident(valid_record(), "entry")
        assert len(db.fetch_incidents(limit=3)) == 3


class TestInjectionSafety:
    def test_malicious_fields_stored_literally(self):
        """A classic injection payload must be stored as text, not executed."""
        payload = "x'; DROP TABLE incidents; --"
        db.insert_incident(
            valid_record(location=payload, notes="<script>alert(1)</script>"),
            "entry",
        )
        rows = db.fetch_incidents()
        assert len(rows) == 1
        assert rows[0]["location"] == payload

        # The table must still exist and accept new inserts.
        db.insert_incident(valid_record(), "entry")
        assert len(db.fetch_incidents()) == 2

    def test_created_by_is_not_trusted_as_sql(self):
        db.insert_incident(valid_record(), "entry'); DROP TABLE incidents; --")
        rows = db.fetch_incidents()
        assert len(rows) == 1
        assert rows[0]["created_by"] == "entry'); DROP TABLE incidents; --"


class TestHourAndRole:
    def test_hour_stored(self):
        new_id = db.insert_incident(valid_record(hour=14), "entry", "Data Entry")
        row = db.fetch_incidents()[0]
        assert row["id"] == new_id
        assert row["hour"] == 14
        assert row["created_role"] == "Data Entry"

    def test_hour_not_recorded_is_null(self):
        db.insert_incident(valid_record(), "entry")
        assert db.fetch_incidents()[0]["hour"] is None


class TestAccessControl:
    def test_count_incidents(self):
        assert db.count_incidents() == 0
        db.insert_incident(valid_record(), "admin", "Administrator")
        db.insert_incident(valid_record(), "entry", "Data Entry")
        assert db.count_incidents() == 2

    def test_fetch_filtered_by_user(self):
        db.insert_incident(valid_record(), "admin", "Administrator")
        db.insert_incident(valid_record(), "entry", "Data Entry")

        admin_rows = db.fetch_incidents(created_by="admin")
        assert len(admin_rows) == 1
        assert admin_rows[0]["created_by"] == "admin"

        assert len(db.fetch_incidents()) == 2
