"""Tests for the incident-entry input validation module.

Run from the repository root:
    pytest Implementation/tests/test_validation.py -v
"""
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils import validation  # noqa: E402


class TestSanitizeText:
    def test_strips_and_collapses_whitespace(self):
        assert validation.sanitize_text("  hello   world  ") == "hello world"

    def test_removes_html_tags(self):
        out = validation.sanitize_text("break-in at <b>10XX MAIN</b> street")
        assert "<" not in out
        assert "break-in at" in out

    def test_neutralizes_script_payload(self):
        out = validation.sanitize_text("<script>alert(1)</script> stolen bike")
        assert "script" not in out.lower()
        assert "stolen bike" in out

    def test_neutralizes_javascript_uri(self):
        out = validation.sanitize_text("javascript:alert(1)")
        assert "javascript" not in out.lower()

    def test_enforces_max_length(self):
        assert len(validation.sanitize_text("x" * 500)) == validation.MAX_TEXT_LENGTH


class TestCrimeTypeValidation:
    def test_accepts_known_type(self):
        assert validation.validate_crime_type("Theft of Bicycle") == "Theft of Bicycle"

    def test_normalizes_whitespace(self):
        assert validation.validate_crime_type("  Mischief ") == "Mischief"

    def test_rejects_unknown_type(self):
        assert validation.validate_crime_type("Bank Robbery") is None

    def test_rejects_empty(self):
        assert validation.validate_crime_type("") is None


class TestNeighbourhoodValidation:
    def test_accepts_known_neighbourhood(self):
        assert validation.validate_neighbourhood("West End") == "West End"

    def test_rejects_unknown_neighbourhood(self):
        assert validation.validate_neighbourhood("Toronto Downtown") is None


class TestDateValidation:
    def test_accepts_past_date(self):
        assert validation.validate_date(date(2020, 5, 1)) is None

    def test_rejects_future_date(self):
        assert validation.validate_date(date(2100, 1, 1)) is not None

    def test_rejects_pre_2003_date(self):
        assert validation.validate_date(date(1999, 12, 31)) is not None


class TestValidateIncidentRecord:
    def make_valid(self):
        return {
            "crime_type": "Mischief",
            "incident_date": date(2024, 3, 10),
            "neighbourhood": "West End",
            "location": "10XX ROBSON ST",
            "notes": "test entry",
        }

    def test_valid_record_passes(self):
        ok, errors = validation.validate_incident_record(self.make_valid())
        assert ok and errors == {}

    def test_multiple_errors_collected(self):
        record = self.make_valid()
        record["crime_type"] = "Nope"
        record["incident_date"] = date(2100, 1, 1)
        record["neighbourhood"] = "Narnia"
        ok, errors = validation.validate_incident_record(record)
        assert not ok
        assert set(errors) == {"crime_type", "incident_date", "neighbourhood"}

    def test_missing_date_reported(self):
        record = self.make_valid()
        del record["incident_date"]
        ok, errors = validation.validate_incident_record(record)
        assert not ok and "incident_date" in errors

    def test_script_in_location_is_sanitized(self):
        record = self.make_valid()
        record["location"] = "<script>x</script> ROBSON"
        ok, errors = validation.validate_incident_record(record)
        assert ok  # sanitized value is still a usable location
