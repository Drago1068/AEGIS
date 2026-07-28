"""Unit tests for operator auth endpoints, via dependency overrides.

No real database or Redis: operator repository and session store are substituted with
in-memory fakes. Passwords are never logged.
"""

from __future__ import annotations

from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import get_operator_repository, get_session_store, require_operator
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.auth_passwords import hash_password, verify_password
from aegis.persistence.models import Operator
from aegis.persistence.sessions import SessionData

_COOKIE = "aegis_session"
_USERNAME = "operator"
_PASSWORD = "change-me-before-non-local-use"


class _InMemorySessionStore:
    def __init__(self) -> None:
        self.sessions: dict[str, SessionData] = {}
        self._next_id = 0

    async def create(self, operator_id: int, username: str) -> str:
        self._next_id += 1
        session_id = f"session-{self._next_id}"
        self.sessions[session_id] = SessionData(operator_id=operator_id, username=username)
        return session_id

    async def get(self, session_id: str) -> SessionData | None:
        return self.sessions.get(session_id)

    async def delete(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)


class _FakeOperatorRepository:
    def __init__(self) -> None:
        self._operators: dict[str, Operator] = {}
        self.seed_calls = 0

    async def get_by_username(self, username: str) -> Operator | None:
        return self._operators.get(username)

    async def ensure_seeded(self, username: str, password: str) -> None:
        self.seed_calls += 1
        if self._operators:
            return
        self._operators[username] = Operator(
            id=1,
            username=username,
            password_hash=hash_password(password),
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, tzinfo=UTC),
        )


def _settings() -> Settings:
    return Settings(
        environment="test",
        operator_username=_USERNAME,
        operator_password=_PASSWORD,
        session_cookie_name=_COOKIE,
        session_ttl_seconds=3600,
        session_cookie_secure=False,
        ingestion_schedule_enabled=False,
    )


def _client(
    repository: _FakeOperatorRepository,
    session_store: _InMemorySessionStore,
) -> AsyncClient:
    app = create_app(settings=_settings())
    app.dependency_overrides[get_operator_repository] = lambda: repository
    app.dependency_overrides[get_session_store] = lambda: session_store
    # require_operator uses the real implementation with overridden deps above.
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def test_login_success_sets_httponly_session_cookie() -> None:
    repository = _FakeOperatorRepository()
    session_store = _InMemorySessionStore()

    async with _client(repository, session_store) as client:
        response = await client.post(
            "/auth/login",
            json={"username": _USERNAME, "password": _PASSWORD},
        )

    assert response.status_code == 200
    assert response.json() == {"username": _USERNAME}
    assert _COOKIE in response.cookies
    set_cookie = response.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie
    assert "Path=/" in set_cookie
    assert repository.seed_calls == 1
    assert len(session_store.sessions) == 1


async def test_login_failure_rejects_bad_password() -> None:
    repository = _FakeOperatorRepository()
    session_store = _InMemorySessionStore()

    async with _client(repository, session_store) as client:
        response = await client.post(
            "/auth/login",
            json={"username": _USERNAME, "password": "wrong-password"},
        )

    assert response.status_code == 401
    assert _COOKIE not in response.cookies
    assert session_store.sessions == {}


async def test_protected_route_returns_401_without_cookie() -> None:
    repository = _FakeOperatorRepository()
    session_store = _InMemorySessionStore()
    app = create_app(settings=_settings())
    app.dependency_overrides[get_operator_repository] = lambda: repository
    app.dependency_overrides[get_session_store] = lambda: session_store

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/watchlist")

    assert response.status_code == 401


async def test_logout_clears_session_and_cookie() -> None:
    repository = _FakeOperatorRepository()
    session_store = _InMemorySessionStore()

    async with _client(repository, session_store) as client:
        login = await client.post(
            "/auth/login",
            json={"username": _USERNAME, "password": _PASSWORD},
        )
        assert login.status_code == 200
        session_id = login.cookies[_COOKIE]
        assert session_id in session_store.sessions

        me = await client.get("/auth/me")
        assert me.status_code == 200
        assert me.json() == {"username": _USERNAME}

        logout = await client.post("/auth/logout")
        assert logout.status_code == 204
        assert session_id not in session_store.sessions

        me_after = await client.get("/auth/me")
        assert me_after.status_code == 401


async def test_ensure_seeded_runs_once_and_ignores_later_env_password() -> None:
    repository = _FakeOperatorRepository()
    session_store = _InMemorySessionStore()

    async with _client(repository, session_store) as client:
        first = await client.post(
            "/auth/login",
            json={"username": _USERNAME, "password": _PASSWORD},
        )
        assert first.status_code == 200
        assert repository.seed_calls == 1

        original = await repository.get_by_username(_USERNAME)
        assert original is not None
        original_hash = original.password_hash

        # Simulate a subsequent ensure_seeded with a different env password (e.g. settings
        # change after first seed). The stored hash must not change.
        await repository.ensure_seeded(_USERNAME, "a-different-env-password")
        assert repository.seed_calls == 2
        again = await repository.get_by_username(_USERNAME)
        assert again is not None
        assert again.password_hash == original_hash
        assert verify_password(_PASSWORD, again.password_hash) is True
        assert verify_password("a-different-env-password", again.password_hash) is False

        second_login = await client.post(
            "/auth/login",
            json={"username": _USERNAME, "password": _PASSWORD},
        )
        assert second_login.status_code == 200


async def test_require_operator_override_allows_protected_route_without_cookie() -> None:
    """Existing watchlist/market-data unit tests override require_operator this way."""

    operator = Operator(
        id=1,
        username=_USERNAME,
        password_hash="unused-in-override",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        updated_at=datetime(2024, 1, 1, tzinfo=UTC),
    )
    app = create_app(settings=_settings())
    app.dependency_overrides[require_operator] = lambda: operator
    # Still need a watchlist repo for the route body; empty fake via override would be needed
    # for a full 200 - this test only asserts the auth gate is bypassed (not 401).
    from aegis.api.dependencies import get_watchlist_repository

    class _EmptyWatchlist:
        async def list_active_rows(self) -> list[object]:
            return []

    app.dependency_overrides[get_watchlist_repository] = lambda: _EmptyWatchlist()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/watchlist")

    assert response.status_code == 200
    assert response.json() == []
