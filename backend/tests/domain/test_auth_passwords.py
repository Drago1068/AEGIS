"""Unit tests for Argon2 password hashing helpers."""

from __future__ import annotations

from aegis.domain.auth_passwords import hash_password, verify_password


def test_hash_password_is_not_plaintext() -> None:
    password = "change-me-before-non-local-use"
    digest = hash_password(password)
    assert digest != password
    assert digest.startswith("$argon2")


def test_verify_password_accepts_matching_password() -> None:
    password = "correct-horse"
    digest = hash_password(password)
    assert verify_password(password, digest) is True


def test_verify_password_rejects_mismatch() -> None:
    digest = hash_password("correct-horse")
    assert verify_password("wrong-password", digest) is False
