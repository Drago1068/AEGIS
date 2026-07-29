#!/usr/bin/env bash
# Build linux/amd64 images and stage a transferrable NAS package (Phase 7 + optional Phase 9 TLS).
# Requires a filled `.env.nas` at the repository root. Does not connect to any NAS.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
ENV_NAS="${REPO_ROOT}/.env.nas"
load_dotenv_file "${ENV_NAS}"
require_env_vars \
  NEXT_PUBLIC_API_BASE_URL \
  AEGIS_CORS_ORIGINS \
  AEGIS_OPERATOR_PASSWORD \
  POSTGRES_PASSWORD
assert_nas_secrets_not_placeholders

if nas_tls_enabled; then
  assert_tls_profile_ready "${REPO_ROOT}"
fi

DIST_DIR="${REPO_ROOT}/docker/nas/dist"
PACKAGE_DIR="${DIST_DIR}/aegis-nas-package"
IMAGES_TAR="${PACKAGE_DIR}/images/aegis-images-amd64.tar"

rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}/images" "${PACKAGE_DIR}/docker/nas/scripts" "${PACKAGE_DIR}/docker/nas/proxy"

mapfile -t COMPOSE_ARGS < <(compose_nas_args "${REPO_ROOT}")

echo "==> Validating NAS Compose overlay"
docker compose "${COMPOSE_ARGS[@]}" config --quiet

echo "==> Building linux/amd64 images (backend + frontend)"
docker compose "${COMPOSE_ARGS[@]}" build --pull

echo "==> Resolving image names for docker save"
mapfile -t IMAGES < <(docker compose "${COMPOSE_ARGS[@]}" config --images | sed '/^$/d')
if ((${#IMAGES[@]} < 2)); then
  echo "error: expected at least backend and frontend images; got: ${IMAGES[*]-}" >&2
  exit 1
fi

echo "==> Saving images to ${IMAGES_TAR}"
docker save -o "${IMAGES_TAR}" "${IMAGES[@]}"

echo "==> Staging package files"
cp "${REPO_ROOT}/docker-compose.yml" "${PACKAGE_DIR}/docker-compose.yml"
cp "${REPO_ROOT}/docker/nas/docker-compose.nas.yml" "${PACKAGE_DIR}/docker/nas/docker-compose.nas.yml"
cp "${REPO_ROOT}/docker/nas/docker-compose.nas.tls.yml" "${PACKAGE_DIR}/docker/nas/docker-compose.nas.tls.yml"
cp "${REPO_ROOT}/docker/nas/README.md" "${PACKAGE_DIR}/docker/nas/README.md"
cp "${REPO_ROOT}/.env.nas.example" "${PACKAGE_DIR}/.env.nas.example"
cp -R "${REPO_ROOT}/docker/nas/scripts/." "${PACKAGE_DIR}/docker/nas/scripts/"
# Proxy templates only (never copy real PEMs from certs/).
cp "${REPO_ROOT}/docker/nas/proxy/Caddyfile.files" "${PACKAGE_DIR}/docker/nas/proxy/Caddyfile.files"
cp "${REPO_ROOT}/docker/nas/proxy/Caddyfile.acme" "${PACKAGE_DIR}/docker/nas/proxy/Caddyfile.acme"
cp "${REPO_ROOT}/docker/nas/proxy/README.md" "${PACKAGE_DIR}/docker/nas/proxy/README.md"
mkdir -p "${PACKAGE_DIR}/docker/nas/proxy/certs"
cp "${REPO_ROOT}/docker/nas/proxy/certs/README.md" "${PACKAGE_DIR}/docker/nas/proxy/certs/README.md"
cp "${REPO_ROOT}/docker/nas/proxy/certs/.gitkeep" "${PACKAGE_DIR}/docker/nas/proxy/certs/.gitkeep"

ARCHIVE_PATH="${DIST_DIR}/aegis-nas-package.tar.gz"
tar -C "${PACKAGE_DIR}" -czf "${ARCHIVE_PATH}" .

echo
echo "Package ready:"
echo "  Directory: ${PACKAGE_DIR}"
echo "  Archive:   ${ARCHIVE_PATH}"
if nas_tls_enabled; then
  echo "  TLS:       enabled (Caddy overlay included; ensure PEMs or ACME on the NAS)"
fi
echo
echo "Next: run deploy.sh (transfer + start). Upload alone is NOT a verified deployment;"
echo "      run verify.sh after the stack is up."
