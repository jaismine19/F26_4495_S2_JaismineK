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
