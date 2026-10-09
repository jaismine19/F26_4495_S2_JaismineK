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
import secrets

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
