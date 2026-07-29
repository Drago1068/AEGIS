# syntax=docker/dockerfile:1
#
# Multi-stage build for the AEGIS frontend. Pinned base image, non-root runtime user,
# lockfile-based production install (pnpm install --frozen-lockfile), Next.js standalone
# output for a minimal final image. See docs/architecture/decisions/0001-phase-0-tooling.md.

FROM node:24.14.0-slim AS base
ENV PNPM_HOME="/pnpm" \
    PATH="/pnpm:$PATH" \
    NEXT_TELEMETRY_DISABLED=1
RUN corepack enable

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Inlined into the Next.js client bundle at build time (required for NAS package builds).
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
RUN pnpm build

FROM base AS runtime
# Pick up Debian security patches published after the pinned base image tag was built (see
# docs/operations/security-scanning.md), and remove the bundled npm CLI: this image only ever
# runs `node server.js` via pnpm/corepack at build time, never `npm`, and npm's own vendored
# dependencies (tar, minimatch, sigstore, etc.) are otherwise flagged by container scans for
# code that is never executed here.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /usr/local/bin/npx
RUN groupadd --system aegis \
    && useradd --system --gid aegis --home-dir /app --shell /usr/sbin/nologin aegis
WORKDIR /app
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0
COPY --from=builder /app/public ./public
COPY --from=builder --chown=aegis:aegis /app/.next/standalone ./
COPY --from=builder --chown=aegis:aegis /app/.next/static ./.next/static
USER aegis
EXPOSE 3000
CMD ["node", "server.js"]
