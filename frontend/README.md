# AEGIS 3.0 Frontend

Next.js operator console for AEGIS 3.0. See
[../docs/architecture/overview.md](../docs/architecture/overview.md) and
[../docs/architecture/decisions/0004-phase-3-operator-console.md](../docs/architecture/decisions/0004-phase-3-operator-console.md).

Phase 3 replaces the Phase 0 placeholder with:

- `/` - watchlist management and on-demand ingest
- `/symbols/[symbol]` - stored daily OHLCV table

Set `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`) so the browser can reach the
backend. The backend must allow that origin via `AEGIS_CORS_ORIGINS`.

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

No scoring, recommendation, prediction, or trading UI exists in this package.
