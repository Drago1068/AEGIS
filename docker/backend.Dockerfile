# syntax=docker/dockerfile:1
#
# Multi-stage build for the AEGIS backend. Pinned base images, non-root runtime user,
# lockfile-based non-editable production dependency installation (uv sync --locked --no-dev
# --no-editable). See docs/architecture/decisions/0001-phase-0-tooling.md.

FROM ghcr.io/astral-sh/uv:0.11.32 AS uv

FROM python:3.12.13-slim-bookworm AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

FROM base AS builder
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable

FROM base AS runtime
# Pick up Debian security patches published after the pinned base image tag was built (see
# docs/operations/security-scanning.md); the base image/package versions stay otherwise pinned.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd --system aegis \
    && useradd --system --gid aegis --home-dir /app --shell /usr/sbin/nologin aegis
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY alembic.ini ./
COPY alembic ./alembic
ENV PATH="/app/.venv/bin:$PATH"
USER aegis
EXPOSE 8000
CMD ["uvicorn", "aegis.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
