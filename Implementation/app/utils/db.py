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
    hour INTEGER,
    neighbourhood TEXT NOT NULL,
    location TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'user',
    created_by TEXT NOT NULL,
    created_role TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
"""


# Columns added after the original schema; used to upgrade databases
# created by older code (CREATE TABLE IF NOT EXISTS alone will not).
COLUMN_MIGRATIONS = {
    "hour": "INTEGER",
    "created_role": "TEXT NOT NULL DEFAULT ''",
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Add any missing columns to databases created by older code."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(incidents)")}
    for column, decl in COLUMN_MIGRATIONS.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE incidents ADD COLUMN {column} {decl}")


def init_db() -> None:
    """Create the incidents table if needed and upgrade old schemas."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(SCHEMA)
        _migrate(conn)


def insert_incident(record: dict, created_by: str, created_role: str = "") -> int:
    """Insert a validated incident record. Returns the new row id."""
    init_db()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO incidents "
            "(crime_type, incident_date, hour, neighbourhood, location, notes, "
            " source, created_by, created_role, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record["crime_type"],
                record["incident_date"].isoformat(),
                record.get("hour"),
                record["neighbourhood"],
                record["location"],
                record.get("notes", ""),
                "user",
                created_by,
                created_role,
                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            ),
        )
        return int(cur.lastrowid)


def fetch_incidents(limit: int = 100, created_by: str | None = None) -> list[dict]:
    """Return the most recent user-entered incidents (newest first).

    When created_by is given, only that user's records are returned.
    """
    init_db()
    columns = (
        "id, crime_type, incident_date, hour, neighbourhood, location, "
        "notes, source, created_by, created_role, created_at"
    )
    with get_connection() as conn:
        if created_by:
            rows = conn.execute(
                f"SELECT {columns} FROM incidents WHERE created_by = ? "
                "ORDER BY id DESC LIMIT ?",
                (created_by, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT {columns} FROM incidents ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [dict(row) for row in rows]


def count_incidents() -> int:
    """Return the total number of stored user-entered incidents."""
    init_db()
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0])
