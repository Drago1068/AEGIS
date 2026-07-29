"use client";

import { useState, useTransition } from "react";

import {
  ApiClientError,
  ResearchAssessment,
  createResearchAssessment,
  getApiBaseUrl,
  getLatestResearchAssessment,
} from "@/lib/api-client";

type ResearchAssessmentPanelProps = {
  symbol: string;
  initialLatest: ResearchAssessment | null;
};

function formatAssessmentError(err: unknown): string {
  if (!(err instanceof ApiClientError)) {
    return "Research assessment request failed.";
  }
  if (err.status === 422 && err.body && typeof err.body === "object") {
    const detail = (err.body as { detail?: unknown }).detail;
    if (detail && typeof detail === "object") {
      const reason = (detail as { reason?: unknown }).reason;
      const message = (detail as { message?: unknown }).message;
      if (typeof reason === "string" && typeof message === "string") {
        return `Unavailable (${reason}): ${message}`;
      }
    }
  }
  return err.message;
}

export function ResearchAssessmentPanel({
  symbol,
  initialLatest,
}: ResearchAssessmentPanelProps) {
  const [latest, setLatest] = useState<ResearchAssessment | null>(initialLatest);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const baseUrl = getApiBaseUrl();

  function onAssess() {
    startTransition(async () => {
      setError(null);
      try {
        const snapshot = await createResearchAssessment(baseUrl, symbol);
        setLatest(snapshot);
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onRefreshLatest() {
    startTransition(async () => {
      setError(null);
      try {
        const snapshot = await getLatestResearchAssessment(baseUrl, symbol);
        setLatest(snapshot);
      } catch (err) {
        if (err instanceof ApiClientError && err.status === 404) {
          setLatest(null);
          setError(null);
          return;
        }
        setError(formatAssessmentError(err));
      }
    });
  }

  return (
    <section className="rounded-lg border border-aegis-line bg-aegis-panel p-5 shadow-sm">
      <header className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-aegis-warn">
            Research only
          </p>
          <h2 className="text-lg font-semibold tracking-tight text-aegis-ink">
            Research assessment
          </h2>
          <p className="text-sm text-aegis-muted">
            Research heuristic from stored primary daily bars (on-demand or after a successful
            ingest when configured). Not a probability, signal, or recommendation. Values come
            from the API only — refresh latest to see post-ingest snapshots.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={onRefreshLatest}
            disabled={isPending}
            className="rounded border border-aegis-line bg-white px-3 py-2 text-sm font-medium text-aegis-ink transition hover:bg-aegis-panel disabled:opacity-60"
          >
            Refresh latest
          </button>
          <button
            type="button"
            onClick={onAssess}
            disabled={isPending}
            className="rounded bg-aegis-ink px-4 py-2 text-sm font-medium text-white transition hover:brightness-110 disabled:opacity-60"
          >
            {isPending ? "Working..." : "Run assessment"}
          </button>
        </div>
      </header>

      {error ? (
        <p className="mb-3 text-sm text-aegis-danger" role="alert">
          {error}
        </p>
      ) : null}

      {latest ? (
        <div className="space-y-3 text-sm">
          <p className="font-semibold uppercase tracking-wide text-aegis-warn">
            State: {latest.state.replaceAll("_", " ")}
          </p>
          <dl className="grid gap-2 sm:grid-cols-2">
            <div>
              <dt className="text-aegis-muted">Method</dt>
              <dd className="font-mono">
                {latest.method_id} v{latest.method_version}
              </dd>
            </div>
            <div>
              <dt className="text-aegis-muted">As-of trading date</dt>
              <dd className="font-mono">{latest.as_of_trading_date}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Coverage confidence</dt>
              <dd className="font-mono">{latest.coverage_confidence.toFixed(4)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Probability confidence</dt>
              <dd className="font-mono">
                {latest.probability_confidence === null
                  ? "null (not calibrated)"
                  : latest.probability_confidence}
              </dd>
            </div>
            <div>
              <dt className="text-aegis-muted">total_return_20</dt>
              <dd className="font-mono">{latest.components.total_return_20}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">realized_vol_20</dt>
              <dd className="font-mono">{latest.components.realized_vol_20}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">research_index</dt>
              <dd className="font-mono">{latest.components.research_index}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Lookback</dt>
              <dd className="font-mono">
                {latest.lookback_start_date} → {latest.lookback_end_date} (
                {latest.bar_count} bars)
              </dd>
            </div>
          </dl>
          <p className="text-xs text-aegis-muted">
            Computed at {latest.computed_at} from source {latest.input_source}. Research
            only — not actionable.
          </p>
        </div>
      ) : !error ? (
        <p className="text-sm text-aegis-muted">
          No research assessment stored yet for {symbol}. Run an assessment to append one.
        </p>
      ) : null}
    </section>
  );
}
