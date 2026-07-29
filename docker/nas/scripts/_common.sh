# Shared helpers for AEGIS NAS shell scripts (Phase 7 + optional Phase 9 TLS).
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

nas_tls_enabled() {
  local v="${AEGIS_NAS_TLS_ENABLED:-false}"
  v="$(printf '%s' "${v}" | tr '[:upper:]' '[:lower:]')"
  [[ "${v}" == "true" || "${v}" == "1" || "${v}" == "yes" ]]
}

# Resolve a path that may be relative to docker/nas/ (TLS compose file directory).
resolve_nas_relative_path() {
  local root="$1"
  local raw="$2"
  if [[ "${raw}" = /* ]]; then
    printf '%s\n' "${raw}"
    return
  fi
  # Strip leading ./
  raw="${raw#./}"
  if [[ "${raw}" == docker/nas/* ]]; then
    printf '%s\n' "${root}/${raw}"
  else
    printf '%s\n' "${root}/docker/nas/${raw}"
  fi
}

assert_tls_profile_ready() {
  # Args: repo_root [--allow-example-placeholders]
  local root="$1"
  local allow_example=0
  if [[ "${2:-}" == "--allow-example-placeholders" ]]; then
    allow_example=1
  fi

  require_env_vars AEGIS_TLS_FRONTEND_HOST AEGIS_TLS_API_HOST AEGIS_TLS_MODE

  if [[ "${allow_example}" -eq 0 ]]; then
    if [[ "${AEGIS_TLS_FRONTEND_HOST}" == replace-with-* || "${AEGIS_TLS_API_HOST}" == replace-with-* ]]; then
      echo "error: AEGIS_TLS_FRONTEND_HOST / AEGIS_TLS_API_HOST still look like placeholders." >&2
      exit 1
    fi
  fi

  local secure
  secure="$(printf '%s' "${AEGIS_SESSION_COOKIE_SECURE:-}" | tr '[:upper:]' '[:lower:]')"
  if [[ "${secure}" != "true" && "${secure}" != "1" ]]; then
    echo "error: TLS profile requires AEGIS_SESSION_COOKIE_SECURE=true (Secure cookies need HTTPS)." >&2
    exit 1
  fi

  local url_vars=(
    AEGIS_CORS_ORIGINS
    NEXT_PUBLIC_API_BASE_URL
    AEGIS_NAS_API_BASE_URL
    AEGIS_NAS_FRONTEND_BASE_URL
  )
  local name
  for name in "${url_vars[@]}"; do
    local val="${!name:-}"
    if [[ -z "${val}" ]]; then
      continue
    fi
    if [[ "${val}" == http://* ]]; then
      echo "error: ${name} must use https:// when the TLS profile is enabled (got HTTP)." >&2
      echo "  Secure cookies will not be sent by browsers over plain HTTP." >&2
      exit 1
    fi
    if [[ "${allow_example}" -eq 0 && "${val}" != https://* && "${val}" == *replace-with-* ]]; then
      echo "error: ${name} still looks incomplete for TLS." >&2
      exit 1
    fi
    if [[ "${allow_example}" -eq 0 && "${val}" != https://* ]]; then
      echo "error: ${name} must be an https:// origin when TLS is enabled." >&2
      exit 1
    fi
  done

  local mode
  mode="$(printf '%s' "${AEGIS_TLS_MODE}" | tr '[:upper:]' '[:lower:]')"
  case "${mode}" in
    files)
      export AEGIS_TLS_CADDYFILE="${AEGIS_TLS_CADDYFILE:-./proxy/Caddyfile.files}"
      local certs_dir
      certs_dir="$(resolve_nas_relative_path "${root}" "${AEGIS_TLS_CERTS_DIR:-./proxy/certs}")"
      if [[ "${allow_example}" -eq 1 ]]; then
        echo "NOTE: TLS files mode with example env — compose config only; PEM presence not enforced."
      else
        local required=(frontend.crt frontend.key api.crt api.key)
        local f
        for f in "${required[@]}"; do
          if [[ ! -f "${certs_dir}/${f}" ]]; then
            echo "error: TLS files mode missing ${certs_dir}/${f}" >&2
            echo "  Provide operator PEMs or switch AEGIS_TLS_MODE=acme when network allows." >&2
            exit 1
          fi
        done
      fi
      ;;
    acme)
      export AEGIS_TLS_CADDYFILE="${AEGIS_TLS_CADDYFILE:-./proxy/Caddyfile.acme}"
      require_env_vars AEGIS_TLS_ACME_EMAIL
      if [[ "${allow_example}" -eq 0 && "${AEGIS_TLS_ACME_EMAIL}" == replace-with-* ]]; then
        echo "error: AEGIS_TLS_ACME_EMAIL still looks like a placeholder." >&2
        exit 1
      fi
      ;;
    *)
      echo "error: AEGIS_TLS_MODE must be 'files' or 'acme' (got: ${AEGIS_TLS_MODE})." >&2
      exit 1
      ;;
  esac
}

compose_nas_args() {
  local root="$1"
  local env_file="${2:-${root}/.env.nas}"
  if [[ ! -f "${env_file}" ]]; then
    echo "error: missing env file at ${env_file}. Copy .env.nas.example and fill placeholders." >&2
    exit 1
  fi
  local args=(
    -f "${root}/docker-compose.yml"
    -f "${root}/docker/nas/docker-compose.nas.yml"
  )
  if nas_tls_enabled; then
    args+=(-f "${root}/docker/nas/docker-compose.nas.tls.yml")
  fi
  args+=(--env-file "${env_file}" --project-directory "${root}")
  printf '%s\n' "${args[@]}"
}

compose_nas_file_flags() {
  # Prints only -f flags (for remote SSH snippets that already set --env-file).
  local root="$1"
  local args=(
    -f docker-compose.yml
    -f docker/nas/docker-compose.nas.yml
  )
  if nas_tls_enabled; then
    args+=(-f docker/nas/docker-compose.nas.tls.yml)
  fi
  printf '%s\n' "${args[@]}"
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
  local args=(-P "${port}" -O -o BatchMode=yes -o StrictHostKeyChecking=accept-new)
  if [[ -n "${AEGIS_NAS_SSH_IDENTITY_FILE:-}" ]]; then
    args+=(-i "${AEGIS_NAS_SSH_IDENTITY_FILE}")
  fi
  printf '%s\n' "${args[@]}"
}
