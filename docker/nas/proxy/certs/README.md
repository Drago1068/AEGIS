# Operator TLS certificate material (not committed)

Place PEM files here (or point `AEGIS_TLS_CERTS_DIR` at another host directory) when
`AEGIS_TLS_MODE=files`:

- `frontend.crt` / `frontend.key` — certificate for `AEGIS_TLS_FRONTEND_HOST`
- `api.crt` / `api.key` — certificate for `AEGIS_TLS_API_HOST`

A single SAN certificate may be copied to both name pairs if it covers both hostnames.

**Never commit real certificates or private keys.** This directory is gitignored except for
this README and `.gitkeep`.
