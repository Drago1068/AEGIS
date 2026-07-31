"use client";

import type { OutcomeLabel } from "@/lib/api-client";

import {
  formatLabelHorizonSummary,
  sortedLabelEntries,
  type OutcomeLabelHistoryLoadKind,
} from "./research-assessment-panel-helpers";

export type ResearchOutcomeLabelHistorySectionProps = {
  outcomeLabel: OutcomeLabel | null;
  outcomeLabelHistory: OutcomeLabel[];
  outcomeLabelHistoryAssessmentId: number | null;
  outcomeLabelHistoryLoadKind: OutcomeLabelHistoryLoadKind | null;
  latestId: number | null;
  isPending: boolean;
  onLoadLatestLabels: () => void;
};

export function ResearchOutcomeLabelHistorySection({
  outcomeLabel,
  outcomeLabelHistory,
  outcomeLabelHistoryAssessmentId,
  outcomeLabelHistoryLoadKind,
  latestId,
  isPending,
  onLoadLatestLabels,
}: ResearchOutcomeLabelHistorySectionProps) {
  if (outcomeLabel == null && outcomeLabelHistoryAssessmentId == null) {
    return null;
  }

  return (
    <div
      className="rounded border border-aegis-line bg-white/60 p-3"
      data-testid="outcome-label-history-section"
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
        Outcome labels (evidence only — not calibrated probability)
      </p>
      {outcomeLabelHistoryAssessmentId != null ? (
        <p
          className="mt-1 font-mono text-xs text-aegis-muted"
          data-testid="outcome-label-history-assessment-id"
        >
          Assessment id {outcomeLabelHistoryAssessmentId}
          {outcomeLabelHistoryLoadKind != null ? (
            <span data-testid="outcome-label-history-load-kind">
              {" "}
              · {outcomeLabelHistoryLoadKind === "scan_labeled" ? "scan-labeled" : "latest"}
              {outcomeLabelHistoryLoadKind === "scan_labeled" &&
              latestId != null &&
              latestId !== outcomeLabelHistoryAssessmentId
                ? ` (latest is ${latestId})`
                : ""}
            </span>
          ) : null}
        </p>
      ) : null}
      {outcomeLabelHistoryAssessmentId != null &&
      latestId != null &&
      outcomeLabelHistoryAssessmentId !== latestId ? (
        <button
          type="button"
          className="mt-2 text-sm underline-offset-2 hover:underline disabled:opacity-60"
          disabled={isPending}
          data-testid="load-latest-labels"
          onClick={onLoadLatestLabels}
        >
          Load labels for latest {latestId}
        </button>
      ) : null}
      {outcomeLabel ? (
        <>
          <dl className="mt-2 grid gap-2 sm:grid-cols-2">
            {sortedLabelEntries(outcomeLabel.labels).map(([key, value]) => {
              const end = outcomeLabel.label_end_dates[key];
              return (
                <div key={key}>
                  <dt className="text-aegis-muted">{key}</dt>
                  <dd className="font-mono">
                    {value.toFixed(6)}
                    {typeof end === "string" && end.length > 0 ? ` · end ${end}` : null}
                  </dd>
                </div>
              );
            })}
          </dl>
          <p className="mt-2 text-xs text-aegis-muted">
            Bar source {outcomeLabel.bar_source}. Label method {outcomeLabel.label_method_id} v
            {outcomeLabel.label_method_version}.
          </p>
          {outcomeLabelHistory.length > 1 ? (
            <div className="mt-3 border-t border-aegis-line pt-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-aegis-muted">
                Outcome label history (newest first)
              </p>
              <ul className="mt-2 space-y-1 font-mono text-xs text-aegis-ink">
                {outcomeLabelHistory.map((row) => {
                  const horizons = formatLabelHorizonSummary(row.labels, row.label_end_dates);
                  return (
                    <li key={row.id ?? `${row.computed_at}-${horizons}`}>
                      {row.computed_at} · {horizons} · {row.bar_source}
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : null}
        </>
      ) : (
        <p className="mt-2 text-sm text-aegis-muted" data-testid="outcome-label-empty-state">
          No outcome labels stored for assessment {outcomeLabelHistoryAssessmentId}
        </p>
      )}
    </div>
  );
}
