"""Input validation for the prototype incident-entry feature.

Security controls implemented here (see docs/security/threat_model.md):
- Allow-list validation for crime type and neighbourhood (A01 Broken Access
  Control / A03 Injection defense-in-depth).
- Strict date range checks (no future or pre-2003 dates).
- Text sanitization: length limits, whitespace normalization, and removal of
  HTML/script markup to reduce stored-XSS risk (A03).

All functions are pure and stdlib-only so they can be unit tested and reused
server-side before any record is written to the database.
"""
import re
from datetime import date

ALLOWED_CRIME_TYPES = frozenset(
    [
        "Break and Enter Commercial",
        "Break and Enter Residential/Other",
        "Homicide",
        "Mischief",
        "Offence Against a Person",
        "Other Theft",
        "Theft from Vehicle",
        "Theft of Bicycle",
        "Theft of Vehicle",
        "Vehicle Collision or Pedestrian Struck (with Fatality)",
        "Vehicle Collision or Pedestrian Struck (with Injury)",
    ]
)

ALLOWED_NEIGHBOURHOODS = frozenset(
    [
        "Arbutus Ridge", "Central Business District", "Dunbar-Southlands",
        "Fairview", "Grandview-Woodland", "Hastings-Sunrise",
        "Kensington-Cedar Cottage", "Kerrisdale", "Killarney", "Kitsilano",
        "Marpole", "Mount Pleasant", "Musqueam", "Oakridge",
        "Renfrew-Collingwood", "Riley Park", "Shaughnessy", "South Cambie",
        "Stanley Park", "Strathcona", "Sunset", "Victoria-Fraserview",
        "West End", "West Point Grey",
    ]
)

EARLIEST_YEAR = 2003
MAX_TEXT_LENGTH = 200
MAX_LOCATION_LENGTH = 100

_HTML_TAG_RE = re.compile(r"<[^>]*>")
_SCRIPT_RE = re.compile(r"(?i)(javascript\s*:|<\s*script|on\w+\s*=)")


def sanitize_text(value: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    """Normalize a text field: strip, collapse whitespace, drop markup."""
    cleaned = value.strip()
    cleaned = _HTML_TAG_RE.sub(" ", cleaned)
    cleaned = _SCRIPT_RE.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:max_length].strip()


def validate_crime_type(value: str) -> str | None:
    """Return the normalized crime type, or None if not allowed."""
    value = sanitize_text(value, MAX_TEXT_LENGTH)
    return value if value in ALLOWED_CRIME_TYPES else None


def validate_neighbourhood(value: str) -> str | None:
    """Return the normalized neighbourhood, or None if not allowed."""
    value = sanitize_text(value, MAX_TEXT_LENGTH)
    return value if value in ALLOWED_NEIGHBOURHOODS else None


def validate_date(value: date) -> str | None:
    """Return an error message for an invalid date, else None.

    Prototype rules: dates must be within the historical range (2003 onwards)
    and must not be in the future.
    """
    if value.year < EARLIEST_YEAR:
        return f"Date must be in {EARLIEST_YEAR} or later."
    if value > date.today():
        return "Date cannot be in the future."
    return None


def validate_location(value: str) -> tuple[str | None, str]:
    """Sanitize a free-text location; return (error, cleaned value)."""
    cleaned = sanitize_text(value, MAX_LOCATION_LENGTH)
    if not cleaned:
        return "Location cannot be empty.", cleaned
    return None, cleaned


def validate_notes(value: str) -> str:
    """Sanitize the optional notes field (no error states)."""
    return sanitize_text(value, MAX_TEXT_LENGTH)


def validate_incident_record(record: dict) -> tuple[bool, dict]:
    """Validate a full incident submission.

    Expects keys: crime_type, incident_date (date), neighbourhood, location,
    notes. Returns (is_valid, errors) where errors is {field: message}.
    """
    errors: dict = {}

    crime_type = record.get("crime_type", "")
    if validate_crime_type(crime_type) is None:
        errors["crime_type"] = "Not a recognized crime type."

    incident_date = record.get("incident_date")
    if not isinstance(incident_date, date):
        errors["incident_date"] = "A valid date is required."
    else:
        date_error = validate_date(incident_date)
        if date_error:
            errors["incident_date"] = date_error

    neighbourhood = record.get("neighbourhood", "")
    if validate_neighbourhood(neighbourhood) is None:
        errors["neighbourhood"] = "Not a recognized Vancouver neighbourhood."

    location_error, _ = validate_location(record.get("location", ""))
    if location_error:
        errors["location"] = location_error

    if "notes" in record:
        validate_notes(record["notes"])

    return (len(errors) == 0), errors
