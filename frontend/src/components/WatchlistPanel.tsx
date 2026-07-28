"use client";

import Link from "next/link";
import { useState, useTransition } from "react";
import type { FormEvent } from "react";

import {
  ApiClientError,
  WatchlistSymbol,
  addWatchlistSymbol,
  getApiBaseUrl,
  removeWatchlistSymbol,
} from "@/lib/api-client";

type WatchlistPanelProps = {
  initialSymbols: WatchlistSymbol[];
  loadError?: string | null;
};

export function WatchlistPanel({ initialSymbols, loadError = null }: WatchlistPanelProps) {
  const [symbols, setSymbols] = useState(initialSymbols);
  const [symbolInput, setSymbolInput] = useState("");
  const [error, setError] = useState<string | null>(loadError);
  const [isPending, startTransition] = useTransition();
  const baseUrl = getApiBaseUrl();

  function refreshAfterMutation(next: WatchlistSymbol[]) {
    setSymbols(next);
    setError(null);
  }

  function onAdd(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const raw = symbolInput.trim();
    if (!raw) {
      setError("Enter a symbol to add.");
      return;
    }

    startTransition(async () => {
      try {
        const created = await addWatchlistSymbol(baseUrl, raw);
        refreshAfterMutation(
          [...symbols.filter((row) => row.symbol !== created.symbol), created].sort((a, b) =>
            a.symbol.localeCompare(b.symbol),
          ),
        );
        setSymbolInput("");
      } catch (err) {
        setError(err instanceof ApiClientError ? err.message : "Failed to add symbol.");
      }
    });
  }

  function onRemove(symbol: string) {
    startTransition(async () => {
      try {
        await removeWatchlistSymbol(baseUrl, symbol);
        refreshAfterMutation(symbols.filter((row) => row.symbol !== symbol));
      } catch (err) {
        setError(err instanceof ApiClientError ? err.message : "Failed to remove symbol.");
      }
    });
  }

  return (
    <section className="rounded-lg border border-aegis-line bg-aegis-panel p-5 shadow-sm">
      <header className="mb-4 flex items-baseline justify-between gap-3">
        <h2 className="text-lg font-semibold tracking-tight text-aegis-ink">Watchlist</h2>
        <p className="text-sm text-aegis-muted">Active symbols for ingestion</p>
      </header>

      <form onSubmit={onAdd} className="mb-4 flex flex-wrap gap-2">
        <label className="sr-only" htmlFor="watchlist-symbol">
          Symbol
        </label>
        <input
          id="watchlist-symbol"
          name="symbol"
          value={symbolInput}
          onChange={(event) => setSymbolInput(event.target.value)}
          placeholder="Add symbol (e.g. AAPL)"
          className="min-w-[12rem] flex-1 rounded border border-aegis-line bg-aegis-surface px-3 py-2 text-aegis-ink outline-none focus:border-aegis-accent"
          disabled={isPending}
          autoComplete="off"
        />
        <button
          type="submit"
          disabled={isPending}
          className="rounded bg-aegis-accent px-4 py-2 font-medium text-white transition hover:brightness-110 disabled:opacity-60"
        >
          Add
        </button>
      </form>

      {error ? (
        <p className="mb-3 text-sm text-aegis-danger" role="alert">
          {error}
        </p>
      ) : null}

      {symbols.length === 0 ? (
        <p className="text-sm text-aegis-muted">No active symbols. Add one to begin tracking.</p>
      ) : (
        <ul className="divide-y divide-aegis-line border-t border-aegis-line">
          {symbols.map((row) => (
            <li key={row.symbol} className="flex items-center justify-between gap-3 py-3">
              <Link
                href={`/symbols/${encodeURIComponent(row.symbol)}`}
                className="font-mono text-base font-medium text-aegis-ink underline-offset-4 hover:underline"
              >
                {row.symbol}
              </Link>
              <button
                type="button"
                onClick={() => onRemove(row.symbol)}
                disabled={isPending}
                className="rounded border border-aegis-line px-3 py-1 text-sm text-aegis-muted transition hover:border-aegis-danger hover:text-aegis-danger disabled:opacity-60"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
