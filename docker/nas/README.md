# UGREEN NAS Deployment Boundary

NAS deployment is explicitly out of scope for Phase 0. This directory intentionally contains
no deployment scripts.

## What Phase 0 does validate

- The backend and frontend Docker images build successfully for `linux/amd64` (the
  architecture used by UGREEN NAS DXP-series hardware), via a build-only step:

  ```sh
  docker buildx build --platform linux/amd64 -f docker/backend.Dockerfile ./backend
  docker buildx build --platform linux/amd64 -f docker/frontend.Dockerfile ./frontend
  ```

  This confirms buildability only. It does not push, run, or deploy any image, and it does
  not connect to any NAS.

## What Phase 0 does not do

- No NAS hostname, IP address, credential, or SSH key exists anywhere in this repository.
- No script in this repository connects to, copies files to, or runs anything on a NAS.
- No CI job targets the NAS.

## Before NAS deployment is implemented

Per the project rules, deployment to the NAS happens only after the current phase's local
acceptance checks pass and are reviewed. When that work begins, it will:

- Live in this directory as explicit, reviewed scripts (for example a
  `docker compose -f docker-compose.nas.yml` topology, or a documented manual deployment
  runbook).
- Source every NAS-specific value (hostname, credentials, paths) from environment variables
  or a local, gitignored configuration file - never hardcoded.
- Include a documented verification step (health checks, API routes, browser behavior, and
  log inspection on the NAS) distinct from the act of uploading a package, per the project
  rule that a successful upload is not the same as a verified live deployment.

## Target architecture note

UGREEN NAS DXP-series hardware (the reference deployment target) uses Intel x86_64
processors, hence `linux/amd64` above. If a different specific NAS model with a different
CPU architecture is used, update the `--platform` value here and in
`docs/architecture/decisions/0001-phase-0-tooling.md`.
