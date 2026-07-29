#!/usr/bin/env bash
# Transfer a NAS package over SSH/SCP, load images, start Compose, apply Alembic (Phase 7 + optional Phase 9 TLS).
# A successful upload is NOT a verified deployment — run verify.sh afterward.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
ENV_NAS="${REPO_ROOT}/.env.nas"
load_dotenv_file "${ENV_NAS}"
require_env_vars \
  AEGIS_NAS_SSH_HOST \
  AEGIS_NAS_SSH_USER \
  AEGIS_NAS_REMOTE_DIR \
  AEGIS_OPERATOR_PASSWORD \
  POSTGRES_PASSWORD \
  NEXT_PUBLIC_API_BASE_URL \
  AEGIS_CORS_ORIGINS
assert_nas_secrets_not_placeholders

if nas_tls_enabled; then
  assert_tls_profile_ready "${REPO_ROOT}"
fi

if [[ "${AEGIS_NAS_SSH_HOST}" == replace-with-* || "${AEGIS_NAS_SSH_HOST}" == your-* ]]; then
  echo "error: AEGIS_NAS_SSH_HOST still looks like a placeholder." >&2
  exit 1
fi

PACKAGE_DIR="${REPO_ROOT}/docker/nas/dist/aegis-nas-package"
IMAGES_TAR="${PACKAGE_DIR}/images/aegis-images-amd64.tar"
if [[ ! -f "${IMAGES_TAR}" ]]; then
  echo "error: package images missing at ${IMAGES_TAR}. Run package.sh first." >&2
  exit 1
fi

REMOTE="${AEGIS_NAS_SSH_USER}@${AEGIS_NAS_SSH_HOST}"
REMOTE_DIR="${AEGIS_NAS_REMOTE_DIR%/}"
mapfile -t SSH_ARGS < <(ssh_base_args)
mapfile -t SCP_ARGS < <(scp_base_args)
mapfile -t COMPOSE_FILES < <(compose_nas_file_flags "${REPO_ROOT}")
# shellcheck disable=SC2124
COMPOSE_FILE_ARGS="${COMPOSE_FILES[*]}"

echo "==> Ensuring remote directory exists: ${REMOTE_DIR}"
ssh "${SSH_ARGS[@]}" "${REMOTE}" "mkdir -p '${REMOTE_DIR}/images' '${REMOTE_DIR}/docker/nas/scripts' '${REMOTE_DIR}/docker/nas/proxy/certs'"

echo "==> Copying package files (compose, scripts, proxy templates, images, .env.nas)"
scp "${SCP_ARGS[@]}" \
  "${PACKAGE_DIR}/docker-compose.yml" \
  "${REMOTE}:${REMOTE_DIR}/docker-compose.yml"
scp "${SCP_ARGS[@]}" \
  "${PACKAGE_DIR}/docker/nas/docker-compose.nas.yml" \
  "${REMOTE}:${REMOTE_DIR}/docker/nas/docker-compose.nas.yml"
scp "${SCP_ARGS[@]}" \
  "${PACKAGE_DIR}/docker/nas/docker-compose.nas.tls.yml" \
  "${REMOTE}:${REMOTE_DIR}/docker/nas/docker-compose.nas.tls.yml"
scp "${SCP_ARGS[@]}" \
  "${PACKAGE_DIR}/docker/nas/README.md" \
  "${REMOTE}:${REMOTE_DIR}/docker/nas/README.md"
scp "${SCP_ARGS[@]}" -r \
  "${PACKAGE_DIR}/docker/nas/scripts" \
  "${REMOTE}:${REMOTE_DIR}/docker/nas/"
scp "${SCP_ARGS[@]}" \
  "${PACKAGE_DIR}/docker/nas/proxy/Caddyfile.files" \
  "${PACKAGE_DIR}/docker/nas/proxy/Caddyfile.acme" \
  "${PACKAGE_DIR}/docker/nas/proxy/README.md" \
  "${REMOTE}:${REMOTE_DIR}/docker/nas/proxy/"
scp "${SCP_ARGS[@]}" \
  "${PACKAGE_DIR}/docker/nas/proxy/certs/README.md" \
  "${PACKAGE_DIR}/docker/nas/proxy/certs/.gitkeep" \
  "${REMOTE}:${REMOTE_DIR}/docker/nas/proxy/certs/"
scp "${SCP_ARGS[@]}" \
  "${IMAGES_TAR}" \
  "${REMOTE}:${REMOTE_DIR}/images/aegis-images-amd64.tar"
scp "${SCP_ARGS[@]}" \
  "${ENV_NAS}" \
  "${REMOTE}:${REMOTE_DIR}/.env.nas"

# Operator PEMs are never packaged from git; copy from local certs dir when TLS files mode.
if nas_tls_enabled; then
  mode="$(printf '%s' "${AEGIS_TLS_MODE}" | tr '[:upper:]' '[:lower:]')"
  if [[ "${mode}" == "files" ]]; then
    certs_dir="$(resolve_nas_relative_path "${REPO_ROOT}" "${AEGIS_TLS_CERTS_DIR:-./proxy/certs}")"
    echo "==> Copying operator TLS PEMs from ${certs_dir}"
    for f in frontend.crt frontend.key api.crt api.key; do
      scp "${SCP_ARGS[@]}" "${certs_dir}/${f}" "${REMOTE}:${REMOTE_DIR}/docker/nas/proxy/certs/${f}"
    done
  fi
fi

echo "==> Remote load, start, and migrate"
ssh "${SSH_ARGS[@]}" "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd '${REMOTE_DIR}'
echo '==> Loading images'
docker load -i images/aegis-images-amd64.tar
echo '==> Starting NAS Compose stack'
docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas --project-directory . up -d --no-build
echo '==> Waiting for backend container'
for i in \$(seq 1 60); do
  if docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas --project-directory . ps --status running | grep -q backend; then
    break
  fi
  sleep 2
done
echo '==> Applying Alembic migrations (through 0005 / head)'
docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas --project-directory . exec -T backend alembic upgrade head
echo '==> Migration current revision'
docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas --project-directory . exec -T backend alembic current
echo 'Deploy start finished. Upload/start is NOT verification — run verify next.'
EOF

echo
echo "Deploy transfer and start completed."
if nas_tls_enabled; then
  echo "TLS profile was enabled (Caddy). Confirm HTTPS URLs before verify."
fi
echo "IMPORTANT: This is not a verified deployment. Run:"
echo "  ./docker/nas/scripts/verify.sh"
