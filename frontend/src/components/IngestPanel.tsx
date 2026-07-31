"use client";

import { useState, useTransition } from "react";

import {
  ApiClientError,
  IngestionRunResponse,
  getApiBaseUrl,
  ingestMarketData,
} from "@/lib/api-client";

export function IngestPanel() {
  const [result, setResult] = useState<IngestionRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const baseUrl = getApiBaseUrl();

  function onIngest() {
    startTransition(async () => {
      setError(null);
      try {
        const run = await ingestMarketData(baseUrl);
        setResult(run);
      } catch (err) {
        setResult(null);
        setError(err instanceof ApiClientError ? err.message : "Ingestion failed.");
      }
    });
  }

  return (
    <section className="rounded-lg border border-aegis-line bg-aegis-panel p-5 shadow-sm">
      <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-aegis-ink">On-demand ingest</h2>
          <p className="text-sm text-aegis-muted">
            Runs one cycle over the active database watchlist
          </p>
        </div>
        <button
          type="button"
          onClick={onIngest}
          disabled={isPending}
          className="rounded bg-aegis-ink px-4 py-2 font-medium text-white transition hover:brightness-110 disabled:opacity-60"
        >
          {isPending ? "Running..." : "Run ingest"}
        </button>
      </header>

      {error ? (
        <p className="text-sm text-aegis-danger" role="alert">
          {error}
        </p>
      ) : null}

      {result ? (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-aegis-line text-aegis-muted">
              <tr>
                <th className="py-2 pr-4 font-medium">Symbol</th>
                <th className="py-2 pr-4 font-medium">Stored</th>
                <th className="py-2 pr-4 font-medium">Skipped</th>
                <th className="py-2 pr-4 font-medium">Rejected</th>
                <th className="py-2 pr-4 font-medium">Provider tip</th>
                <th className="py-2 pr-4 font-medium">Tip source</th>
                <th className="py-2 font-medium">Error</th>
              </tr>
            </thead>
            <tbody>
              {result.results.map((row) => (
                <tr key={row.symbol} className="border-b border-aegis-line/70">
                  <td className="py-2 pr-4 font-mono font-medium">{row.symbol}</td>
                  <td className="py-2 pr-4 font-mono">{row.stored_count}</td>
                  <td className="py-2 pr-4 font-mono">{row.skipped_existing_count}</td>
                  <td className="py-2 pr-4 font-mono">{row.rejected_count}</td>
                  <td
                    className="py-2 pr-4 font-mono"
                    data-testid={`ingest-latest-trading-date-${row.symbol}`}
                  >
                    {row.latest_trading_date ?? "—"}
                  </td>
                  <td
                    className="py-2 pr-4 font-mono"
                    data-testid={`ingest-latest-trading-date-source-${row.symbol}`}
                  >
                    {row.latest_trading_date_source ?? "—"}
                  </td>
                  <td className="py-2 text-aegis-warn">{row.error ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : !error ? (
        <p className="text-sm text-aegis-muted">No ingest run yet in this session.</p>
      ) : null}
    </section>
  );
}
