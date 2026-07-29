# AEGIS 3.0 Frontend

Next.js operator console for AEGIS 3.0. See
[../docs/architecture/overview.md](../docs/architecture/overview.md),
[../docs/architecture/decisions/0004-phase-3-operator-console.md](../docs/architecture/decisions/0004-phase-3-operator-console.md),
[../docs/architecture/decisions/0005-phase-4-operator-auth.md](../docs/architecture/decisions/0005-phase-4-operator-auth.md),
and
[../docs/architecture/decisions/0006-phase-5-daily-bar-charts.md](../docs/architecture/decisions/0006-phase-5-daily-bar-charts.md),
and
[../docs/architecture/decisions/0007-phase-6-research-only-scoring.md](../docs/architecture/decisions/0007-phase-6-research-only-scoring.md).

Phase 3 added the console surfaces; Phase 4 adds login; Phase 5 adds daily-bar charts;
Phase 6 adds research-only assessments:

- `/login` - operator username/password; session cookie via the backend
- `/` - watchlist management and on-demand ingest (requires a valid session)
- `/symbols/[symbol]` - daily OHLC candlestick + volume chart above the stored OHLCV table,
  plus a RESEARCH ONLY assessment panel fed by authenticated `/research` APIs (no client-side
  research math)

Set `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`) so the browser can reach the
backend. The backend must allow that origin via `AEGIS_CORS_ORIGINS` with credentials
enabled. Sign in with the bootstrap operator credentials from `.env`
(`AEGIS_OPERATOR_USERNAME` / `AEGIS_OPERATOR_PASSWORD`). Authenticated API calls use
`credentials: "include"`; HTTP 401 redirects to `/login`.

## Commands

```sh
pnpm install
pnpm dev
pnpm test
pnpm lint
pnpm exec tsc --noEmit
pnpm run check:no-domain-logic
pnpm build
```

No recommendation, prediction, trading, or order-placement UI exists in this package.
Research assessment values are displayed from the API only.
