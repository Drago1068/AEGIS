# Shared helpers for AEGIS NAS shell scripts (Phase 7).
# Sourced by package.sh / deploy.sh / verify.sh / validate-local.sh.

set -euo pipefail

repo_root_from_script() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
  cd "${script_dir}/../../.." && pwd
}

load_dotenv_file() {
  local path="$1"
  if [[ ! -f "${path}" ]]; then
    echo "error: required env file not found: ${path}" >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  set -a
  # Parse KEY=VALUE lines; ignore comments/blank. Does not execute shell.
  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "${line}" || "${line}" == \#* ]] && continue
    [[ "${line}" != *=* ]] && continue
    local key="${line%%=*}"
    local value="${line#*=}"
    key="${key%"${key##*[![:space:]]}"}"
    key="${key#"${key%%[![:space:]]*}"}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    if [[ "${value}" == \"*\" && "${value}" == *\" ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "${value}" == \'*\' && "${value}" == *\' ]]; then
      value="${value:1:${#value}-2}"
    fi
    export "${key}=${value}"
  done < "${path}"
  set +a
}

require_env_vars() {
  local missing=()
  local name
  for name in "$@"; do
    if [[ -z "${!name:-}" ]]; then
      missing+=("${name}")
    fi
  done
  if ((${#missing[@]} > 0)); then
    echo "error: missing required environment variable(s): ${missing[*]}" >&2
    exit 1
  fi
}

assert_nas_secrets_not_placeholders() {
  local forbidden_operator=(
    "change-me-before-non-local-use"
    "replace-with-strong-non-default-nas-operator-password"
    "aegis"
    "operator"
  )
  local forbidden_db=(
    "aegis"
    "replace-with-strong-non-default-nas-db-password"
  )
  local p
  for p in "${forbidden_operator[@]}"; do
    if [[ "${AEGIS_OPERATOR_PASSWORD:-}" == "${p}" ]]; then
      echo "error: AEGIS_OPERATOR_PASSWORD must be a strong non-default value for NAS." >&2
      exit 1
    fi
  done
  for p in "${forbidden_db[@]}"; do
    if [[ "${POSTGRES_PASSWORD:-}" == "${p}" ]]; then
      echo "error: POSTGRES_PASSWORD must be a strong non-default value for NAS." >&2
      exit 1
    fi
  done
}

compose_nas_args() {
  local root="$1"
  local env_file="${root}/.env.nas"
  if [[ ! -f "${env_file}" ]]; then
    echo "error: missing .env.nas at repo root. Copy .env.nas.example and fill placeholders." >&2
    exit 1
  fi
  printf '%s\n' \
    -f "${root}/docker-compose.yml" \
    -f "${root}/docker/nas/docker-compose.nas.yml" \
    --env-file "${env_file}" \
    --project-directory "${root}"
}

ssh_base_args() {
  local port="${AEGIS_NAS_SSH_PORT:-22}"
  local args=(-p "${port}" -o BatchMode=yes -o StrictHostKeyChecking=accept-new)
  if [[ -n "${AEGIS_NAS_SSH_IDENTITY_FILE:-}" ]]; then
    args+=(-i "${AEGIS_NAS_SSH_IDENTITY_FILE}")
  fi
  printf '%s\n' "${args[@]}"
}

scp_base_args() {
  local port="${AEGIS_NAS_SSH_PORT:-22}"
  local args=(-P "${port}" -o BatchMode=yes -o StrictHostKeyChecking=accept-new)
  if [[ -n "${AEGIS_NAS_SSH_IDENTITY_FILE:-}" ]]; then
    args+=(-i "${AEGIS_NAS_SSH_IDENTITY_FILE}")
  fi
  printf '%s\n' "${args[@]}"
}
