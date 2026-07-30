"use client";

import { useState, useTransition } from "react";

import {
  ApiClientError,
  CalibrationReadiness,
  OutcomeLabel,
  ProbabilityCalibration,
  ResearchAssessment,
  ResearchEvidenceSummary,
  createOutcomeLabels,
  createProbabilityCalibration,
  createResearchAssessment,
  downloadResearchEvidenceSummary,
  getApiBaseUrl,
  getCalibrationReadiness,
  getLatestResearchAssessment,
  getResearchEvidenceSummary,
  listOutcomeLabels,
  listProbabilityCalibrations,
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

/** Sort API label keys: forward_return_N by N ascending, then other keys. Never invent values. */
function sortedLabelEntries(labels: Record<string, number>): [string, number][] {
  return Object.entries(labels).sort(([a], [b]) => {
    const na = /^forward_return_(\d+)$/.exec(a);
    const nb = /^forward_return_(\d+)$/.exec(b);
    if (na && nb) {
      return Number(na[1]) - Number(nb[1]);
    }
    if (na) {
      return -1;
    }
    if (nb) {
      return 1;
    }
    return a.localeCompare(b);
  });
}

/** Compact history line from API label payload only (Phase 26, ADR-0027). */
function formatLabelHorizonSummary(labels: Record<string, number>): string {
  const entries = sortedLabelEntries(labels);
  if (entries.length === 0) {
    return "none";
  }
  return entries
    .map(([key, value]) => {
      const match = /^forward_return_(\d+)$/.exec(key);
      const short = match ? `fwd${match[1]}` : key;
      return `${short}=${value.toFixed(4)}`;
    })
    .join(" · ");
}

export function ResearchAssessmentPanel({
  symbol,
  initialLatest,
}: ResearchAssessmentPanelProps) {
  const [latest, setLatest] = useState<ResearchAssessment | null>(initialLatest);
  const [outcomeLabel, setOutcomeLabel] = useState<OutcomeLabel | null>(null);
  const [outcomeLabelHistory, setOutcomeLabelHistory] = useState<OutcomeLabel[]>([]);
  const [readiness, setReadiness] = useState<CalibrationReadiness | null>(null);
  const [calibration, setCalibration] = useState<ProbabilityCalibration | null>(null);
  const [calibrationHistory, setCalibrationHistory] = useState<ProbabilityCalibration[]>(
    [],
  );
  const [evidenceSummary, setEvidenceSummary] = useState<ResearchEvidenceSummary | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const baseUrl = getApiBaseUrl();

  async function loadReadiness() {
    const next = await getCalibrationReadiness(baseUrl, symbol);
    setReadiness(next);
  }

  async function loadEvidenceSummary() {
    const next = await getResearchEvidenceSummary(baseUrl, symbol);
    setEvidenceSummary(next);
  }

  async function loadOutcomeLabelHistory(assessmentId: number) {
    const rows = await listOutcomeLabels(baseUrl, symbol, assessmentId, 20);
    setOutcomeLabelHistory(rows);
    setOutcomeLabel(rows[0] ?? null);
  }

  async function loadCalibrationHistory(assessmentId: number) {
    const rows = await listProbabilityCalibrations(baseUrl, symbol, assessmentId, 20);
    setCalibrationHistory(rows);
    const newest = rows[0] ?? null;
    setCalibration(newest);
    if (newest != null) {
      setLatest((current) =>
        current == null
          ? current
          : { ...current, probability_confidence: newest.probability_confidence },
      );
    }
  }

  function onAssess() {
    startTransition(async () => {
      setError(null);
      try {
        const snapshot = await createResearchAssessment(baseUrl, symbol);
        setLatest(snapshot);
        setOutcomeLabel(null);
        setOutcomeLabelHistory([]);
        setCalibration(null);
        setCalibrationHistory([]);
        setEvidenceSummary(null);
        await loadReadiness();
        if (snapshot.id != null) {
          await loadOutcomeLabelHistory(snapshot.id);
          await loadCalibrationHistory(snapshot.id);
        }
        await loadEvidenceSummary();
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
        setOutcomeLabel(null);
        setOutcomeLabelHistory([]);
        setCalibration(null);
        setCalibrationHistory([]);
        setEvidenceSummary(null);
        if (snapshot.id != null) {
          await loadOutcomeLabelHistory(snapshot.id);
          await loadCalibrationHistory(snapshot.id);
        }
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        if (err instanceof ApiClientError && err.status === 404) {
          setLatest(null);
          setOutcomeLabel(null);
          setOutcomeLabelHistory([]);
          setReadiness(null);
          setCalibration(null);
          setCalibrationHistory([]);
          setEvidenceSummary(null);
          setError(null);
          try {
            await loadEvidenceSummary();
          } catch {
            // empty summary optional when symbol has no assessments
          }
          return;
        }
        setError(formatAssessmentError(err));
      }
    });
  }

  function onComputeOutcomeLabels() {
    if (latest?.id == null) {
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        await createOutcomeLabels(baseUrl, symbol, latest.id as number);
        await loadOutcomeLabelHistory(latest.id as number);
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onComputeCalibration() {
    if (latest?.id == null || readiness?.status !== "ready") {
      return;
    }
    startTransition(async () => {
      setError(null);
      try {
        await createProbabilityCalibration(baseUrl, symbol, latest.id as number);
        await loadCalibrationHistory(latest.id as number);
        await loadReadiness();
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onRefreshEvidenceSummary() {
    startTransition(async () => {
      setError(null);
      try {
        await loadEvidenceSummary();
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onDownloadEvidenceSummary() {
    startTransition(async () => {
      setError(null);
      try {
        await downloadResearchEvidenceSummary(baseUrl, symbol);
      } catch (err) {
        setError(formatAssessmentError(err));
      }
    });
  }

  function onRefreshReadiness() {
    startTransition(async () => {
      setError(null);
      try {
        await loadReadiness();
      } catch (err) {
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
            onClick={onRefreshReadiness}
            disabled={isPending}
            className="rounded border border-aegis-line bg-white px-3 py-2 text-sm font-medium text-aegis-ink transition hover:bg-aegis-panel disabled:opacity-60"
          >
            Refresh readiness
          </button>
          <button
            type="button"
            onClick={onRefreshEvidenceSummary}
            disabled={isPending}
            className="rounded border border-aegis-line bg-white px-3 py-2 text-sm font-medium text-aegis-ink transition hover:bg-aegis-panel disabled:opacity-60"
          >
            Refresh evidence summary
          </button>
          <button
            type="button"
            onClick={onDownloadEvidenceSummary}
            disabled={isPending}
            className="rounded border border-aegis-line bg-white px-3 py-2 text-sm font-medium text-aegis-ink transition hover:bg-aegis-panel disabled:opacity-60"
          >
            Download evidence JSON
          </button>
          <button
            type="button"
            onClick={onComputeOutcomeLabels}
            disabled={isPending || latest?.id == null}
            className="rounded border border-aegis-line bg-white px-3 py-2 text-sm font-medium text-aegis-ink transition hover:bg-aegis-panel disabled:opacity-60"
          >
            Compute outcome labels
          </button>
          <button
            type="button"
            onClick={onComputeCalibration}
            disabled={isPending || latest?.id == null || readiness?.status !== "ready"}
            className="rounded border border-aegis-line bg-white px-3 py-2 text-sm font-medium text-aegis-ink transition hover:bg-aegis-panel disabled:opacity-60"
          >
            Compute calibration
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

      {evidenceSummary ? (
        <div className="mb-4 rounded border border-aegis-line bg-white/60 p-3 text-sm">
          <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
            Evidence summary (research-only — not advice)
          </p>
          <dl className="mt-2 grid gap-2 sm:grid-cols-2">
            <div>
              <dt className="text-aegis-muted">State</dt>
              <dd className="font-mono">{evidenceSummary.state}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Readiness</dt>
              <dd className="font-mono">{evidenceSummary.calibration_readiness.status}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Assessments (≤100)</dt>
              <dd className="font-mono">{evidenceSummary.assessment_count}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Labels / calibrations (latest id)</dt>
              <dd className="font-mono">
                {evidenceSummary.outcome_label_count} / {evidenceSummary.calibration_count}
              </dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Latest probability_confidence</dt>
              <dd className="font-mono">
                {evidenceSummary.latest_calibration == null
                  ? "null"
                  : evidenceSummary.latest_calibration.probability_confidence.toFixed(4)}
              </dd>
            </div>
            {evidenceSummary.latest_outcome_label == null ? (
              <div>
                <dt className="text-aegis-muted">Latest outcome labels</dt>
                <dd className="font-mono">null</dd>
              </div>
            ) : (
              sortedLabelEntries(evidenceSummary.latest_outcome_label.labels).map(
                ([key, value]) => (
                  <div key={key}>
                    <dt className="text-aegis-muted">Latest {key}</dt>
                    <dd className="font-mono">{value.toFixed(4)}</dd>
                  </div>
                ),
              )
            )}
          </dl>
          <p className="mt-2 text-xs text-aegis-muted">{evidenceSummary.detail}</p>
        </div>
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
                  : `${latest.probability_confidence.toFixed(4)} (calibrated research-only)`}
              </dd>
            </div>
            <div>
              <dt className="text-aegis-muted">total_return_20</dt>
              <dd className="font-mono">{String(latest.components.total_return_20)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">realized_vol_20</dt>
              <dd className="font-mono">{String(latest.components.realized_vol_20)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">research_index</dt>
              <dd className="font-mono">{String(latest.components.research_index)}</dd>
            </div>
            <div>
              <dt className="text-aegis-muted">Lookback</dt>
              <dd className="font-mono">
                {latest.lookback_start_date} → {latest.lookback_end_date} (
                {latest.bar_count} bars)
              </dd>
            </div>
            {typeof latest.components.component_source === "string" ? (
              <div>
                <dt className="text-aegis-muted">Component source</dt>
                <dd className="font-mono">{latest.components.component_source}</dd>
              </div>
            ) : null}
            {typeof latest.components.source_availability_factor === "number" ? (
              <div>
                <dt className="text-aegis-muted">Source availability factor</dt>
                <dd className="font-mono">
                  {latest.components.source_availability_factor.toFixed(4)}
                </dd>
              </div>
            ) : null}
            {typeof latest.components.source_agreement_factor === "number" ? (
              <div>
                <dt className="text-aegis-muted">Source agreement factor</dt>
                <dd className="font-mono">
                  {latest.components.source_agreement_factor.toFixed(4)}
                  {typeof latest.components.agreeing_dates === "number" &&
                  typeof latest.components.comparable_dates === "number"
                    ? ` (${latest.components.agreeing_dates}/${latest.components.comparable_dates} comparable)`
                    : null}
                </dd>
              </div>
            ) : null}
          </dl>
          <p className="text-xs text-aegis-muted">
            Computed at {latest.computed_at} from source {latest.input_source}. Research
            only — not actionable.
          </p>
          {outcomeLabel ? (
            <div className="rounded border border-aegis-line bg-white/60 p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                Outcome labels (evidence only — not calibrated probability)
              </p>
              <dl className="mt-2 grid gap-2 sm:grid-cols-2">
                {sortedLabelEntries(outcomeLabel.labels).map(([key, value]) => (
                  <div key={key}>
                    <dt className="text-aegis-muted">{key}</dt>
                    <dd className="font-mono">{value.toFixed(6)}</dd>
                  </div>
                ))}
              </dl>
              <p className="mt-2 text-xs text-aegis-muted">
                Bar source {outcomeLabel.bar_source}. Label method{" "}
                {outcomeLabel.label_method_id} v{outcomeLabel.label_method_version}.
              </p>
              {outcomeLabelHistory.length > 1 ? (
                <div className="mt-3 border-t border-aegis-line pt-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                    Outcome label history (newest first)
                  </p>
                  <ul className="mt-2 space-y-1 font-mono text-xs text-aegis-ink">
                    {outcomeLabelHistory.map((row) => {
                      const horizons = formatLabelHorizonSummary(row.labels);
                      return (
                        <li key={row.id ?? `${row.computed_at}-${horizons}`}>
                          {row.computed_at} · {horizons} · {row.bar_source}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}
          {readiness ? (
            <div className="rounded border border-aegis-line bg-white/60 p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                Calibration readiness (diagnostics only — not advice)
              </p>
              <dl className="mt-2 grid gap-2 sm:grid-cols-2">
                <div>
                  <dt className="text-aegis-muted">Status</dt>
                  <dd className="font-mono">{readiness.status}</dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Method</dt>
                  <dd className="font-mono">{readiness.calibration_method_id}</dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Labeled corpus</dt>
                  <dd className="font-mono">
                    {readiness.corpus_count} / min {readiness.min_corpus}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Similarity bucket</dt>
                  <dd className="font-mono">
                    {readiness.bucket_count} / min {readiness.min_bucket} (±
                    {readiness.index_bucket_width})
                  </dd>
                </div>
              </dl>
              <p className="mt-2 text-xs text-aegis-muted">{readiness.detail}</p>
            </div>
          ) : null}
          {calibration ? (
            <div className="rounded border border-aegis-line bg-white/60 p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                Probability calibration (research-only — not advice)
              </p>
              <dl className="mt-2 grid gap-2 sm:grid-cols-2">
                <div>
                  <dt className="text-aegis-muted">probability_confidence</dt>
                  <dd className="font-mono">{calibration.probability_confidence.toFixed(4)}</dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Method</dt>
                  <dd className="font-mono">
                    {calibration.calibration_method_id} v{calibration.calibration_method_version}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Corpus / bucket</dt>
                  <dd className="font-mono">
                    {calibration.corpus_count} / {calibration.bucket_count}
                  </dd>
                </div>
                <div>
                  <dt className="text-aegis-muted">Computed at</dt>
                  <dd className="font-mono">{calibration.computed_at}</dd>
                </div>
              </dl>
              {calibrationHistory.length > 1 ? (
                <div className="mt-3 border-t border-aegis-line pt-3">
                  <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                    Calibration history (newest first)
                  </p>
                  <ul className="mt-2 space-y-1 font-mono text-xs text-aegis-ink">
                    {calibrationHistory.map((row) => (
                      <li key={row.id ?? `${row.computed_at}-${row.probability_confidence}`}>
                        {row.computed_at} · p={row.probability_confidence.toFixed(4)} · corpus=
                        {row.corpus_count}/{row.bucket_count}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : !error ? (
        <p className="text-sm text-aegis-muted">
          No research assessment stored yet for {symbol}. Run an assessment to append one.
        </p>
      ) : null}
    </section>
  );
}
