"""SQLite storage for user-entered prototype incidents.

Security notes (see docs/security/threat_model.md):
- Every query is parameterized; user input is never concatenated into SQL.
- User-entered records are tagged source='user' and kept in their own table,
  separate from the public VPD dataset.
- The database file lives under data/ and is gitignored.
"""
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "prototype.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crime_type TEXT NOT NULL,
    incident_date TEXT NOT NULL,
    neighbourhood TEXT NOT NULL,
    location TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'user',
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the incidents table if it does not exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(SCHEMA)


def insert_incident(record: dict, created_by: str) -> int:
    """Insert a validated incident record. Returns the new row id."""
    init_db()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO incidents "
            "(crime_type, incident_date, neighbourhood, location, notes, "
            " source, created_by, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record["crime_type"],
                record["incident_date"].isoformat(),
                record["neighbourhood"],
                record["location"],
                record.get("notes", ""),
                "user",
                created_by,
                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            ),
        )
        return int(cur.lastrowid)


def fetch_incidents(limit: int = 100) -> list[dict]:
    """Return the most recent user-entered incidents (newest first)."""
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, crime_type, incident_date, neighbourhood, location, "
            "notes, source, created_by, created_at "
            "FROM incidents ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
