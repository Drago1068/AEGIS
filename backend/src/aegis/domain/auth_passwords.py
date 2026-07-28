"""Password hashing helpers for operator authentication.

Framework-free per the domain module boundary in ``docs/architecture/overview.md``: no
FastAPI, SQLAlchemy, or Redis import belongs here. Uses Argon2 via ``pwdlib`` (see ADR-0005).
Callers must never log plaintext passwords or hashes in a way that re-exposes credentials.
"""

from __future__ import annotations

from pwdlib import PasswordHash

_PASSWORD_HASH = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return an Argon2 hash of ``password`` suitable for durable storage."""

    return _PASSWORD_HASH.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Return ``True`` if ``password`` matches ``password_hash``, else ``False``.

    Never raises on a mismatch; callers treat ``False`` as an authentication failure without
    distinguishing "unknown user" from "bad password" at the HTTP boundary.
    """

    return _PASSWORD_HASH.verify(password, password_hash)
