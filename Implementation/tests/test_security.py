"""Security-focused tests for auth utilities (audit log, login attempts).

Run from the repository root:
    pytest Implementation/tests/test_security.py -v
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.utils import auth  # noqa: E402


class TestAuditLog:
    def test_log_and_read_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(auth, "AUDIT_LOG_PATH", tmp_path / "audit.jsonl")
        auth.log_audit("admin", "login_success", "local demo")
        entries = auth.read_audit_log()
        assert len(entries) == 1
        assert entries[0]["user_id"] == "admin"
        assert entries[0]["event"] == "login_success"
        assert "timestamp_utc" in entries[0]

    def test_rejects_unknown_event(self, tmp_path, monkeypatch):
        monkeypatch.setattr(auth, "AUDIT_LOG_PATH", tmp_path / "audit.jsonl")
        with pytest.raises(ValueError):
            auth.log_audit("admin", "hacked_event")

    def test_empty_when_no_log_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(auth, "AUDIT_LOG_PATH", tmp_path / "missing.jsonl")
        assert auth.read_audit_log() == []


class TestLoginAttempts:
    def test_lockout_after_max_failures(self):
        auth.reset_attempts("attacker")
        for _ in range(auth.MAX_FAILED_ATTEMPTS - 1):
            assert not auth.record_failed_attempt("attacker")
        assert auth.record_failed_attempt("attacker")
        assert auth.is_locked_out("attacker")

    def test_username_case_insensitive(self):
        auth.reset_attempts("attacker")
        for _ in range(auth.MAX_FAILED_ATTEMPTS):
            auth.record_failed_attempt("ATTACKER")
        assert auth.is_locked_out("attacker")

    def test_reset_clears_lockout(self):
        auth.reset_attempts("attacker")
        for _ in range(auth.MAX_FAILED_ATTEMPTS):
            auth.record_failed_attempt("attacker")
        auth.reset_attempts("attacker")
        assert not auth.is_locked_out("attacker")


class TestRoleBasedAccess:
    def test_permission_matrix(self):
        admin = auth.ROLE_PERMISSIONS["Administrator"]
        analyst = auth.ROLE_PERMISSIONS["Analyst"]
        entry = auth.ROLE_PERMISSIONS["Data Entry"]

        assert "view_audit" in admin
        assert "view_audit" not in analyst
        assert "view_audit" not in entry

        assert "view_all" in analyst
        assert "view_all" not in entry

        assert "add_incident" in admin
        assert "add_incident" in analyst
        assert "add_incident" in entry

    def test_has_permission_admin(self):
        user = {"username": "admin", "role": "Administrator",
                "permissions": auth.ROLE_PERMISSIONS["Administrator"]}
        assert auth.has_permission(user, "view_audit")
        assert auth.has_permission(user, "add_incident")

    def test_has_permission_entry_limited(self):
        user = {"username": "entry", "role": "Data Entry",
                "permissions": auth.ROLE_PERMISSIONS["Data Entry"]}
        assert auth.has_permission(user, "add_incident")
        assert not auth.has_permission(user, "view_audit")
        assert not auth.has_permission(user, "view_all")

    def test_has_permission_anonymous(self):
        assert not auth.has_permission(None, "add_incident")
        assert not auth.has_permission(None, "view_audit")


class TestPasswordVerification:
    def test_correct_password_authenticates(self):
        user = auth.authenticate("admin", "demo_admin_123")
        assert user is not None
        assert user["username"] == "admin"
        assert user["role"] == "Administrator"
        assert "password" not in user

    def test_wrong_password_rejected(self):
        assert auth.authenticate("admin", "wrong_password") is None

    def test_unknown_user_rejected(self):
        assert auth.authenticate("nobody", "demo_admin_123") is None

    def test_username_case_insensitive_login(self):
        assert auth.authenticate("ADMIN", "demo_admin_123") is not None
