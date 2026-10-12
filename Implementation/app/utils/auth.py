"""Authentication and role-based access control utilities.

Prototype implementation notes:
- Uses PBKDF2-HMAC-SHA256 from the Python standard library so the skeleton
  runs without extra dependencies.
- The threat model (docs/security/threat_model.md) plans an upgrade to
  bcrypt/argon2 and per-user salts before any non-demo deployment.
- Demo users below are clearly marked; their passwords must never be used
  outside classroom demos.
"""
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path

ROLES = ["Administrator", "Analyst", "Data Entry"]

ROLE_PERMISSIONS = {
    "Administrator": {"view_all", "add_incident", "manage_users", "view_audit"},
    "Analyst": {"view_all", "add_incident"},
    "Data Entry": {"add_incident"},
}

ITERATIONS = 200_000

DEMO_USERS = {
    "admin": {
        "password_hash": "93b2f2299ce1e2951221882120017a51070dc886134ec61512ca71a1dd7da666",
        "salt": "40b1c4d9aded2db4b8f231711a611302",
        "role": "Administrator",
        "password": "demo_admin_123",
    },
    "analyst": {
        "password_hash": "444018535e53953b710f7dc4f535355ff98796a75595e6e805c2830b2f395da8",
        "salt": "d360cd6cdbebdb787769407c5eb068f3",
        "role": "Analyst",
        "password": "demo_analyst_123",
    },
    "entry": {
        "password_hash": "c8d29dff00ad3e6d77a04d5139f3b520ff881156ee0bf256590f9c28ca99d299",
        "salt": "d69e1fc5bb656399d1a3c6b2a5e6e9df",
        "role": "Data Entry",
        "password": "demo_entry_123",
    },
}


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """Return (hex digest, hex salt) for a password using PBKDF2."""
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, ITERATIONS
    )
    return digest.hex(), salt.hex()


def verify_password(password: str, stored_hash: str, salt_hex: str) -> bool:
    """Constant-time password verification."""
    digest, _ = hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(digest, stored_hash)


def authenticate(username: str, password: str) -> dict | None:
    """Check a username/password against the demo user store.

    Returns the user dict (without the demo password) on success, else None.
    """
    user = DEMO_USERS.get(username.strip().lower())
    if user is None:
        return None
    if not verify_password(password, user["password_hash"], user["salt"]):
        return None
    return {
        "username": username.strip().lower(),
        "role": user["role"],
        "permissions": ROLE_PERMISSIONS[user["role"]],
    }


def has_permission(user: dict | None, permission: str) -> bool:
    """True if the logged-in user (or None) holds the permission."""
    if user is None:
        return False
    return permission in user.get("permissions", set())


# ------------------------------------------------------------ audit logging
# Prototype audit log: in-memory + optional file, append-only, timestamps in
# UTC. The threat model plans a database-backed audit table in a later phase.

AUDIT_LOG_PATH = Path(__file__).resolve().parents[3] / "data" / "audit_log.jsonl"

AUDIT_EVENTS = ("login_success", "login_failure", "logout", "incident_added")


def log_audit(user_id: str | None, event: str, detail: str = "") -> None:
    """Append an audit entry (append-only)."""
    if event not in AUDIT_EVENTS:
        raise ValueError(f"Unknown audit event: {event}")
    entry = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "user_id": user_id,
        "event": event,
        "detail": detail,
    }
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_audit_log() -> list[dict]:
    """Read all audit entries (newest last)."""
    if not AUDIT_LOG_PATH.exists():
        return []
    entries = []
    for line in AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


# ------------------------------------------------------ login attempt limits
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 60

_attempts: dict[str, list[float]] = {}


def record_failed_attempt(username: str) -> bool:
    """Record a failed login for a username.

    Returns True if the username is now locked out.
    """
    now = time.time()
    key = username.strip().lower()
    cutoff = now - LOCKOUT_SECONDS
    _attempts[key] = [t for t in _attempts.get(key, []) if t > cutoff]
    _attempts[key].append(now)
    return len(_attempts[key]) >= MAX_FAILED_ATTEMPTS


def is_locked_out(username: str) -> bool:
    """True if the username has too many recent failed attempts."""
    key = username.strip().lower()
    cutoff = time.time() - LOCKOUT_SECONDS
    recent = [t for t in _attempts.get(key, []) if t > cutoff]
    return len(recent) >= MAX_FAILED_ATTEMPTS


def reset_attempts(username: str) -> None:
    """Clear failed-attempt history for a username (after a successful login)."""
    _attempts.pop(username.strip().lower(), None)
