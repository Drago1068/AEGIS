#!/usr/bin/env bash
# Generate self-signed lab PEMs for Phase 40 NAS TLS cutover (ADR-0041).
# Never commit the generated files (gitignored).
set -euo pipefail

FRONTEND_HOST="${1:-aegis.local}"
API_HOST="${2:-api.aegis.local}"
DAYS="${3:-825}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CERTS_DIR="${REPO_ROOT}/docker/nas/proxy/certs"

if ! command -v openssl >/dev/null 2>&1; then
  echo "error: openssl not found on PATH" >&2
  exit 1
fi

mkdir -p "${CERTS_DIR}"

gen_cert() {
  local cn="$1"
  local prefix="$2"
  local key_path="${CERTS_DIR}/${prefix}.key"
  local crt_path="${CERTS_DIR}/${prefix}.crt"
  local cfg_path="${CERTS_DIR}/${prefix}.openssl.cnf"
  cat >"${cfg_path}" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
CN = ${cn}

[v3_req]
subjectAltName = @alt_names
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = ${cn}
EOF
  openssl req -x509 -nodes -newkey rsa:2048 \
    -keyout "${key_path}" -out "${crt_path}" -days "${DAYS}" -config "${cfg_path}"
  rm -f "${cfg_path}"
  echo "Wrote ${crt_path} and ${key_path} (CN/SAN=${cn})"
}

gen_cert "${FRONTEND_HOST}" "frontend"
gen_cert "${API_HOST}" "api"
echo "Lab PEMs ready under ${CERTS_DIR} (gitignored — do not commit)."
